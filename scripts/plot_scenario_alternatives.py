"""Independent emissions/climate and elevation experiments; no target outputs."""
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
    for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/(name+'.'+ext)),dpi=150,bbox_inches='tight')
    plt.close(fig)
def wq(x,w,p):
    order=np.argsort(x);x=x[order];w=w[order]
    return float(x[min(len(x)-1,np.searchsorted(np.cumsum(w)/w.sum(),p,side='left'))])
families=[('documented_prior','Documented prior','#0072B2','weight_prior'),
          ('alternative_budget50','Alternative 50% budget','#E69F00','weight_budget50'),
          ('alternative_budget75','Alternative 75% budget','#009E73','weight_budget75')]
emissions=read('results/emissions_alternative_samples.csv')
eq=read('results/emissions_alternative_quantiles.csv')
fig,axes=plt.subplots(1,2,figsize=(10,4));fig.suptitle('Documented emissions prior and explicit probability alternatives')
for family,label,color,weight in families:
    d=eq[eq['distribution']==family]
    axes[0].plot(d['year'],d['q50_GtCO2_yr'],label=label,color=color)
    axes[0].fill_between(d['year'],d['q05_GtCO2_yr'],d['q95_GtCO2_yr'],color=color,alpha=.12)
    x=emissions['cumulative2022_2100_GtCO2'];order=np.argsort(x)
    axes[1].plot(x[order]/1000,np.cumsum(emissions[weight][order]),color=color,label=label)
axes[0].set(xlabel='Year',ylabel='Annual CO$_2$ emissions (GtCO$_2$/yr)',title='Median and 5th–95th percentiles; 10,000 draws')
axes[0].legend(fontsize=7)
axes[1].axvline(1.223,color='.4',ls=':',label='1,223 GtCO$_2$ budget')
axes[1].set(xlabel='Cumulative emissions 2022–2100 (TtCO$_2$)',ylabel='Cumulative probability',title='Minimum-information event reweighting',ylim=(0,1),xlim=(0,10))
axes[1].legend(fontsize=7)
save(fig,'emissions_probability_alternatives')

if (ROOT/'results/geographic_full_resolution_comparison.json').exists():
    d=read('results/geographic_full_resolution_comparison.csv')
    coarse=d['coarse_incremental_pv_USD2019PPP']/1e9;fine=d['fine_incremental_pv_USD2019PPP']/1e9
    changes=d['coarse_policy']!=d['fine_policy']
    fig,axes=plt.subplots(1,2,figsize=(10,4));fig.suptitle('All 9,531 coast-country units: alternative geographic resolution test')
    axes[0].scatter(coarse[~changes],fine[~changes],s=4,alpha=.25,label='Same policy',rasterized=True)
    axes[0].scatter(coarse[changes],fine[changes],s=9,alpha=.6,label='Changed policy',color='#D55E00',rasterized=True)
    lo=min(coarse.min(),fine.min());hi=max(coarse.max(),fine.max())
    axes[0].plot([lo,hi],[lo,hi],color='black',lw=.7)
    axes[0].set(xscale='symlog',yscale='symlog',xlabel='Six-bin incremental NPV (billion 2019 USD PPP)',ylabel='Original 0.1 m-bin incremental NPV',title='SSP4, uniform 1 m rise by 2100');axes[0].legend(fontsize=7)
    regions=read('results/geographic_fine_regional_costs.csv');old=read('results/geographic_regional_costs.csv')
    old=old[(old['scenario']=='SSP4')&(old['sea2100_m']==1)]
    order=np.argsort(regions['region']);regions=regions[order]
    labels={'East Asia & Pacific':'E. Asia / Pacific','Europe & Central Asia':'Europe / C. Asia','Latin America & Caribbean':'Lat. America / Carib.',
            'Middle East & North Africa':'M. East / N. Africa','North America':'N. America','South Asia':'S. Asia','Sub-Saharan Africa':'Sub-Saharan Africa'}
    a=np.array([old[old['region']==r]['incremental_pv_USD2019PPP'][0] for r in regions['region']])/1e9
    b=regions['incremental_pv_USD2019PPP']/1e9
    axes[1].barh(np.arange(7)-.17,a,.34,label='Six bins');axes[1].barh(np.arange(7)+.17,b,.34,label='200 bins',color='#D55E00')
    axes[1].set_yticks(np.arange(7));axes[1].set_yticklabels([labels[r] for r in regions['region']],fontsize=7)
    axes[1].set(xlabel='Incremental NPV (billion 2019 USD PPP)',title='Same exposure totals; different within-bin resolution');axes[1].legend(fontsize=7)
    save(fig,'geographic_full_resolution')

if (ROOT/'results/coupled_emissions_run.toml').exists():
    end=read('results/coupled_emissions_endpoints.csv');q=read('results/coupled_emissions_quantiles.csv')
    nearest=end[end['forcing_rule']=='annual_nearest_emissions'];fixed=end[end['forcing_rule']=='fixed_ssp245']
    assert np.array_equal(nearest['sample'],fixed['sample'])
    n=len(nearest);rows=[]
    fig,axes=plt.subplots(2,2,figsize=(10.5,7.5));fig.suptitle('Coupled emissions–carbon–climate alternatives; not target projections')
    for family,label,color,weight in families:
        d=q[(q['forcing_rule']=='annual_nearest_emissions')&(q['distribution']==family)]
        axes[0,0].plot(d['year'],d['temperature_q50_K'],color=color,label=label)
        axes[0,0].fill_between(d['year'],d['temperature_q05_K'],d['temperature_q95_K'],color=color,alpha=.12)
        order=np.argsort(nearest['temperature2100_K']);w=nearest[weight]
        axes[0,1].plot(nearest['temperature2100_K'][order],np.cumsum(w[order])/w.sum(),color=color,label=label)
        for rule in ('annual_nearest_emissions','fixed_ssp245'):
            sample=end[end['forcing_rule']==rule]
            for size in (32,64,128,256):
                if size>n:continue
                s=sample[:size];ws=s[weight];ws=ws/ws.sum();t=s['temperature2100_K']
                bins=np.searchsorted([1.5,2.5,3.5],t,side='left')
                row=dict(forcing_rule=rule,distribution=family,members=size,effective_sample_size=float(1/np.sum(ws**2)))
                for j in range(4):row['bin%d_probability'%(j+1)]=float(ws[bins==j].sum());row['bin%d_members'%(j+1)]=int(np.sum(bins==j))
                for p,name in [(.05,'q05'),(.5,'q50'),(.95,'q95')]:row['temperature2100_'+name+'_K']=wq(t,ws,p)
                rows.append(row)
        r=[r for r in rows if r['forcing_rule']=='annual_nearest_emissions' and r['distribution']==family]
        axes[1,1].plot([a['members'] for a in r],[a['temperature2100_q50_K'] for a in r],'o-',color=color,label=label)
    axes[0,0].set(xlabel='Year',ylabel='Warming relative to 1850–1900 (K)',title='Annual nearest-emissions non-CO$_2$ forcing');axes[0,0].legend(fontsize=7)
    for boundary in (1.5,2.5,3.5):axes[0,1].axvline(boundary,color='.5',lw=.7,ls=':')
    axes[0,1].set(xlabel='Annual warming in 2100 (K)',ylabel='Cumulative weighted probability',title='Target threshold definitions; alternative distributions',ylim=(0,1))
    axes[1,0].scatter(nearest['cumulative2022_2100_GtCO2']/1000,nearest['temperature2100_K']-fixed['temperature2100_K'],s=12,alpha=.65)
    axes[1,0].axhline(0,color='.4',lw=.7)
    axes[1,0].set(xlabel='Cumulative emissions 2022–2100 (TtCO$_2$)',ylabel='Nearest minus fixed SSP2-4.5 warming (K)',title='Paired non-CO$_2$ forcing sensitivity')
    axes[1,1].set(xlabel='Balanced conditional sample size',ylabel='Weighted median warming in 2100 (K)',title='Nested prefixes; not a convergence proof')
    save(fig,'coupled_emissions_alternatives')
    with (ROOT/'results/coupled_emissions_bin_summary.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,list(rows[0]));writer.writeheader();writer.writerows(rows)
    # Restart audit uses the same carbon state for all conditional alternatives.
    pilot=read('results/coupled_emissions_pilot_quantiles.csv')
    co2=float(pilot['co2_q50_ppm'][0]);forcing=read('inputs/ssp_forcing.csv')
    f=forcing[(forcing['scenario']=='ssp245')&(forcing['year']==2021)]
    audit=dict(scope='NON-REPRODUCTION; independent calibration and explicit emissions reweighting',members=n,
        maximum_mass_error_GtC=float(end['max_mass_error_GtC'].max()),
        maximum_paired_2100_nonCO2_temperature_difference_K=float(np.max(np.abs(nearest['temperature2100_K']-fixed['temperature2100_K']))),
        median_SSP_switches=float(np.median(nearest['SSP_switches'])),
        restart_CO2_ppm=co2,restart_CO2_forcing_W_m2=float(3.7*np.log2(co2/280)),
        calibrated_historical_CO2_forcing_W_m2=float(f['co2_W_m2'][0]))
    audit['CO2_forcing_restart_jump_W_m2']=audit['restart_CO2_forcing_W_m2']-audit['calibrated_historical_CO2_forcing_W_m2']
    (ROOT/'results/coupled_emissions_assessment.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
    print(json.dumps(audit,indent=2,sort_keys=True))
