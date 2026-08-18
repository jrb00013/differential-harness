# differential-harness

**CHORUS-Skid SGH-1 + AEH-1** — full hardware blueprint: **23 OpenSCAD parts**, simulation, DAQ, BOM, test protocol, patent playbook.

## Vision — osmotic-vortex hydro (VOH)

**Master index:** [docs/VISION.md](docs/VISION.md)

| Layer | Doc | Sim |
|-------|-----|-----|
| **UDT** — Universal Differential Tink (rays, particle bytes) | [UDT_PHYSICS.md](docs/UDT_PHYSICS.md) | `differential_tink.py` |
| **AOR** — Acoustic-Osmotic Ram (sound + brine + ram pipe) | [AOR_PHYSICS.md](docs/AOR_PHYSICS.md) | `acoustic_osmotic_ram.py` |
| **VOH** — Vortex-Osmotic Hydro / Z-Hydro (spin + z-leg) | [VOH_PHYSICS.md](docs/VOH_PHYSICS.md) | `vortex_osmotic_hydro.py` |

```bash
python -m simulation.experiments   # exports vision_stack (E14–E16) in paper_experiments.json
```

## Bench validation (T0–T1)

```bash
pip install -e ".[dev]"
python -m daq.logger --test T1 --duration 3600          # 1 h CSV → data/bench/
python -m simulation.bench_validation --csv data/bench/T1_*.csv
python scripts/run_test_protocol.py --test T1           # full protocol + auto validation
pytest tests/
```

Notebooks: `notebooks/T1_bench_validation.ipynb`, `notebooks/VOH_spin_breakeven.ipynb`

## Real DAQ ingestion, calibration, geometry audit, dashboard

See [docs/ROADMAP.md](docs/ROADMAP.md) for the full current-state /
roadmap and an honest per-item completion status; execution order is
in [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md).

```bash
# Real serial ingestion (pyserial): opens --port for real, decodes
# checksummed $SGH1/$SGHV frames (daq/protocol.py), falls back to
# simulation ONLY on open/read failure, with a loud repeated warning.
python -m daq.serial_sensors --port /dev/ttyUSB0 --duration 60

# Fit L_p / RPM->torque constants from bench CSVs (labels data
# provenance simulated/real explicitly; never fabricates "real").
python -m scripts.calibrate_constants --csv data/bench/*.csv

# CAD geometry manifold/watertightness check (shells out to `openscad`
# CLI when installed; otherwise records an explicit per-part skip
# reason instead of a silent pass).
python -m scripts.audit_openscad

# Resumable protocol runner: re-enter at the first incomplete step
# instead of restarting from T0 after a crash/disconnect.
python scripts/run_test_protocol.py --test all
python scripts/run_test_protocol.py --test all --resume

# Live dashboard over an active/completed bench CSV (stdlib only).
python -m daq.dashboard --csv data/bench/T1_baseline_20260609_235853.csv
```

## Research paper (PoC)

**Joseph Black** and **Connor White** — *CHORUS-SGH-1: Brine-Gradient Power, UDT/AOR/VOH Vision, and Osmotic-Vortex Hydro* ([PDF](papers/Black_2026_CHORUS_SGH1_PoC.pdf) · [source](papers/black_2026_chorus_sgh1_poc.md))

```bash
pip install -e ".[paper]"
python -m simulation.experiments      # exports/paper_experiments.json
python scripts/generate_paper_figures.py  # exports/figures/*.png
python scripts/build_research_paper.py  # papers/Black_2026_CHORUS_SGH1_PoC.pdf (~20+ pages with figures)
```

Math supplements: [docs/math/](docs/math/) · **Real-world anchors:** [REAL_WORLD_DATA.md](docs/math/REAL_WORLD_DATA.md) (Statkraft, Perth, Trapani, 6.3 W/m² PRO)

```bash
./scripts/run_paper_pipeline.sh   # experiments + calibration + figures + PDF

# Or from pdf-genesis (uses .pdf-genesis/manifest.json):
pdf-genesis repo .                  # full pipeline + Black_2026 PDF
pdf-genesis repo . --mode compile   # markdown compendium only
```

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
| **Python sim** | 9+ modules | [simulation/](simulation/) |
| **Vision docs** | 4 | [docs/VISION.md](docs/VISION.md) |
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
