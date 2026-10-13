# Independent reconstruction of Wong et al. (2025)

Target: **Coastal adaptation and damage costs at different global warming
thresholds**, *npj Natural Hazards* 2, 35,
[DOI 10.1038/s44304-025-00089-0](https://doi.org/10.1038/s44304-025-00089-0).

**The scientific reproduction is incomplete.** This repository contains
independent Julia implementations, verified mechanisms, observation-conditioned
calibrations, and explicitly labeled alternative climate, sea-level and coastal
experiments. No target numerical figure is established as independently
reproduced. Main Figures 1–3, supplementary Figures S1–S10 and modeled Table 1
remain **Not reproduced**; Figure 4 is an original **Conceptual schematic**.
Alternative figures and failed checks are retained without being relabeled as
published results.

The [LaTeX report and compiled PDF](report/report.pdf),
[complete target inventory](docs/FIGURE_STATUS.csv), and
[continuation accounting](docs/CONTINUATION_ACCOUNTING.md) distinguish
recovered specifications, derived choices and alternative assumptions.

## Executed scientific work

- Reconstructed conservative climate and carbon dynamics, all five sea-level
  contributions, Antarctic threshold behavior, and coastal adaptation cash flows.
- Calibrated climate against temperature and upper-ocean heat. HadCRUT5 improves
  the temperature-version match, but SSP2-4.5 warming remains below the AR6 best
  estimate. Temperature-only calibration passes sampling diagnostics and fails
  predictive checks; those failures remain visible.
- Propagated three climate calibrations through 250 emissions states, two forcing
  rules and five sea-level closures. Four assumed expert densities implement the
  recovered inversion method; the target density family remains unrecovered.
- Calculated a full 9,531-coast elevation-resolution comparison and a 250-path
  SSP4 coastal alternative, a 14,750-case HadCRUT5 propagation, and matched
  SSP2, regional income, sampling,
  accounting, horizon, interpolation and economic-prior sensitivities.
- Recovered the cited OP58 glacier observations and compared them with the
  different NSIDC vintage. Kept conditional fits, withheld errors and boundary
  solutions separate from posterior inference.
- Audited two carbon optimizer failures, preserved them, verified an equivalent
  faster chemistry solver, and completed twelve independent-model fits with
  SciPy. Mauna Loa-only holdout RMSE improves to 0.858 ppm; combined Law Dome
  fits retain 6.193/4.330 ppm errors and do not replace coupled parameters.

The base warming-conditioned median incremental costs are
0.208/0.290/0.664/1.217 trillion **2019 USD PPP**, for annual 2010–2100 accounting.
They are not commensurate with the target's 1.2/1.5/2.1/2.6 trillion **2010 USD**,
decadal 2010–2150 calculation. The alternative regional ranking also differs.
The highest base warming bin has five members; its tails are not converged.
The HadCRUT5 alternative has medians 0.216/0.308/0.599/1.117 trillion PPP and
22 high-bin states (effective size 13.6). Its regional ranking also remains
discrepant. Matched coastal sampling and 500 finite-ensemble subsamples quantify
numerical sensitivity; they do not establish population-tail convergence.
More sampling alone cannot recover unmatched calibration and geographic inputs.

## Rebuilding and regenerating

Work only in `/data/data2/ludtke/wong-reproduction`:

```bash
bash scripts/run_all.sh
```

This serial offline driver runs tests and small numerical diagnostics, rechecks
saved calibrations and ensemble results, generates figures, and compiles the
report. It uses committed curated results for the longer simulations. It does
not rerun all MCMC chains or the full geographic and coupled ensembles.
[Detailed regeneration instructions](docs/REPRODUCING.md) give the environment,
input preparation, pilot checks, calibration and simulation commands in order.
The latest executed build evidence is in [BUILD_VERIFICATION.json](docs/BUILD_VERIFICATION.json);
[artifact hashes](results/artifact_sha256.json) identify the verified outputs.
The 13 October continuation build passed **486 Julia assertions and 12 Python
checks**, verified **533 curated artifacts**, and compiled the **61-page report**
in 16.1 minutes. Predictive model failures remain documented separately.

Dependencies available here: Julia 1.7.2 (standard libraries only), Python 3.6.8,
NumPy 1.19.5, SciPy 1.5.4, Matplotlib 3.3.4, TeX Live 2018, Ghostscript 9.27,
Poppler, GCC 8.5 and Git 2.43.5. Optional raw-input preparation uses h5py 3.1.0,
numcodecs 0.9.1 and xlrd 2.0.1; the latter two are project-local. No global
installation changes were made. Use one numerical thread, scheduling priority
19, and one substantial job at a time. All downloads, caches and large
intermediates remain under ignored `.local/`.

## Evidence and independence

No original-author implementation, processed input bundle, posterior sample,
simulation output or plotting script was opened or used. Incidental search
snippets were discarded and logged. Written scientific documentation and
original-provider observations/exogenous inputs are the permitted evidence.
No published figure was digitized. Source URLs, versions, transformations and
hashes are in [SOURCES.csv](docs/SOURCES.csv),
[EXTERNAL_INPUTS.csv](docs/EXTERNAL_INPUTS.csv) and [inputs/README.md](inputs/README.md).

| Record | Purpose |
|---|---|
| [Scientific specifications](docs/RECOVERED_SPECIFICATIONS.md) | Equations, sources, derivations and unresolved definitions |
| [Blocker audit](docs/BLOCKER_AUDIT.md) | Renewed searches and superseded access failures |
| [Figure inventory](docs/FIGURE_STATUS.csv) | All 19 target panel/view/table entries and alternative artifacts |
| [Experiment register](docs/EXPERIMENT_STATUS.csv) | Independent experiments and numerical checks |
| [Assumptions](ASSUMPTIONS.md) and [research log](RESEARCH_LOG.md) | Scientific choices, failures and corrections |
| [Numerical record](docs/NUMERICAL_RECORD.md) | Quantitative validation and diagnostic evidence |
| [Full task](RESEARCH_TASK.md) | Controlling research requirements |

Remaining target dependencies include the complete expert density and joint
calibration, verified annual 3000 m heat observations, matched DIVA/DINAS
inputs, component fingerprints and vertical land motion, and consistent cost
baseline, monetary basis and post-2100 socioeconomic treatment. Unsuccessful
searches are not proof that those inputs do not exist. Finite sampling and
incomplete optimization are recorded separately as computational limitations.

Private repository: [mountaingoat321/wong-reproduction](https://github.com/mountaingoat321/wong-reproduction).
Local `master` tracks `origin/master`; author settings are repository-local.
Follow [AGENTS.md](AGENTS.md), [upstream instructions](AGENTS.upstream.md), and
[Brad Lipovsky's style guide](brad-lipovsky-academic-style-guide.md).
Guidance hashes and original tool checks are in [INITIALIZATION.md](docs/INITIALIZATION.md).
This continuing report does not declare the scientific objective complete.
