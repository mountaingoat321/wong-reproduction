import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from assess_calibration import diagnostics

rng = np.random.RandomState(20251035)
x = rng.normal(size=(4, 8000))
d = diagnostics(x)
assert d['rank_folded_rhat'] < 1.005
assert d['bulk_ess'] > 25000 and d['tail_ess'] > 25000
y = x.copy()
for j in range(1, y.shape[1]):
    y[:, j] = .9*y[:, j-1] + x[:, j]
d = diagnostics(y[:, 1000:])
assert 900 < d['bulk_ess'] < 2400  # analytic AR1 ESS ~28000/19
assert d['rank_folded_rhat'] < 1.01
x[0] += 2
assert diagnostics(x)['rank_folded_rhat'] > 1.1
x = rng.normal(size=(4, 8000)); x[0] *= 4
assert diagnostics(x)['rank_folded_rhat'] > 1.1  # folded diagnostic detects scale mismatch
print('6 MCMC diagnostic assertions passed.')
