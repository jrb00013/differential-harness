# CHORUS-AEH Acoustic Layer

## Mode A — Harvest

$I = p_\mathrm{rms}^2 / (\rho c)$, $P = \eta I A$.

See `simulation/acoustic_harvest.py`.

| SPL (dB) | ~Intensity | 0.5 m² @ 2% η |
|----------|------------|----------------|
| 80 | ~10⁻⁵ W/m² | µW |
| 90 | ~10⁻⁴ W/m² | tens µW |
| 96 (plant) | higher | mW class |

## Mode B — Enhance

Ultrasonic CP reduction: flux gain $g$ → net gain $P_\mathrm{PRO}(g) - P_\mathrm{US} - P_0$.

See `simulation/ultrasonic_cp_gain.py`.

## CAD

`hardware/openscad/chorus_aeh_panel.scad`
