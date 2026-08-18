# SGH-1 Fouling Test Protocol (T1f)

Extends `docs/SGH1_TEST_PROTOCOL.md`'s T0/T1/T1b/T1c/T2 sequence with a
dedicated fouling-resistance phase, **T1f**, run after T1 (clean-water
baseline) and before any T2 field sidestream commitment.

## Why this exists — the Statkraft Tofte precedent

This is not a hypothetical concern added for completeness. The
Statkraft Tofte PRO pilot (Hurum, Norway, 2009-2014;
`docs/CANDIDATE_SITES.md` site 3) is the largest real-world PRO test to
date, and it never reached economic power density partly because of
biofouling and scaling from real river/seawater impurities — REDstack's
own multistage RED pilot autopsy after 30 days of natural water found
"mostly organic fouling at the membrane surface and spacers." A T0-T2
protocol validated only on clean bench water (which `data/bench/*.csv`
in this repo currently is — see `docs/ROADMAP.md` M6) would not have
caught the failure mode that historically killed the most comparable
real pilot. T1f exists specifically to close that gap before any real
site commitment (T2).

## Fouling mechanisms this protocol targets

1. **Organic fouling** — dissolved/colloidal organic matter (humic
   substances, proteins, polysaccharides) adsorbing to the membrane
   and support-layer pores; documented in the literature as
   particularly severe in PRO mode specifically, because flow is driven
   through the support layer in the direction that concentrates
   foulant against it.
2. **Biofouling** — microbial biofilm growth on the membrane surface,
   accelerated in real (non-sterile) feed and draw streams.
3. **Inorganic scaling** — calcium sulfate/carbonate precipitation
   where local concentration at the membrane surface (concentration
   polarization, `simulation/membrane_transport.py`) exceeds solubility.
4. **Colloidal fouling** — fine particulates (silt, clay) depositing on
   the membrane surface, distinct from dissolved organic fouling.

## T1f procedure

### T1f.1 — Synthetic foulant baseline (bench, no real hardware access required to *design* this)

Following the standard model-foulant recipes used across FO/PRO fouling
literature (no single codified ASTM-style standard exists for PRO
specifically — this protocol adapts documented research-literature
practice, stated honestly rather than presented as an established
standard):

| Foulant class | Recipe | Represents |
|---|---|---|
| Organic (alginate) | ~200 ppm sodium alginate + 1.5 mM CaCl₂ | Polysaccharide/organic fouling, calcium-alginate gel layer |
| Organic (protein) | ~1,000 ppm bovine serum albumin (BSA) | Protein fouling |
| Colloidal | Kaolin or silica suspension | Particulate/colloidal fouling |
| Scaling | CaCl₂ + Na₂SO₄ at supersaturating concentration for the draw-side salinity | Calcium sulfate/carbonate scaling |

Run each foulant class as an independent T1f sub-run, feed-side only
(draw side remains clean brine, matching how real deployments would see
foulant concentrated on the feed/dilute side).

### T1f.2 — Flux-decline measurement protocol

1. Run T1 baseline (clean feed) for the first 25% of the run (steady
   window, matching `simulation.bench_validation`'s
   `STEADY_WINDOW_FRAC`).
2. Switch feed to the foulant solution; continue logging at 1 Hz
   (`daq/logger.py`) for a minimum of 4 hours (long enough to resolve a
   flux-decline curve, short enough to be a practical bench test).
3. Use `scripts/calibrate_constants.py`'s new `fit_L_p_time_series()`
   (added in this round) to fit `L_p` in chronological sub-windows
   across the run and compute **percent L_p decline from the clean
   baseline window to the final fouled window** — this is the
   headline fouling-resistance metric.
4. Pass/fail gate (proposed, pending real calibration data): **L_p
   decline < 20% over 4 hours** is treated as an acceptable
   fouling-resistance result for continuing to T1f.3; a larger decline
   flags the membrane/geometry combination as high fouling risk before
   committing further bench time.

### T1f.3 — Cleaning-in-place (CIP) recovery test

1. After the T1f.2 fouled run, flush with a CIP solution appropriate to
   the foulant class (e.g. citric acid rinse for scaling, alkaline/
   detergent rinse for organic/biofouling — standard RO/FO CIP
   practice).
2. Re-run a clean-feed steady window and re-fit `L_p`.
3. **Recovery ratio = L_p(post-CIP) / L_p(pre-fouling baseline)**.
   A recovery ratio near 1.0 indicates the fouling was largely
   reversible (favorable for the membrane-replacement-interval
   assumption in `docs/ECONOMICS.md`); a recovery ratio well below 1.0
   indicates irreversible fouling accumulation, which would shorten the
   real membrane life below the 5-7 year RO/FO industry analog
   currently assumed there.

### T1f.4 — Reporting

Each T1f run's `bench_validation.json` / a new `fouling_report.json`
(from `fit_L_p_time_series()`) should record: foulant class, L_p decline
%, recovery ratio, and total run duration — feeding directly into
`docs/ECONOMICS.md`'s membrane-replacement-interval and capacity-factor
assumptions once real T1f data exists.

## Honest hard limits

- **This protocol has not been run against real hardware or real
  foulant solutions.** No physical bench exists in this environment
  (same limit as `docs/ROADMAP.md` M6). This document specifies a
  rigorous, literature-grounded methodology and the exact code
  (`fit_L_p_time_series()`) needed to analyze the resulting data — it
  does not, and cannot, claim any fouling-resistance result for
  CHORUS-SGH-1's actual membrane/geometry combination.
- **No PRO-specific standard foulant recipe or pass/fail threshold
  exists in the public literature** to adopt wholesale — the recipes
  and the 20%/4hr threshold above are this protocol's own reasoned
  synthesis from adjacent RO/FO fouling literature, explicitly flagged
  as such, not a citation of an established PRO fouling standard.
- **Biofouling specifically cannot be meaningfully bench-tested with
  synthetic foulant alone** — real biofouling requires real microbial
  populations from real feed water, which by definition requires a
  real site (T2), not a clean bench. T1f's synthetic-foulant runs are a
  necessary but not sufficient precursor to a real biofouling
  assessment at an actual candidate site.

## Sources

- Fouling fractionation in RED with natural feed waters, *Journal of
  Membrane Science* (ScienceDirect) — https://www.sciencedirect.com/science/article/pii/S0011916421003489
- Influences of Combined Organic Fouling and Inorganic Scaling on FO
  Flux (PMC) — https://pmc.ncbi.nlm.nih.gov/articles/PMC7345687/
- Accelerated testing for fouling of microfiltration membranes using
  model foulants (ScienceDirect) — https://www.sciencedirect.com/science/article/abs/pii/S0011916414000320
- ForwardOsmosisTech, "Is PRO economically feasible? Not according to
  Statkraft" — https://www.forwardosmosistech.com/statkraft-discontinues-investments-in-pressure-retarded-osmosis-2/
