# Round 4 Roadmap — Attacking the Cost Gap Directly

Round 3 (PR #3) built a real LCOE model and found CHORUS-SGH-1's best
case (~$2/kWh, lab-grade 25 W/m² density + optimistic costs) is still
~22-75x more expensive than solar/wind (~$0.03-0.09/kWh, Lazard LCOE+
June 2024). That finding was stated plainly and not softened. Round 4
does not retreat from it — it interrogates it: is there a plausible
combination of parameters that closes the gap, is there value the raw
$/kWh comparison misses, and does manufacturing scale help at all. The
answer is allowed to be "no, and here is why" — that is a legitimate,
valuable round-4 outcome, not a failure to find one.

## Round 4 scope

### R4.1 — Breakeven sensitivity analysis
Extend `scripts/lcoe_model.py` with root-finding solvers
(`solve_breakeven_power_density`, `solve_breakeven_membrane_cost`,
`solve_breakeven_membrane_life`) that answer, for a fixed target LCOE
(e.g. Lazard's solar/wind bounds): what single parameter value, holding
everything else fixed, would need to be true to reach that target? Each
solved value is then checked against a known physical/practical ceiling
(e.g. 60 W/m² lab hypersaline ceiling from
`docs/math/REAL_WORLD_DATA.md`, $0/m² membrane cost floor) so the
answer is reported as "plausible" or "requires exceeding a known
physical/practical limit," not left as a bare number.

### R4.2 — Value beyond raw $/kWh
Adds a real, cited avoided-transmission-and-distribution (T&D) credit
(~$0.02/kWh from utility avoided-cost studies) to `scripts/lcoe_model.py`
and `docs/ECONOMICS.md`, computed honestly as a *partial offset*
against the raw LCOE, not as a replacement number. Also documents —
narratively, without fabricating a number — the "avoided
already-flowing brine stream" argument (the concentration gradient is
otherwise wasted, zero marginal fuel cost) and is explicit that this
does not change the *capital-cost* side of the comparison at all, only
the "what's the fuel worth" framing.

### R4.3 — Manufacturing/volume learning-curve model
Adds a Wright's-law-style learning-curve projection
(`scripts/lcoe_model.py::learning_curve_cost`) grounded in real
per-technology learning rates found via research (solar PV ~20-24%,
aircraft/Wright's original study ~15%, general hardware range
~10-20%), applied to this repo's own BOM baseline cost at 10x/100x/1000x
cumulative unit volume, with an honest statement of which rate
assumption is used and why PRO/FO membrane-specific learning rates are
not available in the public literature.

### R4.4 — Real code + tests
All of the above lands as real, tested code (root-finding correctness
against known closed-form cases, learning-curve arithmetic against
hand-computed values, avoided-cost credit arithmetic) — no doc-only
claims without a script backing them.

## Milestone table (round 4)

| Milestone | Status |
|---|---|
| R4.1 — Breakeven sensitivity solvers | Done — `scripts/lcoe_model.py::breakeven_report` |
| R4.2 — Avoided-T&D value + honest co-benefit framing | Done — `co_benefit_adjusted_lcoe()` |
| R4.3 — Learning-curve volume-cost projection | Done — `volume_cost_projection()` |
| R4.4 — ECONOMICS.md rewrite with the honest bottom-line conclusion | Done |
| R4.5 — Real manufacturing-at-scale validation of the learning-curve assumption | Blocked — no manufacturing history exists for this hardware; same hard-limit class as every prior round |

## Round 4 bottom line (see `docs/ECONOMICS.md` for full detail)

No single lever (power density, membrane cost, or membrane replacement
life) closes the gap to solar/wind LCOE within any real physical or
practical ceiling. Manufacturing scale alone (up to 1000x cumulative
volume, at the most optimistic cited learning rate) does not close it
either. Only stacking two simultaneous, currently-unproven extremes —
lab-hypersaline power density AND 1000x manufacturing scale — reaches
order-of-magnitude parity with standalone battery storage (~$0.30/kWh),
still not solar/wind generation directly. The real, cited avoided-T&D
co-benefit credit (~$0.02/kWh) offsets under 1% of the raw LCOE at
CHORUS-SGH-1's actual cost scale. This is not "no plausible path
under any conditions," but it is a plainly stated "no realistic path
without simultaneously achieving two separate technical extremes
neither of which this repo's own hardware protocol has validated" —
round 4 does not manufacture optimism the model does not support.
