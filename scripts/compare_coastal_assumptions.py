"""Paired socioeconomic, interpolation and time-horizon alternatives."""
from pathlib import Path
from collections import defaultdict
import csv,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def read(path):
    with (ROOT/path).open() as f:return list(csv.DictReader(f))
def write(name,rows):
    with (ROOT/'results'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
def q(x,w,p=.5):
    x=np.asarray(x);w=np.asarray(w);i=np.argsort(x);s=np.cumsum(w[i]);s/=s[-1]
    return float(x[i[min(len(x)-1,np.searchsorted(s,p))]])
def save(fig,name):
    fig.tight_layout(rect=(0,0,1,.94))
    for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/(name+'.'+ext)),dpi=150,bbox_inches='tight')
    plt.close(fig)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
experiments=[('ssp2','SSP2 economics'),('2150_freeze','2150, frozen economics'),('2150_growth','2150, continued growth'),('geometric','Geometric interpolation')]
if '--from-saved' in sys.argv:
    records=read('results/coastal_assumption_pilot_comparison.csv')
    for row in records:
        for key in row:
            if key!='experiment':row[key]=float(row[key])
else:
    design=read('results/coastal_sampling_design.csv')
    draws=defaultdict(list)
    for r in design:
        if int(r['draw'])<=4:draws[r['region']].append(r)
    base={(int(r['sample']),r['coast_id'],r['country']):r for r in read('.local/coastal_coupled_pilot_cases.csv')}
    g={int(r['sample']):r for r in read('results/coastal_coupled_pilot_global.csv')}
    records=[]
    for suffix,label in experiments:
        name='coastal_coupled_'+suffix+'_pilot'
        assert (ROOT/'results'/(name+'_run.toml')).exists()
        refined=read('results/'+name+'_refinement.csv')
        assert len(refined)==12 and all(r['same_policy']=='true' and float(r['relative_quadrature_difference'])<1e-6 for r in refined)
        alternative={(int(r['sample']),r['coast_id'],r['country']):r for r in read('.local/'+name+'_cases.csv')}
        for member in sorted(g):
            means=[];variances=[]
            for region,ds in draws.items():
                z=[]
                for d in ds:
                    key=(member,d['coast_id'],d['country'])
                    z.append((float(alternative[key]['incremental_pv_USD2019PPP'])-float(base[key]['incremental_pv_USD2019PPP']))/float(d['probability']))
                means.append(np.mean(z));variances.append(np.var(z,ddof=1)/len(z))
            records.append(dict(experiment=suffix,sample=member,sea2100_m=float(g[member]['sea2100_m']),
                difference_USD2019PPP=sum(means),paired_sampling_SE_USD2019PPP=np.sqrt(sum(variances)),
                percent_of_estimated_baseline=100*sum(means)/float(g[member]['incremental_NPV_USD2019PPP'])))
    write('coastal_assumption_pilot_comparison.csv',records)
fig,axes=plt.subplots(2,2,figsize=(10.5,8))
for ax,(suffix,label) in zip(axes.flat,experiments):
    d=[r for r in records if r['experiment']==suffix]
    ax.errorbar([r['sea2100_m'] for r in d],[r['difference_USD2019PPP']/1e9 for r in d],
        yerr=[r['paired_sampling_SE_USD2019PPP']/1e9 for r in d],fmt='o',capsize=3)
    ax.axhline(0,color='.4',lw=.7);ax.set(xlabel='Sea-level rise in 2100 (m)',ylabel='Paired cost change (billion 2019 PPP)',title=label)
fig.suptitle('Purposive six-path pilots: differences ± conditional coast-sampling SE')
save(fig,'coastal_assumption_pilots')

# Equal coastal sample size and common draws isolate scenario changes.
reg={scenario:read('results/'+stem+'_regional.csv') for scenario,stem in [('SSP4','coastal_coupled_n8'),('SSP2','coastal_coupled_ssp2')]}
global_rows=read('results/coastal_coupled_ssp2_global.csv')
weights={r['sample']:float(r['weight_budget50']) for r in global_rows}
regions=sorted(set(r['region'] for r in reg['SSP2'])-{'Unmapped'})
summaries=[]
for scenario in ('SSP4','SSP2'):
    for region in regions:
        for b in range(1,5):
            d=[r for r in reg[scenario] if r['region']==region and int(r['warming_bin'])==b]
            w=[weights[r['sample']] for r in d]
            summaries.append(dict(scenario=scenario,region=region,warming_bin=b,
                median_percent_GDP=q([float(r['percent_GDP']) for r in d],w),
                median_minus_global_pp=q([float(r['minus_global_percentage_points']) for r in d],w),
                median_sampling_SE_pp=q([100*float(r['sampling_SE_USD2019PPP'])/float(r['GDP2010_USD2019PPP']) for r in d],w)))
write('coastal_socioeconomic_summary.csv',summaries)
fig,axes=plt.subplots(1,2,figsize=(11,5.5),sharey=True)
colors=['#0072B2','#009E73','#E69F00','#D55E00'];labels=['≤1.5°C','1.5–2.5°C','2.5–3.5°C','>3.5°C']
for ax,scenario in zip(axes,('SSP4','SSP2')):
    for b,(color,label) in enumerate(zip(colors,labels),1):
        d=[next(r for r in summaries if r['scenario']==scenario and r['region']==region and r['warming_bin']==b) for region in regions]
        ax.plot([r['median_minus_global_pp'] for r in d],np.arange(7)+(b-2.5)*.14,'o',color=color,label=label)
    ax.axvline(0,color='.4',lw=.7);ax.set(xlabel='Regional minus global cost/GDP (percentage points)',title=scenario+'; same eight coast draws per region')
    ax.set_yticks(range(7));ax.set_yticklabels(regions,fontsize=8);ax.legend(fontsize=7)
fig.suptitle('Alternative warming-conditioned regional burdens; 50% budget weights')
save(fig,'coupled_ssp_comparison')

# Provider population scales are relative to2019. Ratios2100/2010 cancel that
# reference, allowing independent2010 World Bank national populations to anchor.
wb={r['country']:r for r in read('inputs/worldbank_regions_gdp.csv')}
eco={(r['country'],r['scenario'],int(r['year'])):r for r in read('inputs/sliiders_economics.csv') if r['iam']=='OECD'}
income={};coverage=[]
for region in regions:
    for scenario in ('SSP4','SSP2'):
        total_pop=0.;total_gdp=0.;base_pop=0.;available_pop=0.
        for country,r in wb.items():
            if r['region_pre_July2025']!=region or not r['population2010']:continue
            pop=float(r['population2010']);available_pop+=pop
            if (country,scenario,2100) not in eco or (country,scenario,2010) not in eco:continue
            a=eco[country,scenario,2010];z=eco[country,scenario,2100]
            p=pop*float(z['population_scale'])/float(a['population_scale'])
            total_pop+=p;total_gdp+=p*float(z['income_USD2019PPP_person']);base_pop+=pop
        income[region,scenario]=total_gdp/total_pop
        coverage.append(dict(region=region,scenario=scenario,covered_population2010_fraction=base_pop/available_pop,GDPpc2100_USD2019PPP=income[region,scenario]))
write('coastal_regional_income_coverage.csv',coverage)
contrast=[]
for region in regions:
    def value(scenario,b):return next(r['median_percent_GDP'] for r in summaries if r['scenario']==scenario and r['region']==region and r['warming_bin']==b)
    a=value('SSP4',3)-value('SSP4',2);b=value('SSP2',3)-value('SSP2',2)
    contrast.append(dict(region=region,SSP4_minus_SSP2_GDPpc2100_thousand2019PPP=(income[region,'SSP4']-income[region,'SSP2'])/1000,
        SSP4_warming_cost_difference_pp=a,SSP2_warming_cost_difference_pp=b,SSP4_minus_SSP2_warming_cost_difference_pp=a-b))
write('coastal_regional_income_contrast.csv',contrast)
x=np.array([r['SSP4_minus_SSP2_GDPpc2100_thousand2019PPP'] for r in contrast]);y=np.array([r['SSP4_minus_SSP2_warming_cost_difference_pp'] for r in contrast])
slope,intercept=np.polyfit(x,y,1);r2=1-np.sum((y-(slope*x+intercept))**2)/np.sum((y-y.mean())**2)
fig,ax=plt.subplots(figsize=(8.5,5.8));ax.scatter(x,y,color='#0072B2')
abbrev=['EAP','ECA','LAC','MENA','NA','SA','SSA']
for a,b,label in zip(x,y,abbrev):ax.annotate(label,(a,b),xytext=(5,4),textcoords='offset points')
z=np.array([x.min(),x.max()]);ax.plot(z,slope*z+intercept,color='.4',label='Descriptive fit; R²=%.2f'%r2)
ax.set(xlabel='SSP4 − SSP2 regional2100 GDP per person (thousand2019 PPP)',ylabel='SSP4 − SSP2 change in3°C minus2°C cost/GDP (pp)',title='Seven-region alternative: descriptive association, no causal inference')
ax.legend();fig.suptitle('Supplementary9 analogue; unmatched target monetary basis and inputs')
save(fig,'coupled_regional_income_alternative')
audit=dict(scope='NON-REPRODUCTION: same250alternativepaths; fixed economic parameters; uniformSLR; annual2010–2100 and2019PPP',
    regression_definition='SSP4 minusSSP2 of the difference between category3 and category2 median regionalcost/GDP; interpretation fromW25 discussion andSI9',
    regression_slope_pp_per_thousand2019PPP=float(slope),regression_intercept_pp=float(intercept),descriptive_R_squared=float(r2),
    regression_caution='Seven regions, correlated coastal sampling errors and incomplete population coverage; no pvalue or causal claim',
    minimum_covered_population2010_fraction=min(r['covered_population2010_fraction'] for r in coverage),
    horizon_caution='Six deliberately chosen paths; freeze andcontinuedgrowth after2100 are assumptions, not recoveredSSPspecifications')
(ROOT/'results/coastal_socioeconomic_assessment.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
