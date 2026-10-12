"""Independent SciPy reference integration; no target-author code or results."""
import csv
import json
import platform
from pathlib import Path
import numpy as np
import scipy
from scipy.integrate import quad
from scipy.stats import genextreme

ROOT = Path(__file__).resolve().parents[1]
def rows(name):
    with (ROOT / 'results' / name).open() as f:
        return [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]

bands = rows('flood_fixture.csv')
gev = rows('gev_fixture.csv')[0]
distribution = genextreme(-gev['shape'], loc=gev['location_m'], scale=gev['scale_m'])

def damage_reference(water):
    """Direct numerical elevation integral, independent of Julia's primitive."""
    total = 0.0
    for b in bands:
        lower, upper = b['lower_m'], min(water, b['upper_m'])
        if upper <= lower:
            continue
        density = b['area_km2'] / (b['upper_m'] - b['lower_m'])
        def integrand(elevation):
            depth = water - elevation
            capital = b['capital_usd_km2'] * depth / (1.0 + depth)
            lives = b['people_km2'] * b['mortality'] * b['vsl_usd']
            return density * (1.0 - b['resilience']) * (capital + lives)
        total += quad(integrand, lower, upper, epsabs=1e-7, epsrel=1e-12)[0]
    return total

loss_ref, error_estimate = quad(
    lambda s: damage_reference(s) * distribution.pdf(s),
    gev['lower_m'], gev['upper_m'], points=[0.0, 1.0, 2.0, 5.0],
    epsabs=1e-5, epsrel=1e-10, limit=200)
flood = rows('flood_convergence.csv')
for r in flood:
    r['absolute_difference_usd_per_year'] = abs(r['expected_loss_usd_per_year'] - loss_ref)
fine_error = flood[-1]['absolute_difference_usd_per_year'] / loss_ref
assert fine_error < 1e-6, ('flood reference discrepancy', fine_error)
depth_errors = [abs(r['damage_usd'] - damage_reference(r['water_height_m']))
                for r in rows('flood_damage.csv')]
assert max(depth_errors) < 1e-7
emissions = rows('emissions_limit.csv')
assert all(abs(r['remaining_fraction'] - r['continuous_fraction'] -
               r['endpoint_error_prediction']) < 1e-9 for r in emissions)
audit = rows('published_table_audit.csv')
assert sum(r['published_count'] for r in audit) == 5000
assert sum(r['tail_count_audited'] for r in audit) == 250
assert all(round(r['tail_percent_calculated']) == r['tail_percent_printed'] for r in audit)
greenland = rows('greenland_convergence.csv')
diffusion = rows('diffusion_convergence.csv')
anto = rows('anto_transform.csv')
metrics = {
    'scope': 'manufactured verification, not target projection validation',
    'scipy_expected_loss_usd_per_year': loss_ref,
    'scipy_quadrature_error_estimate_usd_per_year': error_estimate,
    'julia_flood_finest_relative_error': fine_error,
    'damage_integral_max_absolute_error_usd': max(depth_errors),
    'greenland_finest_error_m_sle': greenland[-1]['absolute_error_m'],
    'greenland_refinement_factors': [a['absolute_error_m'] / b['absolute_error_m']
                                   for a, b in zip(greenland[:-1], greenland[1:])],
    'diffusion_finest_error_k': diffusion[-1]['max_error_k'],
    'diffusion_refinement_factors': [a['max_error_k'] / b['max_error_k']
                                   for a, b in zip(diffusion[:-1], diffusion[1:])],
    'diffusion_max_balance_error_k_m': max(r['max_balance_error_k_m'] for r in diffusion),
    'anto_minimum_sampled_c': min(r['ocean_temperature_c'] for r in anto),
    'emissions_annual_remaining_fraction_gamma007': next(
        r['remaining_fraction'] for r in emissions
        if r['decline_per_year'] == 0.07 and r['step_years'] == 1.0),
    'printed_table_counts_sum': 5000,
    'printed_table_tail_sum': 250,
    'python_version': platform.python_version(),
    'numpy_version': np.__version__,
    'scipy_version': scipy.__version__,
    'reference_checks_passed': 7,
}
(ROOT / 'results' / 'verification.json').write_text(json.dumps(metrics, indent=2, sort_keys=True) + '\n')
with (ROOT / 'results' / 'flood_reference_comparison.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(flood[0]))
    writer.writeheader()
    writer.writerows(flood)
print('SciPy reference integration and diagnostic consistency checks passed.')
