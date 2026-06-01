"""Calibrate CHORUS/SGH-1 math to published real-world data."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from simulation.constants import C_RIVER, C_SEAWATER, R_GAS, T_REF, I_NACL
from simulation.pro_cycle import steady_state_pro
from simulation.tsc_network import solve_tsc

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "exports"

# Perth / WaterReuse: brine ~70 g/L ≈ 1.2 mol/L NaCl → 1200 mol/m³
C_BRINE_PERth_70gL = 1200.0
C_BRINE_HIGH_8WT = 1400.0  # ~8 wt% class for SGH-1 nominal
C_WW_EFFLUENT_LOW = 5.0
C_WW_EFFLUENT_MID = 15.0  # ~900 mg/L TDS order


@dataclass(frozen=True)
class PlantCaseStudy:
    name: str
    location: str
    technology: str
    power_W: float | None
    power_density_W_m2: float | None
    flow_m3_day: float | None
    c_high_mol_m3: float | None
    c_low_mol_m3: float | None
    energy_kWh_m3: float | None
    status: str
    source: str


CASE_STUDIES: list[PlantCaseStudy] = [
    PlantCaseStudy(
        "Statkraft Tofte",
        "Hurum, Norway",
        "PRO (river/seawater)",
        3000.0,  # 2–4 kW typical
        1.0,
        None,
        600.0,
        20.0,
        None,
        "Pilot closed 2013",
        "Statkraft; Wikipedia; ForwardOsmosisTech",
    ),
    PlantCaseStudy(
        "REAPower Trapani",
        "Trapani, Italy",
        "RED (brine/brackish)",
        50.0,
        2.0,
        None,
        None,
        None,
        None,
        "Pilot ~50 m² IEM",
        "Tedesco et al., Desalination; SciDirect S0376-7388",
    ),
    PlantCaseStudy(
        "Perth PSDP",
        "Kwinana, Australia",
        "SWRO (not osmotic harvest)",
        None,
        None,
        144_000.0,
        C_BRINE_PERth_70gL,
        C_SEAWATER,
        3.5,
        "Operational since 2006",
        "Wikipedia; Water Corp; ResearchGate",
    ),
    PlantCaseStudy(
        "Commercial PRO (literature)",
        "Lab/seawater",
        "PRO",
        None,
        6.3,
        None,
        600.0,
        20.0,
        None,
        "Pedersen 2024 SSRN — 30°C",
        "SSRN 4944813",
    ),
    PlantCaseStudy(
        "SGH-1 design target",
        "Bench skid",
        "PRO (brine/WW)",
        10.0,
        8.0,
        None,
        C_BRINE_HIGH_8WT,
        C_WW_EFFLUENT_LOW,
        None,
        "This repository",
        "sgh1_design.json",
    ),
]


def mixing_energy_kWh_m3(c_dilute: float, c_concentrated: float, T: float = T_REF) -> float:
    """Ideal mixing ΔG per m³ of dilute stream (same volumes), from WA Table 1 style."""
    import math

    # ΔG_mix ≈ 2 RT (c_c ln(c_c/c_d) - (c_c - c_d)) per m³ if ideal (simplified check)
    dpi = I_NACL * R_GAS * T * (c_concentrated - c_dilute)
    # Use Δπ·V for 1 m³ as upper mechanical bound (Pa·m³ = J)
    return dpi / 3.6e6  # J/m³ → kWh/m³


def perth_sidestream_pro() -> dict:
    """Model PRO if Perth brine (1200) mixed with WW (5) — same math as SGH-1 at Perth salinities."""
    st = steady_state_pro(C_BRINE_PERth_70gL, C_WW_EFFLUENT_LOW, A_mem=0.72)
    return {
        "label": "Perth-class brine + WW",
        "c_draw": C_BRINE_PERth_70gL,
        "c_feed": C_WW_EFFLUENT_LOW,
        "delta_pi_MPa": st.delta_pi / 1e6,
        "P_W_Lp1e12": st.P_elec_equiv_W,
        "mixing_kWh_m3": mixing_energy_kWh_m3(C_SEAWATER, C_BRINE_PERth_70gL),
    }


def statkraft_estuary_red() -> dict:
    """Estuary pair at Statkraft conditions."""
    st = steady_state_pro(C_SEAWATER, C_RIVER, A_mem=1.0)
    E_N_mV = 1000 * st.nernst_V
    V_stack = 50 * st.nernst_V
    P_max = V_stack**2 / (4 * 0.318)  # calibrated R_int for 15 W/m²
    return {
        "E_N_mV": E_N_mV,
        "V_stack_V": V_stack,
        "P_max_W_m2": P_max,
        "delta_pi_MPa": st.delta_pi / 1e6,
    }


def perth_desal_parasitic_fraction() -> dict:
    """If 10 W PRO recovered on sidestream vs plant consumption."""
    P_pro_target = 10.0
    # 144000 m3/d * 3.5 kWh/m3 = 504000 kWh/d
    daily_desal_kWh = 144_000 * 3.5
    daily_pro_kWh = P_pro_target * 24 / 1000  # 10 W continuous
    return {
        "daily_desal_MWh": daily_desal_kWh / 1000,
        "daily_pro_kWh_at_10W": daily_pro_kWh,
        "fraction_of_plant_energy_pct": 100 * daily_pro_kWh / daily_desal_kWh,
        "note": "Single bench skid; scaled fleet would multiply P_pro",
    }


def commercial_pro_at_6p3_W_m2() -> dict:
    """Reverse-size area for 10 W at literature 6.3 W/m²."""
    Ppp = 6.3
    A = 10.0 / Ppp
    st = steady_state_pro(C_SEAWATER, C_RIVER, A_mem=A)
    return {"P_W_m2": Ppp, "A_m2_for_10W": A, "P_est_W": Ppp * A}


def export_all() -> dict:
    return {
        "case_studies": [asdict(c) for c in CASE_STUDIES],
        "perth_sidestream_pro": perth_sidestream_pro(),
        "statkraft_estuary": statkraft_estuary_red(),
        "perth_parasitic_fraction": perth_desal_parasitic_fraction(),
        "commercial_pro_6p3": commercial_pro_at_6p3_W_m2(),
        "mixing_energy": {
            "seawater_brine_kWh_m3": mixing_energy_kWh_m3(C_SEAWATER, C_BRINE_PERth_70gL),
            "literature_WA_table": 0.14,
        },
        "tsc_baseline": asdict(solve_tsc()),
    }


def merge_into_paper_experiments() -> Path:
    exp_path = EXPORTS / "paper_experiments.json"
    data = json.loads(exp_path.read_text(encoding="utf-8"))
    data["real_world"] = export_all()
    exp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    out = EXPORTS / "real_world_calibration.json"
    out.write_text(json.dumps(data["real_world"], indent=2), encoding="utf-8")
    return exp_path


if __name__ == "__main__":
    p = merge_into_paper_experiments()
    print(f"Merged real_world into {p}")
