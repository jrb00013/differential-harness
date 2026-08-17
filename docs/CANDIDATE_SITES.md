# CHORUS-SGH-1 Candidate Deployment Sites

`docs/ECONOMICS.md` concludes CHORUS-SGH-1 only makes economic sense
where a salinity-gradient feed pair already exists as a waste/byproduct
stream — the "fuel" (concentration difference) must be free and already
flowing, because the technology cannot win a cost-of-energy fight
against solar/wind on its own. This document grounds that claim in real,
publicly documented site types with real salinity/flow figures, rather
than a generic "co-locate at a desalination plant" thought experiment.

## Site type 1 — Large SWRO desalination brine outfall: Perth Seawater Desalination Plant, Australia

- Combined Stage 1 + Stage 2 (PSDP1+2) brine discharge ≈ **418 ML/day**
  (~418,000 m³/day); Stage 1 alone discharges at ~2.19 m³/s.
- Brine salinity ≈ **1.8× ambient seawater** — ambient Indian Ocean
  seawater off Perth ~35 g/L (consistent with `docs/math/REAL_WORLD_DATA.md`'s
  "Perth 36-39 g/L" seawater anchor), brine ~63 g/L.
- Outfall: 1.6 m diameter pipe extending 500 m offshore, multi-port
  diffuser angled 60°, licensed for a 45× dilution factor by 50 m from
  the diffuser.
- **Fit for CHORUS-SGH-1**: this is the closest real-world match to the
  repo's own default salinity pair (`C_BRINE_8PCT` ≈ 1400 mol/m³ /
  `C_TREATED_WW` ≈ 5 mol/m³ in `simulation/constants.py`, noted there as
  "conservative-high brine vs. Perth operational ~1200/35 mixing
  pair"). A CHORUS-SGH-1 skid could intercept a slipstream of the
  pre-diffuser brine and mix it with an available lower-salinity stream
  (e.g. treated effluent, harbor water) before it re-enters the outfall
  — recovering some energy from a concentration gradient that is
  otherwise dissipated for free in the diffuser's dilution zone.
- Sources: [Numerical simulations of brine dispersion, PSDP2 (IAHR)](https://static.iahr.org/34/122.pdf), [PSDP2 Environmental Referral Document (WA EPA)](https://www.epa.wa.gov.au/sites/default/files/Referral_Documentation/2.%20PSDP2_Environmental_Referral_Document_Part%20A.pdf)

## Site type 2 — Large SWRO desalination brine outfall: Carlsbad Desalination Plant, California

- Produces 50 MGD (≈189,250 m³/day) of product water and 50 MGD
  (≈189,250 m³/day) of brine concentrate at **~67,000 ppm TSS (~67
  g/L)**, roughly 2× incoming seawater salinity — before the plant's
  own required pre-discharge dilution with intake seawater (up to a
  combined 238 MGD / ~901,000 m³/day permitted discharge scenario, at a
  target diluted salinity of ~42 ppt).
- Documented plume behavior: even after dilution, the discharge plume
  has been observed extending ~600 m offshore with salinity up to 2.7
  units above the ~33.2 ppt ambient baseline — i.e. real, measured
  evidence that dilution capacity is a genuine engineering/permitting
  constraint at this site, not a theoretical concern (see
  `docs/ENVIRONMENTAL_IMPACT.md`).
- **Fit for CHORUS-SGH-1**: structurally identical opportunity to
  Perth — a co-located skid could use some of the plant's own required
  dilution water flow as the low-salinity draw stream, extracting PRO
  power from a mixing step the plant must perform anyway for permit
  compliance.
- Sources: [Biological and Physical Effects of Brine Discharge from Carlsbad (MDPI Water, 2019)](https://www.mdpi.com/2073-4441/11/2/208), [San Diego County Water Authority — Seawater Desalination](https://www.sdcwa.org/your-water/local-water-supplies/seawater-desalination/), [CA Water Boards — Carlsbad Desalination Plant regulatory page](https://www.waterboards.ca.gov/sandiego/water_issues/programs/regulatory/carlsbad_desalination.html)

## Site type 3 — River-mouth/fjord estuary gradient: Statkraft Tofte pilot site, Oslo Fjord, Norway

- The only real-world PRO pilot at meaningful scale to date (2,000 m²
  membrane, opened Nov 2009, shelved Jan 2014): fed by Tofte River
  freshwater against Oslo Fjord seawater, using ~120 m equivalent
  water-column pressure across 66 pressure pipes, producing only 2-4
  kW — a realized power density of **~1-2 W/m²**, far below the ~5
  W/m² industry viability threshold.
- **Honest gap**: this research pass could not independently confirm a
  specific Oslo Fjord salinity (ppt) figure — Oslo Fjord is a
  brackish-influenced estuary and its salinity is very likely below
  open-ocean 35 g/L, but that number is not asserted here without a
  verified source. This is flagged explicitly rather than filled in
  with an invented figure.
- **Fit for CHORUS-SGH-1**: this is the real-world proof that a
  river/fjord-mouth site is a valid site *type*, but also the
  strongest cautionary data point in `docs/ECONOMICS.md` and
  `docs/FOULING_TEST_PROTOCOL.md` — the Tofte pilot's failure to reach
  economic power density, compounded by fouling from real (not clean
  bench) water, is exactly the failure mode this repo's protocol work
  is trying to test for before committing to a real site.
- Sources: [Statkraft osmotic power prototype in Hurum (Wikipedia)](https://en.wikipedia.org/wiki/Statkraft_osmotic_power_prototype_in_Hurum), [POWER Magazine — Norway Inaugurates Osmotic Power Plant](https://www.powermag.com/norway-inaugurates-osmotic-power-plant/), [POWER Magazine — Statkraft Shelves Osmotic Power Project](https://www.powermag.com/statkraft-shelves-osmotic-power-project/)

## Site type 4 — Generic SWRO brine concentrate class (WaterReuse white paper anchor)

Already cited in this repo's `docs/math/REAL_WORLD_DATA.md`: the
WaterReuse Association's Seawater Concentrate White Paper documents
SWRO brine reject in the **52-70 g/L** range (1.5-2× seawater), which
is the general class both Perth and Carlsbad fall into. This matters
as a *class*, separate from the two named sites above, because it is
the basis for treating "co-locate at essentially any SWRO desalination
plant's brine outfall" as a broadly repeatable site type across many
facilities worldwide, not a one-off opportunity limited to Perth or
Carlsbad specifically. Source (already referenced in this repo): [1]
in `docs/math/REAL_WORLD_DATA.md`'s references list.

## Site type 5 — Municipal WWTP effluent into saline receiving water (identified, NOT independently verified — honest gap)

A coastal municipal wastewater treatment plant discharging treated
effluent into an estuary or harbor is a structurally plausible fourth
site *type* (treated effluent is a real, continuously-flowing
low-salinity stream analogous to `C_TREATED_WW` in
`simulation/constants.py`, and many coastal cities operate exactly this
kind of outfall). **This research pass did not find a specific real
plant's effluent salinity/flow figures to cite**, and rather than
fabricate a plausible-sounding number, this is recorded as an open
research gap: a real round-4 task would be to identify one specific
coastal WWTP with public NPDES/discharge-permit flow and salinity data
and confirm whether its effluent quality/flow profile is compatible
with `simulation/constants.py`'s `C_TREATED_WW` anchor before treating
it as a real candidate site rather than a plausible site *type*.

## What this means for siting priority

Sites 1 and 2 (Perth, Carlsbad) are the strongest real candidates:
large, continuous, well-characterized brine flows with public
environmental-monitoring data already available (useful for both
`docs/ECONOMICS.md` capacity-factor assumptions and
`docs/ENVIRONMENTAL_IMPACT.md` permitting precedent). Site 3
(Statkraft Tofte) is the cautionary real-world benchmark this whole
roadmap is implicitly trying to beat. Site 4 is the general
repeatable-class argument. Site 5 is honestly flagged as unverified
rather than invented.
