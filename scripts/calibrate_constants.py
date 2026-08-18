#!/usr/bin/env python3
"""Fit L_p (membrane permeability) and RPM->torque coefficient from bench CSVs.

This is the calibration pipeline referenced in docs/ROADMAP.md milestone
M2. It consumes the same bench CSV schema written by daq/logger.py and
daq/serial_sensors.py.

IMPORTANT — data provenance: every CSV currently in data/bench/ was
produced by the simulator (daq.logger.read_sensors_sim), NOT a real
CHORUS-SGH-1 bench run. This script labels every fit's
"data_provenance" field accordingly and refuses to claim "real" unless
the source CSV rows contain data_source == "hardware" (the tag written
by the real serial ingestion path in daq/serial_sensors.py). Real T1c
bench data (varying RPM under load) does not exist yet in this repo, so
when no CSV supplies real RPM/torque variation, this script generates a
clearly-labeled synthetic demonstration dataset (via
daq.logger.read_sensors_sim swept over RPM) purely to validate that the
fitting math recovers a known-good coefficient. That demonstration
result is marked "synthetic_demo": true and must not be mistaken for a
real calibration.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from daq.logger import read_sensors_sim
from simulation.bench_validation import load_bench_csv, validate_bench_csv
from simulation.constants import RPM_TO_RAD_S

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "bench"
EXPORTS = ROOT / "exports"


def _row_data_provenance(path: Path) -> str:
    """Inspect a CSV's data_source column (if present) to label provenance."""
    try:
        import csv

        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            sources = {row.get("data_source", "") for row in reader}
    except Exception:
        return "unknown"
    if sources == {"hardware"}:
        return "real"
    if "hardware" in sources:
        return "mixed"
    return "simulated"


def fit_L_p(csv_path: Path, A_mem_m2: float = 0.72) -> dict:
    """Fit membrane permeability L_p from a bench CSV's steady-state window."""
    val = validate_bench_csv(csv_path, A_mem_m2=A_mem_m2)
    return {
        "source_csv": str(csv_path),
        "data_provenance": _row_data_provenance(csv_path),
        "L_p_fit_m_Pa_s": val.L_p_fit_m_Pa_s,
        "P_density_measured_W_m2": val.P_density_measured_W_m2,
        "n_rows": val.n_rows,
        "duration_s": val.duration_s,
    }


def fit_rpm_torque(rpm: np.ndarray, power_w: np.ndarray) -> dict:
    """OLS fit of torque_Nm = slope * rpm (forced through the origin) from
    (rpm, P_spin_motor_W) samples, where torque = P / omega_rad_s.

    Returns the fitted slope (Nm per rpm) plus the equivalent
    tau_at_100rpm_Nm used by simulation.constants.tau_spin_from_rpm, and
    basic fit-quality stats.
    """
    mask = rpm > 1e-9
    rpm_f = rpm[mask]
    power_f = power_w[mask]
    if rpm_f.size < 2:
        return {
            "sufficient_data": False,
            "reason": f"need >=2 nonzero-RPM samples, got {rpm_f.size}",
        }

    omega_rad_s = rpm_f * RPM_TO_RAD_S
    torque_Nm = power_f / omega_rad_s

    # Force-through-origin least squares: slope minimizing sum((torque - k*rpm)^2)
    slope = float(np.sum(rpm_f * torque_Nm) / np.sum(rpm_f * rpm_f))
    residuals = torque_Nm - slope * rpm_f
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((torque_Nm - np.mean(torque_Nm)) ** 2)) or 1e-12
    r2 = 1.0 - ss_res / ss_tot

    return {
        "sufficient_data": True,
        "n_samples": int(rpm_f.size),
        "slope_Nm_per_rpm": slope,
        "tau_at_100rpm_Nm": slope * 100.0,
        "r_squared": r2,
    }


def _synthetic_torque_demo() -> dict:
    """Generate an in-memory, clearly-labeled synthetic RPM sweep and fit it.

    This validates the fitting algorithm (fit_rpm_torque) recovers the
    known slope baked into daq.logger.read_sensors_sim's P_spin model,
    since no real (or even simulated-CSV) varying-RPM dataset exists in
    data/bench/ yet. Not written to disk; used only to prove correctness.
    """
    rpms = np.linspace(20, 300, 15)
    rows = [read_sensors_sim(0.0, omega_rpm=float(r)) for r in rpms]
    rpm_arr = np.array([r["omega_rpm"] for r in rows])
    power_arr = np.array([r["P_spin_motor_W"] for r in rows])
    fit = fit_rpm_torque(rpm_arr, power_arr)
    fit["synthetic_demo"] = True
    fit["data_provenance"] = "synthetic_demo_in_memory"
    fit["note"] = (
        "Generated from daq.logger.read_sensors_sim's built-in P_spin model "
        "purely to validate the fitting algorithm. NOT a real or bench-CSV "
        "calibration. Real T1c bench data (varying RPM under physical load) "
        "is still required."
    )
    return fit


def calibrate(csv_paths: list[Path], A_mem_m2: float = 0.72) -> dict:
    l_p_fits = [fit_L_p(p, A_mem_m2=A_mem_m2) for p in csv_paths]

    # Look for real RPM variation across the supplied CSVs.
    all_rpm: list[float] = []
    all_power: list[float] = []
    for p in csv_paths:
        rows = load_bench_csv(p)
        for r in rows:
            omega_rpm = getattr(r, "omega_rpm", 0.0)
            if omega_rpm:
                all_rpm.append(omega_rpm)
                all_power.append(r.P_spin_motor_W)

    if all_rpm:
        torque_fit = fit_rpm_torque(np.array(all_rpm), np.array(all_power))
        torque_fit["data_provenance"] = "simulated" if all(
            _row_data_provenance(p) != "real" for p in csv_paths
        ) else "real"
    else:
        torque_fit = _synthetic_torque_demo()

    l_p_values = [f["L_p_fit_m_Pa_s"] for f in l_p_fits if f["L_p_fit_m_Pa_s"] > 0]
    l_p_mean = float(np.mean(l_p_values)) if l_p_values else None

    return {
        "sources": [str(p) for p in csv_paths],
        "L_p_fits": l_p_fits,
        "L_p_fit_mean_m_Pa_s": l_p_mean,
        "rpm_torque_fit": torque_fit,
        "status": (
            "Real T1/T1c bench data has not been collected yet; all fits above "
            "are derived from simulated data (see docs/ROADMAP.md M6). Update "
            "simulation/constants.py only after review against real hardware runs."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Fit L_p and RPM->torque constants from bench CSVs")
    p.add_argument("--csv", type=Path, nargs="*", default=None, help="bench CSV(s); default: all in data/bench/")
    p.add_argument("--a-mem", type=float, default=0.72)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    csv_paths = args.csv or sorted(DATA.glob("*.csv"))
    if not csv_paths:
        raise SystemExit(f"No bench CSVs found in {DATA}")

    result = calibrate(csv_paths, A_mem_m2=args.a_mem)
    out = args.out or EXPORTS / "constant_calibration.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
