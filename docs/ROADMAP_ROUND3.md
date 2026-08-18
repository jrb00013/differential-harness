# Round 3 Roadmap — Economics, Siting, Environmental, and Fouling

Round 1 (PR #1) built real DAQ/protocol/calibration/geometry-audit
infrastructure. Round 2 (PR #2) added vision-stack signal processing,
dashboard hardening, multi-run calibration statistics, protocol
history, and STL winding checks. Both rounds were entirely internal —
simulation math, code correctness, test coverage. Round 3 turns
outward: is this technology honestly worth building, where would it
actually go, what would it do to its surroundings, and what's the
single biggest real-world failure mode (fouling) this repo has not yet
engaged with at all.

## Audit: what was missing going into round 3

- **No economics.** Nothing in this repo computed a $/kWh number or
  compared CHORUS-SGH-1 against any real energy-cost benchmark. The
  existing `docs/math/REAL_WORLD_DATA.md` had LCOE *anchors* (a
  literature range) but no working cost model tying them to this
  repo's own BOM and simulation.
- **No siting.** "Co-locate at a desalination plant" was asserted in
  passing in various docs but never grounded in a real plant's real
  flow/salinity numbers.
- **No environmental framing.** A system that touches brine discharge
  chemistry has an environmental story whether or not this repo writes
  it down; leaving it unwritten is itself a choice, and not a good one
  for anything meant to be taken seriously by a site owner or
  regulator.
- **No fouling protocol.** The single most consequential real-world PRO
  failure (Statkraft Tofte, `docs/CANDIDATE_SITES.md` site 3) partly
  came down to fouling, and this repo's entire T0-T2 test protocol
  (`docs/SGH1_TEST_PROTOCOL.md`) only ever specifies clean-water bench
  runs. `data/bench/*.csv` contains zero fouling-relevant data and
  `scripts/calibrate_constants.py` (rounds 1-2) had no way to detect a
  permeability decline over time even if such data existed.

## Round 3 scope (all landed in this PR)

### R3.1 — Real LCOE model
`scripts/lcoe_model.py`: computes $/kWh from the bench BOM's own cost
estimate line (`EST-001`), membrane $/m² anchors, a standard capital
recovery factor, and the existing PRO/parasitics physics simulation —
not a bare literature quote. Full optimistic/conservative x lab/
practical/Statkraft-floor sensitivity sweep.

### R3.2 — Honest economics writeup
`docs/ECONOMICS.md`: states plainly, with real numbers, that
CHORUS-SGH-1 is not cost-competitive with solar/wind/storage at any
power density this repo's simulation can substantiate (best case
~$2/kWh vs. Lazard's ~$0.03-0.09/kWh solar/wind range), and reframes
what *is* honestly true: power density is the whole economic lever,
BOP cost dominates at small scale, and this only makes sense as a
niche waste-stream co-location technology.

### R3.3 — Real candidate sites
`docs/CANDIDATE_SITES.md`: 5 site types with real public data (Perth
Seawater Desalination Plant, Carlsbad Desalination Plant, the
Statkraft Tofte pilot itself as the cautionary real-world benchmark,
the general WaterReuse SWRO-brine class, and a municipal-WWTP class
explicitly flagged as an unverified research gap rather than invented).

### R3.4 — Environmental impact framing
`docs/ENVIRONMENTAL_IMPACT.md`: documented ecological concerns with
brine discharge, real regulatory precedent (California's Desalination
Amendment, Perth's environmental referral process), and an explicit,
honest statement that CHORUS-SGH-1's own dilution-reduces-impact
hypothesis is untested.

### R3.5 — Fouling test protocol + code
`docs/FOULING_TEST_PROTOCOL.md` (a T1f phase extending
`docs/SGH1_TEST_PROTOCOL.md`) plus `fit_L_p_time_series()` in
`scripts/calibrate_constants.py`: splits one bench run into
chronological segments, re-fits L_p per segment, and reports percent
permeability decline — the concrete metric the protocol's flux-decline
gate needs, tested against synthetic declining- and stable-flow
fixtures.

## Milestone table (round 3)

| Milestone | Status |
|---|---|
| R3.1 — Real LCOE model | Done — `scripts/lcoe_model.py` |
| R3.2 — Honest economics writeup | Done — `docs/ECONOMICS.md` |
| R3.3 — Real candidate sites | Done — `docs/CANDIDATE_SITES.md` (4 verified, 1 explicitly flagged as unverified) |
| R3.4 — Environmental impact framing | Done — `docs/ENVIRONMENTAL_IMPACT.md` |
| R3.5 — Fouling test protocol + code | Done — `docs/FOULING_TEST_PROTOCOL.md`, `fit_L_p_time_series()` |
| R3.6 — Real fouling/economic/environmental validation at an actual site | Blocked — requires physical bench access and a real site relationship, same hard-limit class as rounds 1-2's M6/M7b/M8 |

R3.6 is the honest carry-forward: every document and script above is
real analysis grounded in public data and this repo's own simulation,
but none of it has been validated against an actual CHORUS-SGH-1 unit
at an actual site. That is not a gap this round could have closed —
it requires the same physical hardware/site access every prior round's
hard limits have already named.
