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
