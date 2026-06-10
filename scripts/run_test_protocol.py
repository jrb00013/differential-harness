#!/usr/bin/env python3
"""Run SGH-1 bench test protocol (T0/T1/T1b/T1c) with auto validation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "bench"
EXPORTS = ROOT / "exports"


def _run_logger(
    test_id: str,
    phase: str,
    duration_s: float,
    out: Path,
    *,
    us_on: bool = False,
    us_coherent: bool = False,
    omega_rpm: float = 0.0,
    interval: float = 1.0,
) -> Path:
    cmd = [
        sys.executable,
        "-m",
        "daq.logger",
        "--test",
        test_id,
        "--phase",
        phase,
        "--duration",
        str(duration_s),
        "--interval",
        str(interval),
        "--out",
        str(out),
        "--omega-rpm",
        str(omega_rpm),
    ]
    if us_on:
        cmd.append("--us-on")
    if us_coherent:
        cmd.append("--us-coherent")
    subprocess.run(cmd, check=True, cwd=ROOT)
    return out


def _validate(csv_path: Path, out_dir: Path) -> Path:
    val_out = out_dir / "bench_validation.json"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "simulation.bench_validation",
            "--csv",
            str(csv_path),
            "--out",
            str(val_out),
        ],
        check=True,
        cwd=ROOT,
    )
    cal_out = out_dir / "bench_calibration.json"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "simulation.inverse_fit",
            "--csv",
            str(csv_path),
            "--out",
            str(cal_out),
        ],
        check=True,
        cwd=ROOT,
    )
    return val_out


def run_t0(out_dir: Path, interval: float) -> list[Path]:
    paths = []
    paths.append(_run_logger("T0", "leak", 600, out_dir / "T0_leak.csv", interval=interval))
    paths.append(_run_logger("T0", "ramp", 1800, out_dir / "T0_ramp.csv", interval=interval))
    return paths


def run_t1(out_dir: Path, interval: float) -> Path:
    csv_path = _run_logger("T1", "baseline", 3600, out_dir / "T1_baseline.csv", interval=interval)
    _validate(csv_path, out_dir)
    return csv_path


def run_t1b(out_dir: Path, interval: float) -> list[Path]:
    configs = [
        ("T1b_A", "us_off", False, False),
        ("T1b_B", "us_phased", True, True),
        ("T1b_C", "aor_full", True, True),
    ]
    paths = []
    for phase, name, us_on, coherent in configs:
        p = _run_logger("T1b", name, 3600, out_dir / f"T1b_{phase}.csv", us_on=us_on, us_coherent=coherent, interval=interval)
        paths.append(p)
    return paths


def run_t1c(out_dir: Path, interval: float, omega_rpm: float) -> list[Path]:
    flat = _run_logger("T1c", "flat", 3600, out_dir / "T1c_flat.csv", omega_rpm=0.0, interval=interval)
    spin = _run_logger("T1c", "spin", 3600, out_dir / "T1c_spin.csv", omega_rpm=omega_rpm, interval=interval)
    _validate(spin, out_dir)
    return [flat, spin]


def main() -> None:
    p = argparse.ArgumentParser(description="SGH-1 test protocol runner")
    p.add_argument("--test", choices=["T0", "T1", "T1b", "T1c", "all"], required=True)
    p.add_argument("--interval", type=float, default=1.0)
    p.add_argument("--omega-rpm", type=float, default=60.0, help="T1c spin rate")
    p.add_argument("--out-dir", type=Path, default=None)
    args = p.parse_args()

    stamp = datetime.now().strftime("%Y%m%d")
    out_dir = args.out_dir or DATA / f"{args.test}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict = {"test": args.test, "out_dir": str(out_dir), "runs": []}

    if args.test in ("T0", "all"):
        manifest["runs"].extend([str(p) for p in run_t0(out_dir, args.interval)])
    if args.test in ("T1", "all"):
        manifest["runs"].append(str(run_t1(out_dir, args.interval)))
    if args.test in ("T1b", "all"):
        manifest["runs"].extend([str(p) for p in run_t1b(out_dir, args.interval)])
    if args.test in ("T1c", "all"):
        manifest["runs"].extend([str(p) for p in run_t1c(out_dir, args.interval, args.omega_rpm)])

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Protocol {args.test} complete → {out_dir}")
    print(f"Manifest → {manifest_path}")


if __name__ == "__main__":
    main()
