"""Separate exposure-resolution sensitivity from flood quadrature error."""
import csv,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/'results'/name).open() as f:return list(csv.DictReader(f))
coarse=read('geographic_pilot_costs.csv');fine=read('geographic_pilot_fine_costs.csv')
assert len(coarse)==len(fine)==114
fields=['pv_USD2019PPP','incremental_pv_USD2019PPP','no_adaptation_pv_USD2019PPP','migrants']
summary={};changes=0;rows=[]
for x,y in zip(coarse,fine):
    assert [x[k] for k in list(x)[:4]]==[y[k] for k in list(y)[:4]]
    changed=any(x[k]!=y[k] for k in ('strategy','return_period'));changes+=changed
    r={k:x[k] for k in list(x)[:4]};r['policy_changed']=changed
    for k in fields:r[k+'_relative_change']=(float(y[k])-float(x[k]))/max(1.,abs(float(x[k])))
    rows.append(r)
for k in fields:
    values=[r[k+'_relative_change'] for r in rows]
    summary[k]=dict(median_relative_change=float(np.median(values)),maximum_absolute_relative_change=float(max(abs(x) for x in values)),
        pilot_sum_relative_change=sum(float(r[k]) for r in fine)/sum(float(r[k]) for r in coarse)-1)
summary.update(cases=len(rows),policy_changes=changes,scope='Six bins vs original0.1m profiles; 19-coast pilot is not extrapolated globally')
refined=read('geographic_pilot_fine_q24_costs.csv')
assert len(refined)==len(fine)
error=0.;policies=0
for x,y in zip(fine,refined):
    assert [x[k] for k in list(x)[:4]]==[y[k] for k in list(y)[:4]]
    policies+=any(x[k]!=y[k] for k in ('strategy','return_period'))
    for k in list(x)[6:]:error=max(error,abs(float(x[k])-float(y[k]))/max(1.,abs(float(y[k]))))
assert error<1e-8 and policies==0
summary['fine_quadrature_maximum_relative_error']=error
summary['fine_quadrature_policy_changes']=policies
(ROOT/'results/geographic_elevation_sensitivity.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
with (ROOT/'results/geographic_elevation_sensitivity.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps(summary,indent=2,sort_keys=True))
