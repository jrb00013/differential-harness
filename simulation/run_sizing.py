#!/usr/bin/env python3
"""CLI: size skid and write exports for CAD."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from simulation.sizing import export_sizing, sizing_to_openscad_constants

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "exports"
SCAD_LIB = ROOT / "hardware" / "openscad" / "lib"


def main() -> None:
    p = argparse.ArgumentParser(description="CHORUS-SGH-1 skid sizing")
    p.add_argument("--power", type=float, default=10.0, help="Target electrical equivalent W")
    p.add_argument("--density", type=float, default=8.0, help="W/m² design point (PRO bench tune)")
    args = p.parse_args()

    s = export_sizing(EXPORTS / "sgh1_sizing.json", P_target_W=args.power, P_density_W_m2=args.density)
    SCAD_LIB.mkdir(parents=True, exist_ok=True)
    (SCAD_LIB / "generated_constants.scad").write_text(
        sizing_to_openscad_constants(s), encoding="utf-8"
    )

    design = {
        "title": "CHORUS-Skid SGH-1 Design Export",
        "sizing": json.loads((EXPORTS / "sgh1_sizing.json").read_text()),
        "claims": {
            "safest": "PRO salinity-gradient core",
            "smartest": "Ultrasonic CP gain + PRO",
            "strangest": "TSC + AEH urban panel",
            "civilization": "Co-located desal brine + effluent + CHORUS skid",
        },
    }
    (EXPORTS / "sgh1_design.json").write_text(json.dumps(design, indent=2), encoding="utf-8")
    print(f"Wrote {EXPORTS / 'sgh1_sizing.json'}")
    print(f"Wrote {SCAD_LIB / 'generated_constants.scad'}")
    print(f"Membrane area: {s.A_mem_m2:.3f} m², plates: {s.n_plates}, ΔP* ≈ {s.delta_P_star_bar:.1f} bar")


if __name__ == "__main__":
    main()
