"""Report predictive and independent ocean checks of restricted/free point fits."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def read(name):return np.genfromtxt(str(ROOT/'results'/name),delimiter=',',names=True,dtype=None,encoding=None)
legacy=read('carbon_vintage_fits.csv');fixed=read('carbon_vintage_revised_fits.csv');free=read('carbon_vintage_free_fits.csv')
assert np.array_equal(fixed['case'],free['case']) and len(free)==3
assert max(free['max_mass_error_GtC'])<1e-8 and max(free['substep_difference_ppm'])<.001
assert np.all(free['objective']<=fixed['objective']+1e-8)
searches=read('carbon_vintage_free_searches.csv')
assert len(searches)==12
assert all(str(v).startswith('scipy_') for v in searches['stop'])
predictions=read('carbon_search_predictions.csv')
assert len(predictions)==12 and max(predictions['max_newton_bisection_difference_ppm'])<1e-6
plt.rcParams.update({'font.size':9,'pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,3,figsize=(14,4.8));labels=['Had4\nMLO only','Had4\nMLO + Law Dome','Had5\nMLO + Law Dome']
for j,(data,label,color) in enumerate([(fixed,'β and initial CO₂','#0072B2'),(free,'Also Q₁₀ and transfer','#D55E00')]):
    x=np.arange(3)+(j-.5)*.28
    axes[0].bar(x,data['MLO_holdout_RMSE_ppm'],width=.26,color=color,label=label)
    axes[1].plot(x,data['ocean1994_GtC'],'o',color=color,label=label)
axes[1].axhspan(99,137,color='.6',alpha=.17,label='Written 118 ± 19 GtC benchmark')
axes[1].axhline(118,color='.5',ls=':')
for ax in axes[:2]:
    ax.set_xticks(range(3));ax.set_xticklabels(labels,fontsize=8);ax.legend(fontsize=7)
axes[0].set(ylabel='2006–2021 CO₂ RMSE (ppm)',title='Withheld observations, not calibration objective')
axes[1].set(ylabel='Ocean carbon uptake by 1994 (GtC)',title='Independent ocean-inventory context')
for i,color in enumerate(['#0072B2','#D55E00','#CC79A7']):
    points=searches[searches['case']==free[i]['case']]
    axes[2].scatter(points['q10'],points['thermocline_transfer_m_yr'],color=color,
                    s=28,label=labels[i].replace('\n',' '))
    axes[2].scatter([free[i]['q10']],[free[i]['thermocline_transfer_m_yr']],
                    marker='*',s=100,color=color,edgecolors='k',linewidths=.5)
axes[2].set(xlabel='Respiration Q₁₀',ylabel='Thermocline transfer (m/year)',
             yscale='log',title='Four starts; stars mark selected minima')
axes[2].legend(fontsize=7)
fig.suptitle('Non-reproduction: four-start carbon fits within documented physical bounds')
fig.tight_layout(rect=(0,0,1,.93))
for ext in ('pdf','png'):fig.savefig(str(ROOT/'figures'/('carbon_parameter_sensitivity.'+ext)),dpi=150,bbox_inches='tight')
plt.close(fig)
audit=dict(scope='NON-REPRODUCTION: conditional point fits, equal group mean-square objective, no posterior or age convolution',
    free_holdout_RMSE_ppm={str(r['case']):float(r['MLO_holdout_RMSE_ppm']) for r in free},
    free_ocean1994_GtC={str(r['case']):float(r['ocean1994_GtC']) for r in free},
    free_boundary_cases=[str(r['case']) for r in free if str(r['boundary_hit']).lower()=='true'],
    restricted_solver_objective_improvement={str(r['case']):float(legacy[i]['objective']-r['objective']) for i,r in enumerate(fixed)},
    revised_restricted_holdout_RMSE_ppm={str(r['case']):float(r['MLO_holdout_RMSE_ppm']) for r in fixed},
    training_objective_improvement={str(r['case']):float(fixed[i]['objective']-r['objective']) for i,r in enumerate(free)},
    optimizer_stop_reasons={str(r['case'])+' start'+str(r['start']):str(r['stop']) for r in searches},
    local_objective_ranges={str(r['case']):[float(min(searches['objective'][searches['case']==r['case']])),float(max(searches['objective'][searches['case']==r['case']]))] for r in free},
    max_fitted_chemistry_solver_difference_ppm=float(max(predictions['max_newton_bisection_difference_ppm'])),
    max_fitted_substep_difference_ppm=float(max(predictions['substep_difference_ppm'])),
    max_projected_gradient=float(max(searches['projected_gradient'])),
    max_scaled_gradient=float(max(searches['scaled_gradient'])),
    caution='Four starts do not prove global optimality. Ocean benchmark has a different preindustrial reference; agreement is contextual. New fits do not replace the base coupled carbon point fit.')
(ROOT/'results/carbon_parameter_assessment.json').write_text(json.dumps(audit,indent=2,sort_keys=True)+'\n')
print(json.dumps(audit,indent=2,sort_keys=True))
