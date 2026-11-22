"""Run with python -m tools.ap02 --config /absolute/local/config.json."""

import argparse
import json
import signal
from types import FrameType

from .scan import run


def main() -> int:
    """Return 0 for completed processing, 2 for incomplete, 130 for user interruption."""

    def interrupted(signum: int, frame: FrameType | None) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, interrupted)
    parser = argparse.ArgumentParser(description="Read-only OHLCV inventory")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    try:
        with open(args.config) as stream:
            output = run(json.load(stream))
        print(output, flush=True)
        return 2 if output.name.endswith(".partial") else 0
    except (ValueError, OSError, KeyError) as error:
        print(f"Configuration or scan error: {error}", flush=True)
        return 2
    except KeyboardInterrupt:
        return 130


raise SystemExit(main())
