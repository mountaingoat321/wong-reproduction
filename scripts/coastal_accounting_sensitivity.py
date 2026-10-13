"""Reference-cost ambiguity in an annual implementation; purposive pilot only."""
from pathlib import Path
from collections import defaultdict
import csv,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))
fields=[('incremental_pv_USD2019PPP','Paired no-rise difference'),('absolute_pv_USD2019PPP','All annual costs'),
    ('exclude2010_pv_USD2019PPP','Exclude2010 payment'),('exclude2010_2019_pv_USD2019PPP','Exclude2010–2019'),
    ('constant2010_subtracted_pv_USD2019PPP','Subtract2010 payment every year')]
baseline_full=sum(float(r['fine_pv_USD2019PPP'])-float(r['fine_incremental_pv_USD2019PPP']) for r in read('results/geographic_full_resolution_comparison.csv'))
if '--from-saved' in sys.argv:
    records=read('results/coastal_accounting_sensitivity.csv')
    for r in records:
        for key in r:
            if key!='accounting':r[key]=float(r[key])
else:
    design=defaultdict(list)
    for d in read('results/coastal_sampling_design.csv'):
        if int(d['draw'])<=4:design[d['region']].append(d)
    cases={(int(r['sample']),r['coast_id'],r['country']):r for r in read('.local/coastal_coupled_accounting_pilot_cases.csv')}
    global_rows=read('results/coastal_coupled_accounting_pilot_global.csv');records=[]
    for g in global_rows:
        member=int(g['sample']);beta=float(g['sea2100_m'])
        for field,label in fields:
            means=[];variances=[]
            for ds in design.values():
                p=np.array([float(d['probability']) for d in ds])
                x=np.array([float(d['auxiliary_coast_cost_USD2019PPP']) for d in ds])
                y=np.array([float(cases[member,d['coast_id'],d['country']][field]) for d in ds])
                z=(y-beta*x)/p
                means.append(beta*float(ds[0]['auxiliary_region_total_USD2019PPP'])+z.mean())
                variances.append(z.var(ddof=1)/len(z))
            estimate=sum(means);se=np.sqrt(sum(variances))
            if field=='absolute_pv_USD2019PPP':
                # The complete-domain no-rise baseline is already known.
                # Use it as a second exact control rather than re-estimating it.
                estimate=float(g['incremental_NPV_USD2019PPP'])+baseline_full
                se=float(g['sampling_SE_USD2019PPP'])
            if field=='incremental_pv_USD2019PPP':assert np.isclose(estimate,float(g['incremental_NPV_USD2019PPP']))
            records.append(dict(sample=member,sea2100_m=beta,accounting=field,NPV_USD2019PPP=estimate,sampling_SE_USD2019PPP=se))
    with (ROOT/'results/coastal_accounting_sensitivity.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,list(records[0]));w.writeheader();w.writerows(records)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,axes=plt.subplots(1,2,figsize=(11,4.8))
for j,(field,label) in enumerate(fields):
    rows=sorted([r for r in records if r['accounting']==field],key=lambda r:r['sea2100_m'])
    ax=axes[0] if j<4 else axes[1]
    ax.errorbar([r['sea2100_m'] for r in rows],[r['NPV_USD2019PPP']/1e12 for r in rows],
        yerr=[r['sampling_SE_USD2019PPP']/1e12 for r in rows],fmt='o-',capsize=2,label=label)
for ax in axes:
    ax.axhline(0,color='.4',lw=.7);ax.set(xlabel='Sea-level rise in2100 from2010 (m)',ylabel='NPV (trillion2019 USD PPP)');ax.legend(fontsize=8)
axes[0].set_title('Annual bookkeeping alternatives; ± sampling SE')
axes[1].set_title('Rejected literal annual subtraction diagnostic')
fig.suptitle('Same six purposive paths and policies: initial-cost conventions are consequential')
fig.tight_layout(rect=(0,0,1,.93))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/('coastal_accounting_sensitivity.'+ext)),dpi=150,bbox_inches='tight')
audit=dict(scope='NON-REPRODUCTION: fixed annual policies, four regional draws, six purposive paths,2010–2100',
    known_complete_domain_no_rise_baseline_trillion2019PPP=baseline_full/1e12,
    constant_subtraction_caution='The initial annual payment includes upfront capital. Repeating its subtraction confuses one-off investment with recurring rates; this diagnostic is rejected as a target annual mapping.',
    retained_interpretations='Full costs, removal of2010payment, removal of2010–2019payments, and pairedzeroSLRbaseline are distinct accounting conventions; none is asserted identical to target decadal spinup',
    constant_subtraction_minimum_trillion2019PPP=min(r['NPV_USD2019PPP']/1e12 for r in records if r['accounting']==fields[-1][0]))
(ROOT/'results/coastal_accounting_assessment.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
