# SGH-1 Test Protocol

## T0 — Coupon / single plate

1. Leak test air @ 3 bar, 10 min.
2. Water flush both sides.
3. Establish feed 5 g/L, draw 80 g/L; record conductivity.
4. Ramp ΔP from 0 → 0.5 Δπ → 0.5 Δπ* over 30 min.
5. Log at 1 Hz (`daq/logger.py`).
6. Pass: no leaks; P_elec or hydraulic power > 0 steady 15 min.

## T1 — Full stack

1. Hydrotest draw side 1.25× ΔP* with water.
2. 1 h steady run; export CSV.
3. Compare `P_density` to simulation ±30%.

## T2 — Field sidestream

1. NDA + utility approval.
2. Tie-in to brine + effluent; same logging.

## Acoustic (AEH)

1. SPL meter at panel face; verify 80+ dB environment optional.
2. Measure harvest Voc into 1 MΩ load.
3. US on: compare flux / power vs off (Mode B).

## T1b — UDT / AOR (vision)

1. Same ΔP as T1; log 1 Hz minimum 60 min.
2. Run A: US off, incoherent driver off.
3. Run B: UDT phased rays on (see [UDT_PHYSICS.md](UDT_PHYSICS.md)).
4. Run C: full AOR — resonant column tuned to `f ≈ c/(4H)`.
5. Pass: `P_net(C) > P_net(B) > P_net(A)` OR document fouling-limited crossover.

## T1c — VOH / Z-Hydro (vision)

1. Compare flat stack (ω = 0) vs spinning drum at fixed ω (RPM logged).
2. Measure `P_spin_motor` separately.
3. Pass: `P_net(ω) > P_net(0)` after subtracting spin parasitic, same brine pair.

Vision index: [VISION.md](VISION.md)
