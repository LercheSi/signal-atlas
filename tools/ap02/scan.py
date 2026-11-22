"""Inventory orchestration and disk-backed comparisons; sources are opened read-only."""

import csv
import fnmatch
import hashlib
import io
import json
import os
import platform
import re
import shutil
import sqlite3
import stat
import time
import zipfile
import zlib
from collections import Counter
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TextIO

from .archives import JoinedParts
from .parsers import invalid_values, next_start, parse

VERSION = "0.1.0"
Json = dict[str, Any]


def utc_now() -> str:
    """Return a timezone-qualified run timestamp, unrelated to source availability."""
    return datetime.now(UTC).isoformat()


def digest(path: Path) -> str:
    """Hash the complete physical file using bounded memory."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def emit(stream: TextIO, record: Json) -> None:
    """Append a JSONL evidence record, immediately visible to progress readers."""
    stream.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
    stream.flush()


def canonical_decimal(value: Any) -> str:
    """Serialize an exact decimal without context-dependent rounding."""
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def classify(relative: str, source: Json) -> str:
    """Apply explicit source-local patterns; unmatched files remain unknown."""
    for category in ("original", "derived", "support"):
        if any(fnmatch.fnmatchcase(relative, pattern) for pattern in source.get(category, [])):
            return category
    return "unknown"


def walk(root: Path, errors: list[Json]) -> Iterator[Path]:
    """Visit without following symlinks; retain inaccessible directories as diagnostics."""

    def onerror(error: OSError) -> None:
        errors.append(
            {"code": "DIRECTORY_UNREADABLE", "path": str(error.filename), "error": str(error)}
        )

    for folder, directories, files in os.walk(root, followlinks=False, onerror=onerror):
        directories.sort()
        for name in list(directories):
            path = Path(folder) / name
            if path.is_symlink():
                directories.remove(name)
                yield path
        for name in sorted(files):
            yield Path(folder) / name


class Analyzer:
    """Store source observations on disk; preserve all conflicting payload variants."""

    def __init__(
        self, database: Path, findings: TextIO, members: TextIO, min_free_bytes: int = 1_073_741_824
    ) -> None:
        self.database_path = database
        self.min_free_bytes = min_free_bytes
        self.database = sqlite3.connect(database)
        self.database.executescript("""
            PRAGMA journal_mode=WAL;
            PRAGMA cache_size=-32768;
            CREATE TABLE observations (
                source TEXT, instrument TEXT, interval TEXT, start INTEGER,
                payload TEXT, location TEXT,
                PRIMARY KEY(source,instrument,interval,start,payload)
            ) WITHOUT ROWID;
            CREATE TABLE coverage (
                source TEXT, instrument TEXT, interval TEXT, first INTEGER,
                last INTEGER, location TEXT
            );
        """)
        self.findings = findings
        self.members = members
        self.counts: Counter[str] = Counter()
        self.formats: Counter[str] = Counter()
        self.missing_points: Counter[str] = Counter()

    def finding(self, code: str, **details: Any) -> None:
        self.counts[code] += 1
        emit(self.findings, {"code": code, **details})

    def analyze(self, source: str, name: str, stream: TextIO, reference: Json) -> None:
        """Inspect every row; parsing failures do not conceal subsequent rows."""
        rows = 0
        parsed = 0
        initial_counts = self.counts.copy()
        last_end: int | None = None
        member_status = "readable"
        first: int | None = None
        last: int | None = None
        previous: int | None = None
        identity: tuple[str, str] | None = None
        try:
            reader = csv.reader(stream)
            for row in reader:
                rows += 1
                location = {"source": source, "path": reference["path"], "line": reader.line_num}
                if "member" in reference:
                    location["member"] = reference["member"]
                try:
                    candle = parse(source, name, row)
                except (ValueError, ArithmeticError, OverflowError) as error:
                    self.finding("PARSE_ERROR", location=location, error=str(error))
                    continue
                parsed += 1
                identity = candle.instrument, candle.interval
                last_end = candle.end_us if last_end is None else max(last_end, candle.end_us)
                first = candle.start_us if first is None else min(first, candle.start_us)
                last = candle.start_us if last is None else max(last, candle.start_us)
                if invalid_values(candle):
                    self.finding("INVALID_VALUES", location=location)
                if previous is not None and candle.start_us < previous:
                    self.finding("OUT_OF_ORDER", location=location, previous_start_us=previous)
                previous = candle.start_us
                payload = json.dumps([canonical_decimal(value) for value in candle.values])
                key = (source, candle.instrument, candle.interval, candle.start_us)
                existing = self.database.execute(
                    "SELECT payload,location FROM observations WHERE source=? AND instrument=? "
                    "AND interval=? AND start=?",
                    key,
                ).fetchall()
                same = next((item for item in existing if item[0] == payload), None)
                if same:
                    self.finding(
                        "IDENTICAL_DUPLICATE", location=location, first_location=json.loads(same[1])
                    )
                elif existing:
                    self.finding(
                        "VALUE_CONFLICT",
                        location=location,
                        other_locations=[json.loads(item[1]) for item in existing],
                        revision_order="unknown",
                    )
                self.database.execute(
                    "INSERT OR IGNORE INTO observations VALUES(?,?,?,?,?,?)",
                    (*key, payload, json.dumps(location)),
                )
                if rows % 10000 == 0:
                    self.database.commit()
                    if rows % 100000 == 0:
                        print(f"Rows: {source} {name} {rows}", flush=True)
                    if shutil.disk_usage(self.database_path.parent).free < self.min_free_bytes:
                        raise OSError("work disk reserve reached")
        except (OSError, UnicodeError, csv.Error, zipfile.BadZipFile, EOFError) as error:
            member_status = "error"
            self.finding("MEMBER_UNREADABLE", location=reference, error=str(error))
            raise
        finally:
            self.database.commit()
            emit(
                self.members,
                {
                    **reference,
                    "name": name,
                    "rows": rows,
                    "parsed_rows": parsed,
                    "first_start_us": first,
                    "last_start_us": last,
                    "last_end_us": last_end,
                    "status": member_status,
                    "findings": dict(self.counts - initial_counts),
                    "source": source,
                    "identity": identity,
                    "availability": "unknown",
                    "quote": "unknown",
                },
            )
        if identity and first is not None and last is not None:
            self.formats[f"{source}:{'12' if source == 'binance' else '7'}-column"] += 1
            self.database.execute(
                "INSERT INTO coverage VALUES(?,?,?,?,?,?)",
                (source, *identity, first, last, json.dumps(reference)),
            )
            self.database.commit()

    def gaps(self) -> None:
        """Count gaps on the union of originals; never infer missing boundary history.

        Kraken archives omit intervals without trades. A missing grid point is
        therefore not itself proof of a lost record, on either source.
        """
        cursor = self.database.execute(
            "SELECT source,instrument,interval,start,MIN(location) FROM observations "
            "GROUP BY source,instrument,interval,start ORDER BY source,instrument,interval,start"
        )
        previous: tuple[str, str, str, int] | None = None
        for source, instrument, interval, start, location in cursor:
            if previous and previous[:3] == (source, instrument, interval):
                expected = next_start(previous[3], interval)
                if start > expected:
                    if interval == "1M":
                        missing = 0
                        while expected < start:
                            missing += 1
                            expected = next_start(expected, interval)
                    else:
                        width = expected - previous[3]
                        missing = (start - previous[3] - 1) // width
                    self.missing_points[source] += missing
                    self.finding(
                        "MISSING_GRID_POINTS",
                        source=source,
                        instrument=instrument,
                        interval=interval,
                        after_start_us=previous[3],
                        before_start_us=start,
                        missing_count=missing,
                        interpretation="no_trade_or_missing_delivery_unresolved",
                        location=json.loads(location),
                    )
                if interval != "1M" and (start - previous[3]) % (expected - previous[3]) != 0:
                    self.finding("INTERVAL_MISMATCH", location=json.loads(location))
            previous = source, instrument, interval, start

    def benchmarks(self, mappings: list[Json]) -> list[Json]:
        """Select reproducible intersections only for explicitly confirmed asset mappings."""
        results = []
        for mapping in mappings:
            interval = mapping["interval"]
            ranges = []
            references = []
            for source in ("binance", "kraken"):
                rows = self.database.execute(
                    "SELECT first,last,location FROM coverage WHERE source=? AND instrument=? "
                    "AND interval=? ORDER BY first",
                    (source, mapping[source], interval),
                ).fetchall()
                ranges.append(rows)
                references.append([json.loads(row[2]) for row in rows])
            if not all(ranges):
                continue
            common = self.database.execute(
                "SELECT MIN(start),MAX(start),COUNT(*) FROM ("
                "SELECT start FROM observations WHERE source='binance' AND instrument=? AND interval=? "
                "INTERSECT SELECT start FROM observations WHERE source='kraken' AND instrument=? AND interval=?)",
                (mapping["binance"], interval, mapping["kraken"], interval),
            ).fetchone()
            start, end, common_count = common
            if not common_count:
                continue
            # Windows are coverage candidates; reported gaps/conflicts remain binding exclusions.
            results.append(
                {
                    "mapping": mapping,
                    "common_timestamp_count": common_count,
                    "start_us": start,
                    "last_start_us": end,
                    "small_last_start_us": min(end, start + 7 * 86400 * 1_000_000),
                    "multiyear": end - start >= 2 * 365 * 86400 * 1_000_000,
                    "references": references,
                    "quality": "see_findings",
                    "status": "coverage_candidate_requires_quality_review",
                }
            )
        return results


def validate_config(config: Json) -> None:
    """Reject unsupported configuration and output paths inside read-only source trees."""
    if config.get("schema_version") != 1 or not config.get("sources"):
        raise ValueError("schema_version=1 and nonempty sources required")
    outputs = [Path(config[key]).resolve() for key in ("output_dir", "work_dir")]
    ids = set()
    for source in config["sources"]:
        if source["id"] not in ("binance", "kraken") or source["id"] in ids:
            raise ValueError("unique binance/kraken source IDs required")
        ids.add(source["id"])
        root = Path(source["root"]).resolve()
        if not root.is_dir():
            raise ValueError(f"source root unavailable: {root}")
        if any(path == root or root in path.parents for path in outputs):
            raise ValueError("output/work directory must be outside source roots")
    if (
        outputs[0] == outputs[1]
        or outputs[0] in outputs[1].parents
        or outputs[1] in outputs[0].parents
    ):
        raise ValueError("output and work directories must be separate")


def run(config: Json) -> Path:
    """Execute inventory, retain interrupted evidence, publish only complete processing.

    Quality findings may exist in a completed scan. Read/format errors, source
    changes and unknown original formats instead leave the run incomplete.
    """
    validate_config(config)
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output = Path(config["output_dir"]) / (run_id + ".partial")
    work = Path(config["work_dir"]) / run_id
    output.mkdir(parents=True)
    work.mkdir(parents=True)
    manifest: Json = {
        "schema_version": 1,
        "scan_version": VERSION,
        "implementation_sha256": hashlib.sha256(
            b"".join(
                path.name.encode() + b"\0" + path.read_bytes()
                for path in sorted(Path(__file__).parent.glob("*.py"))
            )
        ).hexdigest(),
        "started_at": utc_now(),
        "status": "running",
        "configuration": config,
        "configuration_sha256": hashlib.sha256(
            json.dumps(config, sort_keys=True).encode()
        ).hexdigest(),
        "hardware": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "cpu_model": next(
                (
                    line.split(":", 1)[1].strip()
                    for line in Path("/proc/cpuinfo").read_text().splitlines()
                    if line.startswith("model name")
                ),
                "unknown",
            ),
            "work_disk": dict(zip(("total", "used", "free"), shutil.disk_usage(work))),
            "output_disk": dict(zip(("total", "used", "free"), shutil.disk_usage(output))),
            "memory_bytes": os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES"),
        },
        "benchmark_status": "not_evaluated",
        "limitations": [
            "Historical availability and revision order unknown",
            "Quotes require explicit mapping; no filename suffix guessing",
            "Grid gaps do not alone prove delivery failures",
        ],
    }
    manifest_path = output / "manifest.json"

    def save() -> None:
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    save()
    started = time.monotonic()
    counts: Counter[str] = Counter()
    errors: list[Json] = []
    analyzer: Analyzer | None = None
    try:
        # Freeze the selected path list before any content analysis. This initial
        # inventory is retained even if a long hash/quality pass is interrupted.
        discovery_counts: Counter[str] = Counter()
        with (output / "selection.jsonl").open("w") as selection:
            for source in config["sources"]:
                root = Path(source["root"])
                print(f"Discovering {source['id']}: {root}", flush=True)
                for path in walk(root, errors):
                    relative = path.relative_to(root).as_posix()
                    category = classify(relative, source)
                    entry: Json = {"source": source["id"], "path": relative, "category": category}
                    try:
                        entry["bytes"] = path.lstat().st_size
                        discovery_counts["bytes"] += entry["bytes"]
                    except OSError as error:
                        entry["error"] = str(error)
                    discovery_counts["files"] += 1
                    discovery_counts[category] += 1
                    emit(selection, entry)
                    if discovery_counts["files"] % 10000 == 0:
                        print(f"Discovery: {dict(discovery_counts)}", flush=True)
            manifest["selection_counts"] = dict(discovery_counts)
            save()
        with (
            (output / "files.jsonl").open("w") as files,
            (output / "members.jsonl").open("w") as members,
            (output / "findings.jsonl").open("w") as findings,
        ):
            analyzer = Analyzer(
                work / "observations.sqlite",
                findings,
                members,
                config.get("min_free_bytes", 1_073_741_824),
            )
            with (output / "selection.jsonl").open() as selection:
                for line in selection:
                    selected = json.loads(line)
                    source = next(
                        item for item in config["sources"] if item["id"] == selected["source"]
                    )
                    root = Path(source["root"])
                    relative = selected["path"]
                    path = root / relative
                    category = selected["category"]
                    record: Json = {
                        "source": source["id"],
                        "path": relative,
                        "category": category,
                        "status": "pending",
                    }
                    if shutil.disk_usage(work).free < config.get("min_free_bytes", 1_073_741_824):
                        raise OSError("work disk reserve reached")
                    counts["files"] += 1
                    counts[category] += 1
                    try:
                        info = path.lstat()
                        record.update(
                            bytes=info.st_size,
                            mode=stat.filemode(info.st_mode),
                            uid=info.st_uid,
                            gid=info.st_gid,
                        )
                        counts["bytes"] += info.st_size
                        if not stat.S_ISREG(info.st_mode):
                            raise ValueError("symlink or nonregular file excluded")
                        before = digest(path)
                        record["sha256_before"] = before
                        record["status"] = "readable"
                        try:
                            if category == "original":
                                inspect_original(
                                    path, relative, source["id"], before, root, analyzer, record
                                )
                        finally:
                            after = digest(path)
                            record["sha256_after"] = after
                            record["unchanged"] = (
                                before == after and info.st_size == path.stat().st_size
                            )
                        if not record["unchanged"]:
                            raise ValueError("source changed during scan")
                    except (
                        OSError,
                        ValueError,
                        zipfile.BadZipFile,
                        EOFError,
                        UnicodeError,
                        NotImplementedError,
                        RuntimeError,
                    ) as error:
                        record.update(status="error", error=str(error))
                        counts["errors"] += 1
                    emit(files, record)
                    if counts["files"] % 100 == 0:
                        print(json.dumps(dict(counts), sort_keys=True), flush=True)
                        manifest["progress"] = dict(counts)
                        save()
            print("Verifying final source hashes and selected paths", flush=True)
            with (
                (output / "verification.jsonl").open("w") as verification,
                (output / "files.jsonl").open() as scanned,
            ):
                for line in scanned:
                    record = json.loads(line)
                    if "sha256_before" not in record:
                        continue
                    source = next(
                        item for item in config["sources"] if item["id"] == record["source"]
                    )
                    path = Path(source["root"]) / record["path"]
                    result: Json = {"source": source["id"], "path": record["path"]}
                    try:
                        if not stat.S_ISREG(path.lstat().st_mode):
                            raise ValueError("source replaced by nonregular file")
                        result["sha256_final"] = digest(path)
                        result["unchanged"] = result["sha256_final"] == record["sha256_before"]
                        if not result["unchanged"]:
                            counts["errors"] += 1
                    except (OSError, ValueError) as error:
                        result.update(unchanged=False, error=str(error))
                        counts["errors"] += 1
                    emit(verification, result)
            initial_paths = hashlib.sha256()
            with (output / "selection.jsonl").open() as selection:
                for line in selection:
                    item = json.loads(line)
                    initial_paths.update(
                        json.dumps([item["source"], item["path"]]).encode() + b"\n"
                    )
            final_paths = hashlib.sha256()
            for source in config["sources"]:
                root = Path(source["root"])
                for path in walk(root, errors):
                    final_paths.update(
                        json.dumps([source["id"], path.relative_to(root).as_posix()]).encode()
                        + b"\n"
                    )
            manifest["selected_paths_unchanged"] = initial_paths.digest() == final_paths.digest()
            if not manifest["selected_paths_unchanged"]:
                counts["errors"] += 1
            print("Computing cross-file grid gaps", flush=True)
            analyzer.gaps()
            manifest["benchmarks"] = analyzer.benchmarks(config.get("benchmark_mappings", []))
            manifest["benchmark_status"] = (
                "candidates_selected"
                if manifest["benchmarks"]
                else (
                    "no_suitable_overlap_found"
                    if config.get("benchmark_mappings")
                    else "no_mappings_configured"
                )
            )
            manifest["format_matrix"] = dict(analyzer.formats)
            manifest["missing_grid_points"] = dict(analyzer.missing_points)
            manifest["findings"] = dict(analyzer.counts)
            manifest["directory_errors"] = errors
            manifest["counts"] = dict(counts)
            fatal_findings = any(
                analyzer.counts[code] for code in ("PARSE_ERROR", "MEMBER_UNREADABLE")
            )
            manifest["status"] = (
                "complete"
                if not counts["errors"] and not errors and not fatal_findings
                else "incomplete"
            )
    except BaseException as error:
        manifest.update(
            status="interrupted" if isinstance(error, KeyboardInterrupt) else "failed",
            error=f"{type(error).__name__}: {error}",
        )
        raise
    finally:
        if analyzer:
            manifest["missing_grid_points"] = dict(analyzer.missing_points)
            manifest["findings"] = dict(analyzer.counts)
            manifest["format_matrix"] = dict(analyzer.formats)
            analyzer.database.close()
        manifest["finished_at"] = utc_now()
        manifest["elapsed_seconds"] = time.monotonic() - started
        manifest["progress"] = dict(counts)
        save()
        (output / "report.md").write_text(report(manifest))
    if manifest["status"] == "complete":
        final = output.with_suffix("")
        output.rename(final)
        return final
    return output


def inspect_original(
    path: Path,
    relative: str,
    source: str,
    before: str,
    root: Path,
    analyzer: Analyzer,
    record: Json,
) -> None:
    """Read CSV members and verify ZIP CRCs; physical split parts are hashed separately."""
    reference: Json = {"path": relative, "archive_sha256": before}
    if path.suffix == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as stream:
            analyzer.analyze(source, relative, stream, reference)
        return
    match = re.search(r"\.part(\d+)$", path.name)
    if match and int(match[1]) != 0:
        leader = path.with_name(path.name[: match.start()] + ".part00")
        if not leader.exists():
            raise ValueError("split archive leader missing")
        record["archive_leader"] = leader.relative_to(root).as_posix()
        return
    if match:
        prefix = path.name[: match.start()]
        parts = sorted(path.parent.glob(prefix + ".part[0-9][0-9]"))
        if [int(part.suffix[5:]) for part in parts] != list(range(len(parts))):
            raise ValueError("split archive part missing")
        hashes = [
            {"path": part.relative_to(root).as_posix(), "sha256": digest(part)} for part in parts
        ]
        reference["archive_parts"] = hashes
        with JoinedParts(parts) as joined:
            inspect_zip(joined, source, analyzer, reference)
        if any(digest(root / part["path"]) != part["sha256"] for part in hashes):
            raise ValueError("split archive changed during scan")
    elif path.suffix.lower() == ".zip":
        with path.open("rb") as binary:
            inspect_zip(binary, source, analyzer, reference)
    else:
        raise ValueError("unknown original format")


def inspect_zip(binary: Any, source: str, analyzer: Analyzer, reference: Json) -> None:
    """Inspect every member independently; damaged members do not hide later entries."""
    failures = 0
    with zipfile.ZipFile(binary) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            member_ref = {
                **reference,
                "member": member.filename,
                "bytes": member.file_size,
                "crc32": member.CRC,
            }
            try:
                with archive.open(member) as raw:
                    if member.filename.lower().endswith(".csv"):
                        with io.TextIOWrapper(raw, encoding="utf-8-sig", newline="") as stream:
                            analyzer.analyze(source, member.filename, stream, member_ref)
                    else:
                        while raw.read(1024 * 1024):
                            pass
                        emit(analyzer.members, {**member_ref, "status": "unknown_format"})
                        analyzer.finding("UNKNOWN_MEMBER_FORMAT", location=member_ref)
                        failures += 1
            except (
                OSError,
                ValueError,
                RuntimeError,
                UnicodeError,
                zipfile.BadZipFile,
                EOFError,
                NotImplementedError,
                zlib.error,
                csv.Error,
            ) as error:
                emit(analyzer.members, {**member_ref, "status": "error", "error": str(error)})
                analyzer.finding("ARCHIVE_MEMBER_ERROR", location=member_ref, error=str(error))
                failures += 1
    if failures:
        raise ValueError(f"{failures} archive members failed; see members/findings")


def report(manifest: Json) -> str:
    """Render local evidence, including explicit incomplete-state and availability limits."""
    return (
        f"# AP02 inventory · {manifest['status']}\n\n"
        f"Version: {VERSION} · Start: {manifest['started_at']}\n\n"
        "Original files were opened read-only. Complete means processing finished; "
        "quality findings still require review.\n\n"
        "```json\n"
        + json.dumps(
            {
                key: manifest.get(key)
                for key in (
                    "counts",
                    "findings",
                    "format_matrix",
                    "missing_grid_points",
                    "benchmarks",
                    "directory_errors",
                    "limitations",
                    "hardware",
                )
            },
            indent=2,
        )
        + "\n```\n\nDetailed evidence: files.jsonl, members.jsonl, findings.jsonl, manifest.json.\n"
    )
