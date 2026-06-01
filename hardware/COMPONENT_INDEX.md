# CHORUS-SGH-1 Component Index (complete)

## PRO fluid path

| ID | OpenSCAD | STL | Notes |
|----|----------|-----|-------|
| PRO-01 | `sgh1_membrane_housing.scad` | ✓ | Stack shell |
| PRO-02 | `sgh1_membrane_plate.scad` | ✓ | Spacer + window |
| PRO-03 | `sgh1_end_cap.scad` | ✓ | Qty 2 (feed + draw) |
| PRO-04 | `sgh1_pressure_vessel_ring.scad` | ✓ | Qty 2 |
| PRO-05 | `sgh1_manifold_feed.scad` | ✓ | Low salinity |
| PRO-06 | `sgh1_manifold_draw.scad` | ✓ | High pressure |
| PRO-07 | `sgh1_px_module.scad` | ✓ | Pressure work recovery |
| PRO-08 | `sgh1_turbine_housing.scad` | ✓ | Pelton / generator mount |
| PRO-09 | `sgh1_relief_valve_block.scad` | ✓ | Safety |

## CHORUS / AEH

| ID | OpenSCAD | Notes |
|----|----------|-------|
| CHOR-01 | `chorus_skid_enclosure.scad` | Thermal/moist plenum |
| AEH-01 | `chorus_aeh_panel.scad` | 6×4 Helmholtz cells |
| AEH-02 | `sgh1_us_mount_ring.scad` | Ultrasonic clamp |

## Structure & utilities

| ID | OpenSCAD | Notes |
|----|----------|-------|
| STR-01 | `sgh1_skid_frame.scad` | Main frame |
| STR-02 | `sgh1_drip_tray.scad` | Brine containment |
| STR-03 | `sgh1_mount_rail.scad` | Module slide rails |
| UT-01 | `sgh1_pump_mount.scad` | Feed pump |
| UT-02 | `sgh1_sensor_bracket.scad` | DAQ |
| UT-03 | `sgh1_feed_tank_adapter.scad` | Tank top fitting |
| UT-04 | `sgh1_brine_tank_adapter.scad` | Brine return |
| UT-05 | `sgh1_flange_adapter.scad` | 2" tri-clamp style |

## v2 module

| ID | OpenSCAD | Notes |
|----|----------|-------|
| RED-01 | `sgh1_red_cartridge_v2.scad` | Swap-in RED stack |

## Assemblies

| File | Purpose |
|------|---------|
| `sgh1_assembly.scad` | Installed layout |
| `sgh1_exploded_assembly.scad` | Exploded view for docs |
