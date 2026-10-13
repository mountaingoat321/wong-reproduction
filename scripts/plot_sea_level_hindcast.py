"""Historical component sum checked against observations used in AIS forcing."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def read(s):return np.genfromtxt(str(ROOT/'results'/s),delimiter=',',names=True,dtype=None,encoding=None)
d=read('sea_level_hindcast_quantiles.csv');summary=read('sea_level_hindcast_summary.csv')
pilot=read('sea_level_hindcast_pilot_refinement.csv')
assert len(d)==120 and len(summary)==6 and len(pilot)==18
assert max(pilot['heat_80_160_cell_difference_m'])<.001
assert max(pilot['AIS_dt10_dt5_difference_m'])<1e-5
plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(11,4.7))
for ax,depth in zip(axes,[2000,4057]):
    for name,label,color in [('Had4_heat','HadCRUT4 + heat','#0072B2'),('Had5_heat','HadCRUT5 + heat','#D55E00'),('Had4_noheat','HadCRUT4, no heat','#009E73')]:
        r=d[(d['climate']==name)&(d['heat_depth_m']==depth)]
        ax.plot(r['year'],r['model_median_mm'],color=color,label=label)
        ax.fill_between(r['year'],r['model_q05_mm'],r['model_q95_mm'],color=color,alpha=.12)
    ax.plot(r['year'],r['observed_mm'],'k.-',label='Church–White observations')
    ax.set(xlabel='Year midpoint',ylabel='Sea-level anomaly (mm)',title='Heat integrated to '+('2000 m' if depth==2000 else '4057.5 m'))
    ax.legend(fontsize=7)
fig.suptitle('Non-reproduction: historical budget consistency, not independent validation')
fig.tight_layout(rect=(0,0,1,.93))
for ext in ['pdf','png']:fig.savefig(str(ROOT/'figures'/('sea_level_hindcast_consistency.'+ext)),dpi=150,bbox_inches='tight')
plt.close(fig)
audit=dict(scope='Conditional historical consistency; ChurchWhite is also AIS boundary forcing; no independent holdout',
    reference='Separate1995.5–2004.5 model/observation means',
    intervals='Physical-parameter sample percentiles only; no residual error or observation error added',
    cases=1500,maximum_grid_difference_m=float(max(pilot['heat_80_160_cell_difference_m'])),
    maximum_AIS_step_difference_m=float(max(pilot['AIS_dt10_dt5_difference_m'])))
(ROOT/'results/sea_level_hindcast_assessment.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
