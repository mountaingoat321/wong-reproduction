"""Independently implemented split rank/folded R-hat and bulk/tail ESS.
Definitions: Vehtari et al. (2021), DOI10.1214/20-BA1221; Stan reference
manual, Posterior Analysis (equations only; no sampler/source code consulted).
Diagnostics assess simulation accuracy, not adequacy of the scientific model.
"""
import csv
import json
import sys
from pathlib import Path
import numpy as np
from scipy.stats import norm, rankdata

ROOT = Path(__file__).resolve().parents[1]

def split(x):
    n = x.shape[1] // 2
    return np.concatenate((x[:, :n], x[:, -n:]))

def ranks(x):
    r = rankdata(x.ravel(), method='average').reshape(x.shape)
    return norm.ppf((r - 3.0/8) / (x.size + 1.0/4))

def variance(x):
    n = x.shape[1]
    within = np.mean(np.var(x, axis=1, ddof=1))
    between = n * np.var(np.mean(x, axis=1), ddof=1)
    return within, (n-1)/n*within + between/n

def rhat(x):
    w, v = variance(x)
    return np.sqrt(v/w) if w > 0 else np.inf

def ess(x):
    """Biased FFT autocovariances; multichain variance; Geyer positive,
    monotone paired autocorrelations. Cap at retained size conservatively.
    """
    m, n = x.shape
    w, v = variance(x)
    if v == 0:
        return 0.0
    fft = np.fft.rfft(x - x.mean(axis=1, keepdims=True), n=2*n, axis=1)
    acov = np.fft.irfft(fft * fft.conj(), n=2*n, axis=1)[:, :n].real / n
    rho = 1 - (w - acov.mean(axis=0)) / v
    rho[0] = 1
    pairs = []
    for j in range(0, n-1, 2):
        pair = rho[j] + rho[j+1]
        if pair < 0:
            break
        pairs.append(min(pair, pairs[-1]) if pairs else pair)
    tau = max(1.0, -1 + 2*sum(pairs))
    return m*n/tau

def diagnostics(x):
    z = split(x)
    q = np.quantile(x, [.05, .5, .95])
    return dict(rank_folded_rhat=float(max(rhat(ranks(z)), rhat(ranks(abs(z-np.median(z)))))),
                bulk_ess=float(ess(ranks(z))),
                tail_ess=float(min(ess((z <= q[0]).astype(float)), ess((z >= q[2]).astype(float)))),
                q05=float(q[0]), median=float(q[1]), q95=float(q[2]))

if __name__ == '__main__':
    joint='--joint-heat' in sys.argv
    stem='climate_joint' if joint else 'climate'
    data = np.genfromtxt(str(ROOT/('results/'+stem+'_posterior.csv')), delimiter=',', names=True)
    chains = np.unique(data['chain'])
    assert len(chains) == 4
    rows = []
    for name in data.dtype.names[2:]:
        x = np.vstack([data[name][data['chain'] == c] for c in chains])
        d = diagnostics(x)
        d['parameter'] = name
        rows.append(d)
        print(name, d)
    with (ROOT/('results/'+stem+'_mcmc_diagnostics.csv')).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['parameter','rank_folded_rhat','bulk_ess','tail_ess','q05','median','q95'])
        w.writeheader(); w.writerows(rows)
    passed = all(r['rank_folded_rhat'] < 1.01 and r['bulk_ess'] >= 400 and r['tail_ess'] >= 400 for r in rows)
    summary = dict(experiment='ALTERNATIVE '+('temperature and 0--700m heat' if joint else 'temperature-only')+' calibration; not W25 posterior',
                   retained_draws=int(data.size), chains=4, convergence_criteria_met=passed,
                   criteria='rank/folded split Rhat <1.01; bulk and tail ESS >=400 for every coordinate and log density')
    (ROOT/('results/'+stem+'_mcmc_status.json')).write_text(json.dumps(summary, indent=2)+'\n')
    (ROOT/('results/'+stem+'_mcmc_status.toml')).write_text('convergence_criteria_met = %s\nretained_draws = %d\n' % (str(passed).lower(), data.size))
