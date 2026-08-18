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
the writeup. Round 4 (below) goes further and asks whether any
combination of parameters, manufacturing scale, or reframing closes
that gap — the honest answer is "not with any single lever, and only
approaches battery-storage-adjacent economics (not solar/wind) under
two simultaneous, currently-unproven extremes."

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

## Round 4 — attacking the gap directly

Round 3 found the gap; round 4 asks whether any real combination of
parameters, manufacturing scale, or reframing closes it.
`scripts/lcoe_model.py` gained `breakeven_report()`,
`volume_cost_projection()`, and `co_benefit_adjusted_lcoe()` to answer
this with real code, not narrative optimism.

### R4.1 — Breakeven sensitivity: is there a single-lever path?

`scripts/lcoe_model.py::breakeven_report(target_lcoe, ...)` bisects for
the value of power density, membrane cost, or membrane replacement life
that would be needed to hit a target LCOE, holding everything else at
its default (conservative-cost) value, then checks the solved value
against a real ceiling (60 W/m² lab-hypersaline density, $0/m² cost
floor, 15-year industrial RO/FO membrane life):

```
$ python -m scripts.lcoe_model --breakeven 0.09 --power-w 1000
```

**Result: reaching Lazard's solar/wind upper bound ($0.09/kWh) is
UNREACHABLE via any single lever.** Power density would need to exceed
240 W/m² (4x the highest lab-reported PRO density in the literature).
Membrane cost would need to go negative. Membrane life would need to
exceed 150 years. None of these are physically meaningful — **there is
no single-parameter path to solar/wind competitiveness.**

Even stacking every optimistic lever simultaneously (60 W/m² lab
ceiling, a free membrane, a 15-year life, and the cheapest BOP
scenario) at once:

```python
>>> compute_lcoe(P_target_W=1000, P_density_W_m2=60.0,
...     membrane_cost_usd_m2=0.0, membrane_life_years=15.0,
...     bop_cost_usd_per_skid=2500.0).lcoe_usd_per_kWh
0.84
```

**$0.84/kWh — still ~9-28x above solar/wind, even in a scenario that
requires simultaneously exceeding the highest lab-reported power
density AND a free membrane.** This confirms round 3's framing:
capital cost (specifically BOP capex — frame, pumps, sensors, DAQ) is
the dominant term, not membrane cost, and no single lever closes it.

### R4.2 — Manufacturing scale: does volume help?

`scripts/lcoe_model.py::volume_cost_projection()` applies a Wright's-law
learning curve (cost declines a constant % per doubling of cumulative
units produced) to this repo's own BOM baseline, across three cited
learning-rate scenarios (10% conservative/simple-hardware analog, 15%
Wright's original 1936 aircraft-manufacturing rate, 20% solar PV's
sustained real-world rate — no PRO/FO-membrane- or small-batch-BOP-
specific learning rate exists in the public literature, stated plainly
rather than invented):

```
$ python -m scripts.lcoe_model --learning-curve
```

| Volume | Learning rate | BOP cost/skid | LCOE @ practical density (8 W/m²) |
|---|---|---|---|
| 1x (today) | — | $8,000 | $20.78/kWh |
| 1000x | 10% conservative | $2,800 | $7.27/kWh |
| 1000x | 15% typical | $1,584 | $4.11/kWh |
| 1000x | 20% solar-analog | $866 | $2.25/kWh |

**Even at 1000x cumulative manufacturing volume and the most optimistic
(solar-analog) learning rate, at PRACTICAL power density, LCOE stays at
$2.25/kWh — manufacturing scale ALONE does not close the gap either.**
Only combining 1000x volume with lab-hypersaline density (60 W/m²)
approaches order-of-magnitude parity with standalone battery storage:

```python
>>> compute_lcoe(P_target_W=1000, P_density_W_m2=60.0,
...     bop_cost_usd_per_skid=865.6, membrane_cost_usd_m2=16.2,
...     membrane_life_years=15.0).lcoe_usd_per_kWh
0.295
```

**$0.295/kWh — within Lazard's standalone battery storage range
($0.124-0.296/kWh), but still 3-10x above solar/wind directly.** This
requires validating two separate, extreme, currently-unproven
assumptions at once (lab-grade power density AND 1000x manufacturing
scale), neither of which this repo's own T0-T2 protocol has confirmed
achievable on real hardware.

### R4.3 — Value beyond raw $/kWh: is there a co-benefit case?

Two distinct arguments were tested, honestly, for whether the raw
$/kWh comparison is even the right frame:

1. **"The brine is already flowing, so fuel is free."** True, but
   **this is already fully reflected in `compute_lcoe()`** — there has
   never been a fuel-cost line item anywhere in the model, because the
   concentration-gradient "fuel" genuinely costs nothing. This
   argument does not provide an *additional* credit beyond what's
   already modeled; it only explains why capex and power density are
   the entire economic story, which is exactly what R4.1/R4.2 above
   attack. Counting it a second time as a "co-benefit" would be
   double-counting.
2. **Avoided transmission & distribution (T&D) cost.** A generator
   co-located at the point of use (a desalination brine outfall, a
   coastal WWTP) genuinely avoids the T&D infrastructure cost a
   grid-delivered kWh carries. Real utility avoided-cost studies
   quantify this at **~$0.02/kWh** (one CPUC-referenced analysis found
   avoided transmission (1.34¢/kWh) + avoided distribution (0.52¢/kWh)
   = "at least 2.02¢/kWh"). `scripts/lcoe_model.py::co_benefit_adjusted_lcoe()`
   applies this as a real, cited credit:

```
$ python -m scripts.lcoe_model --power-w 1000 --co-benefit
```

**Result: at CHORUS-SGH-1's actual multi-dollar/kWh LCOE scale, this
real credit offsets well under 1% of the raw number** (e.g. $20.78/kWh
→ $20.76/kWh). It is real and worth stating, but it is not remotely
large enough to matter at today's cost structure — it would only start
to matter at an LCOE already close to competitive, which round 4's own
best-case combined scenario ($0.295/kWh) is the closest this analysis
gets to.

### Round 4 bottom line

**No single lever, and no combination of realistic (non-simultaneous-
extreme) levers, closes the gap to solar or wind. A combination of two
simultaneous, currently-unvalidated extremes — lab-hypersaline power
density (60 W/m², never demonstrated outside non-representative lab
conditions per the literature this repo has anchored) AND 1000x
manufacturing scale at a solar-like learning rate (never demonstrated
for this hardware class at all) — gets CHORUS-SGH-1 into the same
order of magnitude as standalone battery storage, not solar/wind
generation directly.** This is the honest answer round 4 was asked to
find: not "here's a plausible path to competitiveness," and not
"the physics fundamentally caps this at any scale" either — it is
"closing this gap requires two separate, extreme, currently-unproven
technical achievements simultaneously, and even then only reaches
battery-storage-adjacent economics, not general renewable-generation
economics." Anything short of both of those simultaneous achievements
leaves this a niche, waste-stream-co-location technology exactly as
round 3 concluded, not a general power-generation competitor.

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
- Our World in Data, "Learning curves: What does it mean for a technology to follow Wright's Law?" — https://ourworldindata.org/learning-curve
- Metavert, "Wright's Law" (solar PV ~20% learning rate over 4+ decades; Wright's original ~15% aircraft-manufacturing rate) — https://metavert.io/wrights-law
- CPUC, T&D avoided-cost study webinar slide deck (avoided transmission 1.34¢/kWh + avoided distribution 0.52¢/kWh) — https://www.cpuc.ca.gov/-/media/cpuc-website/divisions/energy-division/documents/energy-efficiency/ider-cost-effectiveness/td-study-webinar-slide-deck.pdf
- Demand Side Analytics, "Pennsylvania Transmission and Distribution (T&D) Avoided Cost Study" — https://demandsideanalytics.com/pennsylvania-transmission-and-distribution-td-avoided-cost-study/
- `docs/math/REAL_WORLD_DATA.md` (this repo) and its own references list.
