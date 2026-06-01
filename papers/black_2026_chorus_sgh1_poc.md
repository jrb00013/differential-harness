# CHORUS-Skid SGH-1: A Proof-of-Concept Framework for Pressure-Retarded Osmosis on Anthropogenic Brine Gradients with Acoustic Harvest and Column-Scale Energy Accounting

**Joseph Black**  
*CHORUS Research — differential-harness*  
Draft · June 2026 · Proof of concept

---

## Abstract

Coastal and inland desalination plants discharge hypersaline brine while treated effluent remains at near-fresh salinity. The resulting **salinity-gradient resource** is routinely dissipated as mixing entropy rather than converted to useful work. We present **CHORUS** (*Columnar Harvest of Osmotic, Rhizospheric, Orographic, and Solar flux*) as a multi-physics accounting framework for a 1 km² coastal parcel, and **CHORUS-Skid SGH-1** as a bench-scale **pressure-retarded osmosis (PRO)** harness that targets 10 W electrical-equivalent output from anthropogenic brine (1400 mol/m³) against treated wastewater (5 mol/m³). Using van't Hoff thermodynamics, Kim–Baker optimal hydraulic pressure, solution-diffusion water transport, and concentration-polarization film theory, we derive a consistent sizing pipeline (Δπ = 6.92 MPa, ΔP* = 34.6 bar, A_mem = 0.72 m²) and report dimensionless groups Π₁–Π₅ from executable simulation. Column-scale Monte Carlo integration (N = 8000) yields a median harvest of **22.76 MW/km²** (P10–P90: 19.6–26.5 MW), dominated by evaporatively coupled photovoltaics rather than osmotic interfaces. We explicitly separate **defensible near-term claims** (PRO + acoustic energy harvest + ultrasonic CP assist) from **exploratory coupling** (Telluric Storm Conductance routing, global atmospheric circuit, soil–microbial fuel cells). Default membrane permeability predicts **1.66 W** steady-state output versus a 10 W design target; inverse sizing gives L_p* ≈ 6.0×10⁻¹² m/(Pa·s) for bench validation. This paper accompanies open-source notebooks, hardware CAD, and test protocols in the *differential-harness* repository.

**Keywords:** pressure-retarded osmosis; salinity-gradient power; blue energy; concentration polarization; acoustic energy harvest; coastal energy systems

---

## 1. Introduction

### 1.1 Motivation

Reverse-osmosis desalination separates water from seawater or brackish feed, producing a low-salinity permeate and a **reject brine** whose salinity often exceeds 7–8 wt% NaCl. Effluent from advanced wastewater treatment, by contrast, remains at single-digit mol/m³ salinity. The Gibbs free energy of mixing between these streams—if converted reversibly—represents a **dispatchable osmotic resource** co-located with existing hydraulic infrastructure [1].

Pressure-retarded osmosis (PRO) extracts work by allowing water to permeate from a low-salinity feed into a pressurized draw compartment; hydraulic energy is recovered via turbine or pressure exchanger [2]. Estuary reverse electrodialysis (RED) has achieved ~15 W/m² electrical power density at sea/river interfaces [1]; **sidestream PRO** on brine/effluent pairs offers higher osmotic driving force (Δπ) but demands robust fouling control and concentration-polarization (CP) management.

### 1.2 Contributions

This proof-of-concept study contributes:

1. A **unified mathematical blueprint** (Layers A–F) for osmotic, moist-electric, rhizospheric, atmospheric, and column-coupled harvest, with an explicit no-over-unity postulate.
2. **Executable proof** in SymPy/NumPy/SciPy (`CHORUS_physics_proof.ipynb`) exporting reproducible JSON results.
3. **SGH-1 hardware specification**: 12-plate PRO stack, OpenSCAD CAD, BOM, P&ID, and bench test protocol (T0/T1/T2).
4. **AEH-1 acoustic module** with Mode A (harvest) and Mode B (ultrasonic CP reduction) models.
5. **Honest hierarchy** of power densities: PV–hydro ≫ blue energy ≫ MEG/SMFC/collision cells.

---

## 2. Theoretical framework

### 2.1 Osmotic driving force and Nernst potential

For ideal NaCl with van't Hoff factor i = 2:

$$\pi = iRTc, \qquad \Delta\pi = \pi_{\mathrm{draw}} - \pi_{\mathrm{feed}}.$$

The open-circuit Nernst voltage for a single cell pair:

$$E_N = \frac{RT}{F}\ln\frac{c_{\mathrm{draw}}}{c_{\mathrm{feed}}}.$$

**Estuary reference** (c_sea = 600, c_river = 20 mol/m³, T = 298.15 K): E_N = **87.39 mV**, V_oc = 50 E_N = **4.37 V**, Δπ = **2.876 MPa**.

**SGH-1 brine pair** (c_d = 1400, c_f = 5 mol/m³): Δπ = **6.916 MPa**, E_N ≈ **118 mV**.

### 2.2 Electrical max-power theorem (RED)

For linear internal resistance R_int (Ω·m²):

$$P_{\max}'' = \frac{V_{\mathrm{oc}}^2}{4 R_{\mathrm{int}}}.$$

Calibrated to literature P_blue = 15 W/m² at estuary conditions gives R_int = **0.318 Ω·m²**.

### 2.3 PRO water transport and Kim–Baker optimum

$$\dot V_w = L_p A(\Delta\pi - \Delta P), \qquad P_{\mathrm{hyd}} = \rho \dot V_w \Delta P.$$

Optimal hydraulic pressure: **ΔP* = Δπ/2**. With efficiencies η_mem, η_hyd:

$$P_{\mathrm{elec,eq}} = \eta_{\mathrm{mem}} \eta_{\mathrm{hyd}} \rho L_p A (\Delta\pi - \Delta P)\Delta P.$$

### 2.4 Concentration polarization

Wall concentration growth:

$$c_w/c_b = \exp(J_w/k_m).$$

Ultrasonic assist modeled as flux gain g on L_p:

$$P_{\mathrm{net}} = P_{\mathrm{PRO}}(g) - P_{\mathrm{US}} - P_0.$$

### 2.5 Column balance (CHORUS)

For parcel area A_k and capacity factors CF_k:

$$P_{\mathrm{column}} = \sum_k A_k \mathrm{CF}_k \langle P_k'' \rangle.$$

Monte Carlo on lognormal P_k'' (N = 8000) with layers: blue_energy, pv_hydro, meg, smfc.

**Results (chorus_results.json):**

| Quantity | Value |
|----------|-------|
| P_column median | 22.76 MW |
| P_column P10 / P90 | 19.63 / 26.46 MW |
| P_pv'' (evap-cooled) | 187.9 W/m² |
| P_blue'' (estuary) | 15.0 W/m² |
| P_MFC'' | 36.7 µW/m² |

PV–hydro dominates the column median; osmotic interface power is a **credible baseload supplement**, not the land-area leader.

### 2.6 Telluric Storm Coupling (TSC)

Three-node conductance network (atmosphere, soil, estuary): **G ψ = I**, dissipated power P_TSC = ψᵀGψ. TSC **routes** charge between high-impedance harvesters; it is not a new energy source.

---

## 3. CHORUS-Skid SGH-1 system

### 3.1 Architecture

SGH-1 integrates:

- **PRO core:** 12 membrane plates (200×300 mm active), draw brine / feed WW manifolds, PX/turbine path.
- **AEH-1 panel:** piezoelectric acoustic harvest (Mode A) + 28 kHz ultrasonic transducers (Mode B).
- **CHORUS enclosure:** thermal/moist ports for future orographic (CHOR) coupling.
- **DAQ:** pressure, conductivity, flow, voltage logging (`daq/logger.py`).

### 3.2 Sizing results (sgh1_design.json)

| Parameter | Value |
|-----------|-------|
| P_target | 10 W |
| P''_design | 8 W/m² |
| A_mem | 0.72 m² (12 plates) |
| Δπ | 6.916 MPa |
| ΔP* | 34.58 bar |
| Q_feed (model) | 0.149 L/min |
| Frame | 664×480×900 mm |

### 3.3 Dimensionless groups (pi_groups)

| Group | Value |
|-------|-------|
| Π₁ = ΔP/Δπ | 0.500 |
| Π₃ = Pe (order) | 0.692 |
| Π₄ = P''A/P_target | 0.576 |
| Π₅ = P_sim/P_target | 0.166 |
| L_p* for 10 W | 6.03×10⁻¹² m/(Pa·s) |

Steady-state model power: **P_sim = 1.66 W**.

---

## 4. Methods

### 4.1 Software

- `notebooks/CHORUS_physics_proof.ipynb` — symbolic and numeric proof, exports `chorus_results.json`.
- `simulation/pro_cycle.py`, `sizing.py`, `membrane_transport.py`, `ultrasonic_cp_gain.py`, `acoustic_harvest.py`.
- `python simulation/run_sizing.py` — design JSON + OpenSCAD constants.
- `python -m simulation.pi_groups` — Π-group export.

### 4.2 Hardware

OpenSCAD library (23 parts), `BUILD_BLUEPRINT.md`, BOM CSV, bench protocol `SGH1_TEST_PROTOCOL.md` (T0 smoke, T1 ±30% power, T2 AEH).

### 4.3 Materials

SS316 wetted paths, FO/PRO membrane sheet (vendor TBD), EPDM seals — see `MATERIALS_SPEC.md`.

---

## 5. Discussion

### 5.1 Why PRO on brine for PoC

Δπ_brine ≈ 2.4× Δπ_estuary improves volumetric power density at the cost of fouling and CP severity. Co-location with desal plants provides **existing pumps, tanks, and permits** — a deployment advantage over greenfield estuary RED.

### 5.2 Simulation–target gap

The 10 W target follows the area law A = P_target/P'' with P''_design = 8 W/m², capped at twelve plates. Default L_p = 1×10⁻¹² m/(Pa·s) under-predicts power. Bench T1 must either validate higher L_p or revise P'' from measured ΔP, Q, and conductivity.

### 5.3 Acoustic layers

Mode A harvest at urban SPL (90–96 dB) remains **mW-class** per panel. Mode B can raise net PRO if flux gain g exceeds parasitic US power — swept in `SGH1_PRO_simulation.ipynb`.

### 5.4 Column narrative vs bench reality

The 22.8 MW/km² median is an **exploratory sum** with uncertainty; it motivates long-term coastal system design but must not be confused with SGH-1 bench claims.

---

## 6. Conclusion

We have presented a physics-first, reproducible framework for CHORUS multi-layer coastal harvest and a concrete PRO bench skid (SGH-1) sized for anthropogenic brine gradients. Near-term defensible work centers on **PRO + DAQ + CP/ultrasonic assist**; column-scale and TSC claims are explicitly tiered as context. Open-source artifacts enable independent verification of every equation cited herein.

---

## References

[1] Teng et al., *Nature Energy* (2026) — nanopore blue energy, ~15 W/m² estuary demonstration.  
[2] Skilhagen et al., *Desalination* — PRO fundamentals and pilot history.  
[3] Kim & Baker, *J. Membrane Sci.* — optimal pressure in osmotic power.  
[4] Fang et al., *Energy Environ. Sci.* (2026) — PV–MHD evaporative coupling.  
[5] Yao et al., *Advanced Materials* — moisture-enabled charge separation (Air-gen).  
[6] Virgo et al., *Global Challenges* (2020) — atmospheric electricity budget.

---

## Appendix A — Repository map

| Path | Content |
|------|---------|
| `docs/CHORUS_MATH_PLAN.md` | Master equation list |
| `docs/math/PRO_LAYER_DERIVATION.md` | Layer F PRO derivation |
| `notebooks/CHORUS_physics_proof.ipynb` | Executable proof |
| `hardware/openscad/` | CAD library |
| `exports/chorus_results.json` | Column + estuary numbers |
| `exports/sgh1_design.json` | Skid sizing |

---

*Correspondence: Joseph Black, via differential-harness repository.*
