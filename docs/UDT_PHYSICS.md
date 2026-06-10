# Universal Differential Tink (UDT)

Specification for the **differential-harness** control and actuation layer on toroidal membrane loops.

**Parent:** [VISION.md](VISION.md)

---

## 1. Purpose

The UDT raises **sustainable permeate flux** by:

1. Measuring **osmotic differentials** along the feed spine (line).
2. Driving a **discrete ray field** on each membrane loop (circle).
3. Encoding actuation as **geometry-scaled particle bytes**.
4. Applying the **Tink kernel** to produce effective mass-transfer `k_m,eff` and flux gain.

---

## 2. Geometry

### 2.1 Line (spine)

- Index loops `i = 1 … N_loop` along interconnect length `L_line` [m].
- Conductivity sensors at each node give feed/draw salinity proxy `σ_feed,i`, `σ_draw,i`.

$$\Delta\sigma_i = \frac{\partial \sigma}{\partial x}\bigg|_i \approx \frac{\sigma_{\mathrm{draw},i} - \sigma_{\mathrm{feed},i}}{\Delta x_i}$$

$$\Delta\pi_i = i R T \,\Delta c_i \quad (\Delta c_i \propto \Delta\sigma_i)$$

This implements patent claim **ΔP/Δπ feedback from dual conductivity**.

### 2.2 Circle (loop)

Each loop `i` has:

| Symbol | Meaning |
|--------|---------|
| `A_loop,i` | Active membrane area [m²] |
| `C_i = 2πR_i` | Loop circumference [m] |
| `L_line,i` | Spine segment length to neighbors [m] |

Membrane is a **closed 1-cycle** — flux and actuation integrate around the ring.

---

## 3. Ray field

### 3.1 Discretization

Design-point ray count:

$$N_r = 64534$$

(parameter `N_RAYS_DEFAULT` in `simulation/constants.py`; may be reduced on bench hardware e.g. 16–64 transducers).

Each ray `k` on loop `i`:

| Quantity | Symbol | Unit |
|----------|--------|------|
| Surface anchor | `s_k` | m² |
| Direction | `û_k` | — |
| Intensity | `I_k` | W/m² |
| Phase | `φ_k` | rad |

Energy density on the loop surface:

$$\mathcal{E}(\mathbf{r}) = \sum_{k=1}^{N_r} I_k\,\delta(\mathbf{r} - \mathbf{r}_k)$$

**Implementation:** vectorized `numpy` arrays `(N_r,)` — the **vectorized runtime**.

### 3.2 Physical role

Rays deliver **actuation power** (ultrasound / electro-acoustic) that modifies the concentration-polarization boundary layer via increased local shear and `k_m`.

---

## 4. e90 wavelength

**E90** = wavelength band carrying **90%** of coupled actuation power in the ray spectrum.

Default carrier: **f_us = 28 kHz** ultrasonic in water:

$$\lambda_{e90} \approx \frac{c_{\mathrm{sound}}}{f_{\mathrm{us}}} \approx \frac{1500}{28000} \approx 0.054\ \mathrm{m}$$

(`C_SOUND_WATER`, `F_US_DEFAULT` in constants.)

The e90 band sets phased ring timing: traveling wave speed around circumference `C_i` at phase velocity tied to `λ_e90`.

---

## 5. Particle byte

A **particle byte** is a quantized actuation packet per ray per control timestep `Δt`.

### 5.1 Byte length (geometry scaling)

$$\boxed{\texttt{byte\_len}_{k} = \frac{A_{\mathrm{loop},i}}{L_{\mathrm{line},i}} \cdot \frac{\lambda_{e90}}{\lambda_0}}$$

- `λ_0` = reference wavelength (1 m normalization in code).
- Loops with **more membrane per unit spine** receive **longer bytes** → higher control gain.

### 5.2 Energy quantum

$$E_k = I_k \cdot a_k \cdot \Delta t \quad [J]$$

where `a_k` is ray footprint area [m²].

Byte integer (runtime state):

$$b_k = \max\left(1,\ \left\lfloor \frac{E_k}{E_0} \cdot \texttt{byte\_len}_k \right\rfloor\right)$$

State vectors: **B** ∈ ℤ^N_r (bytes), **Φ** ∈ ℝ^N_r (phases).

---

## 6. Tink kernel

The **Universal Differential Tink** maps `(I_k, b_k, φ_k, Δσ_i)` → transport coefficients on loop `i`.

### 6.1 Effective mass-transfer coefficient

$$k_{m,\mathrm{eff},i} = k_{m,0}\left(1 + \eta_{\mathrm{tink}} \cdot \frac{\sum_{k \in \mathrm{loop}\,i} b_k\, I_k \cos\phi_k}{\sum_{k \in \mathrm{loop}\,i} b_k}\right)$$

- `k_m,0` = baseline film coefficient [m/s] (default `D/L` scale from `membrane_transport.py`).
- `η_tink` = coupling efficiency ∈ [0, 1] (calibration constant).

### 6.2 Flux gain

Polarization factor from film model:

$$\frac{c_w}{c_b} = \exp(J_w / k_{m,\mathrm{eff}})$$

Effective flux gain vs baseline:

$$g_{\mathrm{UDT}} = \frac{J_w(k_{m,\mathrm{eff}})}{J_w(k_{m,0})}$$

Feeds `simulation/ultrasonic_cp_gain.py` as **spatial** gain, not a single scalar.

### 6.3 Differential pressure trim

$$\Delta P_i = \mathrm{clip}\left(\Delta P^{*}\cdot\frac{\Delta\pi_i}{\overline{\Delta\pi}},\ \Delta P_{\min},\ \Delta P_{\max}\right)$$

Kim–Baker optimum preserved on average: `ΔP* ≈ Δπ/2`.

---

## 7. Power accounting

Loop production (coupled to `pro_cycle.py`):

$$P_{\mathrm{loop},i} = \eta_{\mathrm{mem}}\eta_{\mathrm{hyd}}\,\rho\,L_{p,\mathrm{eff},i}\,A_{\mathrm{loop},i}\,(\Delta\pi_i - \Delta P_i)\,\Delta P_i$$

Actuation cost:

$$P_{\mathrm{UDT}} = \sum_k I_k a_k + P_{\mathrm{driver}}$$

Net (see [math/SKID_ENERGY_BALANCE.md](math/SKID_ENERGY_BALANCE.md)):

$$P_{\mathrm{net}} = \sum_i P_{\mathrm{loop},i} + P_{\mathrm{AEH}} - P_{\mathrm{UDT}} - P_{\mathrm{pump}} - P_{\mathrm{aux}}$$

---

## 8. Code

```bash
python -c "from simulation.differential_tink import demo; demo()"
```

Module: `simulation/differential_tink.py`

Functions: `ray_field()`, `particle_bytes()`, `tink_kernel()`, `loop_transport_state()`

Experiment: **E14** in `simulation/experiments.py` → `vision_stack.udt`

---

## 9. Bench hardware

- Piezo / US transducers on `chorus_aeh_panel`, `sgh1_us_mount_ring`.
- Conductivity probes on feed/draw manifolds.
- DAQ: `daq/logger.py` at ≥ 1 Hz.
- Planned CAD: `sgh1_tink_ring.scad` (toroidal mount pattern).

---

## 10. Falsification tests

| Test | Prediction if UDT is real |
|------|---------------------------|
| US off vs on, same ΔP | `P_net(on) > P_net(off)` after 30 min fouling |
| Phased vs random φ_k | Phased traveling wave beats incoherent |
| Large `A_loop/L_line` | Higher `b_k` loops show larger `g_UDT` |

---

## 11. Constants (calibrate on T1)

| Constant | Default | Source |
|----------|---------|--------|
| `N_RAYS_DEFAULT` | 64534 | design mesh |
| `F_US_DEFAULT` | 28000 Hz | AEH driver |
| `ETA_TINK_DEFAULT` | 0.15 | TBD bench |
| `E0_JOULES` | 1e-6 | byte quantum |

---

*See also: [AOR_PHYSICS.md](AOR_PHYSICS.md), [VOH_PHYSICS.md](VOH_PHYSICS.md)*
