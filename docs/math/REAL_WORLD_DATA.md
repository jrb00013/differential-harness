# Real-World Data Anchors for CHORUS / SGH-1 Math

This document ties simulation defaults to published and operational data. Use with `simulation/real_world_calibration.py`.

## Salinity pairs (mol/m³ NaCl equivalent)

| Stream | Literature value | mol/m³ (i=2 π) | Source |
|--------|------------------|----------------|--------|
| Seawater feed | 35–37 g/L TDS | ~600 | WaterReuse SWRO concentrate WP; Perth 36–39 g/L |
| SWRO brine reject | 52–70 g/L (1.5–2× seawater) | **1200–1400** | WaterReuse; Perth ~70 g/L; CMU ~1.2 M |
| Treated WW / river | 5–20 mol/m³ class | **5–20** | SGH-1 feed default 5; river RED 20 |
| Statkraft draw | Seawater | ~600 | Tofte PRO pilot |

**SGH-1 default pair (1400 / 5)** is conservative-high brine vs **Perth operational ~1200 / 35** mixing pair.

## PRO power density (W/m²)

| Context | P'' | Notes | Source |
|---------|-----|-------|--------|
| Commercial viability threshold | **≥ 5** | Industry rule of thumb | Statkraft, SSRN reviews |
| RO membrane @ 30°C, seawater | **6.3** | Half Δπ (~15 bar) | Pedersen et al. 2024 SSRN |
| Practical large-scale | **5–8** | Hollow fiber + PX | Industry reports |
| Lab hypersaline, high P | **25–60** | Not sidestream default | ES&T Lett. McCutcheon et al. |
| Statkraft Tofte pilot | **≤ 1** | Membrane limit | Statkraft / ForwardOsmosisTech |

**Our P''_design = 8 W/m²** aligns with upper practical band; bench must validate L_p.

## Pilot plants

| Plant | Power | P'' / notes | Status |
|-------|-------|-------------|--------|
| Statkraft Tofte | 2–4 kW | ~1 W/m² | Closed 2013 |
| REAPower Trapani RED | 40–60 W gross | 1.6–2.6 W/m² per cell pair | ~50 m² IEM |
| Perth PSDP | 180 GWh/yr for 144 ML/d | 3.2–3.8 kWh/m³ desal | Operational |
| Japan Mega-ton (hybrid) | ~13 W class | 30 bar, SWRO brine | Pilot hybrid |

## Mixing energy (estuary / desal)

| Pair | E_mix per m³ | Source |
|------|--------------|--------|
| Seawater 35 g/L + brine 70 g/L | **~0.14 kWh/m³** | WA desalination SGE paper (Table 1) |
| Fresh + brine | ~1.12 kWh/m³ | Same |

Perth-scale: 216k m³/d streams → **~30 GWh/yr** theoretical mixing (not recoverable as electric without membranes).

## Economics (order-of-magnitude)

| Metric | Range | Source |
|--------|-------|--------|
| PRO LCOE (favorable) | $0.15–0.25/kWh | Patsnap / industry |
| PRO LCOE (general) | $0.20–0.40/kWh | Reviews |
| Membrane $/m² | $4–150 (trend → ~4 €/m² RED IEM) | Frontiers RED review 2024 |

## Implementation in code

```python
from simulation.real_world_calibration import CASE_STUDIES, apply_perth_brine_pair

st = apply_perth_brine_pair()  # c_draw=1200, c_feed from seawater diluate
```

Update `constants.py` comments when changing defaults.

## References (verify DOI before publication)

1. WaterReuse, Seawater Concentrate White Paper — brine 52–70 ppt.  
2. Pedersen et al., SSRN 4944813 (2024) — 6.3 W/m² commercial RO at 30°C.  
3. McCutcheon et al., *Environ. Sci. Technol. Lett.* — high-P PRO lab.  
4. Statkraft Tofte — Wikipedia; Power Technology; ForwardOsmosisTech.  
5. Tedesco et al., *Desalination* — REAPower Trapani RED pilot.  
6. Gude, SciEPublish — Perth SGE 0.14 kWh/m³ mixing.  
7. Frontiers frmst.2024.1414721 — RED economics and P''.  
8. PMC11901225 — PRO pretreatment; Japan Mega-ton mention.
