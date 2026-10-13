"""Scientific-result integrity checks, distinct from model verification."""
from pathlib import Path
import csv,json,math
ROOT=Path(__file__).resolve().parents[1]
def rows(name):
    with (ROOT/'results'/name).open() as f:return list(csv.DictReader(f))
checks={}
r=rows('coupled_emissions_stratified_pilot_refinement.csv')
assert len(r)==16
checks['tail_pilot_CO2_difference_ppm']=max(float(x['max_co2_substep_difference_ppm']) for x in r)
checks['tail_pilot_temperature_difference_K']=max(float(x['max_temperature_substep_difference_K']) for x in r)
assert checks['tail_pilot_CO2_difference_ppm']<.001
assert checks['tail_pilot_temperature_difference_K']<1e-4
r=rows('coupled_emissions_stratified_endpoints.csv');assert len(r)==500
checks['full_carbon_mass_error_GtC']=max(float(x['max_mass_error_GtC']) for x in r)
assert checks['full_carbon_mass_error_GtC']<1e-8
for rule in ('annual_nearest_emissions','fixed_ssp245'):
    d=[x for x in r if x['forcing_rule']==rule];assert len(d)==250
    for field in ('weight_prior','weight_budget50','weight_budget75'):
        assert abs(sum(float(x[field]) for x in d)-1)<1e-12
r=rows('sea_level_stratified_pilot_refinement.csv');assert len(r)==80
checks['AIS_step_difference_m']=max(float(x['max_antarctic_step_difference_m']) for x in r)
assert checks['AIS_step_difference_m']<1e-5
r=rows('sea_level_stratified_endpoints.csv');assert len(r)==2500
assert len(set((x['sample'],x['forcing_rule'],x['variant']) for x in r))==2500
for x in r:
    t=float(x['warming2100_K']);assert int(x['warming_bin'])==1+sum(t>b for b in (1.5,2.5,3.5))
    assert all(math.isfinite(float(x[f])) for f in ('total2100_m','total2150_m','antarctic2100_m','thermal2100_m'))
r=rows('sea_level_reference_offsets.csv');assert len(r)==1250
checks['reference_period_closure_m']=max(abs(float(x['mean_after_rebasing_m'])) for x in r)
assert checks['reference_period_closure_m']<1e-12
r=rows('coastal_coupled_pilot_refinement.csv');assert len(r)==12
assert all(x['same_policy']=='true' for x in r)
checks['coastal_pilot_quadrature_relative_difference']=max(float(x['relative_quadrature_difference']) for x in r)
assert checks['coastal_pilot_quadrature_relative_difference']<1e-6
v=json.loads((ROOT/'results/coastal_sampling_validation.json').read_text())['validation']
assert all(abs(x['bias_MC_standard_errors'])<3.5 for x in v)
assert all(.9<x['empirical_to_mean_estimated_variance']<1.1 for x in v)
checks['sampling_normal_interval_coverage_range']=[min(x['normal_95_interval_coverage'] for x in v),max(x['normal_95_interval_coverage'] for x in v)]
g=rows('coastal_coupled_global.csv');regional=rows('coastal_coupled_regional.csv')
assert len(g)==250 and len(regional)==2000
residuals=[]
for x in g:
    parts=[r for r in regional if r['sample']==x['sample']];assert len(parts)==8
    total=sum(float(r['incremental_NPV_USD2019PPP']) for r in parts)
    residuals.append(abs(total-float(x['incremental_NPV_USD2019PPP']))/max(1,abs(total)))
    variance=sum(float(r['sampling_SE_USD2019PPP'])**2 for r in parts)
    assert math.isclose(variance,float(x['sampling_SE_USD2019PPP'])**2,rel_tol=1e-12)
    for field in ('planned_migrants','incremental_planned_migrants'):
        assert math.isclose(sum(float(r[field]) for r in parts),float(x[field]),rel_tol=1e-12,abs_tol=1e-6)
assert max(residuals)<1e-12
checks['coastal_regional_sum_relative_residual']=max(residuals)
checks['completed_coupled_coastal_members']=250
checks['scope']='Saved alternative experiments and numerical pilots; not target reproduction validation'
(ROOT/'results/coupled_verification.json').write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
print(json.dumps(checks,indent=2,sort_keys=True))
