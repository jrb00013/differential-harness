# Vortex-Osmotic Hydro (VOH) / Z-Hydro

**VOH** extends AOR with **rotation** and **vertical (z) pressurized flux** — a new site class for water-electricity: **coastal brine outfalls without river head**.

**Parent:** [VISION.md](VISION.md) · **Builds on:** [AOR_PHYSICS.md](AOR_PHYSICS.md)

---

## 1. Why VOH changes the map

| Classic hydro | VOH / Z-Hydro |
|---------------|---------------|
| Requires `ρgΔh` (dam, river) | Requires `Δπ` + optional small `Δh` |
| Dry coasts excluded | **Desal outfalls** worldwide |
| Seasonal flow | **24/7** brine discharge |
| Single physics channel | `ρgΔh + Δπ + ½ρω²r²` stacked |

**Category name:** *osmotic-vortex hydro* — water-electricity from **spinning brine–fresh interfaces**.

---

## 2. Geometry: world vortex cell

Toroidal or cylindrical basin with:

- **Fresh / feed** (light) above or inside.
- **Brine draw** (dense) below or at rim.
- **Halocline** = working membrane interface.
- **Rotation** angular velocity `ω` [rad/s].
- **z-pipe** = axial draw leg extracting **vertical pressurized flux**.

```
        ╭──────── fresh (ρ_f) ────────╮
        │      ↑ z-upwelling core      │
        │  ═══ halocline / membrane ══ │  ← ω (spin)
        │      brine (ρ_b) → rim       │
        ╰────────────┬────────────────╯
                     │ z-PIPE
                     ▼
              work extraction (PX / turbine)
```

---

## 3. Pressure field (cylindrical)

Total pressure at `(r, z)`:

$$\boxed{P(r,z) = P_0 + \underbrace{\rho g z}_{\text{z-hydro}} + \underbrace{\tfrac{1}{2}\rho\omega^2 r^2}_{\text{spin}} + \underbrace{\Pi_{\mathrm{osm}}(r,z)}_{\text{brine motor}}}$$

### 3.1 z-component (Z-Hydro)

Vertical hydraulic head:

$$P_z = \rho g h_{\mathrm{eff}}$$

Axial draw harvests energy where `∂P/∂z` couples to permeate upwelling — **pressurized flux brought up through the water column**.

### 3.2 Spin component

Centrifugal head at radius `r`:

$$P_\omega = \tfrac{1}{2}\rho\omega^2 r^2$$

Example: `ω = 100 rad/s`, `r = 0.15 m`, `ρ = 1020 kg/m³` → `P_ω ≈ 1.1 MPa` (illustrative; bench RPM must respect membrane mechanical limits).

### 3.3 Coupling

Rotation adds **rim pressure** and **interfacial shear** (Taylor–Couette class):

- Shear strips CP → synergistic with UDT/AOR.
- Centrifugal field biases brine to **outer wall** (density + `ω`).

---

## 4. Taylor–Couette osmotic cell (bench v0)

Inner cylinder: membrane drum. Outer cylinder: brine plenum. Gap width `d`. Spin rate `ω`.

$$\tau_{\mathrm{wall}} \propto \mu \frac{\omega r}{d}$$

Shear stress `τ_wall` reduces effective CP thickness `δ_C ∝ D/k_m`.

**Bench v0:** rotating `sgh1_membrane_housing` class drum — compare flat vs `ω > 0` at same ΔP.

---

## 5. Halocline vortex (scale-up)

At basin scale:

- **Ekman pumping** at rotating interface drives vertical exchange.
- **Stratification** stabilizes brine under fresh.
- **Coriolis** (field scale) may supplement spin stability — not required on bench.

**World win** (deployment): every desal **outfall node** in a fleet — not one literal planet-sized vortex.

---

## 6. VOH power model

Combined extractable pressure head:

$$\Delta P_{\mathrm{VOH}} = \Delta P_{\mathrm{osm}} + \rho g \Delta h_z + \tfrac{1}{2}\rho\omega^2 r_{\mathrm{eff}}^2 - \Delta P_{\mathrm{loss}}$$

Power density (illustrative):

$$P''_{\mathrm{VOH}} \approx \eta \,\Delta P_{\mathrm{VOH}} \cdot \frac{Q_{\mathrm{permeate}}}{A_{\mathrm{mem}}}$$

Full skid:

$$P_{\mathrm{net,VOH}} = P_{\mathrm{VOH}} + P_{\mathrm{AEH}} - P_{\mathrm{UDT}} - P_{\mathrm{spin\_motor}} - P_{\mathrm{pump}} - P_{\mathrm{aux}} + P_{\mathrm{px}}$$

`P_spin_motor` = mechanical cost to sustain `ω`.

---

## 7. Civilization-scale resource (honest)

From [math/REAL_WORLD_DATA.md](math/REAL_WORLD_DATA.md):

- Perth-class mixing energy order **~30 GWh/year** (theoretical, one site).
- Global brine discharge **~142×10⁶ m³/day** (UNESCO-class cite in vision docs).

VOH does not create this energy — it **recovers a fraction** before entropy dissipates.

**Fleet amplifier:** N plants × duty cycle × `η_recovery` → **GWh–TWh/year** addressable if fouling and parasitics solved.

**Not sun-equivalent W/m²** on acoustic or membrane footprint alone.

---

## 8. Code

```bash
python -c "from simulation.vortex_osmotic_hydro import voh_state; print(voh_state())"
```

Module: `simulation/vortex_osmotic_hydro.py`

Experiment: **E16** → `vision_stack.voh`

Sweep: `P_net` vs `ω` at fixed `Δπ`, `Δh_z`.

---

## 9. Hardware roadmap

| Component | CAD | Status |
|-----------|-----|--------|
| Spinning membrane drum | extend `sgh1_membrane_housing` | bench v0 |
| z-leg draw | `sgh1_z_pipe.scad` | planned |
| Vortex basin | `sgh1_vortex_basin.scad` | planned |
| Motor / seal | BOM TBD | T1c |

---

## 10. Validation (T1c)

| Run | Config |
|-----|--------|
| A | Flat stack, no spin |
| B | VOH drum, `ω = ω_1` |
| C | VOH + AOR + UDT full chain |

Pass: `P_net(C) > P_net(B) > P_net(A)` at **≥ 1 h** on 80–140 g/L brine simulant.

Log: `ω`, `ΔP`, `Q`, conductivity ×2, `P_spin_motor`, CSV export.

---

## 11. Relation to hydroelectricity

VOH **complements** river hydro:

- **River hydro:** gravitational potential of freshwater inventory.
- **VOH:** chemical potential of **salinity gradients** at coastal infrastructure, optionally plus small head and spin.

Pitch: **"Z-Hydro — hydroelectricity where there is no river, only brine."**

---

*See also: [UDT_PHYSICS.md](UDT_PHYSICS.md), [SGH1_TEST_PROTOCOL.md](SGH1_TEST_PROTOCOL.md)*
