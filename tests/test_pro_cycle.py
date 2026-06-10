"""PRO cycle math gates."""

from simulation.constants import C_BRINE_8PCT, C_TREATED_WW
from simulation.pro_cycle import steady_state_pro


def test_delta_p_star_is_half_delta_pi():
    st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, 0.72)
    assert abs(st.delta_P_star - 0.5 * st.delta_pi) < 1e-6


def test_power_positive_at_optimum():
    st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, 0.72, delta_P_ratio=0.5)
    assert st.P_elec_equiv_W > 0
    assert st.m_dot_w > 0


def test_nernst_positive_brine_pair():
    st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, 0.72)
    assert st.nernst_V > 0
