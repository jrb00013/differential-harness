#!/usr/bin/env python3
"""Bench DAQ logger for CHORUS-SGH-1 (simulated or serial sensors)."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "bench"

BASE_FIELDS = [
    "t_s",
    "P_feed_bar",
    "P_draw_bar",
    "Q_feed_L_min",
    "Q_draw_L_min",
    "cond_feed_mS_cm",
    "cond_draw_mS_cm",
    "T_feed_C",
    "T_draw_C",
    "P_elec_W",
]

PROTOCOL_FIELDS = [
    "test_id",
    "phase",
    "us_on",
    "us_phase_coherent",
    "omega_rpm",
    "P_us_W",
    "P_pump_W",
    "P_spin_motor_W",
    "P_net_W",
]

ALL_FIELDS = BASE_FIELDS + PROTOCOL_FIELDS + ["iso_time"]


def read_sensors_sim(
    t: float,
    *,
    test_id: str = "dev",
    phase: str = "baseline",
    us_on: bool = False,
    us_coherent: bool = False,
    omega_rpm: float = 0.0,
) -> dict[str, float | str | bool]:
    """Simulated sensor stream for dev without hardware."""
    P_elec = max(0, 1.66 + 0.15 * math.sin(t / 20))
    P_us = 1.08 if us_on else 0.0
    P_pump = 0.35
    P_spin = 0.02 * (omega_rpm / 60.0) ** 2
    P_net = P_elec - P_us - P_pump - 1.5 + 0.4 - P_spin

    return {
        "t_s": t,
        "P_feed_bar": 0.5 + 0.05 * math.sin(t / 10),
        "P_draw_bar": 34.0 + 0.5 * math.sin(t / 7),
        "Q_feed_L_min": 2.0 + 0.2 * math.sin(t / 5),
        "Q_draw_L_min": 0.15 + 0.01 * math.sin(t / 8),
        "cond_feed_mS_cm": 8.0,
        "cond_draw_mS_cm": 85.0,
        "T_feed_C": 22.0,
        "T_draw_C": 23.0,
        "P_elec_W": P_elec,
        "test_id": test_id,
        "phase": phase,
        "us_on": us_on,
        "us_phase_coherent": us_coherent,
        "omega_rpm": omega_rpm,
        "P_us_W": P_us,
        "P_pump_W": P_pump,
        "P_spin_motor_W": P_spin,
        "P_net_W": max(P_net, 0.0),
    }


def run(
    interval_s: float,
    duration_s: float,
    out: Path,
    *,
    test_id: str = "dev",
    phase: str = "baseline",
    us_on: bool = False,
    us_coherent: bool = False,
    omega_rpm: float = 0.0,
) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ALL_FIELDS)
        w.writeheader()
        while True:
            t = time.monotonic() - t0
            if t > duration_s:
                break
            row = read_sensors_sim(
                t,
                test_id=test_id,
                phase=phase,
                us_on=us_on,
                us_coherent=us_coherent,
                omega_rpm=omega_rpm,
            )
            row["iso_time"] = datetime.now(timezone.utc).isoformat()
            w.writerow(row)
            f.flush()
            time.sleep(interval_s)
    meta = {
        "file": str(out),
        "duration_s": duration_s,
        "interval_s": interval_s,
        "test_id": test_id,
        "phase": phase,
        "us_on": us_on,
        "omega_rpm": omega_rpm,
    }
    out.with_suffix(".meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Logged → {out}")


def main() -> None:
    p = argparse.ArgumentParser(description="CHORUS-SGH-1 bench DAQ logger")
    p.add_argument("--interval", type=float, default=1.0)
    p.add_argument("--duration", type=float, default=60.0)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--test", type=str, default="dev", help="T0|T1|T1b|T1c")
    p.add_argument("--phase", type=str, default="baseline")
    p.add_argument("--us-on", action="store_true")
    p.add_argument("--us-coherent", action="store_true")
    p.add_argument("--omega-rpm", type=float, default=0.0)
    args = p.parse_args()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = args.out or DATA / f"{args.test}_{args.phase}_{stamp}.csv"
    run(
        args.interval,
        args.duration,
        out,
        test_id=args.test,
        phase=args.phase,
        us_on=args.us_on,
        us_coherent=args.us_coherent,
        omega_rpm=args.omega_rpm,
    )


if __name__ == "__main__":
    main()
