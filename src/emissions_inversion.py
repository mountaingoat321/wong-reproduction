"""Explicit expert-density alternatives, not recovered Wong/Darnell densities.

Fuller et al. (2017), Statistical calibrations, evaluates the expert density
at the model output as a likelihood. Therefore the parameter density is
proportional to prior(theta)*expert(cumulative_emissions(theta)). It need not
give the same output probability as the expert assessment.
"""
import numpy as np
from scipy.special import gammaln


def expert_density(emissions, budget, tail_mode, lower_shape, tail_shape,
                   below_probability=.5):
    """Beta(a,a) below budget; shifted Gamma(k,scale) above it, in GtCO2^-1.

    Shape choices are sensitivity assumptions. The scale is derived from
    the documented conditional mode: scale=(tail_mode-budget)/(k-1).
    """
    if not (budget > 0 and tail_mode > budget and lower_shape >= 1 and
            tail_shape > 1 and 0 < below_probability < 1):
        raise ValueError('Invalid support, mode, shape or assessment mass')
    c = np.asarray(emissions, dtype=float)
    f = np.zeros_like(c)
    low = (c > 0) & (c <= budget)
    u = c[low]/budget
    a = lower_shape
    f[low] = (below_probability/budget *
              np.exp(gammaln(2*a)-2*gammaln(a)) * (u*(1-u))**(a-1))
    high = c > budget
    z = c[high]-budget
    scale = (tail_mode-budget)/(tail_shape-1)
    f[high] = (1-below_probability)*np.exp(
        (tail_shape-1)*np.log(z)-z/scale-gammaln(tail_shape)-tail_shape*np.log(scale))
    return f


def posterior_weights(prior_weights, likelihood):
    """Normalize prior quadrature/design weights times the expert likelihood."""
    p = np.asarray(prior_weights, dtype=float)
    f = np.asarray(likelihood, dtype=float)
    if p.shape != f.shape or not (np.isfinite(p).all() and np.isfinite(f).all()
                                 and np.all(p >= 0) and np.all(f >= 0)):
        raise ValueError('Aligned finite nonnegative arrays required')
    z = np.sum(p*f)
    if z <= 0:
        raise ValueError('Zero supported likelihood')
    return p*f/z, float(z)
