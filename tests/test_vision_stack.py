"""Vision stack E14–E16 gates."""

from simulation.differential_tink import sweep_eta_tink, udt_pro_state
from simulation.experiments import vision_stack_experiments
from simulation.vortex_osmotic_hydro import breakeven_omega, sweep_omega


def test_udt_flux_gain_non_unity_at_eta_015():
    rows = sweep_eta_tink(11)
    row = next(r for r in rows if r["eta_tink"] >= 0.14)
    assert row["flux_gain"] > 1.01


def test_udt_pro_state_runs():
    st, tink, us = udt_pro_state(eta_tink=0.2)
    assert st.P_elec_equiv_W > 0
    assert tink.flux_gain > 1.0


def test_vision_stack_exports_keys():
    data = vision_stack_experiments()
    assert "E14_udt_eta_tink" in data
    assert "E15_aor_column_height" in data
    assert "E16_voh_omega" in data


def test_voh_omega_sweep_has_flat_point():
    rows = sweep_omega()
    assert rows[0]["omega_rad_s"] == 0


def test_breakeven_omega_optional():
    be = breakeven_omega()
    if be is not None:
        assert be["omega_rad_s"] > 0
        assert be["P_net_W"] > be["P_net_flat_W"]
