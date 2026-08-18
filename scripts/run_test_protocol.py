#!/usr/bin/env python3
"""Run SGH-1 bench test protocol (T0/T1/T1b/T1c) with auto validation and checkpointing.

Each logging/validation sub-run is a named "step". After every step
completes, a checkpoint file (`<out_dir>/checkpoint.json`) is updated
recording which steps are done and their output paths. Pass `--resume`
to re-enter a protocol run at the first incomplete step instead of
restarting from T0 -- a bench disconnect, fixture failure, or crash
partway through no longer throws away completed phases.
"""

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


class Checkpoint:
    """Tracks completed steps for a protocol run so it can be resumed."""

    def __init__(self, path: Path):
        self.path = path
        if path.exists():
            self.state: dict = json.loads(path.read_text(encoding="utf-8"))
        else:
            self.state = {"completed_steps": {}}

    def is_done(self, step_id: str) -> bool:
        return step_id in self.state["completed_steps"]

    def result(self, step_id: str):
        return self.state["completed_steps"][step_id]

    def mark_done(self, step_id: str, result) -> None:
        self.state["completed_steps"][step_id] = result
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")


def _step(ckpt: Checkpoint, step_id: str, fn, *, resume: bool):
    """Run fn() and record it under step_id, unless --resume finds it already done."""
    if resume and ckpt.is_done(step_id):
        print(f"[resume] skipping completed step: {step_id}")
        return ckpt.result(step_id)
    result = fn()
    serializable = str(result) if isinstance(result, Path) else [str(r) for r in result]
    ckpt.mark_done(step_id, serializable)
    return result


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


def run_t0(out_dir: Path, interval: float, ckpt: Checkpoint, resume: bool) -> list[Path]:
    leak = _step(
        ckpt, "T0.leak",
        lambda: _run_logger("T0", "leak", 600, out_dir / "T0_leak.csv", interval=interval),
        resume=resume,
    )
    ramp = _step(
        ckpt, "T0.ramp",
        lambda: _run_logger("T0", "ramp", 1800, out_dir / "T0_ramp.csv", interval=interval),
        resume=resume,
    )
    return [Path(leak), Path(ramp)]


def run_t1(out_dir: Path, interval: float, ckpt: Checkpoint, resume: bool) -> Path:
    csv_path = _step(
        ckpt, "T1.baseline",
        lambda: _run_logger("T1", "baseline", 3600, out_dir / "T1_baseline.csv", interval=interval),
        resume=resume,
    )
    csv_path = Path(csv_path)
    _step(ckpt, "T1.validate", lambda: _validate(csv_path, out_dir), resume=resume)
    return csv_path


def run_t1b(out_dir: Path, interval: float, ckpt: Checkpoint, resume: bool) -> list[Path]:
    configs = [
        ("T1b_A", "us_off", False, False),
        ("T1b_B", "us_phased", True, True),
        ("T1b_C", "aor_full", True, True),
    ]
    paths = []
    for phase, name, us_on, coherent in configs:
        p = _step(
            ckpt,
            f"T1b.{phase}",
            lambda phase=phase, name=name, us_on=us_on, coherent=coherent: _run_logger(
                "T1b", name, 3600, out_dir / f"T1b_{phase}.csv",
                us_on=us_on, us_coherent=coherent, interval=interval,
            ),
            resume=resume,
        )
        paths.append(Path(p))
    return paths


def run_t1c(out_dir: Path, interval: float, omega_rpm: float, ckpt: Checkpoint, resume: bool) -> list[Path]:
    flat = _step(
        ckpt, "T1c.flat",
        lambda: _run_logger("T1c", "flat", 3600, out_dir / "T1c_flat.csv", omega_rpm=0.0, interval=interval),
        resume=resume,
    )
    spin = _step(
        ckpt, "T1c.spin",
        lambda: _run_logger("T1c", "spin", 3600, out_dir / "T1c_spin.csv", omega_rpm=omega_rpm, interval=interval),
        resume=resume,
    )
    spin_path = Path(spin)
    _step(ckpt, "T1c.validate", lambda: _validate(spin_path, out_dir), resume=resume)
    return [Path(flat), spin_path]


def main() -> None:
    p = argparse.ArgumentParser(description="SGH-1 test protocol runner")
    p.add_argument("--test", choices=["T0", "T1", "T1b", "T1c", "all"], required=True)
    p.add_argument("--interval", type=float, default=1.0)
    p.add_argument("--omega-rpm", type=float, default=60.0, help="T1c spin rate")
    p.add_argument("--out-dir", type=Path, default=None)
    p.add_argument(
        "--resume",
        action="store_true",
        help="resume from checkpoint.json in --out-dir instead of restarting from scratch",
    )
    args = p.parse_args()

    stamp = datetime.now().strftime("%Y%m%d")
    out_dir = args.out_dir or DATA / f"{args.test}_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    ckpt = Checkpoint(out_dir / "checkpoint.json")
    if args.resume and ckpt.state["completed_steps"]:
        print(f"Resuming from checkpoint: {sorted(ckpt.state['completed_steps'])}")
    elif not args.resume and ckpt.path.exists():
        print(f"Warning: existing checkpoint at {ckpt.path} found but --resume not passed; steps will rerun.")

    manifest: dict = {"test": args.test, "out_dir": str(out_dir), "runs": []}

    if args.test in ("T0", "all"):
        manifest["runs"].extend([str(p) for p in run_t0(out_dir, args.interval, ckpt, args.resume)])
    if args.test in ("T1", "all"):
        manifest["runs"].append(str(run_t1(out_dir, args.interval, ckpt, args.resume)))
    if args.test in ("T1b", "all"):
        manifest["runs"].extend([str(p) for p in run_t1b(out_dir, args.interval, ckpt, args.resume)])
    if args.test in ("T1c", "all"):
        manifest["runs"].extend(
            [str(p) for p in run_t1c(out_dir, args.interval, args.omega_rpm, ckpt, args.resume)]
        )

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Protocol {args.test} complete → {out_dir}")
    print(f"Manifest → {manifest_path}")
    print(f"Checkpoint → {ckpt.path}")


if __name__ == "__main__":
    main()
