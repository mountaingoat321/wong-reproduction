"""Report tables computed from saved independent experiments."""
from pathlib import Path
import ast,csv,json
ROOT=Path(__file__).resolve().parents[1]
def toml_values(name):
    # These generated metadata contain only single-line scalar/list literals.
    values={}
    for line in (ROOT/'results'/name).read_text().splitlines():
        if ' = ' not in line:continue
        key,value=line.split(' = ',1)
        values[key]=ast.literal_eval({'true':'True','false':'False'}.get(value,value))
    return values
def read(name):
    with (ROOT/'results'/name).open() as f:return list(csv.DictReader(f))
def table(header,rows,caption):
    return '\n'.join([r'\begin{table}[htbp]',r'\centering\small',r'\begin{tabular}{l'+'r'*(len(header)-1)+'}',r'\toprule',
        ' & '.join(header)+r' \\',r'\midrule']+[' & '.join(row)+r' \\' for row in rows]+[
        r'\bottomrule\end{tabular}',r'\caption{'+caption+'}',r'\end{table}'])+'\n'
d=toml_values('dais_conditional_best.toml');a=json.loads((ROOT/'results/dais_paleo_assessment.json').read_text())
rows=[]
for label,value,mean,sd in zip(['Last Interglacial','Last Glacial Maximum','Mid-Holocene','1992--2002 increase'],d['window_predictions_m'],[5.5,-11.35,-2.63,.00197],[.95,2.23,.68,.00046]):
    rows.append([label,'{:.5g}'.format(mean),'{:.5g}'.format(sd),'{:.5g}'.format(value)])
text=table(['Constraint','Written mean (m)','Written SD (m)','Point fit (m)'],rows,
    'Conditional Antarctic predictions under the explicitly alternative forcing. These four quantities are fitted, not held-out validation. The Last Interglacial hard acceptance interval is 3.6--7.4 m.')
text+=r'The conditional solution uses $\gamma=%.5f$, $\alpha=%.5f$, $\lambda=%.5f$ m yr$^{-1}$ and $T_c=%.5f\,{}^\circ$C. ' % (d['gamma'],d['alpha'],d['lambda_m_yr'],d['threshold_degC'])
text+='The search begins with {} Latin hypercube points; {} draws satisfy all four windows before local optimization. '.format(d['latin_hypercube_samples'],a['LHS_all_windows_pass'])
text+=r'The final four-window $\chi^2$ is %.4g. Halving the maximum timestep from 10 to 5 years changes these predictions by at most %.2g m. ' % (d['window_chisq'],d['maximum_dt10_dt5_window_difference_m'])
h=a['conditional_rate_holdout']
text+='The conditional 2003--2008 mass-loss RMSE is {:.2f} Gt yr$^{{-1}}$, with bias {:+.2f} Gt yr$^{{-1}}$. The observed and predicted mean rates are {:.2f} and {:.2f} Gt yr$^{{-1}}$, respectively.\n'.format(h['RMSE_Gt_yr'],h['bias_Gt_yr'],h['mean_observed_Gt_yr'],h['mean_predicted_Gt_yr'])
(ROOT/'report/paleo_tables.tex').write_text(text)

g=json.loads((ROOT/'results/geographic_full_resolution_comparison.json').read_text())
rows=[]
for field,label,scale in [('pv_USD2019PPP','Selected policy total NPV',1e12),('incremental_pv_USD2019PPP','Paired-baseline incremental NPV',1e12),('migrants','Movement count (million)',1e6)]:
    m=g['metrics'][field];rows.append([label,'{:.4f}'.format(m['coarse_sum']/scale),'{:.4f}'.format(m['fine_sum']/scale),'{:+.2f}'.format(100*m['global_relative_change'])])
text=table(['Quantity','Six bins','200 bins','Change (\%)'],rows,
    'Complete matched resolution test for 9,531 coast-country units, SSP4 and prescribed1 m rise by2100. Cost rows use trillion 2019 USD PPP. The input elevation range is unchanged; only within-bin exposure resolution changes.')
text+='The preferred first-period policy changes in {} units ({:.2f}\%). These totals replace extrapolation from the small coastal pilot; they do not establish convergence of the physical exposure data themselves.\n'.format(g['policy_changes'],100*g['policy_change_fraction'])
(ROOT/'report/geographic_resolution_tables.tex').write_text(text)

if (ROOT/'results/coupled_emissions_bin_summary.csv').exists():
    rows=[]
    for r in read('coupled_emissions_bin_summary.csv'):
        if r['forcing_rule']!='annual_nearest_emissions' or int(r['members'])!=256:continue
        label={'documented_prior':'Prior','alternative_budget50':'50\% alternative','alternative_budget75':'75\% alternative'}[r['distribution']]
        rows.append([label]+['{:.3f}'.format(float(r[k])) for k in ['temperature2100_q05_K','temperature2100_q50_K','temperature2100_q95_K']]+['{:.1f}'.format(100*float(r['bin%d_probability'%j])) for j in range(1,5)])
    text=table(['Distribution','$T_{.05}$','$T_{.50}$','$T_{.95}$','$P_1$(\%)','$P_2$(\%)','$P_3$(\%)','$P_4$(\%)'],rows,
        'Alternative annual warming in 2100 relative to 1850--1900, in K. Probabilities refer to the four published threshold definitions. The balanced 256-member subsample has distinct weights for each probability measure; it is not the published 5,000-member ensemble.')
    a=json.loads((ROOT/'results/coupled_emissions_assessment.json').read_text())
    text+='The largest paired change in 2100 warming from nearest-scenario versus fixed-SSP2-4.5 non-CO$_2$ forcing is {:.3f} K. The restart changes the CO$_2$ forcing by {:+.4f} W m$^{{-2}}$, without compensation. Maximum carbon accounting error is {:.2g} Gt C.\n'.format(a['maximum_paired_2100_nonCO2_temperature_difference_K'],a['CO2_forcing_restart_jump_W_m2'],a['maximum_mass_error_GtC'])
    (ROOT/'report/emissions_tables.tex').write_text(text)
