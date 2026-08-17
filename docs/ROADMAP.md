# CHORUS-SGH-1 Harness Roadmap

## Current state (honest baseline, 2026-08-17)

This repo is a physics-simulation + open-hardware R&D harness. The math
(PRO cycle, parasitics, pi_groups, acoustic/vortex vision stack) is real
and covered by tests (11/11 passing at time of writing). Nothing here has
been validated against physical hardware yet:

- `daq/serial_sensors.py` never actually opens a serial port. It accepts
  `--port` but silently discards it and always returns simulated rows
  from `daq.logger.read_sensors_sim`, tagged only with `serial_port` for
  cosmetic traceability. There is no protocol, no framing, no checksum,
  no timeout/reconnect handling — it is a passthrough stub, not a driver.
- `simulation/constants.py` hard-codes `L_p`-class membrane constants and
  a `tau_spin_from_rpm` linear torque model from literature anchors
  (`docs/math/REAL_WORLD_DATA.md`), explicitly marked "calibrate T1c" —
  i.e. placeholders pending real bench data.
- `hardware/openscad/*.scad` (23 parts) are audited today only for
  textual structure (modules, includes, parameter dumps) in
  `scripts/audit_openscad.py`. There is no manifold/watertightness or
  dimensional-tolerance check — geometry could be self-intersecting or
  non-printable and the audit would not catch it.
- `scripts/run_test_protocol.py` runs T0 -> T1 -> T1b -> T1c end to end
  with no checkpointing. If phase 3 of 4 fails (bench disconnect, bad
  fixture, power loss), the whole protocol must restart from T0.
- `daq/logger.py` writes CSV only. There is no live view of a running
  bench session; you can only inspect after the run completes.
- The BOM (`hardware/bom/SGH1_BOM.csv`) specifies `DAQ-001: Raspberry Pi
  4 + ADC HAT (Adafruit/MCP3008)` plus `SENS-001..003` pressure/
  conductivity/flow sensors and `AEH-003` an ultrasonic transducer. The
  realistic bench topology is: an MCU (or the Pi itself acting as a
  serial-attached sensor node) samples the MCP3008 over SPI locally and
  streams framed ASCII telemetry over a USB-CDC serial link to whatever
  machine runs this harness. That is the protocol this roadmap targets.

## Roadmap

### 1. Real DAQ serial ingestion protocol (this PR)
Implement a genuine, protocol-correct ASCII/checksummed serial link in
`daq/serial_sensors.py`, backed by a testable parser in `daq/protocol.py`:
- NMEA-style framed sentences: `$SGH1,<seq>,<millis>,<11 sensor fields>*<XOR checksum hex>\r\n`
- Real `pyserial` port open with configurable baud, connect timeout, and
  per-read timeout.
- Reconnect-with-backoff on port loss (device unplugged mid-run).
- Checksum validation; malformed/short/garbled frames are dropped and
  counted, not silently accepted.
- Explicit, loud fallback: only if the port cannot be opened, or no
  valid frame arrives within the configured timeout, do we fall back to
  `read_sensors_sim`, and we print/log a `RuntimeWarning`-level message
  every time a fallback happens (not once, not silently).
- Unit-testable without hardware: feed synthetic byte streams (good
  frames, corrupted frames, partial frames split across reads) into the
  parser.

### 2. Constant-calibration pipeline (this PR)
`scripts/calibrate_constants.py`: fits membrane permeability `L_p`
(from feed/draw pressure differential vs. flow) and the RPM->torque
coefficient (from `omega_rpm` vs. `P_spin_motor_W`) from bench CSVs
using ordinary least squares (`numpy.polyfit` / `scipy.optimize`).
Validated in this PR against the *simulated* CSVs already in
`data/bench/` (`T1_baseline_*.csv`, `smoke_test.csv`) as a stand-in —
those are clearly synthetic/simulated data, not real bench
measurements. Real T1 calibration still requires physical bench access;
this pipeline is what will consume that data once it exists.

### 3. CAD/STL geometry validation (this PR, partial)
Extend `scripts/audit_openscad.py` with a manifold/watertightness check
per part: shell out to the `openscad` CLI (`--export-format=binstl`) to
render each part to STL, then check basic mesh sanity (triangle count >
0, no degenerate triangles, closed-ness via a numpy-stl / manual
edge-pairing check if `numpy-stl` isn't available). If the `openscad`
binary is not present on the machine (it is not, in this dev
environment — confirmed via `which openscad`), the audit records that
gap explicitly per-part (`"geometry_check": "skipped: openscad not found"`)
rather than pretending to pass.

### 4. Resumable T0->T1->T2 protocol runner (this PR)
`scripts/run_test_protocol.py` gains a checkpoint file
(`<out_dir>/checkpoint.json`) recording which phases/sub-runs completed.
`--resume` re-enters at the first incomplete phase instead of
restarting. A crash or hardware disconnect mid-protocol no longer loses
completed phases.

### 5. Live dashboard mode (this PR, lightweight)
A small stdlib-only local HTTP server (`daq/dashboard.py`) that tails
the active bench CSV and serves a polling HTML page with the latest
readings and a rolling sparkline. No new heavy dependency (Flask is not
in `pyproject.toml`; a `http.server`-based JSON+HTML endpoint keeps the
dependency footprint at zero).

### 6. Vision-stack sensor hookup (deferred, tracked here)
`docs/UDT_PHYSICS.md` / `docs/VOH_PHYSICS.md` describe the acoustic
vortex-vision math (AOR/UDT/VOH). Wiring `AEH-003` (28kHz ultrasonic
transducer) and the PVDF piezo array (`AEH-002`) into the same serial
protocol as a second sentence type (`$SGHV,...`) is the next logical
step once T1c bench torque calibration is validated, because the vision
stack's `eta_tink` coupling coefficient depends on real spin data. Not
implemented in this PR — flagged as next milestone.

### 7. Milestone tracking
| Milestone | Status |
|---|---|
| M0 — Simulation math validated (11/11 tests) | Done (pre-existing) |
| M1 — Real serial protocol + explicit fallback | This PR |
| M2 — Constant-calibration pipeline (sim-data validated) | This PR |
| M3 — Geometry manifold checks in CAD audit | This PR (gap documented: no `openscad` binary here) |
| M4 — Resumable protocol runner | This PR |
| M5 — Live dashboard | This PR |
| M6 — Real T1 bench data collected, constants refit from hardware | Not started — requires physical bench access |
| M7 — Vision-stack sensor hookup (AEH-003, AEH-002) | Not started |
| M8 — Full T0->T2 hardware-in-the-loop run | Not started |

Hardware-in-the-loop validation (M6-M8) cannot be completed in this
environment: there is no physical DAQ, no bench, no CHORUS-SGH-1 unit
attached. Everything above that claims "real" is real *code* — a
correct, testable implementation of the ingestion/calibration/audit
logic — not a claim that it has been run against a physical skid.
