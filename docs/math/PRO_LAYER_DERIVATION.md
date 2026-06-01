# Layer F — Pressure-Retarded Osmosis on Anthropogenic Brine (SGH-1)

Executable counterparts: `simulation/pro_cycle.py`, `simulation/membrane_transport.py`, `notebooks/SGH1_PRO_simulation.ipynb`.

---

## F.1 Thermodynamic driving force

For NaCl with van't Hoff factor $i=2$, the osmotic pressure of a reservoir at molar concentration $c$ (mol/m³) is

$$\pi(c) = i\,R\,T\,c, \qquad T = 298.15\ \mathrm{K}.$$

The **draw** side (desalination reject brine, $c_d \approx 1400$ mol/m³) and **feed** side (treated wastewater, $c_f \approx 5$ mol/m³) give

$$\boxed{\Delta\pi = i R T (c_d - c_f).}$$

**SGH-1 design point:** $\Delta\pi = 6.916\ \mathrm{MPa}$ (34.6 bar class), versus estuary RED $\Delta\pi \approx 2.88\ \mathrm{MPa}$ at $c_\mathrm{sea}=600$, $c_\mathrm{river}=20$ mol/m³.

The corresponding single-pair Nernst potential (informational; PRO power is hydraulic in this model) is

$$E_N = \frac{R T}{F} \ln\frac{c_d}{c_f} \approx 118\ \mathrm{mV}\quad (c_d/c_f = 280).$$

---

## F.2 Water transport and optimal hydraulic pressure

Solution-diffusion water flux (permeability $L_p$, m/(Pa·s)):

$$\dot V_w = L_p\,A\,(\Delta\pi - \Delta P), \qquad \dot m_w = \rho \dot V_w.$$

At steady state, **maximum hydraulic work** on the draw side occurs near the Kim–Baker optimum:

$$\boxed{\Delta P^* = \frac{\Delta\pi}{2}.}$$

**Operating band (FR-1):** $0.4\,\Delta\pi \leq \Delta P \leq 0.6\,\Delta\pi$ → $2.77$–$4.15$ MPa for the SGH-1 brine pair.

---

## F.3 Hydraulic and equivalent electrical power

Hydraulic power extracted from the draw volume:

$$P_\mathrm{hyd} = \dot m_w\,\Delta P.$$

With membrane and hydrodynamic efficiencies $\eta_\mathrm{mem}$, $\eta_\mathrm{hyd}$:

$$\boxed{P_\mathrm{elec,eq} = \eta_\mathrm{mem}\,\eta_\mathrm{hyd}\,\dot m_w\,\Delta P, \qquad P'' = P_\mathrm{elec,eq}/A.}$$

**Default parameters:** $L_p = 1\times10^{-12}$ m/(Pa·s), $\eta_\mathrm{mem}=0.35$, $\eta_\mathrm{hyd}=0.55$, $\Delta P = 0.5\,\Delta\pi$.

At $A = 0.72$ m² this yields $P_\mathrm{elec,eq} \approx 1.7$ W ($\sim 2.4$ W/m²) — below the **10 W design target**. Closing the gap requires bench-calibrated $L_p$, additional plates, or higher effective $P''$ from literature PRO foils (see `docs/math/SKID_ENERGY_BALANCE.md`).

---

## F.4 Concentration polarization (CP)

Film model at the high-salinity wall:

$$\frac{c_w}{c_b} = \exp\left(\frac{J_w}{k_m}\right), \qquad k_m \sim D/\delta_f.$$

Effective driving-force reduction: $\Delta\pi_\mathrm{eff} = \Delta\pi / (c_w/c_b)_\mathrm{outlet}$.

**AEH Mode B (ultrasonic assist):** treat CP disruption as multiplicative gain $g$ on $L_p$:

$$P_\mathrm{net} = P_\mathrm{PRO}(g) - P_\mathrm{US} - P_0,$$

with $P_\mathrm{US} = P''_\mathrm{US}\,A$ (default $1.5$–$2.0$ W/m² driver budget). See `simulation/ultrasonic_cp_gain.py`.

---

## F.5 Salt leakage (Pe group)

Salt flux $J_s = B\,\Delta c$ competes with advection. Peclet number:

$$\Pi_3 = Pe = \frac{v\,L}{D}, \qquad v \sim J_w.$$

High $Pe$ increases draw dilution and reduces $\Delta\pi$ over time — bench protocol T1 tracks conductivity drift.

---

## F.6 RED vs PRO crosswalk

| Regime | High $c$ | Low $c$ | $\Delta\pi$ (MPa) | Primary extraction |
|--------|----------|---------|-------------------|-------------------|
| Estuary RED | 600 (sea) | 20 (river) | 2.88 | Electrical (Nernst + $R_\mathrm{int}$) |
| Sidestream PRO | 1400 (brine) | 5 (WW) | 6.92 | Hydraulic ($\Delta P$ on draw) |

CHORUS column models use RED anchors for **interface** power density ($15$ W/m²); SGH-1 uses PRO for **near-term bench** at existing desal infrastructure.
