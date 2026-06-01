#!/usr/bin/env python3
"""Audit OpenSCAD library: modules, includes, key dimensions."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAD_DIR = ROOT / "hardware" / "openscad"
EXPORT = ROOT / "exports" / "openscad_audit.json"


def parse_scad(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    includes = re.findall(r'include\s*<([^>]+)>', text)
    modules = re.findall(r"module\s+(\w+)\s*\(", text)
    params = re.findall(r"^(\w+)\s*=\s*([^;]+);", text, re.MULTILINE)
    local_params = {k: v.strip() for k, v in params if not k.startswith("//")}
    uses_generated = "generated_constants" in text
    return {
        "file": path.name,
        "includes": includes,
        "modules": modules,
        "local_parameters": local_params,
        "uses_generated_constants": uses_generated,
        "lines": len(text.splitlines()),
    }


def helmholtz_summary() -> dict:
    """Derived AEH geometry from chorus_aeh_panel.scad logic."""
    frame_W = 480.0
    panel_w = frame_W * 0.6
    panel_h = 400
    nx, ny = 6, 4
    return {
        "panel_w_mm": panel_w,
        "panel_h_mm": panel_h,
        "panel_t_mm": 28,
        "resonator_cells": nx * ny,
        "neck_d_mm": 8,
        "cavity_d_mm": 35,
        "estimated_cell_pitch_x_mm": panel_w / (nx + 1),
        "estimated_cell_pitch_z_mm": panel_h / (ny + 1),
    }


def housing_summary() -> dict:
    gc = (SCAD_DIR / "lib" / "generated_constants.scad").read_text()
    vals = {}
    for m in re.finditer(r"^(\w+)\s*=\s*([\d.]+);", gc, re.MULTILINE):
        vals[m.group(1)] = float(m.group(2))
    stack_len = vals.get("n_plates", 12) * vals.get("plate_pitch", 12) + 40
    return {
        **vals,
        "stack_length_mm": stack_len,
        "wall_mm": 10,
        "bore_id_mm": vals.get("housing_od", 280) - 20,
    }


def main() -> None:
    parts = sorted(SCAD_DIR.glob("*.scad"))
    audit = {
        "generated_constants": housing_summary(),
        "aeh_panel": helmholtz_summary(),
        "parts": [parse_scad(p) for p in parts],
        "part_count": len(parts),
        "assembly_files": [p.name for p in parts if "assembly" in p.name],
    }
    EXPORT.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"Wrote {EXPORT} ({audit['part_count']} parts)")


if __name__ == "__main__":
    main()
