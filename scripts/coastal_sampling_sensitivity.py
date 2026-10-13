"""Numerical sampling diagnostics; not the published 4000/5000 or202/bin tests."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def read(name):return np.genfromtxt(str(ROOT/'results'/name),delimiter=',',names=True,dtype=None,encoding=None)
def q(x,w,p):
    i=np.argsort(x);s=np.cumsum(w[i]);s/=s[-1]
    return float(x[i[min(len(x)-1,np.searchsorted(s,p))]])
def write(name,rows):
    with (ROOT/'results'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
full=read('coastal_coupled_global.csv');w=full['weight_budget50'];cost=full['incremental_NPV_USD2019PPP']/1e12
groups=[np.flatnonzero(full['weight_prior']==v) for v in np.unique(full['weight_prior'])]
assert sorted(map(len,groups))==[10,32,48,64,96]
rng=np.random.RandomState(20251046);replicates=500;records=[];nested=[]
for b in range(1,5):
    mask=full['warming_bin']==b
    for p in (.05,.5,.95):
        records.append(dict(design='Full250',replicate=0,warming_bin=b,probability=p,cost_trillion2019PPP=q(cost[mask],w[mask],p)))
for repeat in range(replicates):
    selected=[];weight=[]
    for g in groups:
        count=int(round(.8*len(g)));ix=rng.choice(g,size=count,replace=False)
        selected.extend(ix);weight.extend(w[ix]*len(g)/count)
    selected=np.array(selected);weight=np.array(weight);assert len(selected)==200 and abs(weight.sum()-1)<1e-12
    for b in range(1,5):
        ix=selected[full['warming_bin'][selected]==b];ww=weight[full['warming_bin'][selected]==b]
        if len(ix):
            for p in (.05,.5,.95):records.append(dict(design='Stratified200',replicate=repeat+1,warming_bin=b,probability=p,cost_trillion2019PPP=q(cost[ix],ww,p)))
        group=np.flatnonzero(full['warming_bin']==b);ix=rng.choice(group,size=5,replace=False)
        for p in (.05,.5,.95):records.append(dict(design='Equal5',replicate=repeat+1,warming_bin=b,probability=p,cost_trillion2019PPP=q(cost[ix],w[ix],p)))
write('coastal_sampling_resamples.csv',records)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,axes=plt.subplots(1,3,figsize=(13,4.6));summaries=[]
for k,design in enumerate(('Stratified200','Equal5')):
    for b in range(1,5):
        for p,color,shift in ((.05,'#0072B2',-.17),(.5,'#009E73',0),(.95,'#D55E00',.17)):
            values=np.array([r['cost_trillion2019PPP'] for r in records if r['design']==design and r['warming_bin']==b and r['probability']==p])
            base=[r['cost_trillion2019PPP'] for r in records if r['design']=='Full250' and r['warming_bin']==b and r['probability']==p][0]
            delta=values-base;a,m,z=np.quantile(delta,[.05,.5,.95])
            axes[k].errorbar(b+shift,m,yerr=[[m-a],[z-m]],fmt='o',color=color,capsize=2,label='q{}'.format(int(p*100)) if b==1 else None)
            summaries.append(dict(design=design,warming_bin=b,probability=p,valid_replicates=len(values),
                q05_difference_trillion2019PPP=a,median_difference_trillion2019PPP=m,q95_difference_trillion2019PPP=z))
    axes[k].set(xlabel='Warming category',ylabel='Subsample minus full quantile (trillion PPP)',title=['200/250, same emissions-stratum masses','Five distinct members per category'][k],xticks=[1,2,3,4])
    axes[k].axhline(0,color='.4',lw=.7);axes[k].legend(fontsize=8)
for size,color in [(4,'#0072B2'),(8,'#E69F00'),(16,'#009E73')]:
    d=full if size==16 else read('coastal_coupled_n%d_global.csv'%size)
    assert np.array_equal(d['sample'],full['sample'])
    for b in range(1,5):
        mask=d['warming_bin']==b;value=q(d['incremental_NPV_USD2019PPP'][mask]/1e12,w[mask],.5)
        nested.append(dict(draws_per_region=size,warming_bin=b,median_trillion2019PPP=value,
            median_relative_sampling_SE=q(d['sampling_SE_USD2019PPP'][mask]/np.abs(d['incremental_NPV_USD2019PPP'][mask]),w[mask],.5)))
    axes[2].plot(range(1,5),[r['median_trillion2019PPP'] for r in nested if r['draws_per_region']==size],'o-',color=color,label=str(size)+' draws/region')
axes[2].set(xlabel='Warming category',ylabel='Weighted median NPV (trillion 2019 PPP)',title='Nested coastal probability samples',xticks=[1,2,3,4]);axes[2].legend(fontsize=8)
fig.suptitle('Non-reproduction sampling tests: coast estimates held fixed in climate subsampling',fontsize=12)
fig.tight_layout(rect=(0,0,1,.93))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/('coupled_sampling_sensitivity.'+ext)),dpi=150,bbox_inches='tight')
write('coastal_sampling_resample_summary.csv',summaries);write('coastal_nested_sample_summary.csv',nested)
audit=dict(seed=20251046,replicates=replicates,scope='NON-REPRODUCTION: finite retained alternative ensemble; not5000vs4000 or202independentmembersperbin',
    high_bin_caution='Equal5 keeps all5 high-bin members; zero resampling change in that category does not establish tail convergence',
    sampling_caution='Nested coast samples are dependent; this is a numerical sensitivity, not proof of convergence',
    maximum_median_change_8_to_16_trillion2019PPP=max(abs(nested[4+b]['median_trillion2019PPP']-nested[8+b]['median_trillion2019PPP']) for b in range(4)))
(ROOT/'results/coastal_sampling_sensitivity.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
