"""Observation-vintage importance diagnostic and explicit observable-error alternative."""
from pathlib import Path
import csv,json,sys
import numpy as np
from scipy.special import ndtr
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[1]
pilot='--pilot' in sys.argv;prefix='climate_vintage'+('_pilot' if pilot else '')
def read(name):return np.genfromtxt(str(ROOT/name),delimiter=',',names=True,dtype=None,encoding=None)
def write(name,rows):
    with (ROOT/'results'/name).open('w',newline='') as f:
        w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
def quantile(x,w,p):
    j=np.argsort(x);c=np.cumsum(w[j]);c/=c[-1]
    return float(x[j[min(len(x)-1,np.searchsorted(c,p))]])
d=read('results/'+prefix+'_weights.csv');p=d[d['in_uniform_proposal'].astype(str)=='True']
# Julia CSV booleans are lowercase strings with the installed NumPy parser.
if len(p)==0:p=d[d['in_uniform_proposal'].astype(str)=='true']
assert len(p)>0
logw=p['log_weight_ratio'];w=np.exp(logw-logw.max());w/=w.sum()
uniform=np.ones(len(p))/len(p)
old=read('inputs/hadcrut4.csv');new=read('inputs/hadcrut5_5010.csv')
assert np.array_equal(old['year'],new['year'])
delta=new['anomaly_K']-old[old.dtype.names[1]]
summary=dict(scope='NON-REPRODUCTION: isolated HadCRUT4 to HadCRUT5 likelihood substitution; all other likelihoods and priors retained',
    proposal_rows=len(p),evaluated_rows=len(d),importance_ESS_ignoring_chain_dependence=float(1/np.sum(w*w)),
    maximum_weight=float(w.max()),passes_minimum400_weight_ESS=bool(1/np.sum(w*w)>=400),
    dependence_caution='Weight ESS ignores dependence inherited from the MCMC proposal; it is not a new posterior convergence test',
    observed_version_difference_fit_RMSE_K=float(np.sqrt(np.mean(delta[old['year']<=2005]**2))),
    observed_version_difference_holdout_mean_K=float(np.mean(delta[old['year']>=2006])),
    heat_reference=dict(change_1e22J=12.8,uncertainty_at_least_1e22J=8.,note='Written GK07 summary, not an assigned Gaussian SD or an annual calibration series'),
    chain_weight={str(int(c)):float(w[p['chain']==c].sum()) for c in np.unique(p['chain'])})
for name,weight in [('original',uniform),('vintage_importance_diagnostic',w)]:
    summary[name]={}
    for field in ('ecs_K','ssp245_2081_2100_K','heat3000_decadal_change_1e22J'):
        summary[name][field]={q:quantile(p[field],weight,prob) for prob,q in [(.05,'q05'),(.5,'median'),(.95,'q95')]}
h=read('.local/'+prefix+'_hindcasts.csv');years=np.unique(h['year']);rows=[]
matrix=np.vstack([h['temperature_K'][h['posterior_row']==row] for row in p['posterior_row']])
for i,year in enumerate(years):
    rows.append(dict(year=int(year),HadCRUT4_K=float(old[old.dtype.names[1]][i]),HadCRUT5_K=float(new['anomaly_K'][i]),
        original_median_K=quantile(matrix[:,i],uniform,.5),vintage_importance_median_K=quantile(matrix[:,i],w,.5)))
write(prefix+'_hindcast_summary.csv',rows)
for label in ('original','vintage_importance'):
    predicted=np.array([r[label+'_median_K'] for r in rows]);hold=years>=2006
    summary[label+'_holdout_RMSE_HadCRUT5_K']=float(np.sqrt(np.mean((predicted[hold]-new['anomaly_K'][hold])**2)))
(ROOT/'results'/(prefix+'_assessment.json')).write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2,sort_keys=True))

if not pilot:
    # The fitted AR1 residual represents an observable discrepancy. This
    # sensitivity changes temperature classification, not physical ice forcing.
    c=read('results/coupled_emissions_stratified_parameters.csv')
    e=read('results/coupled_emissions_stratified_endpoints.csv');e=e[e['forcing_rule']=='annual_nearest_emissions']
    assert np.array_equal(c['sample'],e['sample'])
    sd=c['innovation_sd_K']/np.sqrt(1-c['rho']**2)
    mean=e['temperature2100_K'];boundaries=np.array([-np.inf,1.5,2.5,3.5,np.inf])
    probabilities=np.diff(ndtr((boundaries[None,:]-mean[:,None])/sd[:,None]),axis=1)
    assert np.allclose(probabilities.sum(axis=1),1.,rtol=0,atol=1e-14) and np.all(probabilities>=0)
    rows=[];summaries=[]
    for j,row in enumerate(e):
        rows.append(dict(sample=int(row['sample']),stationary_temperature_SD_K=float(sd[j]),
            **{'bin%d_probability'%(b+1):float(probabilities[j,b]) for b in range(4)}))
    for weight in ('weight_prior','weight_budget50','weight_budget75'):
        weights=e[weight]/e[weight].sum();r=dict(distribution=weight)
        for b in range(4):r['bin%d_probability'%(b+1)]=float(np.dot(weights,probabilities[:,b]))
        for prob,name in [(.05,'q05_K'),(.5,'median_K'),(.95,'q95_K')]:
            r[name]=float(brentq(lambda value:np.dot(weights,ndtr((value-mean)/sd))-prob,mean.min()-10,mean.max()+10))
        summaries.append(r)
    write('coupled_temperature_observable_probabilities.csv',rows)
    write('coupled_temperature_observable_summary.csv',summaries)
