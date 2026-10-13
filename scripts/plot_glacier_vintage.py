"""Original observational glacier vintage and conditional point-fit checks."""
from pathlib import Path
import json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def read(name):return np.genfromtxt(str(ROOT/name),delimiter=',',names=True,dtype=None,encoding=None)
op58='--op58' in sys.argv
prefix='glacier_op58' if op58 else 'glacier_vintage'
label='OP58 printed' if op58 else 'NSIDC 2005'
d=read('inputs/dyurgerov_meier2005_op58.csv' if op58 else 'inputs/dyurgerov2005_global.csv')
h=read('results/'+prefix+'_hindcast.csv')
fits=read('results/'+prefix+'_fits.csv')
old=read('results/ice_hindcast.csv');old=old[old['component']=='glaciers']
plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(11,4.8))
axes[0].plot(d['year'],d['sea_level_rate_mm_yr'],'o',ms=3,color='.3',label=label+' global observations')
for name,color in [('HadCRUT4','#0072B2'),('HadCRUT5','#D55E00')]:
    p=h[h['temperature']==name]
    axes[0].plot(p['year'],p['sea_level_rate_mm_yr'],color=color,label=name+' conditional fit')
    metrics=fits[fits['temperature']==name][0]
    axes[1].plot([1,2,3],[metrics['training_RMSE_mm_yr'],metrics['holdout1996_2003_RMSE_mm_yr'],metrics['context2004_2020_RMSE_mm_yr']],'o-',color=color,label=name)
axes[0].plot(old['year'],old['observed_loss_Gt_yr']/362.5,'x',color='#009E73',label='GlaMBIE (different coverage)')
axes[0].axvspan(1995.5,2003.5,color='.6',alpha=.12,label='Withheld observational years')
axes[0].set(xlabel='Year',ylabel='Glacier sea-level contribution (mm/year)',title='1961–1995 fit; later years withheld')
axes[0].legend(fontsize=7)
axes[1].plot(2,fits[0]['holdout_trend_RMSE_mm_yr'],'s',color='.3',label='Training linear-trend baseline')
axes[1].set_xticks([1,2,3]);axes[1].set_xticklabels(['Training\n1961–1995','Same-record holdout\n1996–2003','GlaMBIE context\n2004–2020'],fontsize=8)
axes[1].set(ylabel='Annual rate RMSE (mm/year)',title='Matched-data holdout and separate modern context')
axes[1].legend(fontsize=7)
fig.suptitle('Non-reproduction: original-provider glacier vintage, conditional physical-grid point fits')
fig.tight_layout(rect=(0,0,1,.93))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/(('glacier_op58_fit.' if op58 else 'glacier_observation_vintage.')+ext)),dpi=150,bbox_inches='tight')
plt.close(fig)
overlap=sorted(set(d['year'])&set(old['year']))
diff=[float(d['sea_level_rate_mm_yr'][d['year']==y][0]-old['observed_loss_Gt_yr'][old['year']==y][0]/362.5) for y in overlap]
audit=dict(scope='NON-REPRODUCTION:27conditionalB17physicalgridpoints; scalarbeta fits; fixed1961initialization convention; no posterior',
    observation_overlap_years=[int(y) for y in overlap],DM05_minus_GlaMBIE_overlap_RMSE_mm_yr=float(np.sqrt(np.mean(np.square(diff)))),
    qualification='Observational products differ in coverage and vintage; this difference is not a measurement-error estimate',
    grid_caution='Training minima reachvolume/exponent/initial-state grid boundaries; no inferred global optimum or calibrated uncertainty is claimed')
(ROOT/('results/'+prefix+'_assessment.json')).write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
