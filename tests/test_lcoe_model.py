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
