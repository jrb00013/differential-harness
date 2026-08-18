"""Tests for scripts/lcoe_model.py.

Validates the LCOE arithmetic (capital recovery factor, unit scaling,
capex composition) against hand-computed expected values -- this is a
cost *model*, not a hardware measurement, and every assumption
(membrane cost, BOP cost, membrane life) is a documented anchor from
docs/math/REAL_WORLD_DATA.md / hardware/bom/SGH1_BOM.csv, not a
fabricated hardware result.
"""

from __future__ import annotations

import pytest

from scripts.lcoe_model import (
    MEMBRANE_LIFE_CEILING_YEARS,
    POWER_DENSITY_CEILING_W_M2,
    breakeven_report,
    solve_breakeven_membrane_cost,
    solve_breakeven_membrane_life,
    solve_breakeven_power_density,

    BOP_COST_HIGH_USD,
    MEMBRANE_COST_HIGH_USD_M2,
    capital_recovery_factor,
    compute_lcoe,
    sensitivity_sweep,
)


def test_capital_recovery_factor_matches_hand_computed_value():
    # CRF at r=0.07, n=20 -> ~0.09439 (standard finance formula)
    crf = capital_recovery_factor(0.07, 20)
    assert crf == pytest.approx(0.09439, rel=1e-3)


def test_capital_recovery_factor_zero_rate_is_straight_line():
    crf = capital_recovery_factor(0.0, 10)
    assert crf == pytest.approx(0.1)


def test_compute_lcoe_scales_skid_units_with_required_area():
    small = compute_lcoe(P_target_W=50.0, P_density_W_m2=8.0)
    large = compute_lcoe(P_target_W=50_000.0, P_density_W_m2=8.0)
    assert large.n_skid_units > small.n_skid_units
    assert large.total_capex_usd > small.total_capex_usd
    assert large.A_mem_m2 > small.A_mem_m2


def test_compute_lcoe_higher_density_needs_fewer_units_for_same_target():
    low_density = compute_lcoe(P_target_W=1000.0, P_density_W_m2=1.0)
    high_density = compute_lcoe(P_target_W=1000.0, P_density_W_m2=25.0)
    assert high_density.n_skid_units < low_density.n_skid_units
    assert high_density.A_mem_m2 < low_density.A_mem_m2


def test_compute_lcoe_higher_density_yields_lower_lcoe():
    low_density = compute_lcoe(P_target_W=5000.0, P_density_W_m2=1.0)
    high_density = compute_lcoe(P_target_W=5000.0, P_density_W_m2=25.0)
    assert high_density.lcoe_usd_per_kWh < low_density.lcoe_usd_per_kWh


def test_compute_lcoe_capex_composition_matches_inputs():
    result = compute_lcoe(
        P_target_W=100.0,
        P_density_W_m2=8.0,
        membrane_cost_usd_m2=MEMBRANE_COST_HIGH_USD_M2,
        bop_cost_usd_per_skid=BOP_COST_HIGH_USD,
    )
    assert result.bop_capex_usd == pytest.approx(BOP_COST_HIGH_USD * result.n_skid_units)
    assert result.membrane_capex_usd == pytest.approx(MEMBRANE_COST_HIGH_USD_M2 * result.A_mem_m2)
    assert result.total_capex_usd == pytest.approx(result.bop_capex_usd + result.membrane_capex_usd)


def test_compute_lcoe_is_positive_and_finite_for_normal_inputs():
    result = compute_lcoe(P_target_W=1000.0, P_density_W_m2=8.0)
    assert result.lcoe_usd_per_kWh > 0
    assert result.lcoe_usd_per_kWh < float("inf")


def test_compute_lcoe_zero_capacity_factor_is_infinite_not_a_crash():
    result = compute_lcoe(P_target_W=1000.0, P_density_W_m2=8.0, capacity_factor=0.0)
    assert result.lcoe_usd_per_kWh == float("inf")


def test_sensitivity_sweep_covers_all_scenario_combinations():
    rows = sensitivity_sweep()
    scenarios = {(r["power_density_scenario"], r["cost_scenario"]) for r in rows}
    assert len(scenarios) == 6  # 3 density scenarios x 2 cost scenarios
    assert all(r["lcoe_usd_per_kWh"] > 0 for r in rows)


def test_sensitivity_sweep_optimistic_cost_beats_conservative_cost_same_density():
    rows = sensitivity_sweep()
    by_key = {(r["power_density_scenario"], r["cost_scenario"]): r for r in rows}
    optimistic = by_key[("practical", "optimistic")]
    conservative = by_key[("practical", "conservative")]
    assert optimistic["lcoe_usd_per_kWh"] < conservative["lcoe_usd_per_kWh"]


# --- Breakeven sensitivity solvers (round 4) ---


def test_solve_breakeven_power_density_round_trips_with_compute_lcoe():
    target = 6.4
    result = solve_breakeven_power_density(target, P_target_W=1000.0)
    assert result.plausible is True
    assert result.solved_value is not None
    check = compute_lcoe(P_target_W=1000.0, P_density_W_m2=result.solved_value)
    assert check.lcoe_usd_per_kWh == pytest.approx(target, rel=1e-3)


def test_solve_breakeven_power_density_flags_implausible_when_beyond_ceiling():
    # $2/kWh with default (conservative) costs requires >60 W/m^2 -- beyond
    # the lab-hypersaline ceiling.
    result = solve_breakeven_power_density(2.0, P_target_W=1000.0)
    assert result.solved_value is not None
    assert result.solved_value > POWER_DENSITY_CEILING_W_M2
    assert result.plausible is False
    assert "EXCEEDS" in result.verdict


def test_solve_breakeven_power_density_reports_unreachable_for_solar_benchmark():
    # Lazard's solar/wind upper bound ($0.09/kWh) is not reachable via
    # power density alone even at 4x the lab-hypersaline ceiling.
    result = solve_breakeven_power_density(0.09, P_target_W=1000.0)
    assert result.solved_value is None
    assert result.plausible is False
    assert "UNREACHABLE" in result.verdict


def test_solve_breakeven_membrane_cost_round_trips():
    baseline = compute_lcoe(P_target_W=1000.0, P_density_W_m2=8.0)
    result = solve_breakeven_membrane_cost(baseline.lcoe_usd_per_kWh, P_target_W=1000.0, P_density_W_m2=8.0)
    assert result.solved_value == pytest.approx(150.0, rel=1e-2)  # default membrane cost used by compute_lcoe


def test_solve_breakeven_membrane_cost_implausible_at_zero_floor():
    result = solve_breakeven_membrane_cost(0.09, P_target_W=1000.0)
    assert result.solved_value is None
    assert result.plausible is False


def test_solve_breakeven_membrane_life_round_trips():
    baseline = compute_lcoe(P_target_W=1000.0, membrane_life_years=5.0)
    result = solve_breakeven_membrane_life(baseline.lcoe_usd_per_kWh, P_target_W=1000.0)
    assert result.solved_value == pytest.approx(5.0, rel=1e-2)


def test_solve_breakeven_membrane_life_implausible_or_unreachable_for_hard_target():
    # At $2/kWh, membrane life alone is far from the binding constraint
    # (BOP capex dominates at this scale) -- this may resolve as either
    # "requires an implausibly long life" or fully unreachable; either
    # way it must NOT be reported as plausible.
    result = solve_breakeven_membrane_life(2.0, P_target_W=1000.0)
    assert result.plausible is False
    if result.solved_value is not None:
        assert result.solved_value > MEMBRANE_LIFE_CEILING_YEARS


def test_breakeven_report_states_no_plausible_path_for_solar_benchmark():
    report = breakeven_report(0.09, P_target_W=1000.0)
    assert report["any_single_parameter_plausible"] is False
    assert "NO single-parameter change" in report["summary"]
    assert set(report["results"].keys()) == {"power_density", "membrane_cost", "membrane_life"}


def test_breakeven_report_finds_plausible_path_for_a_reachable_target():
    report = breakeven_report(6.4, P_target_W=1000.0)
    assert report["any_single_parameter_plausible"] is True
