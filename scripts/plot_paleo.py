"""Antarctic forcing, conditional fits and checks; never target reproductions."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
def read(path):return np.genfromtxt(str(ROOT/path),delimiter=',',names=True,dtype=None,encoding=None)
def save(fig,name):
    fig.tight_layout(rect=(0,0,1,.95))
    for ext in ['pdf','png']:fig.savefig(str(ROOT/'figures'/(name+'.'+ext)),dpi=160,bbox_inches='tight')
    plt.close(fig)
paths=read('results/dais_paleo_trajectories.csv');metrics=read('results/dais_paleo_metrics.csv')
fig,axes=plt.subplots(2,2,figsize=(10.5,7.5))
fig.suptitle('Antarctic paleo hindcasts — alternative forcing, not Wong reproduction')
for name,label in [('alternative','Spratt: youngest value removed'),('forcing_waelbroeck_primary','Waelbroeck: adjusted chronology'),('forcing_waelbroeck_unadjusted','Waelbroeck: unadjusted chronology')]:
    f=read('inputs/dais_'+name+'_forcing.csv' if name=='alternative' else 'inputs/dais_'+name+'.csv')
    keep=(f['year_CE']>=-138000)&(f['year_CE']<=-108000)
    axes[0,0].plot((2000-f['year_CE'][keep])/1000,f['sea_level_m'][keep],label=label)
axes[0,0].set(xlabel='Age (kyr before CE2000)',ylabel='Prescribed global sea level (m)',title='Independent proxy boundary conditions')
axes[0,0].invert_xaxis();axes[0,0].legend(fontsize=7)
for name,label in [('s14_case4','Spratt shifted'),('forcing_spratt_unshifted','Spratt unshifted'),('forcing_waelbroeck_primary','Waelbroeck adjusted'),('forcing_waelbroeck_unadjusted','Waelbroeck unadjusted')]:
    p=paths[paths['experiment']==name];keep=(p['year_CE']>=-138000)&(p['year_CE']<=-108000)
    axes[0,1].plot((2000-p['year_CE'][keep])/1000,p['sea_level_relative1961_1990_m'][keep],label=label)
axes[0,1].errorbar([120],[5.5],yerr=[[1.9],[1.9]],fmt='ks',label='W17F constraint',capsize=3)
axes[0,1].set(xlabel='Age (kyr before CE2000)',ylabel='Antarctic contribution (m)',title='Fixed physical parameters; no fast loss')
axes[0,1].invert_xaxis();axes[0,1].legend(fontsize=7)
for lam in [.005,.01,.015]:
    m=metrics[(metrics['lambda_m_yr']==lam)&np.char.startswith(metrics['experiment'],'fast_0')]
    axes[1,0].plot(m['threshold_degC'],m['LIG_m'],'o-',label='%g mm/yr'%(lam*1000))
axes[1,0].axhspan(3.6,7.4,alpha=.2,color='grey',label='W17F LIG window')
axes[1,0].set(xlabel='Fast-loss temperature threshold (°C)',ylabel='Antarctic contribution at 120 kyr BP (m)',title='Threshold sensitivity; other parameters fixed')
axes[1,0].legend(fontsize=7)
base=paths[paths['experiment']=='s14_case4']
initial={}
for name in ['initial_radius_0.9','initial_radius_1.1']:
    p=paths[paths['experiment']==name];difference=np.abs(p['volume_1e15m3']-base['volume_1e15m3'])*57/24.78
    axes[1,1].semilogy((p['year_CE']+238000)/1000,np.maximum(difference,1e-13),label=name.replace('initial_radius_','Initial radius × '))
    after=p['year_CE']>=-218000
    initial[name]=dict(maximum_SLE_difference_after_20kyr_m=float(difference[after].max()))
axes[1,1].set(xlabel='Elapsed time after initialization (kyr)',ylabel='Absolute SLE difference (m)',title='Initial-radius sensitivity; floor $10^{-13}$ m')
axes[1,1].legend(fontsize=7)
save(fig,'dais_paleo_alternative')
summary=dict(scope='NON-REPRODUCTION: independently reconstructed DAIS with alternative forcing',
    cases=len(metrics),all_windows_pass=int(np.sum(metrics['all_windows_pass'])),initial_radius_sensitivity=initial)
sample_path=ROOT/'results/dais_conditional_samples.csv'
if sample_path.exists():
    samples=read('results/dais_conditional_samples.csv');rates=read('results/dais_conditional_modern_rates.csv')
    obs=read('inputs/ice_mass_balance.csv');obs=obs[obs['component']=='antarctica']
    fig,axes=plt.subplots(1,3,figsize=(11,3.8));fig.suptitle('Conditional Antarctic point fit — not a target posterior')
    point=axes[0].scatter(samples['threshold_degC'],samples['LIG_m'],c=np.log10(np.maximum(samples['window_chisq'],1)),s=12,cmap='viridis')
    axes[0].axhspan(3.6,7.4,color='grey',alpha=.2)
    axes[0].set(xlabel='Fast-loss threshold (°C)',ylabel='LIG Antarctic contribution (m)',title='Independent uniform-prior LHS')
    fig.colorbar(point,ax=axes[0],label='$\log_{10}$ four-window chi-square')
    axes[1].errorbar(obs['start_year'], -obs['mass_change_Gt_yr'],yerr=obs['uncertainty_Gt_yr'],fmt='.',color='black',alpha=.65,label='Independent IMBIE ± SD')
    axes[1].plot(rates['year'],rates['mass_loss_Gt_yr'],label='Conditional point fit')
    axes[1].axvline(2002.5,color='grey',ls=':');axes[1].set(xlim=(1991,2009),xlabel='Year',ylabel='Antarctic mass loss (Gt/yr)',title='Annual rates were not fitted')
    axes[1].legend(fontsize=7)
    residual=[];years=[];observed=[];predicted=[]
    for r in rates:
        o=obs[obs['start_year']==r['year']]
        if r['year']>=2003 and len(o)==1:
            years.append(int(r['year']));observed.append(float(-o['mass_change_Gt_yr'][0]));predicted.append(float(r['mass_loss_Gt_yr']))
            residual.append(predicted[-1]-observed[-1])
    axes[2].bar(years,residual,color='#D55E00');axes[2].axhline(0,color='black',lw=.7)
    axes[2].set(xlabel='Withheld calendar year',ylabel='Model minus observed (Gt/yr)',title='Post-2002 conditional rate check')
    save(fig,'dais_conditional_alternative')
    summary['conditional_rate_holdout']=dict(years=years,RMSE_Gt_yr=float(np.sqrt(np.mean(np.square(residual)))),bias_Gt_yr=float(np.mean(residual)),
        mean_observed_Gt_yr=float(np.mean(observed)),mean_predicted_Gt_yr=float(np.mean(predicted)),
        interpretation='Point-fit conditional hindcast; forcing observed; no posterior intervals or target joint calibration')
    summary['LHS_all_windows_pass']=int(np.sum(samples['all_windows_pass']))
(ROOT/'results/dais_paleo_assessment.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2,sort_keys=True))
