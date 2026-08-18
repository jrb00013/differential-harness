# CHORUS-SGH-1 Environmental Impact — Brine Discharge Considerations

Any system that touches the water chemistry of an existing brine
outfall or estuary (see `docs/CANDIDATE_SITES.md`) needs this framing
to be credible to a real site owner or regulator. This is a one-page,
honest assessment — not an environmental impact statement, and not a
substitute for one. It cites real, publicly documented ecological
concerns and regulatory precedent for brine discharge, and states
plainly where CHORUS-SGH-1's own environmental profile is an untested
hypothesis rather than a demonstrated finding.

## Documented ecological concerns with brine discharge (general, desalination industry)

- **Hypersalinity and density stratification.** Desalination brine is
  denser than the receiving water, so it sinks and creeps along the
  seabed as a distinct plume rather than mixing quickly — modeling
  work on real plants shows plumes can be traced tens of kilometers
  beyond the immediate mixing zone under some conditions.
- **Benthic ecosystem stress.** Documented effects on seabed organisms
  exposed to elevated salinity and reduced dissolved oxygen range from
  impaired activity and morphological deformation to measurable shifts
  in community composition — reported across bacteria, seagrasses,
  polychaete worms, and corals in peer-reviewed studies of real
  desalination outfalls.
- **Chemical additives.** Antiscalants (commonly polyphosphonates) and
  coagulants (often ferric-based) used upstream in the desalination
  process accumulate in brine and can alter sediment porewater
  chemistry and redox conditions near the outfall — a separate concern
  from salinity/oxygen stress alone.
- **Real, measured example**: the Carlsbad Desalination Plant
  (`docs/CANDIDATE_SITES.md` site 2) has documented plume salinity
  exceeding its permitted level and extending farther offshore than
  authorized under the California Ocean Plan — i.e. this is not a
  theoretical risk category, it is an observed compliance issue at an
  operating, real-world plant.

## Regulatory precedent

- **California's Desalination Amendment** to the statewide Ocean Plan
  (Cal. Code Regs. tit. 23, §3009; adopted via State Water Resources
  Control Board Resolution 2015-0033, effective 2015) is the first
  statewide regulatory framework directly limiting brine discharge
  salinity, via a narrative receiving-water limit (with an optional
  facility-specific numeric limit), plus siting and monitoring
  requirements. This is real, citable precedent for what a regulator
  would expect from any brine-touching system, CHORUS-SGH-1 included,
  if sited in a comparable jurisdiction.
- **Western Australia's environmental review process** for the Perth
  Seawater Desalination Plant expansions (`docs/CANDIDATE_SITES.md`
  site 1) includes public referral documentation covering diffuser
  design, dilution-factor licensing (45× by 50 m), and brine
  dispersion modeling — a real template for what site-specific
  environmental documentation for a co-located skid would need to
  address.
- **No PRO/RED-specific environmental permitting precedent was
  found.** This research pass looked for prior environmental review of
  real salinity-gradient-power pilots (Statkraft Tofte, REDstack
  Afsluitdijk) and found operational/fouling documentation but no
  public permitting record. This is an honest, stated gap: CHORUS-SGH-1
  would likely be the first system in its class to go through this
  specific regulatory process at most candidate sites, not one
  following an established playbook.

## CHORUS-SGH-1's own dilution-based hypothesis (untested — stated as such)

CHORUS-SGH-1's PRO design mixes existing brine with a lower-salinity
draw stream before any resulting flow is returned to the environment
(`simulation/pro_cycle.py`). It is a logically sound inference from
mass balance that **this could reduce net discharge salinity/impact
relative to discharging the brine undiluted** — the system is, by
construction, doing some of the same dilution work a desalination
plant's own outfall diffuser does, except extracting usable energy
from the mixing step instead of dissipating it for free.

**This research pass did not find a published study directly
confirming reduced ecological impact from a PRO-style pre-discharge
dilution step**, and this document does not claim one exists. It is
recorded here as a testable hypothesis worth real environmental
monitoring at a pilot site, not an established environmental benefit —
treating it otherwise would be exactly the kind of unearned claim this
repo's engineering docs have deliberately avoided elsewhere (see the
honest-gap framing in `docs/ROADMAP.md`, `docs/ECONOMICS.md`).

## What a real site deployment would need (not built here)

1. Site-specific brine dispersion/plume modeling (as Perth's referral
   documents and the Carlsbad MDPI study both did) before any
   discharge-affecting pilot could be sited.
2. Baseline and post-installation benthic ecological monitoring,
   following the general pattern of the peer-reviewed Carlsbad studies
   cited below.
3. A permitting strategy addressing the "no PRO-specific precedent"
   gap directly — likely by analogy to the desalination-plant
   permitting process at the co-located host site, since CHORUS-SGH-1
   would be modifying (diluting) an existing permitted discharge rather
   than creating a new one from scratch.

## Sources

- Impacts of Desalination Brine Discharge on Benthic Ecosystems, *ACS Environmental Science & Technology* — https://pubs.acs.org/doi/10.1021/acs.est.3c07748
- First large-scale ecological impact study of a desalination outfall, *Desalination* (ScienceDirect) — https://www.sciencedirect.com/science/article/abs/pii/S0043135418307012
- Impact of brine discharge on marine ecosystems: a review (ScienceDirect, 2025) — https://www.sciencedirect.com/science/article/pii/S2468584425001023
- Biological and Physical Effects of Brine Discharge from the Carlsbad Desalination Plant, *MDPI Water* (2019) — https://www.mdpi.com/2073-4441/11/2/208
- Cal. Code Regs. tit. 23 §3009, Desalination Amendment (Cornell LII) — https://www.law.cornell.edu/regulations/california/23-CCR-3009
- California Water Boards, Desalination Amendment fact sheet — https://www.waterboards.ca.gov/publications_forms/publications/factsheets/docs/desal_fs.pdf
- California Water Boards, Resolution 2015-0033 — https://www.waterboards.ca.gov/board_decisions/adopted_orders/resolutions/2015/rs2015_0033.pdf
- Western Australia EPA, PSDP2 Environmental Referral Document — https://www.epa.wa.gov.au/sites/default/files/Referral_Documentation/2.%20PSDP2_Environmental_Referral_Document_Part%20A.pdf
- ForwardOsmosisTech, "Is PRO economically feasible? Not according to Statkraft" — https://www.forwardosmosistech.com/statkraft-discontinues-investments-in-pressure-retarded-osmosis-2/
