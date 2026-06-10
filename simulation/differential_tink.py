"""Universal Differential Tink (UDT) — ray field, particle bytes, transport kernel.

Spec: docs/UDT_PHYSICS.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from simulation.constants import (
    C_BRINE_8PCT,
    C_SOUND_WATER,
    C_TREATED_WW,
    E0_JOULES,
    ETA_TINK_DEFAULT,
    F_US_DEFAULT,
    LAMBDA_E90_REF_M,
    N_RAYS_DEFAULT,
)
from simulation.membrane_transport import concentration_polarization_profile
from simulation.parasitics import skid_energy_balance
from simulation.pro_cycle import ProCycleState, steady_state_pro
from simulation.ultrasonic_cp_gain import UltrasonicNetResult, net_power_with_ultrasound


@dataclass
class RayField:
    n_rays: int
    intensity_W_m2: np.ndarray
    phase_rad: np.ndarray
    footprint_m2: float


@dataclass
class ParticleByteState:
    byte_len: np.ndarray
    byte_val: np.ndarray
    lambda_e90_m: float


@dataclass
class TinkResult:
    k_m0_m_s: float
    k_m_eff_m_s: float
    flux_gain: float
    polarization_factor: float
    P_actuation_W: float


@dataclass
class LoopTransportState:
    loop_index: int
    A_loop_m2: float
    L_line_m: float
    delta_sigma: float
    tink: TinkResult
    P_loop_W: float


def lambda_e90(f_us: float = F_US_DEFAULT, c_sound: float = C_SOUND_WATER) -> float:
    return c_sound / max(f_us, 1.0)


def ray_field(
    n_rays: int = N_RAYS_DEFAULT,
    I_mean_W_m2: float = 2.0,
    footprint_m2: float = 1e-4,
    seed: int = 42,
    coherent_phases: bool = False,
) -> RayField:
    """Discrete ray field on one membrane loop (vectorized runtime)."""
    rng = np.random.default_rng(seed)
    intensity = np.clip(rng.normal(I_mean_W_m2, 0.15 * I_mean_W_m2, n_rays), 0.0, None)
    if coherent_phases:
        phase = np.zeros(n_rays)
    else:
        phase = rng.uniform(0, 2 * math.pi, n_rays)
    return RayField(n_rays=n_rays, intensity_W_m2=intensity, phase_rad=phase, footprint_m2=footprint_m2)


def particle_bytes(
    rays: RayField,
    A_loop_m2: float,
    L_line_m: float,
    dt_s: float = 1.0,
    f_us: float = F_US_DEFAULT,
    E0: float = E0_JOULES,
) -> ParticleByteState:
    """Geometry-scaled particle bytes per ray."""
    lam = lambda_e90(f_us)
    scale = (A_loop_m2 / max(L_line_m, 1e-9)) * (lam / LAMBDA_E90_REF_M)
    byte_len = np.full(rays.n_rays, max(scale, 1e-6))
    energy = rays.intensity_W_m2 * rays.footprint_m2 * dt_s
    byte_val = np.maximum(1, np.floor(energy / max(E0, 1e-18) * byte_len).astype(int))
    return ParticleByteState(byte_len=byte_len, byte_val=byte_val, lambda_e90_m=lam)


def tink_kernel(
    rays: RayField,
    bytes_: ParticleByteState,
    k_m0: float,
    eta_tink: float = ETA_TINK_DEFAULT,
    J_w: float = 1e-5,
) -> TinkResult:
    """Map ray bytes + phases → k_m,eff and flux gain."""
    w_sum = float(np.sum(bytes_.byte_val))
    w_amp = float(np.sum(bytes_.byte_val * rays.intensity_W_m2)) / max(w_sum, 1e-18)
    coherence = abs(float(np.mean(np.cos(rays.phase_rad))))
    boost = eta_tink * w_amp * max(coherence, 0.1)
    k_m_eff = k_m0 * (1.0 + boost)
    cp0 = concentration_polarization_profile(J_w=J_w, k_m=k_m0)
    cp1 = concentration_polarization_profile(J_w=J_w, k_m=k_m_eff)
    gain_km = k_m_eff / max(k_m0, 1e-18)
    gain_cp = cp0.polarization_factor / max(cp1.polarization_factor, 1.0)
    flux_gain = gain_km * gain_cp
    P_act = float(np.sum(rays.intensity_W_m2 * rays.footprint_m2))
    return TinkResult(
        k_m0_m_s=k_m0,
        k_m_eff_m_s=k_m_eff,
        flux_gain=flux_gain,
        polarization_factor=cp1.polarization_factor,
        P_actuation_W=P_act,
    )


def udt_pro_state(
    A_mem: float = 0.72,
    L_p: float = 1e-12,
    *,
    eta_tink: float = ETA_TINK_DEFAULT,
    n_rays_bench: int = 64,
    coherent_phases: bool = True,
    flux_gain_cap: float = 1.6,
) -> tuple[ProCycleState, TinkResult, UltrasonicNetResult]:
    """UDT Tink → PRO steady state → ultrasonic net comparison."""
    rays = ray_field(n_rays=n_rays_bench, coherent_phases=coherent_phases, seed=1)
    bytes_ = particle_bytes(rays, A_mem, 0.3)
    tink = tink_kernel(rays, bytes_, k_m0=1.5e-5, eta_tink=eta_tink)
    g = min(tink.flux_gain, flux_gain_cap)
    st_base = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, A_mem, L_p=L_p)
    st_udt = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, A_mem, L_p=L_p * g)
    us = net_power_with_ultrasound(st_base, flux_gain=g, P_us_W_per_m2=tink.P_actuation_W / max(A_mem, 1e-12))
    return st_udt, tink, us


def loop_transport_state(
    A_loop_m2: float = 0.24,
    L_line_m: float = 0.3,
    delta_sigma: float = 1.0,
    n_rays_bench: int = 64,
    flux_gain_cap: float = 1.6,
) -> LoopTransportState:
    """Single-loop UDT state coupled to PRO (bench uses reduced n_rays)."""
    rays = ray_field(n_rays=n_rays_bench, coherent_phases=True, seed=1)
    bytes_ = particle_bytes(rays, A_loop_m2, L_line_m)
    k_m0 = 1.5e-5
    tink = tink_kernel(rays, bytes_, k_m0)
    g = min(tink.flux_gain, flux_gain_cap)
    st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, A_loop_m2, L_p=1e-12 * g)
    return LoopTransportState(
        loop_index=0,
        A_loop_m2=A_loop_m2,
        L_line_m=L_line_m,
        delta_sigma=delta_sigma,
        tink=tink,
        P_loop_W=st.P_elec_equiv_W,
    )


def sweep_eta_tink(n: int = 21) -> list[dict]:
    rows = []
    for eta in np.linspace(0.0, 0.5, n):
        rays = ray_field(n_rays=64, seed=1, coherent_phases=True)
        bytes_ = particle_bytes(rays, 0.24, 0.3)
        tink = tink_kernel(rays, bytes_, k_m0=1.5e-5, eta_tink=float(eta))
        g = min(tink.flux_gain, 1.6)
        st0 = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, 0.24)
        st1 = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, 0.24, L_p=1e-12 * g)
        rows.append(
            {
                "eta_tink": float(eta),
                "flux_gain": tink.flux_gain,
                "k_m_eff": tink.k_m_eff_m_s,
                "P_pro_W": st1.P_elec_equiv_W,
                "P_net_gain_W": st1.P_elec_equiv_W - st0.P_elec_equiv_W - tink.P_actuation_W,
            }
        )
    return rows


def demo() -> LoopTransportState:
    state = loop_transport_state()
    print(f"UDT λ_e90 = {lambda_e90():.4f} m")
    print(f"k_m,eff = {state.tink.k_m_eff_m_s:.2e} m/s, gain = {state.tink.flux_gain:.3f}")
    print(f"P_loop = {state.P_loop_W:.3f} W, P_act = {state.tink.P_actuation_W:.4f} W")
    return state


if __name__ == "__main__":
    demo()
