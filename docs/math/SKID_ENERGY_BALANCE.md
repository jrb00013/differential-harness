# CHORUS-Skid SGH-1 — Steady-State Energy Balance

## 1. Production terms

| Term | Symbol | Typical (model) | Notes |
|------|--------|-----------------|-------|
| PRO equivalent | $P_\mathrm{PRO}$ | 1.7 W | `pro_cycle.py`, default $L_p$ |
| AEH harvest (Mode A) | $P_\mathrm{AEH}$ | 0.1–5 mW | 96 dB, $\eta=2\%$, 0.5 m² panel |
| Ultrasonic net (Mode B) | $P_\mathrm{US,net}$ | TBD | $P(g) - P_\mathrm{US} - P_0$ |

## 2. Parasitic loads (not yet in `pro_cycle.py`)

| Load | Estimate | Action |
|------|----------|--------|
| Feed pump | $P_p \approx Q\,\Delta P_p/\eta_p$ | Add to `simulation/parasitics.py` |
| Draw circulation | Low if gravity-fed | P&ID dependent |
| DAQ + control | < 2 W | `daq/logger.py` budget |
| US driver @ 28 kHz | 1.5–2 W/m² × $A$ | Subtracted in `ultrasonic_cp_gain.py` |

## 3. Net skid power (definition)

$$\boxed{P_\mathrm{net} = P_\mathrm{PRO} + P_\mathrm{AEH} + P_\mathrm{US,net} - P_\mathrm{pump} - P_\mathrm{aux}.}$$

**PoC honesty:** Published 10 W is a **design target** and area scale law, not a validated bench result until T1 completes.

## 4. Column context (1 km²)

From `exports/chorus_results.json` Monte Carlo ($N=8000$):

$$P_\mathrm{column,median} = 22.76\ \mathrm{MW}, \quad P_{10}=19.63,\quad P_{90}=26.46\ \mathrm{MW}.$$

Layer medians (notebook §VII): PV–hydro dominates; blue energy $\sim 0.26$ MW on estuary interface area assumptions.

## 4. Conservation check

$$\sum_k P_k \leq \sum_j \dot E_{j,\mathrm{in}} - \dot S T$$

No layer claims over-unity; TSC routes charge between high-impedance harvesters (see `CHORUS_MATH_PLAN.md` §5).
