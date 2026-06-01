#!/usr/bin/env python3
"""Optional real serial sensor reader (configure PORT). Falls back to sim."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from daq.logger import DATA, read_sensors_sim, run


def read_sensors_serial(t: float, port: str | None) -> dict[str, float]:
    if not port:
        return read_sensors_sim(t)
    # Placeholder: integrate your ADC protocol here
    row = read_sensors_sim(t)
    row["serial_port"] = port
    return row


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=str, default=None, help="e.g. /dev/ttyUSB0")
    p.add_argument("--duration", type=float, default=60)
    p.add_argument("--interval", type=float, default=1.0)
    args = p.parse_args()
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out = DATA / f"serial_{stamp}.csv"

    t0 = time.monotonic()
    import csv

    fields = list(read_sensors_sim(0).keys()) + ["iso_time", "serial_port"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        while time.monotonic() - t0 < args.duration:
            t = time.monotonic() - t0
            from datetime import datetime, timezone

            row = read_sensors_serial(t, args.port)
            row["iso_time"] = datetime.now(timezone.utc).isoformat()
            w.writerow(row)
            f.flush()
            time.sleep(args.interval)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
