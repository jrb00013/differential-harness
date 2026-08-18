# Implementation Plan — Round 4

Ordered, commit-sized steps for `feat/roadmap-round-4` (branched from
`feat/roadmap-round-3`, PR #3).

1. **docs: add round-4 roadmap and implementation plan** (this commit).
2. **feat(scripts): breakeven sensitivity solvers in lcoe_model.py** —
   `solve_breakeven_power_density`, `solve_breakeven_membrane_cost`,
   `solve_breakeven_membrane_life`, each using bisection (LCOE is
   monotonic in each of these parameters, holding others fixed) and
   returning a plausibility verdict against known physical/practical
   ceilings.
3. **test: breakeven solver correctness** — verify each solver recovers
   the parameter value that `compute_lcoe` itself reports for a
   round-tripped target, and that an unreachable target (e.g. $0.01/kWh)
   is correctly reported as implausible rather than a false "solution."
4. **feat(scripts): learning-curve volume-cost model** —
   `learning_curve_cost()` (Wright's law) and
   `volume_cost_projection()` applied to the BOP+membrane cost baseline
   at 10x/100x/1000x cumulative volume, with multiple cited learning-rate
   scenarios (conservative/typical/solar-analog).
5. **test: learning-curve arithmetic** — hand-computed expected cost at
   a known doubling count for a known learning rate.
6. **feat(scripts): avoided-T&D credit + co-benefit-adjusted LCOE** —
   a real, cited $/kWh credit applied as a partial offset, reported
   alongside (never replacing) the raw LCOE.
7. **test: avoided-cost credit arithmetic and reporting.**
8. **docs: rewrite docs/ECONOMICS.md's "path to competitiveness"
   section** with the round-4 breakeven/learning-curve/co-benefit
   results and the honest bottom-line conclusion; update
   docs/ROADMAP_ROUND4.md status and README.

Constraints carried over from rounds 1-3: keep all pre-existing tests
green throughout; every parameter or rate used must be either derived
from this repo's own simulation/BOM or cited from a real public source;
state plainly if the honest answer is "no plausible path" rather than
manufacturing an optimistic framing the model does not support.
