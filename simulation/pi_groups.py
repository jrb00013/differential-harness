"""Evaluate dimensionless groups for SGH-1 sizing."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from simulation.constants import C_BRINE_8PCT, C_TREATED_WW
from simulation.pro_cycle import steady_state_pro
from simulation.sizing import size_skid


@dataclass
class PiGroups:
    Pi1_delta_P_over_delta_pi: float
    Pi2_Jw_scaled: float
    Pi3_Pe_order: float
    Pi4_area_law: float
    Pi5_sim_over_target: float
    L_p_required_for_target: float
    P_sim_W: float
    P_target_W: float


def evaluate_pi_groups(
    P_target_W: float = 10.0,
    P_density_W_m2: float = 8.0,
    L_p: float = 1.0e-12,
    rho: float = 1000.0,
    D: float = 1.5e-9,
    L_channel: float = 0.3,
) -> PiGroups:
    sz = size_skid(P_target_W=P_target_W, P_density_W_m2=P_density_W_m2)
    st = steady_state_pro(
        c_draw=sz.c_draw,
        c_feed=sz.c_feed,
        A_mem=sz.A_mem_m2,
        L_p=L_p,
    )
    J_w = st.m_dot_w / max(st.A_mem, 1e-12) / rho
    v = J_w
    Pe = v * L_channel / D
    Pi1 = st.delta_P / max(st.delta_pi, 1e-12)
    Pi2 = J_w * (rho / max(st.delta_pi, 1e-12)) ** 0.5
    Pi4 = (P_density_W_m2 * sz.A_mem_m2) / max(P_target_W, 1e-12)
    Pi5 = st.P_elec_equiv_W / max(P_target_W, 1e-12)
    # L_p* from P = eta_mem eta_hyd L_p A (Δπ/2)^2 at ΔP = Δπ/2
    eta = st.eta_mem * st.eta_hyd
    dp_half = 0.5 * st.delta_pi
    L_p_star = P_target_W / max(eta * st.A_mem * dp_half**2, 1e-30)
    return PiGroups(
        Pi1_delta_P_over_delta_pi=Pi1,
        Pi2_Jw_scaled=Pi2,
        Pi3_Pe_order=Pe,
        Pi4_area_law=Pi4,
        Pi5_sim_over_target=Pi5,
        L_p_required_for_target=L_p_star,
        P_sim_W=st.P_elec_equiv_W,
        P_target_W=P_target_W,
    )


def main() -> None:
    pg = evaluate_pi_groups()
    print(json.dumps(asdict(pg), indent=2))
    out = Path(__file__).resolve().parent.parent / "exports" / "sgh1_pi_groups.json"
    out.write_text(json.dumps(asdict(pg), indent=2), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
