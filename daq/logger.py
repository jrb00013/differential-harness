#!/usr/bin/env python3
"""Bench DAQ logger for CHORUS-SGH-1 (simulated or serial sensors)."""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "bench"


def read_sensors_sim(t: float) -> dict[str, float]:
    """Simulated sensor stream for dev without hardware."""
    import math

    return {
        "t_s": t,
        "P_feed_bar": 0.5 + 0.05 * math.sin(t / 10),
        "P_draw_bar": 1.4 + 0.1 * math.sin(t / 7),
        "Q_feed_L_min": 2.0 + 0.2 * math.sin(t / 5),
        "Q_draw_L_min": 1.8,
        "cond_feed_mS_cm": 8.0,
        "cond_draw_mS_cm": 85.0,
        "T_feed_C": 22.0,
        "T_draw_C": 23.0,
        "P_elec_W": max(0, 45 + 5 * math.sin(t / 20)),
    }


def run(interval_s: float, duration_s: float, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = list(read_sensors_sim(0).keys()) + ["iso_time"]
    t0 = time.monotonic()
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        while True:
            t = time.monotonic() - t0
            if t > duration_s:
                break
            row = read_sensors_sim(t)
            row["iso_time"] = datetime.now(timezone.utc).isoformat()
            w.writerow(row)
            f.flush()
            time.sleep(interval_s)
    meta = {"file": str(out), "duration_s": duration_s, "interval_s": interval_s}
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Logged → {out}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--interval", type=float, default=1.0)
    p.add_argument("--duration", type=float, default=60.0)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = args.out or DATA / f"run_{stamp}.csv"
    run(args.interval, args.duration, out)


if __name__ == "__main__":
    main()
