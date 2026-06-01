# OpenSCAD Deep Dive — CHORUS-Skid SGH-1

Auto-audit: `python scripts/audit_openscad.py` → `exports/openscad_audit.json`

## Design pipeline

```
simulation/run_sizing.py  →  exports/sgh1_sizing.json
                         →  hardware/openscad/lib/generated_constants.scad
                         →  all part .scad files
hardware/scripts/export_stl.sh  →  hardware/stl/*.stl
```

## Generated constants (single source of truth)

| Variable | Meaning |
|----------|---------|
| `P_target_W` | Design electrical target |
| `A_mem_m2` | Total active membrane area |
| `active_w`, `active_h` | Plate window (mm) |
| `n_plates` | Stack count (CAD cap 12) |
| `housing_od`, `housing_len` | Cylinder shell |
| `bolt_circle` | Flange bolt pattern |
| `frame_L`, `frame_W`, `frame_H` | Skid envelope |
| `delta_P_bar` | Kim–Baker operating pressure |
| `plate_pitch` | Axial spacing per cell |

## PRO fluid path (PRO-01 … PRO-09)

| File | Function |
|------|----------|
| `sgh1_membrane_housing.scad` | Cylinder shell, plate rails, sensor slot |
| `sgh1_membrane_plate.scad` | Spacer/window per cell |
| `sgh1_end_cap.scad` | Feed and draw end closures |
| `sgh1_pressure_vessel_ring.scad` | Compress ring |
| `sgh1_manifold_feed.scad` | Low-sal distribution |
| `sgh1_manifold_draw.scad` | High-pressure brine header |
| `sgh1_px_module.scad` | Pressure exchanger body |
| `sgh1_turbine_housing.scad` | Hydraulic test load mount |
| `sgh1_relief_valve_block.scad` | 1.2× ΔP* safety |

**Housing stack length:** `n_plates × plate_pitch + 40` mm (end allowances).

## CHORUS / AEH (CHOR-01, AEH-01, AEH-02)

| File | Function |
|------|----------|
| `chorus_skid_enclosure.scad` | Moist/thermal plenum around stack |
| `chorus_aeh_panel.scad` | 6×4 Helmholtz cells, piezo pockets, US mount |
| `sgh1_us_mount_ring.scad` | Clamps 28 kHz transducer to feed path |

**AEH panel (derived):** width ≈ 0.6 × frame_W (288 mm), height 400 mm, thickness 28 mm,  
24 resonators (neck 8 mm, cavity 35 mm).

## Structure & utilities

`sgh1_skid_frame.scad`, `sgh1_drip_tray.scad`, `sgh1_mount_rail.scad`,  
`sgh1_pump_mount.scad`, `sgh1_sensor_bracket.scad`, tank adapters, `sgh1_flange_adapter.scad`.

## Assemblies

- `sgh1_assembly.scad` — installed layout for review  
- `sgh1_exploded_assembly.scad` — documentation exploded view  
- `sgh1_red_cartridge_v2.scad` — swap-in RED stack (v2)

## Export

```bash
sudo apt install openscad   # if needed
bash hardware/scripts/export_stl.sh
```

## Tolerances

See `hardware/DRAWINGS_DIMENSIONS.md` — housing bore +0.2/−0.0 mm, NPT manifolds, frame ±1 mm.
