# Implementation Plan — Roadmap Execution

Ordered, commit-sized steps for `feat/roadmap-implementation`. Each step
is meant to land as one working, tested commit.

1. **docs: add roadmap and implementation plan** (this commit) — no code.
2. **feat(daq): add framed ASCII serial protocol encoder/parser
   (`daq/protocol.py`)** — pure parsing/checksum logic, unit tested with
   synthetic byte streams (good frames, corrupted checksum, truncated
   frame, frame split across two reads, garbage prefix before a valid
   frame).
3. **feat(daq): real pyserial ingestion in `daq/serial_sensors.py`** —
   opens the configured `--port` for real, with connect timeout,
   per-read timeout, reconnect-with-backoff, checksum-validated frame
   decode via `daq/protocol.py`, and an explicit repeated
   `RuntimeWarning` + stderr message whenever it falls back to
   simulated data (missing port, open failure, or no valid frames within
   timeout). Never silently substitutes simulation.
4. **test(daq): serial protocol + fallback-path tests** — feed a fake
   `serial.Serial`-like object (in-memory) through `read_sensors_serial`
   to prove: good-frame decode, checksum-fail rejection + fallback
   warning, port-open-failure + fallback warning, reconnect-after-drop.
5. **feat(simulation): constant-calibration script
   (`scripts/calibrate_constants.py`)** — OLS fit of membrane
   permeability `L_p` from `P_feed - P_draw` vs. `Q_draw`, and RPM->torque
   slope from `omega_rpm` vs. `P_spin_motor_W / omega_rad_s`. Runs
   against the existing simulated CSVs in `data/bench/`, writes a JSON
   report clearly labeled `"data_provenance": "simulated"`.
6. **test(simulation): calibration fit tests** — synthetic CSV with a
   known-slope relationship, assert the fit recovers it within
   tolerance; assert the report is labeled simulated.
7. **feat(scripts): geometry manifold check in `audit_openscad.py`** —
   shell out to `openscad` CLI per part when available; otherwise record
   `"geometry_check": "skipped: openscad not found"` per part. Add a
   pure-python STL sanity checker (triangle count, degenerate-triangle
   detection) usable when an STL is produced.
8. **test(scripts): audit_openscad geometry-check gap/behavior test** —
   verify the audit records the explicit skip reason when `openscad` is
   absent, and (if present) that a hand-built valid/invalid STL is
   classified correctly by the pure-python checker.
9. **feat(scripts): checkpointing + `--resume` in
   `run_test_protocol.py`** — write `checkpoint.json` after each
   completed sub-run; `--resume` skips already-completed entries.
10. **test(scripts): checkpoint resume logic** — simulate a partial
    checkpoint file and assert the resume path only re-runs the missing
    phases (mock the subprocess calls).
11. **feat(daq): lightweight live dashboard (`daq/dashboard.py`)** —
    stdlib `http.server`-based JSON+HTML polling viewer over the active
    bench CSV; no new dependency.
12. **test(daq): dashboard data-endpoint test** — start the server on an
    ephemeral port against a fixture CSV, hit the JSON endpoint, assert
    shape.
13. **docs: update README with new scripts/usage + roadmap link** and
    final `docs/ROADMAP.md` status-table refresh reflecting what
    actually landed vs. deferred.

Constraints carried through every step: keep all 11 pre-existing tests
green; never claim real hardware was exercised; label all bench data
provenance explicitly (`simulated` vs. `real`) in any script output.
