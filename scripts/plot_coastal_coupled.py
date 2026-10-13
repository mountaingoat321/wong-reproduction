"""Independent coupled coastal alternatives, with explicit numerical uncertainty.
These plots are not reproductions of the Wong ensemble, geography or accounting.
"""
from pathlib import Path
import csv,json,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
had5='--hadcrut5' in sys.argv
suffix='_hadcrut5' if had5 else ''
def result_name(name):return name.replace('coastal_coupled','coastal_coupled'+suffix)
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
def read(name):
    return np.genfromtxt(str(ROOT/'results'/result_name(name)),delimiter=',',names=True,dtype=None,encoding=None)
def save(fig,name):
    if had5 and fig._suptitle:fig._suptitle.set_text(fig._suptitle.get_text()+'; HadCRUT5 climate')
    fig.tight_layout(rect=(0,0,1,.94))
    for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/(name+suffix+'.'+ext)),dpi=150,bbox_inches='tight')
    plt.close(fig)
def quantile(x,w,p):
    j=np.argsort(x);s=np.cumsum(w[j]);s/=s[-1]
    return float(x[j[min(len(x)-1,np.searchsorted(s,p))]])
def write(name,rows):
    with (ROOT/'results'/result_name(name)).open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
g=read('coastal_coupled_global.csv');r=read('coastal_coupled_regional.csv')
assert len(g)==250 and len(np.unique(g['sample']))==250
cost=g['incremental_NPV_USD2019PPP']/1e12
sea=g['sea2100_m'].copy();sea_reference='2010'
if had5:
    offsets=read('sea_level_reference_hadcrut5_offsets.csv')
    offsets=offsets[offsets['variant']=='fit512_shallow_iid']
    assert np.array_equal(offsets['sample'],g['sample'])
    sea+=offsets['datum_shift_m'];sea_reference='1995–2014'
    write('coastal_coupled_plot_coordinates.csv',[dict(sample=int(i),sea2100_relative1995_2014_m=float(x)) for i,x in zip(g['sample'],sea)])
labels=['≤1.5°C','1.5–2.5°C','2.5–3.5°C','>3.5°C']
colors=['#0072B2','#009E73','#E69F00','#D55E00']
measures=[('weight_prior','Prior','#0072B2'),('weight_budget50','50% alternative','#E69F00'),('weight_budget75','75% alternative','#009E73')]
summaries=[]
fig,axes=plt.subplots(1,2,figsize=(10.5,4.7))
for k,(weight,label,color) in enumerate(measures):
    for b in range(1,5):
        mask=g['warming_bin']==b;w=g[weight][mask];x=cost[mask]
        q=[quantile(x,w,p) for p in (.05,.5,.95)]
        axes[0].errorbar(b+(k-1)*.16,q[1],yerr=[[q[1]-q[0]],[q[2]-q[1]]],fmt='o',color=color,capsize=3,label=label if b==1 else None)
        summaries.append(dict(distribution=weight,warming_bin=b,members=int(mask.sum()),probability=float(w.sum()),
            conditional_ESS=float(w.sum()**2/np.sum(w*w)),q05_trillion2019PPP=q[0],median_trillion2019PPP=q[1],q95_trillion2019PPP=q[2],
            median_relative_sampling_SE=quantile(g['sampling_SE_USD2019PPP'][mask]/(x*1e12),w,.5)))
axes[0].set_xticks(range(1,5));axes[0].set_xticklabels(labels,fontsize=8)
axes[0].set(ylabel='Incremental NPV (trillion 2019 USD PPP)',title='Weighted medians and 5th–95th percentiles')
axes[0].legend(fontsize=8)
axes[1].scatter(sea,100*g['sampling_SE_USD2019PPP']/g['incremental_NPV_USD2019PPP'],c=[colors[b-1] for b in g['warming_bin']],s=18)
axes[1].set(xlabel='Sea-level rise in 2100 from '+sea_reference+' (m)',ylabel='Conditional coastal sampling SE (%)',title='Numerical error is separate from climate variation')
fig.suptitle('Non-reproduction: SSP4, annual 2010–2100, paired no-rise baseline')
save(fig,'coupled_coastal_cost_alternative');write('coastal_coupled_bin_summary.csv',summaries)

# Scatter and empirical weighted marginals; no smoothed tail density is invented.
fig=plt.figure(figsize=(9,7));gs=fig.add_gridspec(2,2,width_ratios=[4,1],height_ratios=[1,4],hspace=.08,wspace=.08)
joint=fig.add_subplot(gs[1,0]);top=fig.add_subplot(gs[0,0],sharex=joint);right=fig.add_subplot(gs[1,1],sharey=joint)
w=g['weight_budget50'];xbins=np.linspace(0,max(sea)*1.02,22);ybins=np.linspace(0,max(cost)*1.02,22)
for b,(label,color) in enumerate(zip(labels,colors),1):
    m=g['warming_bin']==b;weights=w[m]/w[m].sum()
    joint.scatter(sea[m],cost[m],s=12+1800*w[m],color=color,alpha=.8,label=label)
    top.hist(sea[m],bins=xbins,weights=weights,histtype='step',color=color)
    right.hist(cost[m],bins=ybins,weights=weights,histtype='step',orientation='horizontal',color=color)
joint.set(xlabel='Sea-level rise in 2100 from '+sea_reference+' (m)',ylabel='Incremental NPV (trillion 2019 USD PPP)')
joint.legend(fontsize=8);top.set(ylabel='Bin mass');right.set(xlabel='Bin mass')
plt.setp(top.get_xticklabels(),visible=False);plt.setp(right.get_yticklabels(),visible=False)
fig.suptitle('Coupled alternative paths: 50% budget weights; uniform coastal sea level'+('; HadCRUT5 climate' if had5 else ''))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/('coupled_coastal_joint_alternative'+suffix+'.'+ext)),dpi=150,bbox_inches='tight')
plt.close(fig)

regions=sorted(set(r['region'])-{'Unmapped'})
short={'East Asia & Pacific':'East Asia / Pacific','Europe & Central Asia':'Europe / Central Asia','Latin America & Caribbean':'Latin America / Caribbean','Middle East & North Africa':'Middle East / North Africa','North America':'North America','South Asia':'South Asia','Sub-Saharan Africa':'Sub-Saharan Africa'}
fig,axes=plt.subplots(1,3,figsize=(13,5.5),sharey=True);regional=[]
for b,(label,color) in enumerate(zip(labels,colors),1):
    for j,region in enumerate(regions):
        d=r[(r['region']==region)&(r['warming_bin']==b)]
        weight=np.array([w[np.where(g['sample']==i)[0][0]] for i in d['sample']])
        q=[quantile(d['minus_global_percentage_points'],weight,p) for p in (.05,.5,.95)]
        axes[0].plot(q[1],j+(b-2.5)*.14,'o',color=color,label=label if j==0 else None)
        absolute=quantile(d['percent_GDP'],weight,.5)
        se=quantile(100*d['sampling_SE_USD2019PPP']/d['GDP2010_USD2019PPP'],weight,.5)
        axes[1].plot(absolute,j+(b-2.5)*.14,'o',color=color)
        axes[2].plot(se,j+(b-2.5)*.14,'o',color=color)
        regional.append(dict(region=region,warming_bin=b,median_percent_GDP=absolute,median_difference_percentage_points=q[1],
            q05_difference_percentage_points=q[0],q95_difference_percentage_points=q[2],median_sampling_SE_percentage_points=se))
for ax in axes:ax.set_yticks(range(len(regions)));ax.set_yticklabels([short[x] for x in regions],fontsize=8)
axes[0].axvline(0,color='.4',lw=.8);axes[0].set(xlabel='Regional minus global cost/GDP (percentage points)',title='Median relative burden, 50% alternative weights');axes[0].legend(fontsize=7)
axes[1].set(xlabel='Regional cost / 2010 GDP (%)',title='Median regional burden')
axes[2].set(xlabel='Sampling SE / 2010 GDP (%)',title='Median single-path numerical SE')
fig.suptitle('Independent geography and SSP4: regional economic alternatives')
save(fig,'coupled_coastal_regional_alternative');write('coastal_coupled_regional_summary.csv',regional)

fig,axes=plt.subplots(1,2,figsize=(10,4.8));migration=[]
trigger=np.char.lower(g['AIS_fast_trigger_by2100'].astype(str))=='true'
for active,label,color in [(False,'AIS not triggered','#0072B2'),(True,'AIS triggered','#D55E00')]:
    m=trigger==active;weight=w[m];v=g['planned_migrants'][m]/1e6;order=np.argsort(v)
    axes[0].step(v[order],np.cumsum(weight[order])/weight.sum(),where='post',color=color,label=label)
    inc=g['incremental_planned_migrants'][m]/1e6;order=np.argsort(inc)
    axes[1].step(inc[order],np.cumsum(weight[order])/weight.sum(),where='post',color=color,label=label)
    migration.append(dict(AIS_trigger=active,members=int(m.sum()),probability=float(weight.sum()),
        planned_q05_million=quantile(v,weight,.05),planned_median_million=quantile(v,weight,.5),planned_q95_million=quantile(v,weight,.95),
        incremental_median_million=quantile(inc,weight,.5),median_conditional_sampling_SE_million=quantile(g['planned_migrants_sampling_SE'][m]/1e6,weight,.5)))
axes[0].set(xlabel='Planned movement count by 2100 (million)',ylabel='Conditional cumulative probability',title='Includes initialization and later planned retreat')
axes[1].set(xlabel='Difference from no-rise planned count (million)',ylabel='Conditional cumulative probability',title='Counterfactual difference, not unique displaced persons')
for ax in axes:ax.legend(fontsize=8)
fig.suptitle('Conditional migration alternatives; fixed Antarctic point fit; SSP4')
save(fig,'coupled_coastal_migration_alternative');write('coastal_coupled_migration_summary.csv',migration)

# Own upper tail, and a literal price-year threshold check whose unit limitations
# remain explicit. A zero estimated frequency is never asserted to be impossible.
threshold=quantile(cost,w,.95);tail=cost>=threshold
fig=plt.figure(figsize=(9,7));gs=fig.add_gridspec(2,2,width_ratios=[4,1],height_ratios=[1,4],hspace=.08,wspace=.08)
joint=fig.add_subplot(gs[1,0]);top=fig.add_subplot(gs[0,0],sharex=joint);right=fig.add_subplot(gs[1,1],sharey=joint)
for b,(label,color) in enumerate(zip(labels,colors),1):
    m=(g['warming_bin']==b)&tail
    if not m.any():continue
    weights=w[m]/w[m].sum()
    joint.scatter(sea[m],cost[m],s=12+1800*w[m],color=color,alpha=.8,label=label)
    top.hist(sea[m],bins=xbins,weights=weights,histtype='step',color=color)
    right.hist(cost[m],bins=ybins,weights=weights,histtype='step',orientation='horizontal',color=color)
joint.set(xlabel='Sea-level rise in 2100 from '+sea_reference+' (m)',ylabel='Incremental NPV (trillion 2019 USD PPP)')
joint.axhline(threshold,color='.4',ls=':',label='Own weighted95th percentile');joint.legend(fontsize=8)
top.set(ylabel='Tail-bin mass');right.set(xlabel='Tail-bin mass')
plt.setp(top.get_xticklabels(),visible=False);plt.setp(right.get_yticklabels(),visible=False)
fig.suptitle('Alternative upper tail: own threshold %.3f trillion; unresolved high-warming tails'%threshold+('; HadCRUT5 climate' if had5 else ''))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/('coupled_coastal_tail_alternative'+suffix+'.'+ext)),dpi=150,bbox_inches='tight')
plt.close(fig)
cpi=json.loads((ROOT/'results/price_basis_audit.json').read_text())
factor=cpi['factor_2019_to_2010_price_basis']
tail_rows=[]
for b in range(1,5):
    m=g['warming_bin']==b
    tail_rows.append(dict(warming_bin=b,own_upper5_threshold_trillion2019PPP=threshold,
        probability_at_or_above_own_threshold=float(w[m&tail].sum()/w[m].sum()),
        probability_above_literal2p7_after_CPI_only=float(w[m&(cost*factor>2.7)].sum()/w[m].sum()),
        own_tail_sample_count=int(np.sum(m&tail))))
write('coastal_coupled_tail_summary.csv',tail_rows)
audit=dict(scope='NON-REPRODUCTION: alternative emissions/calibration, uniformSLR, independent geography, annual2010–2100 and pairedbaseline',
    members=len(g),maximum_cost_trillion2019PPP=float(cost.max()),minimum_cost_trillion2019PPP=float(cost.min()),
    own_weighted95_threshold_trillion2019PPP=threshold,AIS_trigger_probability=float(w[trigger].sum()),
    maximum_global_relative_sampling_SE=float(np.max(g['sampling_SE_USD2019PPP']/g['incremental_NPV_USD2019PPP'])),
    minimum_conditional_ESS=min(x['conditional_ESS'] for x in summaries),
    target_comparison='W25 printed medians1.2/1.5/2.1/2.6 trillion2010USD use different2010–2150 horizon, baseline and monetary data; no matching claim',
    tail_caution='The >3.5C category has %d members; conditional percentile precision is limited by finite weighted sampling'%int(np.sum(g['warming_bin']==4)),
    sampling_caution='Coast draws are shared across all climate members; conditional numerical errors are correlated and not included in climate percentile bars')
(ROOT/('results/'+result_name('coastal_coupled_assessment.json'))).write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
