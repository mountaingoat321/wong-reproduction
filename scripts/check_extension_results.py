"""Check executed sensitivities without treating alternatives as reproductions."""
from pathlib import Path
import csv,json,math,re
ROOT=Path(__file__).resolve().parents[1]
def rows(name):
    with (ROOT/'results'/name).open() as f:return list(csv.DictReader(f))
def close(a,b):return math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-6)
checks={}
for stem in ['coastal_coupled_ssp2','coastal_coupled_n4','coastal_coupled_n8','coastal_coupled_hadcrut5']:
    g=rows(stem+'_global.csv');r=rows(stem+'_regional.csv')
    assert len(g)==250 and len(r)==2000
    for member in g:
        parts=[v for v in r if v['sample']==member['sample']]
        assert len(parts)==8
        assert close(sum(float(v['incremental_NPV_USD2019PPP']) for v in parts),float(member['incremental_NPV_USD2019PPP']))
        assert close(sum(float(v['sampling_SE_USD2019PPP'])**2 for v in parts),float(member['sampling_SE_USD2019PPP'])**2)
    for weight in ['weight_prior','weight_budget50','weight_budget75']:
        assert abs(sum(float(v[weight]) for v in g)-1)<1e-12
    checks[stem+'_members']=len(g)
for variant in ['ssp2','2150_freeze','2150_growth','geometric','accounting']:
    r=rows('coastal_coupled_'+variant+'_pilot_refinement.csv')
    assert len(r)==12 and all(v['same_policy']=='true' and float(v['relative_quadrature_difference'])<1e-6 for v in r)
checks['additional_coastal_pilot_checks']=60
hp=rows('coastal_coupled_hadcrut5_pilot_refinement.csv')
assert len(hp)>=8 and all(v['same_policy']=='true' and float(v['relative_quadrature_difference'])<1e-6 for v in hp)
checks['HadCRUT5_coastal_pilot_checks']=len(hp)
for suffix in ['_hadcrut5','_temperature_only']:
    c=rows('coupled_emissions_stratified'+suffix+'_endpoints.csv')
    p=rows('coupled_emissions_stratified'+suffix+'_pilot_refinement.csv')
    sea=rows('sea_level_stratified'+suffix+'_endpoints.csv')
    sp=rows('sea_level_stratified'+suffix+'_pilot_refinement.csv')
    assert len(c)==500 and len(p)==16 and len(sea)==2500 and len(sp)==80
    assert max(float(r['max_mass_error_GtC']) for r in c)<1e-8
    assert max(float(r['max_co2_substep_difference_ppm']) for r in p)<.001
    assert max(float(r['max_temperature_substep_difference_K']) for r in p)<1e-4
    assert max(float(r['max_antarctic_step_difference_m']) for r in sp)<1e-5
    for r in sea:
        t=float(r['warming2100_K'])
        assert int(r['warming_bin'])==1+sum(t>b for b in [1.5,2.5,3.5])
        assert all(math.isfinite(float(r[f])) for f in ['total2100_m','total2150_m'])
    offset=rows('sea_level_reference'+suffix+'_offsets.csv')
    assert len(offset)==1250 and max(abs(float(v['mean_after_rebasing_m'])) for v in offset)<1e-12
    checks[suffix[1:]+'_reference_closure_m']=max(abs(float(v['mean_after_rebasing_m'])) for v in offset)
    checks[suffix[1:]+'_carbon_mass_error_GtC']=max(float(r['max_mass_error_GtC']) for r in c)
    checks[suffix[1:]+'_CO2_refinement_ppm']=max(float(r['max_co2_substep_difference_ppm']) for r in p)
inversion=rows('emissions_inversion_weights.csv')
for assessment in set(r['assessment'] for r in inversion):
    w=[float(r['weight']) for r in inversion if r['assessment']==assessment]
    assert len(w)==250 and abs(sum(w)-1)<1e-12 and min(w)>=0
checks['expert_densities']=4
econ=rows('coastal_economic_global.csv');params=rows('coastal_economic_parameters.csv')
assert len(econ)==102 and len(params)==17
bounds={'movefactor':(.5,3),'dvbm':(0,float('inf')),'wvpdl':(0,1),
        'wvel':(0,float('inf')),'vslel':(0,float('inf')),'vslmult':(0,float('inf'))}
for p in params:
    for key,(a,b) in bounds.items():assert a<=float(p[key])<=b
baseline={r['sample']:float(r['incremental_NPV_USD2019PPP']) for r in econ if r['economic_sample']=='0'}
for r in econ:
    assert close(float(r['incremental_NPV_USD2019PPP'])-float(r['difference_from_central_USD2019PPP']),baseline[r['sample']])
er=rows('coastal_economic_refinement.csv')
assert len(er)==68 and all(r['same_policy']=='true' and float(r['relative_quadrature_difference'])<1e-6 for r in er)
checks['economic_prior_draws']=16
carbon=rows('carbon_vintage_free_fits.csv')
fixed={r['case']:float(r['objective']) for r in rows('carbon_vintage_revised_fits.csv')}
assert all(float(r['objective'])<=fixed[r['case']]+1e-8 for r in carbon)
assert len(carbon)==3
assert max(float(r['max_mass_error_GtC']) for r in carbon)<1e-8
assert max(float(r['substep_difference_ppm']) for r in carbon)<.001
checks['carbon_nested_training_objective_check']=True
checks['free_carbon_holdout_RMSE_ppm']={r['case']:float(r['MLO_holdout_RMSE_ppm']) for r in carbon}
glacier=rows('glacier_vintage_grid.csv');assert len(glacier)==54
checks['glacier_conditional_grid_points']=54
ga=json.loads((ROOT/'results/glacier_vintage_input_audit.json').read_text())
assert ga['rows']==43 and ga['cumulative_closure_mm']<1e-11
assert abs(ga['NSIDC_mean1961_2003_mm_yr']-ga['OP58_written_mean1961_2003_mm_yr'])>.1
checks['glacier_source_vintage_mismatch_retained']=True
op=json.loads((ROOT/'results/glacier_op58_input_audit.json').read_text())
assert op['rows']==43 and abs(op['mean1961_2003_mm_yr']-.51)<.005
assert abs(op['mean1994_2003_mm_yr']-.93)<.005
assert op['maximum_rounded_increment_closure_mm']<.010001
assert len(rows('glacier_op58_grid.csv'))==54
checks['OP58_printed_observation_recovered']=True
hindcast=rows('sea_level_hindcast_summary.csv');hp=rows('sea_level_hindcast_pilot_refinement.csv')
assert len(hindcast)==6 and len(hp)==18 and all(int(r['members'])==250 for r in hindcast)
assert max(float(r['heat_80_160_cell_difference_m']) for r in hp)<.001
assert max(float(r['AIS_dt10_dt5_difference_m']) for r in hp)<1e-5
checks['historical_budget_cases']=1500
checks['historical_budget_grid_difference_m']=max(float(r['heat_80_160_cell_difference_m']) for r in hp)
checks['scope']='Numerical/data integrity of declared alternatives; no target-panel reproduction inferred'
(ROOT/'results/extension_verification.json').write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
print(json.dumps(checks,indent=2,sort_keys=True))
