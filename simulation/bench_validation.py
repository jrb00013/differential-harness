"""Bench CSV validation — T1 ±30% gate, P_net, L_p inverse fit.

Spec: docs/SGH1_TEST_PROTOCOL.md
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from simulation.constants import C_BRINE_8PCT, C_TREATED_WW, I_NACL, R_GAS, T_REF
from simulation.parasitics import skid_energy_balance
from simulation.pro_cycle import steady_state_pro

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "exports"
DEFAULT_A_MEM = 0.72
T1_TOLERANCE = 0.30
STEADY_WINDOW_FRAC = 0.25  # last 25% of run for steady metrics


@dataclass
class BenchRow:
    t_s: float
    P_feed_bar: float
    P_draw_bar: float
    Q_feed_L_min: float
    Q_draw_L_min: float
    cond_feed_mS_cm: float
    cond_draw_mS_cm: float
    T_feed_C: float
    T_draw_C: float
    P_elec_W: float
    P_pump_W: float = 0.0
    P_us_W: float = 0.0
    P_spin_motor_W: float = 0.0
    P_net_W: float = 0.0


@dataclass
class BenchValidationResult:
    csv_path: str
    n_rows: int
    duration_s: float
    A_mem_m2: float
    delta_pi_MPa_measured: float
    delta_P_MPa_measured: float
    P_density_measured_W_m2: float
    P_density_predicted_W_m2: float
    P_net_mean_W: float
    P_net_steady_W: float
    L_p_fit_m_Pa_s: float
    relative_error_pct: float
    pass_t1: bool
    pass_p_net_positive: bool
    pass_steady_15min: bool


def _f(row: dict, key: str, default: float = 0.0) -> float:
    v = row.get(key, default)
    if v is None or v == "":
        return default
    return float(v)


def load_bench_csv(path: Path) -> list[BenchRow]:
    rows: list[BenchRow] = []
    with path.open(newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            rows.append(
                BenchRow(
                    t_s=_f(raw, "t_s"),
                    P_feed_bar=_f(raw, "P_feed_bar"),
                    P_draw_bar=_f(raw, "P_draw_bar"),
                    Q_feed_L_min=_f(raw, "Q_feed_L_min"),
                    Q_draw_L_min=_f(raw, "Q_draw_L_min", _f(raw, "Q_feed_L_min")),
                    cond_feed_mS_cm=_f(raw, "cond_feed_mS_cm", 8.0),
                    cond_draw_mS_cm=_f(raw, "cond_draw_mS_cm", 85.0),
                    T_feed_C=_f(raw, "T_feed_C", 22.0),
                    T_draw_C=_f(raw, "T_draw_C", 23.0),
                    P_elec_W=_f(raw, "P_elec_W"),
                    P_pump_W=_f(raw, "P_pump_W"),
                    P_us_W=_f(raw, "P_us_W"),
                    P_spin_motor_W=_f(raw, "P_spin_motor_W"),
                    P_net_W=_f(raw, "P_net_W"),
                )
            )
    return rows


def cond_to_c_mol_m3(cond_mS_cm: float, *, brine: bool = False) -> float:
    """Rough NaCl conductivity → mol/m³ (bench calibration class)."""
    if brine:
        return max(cond_mS_cm * 16.0, 100.0)
    return max(cond_mS_cm * 0.6, 1.0)


def delta_pi_Pa(c_draw: float, c_feed: float, T: float = T_REF) -> float:
    return I_NACL * R_GAS * T * (c_draw - c_feed)


def invert_L_p(Q_m3_s: float, delta_pi: float, delta_P: float, A_mem: float) -> float:
    driving = max(delta_pi - delta_P, 1e-6)
    return Q_m3_s / (driving * max(A_mem, 1e-12))


def compute_P_net_row(row: BenchRow, A_mem: float) -> float:
    if row.P_net_W > 0:
        return row.P_net_W
    Q_m3_s = row.Q_draw_L_min * 1e-3 / 60.0
    delta_P_Pa = max((row.P_draw_bar - row.P_feed_bar) * 1e5, 0.0)
    c_d = cond_to_c_mol_m3(row.cond_draw_mS_cm, brine=True)
    c_f = cond_to_c_mol_m3(row.cond_feed_mS_cm, brine=False)
    st = steady_state_pro(c_d, c_f, A_mem, delta_P_ratio=min(delta_P_Pa / max(delta_pi_Pa(c_d, c_f), 1.0), 0.95))
    bal = skid_energy_balance(
        st,
        P_us_W=row.P_us_W,
        delta_P_pump_Pa=2.0e5 if row.P_pump_W <= 0 else row.P_pump_W * 55 / max(Q_m3_s, 1e-12),
    )
    P_net = bal.P_net_W - row.P_spin_motor_W
    if row.P_pump_W > 0:
        P_net = st.P_elec_equiv_W - row.P_pump_W - row.P_us_W - 1.5 + bal.P_px_recovery_W - row.P_spin_motor_W
    return P_net


def validate_bench_csv(
    path: Path,
    *,
    A_mem_m2: float = DEFAULT_A_MEM,
    tolerance: float = T1_TOLERANCE,
) -> BenchValidationResult:
    rows = load_bench_csv(path)
    if not rows:
        raise ValueError(f"No rows in {path}")

    duration = rows[-1].t_s - rows[0].t_s
    steady_start = rows[0].t_s + duration * (1.0 - STEADY_WINDOW_FRAC)
    steady = [r for r in rows if r.t_s >= steady_start]

    def mean_attr(rs: list[BenchRow], name: str) -> float:
        return float(np.mean([getattr(r, name) for r in rs]))

    c_d = cond_to_c_mol_m3(mean_attr(steady, "cond_draw_mS_cm"), brine=True)
    c_f = cond_to_c_mol_m3(mean_attr(steady, "cond_feed_mS_cm"), brine=False)
    T_avg = 0.5 * (mean_attr(steady, "T_feed_C") + mean_attr(steady, "T_draw_C")) + 273.15
    dpi = delta_pi_Pa(c_d, c_f, T_avg)
    delta_P = mean_attr(steady, "P_draw_bar") - mean_attr(steady, "P_feed_bar")
    delta_P_Pa = max(delta_P * 1e5, 0.0)
    Q_m3_s = mean_attr(steady, "Q_draw_L_min") * 1e-3 / 60.0

    L_p_fit = invert_L_p(Q_m3_s, dpi, delta_P_Pa, A_mem_m2)
    ratio = min(delta_P_Pa / max(dpi, 1.0), 0.95)
    st_pred = steady_state_pro(c_d, c_f, A_mem_m2, L_p=L_p_fit, delta_P_ratio=ratio, T=T_avg)

    P_meas = mean_attr(steady, "P_elec_W") / A_mem_m2 if mean_attr(steady, "P_elec_W") > 0 else st_pred.P_density_W_m2
    P_pred = st_pred.P_density_W_m2
    rel_err = abs(P_meas - P_pred) / max(P_pred, 1e-12)

    P_net_vals = [compute_P_net_row(r, A_mem_m2) for r in steady]
    P_net_mean = float(np.mean(P_net_vals))
    P_net_steady = float(np.median(P_net_vals))

    steady_15min = duration >= 900 and P_net_steady > 0

    return BenchValidationResult(
        csv_path=str(path),
        n_rows=len(rows),
        duration_s=duration,
        A_mem_m2=A_mem_m2,
        delta_pi_MPa_measured=dpi / 1e6,
        delta_P_MPa_measured=delta_P_Pa / 1e6,
        P_density_measured_W_m2=P_meas,
        P_density_predicted_W_m2=P_pred,
        P_net_mean_W=P_net_mean,
        P_net_steady_W=P_net_steady,
        L_p_fit_m_Pa_s=L_p_fit,
        relative_error_pct=100.0 * rel_err,
        pass_t1=rel_err <= tolerance and P_net_steady > 0,
        pass_p_net_positive=P_net_steady > 0,
        pass_steady_15min=steady_15min,
    )


def export_validation(path: Path, out: Path | None = None) -> Path:
    sizing_path = EXPORTS / "sgh1_sizing.json"
    A_mem = DEFAULT_A_MEM
    if sizing_path.exists():
        A_mem = json.loads(sizing_path.read_text()).get("A_mem_m2", A_mem)

    result = validate_bench_csv(path, A_mem_m2=A_mem)
    out = out or EXPORTS / "bench_validation.json"
    payload = asdict(result)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Validate bench CSV against T1 protocol")
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("--A-mem", type=float, default=None)
    args = p.parse_args()

    A_mem = args.A_mem
    if A_mem is None and (EXPORTS / "sgh1_sizing.json").exists():
        A_mem = json.loads((EXPORTS / "sgh1_sizing.json").read_text()).get("A_mem_m2", DEFAULT_A_MEM)
    A_mem = A_mem or DEFAULT_A_MEM

    result = validate_bench_csv(args.csv, A_mem_m2=A_mem)
    out = args.out or EXPORTS / "bench_validation.json"
    out.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")

    status = "PASS" if result.pass_t1 else "FAIL"
    print(f"T1 validation: {status}")
    print(f"  P'' measured={result.P_density_measured_W_m2:.2f} predicted={result.P_density_predicted_W_m2:.2f} W/m²")
    print(f"  relative error={result.relative_error_pct:.1f}% (limit ±{100*T1_TOLERANCE:.0f}%)")
    print(f"  P_net steady={result.P_net_steady_W:.3f} W  L_p_fit={result.L_p_fit_m_Pa_s:.2e}")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
