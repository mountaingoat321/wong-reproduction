"""Propagate explicit expert-density alternatives through existing own paths.

All physical trajectories and costs are unchanged. This is a conditional
sensitivity experiment, not a reconstruction of the unspecified target PDF.
"""
from pathlib import Path
import csv, json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from emissions_inversion import expert_density, posterior_weights

def read(path):
    return np.genfromtxt(str(ROOT/path),delimiter=',',names=True,dtype=None,encoding=None)
def write(name,rows):
    with (ROOT/'results'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
def quantile(x,w,p):
    j=np.argsort(x);s=np.cumsum(w[j]);s/=s[-1]
    return float(x[j[min(len(x)-1,np.searchsorted(s,p))]])

draws=read('results/emissions_alternative_samples.csv')
coast=read('results/coastal_coupled_global.csv')
end=read('results/coupled_emissions_stratified_endpoints.csv')
end=end[end['forcing_rule']=='annual_nearest_emissions']
assert np.array_equal(end['sample'],coast['sample'])
ssps=read('inputs/ssp_emissions.csv')
d=ssps[(ssps['scenario']=='ssp460')&(ssps['year']>=2022)&(ssps['year']<=2100)]
assert len(d)==79
mode=float(d['total_GtCO2_yr'].sum())
budget=1223.
allc=draws['cumulative2022_2100_GtCO2']
c=end['cumulative2022_2100_GtCO2']
assert np.allclose(allc[end['emission_sample']-1],c)
cost=coast['incremental_NPV_USD2019PPP']/1e12
weights=[];summaries=[];bins=[]
plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,3,figsize=(13,4.4))
colors=['#0072B2','#009E73','#E69F00','#D55E00']
for j,(a,k) in enumerate([(1,2),(1,4),(2,2),(2,4)]):
    name='beta%d_gamma%d'%(a,k)
    label='Lower Beta(%d,%d); tail Gamma(%d)'%(a,a,k)
    likelihood=expert_density(allc,budget,mode,a,k)
    wfull,zfull=posterior_weights(np.full(len(draws),1/len(draws)),likelihood)
    w,z=posterior_weights(end['weight_prior'],expert_density(c,budget,mode,a,k))
    summaries.append(dict(assessment=name,lower_beta_shape=a,tail_gamma_shape=k,
        expert_budget_probability=.5,conditional_tail_mode_GtCO2=mode,
        prior10000_budget_probability=float(wfull[allc<=budget].sum()),
        propagated250_budget_probability=float(w[c<=budget].sum()),
        prior10000_ESS=float(1/np.sum(wfull*wfull)),propagated250_ESS=float(1/np.sum(w*w)),
        normalizer10000=zfull,normalizer250=z,
        normalizer_relative_difference=z/zfull-1,
        warming_median_K=quantile(end['temperature2100_K'],w,.5),
        sea_level_median_m=quantile(coast['sea2100_m'],w,.5),
        cost_median_trillion2019PPP=quantile(cost,w,.5)))
    for i in range(len(w)):
        weights.append(dict(assessment=name,sample=int(end['sample'][i]),
            emission_sample=int(end['emission_sample'][i]),weight=w[i]))
    x=np.linspace(.01,12000,1500)
    axes[0].plot(x,1000*expert_density(x,budget,mode,a,k),color=colors[j],label=label)
    for b in range(1,5):
        m=coast['warming_bin']==b;v=w[m];q=[quantile(cost[m],v,p) for p in (.05,.5,.95)]
        bins.append(dict(assessment=name,warming_bin=b,members=int(m.sum()),probability=float(v.sum()),
            conditional_ESS=float(v.sum()**2/np.sum(v*v)),cost_q05_trillion2019PPP=q[0],
            cost_median_trillion2019PPP=q[1],cost_q95_trillion2019PPP=q[2]))
        pos=b+(j-1.5)*.14
        axes[1].plot(pos,100*v.sum(),'o',color=colors[j])
        axes[2].errorbar(pos,q[1],yerr=[[q[1]-q[0]],[q[2]-q[1]]],fmt='o',color=colors[j],capsize=2)
axes[0].axvline(budget,color='.5',ls=':');axes[0].axvline(mode,color='.5',ls='--')
axes[0].set(xlabel='Cumulative 2022–2100 CO₂ (Gt)',ylabel='Expert density (per 1000 Gt)',title='Same mass and conditional mode, different shapes')
axes[0].legend(fontsize=6.5)
for ax in axes[1:]:
    ax.set_xticks(range(1,5));ax.set_xticklabels(['≤1.5','1.5–2.5','2.5–3.5','>3.5'],fontsize=8)
    ax.set_xlabel('2100 warming category (°C)')
axes[1].set(ylabel='Posterior probability (%)',title='Prior × expert-density update')
axes[2].set(ylabel='Incremental cost (trillion 2019 USD PPP)',title='Conditional median and 5th–95th percentiles')
fig.suptitle('Non-reproduction: four explicit emissions assessments; same 250 physical/coastal paths')
fig.tight_layout(rect=(0,0,1,.93))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/('emissions_inversion_sensitivity.'+ext)),dpi=150,bbox_inches='tight')
plt.close(fig)
write('emissions_inversion_summary.csv',summaries)
write('emissions_inversion_bin_summary.csv',bins)
write('emissions_inversion_weights.csv',weights)
audit=dict(scope='NON-REPRODUCTION: four chosen expert PDF shapes; prior-times-likelihood method recovered from Fuller2017 writing',
    source_method='https://doi.org/10.1371/journal.pone.0190115, Statistical calibrations',
    SSP460_mode_GtCO2=mode,budget_GtCO2=budget,
    integration='Annual discrete2022–2100sum, consistent with the independent emissions budget definition',
    missing='Darnell2024/2025 and W25 do not specify the expert density family or width',
    normalizer_max_relative_discrepancy=max(abs(x['normalizer_relative_difference']) for x in summaries),
    tail_caution='Only5 physical paths above3.5C; reweighting cannot supply missing tail states',
    significance='50% expert assessment mass is not imposed as50% posterior event probability')
(ROOT/'results/emissions_inversion_assessment.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
