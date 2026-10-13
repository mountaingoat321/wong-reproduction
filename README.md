# Independent reconstruction of Wong et al. (2025)

Target: **Coastal adaptation and damage costs at different global warming
thresholds**, npj Natural Hazards 2, 35,
[DOI 10.1038/s44304-025-00089-0](https://doi.org/10.1038/s44304-025-00089-0).

**Active continuation: verified mechanisms and alternative experiments; target
numerical figures remain unreproduced.** Independent Julia implementations now
include coupled DOECLIM heat transport, a mass-conserving carbon-cycle alternative,
geometric Antarctic dynamics, and annual coastal adaptation cash flows. A
converged temperature-only calibration fails held-out observational checks; that
failure is retained, and a joint temperature/heat calibration improves holdout predictions but underestimates AR6 warming.
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

This serial driver runs the Julia test suites and Python MCMC-diagnostic
tests, regenerates mechanism and sensitivity experiments, audits coastal inputs,
checks saved climate and ice posteriors, generates 1,000-draw SSP projections,
and builds all current figures and the PDF. The saved posterior is rechecked;
MCMC itself is a separate, longer calculation. A sampler convergence pass does
not imply predictive validity. The observational holdouts document that distinction.
Geographic figures use committed aggregates; their longer simulation commands
are below. The driver does not claim to reproduce the target 5,000-member
global-cost ensemble.

Available dependencies: Julia 1.7.2 (standard libraries only), Python 3.6.8,
NumPy 1.19.5, SciPy 1.5.4, Matplotlib 3.3.4, pdfLaTeX/TeX Live 2018,
GCC 8.5 and Git 2.43.5. Ghostscript9.27 and Poppler's `pdffonts` subset embedded
figure fonts before LaTeX; vector artwork is retained. Optional raw GTSR preparation uses installed h5py 3.1.0.
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
The revised joint run passes convergence checks. Held-out temperature RMSE is
0.087 K, but its SSP2-4.5 late-century warming is 0.727 K below the AR6 best estimate.
After regenerating an accepted run, rerun `scripts/plot_continuation.py` and the report build.

Independent ice-observation preparation and new conditional component fits use
`scripts/prepare_ice_observations.py`, `tests/ice_models.jl`, and
`scripts/ice_calibration.jl`. Both longer runs pass convergence diagnostics;
the initial failures remain recorded. These are conditional rate calibrations
with different observations and residual priors. Run the calibration once, then
`python3 scripts/assess_calibration.py --ice glaciers`,
`python3 scripts/assess_calibration.py --ice greenland`, and
`julia --startup-file=no --history-file=no scripts/ice_projections.jl`.
Held-out ice observations are evaluated conditional on known temperature;
the glacier equation performs worse than a simple training-trend baseline.

Geographic alternatives use the independently published SLIIDERS inputs. A
19-coast pilot and an independent narrow-hazard test verified numerical
quadrature before scaling. Regeneration commands, in the same local environment:

```bash
nice -n 19 julia --startup-file=no --history-file=no scripts/geographic_experiments.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/geographic_experiments.jl --quadrature-check
nice -n 19 julia --startup-file=no --history-file=no scripts/geographic_experiments.jl --all
python3 scripts/prepare_regions.py
python3 scripts/aggregate_geographic.py
```

The full alternative covers 9,531 eligible coast-country units. The 43 exclusions
are listed in `results/geographic_input_exclusions.csv`. It uses prescribed
0.5/1/2m rise in 2100, SSP2/SSP4 OECD economics, annual accounting, 2019 USD PPP,
and no geographical sea-level fingerprints. This is **not a reproduction** of
Wong's warming-conditioned 2010–2150 ensemble. Full per-coast intermediates go
to `.local/`; completed country/global/regional summaries are retained in
`results/`. Regional GDP comparisons cover about98.1% of incremental costs.
The coarse full run completed57,186cases in838seconds on one CPU.

The original0.1m elevation pilot changes2of114policy choices and summed
incremental cost by9.6%; it is not extrapolated globally. Raw SLIIDERS preparation
uses optional `numcodecs==0.9.1`, installed only in `.local/python` (recorded
NumPy/SciPy/Matplotlib installations remain untouched). If needed, set
`PIP_CACHE_DIR="$PWD/.local/cache/pip"` and the local `TMPDIR` above, then run
`python3 -m pip install --no-deps --only-binary=:all: --target "$PWD/.local/python" numcodecs==0.9.1`.
After the checksum-verified raw input download, use:

```bash
python3 scripts/prepare_sliiders.py --fine-pilot
nice -n19 julia --startup-file=no --history-file=no scripts/geographic_experiments.jl --fine-profiles
nice -n19 julia --startup-file=no --history-file=no scripts/geographic_experiments.jl --fine-profiles --quadrature-check
python3 scripts/audit_geographic_elevation.py
python3 scripts/prepare_sliiders.py --fine-all
nice -n19 julia --startup-file=no --history-file=no scripts/geographic_experiments.jl --all --fine-profiles --ssp4-one-metre
```

The last command completed all9,531 units in1,812 seconds, including short
pauses for serial validation work. Run `python3 scripts/aggregate_geographic.py
--fine-ssp4-one-metre` and `python3 scripts/compare_geographic_resolution.py`
afterward. Global incremental cost rises11.03% relative to six bins and148
policies change. This is a matched alternative experiment, not a correction
to the published costs. Binary original-resolution input
arrays and full per-coast output stay in ignored `.local/`.

## Paleo and emissions continuation

New independent inputs are explicitly listed and hash checked in
`docs/EXTERNAL_INPUTS.csv`; `scripts/prepare_external_inputs.py` fetches only
that allowlist. It never traverses target-author repositories. Prepare the
curated boundary and scenario inputs with:

```bash
python3 scripts/prepare_paleo_inputs.py
python3 scripts/prepare_dais_forcing.py
python3 scripts/prepare_ssp_emissions.py
```

The Antarctic experiment uses a recovered initial radius and independent
temperature/sea-level proxies. The ocean polynomial, splice and cutoff
continuation are explicit alternatives. Generate its36 sensitivities and a
restricted conditional point fit with:

```bash
nice -n19 julia --startup-file=no --history-file=no scripts/dais_paleo_experiments.jl
nice -n19 julia --startup-file=no --history-file=no scripts/dais_conditional.jl --pilot
nice -n19 julia --startup-file=no --history-file=no scripts/dais_conditional.jl
python3 scripts/plot_paleo.py
```

The fit is not a posterior or independent validation of the four fitted
constraints. Later annual IMBIE rates supply a separate check. The build
rechecks the saved fit and timestep refinement without repeating optimization.

Emissions experiments distinguish the documented prior from minimum-relative-
entropy50%/75% budget weighting. The latter do not recover the expert density
or impose the SSP4-6.0 mode. Coupled futures compare annual nearest-emissions
and fixed-SSP2-4.5 non-CO2 forcing using independent RCMIP inputs:

```bash
nice -n19 julia --startup-file=no --history-file=no scripts/emissions_design.jl
nice -n19 julia --startup-file=no --history-file=no scripts/coupled_emissions_experiments.jl --pilot
nice -n19 julia --startup-file=no --history-file=no scripts/coupled_emissions_experiments.jl
python3 scripts/plot_scenario_alternatives.py
python3 scripts/scenario_tables.py
```

The pilot checks doubled temporal resolution before the larger256-member
alternative. Raw future paths stay under `.local/`; the repository retains
parameters, endpoints, quantiles, category probabilities and nested-sample
diagnostics. The build reruns the small pilot and plots the retained larger
results. This remains an alternative conditional experiment with fixed carbon
parameters, omitted target dependence and a disclosed forcing restart jump.

`scripts/sea_level_ensemble.jl --pilot` combines the verified component models
for eight climate members, two forcing rules and five explicit closure choices.
It checks doubled Antarctic temporal resolution and component sums. Its raw
paths stay in `.local/`; metadata, endpoints and quantiles remain in `results/`.
The Antarctic shore factors−1/+1 are documented in B17. The global component
sum remains an **uncorrected alternative** because observational component
overlap and the target joint calibration are unresolved. Larger tail-stratified
extensions and coastal probability-sampling experiments are active development;
their run metadata must exist before they can be treated as executed results.

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
