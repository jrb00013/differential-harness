"""Size CHORUS-SGH-1 skid from target power."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

from simulation.constants import C_BRINE_8PCT, C_TREATED_WW, P_BLUE_W_M2, T_REF
from simulation.pro_cycle import steady_state_pro


@dataclass
class SkidSizing:
    P_target_W: float
    P_density_W_m2: float
    A_mem_m2: float
    active_width_mm: float
    active_height_mm: float
    n_plates: int
    plate_area_mm2: float
    delta_pi_MPa: float
    delta_P_star_MPa: float
    delta_P_star_bar: float
    housing_od_mm: float
    housing_length_mm: float
    bolt_pattern_mm: float
    frame_length_mm: float
    frame_width_mm: float
    frame_height_mm: float
    Q_feed_L_min: float
    c_draw: float
    c_feed: float


def size_skid(
    P_target_W: float = 50.0,
    P_density_W_m2: float = P_BLUE_W_M2,
    c_draw: float = C_BRINE_8PCT,
    c_feed: float = C_TREATED_WW,
    plate_width_mm: float = 200.0,
    plate_height_mm: float = 300.0,
) -> SkidSizing:
    A = P_target_W / max(P_density_W_m2, 1e-9)
    plate_area_m2 = (plate_width_mm / 1000) * (plate_height_mm / 1000)
    n_plates_raw = max(1, math.ceil(A / plate_area_m2))
    n_plates = min(n_plates_raw, 12)  # bench CAD cap; scale power target if more area needed
    A_actual = n_plates * plate_area_m2

    st = steady_state_pro(c_draw=c_draw, c_feed=c_feed, A_mem=A_actual)

    housing_od = max(plate_width_mm + 80, 280)
    housing_len = n_plates * 12 + 120  # 12 mm pitch per cell + end caps

    return SkidSizing(
        P_target_W=P_target_W,
        P_density_W_m2=P_density_W_m2,
        A_mem_m2=A_actual,
        active_width_mm=plate_width_mm,
        active_height_mm=plate_height_mm,
        n_plates=n_plates,
        plate_area_mm2=plate_width_mm * plate_height_mm,
        delta_pi_MPa=st.delta_pi / 1e6,
        delta_P_star_MPa=st.delta_P_star / 1e6,
        delta_P_star_bar=st.delta_P_star / 1e5,
        housing_od_mm=housing_od,
        housing_length_mm=housing_len,
        bolt_pattern_mm=housing_od - 40,
        frame_length_mm=housing_len + 400,
        frame_width_mm=housing_od + 200,
        frame_height_mm=900,
        Q_feed_L_min=st.m_dot_w * 1e3 * 60,
        c_draw=c_draw,
        c_feed=c_feed,
    )


def export_sizing(path: Path, **kwargs) -> SkidSizing:
    s = size_skid(**kwargs)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(s), indent=2), encoding="utf-8")
    return s


def sizing_to_openscad_constants(s: SkidSizing) -> str:
    """Generate OpenSCAD include file."""
    lines = [
        "// AUTO-GENERATED from simulation/sizing.py — do not hand edit",
        f"P_target_W = {s.P_target_W};",
        f"A_mem_m2 = {s.A_mem_m2};",
        f"active_w = {s.active_width_mm};",
        f"active_h = {s.active_height_mm};",
        f"n_plates = {s.n_plates};",
        f"housing_od = {s.housing_od_mm};",
        f"housing_len = {s.housing_length_mm};",
        f"bolt_circle = {s.bolt_pattern_mm};",
        f"frame_L = {s.frame_length_mm};",
        f"frame_W = {s.frame_width_mm};",
        f"frame_H = {s.frame_height_mm};",
        f"delta_P_bar = {s.delta_P_star_bar:.2f};",
        f"plate_pitch = 12;",
    ]
    return "\n".join(lines) + "\n"
