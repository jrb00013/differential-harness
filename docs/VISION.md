# CHORUS Vision — differential-harness

**differential-harness** is the open engineering stack for a new class of water-electricity: **osmotic-vortex hydro** at anthropogenic brine outfalls.

This document is the master index. Detailed physics live in linked specs. Executable models live in `simulation/`.

---

## One sentence

> **Sound strips the membrane. Brine propels the loop. Spin and the z-pipe amplify pressure. The Tink differential bus tunes every loop. Fleet deployment at desal outfalls harvests mixing energy gravity hydro cannot reach.**

---

## The problem

- Desalination discharges **hypersaline brine** (~52–70 g/L, often 1.5–2× seawater).
- Treated effluent nearby stays **low salinity** (~5 mol/m³ class).
- Mixing releases **Gibbs free energy** that is normally wasted as entropy.
- Statkraft (2009–2013) proved PRO in principle (~1 W/m²) and **stopped** on fouling and economics.
- Literature now reports **~6.3 W/m²** PRO on commercial RO membranes (Pedersen et al., 2024).

**Gap:** no shipped modular system combines **acoustic CP stripping**, **differential loop control**, **rotating stratified brine geometry**, and **vertical z-leg work extraction** at sidestream scale.

---

## Architecture stack (bottom → top)

| Layer | Name | Role | Doc | Sim |
|-------|------|------|-----|-----|
| 0 | **SGH-1 PRO core** | Brine draw + low-sal feed → pressurized permeate | [SGH1_DEVICE_SPEC.md](SGH1_DEVICE_SPEC.md) | `pro_cycle.py` |
| 1 | **UDT** | Universal Differential Tink — ray field + particle bytes → `k_m,eff` | [UDT_PHYSICS.md](UDT_PHYSICS.md) | `differential_tink.py` |
| 2 | **AOR** | Acoustic-Osmotic Ram — resonant sound + brine motor + hyperspeed pipe | [AOR_PHYSICS.md](AOR_PHYSICS.md) | `acoustic_osmotic_ram.py` |
| 3 | **VOH / Z-Hydro** | Vortex-Osmotic Hydro — rotation + halocline + axial z-pressure harvest | [VOH_PHYSICS.md](VOH_PHYSICS.md) | `vortex_osmotic_hydro.py` |
| 4 | **Fleet** | Cartridge modules at every desal outfall | [SGH1_PATENT_AND_DEPLOYMENT.md](SGH1_PATENT_AND_DEPLOYMENT.md) | `real_world_calibration.py` |

Bench path today: **Layer 0 → 1 → 2**. Layer 3 is the scale-up geometry. Layer 4 is deployment.

---

## Natural amplifiers (no over-unity)

All power is bounded by exogenous flux minus dissipation (see [CHORUS_MATH_PLAN.md](CHORUS_MATH_PLAN.md) §0).

| Amplifier | Mechanism | Typical scale |
|-----------|-----------|---------------|
| **Resonance (Q)** | Acoustic energy stored in water column | Local streaming ↑ |
| **Osmotic Δπ** | Chemical potential brine vs feed | **MPa** class |
| **Hydraulic ram** | Momentum in converging draw leg | Pressure spike / PX recovery |
| **Centrifugal** | `½ρω²r²` in rotating cell | Added draw head + CP shear |
| **Stratification** | `ρ_brine > ρ_fresh` | Halocline engine, z-upwelling |
| **Fleet** | N plants × brine flow | **GWh–TWh** mixing resource |

Sound alone is **mW–W/m²**. Brine mixing at coastal scale is **GWh/year per large plant**.

---

## Geometry (line + circle + z)

```
        feed spine (LINE) ───●────●────●────
                            │    │    │
                         LOOP  LOOP  LOOP   ← membrane circles (UDT)
                            │    │    │
                            └── z-PIPE (axial draw) ──→ work extraction
```

- **Line** = interconnect length `L_line` [m] between loops (hydraulic + sensor bus).
- **Circle** = toroidal membrane loop, area `A_loop`, circumference `C`.
- **z-pipe** = hyperspeed axial draw leg; harvests **vertical pressurized flux** `∂P/∂z`.

---

## Validation ladder

| Stage | Test | Pass criterion |
|-------|------|----------------|
| **T0** | Coupon / single plate | No leaks @ 3 bar; 15 min steady signal |
| **T1** | Full stack | 1 h run; `P_net > 0`; ±30% vs sim |
| **T1b** | UDT / US on vs off | `P_net(US on) > P_net(US off)` same ΔP |
| **T1c** | Spin vs flat | `P_net(ω>0) > P_net(ω=0)` same ΔP |
| **T2** | Field sidestream | Utility NDA; 24 h brine + effluent CSV |
| **T3** | Fleet pilot | SEC reduction or net export $/m³ brine |

Protocol: [SGH1_TEST_PROTOCOL.md](SGH1_TEST_PROTOCOL.md)

---

## Simulation reproduce

```bash
pip install -e .
python -m simulation.experiments    # includes vision_stack (E14–E16)
python -m simulation.run_sizing --power 50
```

Vision exports: `exports/paper_experiments.json` → `vision_stack` key.

---

## Document map

### Vision & physics (this program)

| Document | Content |
|----------|---------|
| [VISION.md](VISION.md) | This file — master index |
| [UDT_PHYSICS.md](UDT_PHYSICS.md) | Rays, e90, particle bytes, Tink kernel |
| [AOR_PHYSICS.md](AOR_PHYSICS.md) | Acoustic-Osmotic Ram |
| [VOH_PHYSICS.md](VOH_PHYSICS.md) | Vortex-Osmotic Hydro / Z-Hydro |
| [CHORUS_MATH_PLAN.md](CHORUS_MATH_PLAN.md) | Layers A–F, column balance |
| [CHORUS_ACOUSTIC_LAYER.md](CHORUS_ACOUSTIC_LAYER.md) | AEH Mode A/B |

### Math & data

| Document | Content |
|----------|---------|
| [math/PRO_LAYER_DERIVATION.md](math/PRO_LAYER_DERIVATION.md) | PRO transport |
| [math/SKID_ENERGY_BALANCE.md](math/SKID_ENERGY_BALANCE.md) | `P_net` definition |
| [math/REAL_WORLD_DATA.md](math/REAL_WORLD_DATA.md) | Statkraft, Perth, Pedersen |
| [math/EXPERIMENTAL_RESULTS.md](math/EXPERIMENTAL_RESULTS.md) | E1–E13 + vision E14–E16 |

### Hardware & deployment

| Document | Content |
|----------|---------|
| [../hardware/BUILD_BLUEPRINT.md](../hardware/BUILD_BLUEPRINT.md) | Build order |
| [SGH1_DEVICE_SPEC.md](SGH1_DEVICE_SPEC.md) | FR-1–FR-5 |
| [SGH1_PATENT_AND_DEPLOYMENT.md](SGH1_PATENT_AND_DEPLOYMENT.md) | Claims, outreach |
| [INVENTOR_NOTEBOOK.md](INVENTOR_NOTEBOOK.md) | Milestones |

---

## Honest claims (tiered)

**Tier 1 — defensible near-term (bench):**
- PRO on anthropogenic brine + effluent
- AEH harvest (supplemental mW)
- Ultrasonic CP assist (net gain if `g ≳ 1.5`)
- UDT differential conductivity → ΔP trim

**Tier 2 — engineering target (T1c/T2):**
- AOR resonant column + ram pipe
- Rotating loop fouling advantage
- Z-leg work extraction

**Tier 3 — civilization scale (fleet):**
- Material SEC reduction at co-located desal + WWTP
- Global brine outfall energy recovery

**Not claimed:** over-unity; sun-equivalent W/m² from acoustics alone; replacement of river hydro.

---

## CAD roadmap (not yet built)

| Part | Purpose | Status |
|------|---------|--------|
| `sgh1_*` (23 parts) | SGH-1 bench PRO | ✓ OpenSCAD |
| `sgh1_tink_ring.scad` | Toroidal UDT ray mounts | planned |
| `sgh1_z_pipe.scad` | Axial hyperspeed draw leg | planned |
| `sgh1_vortex_basin.scad` | Taylor–Couette / halocline cell | planned |

---

## Pitch (external)

**Category:** Osmotic-vortex hydro (VOH) — water-electricity without a dam.

**Wedge:** Membrane fouling/CP solved by UDT + AOR; brine is the motor; rotation + z-pipe are amplifiers.

**Ask:** Sidestream tap for T2; membrane vendor partnership for L_p validation.

---

*CHORUS Research · differential-harness · June 2026*
