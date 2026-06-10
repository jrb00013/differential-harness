# CHORUS — Mathematical & Physical Proof Plan

**CHORUS** = *Columnar Harvest of Osmotic, Rhizospheric, Orographic, and Solar flux*

This document is the derivation blueprint. The executable proof lives in **`notebooks/CHORUS_physics_proof.ipynb`**.

---

## 0. Axioms & notation

| Symbol | Meaning | SI |
|--------|---------|-----|
| $R$ | Gas constant | J/(mol·K) |
| $F$ | Faraday constant | C/mol |
| $T$ | Temperature | K |
| $z$ | Ion valence | 1 |
| $c_i$ | Molar concentration | mol/m³ |
| $\psi$ | Electric potential | V |
| $\pi$ | Osmotic pressure | Pa |
| $\mathbf{N}$ | Molar flux | mol/(m²·s) |
| $\mathbf{J}_q$ | Energy flux | W/m² |

**Postulate (no over-unity):** Total electrical power extracted from the column at steady state satisfies
$$\sum_k P_k \leq \sum_j \dot{E}_{j,\mathrm{in}} - \dot{S}T$$
where $\dot{E}_{j,\mathrm{in}}$ are exogenous fluxes (solar irradiance, geochemical mixing, wind kinetic, etc.) and $\dot{S}T$ is dissipation.

---

## 1. Layer A — Osmotic mixing & blue energy (RED)

### 1.1 Gibbs free energy of ideal electrolyte mixing

For species $i$ transferring from reservoir $+$ to $-$:
$$\Delta g_{\mathrm{mix}} = RT \sum_i \int \ln\frac{a_i^+}{a_i^-}\,dc_i$$

For single 1:1 salt NaCl with $c^+ = c^-$ (activity $a \approx c$):
$$\Delta G_{\mathrm{mix}} = 2RT\,V\,\left(c_+\ln\frac{c_+}{c_-} - (c_+-c_-)\right)$$

### 1.2 Van't Hoff osmotic pressure
$$\pi = i\,RT\,c \quad (i=2\ \text{for NaCl})$$
$$\Delta\pi = \pi_{\mathrm{sea}} - \pi_{\mathrm{river}}$$

### 1.3 Hydraulic / mixing power ceiling
$$\boxed{P_{\mathrm{mix,max}} = \Delta\pi \cdot Q}$$
with $Q$ = volumetric flow of fresh water into the mixing zone (m³/s).

### 1.4 Nernst membrane potential (single pair)
$$\boxed{E_N = \frac{RT}{zF}\ln\frac{a_{\mathrm{high}}}{a_{\mathrm{low}}}}$$
Stack of $n$ pairs: $V_{\mathrm{oc}} = n E_N$.

### 1.5 Electrical max-power theorem (linear internal resistance)
$$P_{\mathrm{elec}} = IV,\quad V = V_{\mathrm{oc}} - R_{\mathrm{int}} I$$
$$\boxed{P_{\mathrm{max}} = \frac{V_{\mathrm{oc}}^2}{4R_{\mathrm{int}}}} \quad\text{(per unit area if }R_{\mathrm{int}}\text{ is Ω·m²)}$$

### 1.6 Nanopore conductance (slip-corrected, 2026 scaling)
Hagen–Poiseuille + surface charge → conductance $G$ [S/m²]. Hydration lubrication enters as effective slip length $b$:
$$G(b) = G_0\left(1 + \frac{2b}{h}\right)$$
$$P_{\mathrm{np}} = \tfrac{1}{4} G(b)\,V_{\mathrm{oc}}^2$$

**Calibration anchor:** $P_{\mathrm{np}} \approx 15\ \mathrm{W/m^2}$ at $c_{\mathrm{sea}}\approx600$, $c_{\mathrm{river}}\approx20$ mol/m³ (Nature Energy 2026).

---

## 2. Layer B — Moist-electric & hydrovoltaic (orographic)

### 2.1 Water vapor chemical potential
$$\mu_v = \mu_v^\circ(T) + RT\ln a_w,\quad a_w \approx \mathrm{RH}$$
Flux (Fick): $N_v = -D_{\mathrm{eff}}\nabla c_v$.

### 2.2 Asymmetric nanopore charge separation (Air-gen class)
Collision rate on surface $\propto$ molecular flux $\Gamma \propto p_v/\sqrt{2\pi m k_BT}$.
Top vs bottom pore opening area asymmetry $\Rightarrow$ net charge current:
$$\boxed{I_q = e\,\Delta\Gamma\,\bar{q}_{\mathrm{trans}}}$$
Open-circuit: $V_{\mathrm{oc}} \approx I_q/G_{\mathrm{pore}}$.

### 2.3 Streaming potential (hydrovoltaic)
Helmholtz–Smoluchowski:
$$\boxed{E_s = \frac{\varepsilon\zeta}{\sigma}\frac{\Delta p}{\eta}}$$
Streaming current $I_s = \sigma_{\mathrm{eff}} E_s$ (thin double layer).

### 2.4 PV–thermal–evaporative node (coupled)
$$C_{\mathrm{th}}\frac{dT_s}{dt} = \alpha_s G_{\mathrm{solar}} - h_c(T_s-T_\infty) - L_v\dot{m}_e - P_{\mathrm{hybrid}}$$
$$\dot{m}_e = h_m\bigl(c_v^*(T_s)-c_v^\infty\bigr)$$
PV efficiency: $\eta_{\mathrm{pv}}(T_s) = \eta_0\bigl[1 - \beta(T_s-T_{\mathrm{ref}})\bigr]$.

**Coupling gain (EES 2026 class):** waste heat feeds MHD → $\Delta P_{\mathrm{MHD}}/\Delta P_{\mathrm{PV}} \sim 1.5$ on MHD side, $\sim0.15$ on PV side.

---

## 3. Layer C — Rhizosphere (SMFC + piezoelectrotrophy)

### 3.1 Butler–Volmer at anode
$$j = j_0\left[\exp\frac{\alpha_a F\eta}{RT} - \exp\frac{-\alpha_c F\eta}{RT}\right],\quad \eta = E - E_{\mathrm{eq}}$$

### 3.2 Fuel-cell power density
$$P = j(E_0 - b\log j - R_\Omega j)$$
Maximize over $j$ → $P_{\mathrm{mp}}$.

### 3.3 Piezoelectric constitutive (d₃₃ mode)
$$D = d_{33}\sigma + \varepsilon^T E,\quad S = s^E\sigma + d_{33}E$$
Energy per cycle: $U = \frac{1}{2}\int \sigma\,S\,\mathrm{d}V$.

### 3.4 Piezoelectrotrophy coupling
Mechanical power density $P_{\mathrm{mech}}$ from root growth / rain / freeze–thaw:
$$\dot{E}_{\mathrm{bio}} = \eta_{\mathrm{pzt}}\,P_{\mathrm{mech}}$$
feeds exoelectrogenic carbon fixation (parallel pathway to substrate oxidation).

---

## 4. Layer D — Atmospheric charge & collision cells

### 4.1 Fair-weather global circuit
Ionosphere–surface capacitor: $I_{\mathrm{glob}} \approx 1\text{–}3\ \mathrm{kA}$, $V \approx 200\text{–}400\ \mathrm{kV}$:
$$\boxed{P_{\mathrm{glob}} = I_{\mathrm{glob}} V \approx 0.25\text{–}0.9\ \mathrm{GW}}$$
Areal mean: $P'' \approx P_{\mathrm{glob}}/4\pi R_\oplus^2 \sim 10^{-4}\ \mathrm{W/m^2}$.

### 4.2 Droplet collision charging (Mason scaling)
$$\frac{\mathrm{d}q}{\mathrm{d}t} \approx \alpha_{\mathrm{coll}}\,n_d^2\,\pi d^2\,v_{\mathrm{rel}}\,\Delta q$$
Power in volume $V$: $P = \frac{\mathrm{d}q}{\mathrm{d}t} V_{\mathrm{coll}}$.

### 4.3 Tornado kinetic sanity (not harvest target)
$K = \frac{1}{2}\rho V_{\mathrm{tor}} \pi (D/2)^2 H$ — episodic GW, not steady baseload.

---

## 5. CHORUS coupling — Telluric Storm Coupling (TSC)

Three-node conductance network (atmosphere $a$, soil $s$, estuary $w$):

$$\mathbf{G}\boldsymbol{\psi} = \mathbf{I}$$
$$\mathbf{G} = \begin{bmatrix}
G_{as}+G_{s0} & -G_{as} & 0 \\
-G_{as} & G_{as}+G_{sw} & -G_{sw} \\
0 & -G_{sw} & G_{sw}+G_{w0}
\end{bmatrix}$$

Dissipated power: $P_{\mathrm{TSC}} = \boldsymbol{\psi}^\top \mathbf{G}\boldsymbol{\psi}$.

**Interpretation:** CHORUS is not a new energy source; TSC routes **already-separated** charge between layers, improving utilization of high-impedance harvesters (MEG, SMFC).

---

## 6. Column balance (1 km² coastal parcel)

$$\boxed{P_{\mathrm{column}} = \sum_k A_k\,\mathrm{CF}_k\,\langle P_k''\rangle}$$

Monte Carlo on $\ln P_k''$ with literature medians and uncertainties.

**Expected hierarchy (honest):**
1. PV–hydro land ($\sim 10^2$ W/m² footprint-weighted)
2. Blue energy estuary ($\sim 10^1$ W/m² on interface)
3. MEG / collision ($\sim 10^{-2}$–$10^0$ W/m²)
4. SMFC ($\sim 10^{-4}$ W/m²)

---

## 9. Layer F — PRO / anthropogenic brine (SGH-1)

Full derivation: **`docs/math/PRO_LAYER_DERIVATION.md`**. Numeric Π-groups: **`docs/math/DIMENSIONLESS_GROUPS_NUMERIC.md`**. Skid balance: **`docs/math/SKID_ENERGY_BALANCE.md`**.

$$\Delta\pi = iRT(c_\mathrm{brine} - c_\mathrm{feed})$$
$$\Delta P^* \approx \Delta\pi/2$$
$$\dot V_w = L_p A(\Delta\pi - \Delta P), \quad P \approx \eta_\mathrm{mem}\eta_\mathrm{hyd}\,\rho \dot V_w\,\Delta P$$
$$\frac{c_w}{c_b} = \exp(J_w/k_m) \quad\text{(CP)}$$

Bench: `python simulation/run_sizing.py` · Π-groups: `python -m simulation.pi_groups`

---

## 10. Vision stack — UDT / AOR / VOH

**Master index:** [VISION.md](VISION.md)

| Layer | Physics | Key equation |
|-------|---------|--------------|
| **UDT** | Ray field + particle bytes → Tink kernel | $k_{m,\mathrm{eff}} = k_{m,0}(1 + \eta_{\mathrm{tink}}\bar{w})$ |
| **AOR** | Resonant column + brine motor + ram pipe | $P_{\mathrm{net}} = P_{\mathrm{PRO}}(g) - P_{\mathrm{US}} - P_{\mathrm{pump}} + P_{\mathrm{px}}$ |
| **VOH** | Spin + z-hydro + osmosis | $P = P_0 + \rho g z + \tfrac{1}{2}\rho\omega^2 r^2 + \Pi_{\mathrm{osm}}$ |

Sim: `differential_tink.py`, `acoustic_osmotic_ram.py`, `vortex_osmotic_hydro.py` · Experiments E14–E16.

---

## 7. Notebook section map

| § | Content | Method |
|---|---------|--------|
| I | Symbolic Gibbs, Nernst, $P_{\max}$ | SymPy |
| II | RED + slip conductance sweep | NumPy |
| III | MEG flux + $V_{\mathrm{oc}}$ | NumPy |
| IV | Thermal ODE + PV boost | SciPy `solve_ivp` |
| V | Butler–Volmer + piezo | NumPy |
| VI | Global circuit + collision cell | NumPy |
| VII | TSC Kirchhoff + Monte Carlo column | NumPy |

---

## References (anchors)

- Teng et al., *Nat. Energy* 2026 — lipid nanopore blue energy (~15 W/m²)
- Yao et al., *Adv. Mater.* — Air-gen moisture charge separation
- Fang et al., *Energy Environ. Sci.* 2026 — PV–MHD coupling
- NSO 2026 — piezoelectrotrophy paradigm
- Virgo et al., *Glob. Chall.* 2020 — lightning / atmospheric circuit budget
