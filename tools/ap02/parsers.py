"""Provider-specific CSV contracts; timestamps describe candles, never availability."""

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import PurePosixPath


@dataclass(frozen=True)
class Candle:
    """A source observation with an exclusive UTC end and exact decimal payload."""

    instrument: str
    interval: str
    start_us: int
    end_us: int
    values: tuple[Decimal, ...]
    source_time_unit: str


def next_start(start_us: int, interval: str) -> int:
    """Return the next UTC grid point, including calendar months."""
    if interval == "1M":
        date = datetime.fromtimestamp(start_us / 1_000_000, UTC)
        return (
            int(
                datetime(
                    date.year + (date.month == 12), date.month % 12 + 1, 1, tzinfo=UTC
                ).timestamp()
            )
            * 1_000_000
        )
    match = re.fullmatch(r"(\d+)([smhdw])", interval)
    if not match or int(match[1]) <= 0:
        raise ValueError("unknown interval")
    seconds = int(match[1]) * {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}[match[2]]
    return start_us + seconds * 1_000_000


def parse(source: str, name: str, row: list[str]) -> Candle:
    """Parse documented Binance Spot or Kraken OHLCVT; reject unknown schemas/units.

    Binance close time is inclusive at source precision. The exclusive end is
    computed from the interval and checked against that close. Neither provider
    archive proves historical publication or receipt time.
    """
    filename = PurePosixPath(name).name
    if source == "binance":
        match = re.fullmatch(r"(.+)-(\d+[smhdwM])-\d{4}-\d{2}(?:-\d{2})?\.csv", filename)
        if not match or len(row) != 12:
            raise ValueError("unknown Binance filename/schema")
        instrument, interval = match.groups()
        timestamp = int(row[0])
        if 10**12 <= timestamp < 10**14:
            scale = 1000
        elif 10**15 <= timestamp < 10**17:
            scale = 1
        else:
            raise ValueError("unknown Binance timestamp unit")
        source_time_unit = "milliseconds" if scale == 1000 else "microseconds"
        start_us = timestamp * scale
        end_us = next_start(start_us, interval)
        if (int(row[6]) + 1) * scale != end_us:
            raise ValueError("close time does not match interval")
        values = tuple(Decimal(row[i]) for i in (1, 2, 3, 4, 5, 7, 8, 9, 10))
    elif source == "kraken":
        match = re.fullmatch(r"(.+)_(\d+)\.csv", filename)
        if not match or len(row) != 7:
            raise ValueError("unknown Kraken filename/schema")
        instrument, minutes = match.groups()
        interval = f"{int(minutes)}m"
        seconds = int(row[0])
        if not 10**9 <= seconds < 10**10:
            raise ValueError("unknown Kraken timestamp unit")
        source_time_unit = "seconds"
        start_us = seconds * 1_000_000
        end_us = next_start(start_us, interval)
        values = tuple(Decimal(value) for value in row[1:])
    else:
        raise ValueError("unknown source")
    if not all(value.is_finite() for value in values):
        raise ValueError("nonfinite numeric value")
    return Candle(instrument, interval, start_us, end_us, values, source_time_unit)


def invalid_values(candle: Candle) -> bool:
    """Check positive prices, OHLC bounds, nonnegative volumes and integer trade counts."""
    open_price, high, low, close, *rest = candle.values
    trades = rest[2] if len(candle.values) == 9 else rest[1]
    return (
        min(open_price, high, low, close) <= 0
        or low > min(open_price, close)
        or high < max(open_price, close)
        or low > high
        or any(value < 0 for value in rest)
        or trades != trades.to_integral_value()
    )
