"""Telluric Storm Coupling — 3-node conductance network."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class TscResult:
    psi_a_V: float
    psi_s_V: float
    psi_w_V: float
    P_dissipated_W: float
    currents_A: list[float]


def solve_tsc(
    I_inject_A: tuple[float, float, float] = (0.0, 1e-6, 0.0),
    G_as: float = 1e-8,
    G_sw: float = 5e-9,
    G_a0: float = 2e-9,
    G_s0: float = 3e-9,
    G_w0: float = 4e-9,
) -> TscResult:
    """
    Nodes: 0=atmosphere, 1=soil, 2=estuary/water.
    G ψ = I with conductance matrix from CHORUS_MATH_PLAN.md §5.
    """
    G = np.array(
        [
            [G_as + G_a0, -G_as, 0.0],
            [-G_as, G_as + G_sw + G_s0, -G_sw],
            [0.0, -G_sw, G_sw + G_w0],
        ],
        dtype=float,
    )
    I = np.array(I_inject_A, dtype=float)
    psi = np.linalg.solve(G, I)
    P = float(psi @ G @ psi)
    return TscResult(
        psi_a_V=float(psi[0]),
        psi_s_V=float(psi[1]),
        psi_w_V=float(psi[2]),
        P_dissipated_W=P,
        currents_A=I.tolist(),
    )


def sweep_injection_current(n: int = 21) -> list[dict]:
    rows = []
    for j in np.linspace(0, 5e-6, n):
        r = solve_tsc(I_inject_A=(0.0, float(j), 0.0))
        rows.append(
            {
                "I_soil_A": float(j),
                "psi_s_mV": r.psi_s_V * 1000,
                "P_dissipated_uW": r.P_dissipated_W * 1e6,
            }
        )
    return rows
