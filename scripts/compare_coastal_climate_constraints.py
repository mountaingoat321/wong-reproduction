"""Matched coast-sampling comparison of independently calibrated climate versions."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def read(n):return np.genfromtxt(str(ROOT/'results'/n),delimiter=',',names=True,dtype=None,encoding=None)
def quantile(x,w,p):
    j=np.argsort(x);c=np.cumsum(w[j]);c/=c[-1]
    return float(x[j[min(len(x)-1,np.searchsorted(c,p))]])
groups=[('HadCRUT4','coastal_coupled_n8','#0072B2'),('HadCRUT5','coastal_coupled_hadcrut5','#D55E00')]
expert=read('emissions_inversion_weights.csv');assessments=list(dict.fromkeys(expert['assessment']))
rows=[];metrics={};plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(11,4.8))
for i,(label,prefix,color) in enumerate(groups):
    g=read(prefix+'_global.csv');assert len(g)==250
    cost=g['incremental_NPV_USD2019PPP']/1e12
    measures=[('Prior',g['weight_prior']),('Budget50',g['weight_budget50']),('Budget75',g['weight_budget75'])]
    for name in assessments:
        e=expert[expert['assessment']==name]
        assert np.array_equal(g['sample'],e['sample'])
        measures.append((name,e['weight']))
    for name,w in measures:
        for b in range(5):
            m=np.ones(len(g),dtype=bool) if b==0 else g['warming_bin']==b
            v=w[m];x=cost[m];q=[quantile(x,v,p) for p in (.05,.5,.95)]
            rows.append(dict(climate=label,distribution=name,warming_bin=b,members=int(m.sum()),probability=float(v.sum()),
                conditional_ESS=float(v.sum()**2/np.sum(v*v)),q05_trillion2019PPP=q[0],median_trillion2019PPP=q[1],q95_trillion2019PPP=q[2]))
            if name=='Budget50' and b>0:
                axes[0].errorbar(b+(i-.5)*.17,q[1],yerr=[[q[1]-q[0]],[q[2]-q[1]]],fmt='o',capsize=3,color=color,label=label if b==1 else None)
    w=g['weight_budget50'];order=np.argsort(cost)
    axes[1].step(cost[order],np.cumsum(w[order])/w.sum(),where='post',color=color,label=label)
    high=g['warming_bin']==4
    metrics[label]=dict(high_warming_members=int(high.sum()),high_warming_probability=float(w[high].sum()),
        high_warming_ESS=float(w[high].sum()**2/np.sum(w[high]**2)),
        median_relative_coastal_sampling_SE=float(np.median(g['sampling_SE_USD2019PPP']/g['incremental_NPV_USD2019PPP'])))
axes[0].set_xticks(range(1,5));axes[0].set_xticklabels(['≤1.5','1.5–2.5','2.5–3.5','>3.5'])
axes[0].set(xlabel='2100 warming category (°C)',ylabel='Incremental NPV (trillion 2019 USD PPP)',title='Conditional medians and 5th–95th percentiles')
axes[1].set(xlabel='Incremental NPV (trillion 2019 USD PPP)',ylabel='Cumulative probability',title='Unconditional alternative 50% budget weights')
for ax in axes:ax.legend(fontsize=8)
fig.suptitle('Non-reproduction: temperature-version substitution; same eight coast draws per region')
fig.tight_layout(rect=(0,0,1,.93))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/('coastal_climate_constraint_comparison.'+ext)),dpi=150,bbox_inches='tight')
plt.close(fig)
with (ROOT/'results/coastal_climate_constraint_summary.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
metrics['scope']='NON-REPRODUCTION: independent climate posteriors, same emissions/coast sampling; distribution comparison, not paired physical posterior draws'
metrics['caution']='Conditional sampling SE is separate from physical variation; finite weighted high tail remains unresolved; fixed carbon/AIS and independent ice marginals'
(ROOT/'results/coastal_climate_constraint_assessment.json').write_text(json.dumps(metrics,indent=2,sort_keys=True)+'\n')
print(json.dumps(metrics,indent=2,sort_keys=True))
