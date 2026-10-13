"""Datum-consistent contextual comparison, not an SSP-matched reproduction."""
from pathlib import Path
import csv,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def rows(name):
    with (ROOT/name).open() as f:return list(csv.DictReader(f))
def quantile(x,w,p):
    j=np.argsort(x);q=np.cumsum(w[j]);q/=q[-1]
    return float(x[j[min(len(x)-1,np.searchsorted(q,p))]])
offset={int(r['sample']):float(r['datum_shift_m']) for r in rows('results/sea_level_reference_offsets.csv') if r['variant']=='fit512_shallow_iid'}
end=[r for r in rows('results/sea_level_stratified_endpoints.csv') if r['variant']=='fit512_shallow_iid' and r['forcing_rule']=='annual_nearest_emissions']
years=np.arange(2010,2151)
saved='--from-saved' in sys.argv
if saved:
    saved_rows=rows('results/sea_level_referenced_quantiles.csv')
else:
    paths=np.full((len(end),len(years)),np.nan)
    with (ROOT/'.local/sea_level_stratified_paths.csv').open() as f:
        for r in csv.DictReader(f):
            if r['variant']=='fit512_shallow_iid' and r['forcing_rule']=='annual_nearest_emissions':
                j=int(r['sample']);year=int(float(r['year']))
                paths[j-1,year-2010]=float(r['total_m'])+offset[j]
    assert np.isfinite(paths).all()
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,axes=plt.subplots(1,2,figsize=(10,4.4));output=[];summaries=[]
for i,(name,label,color) in enumerate([('weight_prior','Prior','#0072B2'),('weight_budget50','50% alternative','#E69F00'),('weight_budget75','75% alternative','#009E73')]):
    if saved:
        selected=[r for r in saved_rows if r['distribution']==name]
        assert [int(r['year']) for r in selected]==list(years)
        q=np.array([[float(r[k]) for k in ('q17_m','median_m','q83_m')] for r in selected])
    else:
        w=np.array([float(r[name]) for r in end]);q=np.array([[quantile(paths[:,k],w,p) for p in (.17,.5,.83)] for k in range(len(years))])
    axes[0].plot(years,q[:,1],color=color,label=label)
    axes[0].fill_between(years,q[:,0],q[:,2],color=color,alpha=.2)
    z=q[90];axes[1].errorbar(z[1],i,xerr=[[z[1]-z[0]],[z[2]-z[1]]],fmt='o',color=color,capsize=3)
    summaries.append(dict(distribution=name,q17_m=z[0],median_m=z[1],q83_m=z[2]))
    output.extend(dict(distribution=name,year=int(year),q17_m=a[0],median_m=a[1],q83_m=a[2]) for year,a in zip(years,q))
ar6=rows('config/ar6_sealevel_comparison.csv')
for i,r in enumerate(ar6):
    a,b,c=[float(r[k]) for k in ('q17_m','median_m','q83_m')]
    axes[1].errorbar(b,i+4,xerr=[[b-a],[c-b]],fmt='s',color='.35',capsize=3)
axes[0].set(xlabel='Year',ylabel='Sea level relative to 1995–2014 (m)',title='Uncorrected alternative budget: median and 66% range')
axes[0].legend(fontsize=8)
axes[1].set_yticks(list(range(3))+list(range(4,9)));axes[1].set_yticklabels(['Prior','50% alternative','75% alternative']+[r['scenario'] for r in ar6])
axes[1].set(xlabel='Sea level in 2100 (m)',title='Different emissions experiments; contextual comparison')
fig.suptitle('Independent model datum and written AR6 assessment ranges',fontsize=12)
fig.tight_layout(rect=(0,0,1,.94))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/('sea_level_ar6_context.'+ext)),dpi=150,bbox_inches='tight')
with (ROOT/'results/sea_level_referenced_quantiles.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,list(output[0]));writer.writeheader();writer.writerows(output)
audit=dict(scope='NON-REPRODUCTION: own hindcast datum; uncorrected component overlap; AR6 is contextual, not emissions-matched validation',
    reference='Arithmetic mean of annual1995–2014 model levels',offset_min_m=min(offset.values()),offset_max_m=max(offset.values()),
    alternative2100=summaries,ar6_source='https://www.ipcc.ch/report/ar6/wg1/chapter/chapter-9/',
    source_access='Official indexed Table9.9 checked; direct webpage/PDF downloads returned403; no raw checksum claimed')
(ROOT/'results/sea_level_reference_assessment.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
