# Implementation Plan — Round 2

Ordered, commit-sized steps for `feat/roadmap-round-2` (branched from
`feat/roadmap-implementation`, PR #1).

1. **docs: add round-2 roadmap and implementation plan** (this commit).
2. **feat(simulation): vision-stack signal processing
   (`simulation/vision_signal.py`)** — windowed RMS/envelope amplitude
   estimate, circular-statistics phase-coherence over a rolling window
   of `$SGHV` samples, and an `eta_tink` coupling-efficiency estimate
   bridging to `simulation.differential_tink`.
3. **test(simulation): vision_signal correctness tests** — synthetic
   sine-wave sample streams with known amplitude/phase; assert RMS and
   coherence estimates match analytically expected values within
   tolerance; assert a phase-incoherent stream yields low coherence.
4. **feat(daq): harden dashboard.py against concurrent/partial reads** —
   any bug fixes surfaced by the new tests in step 5 (e.g. read races,
   malformed-field handling) land here.
5. **test(daq): dashboard race/edge-case tests** — mid-append CSV read,
   concurrent GETs, window boundary cases, malformed numeric fields.
6. **feat(scripts): multi-run aggregate calibration with confidence
   intervals** — `fit_L_p_aggregate()` in `calibrate_constants.py` using
   `scipy.stats.t` for a 95% CI and an outlier flag.
7. **test(scripts): aggregate calibration tests** — synthetic multi-run
   fixture with a known outlier; assert the CI and outlier flag are
   correct.
8. **feat(scripts): protocol-history CLI (`scripts/protocol_history.py`)**
   — scans `data/bench/*/checkpoint.json` + `manifest.json` +
   `bench_validation.json`, renders a table, supports `--json` and
   `--test-id`.
9. **test(scripts): protocol_history tests** — synthetic checkpoint/
   manifest/validation fixtures in a tmp dir; assert table contents and
   JSON output shape.
10. **feat(scripts): STL winding-consistency + ASCII-STL rejection in
    `stl_check.py`** — directed-edge counting to detect inconsistent
    winding; explicit `solid` header sniff for ASCII STL rejection.
11. **test(scripts): STL winding/ASCII-rejection tests** — a
    consistently-wound closed mesh, a deliberately flipped-winding
    triangle, and an ASCII STL fixture.
12. **docs: update docs/ROADMAP_ROUND2.md status + README round-2
    section** reflecting what actually landed.

Constraints carried over from round 1: keep all pre-existing tests
green throughout; label all data provenance explicitly; document any
genuine hardware/toolchain blocker instead of skipping silently.
