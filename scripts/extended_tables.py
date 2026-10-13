"""Computed extended-report tables; inputs are independently generated results."""
import csv,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/'results'/name).open() as f:return list(csv.DictReader(f))
out=[r'\begin{table}[htbp]',r'\centering\small',r'\begin{tabular}{llrrr}',r'\toprule',
     r'SSP & Rise (m) & Selected cost & No-adapt. cost & Migrants (million) \\',r'\midrule']
for r in read('geographic_global_costs.csv'):
    values=[r['scenario'],float(r['sea2100_m']),float(r['incremental_pv_USD2019PPP'])/1e12,
            (float(r['no_adaptation_pv_USD2019PPP'])-float(r['baseline_no_adaptation_pv_USD2019PPP']))/1e12,float(r['migrants'])/1e6]
    out.append('{} & {:.1f} & {:.3f} & {:.3f} & {:.3f} \\\\'.format(*values))
out.extend([r'\bottomrule\end{tabular}',r'\caption{Geographic alternative totals. Cost columns are trillion 2019 USD PPP, discounted to2010. Migrants count movements in the selected policy over2010--2100 and are not unique individuals over a demographic lifetime. No warming probabilities are assigned.}',r'\end{table}'])
metrics=json.loads((ROOT/'results/extended_metrics.json').read_text())
out.extend([r'\begin{table}[htbp]',r'\centering\small',r'\begin{tabular}{lrrrr}',r'\toprule',r'Ice component & Max $\widehat R$ & Min bulk ESS & Min tail ESS & Holdout RMSE (Gt/yr) \\',r'\midrule'])
for component in ('glaciers','greenland'):
    rows=read('ice_'+component+'_mcmc_diagnostics.csv')
    values=[component.capitalize(),max(float(r['rank_folded_rhat']) for r in rows),min(float(r['bulk_ess']) for r in rows),min(float(r['tail_ess']) for r in rows),metrics['ice_'+component]['conditional_holdout_rmse_Gt_yr']]
    out.append('{} & {:.4f} & {:.0f} & {:.0f} & {:.1f} \\\\'.format(*values))
out.extend([r'\bottomrule\end{tabular}',r'\caption{Final conditional ice calibration diagnostics and held-out rate errors. Every coordinate and log density must pass $\widehat R<1.01$ and both ESS$\ge400$. Observed temperature is supplied in held-out years.}',r'\end{table}'])
(ROOT/'report/extended_tables.tex').write_text('\n'.join(out)+'\n')
