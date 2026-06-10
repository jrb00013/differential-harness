"""Skid net energy balance."""

from simulation.constants import C_BRINE_8PCT, C_TREATED_WW
from simulation.parasitics import skid_energy_balance
from simulation.pro_cycle import steady_state_pro


def test_baseline_with_px_can_be_positive():
    st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, 0.72)
    bal = skid_energy_balance(st, P_us_W=0.0, use_px=True)
    assert bal.P_px_recovery_W > 0
    assert bal.P_net_W > 0


def test_us_reduces_net():
    st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, 0.72)
    off = skid_energy_balance(st, P_us_W=0.0)
    on = skid_energy_balance(st, P_us_W=2.0)
    assert on.P_net_W < off.P_net_W
