# Round 2 Roadmap — Post-PR#1 Audit

This picks up where `docs/ROADMAP.md` (round 1, see PR #1 /
`feat/roadmap-implementation`) left off. Round 1 shipped real protocol
plumbing, calibration, geometry-check code, checkpointing, a dashboard,
and vision-stack framing. This round audits what round 1 actually left
thin and does the next honest layer of work — not busywork, not
re-wrapping the same functions.

## Audit of round 1's gaps

- **`$SGHV` is protocol-only.** `daq/protocol.py` and
  `daq/serial_sensors.py` can frame, checksum, and multiplex vision-stack
  telemetry, but nothing downstream *interprets* `us_amplitude_mV`,
  `us_phase_deg`, `piezo_array_V` as a signal. There is no envelope
  detection, no phase-coherence estimate across samples, no coupling
  with the UDT/AOR/VOH math already in `simulation/differential_tink.py`
  / `simulation/vortex_osmotic_hydro.py`. This is the single biggest gap
  — round 1 explicitly called it "protocol-complete", not
  "signal-processing-complete".
- **`daq/dashboard.py` has only 3 tests**, all against a static fixture
  CSV. There is no test that the server handles a CSV actively being
  appended to mid-request (the real operating condition), no test of
  concurrent requests, and no coverage of the `window` truncation
  boundary or of a CSV with malformed/missing columns.
- **`scripts/calibrate_constants.py` fits from a single CSV (or a set of
  CSVs treated as one pooled sample) with no per-run breakdown,
  no confidence interval, and no way to see whether L_p is consistent
  run-to-run** (an operator running T1 three times has no way to know if
  the fits agree or one run was an outlier).
- **`checkpoint.json` is a private implementation detail of
  `run_test_protocol.py`.** There is no CLI to inspect run history across
  multiple `data/bench/<TEST>_<date>/` directories, so answering "which
  bench sessions have I actually completed, and what's their pass/fail
  status" means manually grepping JSON files.
- **`scripts/stl_check.py`'s watertightness check has known blind spots**:
  it does not detect self-intersecting (non-manifold-but-technically-
  edge-paired) geometry, does not check triangle winding
  consistency (a mesh can be edge-paired-closed yet have inconsistent
  normals — not truly manifold), and silently accepts ASCII-format STL
  as "too small" garbage rather than giving a clear "wrong format"
  error.

## Round 2 scope

### R2.1 — Vision-stack signal processing (real math, this PR)
Add `simulation/vision_signal.py`: turns a stream of `$SGHV` samples
into the quantities the UDT/AOR/VOH math actually consumes —
envelope/RMS amplitude estimation, phase-coherence (circular variance)
across a rolling window, and a coupling-efficiency estimate feeding
`simulation.differential_tink.sweep_eta_tink`. This is real signal
processing (windowed RMS, circular statistics for phase), not another
protocol pass-through, and is unit-tested against synthetic sine-wave
sample streams with known amplitude/phase so the math is verifiably
correct.

### R2.2 — Dashboard hardening (this PR)
Add tests for: CSV mutated mid-request (append-while-reading race),
concurrent GETs against the running server, `window` boundary behavior
(window larger than file, window=0), and a CSV with missing/malformed
numeric fields (falls back to the raw string rather than crashing).
Fix any bugs these surface.

### R2.3 — Multi-run aggregate calibration with confidence intervals (this PR)
Extend `scripts/calibrate_constants.py` with `fit_L_p_aggregate()`:
runs the existing per-CSV fit across N runs, reports mean, sample
standard deviation, and a t-distribution-based 95% confidence interval
(using `scipy.stats`, already a dependency) — and flags any run whose
fit is more than 2 standard deviations from the pooled mean as a
candidate outlier for operator review.

### R2.4 — Protocol-history CLI (this PR)
`scripts/protocol_history.py`: scans `data/bench/*/checkpoint.json` +
`manifest.json`, and prints a table of test id, completed steps,
pass/fail (from `bench_validation.json` if present), and timestamp.
Supports `--json` for machine-readable output and `--test-id` filtering.

### R2.5 — STL checker hardening (this PR)
Extend `scripts/stl_check.py`: detect inconsistent triangle winding
(an edge shared by two triangles traversed in the *same* direction
indicates inconsistent winding / a non-orientable patch, distinct from
an open edge), and detect and clearly reject ASCII-format STL input
(`solid ...` text header) with a specific error message instead of a
generic "too small" one.

## Milestone table (round 2)

| Milestone | Status |
|---|---|
| R2.1 — Vision-stack signal processing | Done — `simulation/vision_signal.py` |
| R2.2 — Dashboard race/edge-case hardening | Done — fixed a real `window=0` bug, added race/malformed-field tests |
| R2.3 — Multi-run calibration + confidence intervals | Done — `fit_L_p_aggregate()`, MAD-based outlier flagging |
| R2.4 — Protocol-history CLI | Done — `scripts/protocol_history.py` |
| R2.5 — STL winding-consistency + ASCII-STL rejection | Done — `scripts/stl_check.py` |
| R2.6 — Real vision-stack hardware validation of R2.1's algorithms | Blocked — no physical transducer/piezo attached (same hard limit as round 1's M7b) |

Same hard limits as round 1 apply and are not re-litigated here: no
physical DAQ, bench, or CHORUS-SGH-1 skid is attached in this
environment. Everything in R2.1-R2.5 is real, tested code; R2.6 is the
only round-2 item that hardware access would unblock.
