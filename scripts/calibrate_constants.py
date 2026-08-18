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
import math
from pathlib import Path

import numpy as np
from scipy import stats

from daq.logger import read_sensors_sim
from simulation.bench_validation import (
    cond_to_c_mol_m3,
    delta_pi_Pa,
    invert_L_p,
    load_bench_csv,
    validate_bench_csv,
)
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


def _fit_L_p_from_rows(rows: list, A_mem_m2: float) -> float:
    """Fit L_p from a chronological slice of BenchRow objects, using the
    same math as simulation.bench_validation.validate_bench_csv's steady
    window, but on a caller-supplied window rather than the fixed
    last-25%-of-run steady window. Shared by fit_L_p_time_series() below."""
    if not rows:
        return 0.0

    def mean_attr(name: str) -> float:
        return float(np.mean([getattr(r, name) for r in rows]))

    c_d = cond_to_c_mol_m3(mean_attr("cond_draw_mS_cm"), brine=True)
    c_f = cond_to_c_mol_m3(mean_attr("cond_feed_mS_cm"), brine=False)
    T_avg = 0.5 * (mean_attr("T_feed_C") + mean_attr("T_draw_C")) + 273.15
    dpi = delta_pi_Pa(c_d, c_f, T_avg)
    delta_P_Pa = max((mean_attr("P_draw_bar") - mean_attr("P_feed_bar")) * 1e5, 0.0)
    Q_m3_s = mean_attr("Q_draw_L_min") * 1e-3 / 60.0
    return invert_L_p(Q_m3_s, dpi, delta_P_Pa, A_mem_m2)


def fit_L_p_time_series(csv_path: Path, A_mem_m2: float = 0.72, n_segments: int = 4) -> dict:
    """Fit L_p in `n_segments` chronological sub-windows of a single bench
    run and report the percent decline from the first to the last
    segment -- the headline fouling-resistance metric in
    docs/FOULING_TEST_PROTOCOL.md's T1f.2 flux-decline measurement.

    A membrane fouling over the course of a run manifests as L_p
    (permeability) declining over time even though feed/draw
    conditions are nominally held steady: fouling deposits add
    additional hydraulic resistance the steady-state PRO model does not
    otherwise account for. Splitting one CSV into chronological
    segments and re-fitting L_p per segment turns that decline into a
    measurable curve instead of a single pooled number that would average
    it away.
    """
    rows = load_bench_csv(csv_path)
    if len(rows) < n_segments:
        return {
            "source_csv": str(csv_path),
            "sufficient_data": False,
            "reason": f"need >= {n_segments} rows for {n_segments} segments, got {len(rows)}",
        }

    segment_size = len(rows) // n_segments
    segments = []
    for i in range(n_segments):
        start = i * segment_size
        end = (i + 1) * segment_size if i < n_segments - 1 else len(rows)
        seg_rows = rows[start:end]
        L_p = _fit_L_p_from_rows(seg_rows, A_mem_m2)
        segments.append(
            {
                "segment_index": i,
                "t_start_s": seg_rows[0].t_s,
                "t_end_s": seg_rows[-1].t_s,
                "n_rows": len(seg_rows),
                "L_p_fit_m_Pa_s": L_p,
            }
        )

    first_valid = next((s["L_p_fit_m_Pa_s"] for s in segments if s["L_p_fit_m_Pa_s"] > 0), None)
    last_valid = next((s["L_p_fit_m_Pa_s"] for s in reversed(segments) if s["L_p_fit_m_Pa_s"] > 0), None)

    if first_valid is None or last_valid is None:
        decline_pct = None
    else:
        decline_pct = 100.0 * (first_valid - last_valid) / first_valid

    return {
        "source_csv": str(csv_path),
        "data_provenance": _row_data_provenance(csv_path),
        "sufficient_data": True,
        "n_segments": n_segments,
        "segments": segments,
        "L_p_first_segment_m_Pa_s": first_valid,
        "L_p_last_segment_m_Pa_s": last_valid,
        "L_p_decline_pct": decline_pct,
        "note": (
            "L_p_decline_pct > 0 indicates permeability dropped over the "
            "course of this run (consistent with fouling); see "
            "docs/FOULING_TEST_PROTOCOL.md T1f.2 for the proposed pass/fail "
            "threshold and its honest caveats."
        ),
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


def fit_L_p_aggregate(csv_paths: list[Path], A_mem_m2: float = 0.72, confidence: float = 0.95) -> dict:
    """Fit L_p per-run across multiple bench CSVs and report an aggregate
    with a t-distribution confidence interval, flagging outlier runs.

    Round-2 addition (docs/ROADMAP_ROUND2.md R2.3): an operator running
    T1 several times previously had no way to see whether the fits
    agreed run-to-run or one run was an outlier -- only a single pooled
    number. This reports per-run values, mean, sample standard
    deviation, a `confidence`-level CI (via scipy.stats.t, since the
    true population std is unknown and sample sizes are typically
    small), and flags any run more than 2 standard deviations from the
    mean.
    """
    per_run = [fit_L_p(p, A_mem_m2=A_mem_m2) for p in csv_paths]
    values = np.array([r["L_p_fit_m_Pa_s"] for r in per_run if r["L_p_fit_m_Pa_s"] > 0])
    n = values.size

    if n == 0:
        return {
            "n_runs": 0,
            "per_run": per_run,
            "mean_m_Pa_s": None,
            "std_m_Pa_s": None,
            "confidence": confidence,
            "ci_low_m_Pa_s": None,
            "ci_high_m_Pa_s": None,
            "outlier_runs": [],
            "note": "No valid L_p fits available across the supplied runs.",
        }

    mean = float(np.mean(values))
    std = float(np.std(values, ddof=1)) if n > 1 else 0.0

    if n > 1 and std > 0:
        sem = std / math.sqrt(n)
        t_crit = float(stats.t.ppf(0.5 + confidence / 2.0, df=n - 1))
        ci_low = mean - t_crit * sem
        ci_high = mean + t_crit * sem
    else:
        # A single run (or zero-variance runs) has no meaningful CI half-width.
        ci_low = ci_high = mean

    # Outlier detection uses the median + MAD (median absolute deviation),
    # not mean/std: with small n (typical for a handful of bench runs), a
    # single genuine outlier drags the mean and inflates the std enough
    # that a naive z-score often fails to flag the very point that caused
    # it (masking). The MAD-based "robust z-score" (Iglewicz & Hoaglin,
    # 1993) is resistant to that failure mode.
    outliers = []
    median = float(np.median(values))
    mad = float(np.median(np.abs(values - median)))
    if mad > 0:
        for r in per_run:
            v = r["L_p_fit_m_Pa_s"]
            if v <= 0:
                continue
            robust_z = 0.6745 * (v - median) / mad
            if abs(robust_z) > 3.5:
                outliers.append({"source_csv": r["source_csv"], "L_p_fit_m_Pa_s": v, "robust_z_score": robust_z})

    return {
        "n_runs": n,
        "per_run": per_run,
        "mean_m_Pa_s": mean,
        "std_m_Pa_s": std,
        "confidence": confidence,
        "ci_low_m_Pa_s": ci_low,
        "ci_high_m_Pa_s": ci_high,
        "outlier_runs": outliers,
        "note": (
            "Aggregate fit across simulated bench CSVs (see docs/ROADMAP.md M6 -- "
            "real T1 bench data has not been collected yet). A run flagged as an "
            "outlier (>2 sigma from the pooled mean) warrants operator review "
            "before being folded into simulation/constants.py."
        ),
    }


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
    p.add_argument(
        "--aggregate",
        action="store_true",
        help="also fit L_p per-CSV and report a multi-run mean/CI/outlier summary",
    )
    p.add_argument("--confidence", type=float, default=0.95, help="CI level for --aggregate")
    p.add_argument(
        "--time-series",
        action="store_true",
        help="fit L_p in chronological sub-windows per CSV (docs/FOULING_TEST_PROTOCOL.md T1f.2 flux-decline check)",
    )
    p.add_argument("--segments", type=int, default=4, help="number of chronological segments for --time-series")
    args = p.parse_args()

    csv_paths = args.csv or sorted(DATA.glob("*.csv"))
    if not csv_paths:
        raise SystemExit(f"No bench CSVs found in {DATA}")

    result = calibrate(csv_paths, A_mem_m2=args.a_mem)
    if args.aggregate:
        result["L_p_aggregate"] = fit_L_p_aggregate(csv_paths, A_mem_m2=args.a_mem, confidence=args.confidence)
    if args.time_series:
        result["L_p_time_series"] = [
            fit_L_p_time_series(p_csv, A_mem_m2=args.a_mem, n_segments=args.segments) for p_csv in csv_paths
        ]

    out = args.out or EXPORTS / "constant_calibration.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
