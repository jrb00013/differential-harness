"""Acoustic-Osmotic Ram (AOR) — resonant column + brine motor + ram pipe.

Spec: docs/AOR_PHYSICS.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from simulation.constants import C_BRINE_8PCT, C_SOUND_WATER, C_TREATED_WW, F_US_DEFAULT
from simulation.differential_tink import loop_transport_state
from simulation.parasitics import skid_energy_balance
from simulation.pro_cycle import steady_state_pro


@dataclass
class ResonantColumn:
    height_m: float
    f_us_Hz: float
    Q: float
    I_wall_W_m2: float


@dataclass
class RamLeg:
    area_ratio: float
    delta_h_m: float
    rho_kg_m3: float


@dataclass
class AORState:
    resonant: ResonantColumn
    ram: RamLeg
    P_osmotic_MPa: float
    P_pro_W: float
    P_us_W: float
    P_net_W: float
    flux_gain_udt: float


def resonant_column(
    height_m: float = 0.54,
    Q: float = 50.0,
    p_rms_Pa: float = 5e4,
    rho: float = 1000.0,
) -> ResonantColumn:
    """Quarter-wave match: f ≈ c/(4H)."""
    f = C_SOUND_WATER / (4 * max(height_m, 1e-6))
    I = p_rms_Pa**2 / (rho * C_SOUND_WATER)
    return ResonantColumn(height_m=height_m, f_us_Hz=f, Q=Q, I_wall_W_m2=I * Q)


def ram_pressure_gain(ram: RamLeg, v_in_m_s: float = 0.5) -> float:
    """Bernoulli-style head from area contraction."""
    v_out = v_in_m_s / max(ram.area_ratio, 1e-6)
    dynamic = 0.5 * ram.rho_kg_m3 * (v_out**2 - v_in_m_s**2)
    hydrostatic = ram.rho_kg_m3 * 9.81 * ram.delta_h_m
    return dynamic + hydrostatic


def aor_state(
    A_mem: float = 0.72,
    column_height_m: float = 0.54,
    area_ratio: float = 0.4,
    delta_h_m: float = 0.5,
    P_us_W_m2: float = 1.5,
) -> AORState:
    """Full AOR chain: UDT loop + PRO + parasitics."""
    res = resonant_column(column_height_m)
    ram = RamLeg(area_ratio=area_ratio, delta_h_m=delta_h_m, rho_kg_m3=1020.0)
    udt = loop_transport_state(A_loop_m2=A_mem, n_rays_bench=64)
    g = min(udt.tink.flux_gain, 1.6)
    st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, A_mem, L_p=1e-12 * g)
    P_us = P_us_W_m2 * A_mem
    bal = skid_energy_balance(st, P_us_W=P_us)
    return AORState(
        resonant=res,
        ram=ram,
        P_osmotic_MPa=st.delta_pi / 1e6,
        P_pro_W=st.P_elec_equiv_W,
        P_us_W=P_us,
        P_net_W=bal.P_net_W,
        flux_gain_udt=g,
    )


def sweep_column_height(heights: list[float] | None = None) -> list[dict]:
    if heights is None:
        heights = [0.2, 0.35, 0.54, 0.7, 1.0, 1.2]
    rows = []
    for h in heights:
        aor = aor_state(column_height_m=h)
        rows.append(
            {
                "height_m": h,
                "f_res_Hz": aor.resonant.f_us_Hz,
                "I_wall_W_m2": aor.resonant.I_wall_W_m2,
                "P_net_W": aor.P_net_W,
                "flux_gain": aor.flux_gain_udt,
            }
        )
    return rows


if __name__ == "__main__":
    s = aor_state()
    print(f"AOR f_res={s.resonant.f_us_Hz:.0f} Hz, P_osm={s.P_osmotic_MPa:.2f} MPa")
    print(f"P_pro={s.P_pro_W:.3f} W, P_net={s.P_net_W:.3f} W, g={s.flux_gain_udt:.3f}")
