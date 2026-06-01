# SGH-1 Dimensional Analysis

## Governing groups

| Symbol | Definition | Use |
|--------|------------|-----|
| $\Pi_1$ | $\Delta P / \Delta\pi$ | Pressure ratio — operate 0.4–0.6 |
| $\Pi_2$ | $J_w \sqrt{\rho/\Delta\pi}$ | Water flux vs osmotic driving force |
| $\Pi_3$ | $Pe = v L / D$ | Salt leakage vs advection |
| $\Pi_4$ | $P'' A / P_\mathrm{target}$ | Area scale law |

## Scale law (area)

$$A_\mathrm{mem} = \frac{P_\mathrm{target}}{P''_\mathrm{design}}$$

Default $P''_\mathrm{design} = 15\ \mathrm{W/m^2}$ (estuary RED anchor; tune from bench).

## Hydraulic

$$\Delta\pi = iRT(c_\mathrm{draw} - c_\mathrm{feed})$$
$$\Delta P^* = \frac{\Delta\pi}{2}$$

## Simulator

```bash
python simulation/run_sizing.py --power 50 --density 15
```
