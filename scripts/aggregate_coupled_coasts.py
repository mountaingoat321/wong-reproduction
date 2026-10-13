"""Design-based global/regional coastal estimates with sampling uncertainty."""
from pathlib import Path
from collections import defaultdict
import csv,json,sys,re
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from coastal_sampling import total_with_control
pilot='--pilot' in sys.argv
had5='--hadcrut5' in sys.argv
sea_prefix='sea_level_stratified'+('_hadcrut5' if had5 else '')
prefix='coastal_coupled'+('_hadcrut5' if had5 else '')+('_ssp2' if '--ssp2' in sys.argv else '')
for flag,suffix in [('--horizon-freeze','_2150_freeze'),('--horizon-growth','_2150_growth'),('--geometric-economy','_geometric'),('--accounting','_accounting')]:
    if flag in sys.argv:prefix+=suffix
prefix+='_pilot' if pilot else ''
assert (ROOT/'results'/(prefix+'_run.toml')).exists()
def read(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))
def save(name,rows):
    with (ROOT/'results'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
metadata=(ROOT/'results'/(prefix+'_run.toml')).read_text()
perregion=int(re.search(r'^draws_per_region = (\d+)$',metadata,re.M).group(1))
output_prefix=prefix
if '--draws' in sys.argv:
    requested=int(sys.argv[sys.argv.index('--draws')+1]);assert 2<=requested<=perregion and not pilot
    perregion=requested
    output_prefix=prefix+'_n'+str(perregion)
draws=[r for r in read('results/coastal_sampling_design.csv') if int(r['draw'])<=perregion]
draws_by_region=defaultdict(list)
for r in draws:draws_by_region[r['region']].append(r)
meta={r['country']:r for r in read('inputs/worldbank_regions_gdp.csv')}
def region(country):
    m=meta.get(country)
    return m['region_pre_July2025'] if m and m['gdp2010_USD2019PPP'] else 'Unmapped'
gdp=defaultdict(float)
for r in meta.values():
    if r['gdp2010_USD2019PPP']:gdp[r['region_pre_July2025']]+=float(r['gdp2010_USD2019PPP'])
coast=read('results/geographic_full_resolution_comparison.csv')
aux_migrants={(r['coast_id'],r['country']):float(r['fine_migrants']) for r in coast}
aux_region=defaultdict(float)
for r in coast:aux_region[region(r['country'])]+=float(r['fine_migrants'])
paths=read('.local/'+prefix+'_cases.csv')
cases={(int(r['sample']),r['coast_id'],r['country']):r for r in paths}
members=sorted(set(int(r['sample']) for r in paths))
end={int(r['sample']):r for r in read('results/'+sea_prefix+'_endpoints.csv')
     if r['forcing_rule']=='annual_nearest_emissions' and r['variant']=='fit512_shallow_iid'}
global_rows=[];regional_rows=[]
for member in members:
    endpoint=end[member];beta=float(endpoint['total2100_m']);parts=[]
    for name,draw in sorted(draws_by_region.items()):
        p=np.array([float(r['probability']) for r in draw]);n=len(p)
        r=[cases[(member,d['coast_id'],d['country'])] for d in draw]
        x=np.array([float(d['auxiliary_coast_cost_USD2019PPP']) for d in draw])
        y=np.array([float(d['incremental_pv_USD2019PPP']) for d in r])
        estimate,variance=total_with_control(y,x,p,float(draw[0]['auxiliary_region_total_USD2019PPP']),beta)
        # No-adaptation is a direct positive-probability estimator: it does not
        # silently borrow the selected-policy control's known total.
        noadapt=np.array([float(d['no_adaptation_incremental_pv_USD2019PPP']) for d in r])/p
        migration=np.array([float(d['migrants'])-aux_migrants[(d['coast_id'],d['country'])] for d in r])/p
        row=dict(sample=member,region=name,warming2100_K=float(endpoint['warming2100_K']),warming_bin=int(endpoint['warming_bin']),
            sea2100_m=beta,incremental_NPV_USD2019PPP=float(estimate),sampling_SE_USD2019PPP=float(np.sqrt(variance)),
            no_adaptation_incremental_NPV_USD2019PPP=float(noadapt.mean()),no_adaptation_sampling_SE_USD2019PPP=float(noadapt.std(ddof=1)/np.sqrt(n)),
            migrants=float(aux_region[name]+migration.mean()),migration_sampling_SE=float(migration.std(ddof=1)/np.sqrt(n)),
            GDP2010_USD2019PPP=gdp[name] if name!='Unmapped' else None)
        for field in ('planned_migrants','incremental_planned_migrants'):
            z=np.array([float(d[field]) for d in r])/p
            row[field]=float(z.mean());row[field+'_sampling_SE']=float(z.std(ddof=1)/np.sqrt(n))
        parts.append(row)
    covered=sum(r['incremental_NPV_USD2019PPP'] for r in parts if r['region']!='Unmapped')
    covered_gdp=sum(gdp.values())
    for r in parts:
        r['percent_GDP']=100*r['incremental_NPV_USD2019PPP']/r['GDP2010_USD2019PPP'] if r['GDP2010_USD2019PPP'] else None
        r['minus_global_percentage_points']=r['percent_GDP']-100*covered/covered_gdp if r['percent_GDP'] is not None else None
        regional_rows.append(r)
    total=sum(r['incremental_NPV_USD2019PPP'] for r in parts)
    row=dict(sample=member,warming2100_K=float(endpoint['warming2100_K']),warming_bin=int(endpoint['warming_bin']),sea2100_m=beta,
        incremental_NPV_USD2019PPP=total,sampling_SE_USD2019PPP=float(np.sqrt(sum(r['sampling_SE_USD2019PPP']**2 for r in parts))),
        no_adaptation_incremental_NPV_USD2019PPP=sum(r['no_adaptation_incremental_NPV_USD2019PPP'] for r in parts),
        no_adaptation_sampling_SE_USD2019PPP=float(np.sqrt(sum(r['no_adaptation_sampling_SE_USD2019PPP']**2 for r in parts))),
        migrants=sum(r['migrants'] for r in parts),migration_sampling_SE=float(np.sqrt(sum(r['migration_sampling_SE']**2 for r in parts))),
        regional_cost_fraction_covered=covered/total)
    for name in ('weight_prior','weight_budget50','weight_budget75'):row[name]=float(endpoint[name])
    for field in ('planned_migrants','incremental_planned_migrants'):
        row[field]=sum(r[field] for r in parts)
        row[field+'_sampling_SE']=float(np.sqrt(sum(r[field+'_sampling_SE']**2 for r in parts)))
    row['AIS_fast_trigger_by2100']=endpoint['AIS_fast_trigger_by2100']=='true'
    global_rows.append(row)
save(output_prefix+'_global.csv',global_rows);save(output_prefix+'_regional.csv',regional_rows)
audit=dict(scope='NON-REPRODUCTION: spatially uniform coupled alternativeSLR and independent geographic data',
    members=len(global_rows),draws_per_region=perregion,region_strata=len(draws_by_region),
    maximum_relative_cost_sampling_SE=max(r['sampling_SE_USD2019PPP']/abs(r['incremental_NPV_USD2019PPP']) for r in global_rows),
    median_relative_cost_sampling_SE=float(np.median([r['sampling_SE_USD2019PPP']/abs(r['incremental_NPV_USD2019PPP']) for r in global_rows])),
    climate_sample_interpretation='Purposive validation paths; no ensemble probabilities inferred' if pilot else 'All250 tail-stratified alternative members; three separate weighting measures',
    covariance_note='Common coast draws induce correlated numerical errors across climate members; SE is conditional design uncertainty, not climate posterior uncertainty',
    migration_note='Movement counts include initial adaptation; not unique lifetime migrants or solely SLR-attributable displacement')
(ROOT/'results'/(output_prefix+'_audit.json')).write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
