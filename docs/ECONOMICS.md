# CHORUS-SGH-1 Economics — LCOE Model and Honest Competitiveness Assessment

This document grounds a real levelized-cost-of-energy (LCOE) estimate
for CHORUS-SGH-1 in the cost anchors already in this repo
(`hardware/bom/SGH1_BOM.csv`, `docs/math/REAL_WORLD_DATA.md`) plus the
existing PRO physics simulation (`simulation.pro_cycle`,
`simulation.parasitics`), computed by `scripts/lcoe_model.py`. It is
written to be honest, not promotional: **the numbers below show this
technology is not currently cost-competitive with solar, wind, or
battery storage at any power density this repo's simulation can
substantiate**, and that is treated as a real finding, not a defect in
the writeup.

## Model summary

`scripts/lcoe_model.py::compute_lcoe()`:

1. Required membrane area = target power / assumed areal power density
   (W/m²).
2. `simulation.sizing.size_skid` caps a single skid unit's CAD at 12
   membrane plates (~0.72 m²) — a target beyond that is modeled as N
   identical parallel skid units, not one skid with unrealistically
   large membrane area.
3. Capital cost = balance-of-plant (BOP) cost per skid unit (from the
   BOM's own estimate line, `EST-001`, "~$2,500-8,000 excl. membrane
   OEM") × N units, plus membrane cost (area × $/m²).
4. Capital is annualized with a standard capital recovery factor (CRF)
   at a 7% discount rate over a 20-year project life; membrane capital
   is annualized separately over its own (shorter) replacement life,
   since replacing a membrane is a recurring capital expenditure, not
   simple opex.
5. Net energy uses a parasitic-loss derate taken from
   `simulation.parasitics.skid_energy_balance` (pump power, PX
   recovery credit) at a reference skid state, applied to the assumed
   gross areal power. See the caveat below — this derate currently
   floors at 0% because the bench-scale PX recovery credit formula in
   `simulation/parasitics.py` is explicitly documented there as
   "illustrative," not calibrated, and at these small W-scale bench
   numbers it can exceed the pump load. That is a real model
   limitation, not a claim of zero parasitic loss at any real scale.

## Cost anchors used (all sourced, not invented)

| Anchor | Value | Source |
|---|---|---|
| Balance-of-plant cost per skid unit | $2,500 (optimistic) – $8,000 (conservative) | `hardware/bom/SGH1_BOM.csv`, line `EST-001`, "excl. membrane OEM" |
| Membrane cost | $30/m² (optimistic) – $150/m² (conservative) | `docs/math/REAL_WORLD_DATA.md` ($4-150/m² range); a 2024 Frontiers in Energy Research PRO-SWRO techno-economic analysis cites commercial PRO-membrane-provider quotes of **$9.2-12.3/m²**; a real commercial SWRO element (LG Chem SW 400 R, 37 m² active area) retails at **~$21/m²** (wateranywhere.com) as an upper-bound analog since PRO/FO specialty sheets are less commoditized than standard SWRO |
| Membrane replacement interval | 5 (conservative) – 7 (optimistic) years | RO/FO industry maintenance guidance puts commercial membrane life at 3-5 years (Morui); PRO-specific figures were not found publicly — treated as an assumption pending real fouling data, see `docs/FOULING_TEST_PROTOCOL.md` |
| Power density scenarios | 1 W/m² (Statkraft Tofte pilot floor) / 8 W/m² (practical large-scale) / 25 W/m² (lab hypersaline ceiling) | `docs/math/REAL_WORLD_DATA.md` |

## Results (`scripts/lcoe_model.py --sensitivity`)

| Power-density scenario | Cost scenario | Area needed (m², 1 kW target) | LCOE ($/kWh) |
|---|---|---|---|
| Lab optimistic (25 W/m²) | Optimistic cost | 2.16 | **$2.05** |
| Lab optimistic (25 W/m²) | Conservative cost | 2.16 | **$6.65** |
| Practical (8 W/m²) | Optimistic cost | 6.48 | **$6.40** |
| Practical (8 W/m²) | Conservative cost | 6.48 | **$20.78** |
| Statkraft-floor (1 W/m²) | Optimistic cost | 50.4 | **$51.16** |
| Statkraft-floor (1 W/m²) | Conservative cost | 50.4 | **$166.24** |

(Full sweep: `python -m scripts.lcoe_model --sensitivity`.)

## Honest comparison against real benchmarks

From Lazard's LCOE+ report (June 2024, the standard industry reference):

| Technology | LCOE ($/kWh) |
|---|---|
| Utility-scale solar PV (standalone) | **$0.029 – $0.092** (midpoint ~$0.061) |
| Onshore wind (standalone) | **$0.027 – $0.073** (midpoint ~$0.050) |
| Solar + storage | $0.060 – $0.210 |
| Standalone battery storage (100MW/4hr) | $0.124 – $0.296 |

**Even CHORUS-SGH-1's best-case scenario ($2.05/kWh, requiring both a
lab-grade 25 W/m² power density this repo has not validated on real
hardware and optimistic membrane/BOP costs) is ~22-75x more expensive
than solar or wind, and ~7-33x more expensive than standalone battery
storage.** The practical-density scenario (8 W/m², the literature's
"practical large-scale" anchor) is $6.40-$20.78/kWh — 70-750x solar.
The Statkraft-floor scenario, which is what an unimproved real-world
pilot actually achieved in 2009-2013, is $51-$166/kWh — in the range
that led Statkraft to shut the Tofte pilot down in 2014, stating PRO
"would not be competitive with other renewable energy technologies
within the foreseeable future" (POWER Magazine, ForwardOsmosisTech).

**This is not competitive today, and this document says so plainly.**
The honest, useful information here is not "CHORUS-SGH-1 is cheap" but:

1. **Power density is the entire game.** Moving from the Statkraft
   floor (1 W/m²) to the lab ceiling (25 W/m²) closes nearly the whole
   gap between "hopeless" and "merely 20-75x too expensive" — this
   repo's own UDT/AOR/VOH vision-stack work (`docs/UDT_PHYSICS.md`,
   `simulation/differential_tink.py`) exists specifically because
   raising *effective* membrane power density (concentration-
   polarization mitigation via acoustic/vortex actuation) is the only
   lever big enough to matter economically, not a side experiment.
2. **BOP cost dominates over membrane cost at small scale** (compare
   the $/kWh spread across cost scenarios above): at bench/pilot scale,
   fixed per-unit balance-of-plant cost (frame, pumps, sensors, DAQ)
   swamps the membrane's own $/m², meaning larger single-unit skids
   (fewer, bigger units instead of many small ones) is a real cost
   lever this repo's CAD (`hardware/openscad/`) does not yet target —
   the 12-plate bench cap in `simulation/sizing.py` exists for CAD
   printability reasons, not economic ones.
3. **This is a niche co-location technology, not a general
   solar/wind replacement.** The honest framing (see
   `docs/CANDIDATE_SITES.md`) is: CHORUS-SGH-1 only makes any
   economic sense at all where a salinity-gradient feed pair *already
   exists as a waste stream* (a desalination brine outfall, for
   example), because the "fuel" (concentration difference) is free and
   already flowing — the LCOE fight here is purely about capex and
   parasitics on a stream that would otherwise be discharged
   unused, not about competing for siting against solar/wind on
   cost-of-energy alone.

## Known model limitations (stated, not hidden)

- The parasitic-loss derate currently floors at 0% because
  `simulation/parasitics.py::px_recovery_credit_W` is explicitly
  documented as "illustrative" and is not calibrated against real
  pressure-exchanger hardware — at bench-scale wattages it can exceed
  the pump load, which is not physically meaningful at any real
  deployment scale. Real T1c-scale bench data (`docs/ROADMAP.md` M6)
  is required before this derate can be trusted quantitatively.
- No O&M labor cost is modeled beyond a flat 2%/year of capex
  rule-of-thumb; a real pilot's O&M (especially cleaning-in-place for
  fouling, see `docs/FOULING_TEST_PROTOCOL.md`) could be materially
  higher.
- Membrane replacement interval (5-7 years) is an RO/FO industry
  analog, not a PRO-specific or CHORUS-SGH-1-specific measurement —
  PRO fouling is generally understood in the literature to be worse
  than RO (see `docs/FOULING_TEST_PROTOCOL.md`), so this may be
  optimistic.
- Capacity factor is assumed at 90% (a continuously-fed brine/estuary
  stream, unlike solar's ~25% or wind's ~35%) but this has not been
  validated against any real operating data — biofouling-driven
  downtime (again, see `docs/FOULING_TEST_PROTOCOL.md`) could reduce
  it substantially.

## Sources

- Lazard, *LCOE+ Report*, June 2024 — https://www.lazard.com/media/xemfey0k/lazards-lcoeplus-june-2024-_vf.pdf
- pv magazine, "Lazard says fossil fuel costs double that of utility-scale solar," June 2024 — https://www.pv-magazine.com/2024/06/12/lazard-says-fossil-fuel-costs-double-that-of-utility-scale-solar/
- POWER Magazine, "Statkraft Shelves Osmotic Power Project" — https://www.powermag.com/statkraft-shelves-osmotic-power-project/
- ForwardOsmosisTech, "Is PRO economically feasible? Not according to Statkraft" — https://www.forwardosmosistech.com/statkraft-discontinues-investments-in-pressure-retarded-osmosis-2/
- Frontiers in Energy Research, "Techno-economic analysis of a PRO-SWRO hybrid," 2024 — https://www.frontiersin.org/journals/energy-research/articles/10.3389/fenrg.2024.1448402/full
- WaterAnywhere, LG Chem SW 400 R SWRO element listing — https://wateranywhere.com/products/8x40-seawater-9-000-gpd-800-psi-99-85-rej-400-ft2-lg-chem-ro-membrane
- Morui, "Typical operating costs and lifespan of industrial RO membranes" — https://www.moruiwater.com/knowledge/typical-operating-costs-and-lifespan-of-industrial-ro-membranes
- `docs/math/REAL_WORLD_DATA.md` (this repo) and its own references list.
