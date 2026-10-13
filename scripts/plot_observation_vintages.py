"""Independent calibration-vintage experiments, including failed diagnostics."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def read(path):return np.genfromtxt(str(ROOT/path),delimiter=',',names=True,dtype=None,encoding=None)
def save(fig,name):
    fig.tight_layout(rect=(0,0,1,.94))
    for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/(name+'.'+ext)),dpi=150,bbox_inches='tight')
    plt.close(fig)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
old=read('inputs/hadcrut4.csv');new=read('inputs/hadcrut5_5010.csv')
fig,axes=plt.subplots(2,2,figsize=(10.5,8));summary=[]
axes[0,0].plot(old['year'],old['anomaly_1961_1990_K'],color='#0072B2',lw=.9,label='HadCRUT4.6.0.0')
axes[0,0].plot(new['year'],new['anomaly_K'],color='#D55E00',lw=.9,label='HadCRUT5.0.1.0')
axes[0,0].axvline(2005,color='.5',ls=':');axes[0,0].legend(fontsize=8)
axes[0,0].set(xlabel='Year',ylabel='Temperature from 1961–1990 (K)',title='Original-provider observation vintages')
for stem,label,color in [('climate_joint','HadCRUT4','#0072B2'),('climate_hadcrut5','HadCRUT5','#D55E00')]:
    status=json.loads((ROOT/'results'/(stem+'_mcmc_status.json')).read_text());assert status['convergence_criteria_met']
    p=read('results/'+stem+'_posterior.csv');h=read('results/'+stem+'_holdout.csv')
    s=read('results/'+stem+'_scenario_quantiles.csv')
    axes[0,1].hist(p['ecs_K'],bins=np.linspace(.5,3,36),density=True,histtype='step',label=label,color=color)
    axes[1,0].plot(h['year'],h['predictive_median_K'],color=color,label=label+' fit')
    axes[1,0].fill_between(h['year'],h['predictive_q05_K'],h['predictive_q95_K'],color=color,alpha=.12)
    d=read('results/'+stem+'_mcmc_diagnostics.csv')
    summary.append(dict(experiment=stem,maximum_Rhat=float(d['rank_folded_rhat'].max()),minimum_bulk_ESS=float(d['bulk_ess'].min()),
        minimum_tail_ESS=float(d['tail_ess'].min()),ECS_median_K=float(np.median(p['ecs_K'])),
        holdout_RMSE_K=float(np.sqrt(np.mean((h['predictive_median_K']-h['observed_K'])**2)))))
    q=s[(s['scenario']=='ssp245')&(s['year']>=2020)&(s['year']<=2100)]
    axes[1,1].plot(q['year'],q['median_K'],color=color,label=label)
    axes[1,1].fill_between(q['year'],q['q05_K'],q['q95_K'],color=color,alpha=.15)
axes[0,1].set(xlabel='Equilibrium climate sensitivity (K)',ylabel='Posterior density',title='Fresh four-chain fits; same 700 m heat likelihood');axes[0,1].legend()
axes[1,0].plot(new['year'][-16:],new['anomaly_K'][-16:],'k.',label='HadCRUT5 observed')
axes[1,0].set(xlabel='Held-out year',ylabel='Temperature from 1961–1990 (K)',title='2006–2021 predictions, including AR(1) errors');axes[1,0].legend(fontsize=8)
axes[1,1].set(xlabel='Year',ylabel='Temperature from 1850–1900 (K)',title='SSP2-4.5: parameter medians and 90% ranges');axes[1,1].legend()
fig.suptitle('Calibration alternatives: documented temperature vintage, restricted likelihood')
save(fig,'observation_vintage_climate')

with (ROOT/'inputs/law_dome2006_calibration.csv').open() as f:
    law_rows=list(csv.DictReader(f))
law={name:np.array([float(r[name]) for r in law_rows]) for name in ('gas_age_CE','co2_ppm')}
mlo=read('inputs/noaa_mlo_co2.csv')
t=read('results/carbon_vintage_trajectories.csv');fits=read('results/carbon_vintage_fits.csv')
fig,axes=plt.subplots(1,2,figsize=(10.5,4.8))
for case,label,color in [('HadCRUT4_MLO_only','Had4; MLO only','#0072B2'),('HadCRUT4_joint','Had4; MLO + Law Dome','#009E73'),('HadCRUT5_joint','Had5; MLO + Law Dome','#D55E00')]:
    d=t[t['case']==case]
    residual=np.interp(law['gas_age_CE'],d['year'],d['co2_ppm'])-law['co2_ppm']
    axes[0].scatter(law['gas_age_CE'],residual,s=9,color=color,alpha=.65,label=label)
    residual=np.interp(mlo['year'],d['year'],d['co2_ppm'])-mlo['co2_ppm']
    axes[1].plot(mlo['year'],residual,color=color,label=label)
for ax in axes:ax.axhline(0,color='.4',lw=.8);ax.set(xlabel='Year',ylabel='Modeled minus observed CO₂ (ppm)')
axes[0].set_title('Irregular Law Dome samples; no age convolution');axes[0].legend(fontsize=8)
axes[1].axvline(2005,color='.5',ls=':');axes[1].set_title('Mauna Loa: 2006–2021 is held out')
fig.suptitle('Failed restricted carbon fits: initial CO₂ and fertilization coefficient only')
save(fig,'observation_vintage_carbon')
audit=dict(scope='NON-REPRODUCTION: observation-vintage sensitivity and restricted carbon point fits',climate=summary,
    carbon_maximum_holdout_RMSE_ppm=float(fits['MLO_holdout_RMSE_ppm'].max()),
    carbon_minimum_holdout_RMSE_ppm=float(fits['MLO_holdout_RMSE_ppm'].min()),
    carbon_boundary_cases=[str(r['case']) for r in fits if str(r['boundary_hit']).lower()=='true'],
    interpretation='HadCRUT5 MCMC passed; failed importance weights and carbon fits are retained, not propagated into the base coastal ensemble')
(ROOT/'results/observation_vintage_assessment.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
