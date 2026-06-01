"""Numerical experiments for CHORUS / SGH-1 math validation and paper exports."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

from simulation.acoustic_harvest import harvest_power, sweep_spl
from simulation.constants import (
    C_BRINE_8PCT,
    C_RIVER,
    C_SEAWATER,
    C_TREATED_WW,
    F_FARADAY,
    I_NACL,
    P_BLUE_W_M2,
    R_GAS,
    T_REF,
)
from simulation.membrane_transport import concentration_polarization_profile, effective_driving_force_reduction
from simulation.pro_cycle import steady_state_pro
from simulation.parasitics import skid_energy_balance
from simulation.symbolic_checks import run_symbolic_checks
from simulation.tsc_network import solve_tsc, sweep_injection_current
from simulation.ultrasonic_cp_gain import net_power_with_ultrasound

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "exports"
FIGURES = EXPORTS / "figures"


@dataclass
class SweepPoint:
    x: float
    y: float
    label: str = ""


def nernst_mV(c_high: float, c_low: float, T: float = T_REF) -> float:
    return 1000 * (R_GAS * T / F_FARADAY) * math.log(c_high / max(c_low, 1e-9))


def delta_pi_MPa(c_draw: float, c_feed: float, T: float = T_REF) -> float:
    return I_NACL * R_GAS * T * (c_draw - c_feed) / 1e6


def sweep_delta_p_ratio(
    c_draw: float = C_BRINE_8PCT,
    c_feed: float = C_TREATED_WW,
    A: float = 0.72,
    L_p: float = 1e-12,
    n: int = 41,
) -> list[dict]:
    st0 = steady_state_pro(c_draw, c_feed, A, L_p, delta_P_ratio=0.01)
    out = []
    for r in np.linspace(0.05, 0.95, n):
        st = steady_state_pro(c_draw, c_feed, A, L_p, delta_P_ratio=float(r))
        out.append(
            {
                "ratio": float(r),
                "delta_P_MPa": st.delta_P / 1e6,
                "P_W": st.P_elec_equiv_W,
                "P_W_m2": st.P_density_W_m2,
                "m_dot_L_min": st.m_dot_w * 1e3 * 60,
            }
        )
    out.append({"delta_pi_MPa": st0.delta_pi / 1e6, "P_star_ratio": 0.5})
    return out


def sweep_L_p(
    L_p_values: list[float] | None = None,
    A: float = 0.72,
) -> list[dict]:
    if L_p_values is None:
        L_p_values = [0.5e-12, 1e-12, 2e-12, 4e-12, 6e-12, 8e-12, 1e-11, 1.5e-11]
    rows = []
    for L_p in L_p_values:
        st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, A, L_p=L_p)
        rows.append(
            {
                "L_p": L_p,
                "P_W": st.P_elec_equiv_W,
                "P_W_m2": st.P_density_W_m2,
                "Q_L_min": st.m_dot_w * 1e3 * 60,
                "hits_10W": st.P_elec_equiv_W >= 10.0,
            }
        )
    return rows


def salinity_pair_matrix() -> list[dict]:
    """RED estuary vs PRO brine pairs."""
    pairs = [
        ("Estuary RED", C_SEAWATER, C_RIVER),
        ("SGH-1 PRO", C_BRINE_8PCT, C_TREATED_WW),
        ("Mid brine", 1000.0, 50.0),
        ("High gradient", 1800.0, 2.0),
    ]
    rows = []
    for name, c_d, c_f in pairs:
        st = steady_state_pro(c_d, c_f, A_mem=1.0)
        rows.append(
            {
                "name": name,
                "c_draw": c_d,
                "c_feed": c_f,
                "delta_pi_MPa": st.delta_pi / 1e6,
                "E_N_mV": nernst_mV(c_d, c_f),
                "delta_P_star_bar": st.delta_P_star / 1e5,
                "P_W_m2_at_Lp1e12": st.P_density_W_m2,
            }
        )
    return rows


def sweep_cp(J_w_values: list[float] | None = None) -> list[dict]:
    if J_w_values is None:
        J_w_values = [1e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4]
    rows = []
    for J_w in J_w_values:
        cp = concentration_polarization_profile(J_w=J_w)
        eta = effective_driving_force_reduction(cp)
        rows.append(
            {
                "J_w": J_w,
                "polarization_factor": cp.polarization_factor,
                "driving_force_fraction": eta,
                "power_loss_pct": (1 - eta) * 100,
            }
        )
    return rows


def sweep_ultrasonic(flux_gains: list[float] | None = None, A: float = 0.72) -> list[dict]:
    if flux_gains is None:
        flux_gains = [1.0, 1.1, 1.2, 1.35, 1.5, 1.75, 2.0]
    st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, A)
    rows = []
    for g in flux_gains:
        r = net_power_with_ultrasound(st, flux_gain=g, P_us_W_per_m2=1.5)
        rows.append(
            {
                "flux_gain": g,
                "P_base_W": r.P_pro_baseline_W,
                "P_with_us_W": r.P_pro_us_W,
                "P_us_input_W": r.P_us_input_W,
                "P_us_W": r.P_us_input_W,
                "P_net_gain_W": r.P_net_gain_W,
            }
        )
    return rows


def sweep_red_river_concentration(n: int = 31) -> list[dict]:
    """RED: vary c_river at fixed c_sea."""
    rows = []
    for c_r in np.linspace(5, 200, n):
        st = steady_state_pro(C_SEAWATER, float(c_r), A_mem=1.0)
        E_N = nernst_mV(C_SEAWATER, float(c_r))
        V_oc = 50 * E_N / 1000
        R_int = max(V_oc**2 / (4 * P_BLUE_W_M2), 1e-9)
        P_max = V_oc**2 / (4 * R_int)
        rows.append(
            {
                "c_river": float(c_r),
                "delta_pi_MPa": st.delta_pi / 1e6,
                "E_N_mV": E_N,
                "P_max_W_m2": P_max,
            }
        )
    return rows


def sweep_temperature(T_values: list[float] | None = None, A: float = 0.72) -> list[dict]:
    if T_values is None:
        T_values = [288.15, 293.15, 298.15, 303.15, 308.15]
    rows = []
    for T in T_values:
        st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, A, T=T)
        rows.append(
            {
                "T_K": T,
                "delta_pi_MPa": st.delta_pi / 1e6,
                "P_W": st.P_elec_equiv_W,
                "E_N_mV": st.nernst_V * 1000,
            }
        )
    return rows


def sweep_eta_membrane(n: int = 11) -> list[dict]:
    rows = []
    for eta in np.linspace(0.15, 0.55, n):
        st = steady_state_pro(
            C_BRINE_8PCT, C_TREATED_WW, 0.72, eta_mem=float(eta), eta_hyd=0.55
        )
        rows.append({"eta_mem": float(eta), "P_W": st.P_elec_equiv_W})
    return rows


def sweep_slip_length_red(b_nm: list[float] | None = None) -> list[dict]:
    """Nanopore slip scaling G(b) ∝ (1 + 2b/h), illustrative h = 100 nm."""
    if b_nm is None:
        b_nm = [0, 10, 25, 50, 75, 100]
    h_nm = 100.0
    V_oc = 4.37
    G0 = 4 * P_BLUE_W_M2 / (V_oc**2)
    rows = []
    for b in b_nm:
        G = G0 * (1 + 2 * b / h_nm)
        P_np = 0.25 * G * V_oc**2
        rows.append({"slip_b_nm": b, "G_relative": G / G0, "P_np_W_m2": P_np})
    return rows


def net_energy_scenarios() -> list[dict]:
    st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, 0.72)
    scenarios = [
        ("baseline", 0.0, True),
        ("with_US", 1.08, True),
        ("no_PX", 0.0, False),
        ("high_pump_loss", 0.0, True),
    ]
    rows = []
    for name, P_us, use_px in scenarios:
        bal = skid_energy_balance(
            st,
            P_us_W=P_us,
            delta_P_pump_Pa=4.0e5 if name == "high_pump_loss" else 2.0e5,
            use_px=use_px,
        )
        rows.append(
            {
                "scenario": name,
                "P_pro_W": bal.P_pro_W,
                "P_pump_W": bal.P_pump_W,
                "P_px_W": bal.P_px_recovery_W,
                "P_net_W": bal.P_net_W,
            }
        )
    return rows


def sweep_acoustic_spl() -> list[dict]:
    return [
        {
            "spl_db": h.spl_db,
            "intensity_W_m2": h.intensity_W_m2,
            "power_mW": h.power_W * 1000,
        }
        for h in sweep_spl(60, 100, 21, area_m2=0.5, eta=0.02)
    ]


def column_monte_carlo(N: int = 8000, seed: int = 42) -> dict:
    """Replicate notebook §VII layer MC."""
    rng = np.random.default_rng(seed)
    P_pv = 187.9  # from chorus export steady-state
    P_mfc = 36.75e-6
    layers = {
        "blue_energy": {"P50": P_BLUE_W_M2, "CF": 0.88, "sigma": 0.30, "area": 2e4},
        "pv_hydro": {"P50": P_pv, "CF": 0.20, "sigma": 0.12, "area": 6e5},
        "meg": {"P50": 0.02, "CF": 0.92, "sigma": 0.55, "area": 6e5},
        "smfc": {"P50": P_mfc, "CF": 1.0, "sigma": 0.45, "area": 6e5},
    }
    contrib = {k: np.zeros(N) for k in layers}
    totals = np.zeros(N)
    for i in range(N):
        for k, p in layers.items():
            draw = rng.lognormal(np.log(p["P50"]), p["sigma"])
            power = p["area"] * p["CF"] * draw
            contrib[k][i] = power
            totals[i] += power
    layer_stats = {}
    for k in layers:
        layer_stats[k] = {
            "median_MW": float(np.median(contrib[k]) / 1e6),
            "p10_MW": float(np.percentile(contrib[k], 10) / 1e6),
            "p90_MW": float(np.percentile(contrib[k], 90) / 1e6),
            "share_of_median_column_pct": float(
                100 * np.median(contrib[k]) / max(np.median(totals), 1e-12)
            ),
        }
    return {
        "N": N,
        "parcel_area_m2": 1e6,
        "column_MW_median": float(np.median(totals) / 1e6),
        "column_MW_p10": float(np.percentile(totals, 10) / 1e6),
        "column_MW_p90": float(np.percentile(totals, 90) / 1e6),
        "layers": layer_stats,
    }


def gibbs_mixing_ceiling_MW(c_sea: float, c_river: float, Q_m3_s: float = 500.0) -> float:
    """Ideal mixing power ceiling Δπ·Q with estuary Δπ."""
    dpi = I_NACL * R_GAS * T_REF * (c_sea - c_river)
    return dpi * Q_m3_s / 1e6


def run_all() -> dict:
    A = 0.72
    st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, A)
    dp_sweep = sweep_delta_p_ratio()
    p_at_star = max((p for p in dp_sweep if "ratio" in p and abs(p["ratio"] - 0.5) < 0.02), key=lambda x: x["P_W"], default=dp_sweep[0])

    return {
        "meta": {
            "T_K": T_REF,
            "description": "CHORUS/SGH-1 math experiments for Joseph Black PoC paper",
        },
        "sg_h1_baseline": {
            "c_draw": C_BRINE_8PCT,
            "c_feed": C_TREATED_WW,
            "A_m2": A,
            "delta_pi_MPa": st.delta_pi / 1e6,
            "delta_P_star_bar": st.delta_P_star / 1e5,
            "E_N_mV": st.nernst_V * 1000,
            "P_at_delta_P_star_W": p_at_star.get("P_W", st.P_elec_equiv_W),
            "P_default_Lp_W": st.P_elec_equiv_W,
            "P_density_W_m2": st.P_density_W_m2,
            "Q_L_min": st.m_dot_w * 1e3 * 60,
        },
        "estuary_RED": {
            "E_N_mV": nernst_mV(C_SEAWATER, C_RIVER),
            "delta_pi_MPa": delta_pi_MPa(C_SEAWATER, C_RIVER),
            "P_max_W_m2": P_BLUE_W_M2,
            "P_mix_ceiling_MW": gibbs_mixing_ceiling_MW(C_SEAWATER, C_RIVER),
        },
        "sweeps": {
            "delta_P_ratio": dp_sweep,
            "L_p": sweep_L_p(),
            "salinity_pairs": salinity_pair_matrix(),
            "concentration_polarization": sweep_cp(),
            "ultrasonic_gain": sweep_ultrasonic(),
            "acoustic_SPL": sweep_acoustic_spl(),
            "red_river_c": sweep_red_river_concentration(),
            "temperature": sweep_temperature(),
            "eta_membrane": sweep_eta_membrane(),
            "slip_length_red": sweep_slip_length_red(),
            "net_energy": net_energy_scenarios(),
        },
        "column_monte_carlo": column_monte_carlo(),
        "tsc": {
            "baseline": asdict(solve_tsc()),
            "injection_sweep": sweep_injection_current(),
        },
        "symbolic_checks": run_symbolic_checks(),
    }


def export(path: Path | None = None) -> Path:
    path = path or EXPORTS / "paper_experiments.json"
    data = run_all()
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    p = export()
    print(f"Wrote {p}")
