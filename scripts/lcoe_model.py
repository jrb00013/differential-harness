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
import math
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


def _bisect_monotonic_decreasing(
    f,
    target: float,
    lo: float,
    hi: float,
    *,
    tol: float = 1e-6,
    max_iter: int = 200,
) -> float | None:
    """Find x in [lo, hi] such that f(x) == target, given f is monotonically
    DECREASING in x (e.g. LCOE decreases as power density or membrane life
    increases). Returns None if target is not bracketed by [f(hi), f(lo)]
    (i.e. unreachable within the search range even at its most favorable
    endpoint)."""
    f_lo, f_hi = f(lo), f(hi)
    # decreasing f: f_lo should be >= target >= f_hi for target to be bracketed
    if not (f_hi <= target <= f_lo):
        return None
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f_mid = f(mid)
        if abs(f_mid - target) < tol * max(abs(target), 1.0):
            return mid
        if f_mid > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _bisect_monotonic_increasing(
    f,
    target: float,
    lo: float,
    hi: float,
    *,
    tol: float = 1e-6,
    max_iter: int = 200,
) -> float | None:
    """Same as _bisect_monotonic_decreasing but for f monotonically
    INCREASING in x (e.g. LCOE increases with membrane cost)."""
    f_lo, f_hi = f(lo), f(hi)
    if not (f_lo <= target <= f_hi):
        return None
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        f_mid = f(mid)
        if abs(f_mid - target) < tol * max(abs(target), 1.0):
            return mid
        if f_mid < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# Physical/practical ceilings used to judge whether a breakeven solution is
# plausible, all sourced from docs/math/REAL_WORLD_DATA.md:
#   "Lab hypersaline, high P | 25-60 | Not sidestream default | ES&T Lett.
#   McCutcheon et al." -- the highest areal power density reported ANYWHERE
#   in the PRO literature this repo has anchored, under non-representative
#   lab conditions (not a sidestream/bench design point).
POWER_DENSITY_CEILING_W_M2 = 60.0
# A membrane cost of exactly $0/m^2 is the trivial floor; treated as the
# search floor rather than claiming anything below it is meaningful.
MEMBRANE_COST_FLOOR_USD_M2 = 0.0
# An arbitrarily long membrane life is not physically meaningless the way
# negative cost or superluminal density would be, but industrial RO/FO
# membranes are not documented anywhere in the public literature lasting
# beyond ~10-15 years even in favorable conditions before support-layer
# compaction/aging dominates; used here as a practical (not hard-physical)
# ceiling.
MEMBRANE_LIFE_CEILING_YEARS = 15.0


@dataclass
class BreakevenResult:
    parameter: str
    target_lcoe_usd_per_kWh: float
    solved_value: float | None
    ceiling: float
    plausible: bool
    verdict: str


def solve_breakeven_power_density(
    target_lcoe_usd_per_kWh: float,
    P_target_W: float = 1000.0,
    **lcoe_kwargs,
) -> BreakevenResult:
    """What power density (W/m^2), holding all other lcoe_kwargs fixed,
    would be needed to hit target_lcoe_usd_per_kWh? LCOE decreases
    monotonically as power density increases (fewer skid units needed
    for the same target power, so BOP capex drops faster than net energy
    drops), so this is a decreasing-function bisection."""

    def lcoe_at(density: float) -> float:
        return compute_lcoe(P_target_W=P_target_W, P_density_W_m2=density, **lcoe_kwargs).lcoe_usd_per_kWh

    solved = _bisect_monotonic_decreasing(
        lcoe_at, target_lcoe_usd_per_kWh, lo=0.5, hi=POWER_DENSITY_CEILING_W_M2 * 4
    )
    plausible = solved is not None and solved <= POWER_DENSITY_CEILING_W_M2
    if solved is None:
        verdict = (
            f"UNREACHABLE: even at {POWER_DENSITY_CEILING_W_M2 * 4:.0f} W/m^2 "
            f"(far beyond any reported PRO density), LCOE does not reach "
            f"${target_lcoe_usd_per_kWh:.3f}/kWh with these cost assumptions."
        )
    elif plausible:
        verdict = (
            f"PLAUSIBLE: {solved:.2f} W/m^2 is within the {POWER_DENSITY_CEILING_W_M2:.0f} "
            f"W/m^2 lab-hypersaline ceiling reported in docs/math/REAL_WORLD_DATA.md."
        )
    else:
        verdict = (
            f"IMPLAUSIBLE: reaching ${target_lcoe_usd_per_kWh:.3f}/kWh requires "
            f"{solved:.2f} W/m^2, which EXCEEDS the {POWER_DENSITY_CEILING_W_M2:.0f} "
            f"W/m^2 highest lab-reported PRO density in the public literature this "
            f"repo has anchored."
        )
    return BreakevenResult(
        parameter="P_density_W_m2",
        target_lcoe_usd_per_kWh=target_lcoe_usd_per_kWh,
        solved_value=solved,
        ceiling=POWER_DENSITY_CEILING_W_M2,
        plausible=plausible,
        verdict=verdict,
    )


def solve_breakeven_membrane_cost(
    target_lcoe_usd_per_kWh: float,
    P_target_W: float = 1000.0,
    **lcoe_kwargs,
) -> BreakevenResult:
    """What membrane $/m^2, holding all else fixed, would hit the target?
    LCOE increases monotonically with membrane cost, so any positive
    target below the cost-free LCOE floor is reachable by construction
    (membrane cost -> 0) -- the interesting question is whether the
    REQUIRED value is a plausible cost at all (it's always plausible in
    the trivial sense that $0/m^2 is achievable in the limit only, i.e.
    free -- flagged as implausible if the solved cost is at or below the
    floor, meaning even a FREE membrane would not reach the target)."""

    def lcoe_at(cost: float) -> float:
        return compute_lcoe(P_target_W=P_target_W, membrane_cost_usd_m2=cost, **lcoe_kwargs).lcoe_usd_per_kWh

    solved = _bisect_monotonic_increasing(
        lcoe_at, target_lcoe_usd_per_kWh, lo=MEMBRANE_COST_FLOOR_USD_M2, hi=MEMBRANE_COST_HIGH_USD_M2 * 10
    )
    plausible = solved is not None and solved > MEMBRANE_COST_FLOOR_USD_M2
    if solved is None:
        verdict = (
            f"UNREACHABLE: even at ${MEMBRANE_COST_HIGH_USD_M2 * 10:.0f}/m^2, LCOE does "
            f"not reach ${target_lcoe_usd_per_kWh:.3f}/kWh -- membrane cost is not the "
            f"binding constraint here."
        )
    elif plausible:
        verdict = f"PLAUSIBLE: membrane cost would need to be ${solved:.2f}/m^2."
    else:
        verdict = (
            f"IMPLAUSIBLE: reaching ${target_lcoe_usd_per_kWh:.3f}/kWh requires a "
            f"membrane cost at or below the $0/m^2 floor -- membrane cost alone "
            f"cannot close this gap regardless of how cheap the membrane becomes."
        )
    return BreakevenResult(
        parameter="membrane_cost_usd_m2",
        target_lcoe_usd_per_kWh=target_lcoe_usd_per_kWh,
        solved_value=solved,
        ceiling=MEMBRANE_COST_FLOOR_USD_M2,
        plausible=plausible,
        verdict=verdict,
    )


def solve_breakeven_membrane_life(
    target_lcoe_usd_per_kWh: float,
    P_target_W: float = 1000.0,
    **lcoe_kwargs,
) -> BreakevenResult:
    """What membrane replacement life (years), holding all else fixed,
    would hit the target? LCOE decreases as life increases (annualized
    membrane capex shrinks), so this is a decreasing-function bisection,
    checked against a practical (not hard-physical) ceiling."""

    def lcoe_at(life: float) -> float:
        return compute_lcoe(P_target_W=P_target_W, membrane_life_years=life, **lcoe_kwargs).lcoe_usd_per_kWh

    solved = _bisect_monotonic_decreasing(
        lcoe_at, target_lcoe_usd_per_kWh, lo=0.5, hi=MEMBRANE_LIFE_CEILING_YEARS * 10
    )
    plausible = solved is not None and solved <= MEMBRANE_LIFE_CEILING_YEARS
    if solved is None:
        verdict = (
            f"UNREACHABLE: even at a {MEMBRANE_LIFE_CEILING_YEARS * 10:.0f}-year membrane "
            f"life, LCOE does not reach ${target_lcoe_usd_per_kWh:.3f}/kWh -- membrane "
            f"life is not the binding constraint here."
        )
    elif plausible:
        verdict = (
            f"PLAUSIBLE: a {solved:.1f}-year membrane life is within the "
            f"{MEMBRANE_LIFE_CEILING_YEARS:.0f}-year practical ceiling for industrial "
            f"RO/FO membranes."
        )
    else:
        verdict = (
            f"IMPLAUSIBLE: reaching ${target_lcoe_usd_per_kWh:.3f}/kWh requires a "
            f"{solved:.1f}-year membrane life, EXCEEDING the "
            f"{MEMBRANE_LIFE_CEILING_YEARS:.0f}-year practical ceiling documented for "
            f"industrial RO/FO membranes."
        )
    return BreakevenResult(
        parameter="membrane_life_years",
        target_lcoe_usd_per_kWh=target_lcoe_usd_per_kWh,
        solved_value=solved,
        ceiling=MEMBRANE_LIFE_CEILING_YEARS,
        plausible=plausible,
        verdict=verdict,
    )


def breakeven_report(target_lcoe_usd_per_kWh: float, P_target_W: float = 1000.0, **lcoe_kwargs) -> dict:
    """Run all three single-parameter breakeven solvers against one target
    and summarize whether ANY plausible single-parameter path exists."""
    results = {
        "power_density": solve_breakeven_power_density(target_lcoe_usd_per_kWh, P_target_W, **lcoe_kwargs),
        "membrane_cost": solve_breakeven_membrane_cost(target_lcoe_usd_per_kWh, P_target_W, **lcoe_kwargs),
        "membrane_life": solve_breakeven_membrane_life(target_lcoe_usd_per_kWh, P_target_W, **lcoe_kwargs),
    }
    any_plausible = any(r.plausible for r in results.values())
    return {
        "target_lcoe_usd_per_kWh": target_lcoe_usd_per_kWh,
        "results": {k: asdict(v) for k, v in results.items()},
        "any_single_parameter_plausible": any_plausible,
        "summary": (
            "At least one single-parameter change stays within a known physical/"
            "practical ceiling."
            if any_plausible
            else "NO single-parameter change (power density, membrane cost, or "
            "membrane life alone) reaches this target within known physical/"
            "practical ceilings -- closing this gap would require multiple "
            "simultaneous improvements, not one lever."
        ),
    }


# --- Manufacturing / volume learning-curve model (Wright's law) ---
#
# Wright's law: cost declines by a constant fraction (the "learning rate")
# for every DOUBLING of cumulative production volume:
#     cost(N) = cost(N0) * (N / N0) ** b,  b = log2(1 - learning_rate)
#
# Learning rates by technology, from public research (see
# docs/ECONOMICS.md Sources for full citations):
#   - Solar PV: ~20-24% per doubling (sustained over 4+ decades).
#   - Wright's own original 1936 aircraft-manufacturing study: ~15% per
#     doubling.
#   - General range cited across semiconductors/batteries/solar/genome
#     sequencing: 20-30%.
#   - No PRO/FO-membrane-specific or small-batch-BOP-hardware-specific
#     learning rate was found in the public literature -- this is a real,
#     stated gap, not filled in with an invented number. Three scenarios
#     are offered instead of one invented "best" rate:
LEARNING_RATE_CONSERVATIVE = 0.10  # simple/mature hardware analog (low end of general range)
LEARNING_RATE_TYPICAL = 0.15  # Wright's original aircraft-manufacturing rate
LEARNING_RATE_SOLAR_ANALOG = 0.20  # solar PV's sustained real-world rate, optimistic analog


def learning_curve_cost(
    baseline_cost: float,
    baseline_volume: float,
    target_volume: float,
    learning_rate: float,
) -> float:
    """Wright's law: cost at target_volume given a baseline cost/volume and
    a per-doubling learning rate (e.g. 0.20 for 20% cost decline per
    doubling of cumulative units produced)."""
    if baseline_volume <= 0 or target_volume <= 0:
        raise ValueError("volumes must be positive")
    b = math.log2(1.0 - learning_rate)
    return baseline_cost * (target_volume / baseline_volume) ** b


def volume_cost_projection(
    baseline_bop_cost_usd: float = BOP_COST_HIGH_USD,
    baseline_membrane_cost_usd_m2: float = MEMBRANE_COST_HIGH_USD_M2,
    volumes: tuple[int, ...] = (1, 10, 100, 1000),
) -> list[dict]:
    """Project BOP and membrane cost at 10x/100x/1000x cumulative unit
    volume (relative to a volume-1 prototype baseline, i.e. this repo's
    own bench BOM cost), across the three learning-rate scenarios above.
    This answers 'could this get cheaper with scale' honestly -- it is a
    projection grounded in real per-technology learning rates, not a
    claim that CHORUS-SGH-1 specifically will follow any of them."""
    rows = []
    for label, rate in (
        ("conservative_10pct", LEARNING_RATE_CONSERVATIVE),
        ("typical_15pct", LEARNING_RATE_TYPICAL),
        ("solar_analog_20pct", LEARNING_RATE_SOLAR_ANALOG),
    ):
        for volume in volumes:
            bop_cost = learning_curve_cost(baseline_bop_cost_usd, 1, volume, rate)
            mem_cost = learning_curve_cost(baseline_membrane_cost_usd_m2, 1, volume, rate)
            lcoe_result = compute_lcoe(
                P_target_W=1000.0,
                P_density_W_m2=8.0,
                bop_cost_usd_per_skid=bop_cost,
                membrane_cost_usd_m2=mem_cost,
            )
            rows.append(
                {
                    "learning_rate_scenario": label,
                    "learning_rate": rate,
                    "cumulative_volume": volume,
                    "bop_cost_usd_per_skid": bop_cost,
                    "membrane_cost_usd_m2": mem_cost,
                    "lcoe_usd_per_kWh_at_1kW_practical_density": lcoe_result.lcoe_usd_per_kWh,
                }
            )
    return rows


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
