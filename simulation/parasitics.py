"""Parasitic loads for skid net energy balance."""

from __future__ import annotations

from dataclasses import dataclass

from simulation.pro_cycle import ProCycleState


@dataclass
class SkidEnergyBalance:
    P_pro_W: float
    P_aeh_W: float
    P_us_W: float
    P_pump_W: float
    P_daq_W: float
    P_px_recovery_W: float
    P_net_W: float


def pump_hydraulic_power_W(
    Q_m3_s: float,
    delta_P_Pa: float,
    eta_pump: float = 0.55,
) -> float:
    """Shaft power to move fluid against delta_P."""
    return max(Q_m3_s * delta_P_Pa / max(eta_pump, 1e-9), 0.0)


def px_recovery_credit_W(
    draw_pressure_Pa: float,
    Q_permeate_m3_s: float,
    px_efficiency: float = 0.85,
) -> float:
    """Illustrative energy returned from pressure exchanger on permeate/brine path."""
    return px_efficiency * draw_pressure_Pa * Q_permeate_m3_s * 0.5


def skid_energy_balance(
    state: ProCycleState,
    *,
    P_aeh_W: float = 0.002,
    P_us_W: float | None = None,
    delta_P_pump_Pa: float = 2.0e5,
    eta_pump: float = 0.55,
    P_daq_W: float = 1.5,
    use_px: bool = True,
) -> SkidEnergyBalance:
    P_pro = state.P_elec_equiv_W
    P_us = P_us_W if P_us_W is not None else 0.0
    P_pump = pump_hydraulic_power_W(state.m_dot_w, delta_P_pump_Pa, eta_pump)
    P_px = px_recovery_credit_W(state.delta_P, state.m_dot_w) if use_px else 0.0
    P_net = P_pro + P_aeh_W - P_us - P_pump - P_daq_W + P_px
    return SkidEnergyBalance(
        P_pro_W=P_pro,
        P_aeh_W=P_aeh_W,
        P_us_W=P_us,
        P_pump_W=P_pump,
        P_daq_W=P_daq_W,
        P_px_recovery_W=P_px,
        P_net_W=P_net,
    )
