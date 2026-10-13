"""Plots of independently calibrated and geographic NON-REPRODUCTIONS."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.ticker import MaxNLocator
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
def read(name):return np.genfromtxt(str(ROOT/'results'/name),delimiter=',',names=True,dtype=None,encoding=None)
def save(fig,name):
    fig.tight_layout(rect=(0,0,1,.96))
    for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/(name+'.'+ext)),bbox_inches='tight',dpi=150)
    plt.close(fig)
metrics={}
fits=read('carbon_conditional_fit.csv');paths=read('carbon_conditional_trajectories.csv')
fig,axes=plt.subplots(1,3,figsize=(10.5,3.8));fig.suptitle('Conditional carbon fits — alternatives, not SNEASY reproduction',fontsize=12)
for q,color in [(1,'#0072B2'),(2,'#009E73'),(3,'#D55E00')]:
    d=paths[(paths['q10']==q)&(paths['exchange_m_yr']==16.87)]
    axes[0].plot(d['year'],d['co2_ppm'],color=color,label=r'$Q_{10}='+str(q)+'$')
    f=fits[fits['q10']==q]
    axes[1].plot(f['exchange_m_yr'],f['holdout_co2_rmse_ppm'],'o-',color=color,label=str(q))
    axes[2].plot(f['exchange_m_yr'],f['ocean_1994_GtC'],'o-',color=color)
co2=np.genfromtxt(str(ROOT/'inputs/noaa_co2.csv'),delimiter=',',names=True)
axes[0].plot(co2['year'],co2['co2_ppm'],'k--',lw=.8,label='NOAA')
axes[0].axvline(2005,color='.4',ls=':');axes[0].set(xlim=(1979,2021),xlabel='Year',ylabel='CO$_2$ (ppm)',title='Transfer = 16.87 m yr$^{-1}$');axes[0].legend(fontsize=7)
axes[1].set(xlabel='Mixed–thermocline transfer (m yr$^{-1}$)',ylabel='Held-out CO$_2$ RMSE (ppm)',title='2006–2021; fit only 1979–2005')
axes[2].axhspan(99,137,color='.7',alpha=.35,label='Independent 118 ± 19 GtC')
axes[2].axhline(118,color='.4',ls=':');axes[2].set(xlabel='Transfer (m yr$^{-1}$)',ylabel='Ocean uptake through 1994 (Gt C)',title='Ocean inventory not fitted');axes[2].legend(fontsize=7)
save(fig,'carbon_conditional')
metrics['carbon_conditional']=dict(holdout_rmse_min_ppm=float(min(fits['holdout_co2_rmse_ppm'])),
    holdout_rmse_max_ppm=float(max(fits['holdout_co2_rmse_ppm'])),
    max_mass_error_GtC=float(max(fits['max_mass_error_GtC'])),
    max_time_refinement_ppm=float(max(fits['substep_refinement_co2_ppm'])))
if (ROOT/'results/ice_holdout.csv').exists():
    hist=read('ice_hindcast.csv');hold=read('ice_holdout.csv');future=read('ice_scenario_quantiles.csv')
    fig,axes=plt.subplots(2,2,figsize=(9,6.7));fig.suptitle('Conditional ice calibration — alternatives, not BRICK reproduction',fontsize=12)
    for j,component in enumerate(('glaciers','greenland')):
        h=hist[hist['component']==component];d=hold[hold['component']==component];a=axes[0,j]
        a.fill_between(h['year'],h['q05_Gt_yr'],h['q95_Gt_yr'],color='#0072B2',alpha=.18,label='Parameter 90%')
        a.plot(h['year'],h['median_Gt_yr'],color='#0072B2')
        a.errorbar(h['year'],h['observed_loss_Gt_yr'],yerr=h['obs_sd_Gt_yr'],fmt='o',color='.2',ms=2,lw=.6,label='Observation ±1 SD')
        a.fill_between(d['year'],d['predictive_q05_Gt_yr'],d['predictive_q95_Gt_yr'],color='#E69F00',alpha=.18,label='Held-out predictive 90%')
        a.axvline(2014.5,color='.4',ls=':');a.set(xlabel='Year',ylabel='Mass loss (Gt yr$^{-1}$)',title=component.capitalize()+'; observed temperature prescribed');a.legend(fontsize=6)
        a.xaxis.set_major_locator(MaxNLocator(nbins=5,integer=True))
        a=axes[1,j]
        for scenario,color in [('ssp126','#009E73'),('ssp245','#E69F00'),('ssp585','#D55E00')]:
            d=future[(future['component']==component)&(future['scenario']==scenario)]
            a.fill_between(d['year'],d['q05_change_m'],d['q95_change_m'],color=color,alpha=.14)
            a.plot(d['year'],d['median_change_m'],color=color,label=scenario.upper())
        a.set(xlabel='Year',ylabel='Sea-level contribution (m; relative to 2010)',title='1,000 independent climate–ice parameter pairings');a.legend(fontsize=7)
        d=hold[hold['component']==component];error=d['predictive_median_Gt_yr']-d['observed_loss_Gt_yr']
        metrics['ice_'+component]=dict(conditional_holdout_rmse_Gt_yr=float(np.sqrt(np.mean(error**2))),
            conditional_holdout_bias_Gt_yr=float(np.mean(error)),
            predictive_90_coverage=float(np.mean((d['observed_loss_Gt_yr']>=d['predictive_q05_Gt_yr'])&(d['observed_loss_Gt_yr']<=d['predictive_q95_Gt_yr']))))
        training=h[h['year']<=2014]
        for name,forecast in [('training_mean',np.full(d.size,np.mean(training['observed_loss_Gt_yr']))),
                              ('last_training_year',np.full(d.size,training['observed_loss_Gt_yr'][-1])),
                              ('training_linear_trend',np.polyval(np.polyfit(training['year'],training['observed_loss_Gt_yr'],1),d['year']))]:
            metrics['ice_'+component][name+'_holdout_rmse_Gt_yr']=float(np.sqrt(np.mean((forecast-d['observed_loss_Gt_yr'])**2)))
    save(fig,'ice_alternative')
if (ROOT/'results/geographic_global_costs.csv').exists():
    g=read('geographic_global_costs.csv');r=read('geographic_regional_costs.csv');m=read('geographic_ssp4_1m_map.csv')
    fig,axes=plt.subplots(2,2,figsize=(10,7));fig.suptitle('9,531 coast-country units, six elevation bins — not Wong reproduction',fontsize=12)
    for scenario,color in [('SSP2','#0072B2'),('SSP4','#D55E00')]:
        d=g[g['scenario']==scenario]
        axes[0,0].plot(d['sea2100_m'],d['incremental_pv_USD2019PPP']/1e12,'o-',color=color,label=scenario+' selected policy')
        axes[0,0].plot(d['sea2100_m'],(d['no_adaptation_pv_USD2019PPP']-d['baseline_no_adaptation_pv_USD2019PPP'])/1e12,'x--',color=color,label=scenario+' no adaptation')
    axes[0,0].set(xlabel='Prescribed uniform sea-level rise in 2100 (m)',ylabel='Incremental NPV (trillion 2019 USD PPP)',title='2010–2100 cash flows, 4% discount');axes[0,0].legend(fontsize=7)
    axes[0,0].set_yscale('log')
    d=g[(g['scenario']=='SSP4')&(g['sea2100_m']==1)][0]
    labels=['Construct','Maintain','Relocate','Inundate','Wetland','Flood']
    values=[d[k+'_pv']/1e12 for k in ('construction','maintenance','retreat','inundation','wetland','flood')]
    axes[0,1].bar(np.arange(6),values,color=['#0072B2','#56B4E9','#009E73','#E69F00','#CC79A7','#D55E00'])
    axes[0,1].set_xticks(np.arange(6));axes[0,1].set_xticklabels(labels,rotation=25,ha='right')
    axes[0,1].set(ylabel='Total NPV (trillion 2019 USD PPP)',title='SSP4, 1 m; before baseline subtraction')
    mask=m['incremental_pv_USD2019PPP']>0
    sc=axes[1,0].scatter(m['longitude'][mask],m['latitude'][mask],c=m['incremental_pv_USD2019PPP'][mask],s=3,
                         norm=LogNorm(vmin=1e5,vmax=1e10),cmap='viridis',rasterized=True)
    axes[1,0].set(xlim=(-180,180),ylim=(-65,85),xlabel='Longitude (degrees)',ylabel='Latitude (degrees)',title='SSP4, 1 m; positive incremental segment costs')
    fig.colorbar(sc,ax=axes[1,0],label='2019 USD PPP',shrink=.7)
    regions=sorted(set(r['region']))
    short={'East Asia & Pacific':'E. Asia/Pacific','Europe & Central Asia':'Europe/C. Asia','Latin America & Caribbean':'Lat. America/Carib.',
           'Middle East & North Africa':'M. East/N. Africa','North America':'N. America','South Asia':'S. Asia','Sub-Saharan Africa':'Sub-Saharan Afr.'}
    for j,(scenario,color) in enumerate([('SSP2','#0072B2'),('SSP4','#D55E00')]):
        d=r[(r['scenario']==scenario)&(r['sea2100_m']==1)]
        values=[d[d['region']==reg]['minus_global_percentage_points'][0] for reg in regions]
        axes[1,1].barh(np.arange(7)+j*.35,values,height=.35,color=color,label=scenario)
    axes[1,1].set_yticks(np.arange(7)+.175);axes[1,1].set_yticklabels([short[x] for x in regions],fontsize=7)
    axes[1,1].axvline(0,color='.4',lw=.6);axes[1,1].set(xlabel='Regional minus global cost/GDP (percentage points)',title='1 m; alternative GDP input and coverage');axes[1,1].legend(fontsize=7)
    save(fig,'geographic_alternative')
(ROOT/'results/extended_metrics.json').write_text(json.dumps(metrics,indent=2,sort_keys=True)+'\n')
print('Extended non-reproduction figures and metrics saved.')
