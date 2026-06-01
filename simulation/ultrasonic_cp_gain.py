"""Ultrasonic concentration-polarization reduction → PRO flux gain."""

from __future__ import annotations

from dataclasses import dataclass

from simulation.pro_cycle import ProCycleState, steady_state_pro


@dataclass
class UltrasonicNetResult:
    P_pro_baseline_W: float
    P_pro_us_W: float
    P_us_input_W: float
    P_net_gain_W: float
    flux_gain_ratio: float


def net_power_with_ultrasound(
    state: ProCycleState,
    flux_gain: float = 1.4,
    P_us_W_per_m2: float = 2.0,
) -> UltrasonicNetResult:
    """flux_gain: multiplicative water flux increase from CP disruption."""
    P_base = state.P_elec_equiv_W
    st_hi = steady_state_pro(
        c_draw=state.c_draw,
        c_feed=state.c_feed,
        A_mem=state.A_mem,
        L_p=state.L_p * flux_gain,
        B=state.B,
        delta_P_ratio=state.delta_P / max(state.delta_pi, 1.0),
        T=state.T,
        eta_mem=state.eta_mem,
        eta_hyd=state.eta_hyd,
    )
    P_us = P_us_W_per_m2 * state.A_mem
    P_hi = st_hi.P_elec_equiv_W
    return UltrasonicNetResult(
        P_pro_baseline_W=P_base,
        P_pro_us_W=P_hi,
        P_us_input_W=P_us,
        P_net_gain_W=P_hi - P_base - P_us,
        flux_gain_ratio=flux_gain,
    )
