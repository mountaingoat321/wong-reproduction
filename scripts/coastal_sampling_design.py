"""Probability sampling of coasts with a known independent control variate.
This numerical approximation is not the target segmentation or ensemble.
Every coast has positive probability. No convenience sample is extrapolated.
"""
from pathlib import Path
import csv,json
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))
metadata={r['country']:r for r in read('inputs/worldbank_regions_gdp.csv')}
coasts=read('results/geographic_full_resolution_comparison.csv')
groups={}
for r in coasts:
    m=metadata.get(r['country'])
    region=m['region_pre_July2025'] if m and m['gdp2010_USD2019PPP'] else 'Unmapped'
    groups.setdefault(region,[]).append(r)
seed=20251042;rng=np.random.RandomState(seed);draws=[];design={};auxiliary={}
for region,rows in sorted(groups.items()):
    x=np.array([float(r['fine_incremental_pv_USD2019PPP']) for r in rows])
    p=.1/len(x)+.9*np.abs(x)/np.sum(np.abs(x))
    assert np.all(p>0) and abs(p.sum()-1)<1e-12
    selected=rng.choice(len(x),32,replace=True,p=p)
    auxiliary[region]=float(x.sum());design[region]=(rows,x,p)
    for draw,index in enumerate(selected):
        r=rows[index]
        draws.append(dict(region=region,draw=draw+1,coast_id=r['coast_id'],country=r['country'],
            probability=float(p[index]),auxiliary_coast_cost_USD2019PPP=float(x[index]),
            auxiliary_region_total_USD2019PPP=float(x.sum())))
with (ROOT/'results/coastal_sampling_design.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(draws[0]));w.writeheader();w.writerows(draws)

# Validate design bias, estimated variance and normal-interval coverage against
# independently computed exact full-domain totals at three coarse SLR levels.
full=read('.local/geographic_global_costs.csv')
lookup={(r['coast_id'],r['country'],float(r['sea2100_m'])):float(r['incremental_pv_USD2019PPP'])
        for r in full if r['scenario']=='SSP4'}
replicates=5000;validation=[];vrng=np.random.RandomState(seed+1)
for high in (.5,1.,2.):
    exact=sum(lookup[(r['coast_id'],r['country'],high)] for r in coasts)
    for size in (4,16,32,64):
        estimates=np.zeros(replicates);variances=np.zeros(replicates)
        for region,(rows,x,p) in sorted(design.items()):
            y=np.array([lookup[(r['coast_id'],r['country'],high)] for r in rows])
            selected=vrng.choice(len(x),(replicates,size),replace=True,p=p)
            # A known-total control can be scaled by any fixed coefficient
            # without changing unbiasedness. Endpoint scaling reduces noise
            # for low-rise trajectories; no physical linearity is assumed.
            residual=(y[selected]-high*x[selected])/p[selected]
            estimates+=high*x.sum()+residual.mean(axis=1)
            variances+=residual.var(axis=1,ddof=1)/size
        error=estimates-exact
        validation.append(dict(sea2100_m=high,draws_per_region=size,total_draws=size*len(groups),
            exact_cost_USD2019PPP=exact,replicates=replicates,
            relative_bias=float(error.mean()/exact),relative_RMSE=float(np.sqrt(np.mean(error**2))/exact),
            normal_95_interval_coverage=float(np.mean(np.abs(error)<=1.96*np.sqrt(variances))),
            bias_MC_standard_errors=float(error.mean()/(error.std(ddof=1)/np.sqrt(replicates))),
            empirical_to_mean_estimated_variance=float(estimates.var(ddof=1)/variances.mean())))
audit=dict(seed=seed,regions=len(groups),draws=len(draws),eligible_coasts=len(coasts),
    unique_sampled_coasts=len(set((r['coast_id'],r['country']) for r in draws)),
    estimator='Within-region beta*X_total + mean((Y_i-beta*X_i)/p_i), beta=SLR2100/(1m); independent sampling with replacement; sum regional estimates',
    auxiliary='Complete independently calculated200-binSSP4/1m incremental NPV; input totals fixed',
    scope='NON-REPRODUCTION: design-based numerical approximation; finite-sample uncertainty reported separately from climate uncertainty',
    interval_note='Normal intervals are approximate; validation coverage is reported rather than presumed95%',
    validation=validation)
(ROOT/'results/coastal_sampling_validation.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
