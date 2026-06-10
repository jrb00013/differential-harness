"""Inverse fit bench CSV → calibration constants export."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from simulation.bench_validation import DEFAULT_A_MEM, export_validation, load_bench_csv, validate_bench_csv
from simulation.differential_tink import sweep_eta_tink
from simulation.vortex_osmotic_hydro import breakeven_omega, sweep_omega

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "exports"


def fit_from_csv(path: Path, A_mem_m2: float = DEFAULT_A_MEM) -> dict:
    val = validate_bench_csv(path, A_mem_m2=A_mem_m2)
    rows = load_bench_csv(path)

    omega_vals = [r for r in rows if hasattr(r, "omega_rpm") or True]
    _ = omega_vals  # reserved for future omega column in CSV

    be = breakeven_omega(A_mem=A_mem_m2)
    udt_peak = max(sweep_eta_tink(11), key=lambda x: x["P_net_gain_W"])

    return {
        "source_csv": str(path),
        "L_p_fit_m_Pa_s": val.L_p_fit_m_Pa_s,
        "P_density_measured_W_m2": val.P_density_measured_W_m2,
        "P_net_steady_W": val.P_net_steady_W,
        "pass_t1": val.pass_t1,
        "eta_tink_suggested": udt_peak["eta_tink"] if udt_peak["P_net_gain_W"] > 0 else None,
        "voh_breakeven_omega_rad_s": be["omega_rad_s"] if be else None,
        "voh_breakeven_rpm": be["rpm"] if be else None,
        "notes": "Review before updating simulation/constants.py",
    }


def export(path: Path, out: Path | None = None) -> Path:
    export_validation(path)
    sizing = EXPORTS / "sgh1_sizing.json"
    A_mem = DEFAULT_A_MEM
    if sizing.exists():
        A_mem = json.loads(sizing.read_text()).get("A_mem_m2", A_mem)

    payload = fit_from_csv(path, A_mem_m2=A_mem)
    out = out or EXPORTS / "bench_calibration.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()
    out = export(args.csv, args.out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
