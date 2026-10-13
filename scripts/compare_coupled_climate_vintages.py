"""Compare completed HadCRUT4/5 conditional climate and sea-level alternatives."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    return np.genfromtxt(str(ROOT/'results'/name),delimiter=',',names=True,dtype=None,encoding=None)
def quantile(x,w,p):
    j=np.argsort(x);s=np.cumsum(w[j]);s/=s[-1]
    return float(x[j[min(len(x)-1,np.searchsorted(s,p))]])
def write(name,rows):
    with (ROOT/'results'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
measures=['weight_prior','weight_budget50','weight_budget75']
labels=['Prior','50% budget','75% budget']
summary=[];bins=[];audits={};expert_summary=[]
expert_weights=read('emissions_inversion_weights.csv')
assessments=list(dict.fromkeys(expert_weights['assessment']))
climates=[('HadCRUT4 + heat','','#0072B2'),('HadCRUT5 + heat','_hadcrut5','#D55E00'),
          ('HadCRUT4, no heat','_temperature_only','#009E73')]
plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,3,figsize=(13,4.7))
for j,(vintage,suffix,color) in enumerate(climates):
    climate=read('coupled_emissions_stratified'+suffix+'_endpoints.csv')
    sea=read('sea_level_stratified'+suffix+'_endpoints.csv')
    cp=read('coupled_emissions_stratified'+suffix+'_pilot_refinement.csv')
    sp=read('sea_level_stratified'+suffix+'_pilot_refinement.csv')
    assert len(cp)==16 and len(sp)==80
    assert max(cp['max_co2_substep_difference_ppm'])<.001
    assert max(cp['max_temperature_substep_difference_K'])<1e-4
    assert max(sp['max_antarctic_step_difference_m'])<1e-5
    assert max(climate['max_mass_error_GtC'])<1e-8
    d=sea[(sea['forcing_rule']=='annual_nearest_emissions')&(sea['variant']=='fit512_shallow_iid')]
    c=climate[climate['forcing_rule']=='annual_nearest_emissions']
    assert len(c)==len(d)==250 and np.array_equal(c['sample'],d['sample'])
    if j==0:reference_emissions=c['emission_sample'].copy()
    else:assert np.array_equal(reference_emissions,c['emission_sample'])
    audits[vintage]=dict(members=250,max_carbon_mass_error_GtC=float(max(climate['max_mass_error_GtC'])),
        pilot_CO2_max_difference_ppm=float(max(cp['max_co2_substep_difference_ppm'])),
        pilot_temperature_max_difference_K=float(max(cp['max_temperature_substep_difference_K'])),
        pilot_AIS_max_difference_m=float(max(sp['max_antarctic_step_difference_m'])))
    for mi,measure in enumerate(measures):
        w=d[measure]
        assert abs(w.sum()-1)<1e-12
        row=dict(vintage=vintage,distribution=measure)
        for field,key in [('warming2100_K','temperature2100_K'),('total2100_m','sea_level2100_m')]:
            for p,name in [(.05,'q05'),(.5,'median'),(.95,'q95')]:
                row[key+'_'+name]=quantile(d[field],w,p)
        trigger=np.char.lower(d['AIS_fast_trigger_by2100'].astype(str))=='true'
        row['AIS_trigger_probability']=float(w[trigger].sum())
        summary.append(row)
        q=[row['sea_level2100_m_'+name] for name in ('q05','median','q95')]
        axes[2].errorbar(mi+(j-1)*.16,q[1],yerr=[[q[1]-q[0]],[q[2]-q[1]]],fmt='o',color=color,capsize=3,label=vintage if mi==0 else None)
        for b in range(1,5):
            m=d['warming_bin']==b;v=w[m]
            bins.append(dict(vintage=vintage,distribution=measure,warming_bin=b,members=int(m.sum()),
                probability=float(v.sum()),conditional_ESS=float(v.sum()**2/np.sum(v*v)) if len(v) else 0.))
            if measure=='weight_budget50':
                axes[1].bar(b+(j-1)*.26,100*v.sum(),width=.24,color=color,label=vintage if b==1 else None)
    for assessment in assessments:
        e=expert_weights[expert_weights['assessment']==assessment]
        assert np.array_equal(e['sample'],d['sample']) and np.array_equal(e['emission_sample'],c['emission_sample'])
        w=e['weight']
        row=dict(vintage=vintage,assessment=assessment,
            warming_median_K=quantile(d['warming2100_K'],w,.5),
            sea_level_median_m=quantile(d['total2100_m'],w,.5))
        for b in range(1,5):row['bin%d_probability'%b]=float(w[d['warming_bin']==b].sum())
        expert_summary.append(row)
    q=read('coupled_emissions_stratified'+suffix+'_quantiles.csv')
    q=q[(q['forcing_rule']=='annual_nearest_emissions')&(q['distribution']=='alternative_budget50')&(q['year']<=2100)]
    axes[0].plot(q['year'],q['temperature_q50_K'],color=color,label=vintage)
    axes[0].fill_between(q['year'],q['temperature_q05_K'],q['temperature_q95_K'],color=color,alpha=.13)
axes[0].set(xlabel='Year',ylabel='Warming from 1850–1900 (°C)',title='50% alternative: median and 5th–95th')
axes[0].legend(fontsize=8)
axes[1].set_xticks(range(1,5));axes[1].set_xticklabels(['≤1.5','1.5–2.5','2.5–3.5','>3.5'],fontsize=8)
axes[1].set(xlabel='2100 warming category (°C)',ylabel='Probability (%)',title='Same emissions design; fresh climate posterior')
axes[1].legend(fontsize=8)
axes[2].set_xticks(range(3));axes[2].set_xticklabels(labels,fontsize=8)
axes[2].set(ylabel='2100 sea-level change from 2010 (m)',title='Uncorrected sea-level components')
axes[2].legend(fontsize=8)
fig.suptitle('Non-reproduction: climate-data constraints propagated through 250 paths each')
fig.tight_layout(rect=(0,0,1,.93))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/('coupled_climate_vintage_sensitivity.'+ext)),dpi=150,bbox_inches='tight')
plt.close(fig)
write('coupled_climate_vintage_summary.csv',summary)
write('coupled_climate_vintage_bins.csv',bins)
write('coupled_climate_expert_density_summary.csv',expert_summary)
fig,axes=plt.subplots(1,2,figsize=(12,4.1))
for ax,field,label,factor in [(axes[0],'bin4_probability','Probability above 3.5°C (%)',100),
                             (axes[1],'sea_level_median_m','Median 2100 sea-level rise from 2010 (m)',1)]:
    values=np.array([[next(r[field]*factor for r in expert_summary if r['vintage']==v and r['assessment']==a)
                      for a in assessments] for v,_,_ in climates])
    ax.imshow(values,cmap='Blues',aspect='auto',vmin=0,vmax=values.max()*1.4)
    for i in range(3):
        for j in range(4):ax.text(j,i,'%.3f'%values[i,j],ha='center',va='center',fontsize=9)
    ax.set_xticks(range(4));ax.set_xticklabels(['Beta1/Gamma2','Beta1/Gamma4','Beta2/Gamma2','Beta2/Gamma4'],fontsize=7)
    ax.set_yticks(range(3));ax.set_yticklabels([v for v,_,_ in climates],fontsize=8)
    ax.set_title(label)
fig.suptitle('Non-reproduction: recovered inversion method, four assumed expert densities')
fig.tight_layout(rect=(0,0,1,.91))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/('coupled_expert_climate_sensitivity.'+ext)),dpi=150,bbox_inches='tight')
plt.close(fig)
audits['scope']='NON-REPRODUCTION: climate posterior substitution; fixed Had4 carbon hindcast, carbon/AIS point fits, and conditional ice histories'
audits['pairing']='Same emissions and random row indices, not matched physical posterior states; distribution comparison only'
audits['coastal_scope']='Base coastal costs are still the HadCRUT4 experiment; no implicit replacement'
audits['no_heat_scope']='HadCRUT4 temperature-only calibration deliberately omits the700mheat constraint; diagnostic of constraint influence, not recovered target calibration'
(ROOT/'results/coupled_climate_vintage_assessment.json').write_text(json.dumps(audits,indent=2,sort_keys=True)+'\n')
print(json.dumps(audits,indent=2,sort_keys=True))
