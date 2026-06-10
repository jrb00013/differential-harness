"""Vortex-Osmotic Hydro (VOH) / Z-Hydro — spin + brine + z-leg.

Spec: docs/VOH_PHYSICS.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from simulation.acoustic_osmotic_ram import aor_state
from simulation.constants import (
    C_BRINE_8PCT,
    C_TREATED_WW,
    TAU_SPIN_DEFAULT_NM,
    rpm_from_omega,
    tau_spin_from_rpm,
)
from simulation.parasitics import skid_energy_balance
from simulation.pro_cycle import steady_state_pro


@dataclass
class VOHGeometry:
    r_m: float
    omega_rad_s: float
    delta_h_z_m: float
    rho_kg_m3: float


@dataclass
class VOHState:
    geom: VOHGeometry
    P_spin_Pa: float
    P_z_Pa: float
    P_osmotic_Pa: float
    P_combined_head_Pa: float
    P_pro_W: float
    P_spin_motor_W: float
    P_net_W: float


def centrifugal_pressure(rho: float, omega: float, r: float) -> float:
    return 0.5 * rho * omega**2 * r**2


def z_hydro_pressure(rho: float, delta_h: float) -> float:
    return rho * 9.80665 * delta_h


def spin_motor_power_W(tau_Nm: float, omega: float) -> float:
    return max(tau_Nm * omega, 0.0)


def voh_state(
    A_mem: float = 0.72,
    r_m: float = 0.15,
    omega_rad_s: float = 50.0,
    delta_h_z_m: float = 0.5,
    rho: float = 1020.0,
    tau_spin_Nm: float = TAU_SPIN_DEFAULT_NM,
) -> VOHState:
    """VOH stacked head on AOR-enhanced PRO baseline."""
    aor = aor_state(A_mem=A_mem)
    g = aor.flux_gain_udt
    st = steady_state_pro(C_BRINE_8PCT, C_TREATED_WW, A_mem, L_p=1e-12 * g)
    P_spin = centrifugal_pressure(rho, omega_rad_s, r_m)
    P_z = z_hydro_pressure(rho, delta_h_z_m)
    P_osm = st.delta_pi
    P_head = P_osm + P_z + P_spin
    P_motor = spin_motor_power_W(tau_spin_Nm, omega_rad_s)
    bal = skid_energy_balance(st, P_us_W=aor.P_us_W)
    P_net = bal.P_net_W - P_motor
    return VOHState(
        geom=VOHGeometry(r_m=r_m, omega_rad_s=omega_rad_s, delta_h_z_m=delta_h_z_m, rho_kg_m3=rho),
        P_spin_Pa=P_spin,
        P_z_Pa=P_z,
        P_osmotic_Pa=P_osm,
        P_combined_head_Pa=P_head,
        P_pro_W=st.P_elec_equiv_W,
        P_spin_motor_W=P_motor,
        P_net_W=P_net,
    )


def sweep_omega(
    omega_values: list[float] | None = None,
    A_mem: float = 0.72,
) -> list[dict]:
    if omega_values is None:
        omega_values = [0, 25, 50, 75, 100, 150]
    rows = []
    for w in omega_values:
        v = voh_state(A_mem=A_mem, omega_rad_s=float(w))
        rows.append(
            {
                "omega_rad_s": float(w),
                "rpm": float(w) * 60 / (2 * math.pi),
                "P_spin_MPa": v.P_spin_Pa / 1e6,
                "P_z_MPa": v.P_z_Pa / 1e6,
                "P_combined_MPa": v.P_combined_head_Pa / 1e6,
                "P_spin_motor_W": v.P_spin_motor_W,
                "P_net_W": v.P_net_W,
            }
        )
    return rows


def breakeven_omega(
    A_mem: float = 0.72,
    omega_max: float = 150.0,
    n: int = 76,
    tau_spin_Nm: float = TAU_SPIN_DEFAULT_NM,
) -> dict | None:
    """Smallest ω where P_net(ω) > P_net(0) with spin parasitic subtracted."""
    flat = voh_state(A_mem=A_mem, omega_rad_s=0.0, delta_h_z_m=0.0, tau_spin_Nm=tau_spin_Nm)
    P_flat = flat.P_net_W
    for w in np.linspace(0.0, omega_max, n)[1:]:
        v = voh_state(A_mem=A_mem, omega_rad_s=float(w), tau_spin_Nm=tau_spin_Nm)
        if v.P_net_W > P_flat:
            return {
                "omega_rad_s": float(w),
                "rpm": rpm_from_omega(float(w)),
                "P_net_W": v.P_net_W,
                "P_net_flat_W": P_flat,
                "delta_P_net_W": v.P_net_W - P_flat,
            }
    return None


def compare_flat_vs_voh() -> dict:
    flat = voh_state(omega_rad_s=0.0, delta_h_z_m=0.0)
    voh = voh_state(omega_rad_s=75.0, delta_h_z_m=0.5)
    return {
        "flat_P_net_W": flat.P_net_W,
        "voh_P_net_W": voh.P_net_W,
        "delta_P_net_W": voh.P_net_W - flat.P_net_W,
        "flat_combined_MPa": flat.P_combined_head_Pa / 1e6,
        "voh_combined_MPa": voh.P_combined_head_Pa / 1e6,
    }


if __name__ == "__main__":
    v = voh_state()
    print(f"VOH combined head = {v.P_combined_head_Pa/1e6:.2f} MPa")
    print(f"P_pro={v.P_pro_W:.3f} W, P_spin_motor={v.P_spin_motor_W:.3f} W, P_net={v.P_net_W:.3f} W")
    print("compare:", compare_flat_vs_voh())
