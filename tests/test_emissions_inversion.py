"""Distribution constraints and Bayes update, independent of model outputs."""
import sys, unittest
from pathlib import Path
import numpy as np
from scipy.integrate import quad
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from emissions_inversion import expert_density, posterior_weights


class InversionTests(unittest.TestCase):
    def test_assessment_mass_and_conditional_mode(self):
        b, m = 1223., 4200.
        for a in (1, 2):
            for k in (2, 4):
                f = lambda x: float(expert_density(x, b, m, a, k))
                self.assertAlmostEqual(quad(f, 0, b)[0], .5, places=10)
                self.assertAlmostEqual(quad(f, b, b+100000)[0], .5, places=10)
                self.assertGreater(f(m), f(m-1))
                self.assertGreater(f(m), f(m+1))

    def test_update_is_not_an_output_mass_constraint(self):
        w, z = posterior_weights([.1, .9], [2., 1.])
        np.testing.assert_allclose(w, [2/11, 9/11], rtol=1e-14)
        self.assertAlmostEqual(z, 1.1)
        v, _ = posterior_weights([.1, .9], [20., 10.])
        np.testing.assert_allclose(w, v, rtol=1e-14)

    def test_invalid_support(self):
        with self.assertRaises(ValueError):
            expert_density([1.], 1223., 1000., 1, 2)
        with self.assertRaises(ValueError):
            posterior_weights([.5, .5], [0., 0.])


if __name__ == '__main__':
    unittest.main()
