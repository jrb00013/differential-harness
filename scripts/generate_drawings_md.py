#!/usr/bin/env python3
"""Emit hardware/DRAWINGS_DIMENSIONS.md from exports/sgh1_sizing.json."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
s = json.loads((ROOT / "exports" / "sgh1_sizing.json").read_text())
md = f"""# SGH-1 Dimensioned Drawing Table (auto-generated)

| Parameter | Value | Unit |
|-----------|-------|------|
| Target power | {s['P_target_W']} | W |
| Membrane area (total) | {s['A_mem_m2']:.4f} | m² |
| Active plate | {s['active_width_mm']} × {s['active_height_mm']} | mm |
| Plate count | {s['n_plates']} | — |
| Housing OD × length | {s['housing_od_mm']} × {s['housing_length_mm']} | mm |
| Bolt circle | {s['bolt_pattern_mm']} | mm |
| Skid frame L × W × H | {s['frame_length_mm']} × {s['frame_width_mm']} × {s['frame_height_mm']} | mm |
| Δπ | {s['delta_pi_MPa']:.3f} | MPa |
| ΔP* (operating) | {s['delta_P_star_bar']:.2f} | bar |
| Feed flow (sim) | {s['Q_feed_L_min']:.3f} | L/min |
| c_draw / c_feed | {s['c_draw']} / {s['c_feed']} | mol/m³ |

## Tolerances (shop)

| Feature | Tolerance |
|---------|-----------|
| Housing bore | +0.2 / -0.0 mm |
| O-ring groove | per AS568 dash |
| Manifold ports | NPT thread class |
| Frame extrusion cut | ±1 mm |

## OpenSCAD → STL

See `hardware/scripts/export_stl.sh`.
"""
(ROOT / "hardware" / "DRAWINGS_DIMENSIONS.md").write_text(md, encoding="utf-8")
print("Wrote hardware/DRAWINGS_DIMENSIONS.md")
