# Implementation Plan — Round 3

Ordered, commit-sized steps for `feat/roadmap-round-3` (branched from
`feat/roadmap-round-2`, PR #2).

1. **docs: add round-3 roadmap and implementation plan** (this
   commit).
2. **feat(scripts): real LCOE model** (`scripts/lcoe_model.py`) grounded
   in `hardware/bom/SGH1_BOM.csv` and `docs/math/REAL_WORLD_DATA.md`
   cost anchors plus the existing PRO/parasitics simulation; tested
   against hand-computed CRF values and capex-composition arithmetic.
3. **docs: ECONOMICS.md** — the full sensitivity sweep, a real
   comparison against Lazard's LCOE+ solar/wind/storage benchmarks
   (fetched live via WebSearch, cited), and an honest statement of
   non-competitiveness plus what would actually move the number.
4. **docs: CANDIDATE_SITES.md** — real public site data (Perth PSDP,
   Carlsbad, Statkraft Tofte, general SWRO-brine class), fetched live
   via WebSearch and cited; one site type (municipal WWTP) explicitly
   flagged as an identified-but-unverified gap rather than filled in.
5. **docs: ENVIRONMENTAL_IMPACT.md** — documented ecological concerns
   and real regulatory precedent for brine discharge, fetched live via
   WebSearch and cited; explicit statement that CHORUS-SGH-1's own
   dilution-benefit hypothesis is untested.
6. **docs+feat: FOULING_TEST_PROTOCOL.md and
   `fit_L_p_time_series()`** — a T1f fouling-test phase citing the
   Statkraft Tofte fouling-driven failure as motivating precedent, with
   a real code implementation (chronological L_p segment fitting) for
   its flux-decline metric.
7. **test: fit_L_p_time_series coverage** — synthetic
   declining-flow and stable-flow fixtures, insufficient-data and
   chronological-ordering checks.
8. **docs: this file + docs/ROADMAP_ROUND3.md status refresh, README
   round-3 section** reflecting what actually landed.

Constraints carried over from rounds 1-2: keep all pre-existing tests
green throughout; every public-data claim in a docs file must carry a
real, checked URL in a Sources section; never fabricate bench data,
site data, or environmental/economic claims as established when they
are this repo's own reasoned synthesis instead.
