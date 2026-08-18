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
    AVOIDED_TD_CREDIT_USD_PER_KWH,
    LEARNING_RATE_SOLAR_ANALOG,
    LEARNING_RATE_TYPICAL,
    MEMBRANE_LIFE_CEILING_YEARS,
    POWER_DENSITY_CEILING_W_M2,
    breakeven_report,
    co_benefit_adjusted_lcoe,
    learning_curve_cost,
    solve_breakeven_membrane_cost,
    solve_breakeven_membrane_life,
    solve_breakeven_power_density,
    volume_cost_projection,

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


# --- Learning-curve / manufacturing-volume model (round 4) ---


def test_learning_curve_cost_matches_hand_computed_value_at_one_doubling():
    # One doubling (volume 2 vs baseline 1) at a 20% learning rate should
    # give exactly cost * 0.80, by definition of "20% decline per doubling."
    cost = learning_curve_cost(100.0, baseline_volume=1, target_volume=2, learning_rate=0.20)
    assert cost == pytest.approx(80.0, rel=1e-9)


def test_learning_curve_cost_matches_hand_computed_value_at_ten_doublings():
    # 2^10 = 1024x volume at a 15% learning rate -> cost * 0.85**10
    cost = learning_curve_cost(100.0, baseline_volume=1, target_volume=1024, learning_rate=0.15)
    assert cost == pytest.approx(100.0 * 0.85**10, rel=1e-9)


def test_learning_curve_cost_rejects_nonpositive_volumes():
    with pytest.raises(ValueError):
        learning_curve_cost(100.0, baseline_volume=0, target_volume=10, learning_rate=0.15)
    with pytest.raises(ValueError):
        learning_curve_cost(100.0, baseline_volume=1, target_volume=-5, learning_rate=0.15)


def test_learning_curve_cost_higher_learning_rate_gives_lower_cost_at_same_volume():
    low_rate_cost = learning_curve_cost(100.0, 1, 1000, LEARNING_RATE_TYPICAL)
    high_rate_cost = learning_curve_cost(100.0, 1, 1000, LEARNING_RATE_SOLAR_ANALOG)
    assert high_rate_cost < low_rate_cost


def test_volume_cost_projection_costs_decrease_monotonically_with_volume():
    rows = volume_cost_projection(volumes=(1, 10, 100, 1000))
    by_scenario: dict[str, list[dict]] = {}
    for row in rows:
        by_scenario.setdefault(row["learning_rate_scenario"], []).append(row)

    for scenario_rows in by_scenario.values():
        scenario_rows.sort(key=lambda r: r["cumulative_volume"])
        costs = [r["bop_cost_usd_per_skid"] for r in scenario_rows]
        assert costs == sorted(costs, reverse=True)
        lcoes = [r["lcoe_usd_per_kWh_at_1kW_practical_density"] for r in scenario_rows]
        assert lcoes == sorted(lcoes, reverse=True)


def test_volume_cost_projection_even_at_1000x_solar_analog_rate_stays_above_solar_wind():
    # The honest round-4 finding: even 1000x cumulative volume at the most
    # optimistic (solar-analog) learning rate, at PRACTICAL (not lab-ceiling)
    # power density, does not reach Lazard's solar/wind LCOE range
    # ($0.03-0.09/kWh) -- manufacturing scale alone does not close the gap.
    rows = volume_cost_projection(volumes=(1000,))
    solar_analog_1000x = next(r for r in rows if r["learning_rate_scenario"] == "solar_analog_20pct")
    assert solar_analog_1000x["lcoe_usd_per_kWh_at_1kW_practical_density"] > 0.09


# --- Avoided-T&D co-benefit credit (round 4) ---


def test_co_benefit_adjusted_lcoe_subtracts_credit():
    result = co_benefit_adjusted_lcoe(6.40)
    assert result["avoided_td_credit_usd_per_kWh"] == AVOIDED_TD_CREDIT_USD_PER_KWH
    assert result["co_benefit_adjusted_lcoe_usd_per_kWh"] == pytest.approx(6.40 - AVOIDED_TD_CREDIT_USD_PER_KWH)


def test_co_benefit_adjusted_lcoe_never_goes_negative():
    result = co_benefit_adjusted_lcoe(0.01)  # credit (0.02) exceeds raw LCOE
    assert result["co_benefit_adjusted_lcoe_usd_per_kWh"] == 0.0


def test_co_benefit_adjusted_lcoe_reports_small_pct_offset_at_multi_dollar_scale():
    # The honest round-4 co-benefit finding: at CHORUS-SGH-1's actual
    # multi-dollar/kWh LCOE scale, the (real, citable) avoided-T&D credit
    # offsets only a tiny fraction of the raw number.
    result = co_benefit_adjusted_lcoe(6.40)
    assert result["pct_of_raw_lcoe_offset"] < 1.0  # well under 1% at this scale


def test_co_benefit_adjusted_lcoe_offsets_larger_share_at_near_competitive_scale():
    # At a much lower (near-competitive) raw LCOE, the same fixed credit
    # is a much larger relative share -- consistent with it being a fixed
    # $/kWh offset, not a percentage discount.
    high_scale = co_benefit_adjusted_lcoe(6.40)
    low_scale = co_benefit_adjusted_lcoe(0.30)
    assert low_scale["pct_of_raw_lcoe_offset"] > high_scale["pct_of_raw_lcoe_offset"]
