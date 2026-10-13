"""Tail-sampling and component-budget alternatives, never target projections."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
def read(name):return np.genfromtxt(str(ROOT/name),delimiter=',',names=True,dtype=None,encoding=None)
def save(fig,name):
    fig.tight_layout(rect=(0,0,1,.95))
    for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/(name+'.'+ext)),dpi=150,bbox_inches='tight')
    plt.close(fig)
def wq(x,w,p):
    order=np.argsort(x);s=np.cumsum(w[order]);s/=s[-1]
    return float(x[order[min(len(x)-1,np.searchsorted(s,p,side='left'))]])
families=[('documented_prior','Prior','weight_prior','#0072B2'),('alternative_budget50','50% alternative','weight_budget50','#E69F00'),('alternative_budget75','75% alternative','weight_budget75','#009E73')]
climate=read('results/coupled_emissions_stratified_endpoints.csv')
climate=climate[climate['forcing_rule']=='annual_nearest_emissions']
old=read('results/coupled_emissions_endpoints.csv');old=old[old['forcing_rule']=='annual_nearest_emissions']
q=read('results/sea_level_stratified_quantiles.csv');end=read('results/sea_level_stratified_endpoints.csv')
base=end[(end['forcing_rule']=='annual_nearest_emissions')&(end['variant']=='fit512_shallow_iid')]
assert np.array_equal(base['sample'],climate['sample'])
bins=[]
for family,label,weight,color in families:
    for k in range(1,5):
        mask=base['warming_bin']==k;w=base[weight][mask];t=base['total2100_m'][mask]
        row=dict(distribution=family,warming_bin=k,members=int(mask.sum()),probability=float(w.sum()),
            conditional_effective_sample_size=float(w.sum()**2/np.sum(w*w)) if len(w) else 0.)
        for p,name in [(.05,'q05'),(.5,'q50'),(.95,'q95')]:row['sea2100_'+name+'_m']=wq(t,w,p) if len(w) else None
        bins.append(row)
with (ROOT/'results/sea_level_stratified_bin_summary.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,list(bins[0]));writer.writeheader();writer.writerows(bins)
fig,axes=plt.subplots(2,2,figsize=(10.5,7.6));fig.suptitle('Tail-stratified climate and uncorrected sea-level alternatives')
for family,label,weight,color in families:
    order=np.argsort(climate['temperature2100_K']);w=climate[weight]
    axes[0,0].plot(climate['temperature2100_K'][order],np.cumsum(w[order])/w.sum(),color=color,label=label)
    oo=np.argsort(old['temperature2100_K'])
    axes[0,0].plot(old['temperature2100_K'][oo],np.cumsum(old[weight][oo])/old[weight].sum(),color=color,ls=':',lw=.8)
    d=q[(q['forcing_rule']=='annual_nearest_emissions')&(q['variant']=='fit512_shallow_iid')&(q['distribution']==family)]
    axes[0,1].plot(d['year'],d['q50_m'],color=color,label=label)
    axes[0,1].fill_between(d['year'],d['q05_m'],d['q95_m'],color=color,alpha=.15)
axes[0,0].set(xlabel='Annual warming in 2100 (K)',ylabel='Weighted cumulative probability',title='Solid: 5 strata; dotted: budget-balanced sample');axes[0,0].legend(fontsize=7)
axes[0,1].set(xlabel='Year',ylabel='Sea-level change from 2010 (m)',title='Base closure; median and 5th–95th percentiles');axes[0,1].legend(fontsize=7)
sc=axes[1,0].scatter(base['warming2100_K'],base['total2100_m'],c=base['antarctic2100_m'],s=12+1500*base['weight_budget50'],cmap='viridis',alpha=.8)
for boundary in (1.5,2.5,3.5):axes[1,0].axvline(boundary,color='.6',ls=':',lw=.8)
axes[1,0].set(xlabel='Annual warming in 2100 (K)',ylabel='Sea-level change from 2010 (m)',title='Marker area reflects 50% alternative probability')
fig.colorbar(sc,ax=axes[1,0],label='Antarctic contribution (m)')
variants=[('fit64_shallow_iid','Other AIS point fit'),('fit512_deep_iid','Full-depth coefficient'),('fit512_shallow_common','Common LWS rate'),('fit512_shallow_iid_lagged','Lagged AIS forcing')]
sensitivities={}
for j,(variant,label) in enumerate(variants):
    d=end[(end['forcing_rule']=='annual_nearest_emissions')&(end['variant']==variant)]
    assert np.array_equal(d['sample'],base['sample'])
    delta=d['total2100_m']-base['total2100_m'];w=base['weight_budget50'];qs=[wq(delta,w,p) for p in (.05,.5,.95)]
    axes[1,1].errorbar(qs[1],j,xerr=[[qs[1]-qs[0]],[qs[2]-qs[1]]],fmt='o',color='#D55E00',capsize=3)
    sensitivities[variant]=dict(weighted_q05_m=qs[0],weighted_median_m=qs[1],weighted_q95_m=qs[2],maximum_absolute_difference_m=float(np.max(np.abs(delta))))
axes[1,1].set_yticks(np.arange(4));axes[1,1].set_yticklabels([v[1] for v in variants],fontsize=8)
axes[1,1].axvline(0,color='.4',lw=.7);axes[1,1].set(xlabel='Paired change in 2100 sea level (m)',title='Closure sensitivity; 50% alternative weights')
save(fig,'coupled_sea_level_alternatives')
audit=dict(scope='NON-REPRODUCTION: uncorrected conditional component budget; probability alternatives',
    members=len(base),temperature_counts={str(k):int(np.sum(base['warming_bin']==k)) for k in range(1,5)},
    minimum_warming2100_K=float(base['warming2100_K'].min()),maximum_warming2100_K=float(base['warming2100_K'].max()),
    minimum_sealevel2100_m=float(base['total2100_m'].min()),maximum_sealevel2100_m=float(base['total2100_m'].max()),
    sensitivities=sensitivities)
(ROOT/'results/sea_level_stratified_assessment.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
