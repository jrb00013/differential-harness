# Dimensionless Groups — Numeric Evaluation (SGH-1)

Computed by `python -m simulation.pi_groups` at the default 10 W / 8 W/m² design point.

| Group | Definition | SGH-1 value | Interpretation |
|-------|------------|-------------|----------------|
| $\Pi_1$ | $\Delta P / \Delta\pi$ | **0.500** | At Kim–Baker optimum |
| $\Pi_2$ | $J_w \sqrt{\rho / \Delta\pi}$ | **4.16×10⁻¹¹** | Water flux vs osmotic head (SI) |
| $\Pi_3$ | $Pe = v L / D$ | **0.692** | Moderate CP risk along 0.3 m channel |
| $\Pi_4$ | $P'' A / P_\mathrm{target}$ | **0.576** | Area law: 0.72 m² × 8 W/m² / 10 W |
| $\Pi_5$ | $P_\mathrm{sim} / P_\mathrm{target}$ | **0.166** | Model vs target ($P_\mathrm{sim}$ = 1.66 W) |

## Area scale law

$$A_\mathrm{mem} = \frac{P_\mathrm{target}}{P''_\mathrm{design}} = \frac{10}{8} = 0.875\ \mathrm{m^2} \Rightarrow \mathrm{cap\ at\ } 12 \times 0.06 = 0.72\ \mathrm{m^2}.$$

## Operating band check

$\Pi_1 = 0.5 \in [0.4, 0.6]$ — satisfies FR-1 from `SGH1_DEVICE_SPEC.md`.

## Inverse sizing for $L_p$ (bench target)

To hit $P_\mathrm{target} = 10$ W at $\Delta P = \Delta\pi/2$ with $A = 0.72$ m²:

$$L_p^\* \approx \frac{P_\mathrm{target}}{\eta_\mathrm{mem}\eta_\mathrm{hyd}\,A\,(\Delta\pi/2)^2} \approx 6.03\times10^{-12}\ \mathrm{m/(Pa\cdot s)}.$$

This is the permeability to verify in T1 (±30% protocol in `SGH1_TEST_PROTOCOL.md`).
