import numpy as np
import matplotlib.pyplot as plt
import openmc

# Materials
fuel = openmc.Material(name='UO2')
fuel.add_element('U', 1.0, enrichment=3.5)
fuel.add_element('O', 2.0)
fuel.set_density('g/cm3', 10.4)

clad = openmc.Material(name='Zircaloy')
clad.add_element('Zr', 1.0)
clad.set_density('g/cm3', 6.55)

water = openmc.Material(name='H2O')
water.add_element('H', 2.0)
water.add_element('O', 1.0)
water.set_density('g/cm3', 0.72)
water.add_s_alpha_beta('c_H_in_H2O')

materials = openmc.Materials([fuel, clad, water])
materials.export_to_xml()

# Pin radii [cm]
r_fuel = 0.41
r_clad = 0.475
fuel_cyl = openmc.ZCylinder(r=r_fuel)
clad_cyl = openmc.ZCylinder(r=r_clad)

# Simulation settings (lightweight for parametric sweep)
settings = openmc.Settings()
settings.batches = 60
settings.inactive = 15
settings.particles = 2000
settings.source = openmc.IndependentSource(
    space=openmc.stats.Box([-r_fuel, -r_fuel, -1], [r_fuel, r_fuel, 1])
)
settings.output = {'tallies': False}
settings.export_to_xml()

pitches = np.linspace(1.10, 2.20, 8)
k_vals = []
k_errs = []
vm_vf_ratios = []

for pitch in pitches:
    box = openmc.model.RectangularPrism(width=pitch, height=pitch, boundary_type='reflective')

    fuel_cell = openmc.Cell(fill=fuel, region=-fuel_cyl)
    clad_cell = openmc.Cell(fill=clad, region=+fuel_cyl & -clad_cyl)
    water_cell = openmc.Cell(fill=water, region=+clad_cyl & -box)

    geometry = openmc.Geometry([fuel_cell, clad_cell, water_cell])
    geometry.export_to_xml()

    openmc.run(output=False)

    with openmc.StatePoint('statepoint.60.h5') as sp:
        k_vals.append(sp.keff.nominal_value)
        k_errs.append(sp.keff.std_dev)

    v_fuel = np.pi * r_fuel**2
    v_mod = pitch**2 - np.pi * r_clad**2
    vm_vf_ratios.append(v_mod / v_fuel)
    print(f"Pitch = {pitch:.2f} cm | Vm/Vf = {v_mod/v_fuel:.2f} | k_inf = {k_vals[-1]:.4f} +/- {k_errs[-1]:.4f}")

plt.figure(figsize=(7, 4.5))
plt.errorbar(vm_vf_ratios, k_vals, yerr=k_errs, fmt='o-', capsize=3, color='navy')
plt.axhline(1.0, color='gray', linestyle='--', linewidth=1, label='k_inf = 1.0')
plt.xlabel('Moderator-to-Fuel Volume Ratio (Vm / Vf)')
plt.ylabel('Infinite Multiplication Factor (k_inf)')
plt.title('2D PWR Pin-Cell Moderation Curve (OpenMC)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig('moderation_curve.png', dpi=200)
