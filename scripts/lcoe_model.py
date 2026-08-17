#!/usr/bin/env python3
"""Levelized cost of energy (LCOE) model for CHORUS-SGH-1.

Grounds a real $/kWh estimate in the numbers already anchored in this
repo (docs/math/REAL_WORLD_DATA.md, hardware/bom/SGH1_BOM.csv) plus the
existing PRO steady-state / parasitics simulation
(simulation.sizing, simulation.parasitics), rather than a bare
literature LCOE quote. See docs/ECONOMICS.md for the full narrative,
citations, and honest comparison against solar/wind/storage benchmarks.

Model, in order:
  1. Size a skid for a target gross power at a given membrane power
     density (simulation.sizing.size_skid).
  2. Run the net (parasitics-adjusted) energy balance
     (simulation.parasitics.skid_energy_balance) so pumping losses are
     NOT double-counted as both an opex line item and a generation
     derate.
  3. Capital cost = balance-of-plant (from the bench BOM's own
     estimated-cost line, `EST-001` in hardware/bom/SGH1_BOM.csv,
     scaled by the number of skid units needed) + membrane cost
     (membrane area x $/m^2, both bounds from REAL_WORLD_DATA.md).
  4. Annualize capital cost with a standard capital recovery factor
     (CRF) at a given discount rate and project lifetime.
  5. Membrane replacement is modeled as a recurring capital cost every
     `membrane_life_years` (NOT simple opex), since replacing a
     membrane is a capital-scale expenditure, amortized over its own
     life within the project lifetime.
  6. LCOE = (annualized BOP capex + annualized membrane cost + annual
     O&M) / annual net energy delivered (kWh), at a given capacity
     factor (this is a continuously-driven brine-gradient plant, so a
     high capacity factor vs. solar/wind is itself a claim worth
     stating explicitly and testing sensitivity on).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from simulation.constants import C_BRINE_8PCT, C_TREATED_WW
from simulation.parasitics import skid_energy_balance

ROOT = Path(__file__).resolve().parent.parent
EXPORTS = ROOT / "exports"
HOURS_PER_YEAR = 8760.0

# --- Cost anchors, sourced from docs/math/REAL_WORLD_DATA.md and the BOM ---
# Membrane cost range ($/m^2): "Membrane $/m² | $4-150 (trend -> ~4 EUR/m^2
# RED IEM) | Frontiers RED review 2024" in docs/math/REAL_WORLD_DATA.md.
MEMBRANE_COST_LOW_USD_M2 = 30.0   # commodity FO/PRO composite sheet, optimistic/bulk
MEMBRANE_COST_HIGH_USD_M2 = 150.0  # OEM PRO module sheet, conservative/small-order

# Balance-of-plant (frame, housing, pumps, sensors, DAQ, fittings -- everything
# in hardware/bom/SGH1_BOM.csv EXCEPT the membrane itself) per single skid
# unit, taken directly from the BOM's own estimate line EST-001
# ("Estimated bench BOM ... ~2500-8000 excl membrane OEM").
BOP_COST_LOW_USD = 2500.0
BOP_COST_HIGH_USD = 8000.0

# Membrane replacement interval: industrial RO/FO membrane service life is
# commonly cited in the 5-7 year range before performance degrades below
# an economic threshold (fouling/compaction); PRO-specific literature is
# thinner, so this uses the RO/FO range as the working assumption -- flagged
# explicitly as an assumption pending real T1c-scale fouling data
# (docs/FOULING_TEST_PROTOCOL.md).
MEMBRANE_LIFE_YEARS_LOW = 5.0
MEMBRANE_LIFE_YEARS_HIGH = 7.0

DEFAULT_DISCOUNT_RATE = 0.07  # typical small-infrastructure real discount rate
DEFAULT_PROJECT_LIFE_YEARS = 20.0
DEFAULT_OM_FRACTION_OF_CAPEX_PER_YEAR = 0.02  # 2%/yr, typical small-plant O&M rule of thumb


@dataclass
class LcoeInputs:
    P_target_W: float
    P_density_W_m2: float
    membrane_cost_usd_m2: float
    bop_cost_usd_per_skid: float
    membrane_life_years: float
    discount_rate: float
    project_life_years: float
    capacity_factor: float
    om_fraction_per_year: float


@dataclass
class LcoeResult:
    inputs: LcoeInputs
    A_mem_m2: float
    n_skid_units: int
    P_net_W: float
    annual_net_energy_kWh: float
    bop_capex_usd: float
    membrane_capex_usd: float
    total_capex_usd: float
    annualized_bop_usd_per_year: float
    annualized_membrane_usd_per_year: float
    annual_om_usd_per_year: float
    lcoe_usd_per_kWh: float


def capital_recovery_factor(discount_rate: float, life_years: float) -> float:
    """Standard CRF: converts a present capital cost into a level annual payment."""
    r = discount_rate
    n = life_years
    if r <= 0:
        return 1.0 / n
    return (r * (1 + r) ** n) / ((1 + r) ** n - 1)


def _max_area_per_skid_unit(plate_width_mm: float = 200.0, plate_height_mm: float = 300.0) -> float:
    """The bench CAD caps a single skid at 12 plates (simulation.sizing.size_skid)."""
    plate_area_m2 = (plate_width_mm / 1000) * (plate_height_mm / 1000)
    return 12 * plate_area_m2


def compute_lcoe(
    P_target_W: float = 50.0,
    P_density_W_m2: float = 8.0,
    *,
    membrane_cost_usd_m2: float = MEMBRANE_COST_HIGH_USD_M2,
    bop_cost_usd_per_skid: float = BOP_COST_HIGH_USD,
    membrane_life_years: float = MEMBRANE_LIFE_YEARS_LOW,
    discount_rate: float = DEFAULT_DISCOUNT_RATE,
    project_life_years: float = DEFAULT_PROJECT_LIFE_YEARS,
    capacity_factor: float = 0.90,
    om_fraction_per_year: float = DEFAULT_OM_FRACTION_OF_CAPEX_PER_YEAR,
) -> LcoeResult:
    # simulation.sizing.size_skid deliberately caps a single skid's CAD at
    # 12 membrane plates (~0.72 m^2, see its own "bench CAD cap" comment).
    # A target power beyond what one capped skid unit can deliver is
    # modeled here as N identical skid units operating in parallel, each
    # sized to its own 12-plate cap -- NOT as one skid with an
    # arbitrarily large membrane area size_skid was never designed to
    # produce. This is what determines how BOP capex scales with target
    # power.
    max_area_per_unit = _max_area_per_skid_unit()
    required_area_m2 = P_target_W / max(P_density_W_m2, 1e-9)
    n_skid_units = max(1, -(-required_area_m2 // max_area_per_unit))  # ceil division
    n_skid_units = int(n_skid_units)
    total_A_mem_m2 = max_area_per_unit * n_skid_units

    # Gross power at the ASSUMED areal density (this IS what P_density_W_m2
    # means, per docs/math/REAL_WORLD_DATA.md's literature anchors: 8 W/m^2
    # "practical large-scale", 25-60 W/m^2 "lab hypersaline", ~1 W/m^2
    # "Statkraft Tofte pilot"). The parasitic derate is taken from the
    # existing physics simulation (simulation.pro_cycle / .parasitics) run
    # at a single reference skid unit's DEFAULT-anchored physics state,
    # rather than re-deriving parasitics from the assumed scenario density
    # directly -- an honest approximation (documented in docs/ECONOMICS.md)
    # that carries the *shape* of the real parasitics model (pump power vs.
    # flow, PX recovery credit) into scenarios the underlying L_p-based
    # physics model doesn't itself span.
    from simulation.pro_cycle import steady_state_pro

    ref_state = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, max_area_per_unit)
    ref_balance = skid_energy_balance(ref_state)
    parasitic_fraction = 1.0 - (
        max(ref_balance.P_net_W, 0.0) / max(ref_balance.P_pro_W, 1e-9)
    )
    parasitic_fraction = min(max(parasitic_fraction, 0.0), 1.0)

    P_gross_W = P_density_W_m2 * total_A_mem_m2
    P_net_W = P_gross_W * (1.0 - parasitic_fraction)

    bop_capex = bop_cost_usd_per_skid * n_skid_units
    membrane_capex = membrane_cost_usd_m2 * total_A_mem_m2
    total_capex = bop_capex + membrane_capex

    crf_bop = capital_recovery_factor(discount_rate, project_life_years)
    crf_membrane = capital_recovery_factor(discount_rate, membrane_life_years)

    annualized_bop = bop_capex * crf_bop
    annualized_membrane = membrane_capex * crf_membrane
    annual_om = total_capex * om_fraction_per_year

    annual_net_energy_kWh = (P_net_W / 1000.0) * HOURS_PER_YEAR * capacity_factor

    lcoe = (
        (annualized_bop + annualized_membrane + annual_om) / annual_net_energy_kWh
        if annual_net_energy_kWh > 1e-9
        else float("inf")
    )

    inputs = LcoeInputs(
        P_target_W=P_target_W,
        P_density_W_m2=P_density_W_m2,
        membrane_cost_usd_m2=membrane_cost_usd_m2,
        bop_cost_usd_per_skid=bop_cost_usd_per_skid,
        membrane_life_years=membrane_life_years,
        discount_rate=discount_rate,
        project_life_years=project_life_years,
        capacity_factor=capacity_factor,
        om_fraction_per_year=om_fraction_per_year,
    )

    return LcoeResult(
        inputs=inputs,
        A_mem_m2=total_A_mem_m2,
        n_skid_units=n_skid_units,
        P_net_W=P_net_W,
        annual_net_energy_kWh=annual_net_energy_kWh,
        bop_capex_usd=bop_capex,
        membrane_capex_usd=membrane_capex,
        total_capex_usd=total_capex,
        annualized_bop_usd_per_year=annualized_bop,
        annualized_membrane_usd_per_year=annualized_membrane,
        annual_om_usd_per_year=annual_om,
        lcoe_usd_per_kWh=lcoe,
    )


def sensitivity_sweep(P_target_W: float = 50.0) -> list[dict]:
    """LCOE across the honest optimistic<->conservative bound combinations,
    for the sensitivity table in docs/ECONOMICS.md."""
    rows = []
    for label, p_density in (("lab_optimistic", 25.0), ("practical", 8.0), ("statkraft_floor", 1.0)):
        for cost_label, mem_cost, bop_cost, mem_life in (
            ("optimistic", MEMBRANE_COST_LOW_USD_M2, BOP_COST_LOW_USD, MEMBRANE_LIFE_YEARS_HIGH),
            ("conservative", MEMBRANE_COST_HIGH_USD_M2, BOP_COST_HIGH_USD, MEMBRANE_LIFE_YEARS_LOW),
        ):
            result = compute_lcoe(
                P_target_W=P_target_W,
                P_density_W_m2=p_density,
                membrane_cost_usd_m2=mem_cost,
                bop_cost_usd_per_skid=bop_cost,
                membrane_life_years=mem_life,
            )
            rows.append(
                {
                    "power_density_scenario": label,
                    "P_density_W_m2": p_density,
                    "cost_scenario": cost_label,
                    "A_mem_m2": result.A_mem_m2,
                    "n_skid_units": result.n_skid_units,
                    "total_capex_usd": result.total_capex_usd,
                    "lcoe_usd_per_kWh": result.lcoe_usd_per_kWh,
                }
            )
    return rows


def main() -> None:
    p = argparse.ArgumentParser(description="Compute CHORUS-SGH-1 LCOE from sim + BOM cost anchors")
    p.add_argument("--power-w", type=float, default=50.0)
    p.add_argument("--density-w-m2", type=float, default=8.0)
    p.add_argument("--capacity-factor", type=float, default=0.90)
    p.add_argument("--sensitivity", action="store_true", help="print the full optimistic/conservative sweep")
    p.add_argument("--out", type=Path, default=None)
    args = p.parse_args()

    if args.sensitivity:
        rows = sensitivity_sweep(P_target_W=args.power_w)
        out = args.out or EXPORTS / "lcoe_sensitivity.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print(f"Wrote {out}")
        print(json.dumps(rows, indent=2))
        return

    result = compute_lcoe(P_target_W=args.power_w, P_density_W_m2=args.density_w_m2, capacity_factor=args.capacity_factor)
    payload = {
        "inputs": asdict(result.inputs),
        "A_mem_m2": result.A_mem_m2,
        "n_skid_units": result.n_skid_units,
        "P_net_W": result.P_net_W,
        "annual_net_energy_kWh": result.annual_net_energy_kWh,
        "bop_capex_usd": result.bop_capex_usd,
        "membrane_capex_usd": result.membrane_capex_usd,
        "total_capex_usd": result.total_capex_usd,
        "lcoe_usd_per_kWh": result.lcoe_usd_per_kWh,
    }
    out = args.out or EXPORTS / "lcoe_result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
