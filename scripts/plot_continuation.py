"""Figures of independent mechanism tests and explicit non-reproduction experiments."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,
                     'pdf.fonttype':42,'figure.dpi':120})
def read(name):
    return np.genfromtxt(str(ROOT/'results'/name),delimiter=',',names=True,dtype=None,encoding=None)
def save(fig,name):
    fig.tight_layout(rect=(0,0,1,.96))
    for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/(name+'.'+ext)),bbox_inches='tight')
    plt.close(fig)
def ribbon(ax,x,lo,mid,hi,color,label):
    ax.fill_between(x,lo,hi,color=color,alpha=.16,linewidth=0)
    ax.plot(x,mid,color=color,label=label,lw=1.4)

metrics={}
ar6={'ssp119':(1.,1.4,1.8),'ssp126':(1.3,1.8,2.4),'ssp245':(2.1,2.7,3.5),
     'ssp370':(2.8,3.6,4.6),'ssp585':(3.3,4.4,5.7)}
# These are printed assessment-table numbers, not digitized curves or inputs
# to calibration: IPCC AR6 WGI Table SPM.1 / SYR 2023 footnote 113.
comparison=[]
for stem,title in [('climate','Temperature-only calibration'),('climate_joint','Temperature + upper-ocean heat calibration')]:
    if not (ROOT/'results'/(stem+'_scenario_quantiles.csv')).exists():continue
    hist=read(stem+'_hindcast.csv');hold=read(stem+'_holdout.csv');heat=read(stem+'_heat_check.csv')
    fig,axes=plt.subplots(2,2,figsize=(9,6.4))
    fig.suptitle(title+' — alternative, not Wong reproduction',fontsize=12)
    a=axes[0,0];ribbon(a,hist['year'],hist['parameter_q05_K'],hist['parameter_median_K'],hist['parameter_q95_K'],'#0072B2','Parameter 90% interval')
    a.plot(hist['year'],hist['observed_K'],color='.2',lw=.8,label='HadCRUT4')
    a.axvline(2005,color='.4',ls=':',lw=.8);a.set(xlabel='Year',ylabel='Temperature anomaly (K; 1961–1990)',title='Fit ends in 2005');a.legend(fontsize=7)
    a=axes[0,1];ribbon(a,hold['year'],hold['predictive_q05_K'],hold['predictive_median_K'],hold['predictive_q95_K'],'#0072B2','Predictive 90% interval')
    a.plot(hold['year'],hold['observed_K'],'o',ms=3,color='.15',label='Held out');a.set(xlabel='Year',ylabel='Temperature anomaly (K)',title='Conditional forecast, 2006–2021');a.legend(fontsize=7)
    a=axes[1,0];scenario=read(stem+'_scenario_quantiles.csv')
    colors=['#56B4E9','#009E73','#E69F00','#D55E00','#CC79A7','#882255']
    for s,c in zip(['ssp119','ssp126','ssp245','ssp370','ssp460','ssp585'],colors):
        d=scenario[(scenario['scenario']==s)&(scenario['year']>=2000)]
        ribbon(a,d['year'],d['q05_K'],d['median_K'],d['q95_K'],c,s.upper())
    a.set(xlabel='Year',ylabel='Warming (K; 1850–1900)',title='Prescribed SSP forcing; 1,000 joint draws');a.legend(ncol=2,fontsize=7)
    a=axes[1,1];ribbon(a,heat['year'],heat['q05_1e22J'],heat['median_1e22J'],heat['q95_1e22J'],'#D55E00','Parameter 90% interval')
    a.errorbar(heat['year'],heat['observed_1e22J'],yerr=heat['obs_se_1e22J'],color='.2',lw=.6,label='NOAA ±1 SE')
    a.axvline(2005,color='.4',ls=':',lw=.8);a.set(xlabel='Year',ylabel='0–700 m ocean heat ($10^{22}$ J)',title='Depth-matched heat check');a.legend(fontsize=7)
    save(fig,stem+'_alternative')
    e=hold['predictive_median_K']-hold['observed_K']
    hp=heat['year']>2005
    he=heat['median_1e22J'][hp]-heat['observed_1e22J'][hp]
    metrics[stem]=dict(temperature_holdout_rmse_K=float(np.sqrt(np.mean(e*e))),
        temperature_holdout_mean_bias_K=float(np.mean(e)),
        temperature_holdout_predictive_90_coverage=float(np.mean((hold['observed_K']>=hold['predictive_q05_K'])&(hold['observed_K']<=hold['predictive_q95_K']))),
        heat_holdout_parameter_median_rmse_1e22J=float(np.sqrt(np.mean(he*he))),
        heat_holdout_parameter_median_bias_1e22J=float(np.mean(he)))
    hpfile=ROOT/'results'/(stem+'_heat_holdout.csv')
    if hpfile.exists():
        d=read(stem+'_heat_holdout.csv');er=d['predictive_median_1e22J']-d['observed_1e22J']
        metrics[stem].update(heat_holdout_predictive_rmse_1e22J=float(np.sqrt(np.mean(er*er))),
            heat_holdout_predictive_90_coverage=float(np.mean((d['observed_1e22J']>=d['predictive_q05_1e22J'])&(d['observed_1e22J']<=d['predictive_q95_1e22J']))))
    counts=read(stem+'_sample_convergence.csv')
    for row in counts[counts['n']==1000]:
        if row['scenario'] in ar6:
            ref=ar6[row['scenario']]
            comparison.append([stem,row['scenario'],row['q05_2081_2100_K'],row['median_2081_2100_K'],row['q95_2081_2100_K']]+list(ref)+[row['median_2081_2100_K']-ref[1]])

x=read('carbon_historical_sensitivity.csv');future=read('carbon_emission_scenarios.csv')
co2=np.genfromtxt(str(ROOT/'inputs/noaa_co2.csv'),delimiter=',',names=True)
fig,axes=plt.subplots(1,3,figsize=(11,3.6));fig.suptitle('Carbon–climate closure: uncalibrated alternatives, not Wong results',fontsize=12)
for beta,color in zip([.15,.287,.6],['#D55E00','#0072B2','#009E73']):
    for early,style in [(0.,'-'),(.72141,'--')]:
        d=x[(x['beta']==beta)&(x['q10']==2)&(x['pre1850_land_use_GtC_yr']==early)]
        axes[0].plot(d['year'],d['co2_ppm'],style,color=color,label=r'$\beta={}$'.format(beta) if early==0 else None)
axes[0].plot(co2['year'],co2['co2_ppm'],color='black',lw=1.2,label='NOAA')
axes[0].set(xlim=(1950,2022),xlabel='Year',ylabel='CO$_2$ (ppm)',title='Early land-use input: 0 (solid), 0.72 (dashed)');axes[0].legend(fontsize=7)
for peak,color in zip([2035,2070,2100],['#009E73','#E69F00','#D55E00']):
    d=future[future['peak_year']==peak]
    axes[1].plot(d['year'],d['emissions_GtCO2_yr'],color=color,label=str(peak))
    axes[2].plot(d['year'],d['temperature_relative1850_1900_K'],color=color,label=str(peak))
axes[1].set(xlabel='Year',ylabel='Emissions (Gt CO$_2$ yr$^{-1}$)',title='Documented recurrence; prescribed peak year');axes[1].legend(fontsize=7)
axes[2].set(xlabel='Year',ylabel='Warming (K; 1850–1900)',title='Fixed SSP2-4.5 non-CO$_2$ forcing');save(fig,'carbon_alternative')
metrics['carbon']=dict(max_mass_balance_error_GtC=float(np.max(abs(x['carbon_balance_error_GtC']))),
    baseline_2022_co2_ppm=float(x[(x['year']==2022)&(x['pre1850_land_use_GtC_yr']==0)&(x['beta']==.287)&(x['q10']==2)]['co2_ppm'][0]),
    observed_2022_co2_ppm=float(co2[co2['year']==2022]['co2_ppm'][0]))

x=read('thermal_observation_prediction.csv');fits=read('thermal_observation_fit.csv')
fig,axes=plt.subplots(1,2,figsize=(8,3.7));fig.suptitle('Observed heat–thermosteric relation: alternative coefficient check',fontsize=12)
for a,depth,color in zip(axes,[700,2000],['#0072B2','#D55E00']):
    d=x[x['depth_m']==depth];p=fits[fits['depth_m']==depth][0]
    train=d['training'].astype(str)=='True';held=(~train)&(d['year_midpoint']<2022)
    a.plot(d['heat_1e22J'][train],d['observed_mm'][train],'o',ms=3,color=color,label='Fit')
    a.plot(d['heat_1e22J'][held],d['observed_mm'][held],'x',color='.2',label='Held out through 2021')
    order=np.argsort(d['heat_1e22J']);a.plot(d['heat_1e22J'][order],d['predicted_mm'][order],color=color,lw=1)
    a.set(xlabel='Ocean heat ($10^{22}$ J)',ylabel='Thermosteric sea level (mm)',title='0–{} m; coefficient {:.3f} × 10$^{{-25}}$ m/J'.format(depth,p['coefficient_m_J']/1e-25));a.legend(fontsize=7)
save(fig,'thermal_observations')

x=read('dais_event_warming.csv');old=read('dais_warming_sensitivity.csv');conv=read('climate_grid_convergence.csv')
fig,axes=plt.subplots(1,2,figsize=(8,3.7));fig.suptitle('Mechanism verification and Antarctic runoff sensitivity',fontsize=12)
for warming,color in zip([0.,2.,4.,6.],['.3','#0072B2','#E69F00','#D55E00']):
    d=x[x['antarctic_warming_K']==warming];alt=old[(old['antarctic_warming_K']==warming)&(old['runoff_rule']=='local_height')]
    axes[0].plot(d['year'],d['mass_equivalent_sea_level_m'],color=color,label='{} K'.format(int(warming)))
    axes[0].plot(alt['year'],alt['mass_equivalent_sea_level_m'],'--',color=color,lw=.8)
axes[0].set(xlabel='Years after forcing starts',ylabel='Mass-equivalent sea level (m)',title='Paper gate (solid); local-height gate (dashed)');axes[0].legend(fontsize=7)
err=np.abs(conv['temperature_year70_K'][:-1]-conv['temperature_year70_K'][1:])
axes[1].loglog(conv['cells'][:-1],err,'o-',color='#0072B2');axes[1].set(xlabel='Ocean cells',ylabel='Difference after grid doubling (K)',title='1% CO$_2$/year, temperature at year 70')
save(fig,'recovered_mechanisms')

x=read('coastal_path_sensitivity.csv');annual=read('coastal_annual_paths.csv')
fig,axes=plt.subplots(1,2,figsize=(8,3.7))
fig.suptitle('Synthetic coastal decisions: alternatives, not global Wong costs',fontsize=11)
for income,color in zip([5000.,15000.,40000.],['#0072B2','#E69F00','#D55E00']):
    for rule,style in [('literal','-'),('physical','--')]:
        d=x[(x['income2010_USD']==income)&(x['land_rule']==rule)&(x['maintenance_rule']=='linear')]
        axes[0].plot(d['sea2150_m'],d['incremental_pv_USD']/1e6,style+'o',color=color,
            label='Income ${:,.0f}'.format(income) if rule=='literal' else None,ms=3)
axes[0].set(xlabel='Sea level in 2150 (m; relative to 2010)',ylabel='Incremental NPV (million 2010 USD)',
            title='Literal land loss (solid); annual loss (dashed)')
axes[0].legend(fontsize=7)
d=annual[(annual['income2010_USD']==15000)&(annual['sea2150_m']==2)]
for name,color in [('construction','#0072B2'),('retreat','#009E73'),('inundation','#E69F00'),('wetland','#CC79A7'),('flood','#D55E00')]:
    axes[1].plot(d['year'],d[name+'_USD']/1e6,color=color,label=name.capitalize(),lw=1)
axes[1].set(xlabel='Year',ylabel='Annual cost (million 2010 USD)',title='Selected retreat; $15,000 income, 2 m rise')
axes[1].legend(fontsize=7)
save(fig,'coastal_alternative')

with (ROOT/'results/alternative_ar6_comparison.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['experiment','scenario','q05_K','median_K','q95_K','ar6_lower_K','ar6_best_K','ar6_upper_K','median_minus_ar6_K']);w.writerows(comparison)
(ROOT/'results/continuation_metrics.json').write_text(json.dumps(metrics,indent=2,sort_keys=True)+'\n')
print('Continuation figures and quantitative validation metrics generated.')
