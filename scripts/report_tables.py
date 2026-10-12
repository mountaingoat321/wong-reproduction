"""Generate report tables from verified results; all table text remains auditable."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def escape(text):
    return str(text).replace('&', r'\&').replace('%', r'\%').replace('_', r'\_').replace('#', r'\#')
def table(path):
    with path.open() as f:
        return list(csv.DictReader(f))

m = json.loads((ROOT / 'results' / 'verification.json').read_text())
metrics = [
    ('Greenland finest absolute error (m SLE)', '{:.3e}'.format(m['greenland_finest_error_m_sle'])),
    ('Ocean finest maximum temperature error (K)', '{:.3e}'.format(m['diffusion_finest_error_k'])),
    ('Ocean maximum heat-balance residual (K m)', '{:.3e}'.format(m['diffusion_max_balance_error_k_m'])),
    ('Expected flood loss, SciPy reference (USD/year)', '{:.6f}'.format(m['scipy_expected_loss_usd_per_year'])),
    ('Expected flood loss, Julia relative difference', '{:.3e}'.format(m['julia_flood_finest_relative_error'])),
    ('Depth integral maximum difference (USD)', '{:.3e}'.format(m['damage_integral_max_absolute_error_usd'])),
    ('Annual emissions residual at gamma=0.07 (% of peak)', '{:.6f}'.format(100*m['emissions_annual_remaining_fraction_gamma007'])),
    ('Minimum sampled Antarctic ocean transform (degree C)', '{:.6f}'.format(m['anto_minimum_sampled_c'])),
]
(ROOT / 'report' / 'metrics.tex').write_text('\n'.join(
    escape(a) + ' & ' + escape(b) + r' \\' for a, b in metrics) + '\n')
rows = table(ROOT / 'docs' / 'FIGURE_STATUS.csv')
(ROOT / 'report' / 'figure_status.tex').write_text('\n'.join(
    '{} & {} & {} \\\\'.format(escape(r['figure'] + ': ' + r['panel']), escape(r['quantity']), escape(r['status']))
    for r in rows) + '\n')
rows = table(ROOT / 'results' / 'published_table_audit.csv')
(ROOT / 'report' / 'table_audit.tex').write_text('\n'.join(
    '{} & {} & {} & {:.4f} & {} \\\\'.format(r['bin'], r['published_count'], r['tail_count_audited'],
        float(r['tail_percent_calculated']), r['tail_percent_printed']) for r in rows) + '\n')
rows = table(ROOT / 'results' / 'decision_sensitivity.csv')
(ROOT / 'report' / 'decision_table.tex').write_text('\n'.join(
    escape(r['quantity'].replace('_', ' ')) + ' & {:.6f}'.format(float(r['value'])) + r' \\' for r in rows) + '\n')
