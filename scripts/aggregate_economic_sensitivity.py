"""Design-based totals and paired effects of explicit economic-prior draws."""
from pathlib import Path
from collections import defaultdict
import csv,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from coastal_sampling import total_with_control
pilot='--pilot' in sys.argv
prefix='coastal_economic'+('_pilot' if pilot else '')
def read(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))
def write(name,rows):
    with (ROOT/'results'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
base={int(r['sample']):r for r in read('results/coastal_coupled_pilot_global.csv')}
assert (ROOT/'results'/(prefix+'_run.toml')).exists()
checks=read('results/'+prefix+'_refinement.csv')
assert all(float(r['relative_quadrature_difference'])<1e-6 and r['same_policy']=='true' for r in checks)
if '--from-saved' in sys.argv:
    rows=read('results/'+prefix+'_global.csv')
    for r in rows:
        for key in r:r[key]=float(r[key])
else:
    draws=defaultdict(list)
    for d in read('results/coastal_sampling_design.csv'):
        if int(d['draw'])<=4:draws[d['region']].append(d)
    raw=read('.local/'+prefix+'_cases.csv')
    cases={(int(r['economic_sample']),int(r['sample']),r['coast_id'],r['country']):r for r in raw}
    members=sorted(set(int(r['sample']) for r in raw))
    params=sorted(set(int(r['economic_sample']) for r in raw))
    rows=[];regional=[]
    for es in params:
        for member in members:
            totals=[];variances=[];diffs=[];dvars=[]
            beta=float(base[member]['sea2100_m'])
            for region,ds in sorted(draws.items()):
                data=[cases[es,member,d['coast_id'],d['country']] for d in ds]
                p=np.array([float(d['probability']) for d in ds])
                x=np.array([float(d['auxiliary_coast_cost_USD2019PPP']) for d in ds])
                y=np.array([float(d['incremental_pv_USD2019PPP']) for d in data])
                delta=np.array([float(d['difference_from_central_USD2019PPP']) for d in data])/p
                total,var=total_with_control(y,x,p,float(ds[0]['auxiliary_region_total_USD2019PPP']),beta)
                diff=float(delta.mean());dvar=float(delta.var(ddof=1)/len(delta))
                regional.append(dict(economic_sample=es,sample=member,region=region,
                    incremental_NPV_USD2019PPP=total,sampling_SE_USD2019PPP=var**.5,
                    difference_from_central_USD2019PPP=diff,paired_sampling_SE_USD2019PPP=dvar**.5))
                totals.append(total);variances.append(var);diffs.append(diff);dvars.append(dvar)
            row=dict(economic_sample=es,sample=member,sea2100_m=beta,
                incremental_NPV_USD2019PPP=sum(totals),sampling_SE_USD2019PPP=np.sqrt(sum(variances)),
                difference_from_central_USD2019PPP=sum(diffs),paired_sampling_SE_USD2019PPP=np.sqrt(sum(dvars)))
            ref=float(base[member]['incremental_NPV_USD2019PPP'])
            assert abs(row['incremental_NPV_USD2019PPP']-sum(diffs)-ref)<max(.01,abs(ref)*1e-10)
            if es==0:assert abs(sum(diffs))<1e-6
            rows.append(row)
    write(prefix+'_global.csv',rows);write(prefix+'_regional.csv',regional)
members=sorted(set(int(r['sample']) for r in rows))
plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(10.5,4.8));summary=[]
for j,member in enumerate(members):
    center=next(r for r in rows if int(r['sample'])==member and int(r['economic_sample'])==0)
    d=[r for r in rows if int(r['sample'])==member and int(r['economic_sample'])>0]
    x=center['sea2100_m'];ref=center['incremental_NPV_USD2019PPP']
    y=np.array([r['incremental_NPV_USD2019PPP']/1e12 for r in d])
    z=100*np.array([r['difference_from_central_USD2019PPP'] for r in d])/ref
    axes[0].plot(np.full(len(y),x),y,'.',color='.55',label='Economic draws' if j==0 else None)
    axes[0].plot(x,ref/1e12,'o',color='#D55E00',label='Central parameters' if j==0 else None)
    se=100*np.array([r['paired_sampling_SE_USD2019PPP'] for r in d])/ref
    axes[1].errorbar(np.full(len(z),x),z,yerr=se,fmt='.',alpha=.45,color='#0072B2')
    summary.append(dict(sample=member,sea2100_m=x,economic_draws=len(d),
        central_cost_trillion2019PPP=ref/1e12,minimum_cost_trillion2019PPP=float(y.min()),
        median_cost_trillion2019PPP=float(np.median(y)),maximum_cost_trillion2019PPP=float(y.max()),
        minimum_paired_percent_difference=float(z.min()),maximum_paired_percent_difference=float(z.max()),
        median_paired_sampling_SE_percent=float(np.median(se))))
axes[0].set(xlabel='2100 sea-level change (m)',ylabel='Incremental cost (trillion 2019 USD PPP)',title='Six explicit economic marginal priors')
axes[0].legend(fontsize=8)
axes[1].axhline(0,color='.5',lw=.8)
axes[1].set(xlabel='2100 sea-level change (m)',ylabel='Change from central cost (%)',title='Paired changes ± conditional coast-sampling SE')
fig.suptitle('Non-reproduction: conditional economic uncertainty on purposive climate paths')
fig.tight_layout(rect=(0,0,1,.93))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/(prefix+'_sensitivity.'+ext)),dpi=150,bbox_inches='tight')
plt.close(fig)
write(prefix+'_summary.csv',summary)
audit=dict(scope='NON-REPRODUCTION: four coast draws per region; six independent economic priors applied conditionally to chosen climate paths',
    purpose_paths=len(members),economic_draws=summary[0]['economic_draws'],
    maximum_absolute_paired_percent_difference=max(max(abs(r['minimum_paired_percent_difference']),abs(r['maximum_paired_percent_difference'])) for r in summary),
    caution='Sample ranges are not converged credible intervals; climate paths are purposive; parameter correlations and initial valuation mapping are assumptions')
(ROOT/'results'/(prefix+'_assessment.json')).write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
