"""Compare completed coast calculations at six-bin and original resolution."""
from pathlib import Path
from collections import Counter
import csv,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def load(path):
    with (ROOT/path).open() as f:
        return {(r['coast_id'],r['country']):r for r in csv.DictReader(f)
                if r['scenario']=='SSP4' and float(r['sea2100_m'])==1}
assert (ROOT/'results/geographic_global_fine_ssp4_1m_run.toml').exists()
coarse=load('.local/geographic_global_costs.csv');fine=load('.local/geographic_global_fine_ssp4_1m_costs.csv')
assert coarse.keys()==fine.keys() and len(fine)==9531
fields=['pv_USD2019PPP','incremental_pv_USD2019PPP','no_adaptation_pv_USD2019PPP','migrants']
rows=[];transitions=Counter();metrics={}
for key in sorted(coarse):
    a=coarse[key];b=fine[key]
    policy_a=a['strategy']+'_'+a['return_period'];policy_b=b['strategy']+'_'+b['return_period']
    transitions[(policy_a,policy_b)]+=1
    row=dict(coast_id=key[0],country=key[1],coarse_policy=policy_a,fine_policy=policy_b)
    for field in fields:
        row['coarse_'+field]=float(a[field]);row['fine_'+field]=float(b[field])
    rows.append(row)
for field in fields:
    a=np.array([r['coarse_'+field] for r in rows]);b=np.array([r['fine_'+field] for r in rows])
    positive=np.abs(a)>1e-8;rel=(b[positive]-a[positive])/a[positive]
    metrics[field]=dict(coarse_sum=float(a.sum()),fine_sum=float(b.sum()),global_relative_change=float(b.sum()/a.sum()-1),
                       median_relative_change=float(np.median(rel)),maximum_absolute_relative_change=float(np.max(np.abs(rel))),
                       relative_change_q05=float(np.percentile(rel,5)),relative_change_q95=float(np.percentile(rel,95)))
changes=sum(n for (a,b),n in transitions.items() if a!=b)
with (ROOT/'results/geographic_full_resolution_comparison.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
with (ROOT/'results/geographic_full_resolution_policy_changes.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['coarse_policy','fine_policy','coast_country_units'])
    for (a,b),n in sorted(transitions.items()):w.writerow([a,b,n])
audit=dict(scope='NON-REPRODUCTION: SSP4, 1m spatially uniform prescribed SLR; all9531eligible coast-country units',
    policy_changes=changes,policy_change_fraction=changes/9531,coarse_bins=6,fine_bins=200,metrics=metrics,
    interpretation='Matched original input totals and all other conventions; resolves within-bin exposure, not target-model specification')
(ROOT/'results/geographic_full_resolution_comparison.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
