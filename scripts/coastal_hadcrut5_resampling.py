"""Finite-sample sensitivity of the completed HadCRUT5 coastal alternative.

These are subsamples of saved states, not new climate realizations or a
confidence interval for population quantiles. Coastal estimates remain fixed.
"""
from pathlib import Path
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
data = np.genfromtxt(str(ROOT/'results/coastal_coupled_hadcrut5_global.csv'),
                     delimiter=',', names=True, dtype=None, encoding=None)
cost = data['incremental_NPV_USD2019PPP']/1e12
weights = data['weight_budget50']
bins = data['warming_bin']
strata = [np.flatnonzero(data['weight_prior'] == value)
          for value in np.unique(data['weight_prior'])]
assert sorted(map(len, strata)) == [10, 32, 48, 64, 96]
assert [sum(bins == b) for b in range(1, 5)] == [101, 56, 71, 22]

def quantile(values, w, p):
    order = np.argsort(values)
    cumulative = np.cumsum(w[order])/sum(w)
    return float(values[order[min(len(order)-1, np.searchsorted(cumulative, p))]])

def write(name, rows):
    with (ROOT/'results'/name).open('w', newline='') as f:
        writer = csv.DictWriter(f, list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

seed = 20251048
rng = np.random.RandomState(seed)
records = []
members = []
for repeat in range(500):
    selected = []
    sampled_weights = []
    for group in strata:
        n = int(round(.8*len(group)))
        ix = rng.choice(group, n, replace=False)
        selected.extend(ix)
        sampled_weights.extend(weights[ix]*len(group)/n)
    selected = np.asarray(selected)
    sampled_weights = np.asarray(sampled_weights)
    assert len(selected) == 200 and abs(sum(sampled_weights)-1) < 1e-12
    for b in range(1, 5):
        mask = bins[selected] == b
        ix = selected[mask]
        members.append(dict(replicate=repeat+1, warming_bin=b, members=len(ix)))
        assert len(ix) > 0
        group = np.flatnonzero(bins == b)
        equal = rng.choice(group, 16, replace=False)
        for design, indices, w in [('Stratified200', ix, sampled_weights[mask]),
                                    ('Equal16', equal, weights[equal])]:
            for p in (.05, .5, .95):
                base = quantile(cost[group], weights[group], p)
                value = quantile(cost[indices], w, p)
                records.append(dict(design=design, replicate=repeat+1,
                    warming_bin=b, probability=p, cost_trillion2019PPP=value,
                    difference_trillion2019PPP=value-base))
write('coastal_hadcrut5_resamples.csv', records)
write('coastal_hadcrut5_resample_members.csv', members)
summary = []
plt.rcParams.update({'font.size': 9, 'pdf.fonttype': 42,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6))
for ax, design, title in zip(axes, ['Stratified200', 'Equal16'],
        ['200 of 250; preserved emissions-stratum masses',
         '16 distinct states in each warming category']):
    for b in range(1, 5):
        for p, color, shift in [(.05, '#0072B2', -.17), (.5, '#009E73', 0),
                                 (.95, '#D55E00', .17)]:
            values = [r['difference_trillion2019PPP'] for r in records
                      if r['design'] == design and r['warming_bin'] == b
                      and r['probability'] == p]
            lo, median, hi = np.quantile(values, [.05, .5, .95])
            ax.errorbar(b+shift, median, yerr=[[median-lo], [hi-median]],
                        fmt='o', color=color, capsize=2,
                        label='q{}'.format(int(p*100)) if b == 1 else None)
            summary.append(dict(design=design, warming_bin=b, probability=p,
                q05_difference_trillion2019PPP=lo,
                median_difference_trillion2019PPP=median,
                q95_difference_trillion2019PPP=hi))
    ax.set(xticks=[1, 2, 3, 4], xlabel='Warming category', title=title,
           ylabel='Subsample minus full quantile (trillion 2019 PPP)')
    ax.axhline(0, color='.4', lw=.7)
    ax.legend(fontsize=8)
fig.suptitle('Non-reproduction: sensitivity within the finite HadCRUT5 ensemble')
fig.tight_layout(rect=(0, 0, 1, .93))
for ext in ('pdf', 'png'):
    fig.savefig(str(ROOT/'figures'/('coastal_hadcrut5_resampling.'+ext)),
                dpi=150, bbox_inches='tight')
plt.close(fig)
write('coastal_hadcrut5_resample_summary.csv', summary)
high = [r['members'] for r in members if r['warming_bin'] == 4]
audit = dict(seed=seed, replicates=500, full_members=250,
    high_bin_members=22, stratified_high_bin_minimum=min(high),
    stratified_high_bin_maximum=max(high), equal_bin_members=16,
    scope='NON-REPRODUCTION: finite saved-state subsampling; no new climate draws',
    caution='Ranges measure sensitivity within retained states, not population '
            'quantile uncertainty. Coastal errors and missing joint physical '
            'uncertainty are held fixed. The upper tail remains unresolved.')
(ROOT/'results/coastal_hadcrut5_resampling_assessment.json').write_text(
    json.dumps(audit, indent=2, sort_keys=True)+'\n')
print(json.dumps(audit, indent=2, sort_keys=True))
