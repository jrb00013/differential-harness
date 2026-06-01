"""Urban / industrial acoustic harvest estimates."""

from __future__ import annotations

import math
from dataclasses import dataclass

RHO_AIR = 1.2
C_SOUND = 343.0


@dataclass
class AcousticHarvestResult:
    spl_db: float
    p_rms_pa: float
    intensity_W_m2: float
    area_m2: float
    eta_transducer: float
    power_W: float


def spl_to_pressure(spl_db: float, p_ref: float = 20e-6) -> float:
    return p_ref * 10 ** (spl_db / 20.0)


def intensity_from_pressure(p_rms: float) -> float:
    return p_rms**2 / (RHO_AIR * C_SOUND)


def harvest_power(
    spl_db: float,
    area_m2: float,
    eta_transducer: float = 0.02,
) -> AcousticHarvestResult:
    p = spl_to_pressure(spl_db)
    I = intensity_from_pressure(p)
    P = eta_transducer * I * area_m2
    return AcousticHarvestResult(
        spl_db=spl_db,
        p_rms_pa=p,
        intensity_W_m2=I,
        area_m2=area_m2,
        eta_transducer=eta_transducer,
        power_W=P,
    )


def sweep_spl(
    spl_min: float = 60.0,
    spl_max: float = 100.0,
    n: int = 50,
    area_m2: float = 0.5,
    eta: float = 0.02,
) -> list[AcousticHarvestResult]:
    return [
        harvest_power(spl_min + (spl_max - spl_min) * i / (n - 1), area_m2, eta)
        for i in range(n)
    ]
