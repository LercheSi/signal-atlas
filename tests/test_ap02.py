"""Contract tests through parsers, archive streams and the public CLI."""

import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest.mock import patch

from tools.ap02.archives import JoinedParts
from tools.ap02.parsers import invalid_values, next_start, parse
from tools.ap02.scan import canonical_decimal, run, validate_config


class InventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "source").mkdir()
        self.config: dict[str, Any] = {
            "schema_version": 1,
            "sources": [
                {
                    "id": "kraken",
                    "root": str(self.root / "source"),
                    "original": ["*.csv", "*.zip", "*.part??"],
                    "derived": ["derived/*"],
                }
            ],
            "output_dir": str(self.root / "output"),
            "work_dir": str(self.root / "work"),
        }

    def archive(self, path: Path, content: str) -> None:
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("XBTUSD_1.csv", content)

    def records(self, output: Path, name: str) -> list[dict[str, Any]]:
        return [json.loads(line) for line in (output / name).read_text().splitlines()]

    def test_binance_units_and_calendar(self) -> None:
        for scale in (1, 1000):
            start = 1735689600000000
            row = [
                str(start // scale),
                "1",
                "2",
                "1",
                "2",
                "3",
                str((start + 60000000) // scale - 1),
                "4",
                "2",
                "1",
                "2",
                "0",
            ]
            candle = parse("binance", "BTCUSDT-1m-2025-01.csv", row)
            self.assertEqual(candle.start_us, start)
            self.assertFalse(invalid_values(candle))
        self.assertEqual(next_start(1735689600000000, "1M"), 1738368000000000)
        with self.assertRaises(ValueError):
            parse("binance", "bad.csv", row)

    def test_invalid_numeric_and_unknown_schema(self) -> None:
        for values in ("1,nan,1,1,1,1", "1,2,1,1,-1,1", "1,2,1,1,1,1.5"):
            row = ("1735689600," + values).split(",")
            try:
                candle = parse("kraken", "XBTUSD_1.csv", row)
            except ValueError:
                continue
            self.assertTrue(invalid_values(candle))
        with self.assertRaises(ValueError):
            parse("kraken", "XBTUSD.csv", ["1"] * 7)

    def test_cli_duplicate_conflict_gap_and_reproducibility(self) -> None:
        source = self.root / "source"
        (source / "XBTUSD_1.csv").write_text(
            "1735689600,1,2,1,2,3,1\n1735689720,1,2,1,2,3,1\n1735689600,1,2,1,2,3,1\nbad\n"
        )
        self.archive(source / "overlap.zip", "1735689600,1,3,1,3,3,1\n")
        config_path = self.root / "config.json"
        config_path.write_text(json.dumps(self.config))
        completed = subprocess.run(
            [sys.executable, "-m", "tools.ap02", "--config", str(config_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 2, completed.stderr)
        output = Path(completed.stdout.splitlines()[-1])
        findings = self.records(output, "findings.jsonl")
        codes = [item["code"] for item in findings]
        for code in (
            "IDENTICAL_DUPLICATE",
            "VALUE_CONFLICT",
            "MISSING_GRID_POINTS",
            "PARSE_ERROR",
            "OUT_OF_ORDER",
        ):
            self.assertIn(code, codes)
        other = run(self.config)
        self.assertEqual(findings, self.records(other, "findings.jsonl"))
        for record in self.records(output, "files.jsonl"):
            self.assertTrue(record["unchanged"])

    def test_split_zip_and_missing_part(self) -> None:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr("XBTUSD_1.csv", "1735689600,1,2,1,2,3,1\n")
        data = stream.getvalue()
        paths = []
        for index, chunk in enumerate((data[:40], data[40:80], data[80:])):
            path = self.root / "source" / f"full.zip.part{index:02}"
            path.write_bytes(chunk)
            paths.append(path)
        with JoinedParts(paths) as joined, zipfile.ZipFile(joined) as archive:
            self.assertIn(b"1735689600", archive.read("XBTUSD_1.csv"))
        output = run(self.config)
        self.assertEqual(json.loads((output / "manifest.json").read_text())["status"], "complete")
        paths[1].unlink()
        output = run(self.config)
        self.assertEqual(json.loads((output / "manifest.json").read_text())["status"], "incomplete")

    def test_unreadable_corrupt_changed_and_interrupted(self) -> None:
        path = self.root / "source" / "bad.zip"
        path.write_bytes(b"not zip")
        self.assertTrue(run(self.config).name.endswith(".partial"))
        path.unlink()
        path = self.root / "source" / "XBTUSD_1.csv"
        path.write_text("1735689600,1,2,1,2,3,1\n")
        with patch("tools.ap02.scan.digest", side_effect=PermissionError("denied")):
            self.assertTrue(run(self.config).name.endswith(".partial"))
        with patch("tools.ap02.scan.digest", side_effect=["before", "after"]):
            self.assertTrue(run(self.config).name.endswith(".partial"))
        with (
            patch("tools.ap02.scan.digest", side_effect=KeyboardInterrupt),
            self.assertRaises(KeyboardInterrupt),
        ):
            run(self.config)
        manifests = [
            json.loads(p.read_text()) for p in (self.root / "output").glob("*/manifest.json")
        ]
        self.assertIn("interrupted", [m["status"] for m in manifests])

    def test_unknown_member_does_not_hide_later_csv(self) -> None:
        with zipfile.ZipFile(self.root / "source" / "mixed.zip", "w") as archive:
            archive.writestr("unknown.txt", "unknown")
            archive.writestr("XBTUSD_1.csv", "1735689600,1,2,1,2,3,1\n")
        output = run(self.config)
        self.assertTrue(output.name.endswith(".partial"))
        self.assertTrue(
            any(item.get("parsed_rows") == 1 for item in self.records(output, "members.jsonl"))
        )
        self.assertTrue(self.records(output, "files.jsonl")[0]["unchanged"])

    def test_exact_decimal_and_disk_reserve(self) -> None:
        value = "1.123456789012345678901234567890123456789"
        self.assertEqual(canonical_decimal(Decimal(value)), value)
        self.assertEqual(canonical_decimal(Decimal("1.00")), "1")
        self.config["min_free_bytes"] = 10**30
        (self.root / "source" / "XBTUSD_1.csv").write_text("1735689600,1,2,1,2,3,1\n")
        with self.assertRaises(OSError):
            run(self.config)
        manifest = next((self.root / "output").glob("*/manifest.json"))
        self.assertEqual(json.loads(manifest.read_text())["status"], "failed")

    def test_benchmark_uses_actual_intersection(self) -> None:
        binance = self.root / "binance"
        binance.mkdir()
        self.config["sources"].append(
            {"id": "binance", "root": str(binance), "original": ["*.csv"]}
        )
        self.config["benchmark_mappings"] = [
            {"binance": "BTCUSDT", "kraken": "XBTUSD", "interval": "1m"}
        ]
        (binance / "BTCUSDT-1m-2025-01.csv").write_text(
            "1735689600000000,1,2,1,2,3,1735689659999999,4,2,1,2,0\n"
            "1735689720000000,1,2,1,2,3,1735689779999999,4,2,1,2,0\n"
        )
        kraken = self.root / "source" / "XBTUSD_1.csv"
        kraken.write_text("1735689660,1,2,1,2,3,1\n")
        output = run(self.config)
        self.assertEqual(json.loads((output / "manifest.json").read_text())["benchmarks"], [])
        kraken.write_text("1735689600,1,2,1,2,3,1\n")
        output = run(self.config)
        benchmark = json.loads((output / "manifest.json").read_text())["benchmarks"][0]
        self.assertEqual(benchmark["common_timestamp_count"], 1)
        self.assertFalse(benchmark["multiyear"])

    def test_output_guard_and_symlink(self) -> None:
        bad = {**self.config, "output_dir": str(self.root / "source" / "output")}
        with self.assertRaises(ValueError):
            validate_config(bad)
        (self.root / "source" / "link.csv").symlink_to("/etc/passwd")
        self.assertTrue(run(self.config).name.endswith(".partial"))
        self.assertNotIn(
            "sha256_before", self.records(next((self.root / "output").iterdir()), "files.jsonl")[0]
        )


if __name__ == "__main__":
    unittest.main()
