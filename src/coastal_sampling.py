"""Design-based totals for independent sampling with replacement.

The control total and coefficient must be fixed independently of these draws.
Returned variance is conditional on the target coastal trajectory, not a
variance for climate or socioeconomic uncertainty.
"""
import numpy as np


def total_with_control(values, controls, probabilities, control_total, beta):
    y = np.asarray(values, dtype=float)
    x = np.asarray(controls, dtype=float)
    p = np.asarray(probabilities, dtype=float)
    if y.ndim != 1 or y.shape != x.shape or y.shape != p.shape or len(y) < 2:
        raise ValueError('At least two aligned draws are required')
    if not (np.isfinite(y).all() and np.isfinite(x).all() and
            np.isfinite(p).all() and np.all((p > 0) & (p <= 1))):
        raise ValueError('Finite inputs and positive selection probabilities required')
    residual = (y - beta*x)/p
    return (float(beta*control_total + residual.mean()),
            float(residual.var(ddof=1)/len(y)))
