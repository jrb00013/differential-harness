# differential-harness

**CHORUS-Skid SGH-1 + AEH-1** — full hardware blueprint: **23 OpenSCAD parts**, simulation, DAQ, BOM, test protocol, patent playbook.

## One command

```bash
cd ~/projects/differential-harness
python3 -m venv .venv && source .venv/bin/activate && pip install -e .
chmod +x scripts/build_all.sh hardware/scripts/export_stl.sh
./scripts/build_all.sh
```

Requires [OpenSCAD](https://openscad.org/) for STL export: `sudo apt install openscad`

## What you get

| Category | Count | Location |
|----------|-------|----------|
| **OpenSCAD parts** | 23 | [hardware/openscad/](hardware/openscad/) |
| **STL exports** | 23 | [hardware/stl/](hardware/stl/) after export |
| **Docs** | 12+ | [docs/](docs/), [hardware/BUILD_BLUEPRINT.md](hardware/BUILD_BLUEPRINT.md) |
| **BOM lines** | 35+ | [hardware/bom/SGH1_BOM.csv](hardware/bom/SGH1_BOM.csv) |
| **Python sim** | 6 modules | [simulation/](simulation/) |
| **DAQ** | 3 scripts | [daq/](daq/) |
| **Notebooks** | 2 | [notebooks/](notebooks/) |

## CAD part list

**PRO path:** membrane_housing, membrane_plate, end_cap, manifolds (feed/draw), pressure_ring, px_module, turbine_housing, relief_valve_block  

**CHORUS/AEH:** skid_enclosure, aeh_panel, us_mount_ring  

**Structure:** skid_frame, drip_tray, mount_rail, pump_mount, sensor_bracket  

**Utilities:** feed/brine tank adapters, flange_adapter  

**v2:** red_cartridge_v2  

**Assemblies:** sgh1_assembly, sgh1_exploded_assembly  

Index: [hardware/COMPONENT_INDEX.md](hardware/COMPONENT_INDEX.md)  
Dimensions: [hardware/DRAWINGS_DIMENSIONS.md](hardware/DRAWINGS_DIMENSIONS.md) (auto-generated)

## PDF report

```bash
cd ~/projects/pdf-genesis && pip install -e .
pdf-genesis build ../differential-harness/exports/sgh1_design.json \
  -o ../differential-harness/exports/SGH1_Design_Report.pdf
```

## Wiring & test

- [hardware/electrical/WIRING.md](hardware/electrical/WIRING.md)
- [docs/SGH1_TEST_PROTOCOL.md](docs/SGH1_TEST_PROTOCOL.md)
- [docs/SGH1_PATENT_AND_DEPLOYMENT.md](docs/SGH1_PATENT_AND_DEPLOYMENT.md)
