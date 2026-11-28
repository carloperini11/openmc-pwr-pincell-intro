# 2D PWR Pin-Cell Moderation Study (OpenMC)

Monte Carlo eigenvalue calculation of the infinite multiplication factor (k-inf) for a 2D PWR fuel pin-cell in OpenMC.
Holding UO_2 fuel and Zircaloy cladding radiuses fixed, varying the square lattice pitch sweeps the moderator-to-fuel volume ratio (V_m/V_f) across under-moderated and over-moderated regimes.

![Moderation Curve](moderation_curve.png)

## Run
```bash
python pincell_study.py
```
