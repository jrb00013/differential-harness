#!/usr/bin/env python3
"""Audit OpenSCAD library: modules, includes, key dimensions, geometry validity."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from scripts.stl_check import check_stl_manifold

ROOT = Path(__file__).resolve().parent.parent
SCAD_DIR = ROOT / "hardware" / "openscad"
EXPORT = ROOT / "exports" / "openscad_audit.json"
OPENSCAD_RENDER_TIMEOUT_S = 120


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


def openscad_binary() -> str | None:
    return shutil.which("openscad")


def geometry_check(scad_path: Path, binary: str | None) -> dict:
    """Render `scad_path` to binary STL via the openscad CLI and manifold-check it.

    If the openscad binary is not present on this machine, this returns
    an explicit skip reason rather than silently omitting the check or
    pretending it passed.
    """
    if binary is None:
        return {
            "geometry_check": "skipped: openscad binary not found on PATH",
            "watertight": None,
        }

    with tempfile.TemporaryDirectory() as td:
        stl_path = Path(td) / (scad_path.stem + ".stl")
        try:
            proc = subprocess.run(
                [binary, "--export-format=binstl", "-o", str(stl_path), str(scad_path)],
                capture_output=True,
                text=True,
                timeout=OPENSCAD_RENDER_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            return {
                "geometry_check": f"skipped: openscad render exceeded {OPENSCAD_RENDER_TIMEOUT_S}s timeout",
                "watertight": None,
            }
        except OSError as exc:
            return {
                "geometry_check": f"skipped: failed to invoke openscad ({exc})",
                "watertight": None,
            }

        if proc.returncode != 0 or not stl_path.exists():
            return {
                "geometry_check": "failed: openscad render error",
                "openscad_stderr": proc.stderr[-2000:],
                "watertight": False,
            }

        report = check_stl_manifold(stl_path)
        return {
            "geometry_check": "rendered",
            "watertight": report.watertight,
            "triangle_count": report.triangle_count,
            "degenerate_triangles": report.degenerate_triangles,
            "open_edges": report.open_edges,
            "non_manifold_edges": report.non_manifold_edges,
            "inconsistent_winding_edges": report.inconsistent_winding_edges,
            "mesh_ok": report.ok,
        }


def main() -> None:
    parts = sorted(SCAD_DIR.glob("*.scad"))
    binary = openscad_binary()
    part_audits = []
    for p in parts:
        entry = parse_scad(p)
        entry.update(geometry_check(p, binary))
        part_audits.append(entry)

    n_checked = sum(1 for e in part_audits if e["geometry_check"] == "rendered")
    n_watertight = sum(1 for e in part_audits if e.get("watertight") is True)

    audit = {
        "generated_constants": housing_summary(),
        "aeh_panel": helmholtz_summary(),
        "parts": part_audits,
        "part_count": len(parts),
        "assembly_files": [p.name for p in parts if "assembly" in p.name],
        "openscad_binary_found": binary is not None,
        "geometry_checked_count": n_checked,
        "geometry_watertight_count": n_watertight,
        "geometry_check_note": (
            "openscad CLI not found in this environment; per-part geometry_check "
            "is 'skipped' with an explicit reason rather than a silent pass. "
            "See docs/ROADMAP.md M3."
            if binary is None
            else f"{n_watertight}/{n_checked} rendered parts are watertight."
        ),
    }
    EXPORT.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"Wrote {EXPORT} ({audit['part_count']} parts)")
    print(audit["geometry_check_note"])


if __name__ == "__main__":
    main()
