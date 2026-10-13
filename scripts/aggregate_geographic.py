"""Curate completed independent coast experiments; preserve all exclusions.
The full coast-by-scenario intermediate remains in .local; country/global
aggregates and the SSP4 1m coast map are small enough to retain in Git.
"""
from pathlib import Path
from collections import defaultdict
import csv,json,hashlib,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(path):
    with (ROOT/path).open() as f:return list(csv.DictReader(f))
def save(path,fields,rows):
    with (ROOT/path).open('w',newline='') as f:
        w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)
raw=ROOT/'.local/geographic_global_costs.csv'
assert (ROOT/'results/geographic_global_run.toml').exists(),'Full run has not completed'
rows=read('.local/geographic_global_costs.csv')
assert len(rows)==9531*6
keys={(r['coast_id'],r['country'],r['scenario'],r['sea2100_m']) for r in rows}
assert len(keys)==len(rows),'Duplicate case'
columns=list(rows[0])[6:]
assert 'baseline_no_adaptation_pv_USD2019PPP' in columns
country=defaultdict(lambda:defaultdict(float));global_cost=defaultdict(lambda:defaultdict(float))
policy=defaultdict(int);accounting=0.;selected_higher=0
for r in rows:
    c=(r['country'],r['scenario'],float(r['sea2100_m']));g=c[1:]
    values={k:float(r[k]) for k in columns}
    assert all(math.isfinite(v) for v in values.values())
    assert all(v>=-1e-6 for k,v in values.items() if k!='incremental_pv_USD2019PPP')
    components=sum(values[k] for k in ('construction_pv','maintenance_pv','retreat_pv','inundation_pv','wetland_pv','flood_pv'))
    accounting=max(accounting,abs(components-values['pv_USD2019PPP'])/max(1.,values['pv_USD2019PPP']))
    assert abs(values['pv_USD2019PPP']-values['baseline_pv_USD2019PPP']-values['incremental_pv_USD2019PPP'])<1e-3
    selected_higher+=values['pv_USD2019PPP']>values['no_adaptation_pv_USD2019PPP']+1e-4
    for k,v in values.items():country[c][k]+=v;global_cost[g][k]+=v
    policy[(g[0],g[1],r['strategy'],r['return_period'])]+=1
assert accounting<1e-12
def records(data,labels):
    return [dict(list(zip(labels,key))+list(value.items())) for key,value in sorted(data.items())]
save('results/geographic_country_costs.csv',['country','scenario','sea2100_m']+columns,records(country,['country','scenario','sea2100_m']))
save('results/geographic_global_costs.csv',['scenario','sea2100_m']+columns,records(global_cost,['scenario','sea2100_m']))
save('results/geographic_policy_counts.csv',['scenario','sea2100_m','strategy','return_period','coasts'],
     [dict(zip(['scenario','sea2100_m','strategy','return_period','coasts'],key+(n,))) for key,n in sorted(policy.items())])
coordinates={}
for r in read('inputs/sliiders_segments.csv'):
    coordinates[(r['coast_id'],r['country'])]=(r['longitude_deg'],r['latitude_deg'])
maps=[]
for r in rows:
    if r['scenario']=='SSP4' and float(r['sea2100_m'])==1:
        lon,lat=coordinates[(r['coast_id'],r['country'])]
        maps.append(dict(coast_id=r['coast_id'],country=r['country'],longitude=lon,latitude=lat,
            incremental_pv_USD2019PPP=r['incremental_pv_USD2019PPP'],strategy=r['strategy'],migrants=r['migrants']))
save('results/geographic_ssp4_1m_map.csv',list(maps[0]),maps)

# Regional ratio uses total national GDP, including landlocked countries,
# and excludes coast-country costs lacking a matching positive GDP input.
metadata={r['country']:r for r in read('inputs/worldbank_regions_gdp.csv')}
gdp=defaultdict(float)
for r in metadata.values():
    if r['gdp2010_USD2019PPP']:gdp[r['region_pre_July2025']]+=float(r['gdp2010_USD2019PPP'])
regional=defaultdict(lambda:defaultdict(float));unmapped=[]
for key,values in country.items():
    c,scenario,sea=key;r=metadata.get(c)
    if r is None or not r['gdp2010_USD2019PPP']:
        unmapped.append(dict(country=c,scenario=scenario,sea2100_m=sea,pv_USD2019PPP=values['pv_USD2019PPP'],incremental_pv_USD2019PPP=values['incremental_pv_USD2019PPP'],reason='country/region missing' if r is None else 'GDP missing'))
        continue
    for k,v in values.items():regional[(r['region_pre_July2025'],scenario,sea)][k]+=v
regional_rows=[]
for (region,scenario,sea),values in sorted(regional.items()):
    global_total=sum(v['incremental_pv_USD2019PPP'] for k,v in regional.items() if k[1:]==(scenario,sea))
    global_fraction=global_total/sum(gdp.values())
    regional_rows.append(dict(region=region,scenario=scenario,sea2100_m=sea,gdp2010_USD2019PPP=gdp[region],
        incremental_pv_USD2019PPP=values['incremental_pv_USD2019PPP'],
        percent_gdp=100*values['incremental_pv_USD2019PPP']/gdp[region],
        minus_global_percentage_points=100*(values['incremental_pv_USD2019PPP']/gdp[region]-global_fraction)))
save('results/geographic_regional_costs.csv',list(regional_rows[0]),regional_rows)
save('results/geographic_regional_exclusions.csv',['country','scenario','sea2100_m','pv_USD2019PPP','incremental_pv_USD2019PPP','reason'],unmapped)
coverage=[]
for (scenario,sea),values in sorted(global_cost.items()):
    omitted=sum(float(r['incremental_pv_USD2019PPP']) for r in unmapped if (r['scenario'],r['sea2100_m'])==(scenario,sea))
    coverage.append(dict(scenario=scenario,sea2100_m=sea,incremental_cost_fraction_covered=1-omitted/values['incremental_pv_USD2019PPP']))
audit=dict(experiment='NON-REPRODUCTION; prescribed uniform SLR, independent SLIIDERS exposure and 2019 PPP',
    cases=len(rows),eligible_coast_country_units=9531,global_aggregation_relative_accounting_error=accounting,
    cases_selected_policy_exceeds_no_adaptation_full_horizon=selected_higher,
    selection_note='First-period optimum retained; whole-horizon cost dominance is not guaranteed',
    full_intermediate_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),regional_coverage=coverage,
    regional_GDP_note='All available WB national 2010 GDP valued at 2019 PPP; landlocked included; input vintage differs from target')
(ROOT/'results/geographic_aggregation_audit.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
