# CHORUS-Skid SGH-1: Brine-Gradient Power, UDT/AOR/VOH Vision Stack, and Osmotic-Vortex Hydro

**Joseph Black** and **Connor White**  
*CHORUS Research — differential-harness*  
Full technical report · Draft v5 · June 2026

---

## Abstract

Coastal and inland desalination plants discharge hypersaline brine while treated effluent remains at near-fresh salinity. The resulting **salinity-gradient resource** is routinely dissipated as mixing entropy rather than converted to useful work. We present **CHORUS** (*Columnar Harvest of Osmotic, Rhizospheric, Orographic, and Solar flux*) as a multi-physics accounting framework for a 1 km² coastal parcel, **CHORUS-Skid SGH-1** as a bench-scale **pressure-retarded osmosis (PRO)** harness, and a three-layer **vision stack**: **UDT** (Universal Differential Tink), **AOR** (Acoustic-Osmotic Ram), and **VOH** (Vortex-Osmotic Hydro / Z-Hydro) targeting osmotic-vortex hydro at desal outfalls.

Using van't Hoff thermodynamics, Kim–Baker optimal hydraulic pressure, solution-diffusion transport, concentration-polarization film theory, and executable vision modules, we derive a consistent sizing pipeline (Δπ = 6.92 MPa, ΔP* = 34.6 bar, A_mem = 0.72 m²) and report experiments E1–E16. A **T0–T1c bench validation pipeline** (`bench_validation.py`, `run_test_protocol.py`) produces pass/fail artifacts from CSV. Column-scale Monte Carlo (N = 8000) yields median **22.76 MW/km²** (PV-dominated). Default L_p predicts **1.66 W** vs 10 W design target; L_p* ≈ 6.0×10⁻¹² m/(Pa·s) for bench closure.

**Keywords:** pressure-retarded osmosis; salinity-gradient power; UDT; AOR; VOH; Z-Hydro; osmotic-vortex hydro; bench validation

---

## Vision stack (UDT / AOR / VOH)

| Layer | Physics | Module |
|-------|---------|--------|
| **UDT** | Ray field + particle bytes → Tink kernel → k_m,eff | `differential_tink.py` |
| **AOR** | Resonant column + brine motor + ram pipe | `acoustic_osmotic_ram.py` |
| **VOH** | Spin + halocline + z-leg pressurized flux | `vortex_osmotic_hydro.py` |

Master index: [docs/VISION.md](../docs/VISION.md)

**Pitch:** Sound strips the membrane. Brine propels the loop. Spin and the z-pipe amplify. Fleet at outfalls scales to civilization impact.

---

## Bench validation (T0–T1c)

| Stage | Pass |
|-------|------|
| T0 | No leaks @ 3 bar; 15 min positive signal |
| T1 | P'' ±30% sim; P_net > 0 for 1 h |
| T1b | P_net(C) > P_net(B) > P_net(A) — UDT/AOR |
| T1c | P_net(ω) > P_net(0) — VOH spin |

```bash
python scripts/run_test_protocol.py --test T1
python -m simulation.bench_validation --csv data/bench/T1_*.csv
pytest tests/
```

---

## Reproduce PDF

```bash
./scripts/run_paper_pipeline.sh
# → papers/Black_2026_CHORUS_SGH1_PoC.pdf
```

---

*Correspondence: Joseph Black and Connor White, via differential-harness repository.*
