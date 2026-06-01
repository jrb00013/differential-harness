"""Steady-state PRO cycle model."""

from __future__ import annotations

from dataclasses import dataclass

from simulation.constants import F_FARADAY, I_NACL, R_GAS, T_REF


@dataclass
class ProCycleState:
    c_draw: float  # mol/m³
    c_feed: float
    T: float
    A_mem: float  # m²
    L_p: float  # m/(Pa·s) water permeability
    B: float  # m/s salt permeability
    delta_P: float  # Pa hydraulic on draw
    eta_mem: float
    eta_hyd: float

    @property
    def pi_draw(self) -> float:
        return I_NACL * R_GAS * self.T * self.c_draw

    @property
    def pi_feed(self) -> float:
        return I_NACL * R_GAS * self.T * self.c_feed

    @property
    def delta_pi(self) -> float:
        return self.pi_draw - self.pi_feed

    @property
    def delta_P_star(self) -> float:
        return 0.5 * self.delta_pi

    @property
    def nernst_V(self) -> float:
        return (R_GAS * self.T / F_FARADAY) * __import__("math").log(
            self.c_draw / max(self.c_feed, 1e-6)
        )

    @property
    def m_dot_w(self) -> float:
        """Volumetric water flux m³/s across area (simplified)."""
        driving = max(self.delta_pi - self.delta_P, 0.0)
        return self.L_p * driving * self.A_mem

    @property
    def P_hydraulic_W(self) -> float:
        return self.m_dot_w * self.delta_P

    @property
    def P_elec_equiv_W(self) -> float:
        """Equivalent electrical power from salinity work."""
        return self.eta_mem * self.eta_hyd * self.P_hydraulic_W

    @property
    def P_density_W_m2(self) -> float:
        return self.P_elec_equiv_W / max(self.A_mem, 1e-12)


def steady_state_pro(
    c_draw: float,
    c_feed: float,
    A_mem: float,
    L_p: float = 1.0e-12,
    B: float = 1.0e-8,
    delta_P_ratio: float = 0.5,
    T: float = T_REF,
    eta_mem: float = 0.35,
    eta_hyd: float = 0.55,
) -> ProCycleState:
    st = ProCycleState(
        c_draw=c_draw,
        c_feed=c_feed,
        T=T,
        A_mem=A_mem,
        L_p=L_p,
        B=B,
        delta_P=0.0,
        eta_mem=eta_mem,
        eta_hyd=eta_hyd,
    )
    object.__setattr__(st, "delta_P", delta_P_ratio * st.delta_pi)
    return st
