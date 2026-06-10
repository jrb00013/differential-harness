# CHORUS-Skid SGH-1 + AEH-1 — Build Blueprint

Complete hardware build guide. Pair with [docs/SGH1_DEVICE_SPEC.md](../docs/SGH1_DEVICE_SPEC.md) and OpenSCAD in `openscad/`.

## 0. Generate sizing + CAD constants

```bash
cd ~/projects/differential-harness
source .venv/bin/activate
python simulation/run_sizing.py --power 50
bash hardware/scripts/export_stl.sh   # needs OpenSCAD
```

Outputs:
- `exports/sgh1_sizing.json`
- `hardware/openscad/lib/generated_constants.scad`
- `hardware/stl/*.stl`

## 1. System overview

| Subsystem | Part files | Function |
|-----------|------------|----------|
| **PRO core** | `sgh1_membrane_housing`, `sgh1_membrane_plate`, `sgh1_end_cap` ×2, `sgh1_pressure_vessel_ring` | Salinity-gradient power |
| **Fluids** | `sgh1_manifold_feed`, `sgh1_manifold_draw`, `sgh1_pump_mount` | Feed + brine + pressurized draw |
| **CHORUS frame** | `sgh1_skid_frame`, `chorus_skid_enclosure` | Mount + thermal/moist plenum |
| **AEH** | `chorus_aeh_panel` | Acoustic harvest + US mount |
| **Instruments** | `sgh1_sensor_bracket` | Conductivity / pressure / DAQ |

## 2. Build order

1. **Skid frame** — weld or bolt 40×40 aluminum extrusion per `sgh1_skid_frame.stl`; level feet.
2. **Membrane plates** — CNC HDPE/SS316 plates or print HDPE; bond commercial FO/PRO sheet per active window.
3. **Housing** — machine or print shell; install guide rails; torque end caps with Viton O-rings.
4. **Manifolds** — machine feed (low pressure) and draw (rated for `delta_P_bar` from sizing JSON).
5. **Plumb loop** — feed pump → prefilter → feed manifold → stack → draw manifold → PX/turbine test loop → brine return tank.
6. **Enclosure + AEH panel** — bolt to frame; route piezo wires to DAQ; optional US transducer on feed manifold.
7. **DAQ** — `python daq/logger.py`; verify conductivity, ΔP, flow.

## 3. Pressure rating

Design hydraulic pressure on draw side: **ΔP* ≈ Δπ/2** (see `exports/sgh1_sizing.json` → `delta_P_star_bar`).

- Relief valve set at **1.2 × delta_P_star_bar**
- Hydrotest at **1.5 ×** before saline service

## 4. Fluids (bench)

| Stream | Composition (bench) | Tank |
|--------|---------------------|------|
| Feed | NaCl **5 g/L** tap water | 50 L low-sal tank |
| Draw | NaCl **80–140 g/L** (brine simulant) | 50 L high-sal tank |

**Warning:** corrosive — SS316 wetted parts, eye protection, brine containment tray on skid.

## 5. Electrical

- Turbine/alternator or pressure motor on draw loop (measure shaft power).
- AEH panel → rectifier → supercap → Raspberry Pi DAQ (optional).
- US driver: 28 kHz ultrasonic transducer, **separate** from harvest piezos.

## 6. Acceptance test

1. Zero leak hold at 1.0× ΔP* for 10 min.
2. Stable conductivity differential feed vs draw.
3. Positive hydraulic power on draw circuit OR positive electrical from turbine.
4. Log CSV 1 h; compare `P_density` to simulation ±30%.

## 7. Vision hardware (v3 — planned)

See [docs/VISION.md](../docs/VISION.md).

| Part | Purpose |
|------|---------|
| `sgh1_tink_ring.scad` | Toroidal UDT ray / US mounts |
| `sgh1_z_pipe.scad` | Axial hyperspeed draw leg (Z-Hydro) |
| `sgh1_vortex_basin.scad` | Taylor–Couette / halocline cell |

Bench order after SGH-1 T1: T1b (UDT/AOR) → T1c (spinning drum).

## 8. File index (OpenSCAD)

```
hardware/openscad/
  sgh1_assembly.scad          # full layout
  sgh1_membrane_plate.scad
  sgh1_end_cap.scad
  sgh1_membrane_housing.scad
  sgh1_manifold_feed.scad
  sgh1_manifold_draw.scad
  sgh1_pressure_vessel_ring.scad
  sgh1_skid_frame.scad
  chorus_skid_enclosure.scad
  chorus_aeh_panel.scad
  sgh1_pump_mount.scad
  sgh1_sensor_bracket.scad
  lib/generated_constants.scad
  lib/utils.scad
```

Import assembly into **FreeCAD**: File → Import STL from `hardware/stl/`, assemble constraints in `hardware/freecad/SGH1_Assembly.FCStd` (create locally).
