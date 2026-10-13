"""Ordinary SciPy optimization; scientific residuals are evaluated by Julia.

The line protocol passes scaled coordinates and residual vectors over pipes.
No scientific equations, observations or target implementation are imported.
"""
import sys
import numpy as np
from scipy.optimize import least_squares

start = np.asarray([float(v) for v in sys.argv[1].split(',')])
evaluations = [0]
def residual(u):
    evaluations[0] += 1
    print('E,'+','.join(format(v, '.17g') for v in u), flush=True)
    line = sys.stdin.readline()
    if not line:
        raise RuntimeError('Julia residual stream closed')
    return np.asarray([float(v) for v in line.strip().split(',')])

result = least_squares(residual, start, bounds=(0., 1.), method='trf',
    jac='3-point', diff_step=1e-4, x_scale='jac',
    ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=400)
gradient = result.grad.copy()
gradient[(result.x < 1e-8) & (gradient > 0)] = 0
gradient[(result.x > 1-1e-8) & (gradient < 0)] = 0
reasons = {0: 'evaluation_limit', 1: 'scipy_scaled_gradient',
           2: 'scipy_objective', 3: 'scipy_step', 4: 'scipy_objective_and_step'}
print('R,'+','.join(format(v, '.17g') for v in result.x)+','+
    ','.join(map(str, [2*result.cost, result.nfev, np.max(np.abs(gradient)),
                      reasons[result.status], evaluations[0], result.optimality])), flush=True)
