# Acoustic-Osmotic Ram (AOR)

**AOR** stacks natural amplifiers: **resonant sound** strips the membrane, **brine osmotic pressure** propels flow, **hyperspeed draw pipe** multiplies hydraulic head.

**Parent:** [VISION.md](VISION.md) · **Coupling:** [UDT_PHYSICS.md](UDT_PHYSICS.md)

---

## 1. Concept

```
  SOUND + WATER (feed / effluent)
           │
           ▼
  ┌────────────────────┐
  │ RESONANT COLUMN    │  Q-factor amplifier
  │ acoustic streaming │  strips CP boundary layer
  └─────────┬──────────┘
            │ membrane
            ▼
  ┌────────────────────┐
  │ BRINE PLENUM       │  Δπ osmotic motor (MPa)
  │ (draw solution)    │
  └─────────┬──────────┘
            │
            ▼
  ┌────────────────────┐
  │ HYPERSPEED PIPE    │  converging draw leg
  │ (ram + Bernoulli)  │  hydraulic amplifier
  └─────────┬──────────┘
            ▼
     turbine / PX → P_work
            │
            ▼
  recirculating brine loop (working fluid)
```

**Tagline:** Sound strips. Brine propels. Pipe amplifies.

---

## 2. Resonant feed column

### 2.1 Acoustic intensity

$$I = \frac{p_{\mathrm{rms}}^2}{\rho c}$$

See `simulation/acoustic_harvest.py` (AEH Mode A harvest is supplemental; AOR uses Mode B actuation).

### 2.2 Resonance Q

For water column height `H` and quarter-wave match `f ≈ c/(4H)`:

$$Q \approx \frac{\omega_0}{\Delta\omega}$$

Stored cyclic energy scales as `Q × P_driver`. Local **acoustic streaming** velocity at membrane wall:

$$v_{\mathrm{stream}} \propto \frac{I}{\rho c} \cdot f$$

**Role:** dilutes **concentration polarization** at the wall, not bulk brine salinity.

### 2.3 Attribute stripping

| Stripped layer | Mechanism |
|----------------|-----------|
| CP film | Streaming + oscillatory shear |
| Hydration shell | High-frequency boundary oscillation |
| Fouling gel | Controlled micro-shear (avoid uncontrolled cavitation) |

Effective result: `k_m ↑`, `g_UDT ↑` (UDT Tink input).

---

## 3. Brine motor (osmotic)

Draw brine at `c_draw` (e.g. 1400 mol/m³) vs feed at `c_feed` (e.g. 5 mol/m³):

$$\Delta\pi = i R T (c_{\mathrm{draw}} - c_{\mathrm{feed}})$$

SGH-1 default: **Δπ ≈ 6.92 MPa**, **ΔP* ≈ 34.6 bar**.

Water flux (solution-diffusion):

$$\dot V_w = L_p A (\Delta\pi - \Delta P)$$

Brine is the **chemical amplifier** — MPa-scale drive without a dam.

---

## 4. Hyperspeed pipe (ram leg)

### 4.1 Converging nozzle

Draw leg area `A(z)` decreasing in flow direction:

$$\rho v \cdot A = \mathrm{const} \quad \Rightarrow \quad v \uparrow \text{ as } A \downarrow$$

Bernoulli (steady, inviscid reference):

$$P + \tfrac{1}{2}\rho v^2 + \rho g z = \mathrm{const}$$

### 4.2 Water hammer / ram (transient)

Pressure spike on sudden momentum change:

$$\Delta P_{\mathrm{ram}} \approx \rho c_{\mathrm{sound}} \,\Delta v$$

Pressure exchanger (`sgh1_px_module`) recovers a fraction `η_px` of draw pressurization energy.

### 4.3 Output

Pressurized **working brine stream** at design rating; permeate flux coupled to hydraulic work:

$$P_{\mathrm{hyd}} = \rho \dot V_w \Delta P \cdot \eta_{\mathrm{hyd}}$$

---

## 5. Combined AOR power density

Illustrative extractable head:

$$\Delta P_{\mathrm{eff}} \approx \Delta P_{\mathrm{osm}} + \rho g \Delta h_{\mathrm{z}} - \Delta P_{\mathrm{loss}}$$

where `Δh_z` is axial leg height (see [VOH_PHYSICS.md](VOH_PHYSICS.md)).

$$P_{\mathrm{AOR}} \approx \eta_{\mathrm{mem}}\eta_{\mathrm{hyd}}\,\rho\,L_{p,\mathrm{eff}}\,A\,(\Delta\pi - \Delta P)\Delta P - P_{\mathrm{US}} - P_{\mathrm{pump}} + P_{\mathrm{px}}$$

---

## 6. Natural amplifiers summary

| Stage | Amplifier | Input | Output |
|-------|-----------|-------|--------|
| Resonant column | Q | W driver | Local streaming / `k_m` gain |
| Brine plenum | Δπ | Salinity gradient | MPa osmotic head |
| Hyperspeed pipe | Ram / area change | Flux momentum | Pressure recovery |
| PX | η_px | Draw pressure | Feed pressurization credit |

**Not claimed:** acoustic areal power comparable to solar (~1 kW/m²). AOR taps **osmotic + hydraulic** head; sound is the **unlock**, not the primary reservoir.

---

## 7. Code

```bash
python -c "from simulation.acoustic_osmotic_ram import aor_state; print(aor_state())"
```

Module: `simulation/acoustic_osmotic_ram.py`

Experiment: **E15** → `vision_stack.aor`

---

## 8. Hardware mapping

| AOR stage | SGH-1 part |
|-----------|------------|
| Resonant column | `chorus_skid_enclosure`, feed manifold |
| Membrane | `sgh1_membrane_*` stack |
| Brine plenum | draw manifold, brine tank adapter |
| Hyperspeed pipe | `sgh1_manifold_draw` → `sgh1_px_module` → `sgh1_turbine_housing` |
| UDT | `chorus_aeh_panel`, `sgh1_us_mount_ring` |

Planned: `sgh1_z_pipe.scad` (axial leg).

---

## 9. Validation (T1b)

1. Baseline PRO, no US, no resonance tuning.
2. Enable resonant column (match `f_us` to column `H`).
3. Enable UDT phased rays.
4. Compare `P_net` at 30 min and 60 min (fouling window).

Pass: **AOR chain beats baseline at ≥ 60 min** on same brine simulant.

---

*See also: [CHORUS_ACOUSTIC_LAYER.md](CHORUS_ACOUSTIC_LAYER.md), [math/PRO_LAYER_DERIVATION.md](math/PRO_LAYER_DERIVATION.md)*
