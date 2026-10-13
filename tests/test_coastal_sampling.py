"""Exact finite-population tests of the coastal sampling estimator."""
from pathlib import Path
import itertools
import sys
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from coastal_sampling import total_with_control


class SamplingTests(unittest.TestCase):
    def test_exact_enumeration_unbiased_total_and_variance(self):
        # Enumerate all ordered samples, including repeated coast draws.
        y = np.array([2., 9., -1.])
        x = np.array([3., -2., 5.])
        p = np.array([.1, .3, .6])
        for beta in (0., .37, -2.):
            estimates, variances, mass = [], [], []
            for pair in itertools.product(range(3), repeat=2):
                j = list(pair)
                estimate, variance = total_with_control(y[j], x[j], p[j], x.sum(), beta)
                estimates.append(estimate)
                variances.append(variance)
                mass.append(p[j].prod())
            mass = np.array(mass)
            mean = np.dot(mass, estimates)
            actual_variance = np.dot(mass, (np.array(estimates)-mean)**2)
            self.assertAlmostEqual(mean, y.sum(), places=12)
            self.assertAlmostEqual(np.dot(mass, variances), actual_variance, places=10)

    def test_exact_control_has_zero_variance(self):
        estimate, variance = total_with_control([6., 2., 6.], [3., 1., 3.],
                                               [.7, .1, .7], 8., 2.)
        self.assertEqual(estimate, 16.)
        self.assertEqual(variance, 0.)

    def test_invalid_design_is_rejected(self):
        with self.assertRaises(ValueError):
            total_with_control([1.], [1.], [.2], 1., 1.)
        with self.assertRaises(ValueError):
            total_with_control([1., 2.], [1., 2.], [.2, 0.], 3., 1.)


if __name__ == '__main__':
    unittest.main()
