"""1D concentration polarization model along membrane channel."""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass


@dataclass
class CPProfile:
    x: np.ndarray
    c_wall: np.ndarray
    c_bulk: float
    polarization_factor: float  # c_wall / c_bulk at outlet


def concentration_polarization_profile(
    L: float = 0.3,
    n: int = 100,
    c_bulk: float = 1400.0,
    J_w: float = 1e-5,
    D: float = 1.5e-9,
    k_m: float | None = None,
) -> CPProfile:
    """
    Steady film model: c_w / c_b = exp(J_w / k_m) at wall.
    k_m ~ D / delta_f; if None, use D/L scale.
    """
    if k_m is None:
        k_m = D / (L * 0.1)
    x = np.linspace(0, L, n)
    # growth of polarization along channel (simplified exponential approach)
    xi = J_w * x / (D * c_bulk + 1e-12)
    c_wall = c_bulk * np.exp(np.clip(xi, 0, 3))
    factor = float(c_wall[-1] / c_bulk)
    return CPProfile(x=x, c_wall=c_wall, c_bulk=c_bulk, polarization_factor=factor)


def effective_driving_force_reduction(cp: CPProfile) -> float:
    """Fraction of osmotic driving force remaining (1 = no CP)."""
    return 1.0 / max(cp.polarization_factor, 1.0)
