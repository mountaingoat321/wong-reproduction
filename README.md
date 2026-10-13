# Independent reconstruction of Wong et al. (2025)

Target: **Coastal adaptation and damage costs at different global warming
thresholds**, npj Natural Hazards 2, 35,
[DOI 10.1038/s44304-025-00089-0](https://doi.org/10.1038/s44304-025-00089-0).

**Active continuation: verified mechanisms and alternative experiments; target
numerical figures remain unreproduced.** Independent Julia implementations now
include coupled DOECLIM heat transport, a mass-conserving carbon-cycle alternative,
geometric Antarctic dynamics, and annual coastal adaptation cash flows. A
converged temperature-only calibration fails held-out observational checks; that
failure is retained, and a joint temperature/heat calibration is being evaluated.
These are research results and diagnostics, not recovered Wong posterior draws.

No target-author implementation, processed bundle, simulation output, posterior
sample or plotting script was consulted. Permitted independent observations and
exogenous inputs are documented in [inputs/README.md](inputs/README.md).
Main figures 1–3, supplementary figures S1–S10 and modeled Table 1 remain
**Not reproduced**. Figure 4 is an original **Conceptual schematic**. Alternative
figures are explicitly labeled non-reproductions. See the
[figure inventory](docs/FIGURE_STATUS.csv), [blocker audit](docs/BLOCKER_AUDIT.md),
[experiment register](docs/EXPERIMENT_STATUS.csv), and
[continuing scientific report](report/report.pdf).

## Offline verification and rebuilding

Work only in `/data/data2/ludtke/wong-reproduction`:

```bash
bash scripts/run_all.sh
```

This serial driver runs the five Julia test suites and Python MCMC-diagnostic
tests, regenerates mechanism and sensitivity experiments, audits coastal inputs,
checks the saved temperature posterior, generates 1,000-draw SSP projections,
and builds all current figures and the PDF. The saved posterior is rechecked;
MCMC itself is a separate, longer calculation. A sampler convergence pass does
not imply predictive validity. The observational holdouts document that distinction.
The driver does not claim to reproduce the target 5,000-member global-cost ensemble.

Available dependencies: Julia 1.7.2 (standard libraries only), Python 3.6.8,
NumPy 1.19.5, SciPy 1.5.4, Matplotlib 3.3.4, pdfLaTeX/TeX Live 2018,
GCC 8.5 and Git 2.43.5. Optional raw GTSR preparation uses installed h5py 3.1.0.
No installation or global configuration changes are required. All numerical
libraries use one thread and scheduling priority 19. Caches, downloads and TeX
state remain under ignored `.local/`. Do not run multiple long jobs concurrently
on the shared server.

## Recalibration and input acquisition

The raw input preparation and scholarly-document acquisition are separate from
the offline build:

```bash
python3 scripts/fetch_sources.py
python3 scripts/prepare_external_inputs.py
```

Both restrict acquisition to documented sources. The input script checks raw-byte
hashes and stops on a changed live product; committed curated subsets support
an offline rebuild. Spreadsheet cell values are read without executing content.
Exact URLs, licenses, subsets and hashes are in `docs/EXTERNAL_INPUTS.csv`.

To regenerate the temperature-only posterior, use this environment and run the
commands serially. The configuration records seed, priors, training/holdout
periods, warmup, chain length, thinning and numerical resolution.

```bash
export JULIA_DEPOT_PATH="$PWD/.local/julia" JULIA_LOAD_PATH=@stdlib
export JULIA_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export TMPDIR="$PWD/.local/tmp" PYTHONDONTWRITEBYTECODE=1
nice -n 19 julia --startup-file=no --history-file=no scripts/climate_calibration.jl
python3 scripts/assess_calibration.py
nice -n 19 julia --startup-file=no --history-file=no scripts/climate_projections.jl
```

The corresponding joint temperature/700m-heat experiment adds `--joint-heat`
to each of those three commands and uses `config/climate_joint_calibration.toml`.
The projection script refuses an unconverged posterior. The first joint run
failed convergence; its diagnostics remain under `climate_joint_initial_*`.
Its unaccepted samples are kept only in ignored local storage. A revised sampler
uses logarithmic innovation scales, logit correlations and a recent warmup
covariance window, preserving the same physical-coordinate priors by Jacobians.
This experiment is in progress; its commands are not a claim of validated output.
After an accepted run, rerun `scripts/plot_continuation.py` and the report build.

## Scientific record

| Location | Purpose |
|---|---|
| [report/report.pdf](report/report.pdf) and [source](report/report.tex) | Equations, generated figures, comparisons, limitations and AI-process assessment. |
| [docs/RECOVERED_SPECIFICATIONS.md](docs/RECOVERED_SPECIFICATIONS.md) | Recovered physical and economic methods, with explicit derivations and alternatives. |
| [docs/FIGURE_STATUS.csv](docs/FIGURE_STATUS.csv) | All 19 target figure/view/table entries and linked alternative work. |
| [docs/EXPERIMENT_STATUS.csv](docs/EXPERIMENT_STATUS.csv) | Independent experiments and their validation status. |
| [docs/SOURCES.csv](docs/SOURCES.csv), [inputs/README.md](inputs/README.md) | Scientific writing and independently acquired input provenance. |
| `src/`, `tests/`, `config/`, `scripts/` | Independent implementations, verification, parameter choices and execution commands. |
| `results/`, `figures/` | Small curated computed data and original PDF/PNG figures. |
| [ASSUMPTIONS.md](ASSUMPTIONS.md), [RESEARCH_LOG.md](RESEARCH_LOG.md) | Scientific choices, source access, failures, corrections and execution record. |
| [RESEARCH_TASK.md](RESEARCH_TASK.md) | Full controlling research requirements. |

Analytical, conservation, numerical-convergence and accounting checks establish
implementation properties. They do not establish that a model or dataset is the
one used in the target publication. Remaining work includes carbon and sea-level
calibration, emissions inversion, and independently recovered elevation-area,
exposure, economic, fingerprint and vertical-land-motion inputs. These are active
research tasks, not a declaration that reproduction is impossible or complete.

## Repository and instructions

Existing private repository: [mountaingoat321/wong-reproduction](https://github.com/mountaingoat321/wong-reproduction).
Local `master` tracks `origin/master`. Git author is Sophia Ludtke, with the
user-supplied email; global settings are unchanged. Instructions are
[AGENTS.md](AGENTS.md), [Brad Lipovsky's original instructions](AGENTS.upstream.md),
and the [academic style guide](brad-lipovsky-academic-style-guide.md).
Guidance source revisions and hashes, and original environment/authentication
checks, are preserved in [docs/INITIALIZATION.md](docs/INITIALIZATION.md).
