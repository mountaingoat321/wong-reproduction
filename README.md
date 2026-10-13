# Independent reconstruction of Wong et al. (2025)

Target: **Coastal adaptation and damage costs at different global warming
thresholds**, npj Natural Hazards 2, 35,
[DOI 10.1038/s44304-025-00089-0](https://doi.org/10.1038/s44304-025-00089-0).

**Active continuation: verified mechanisms and alternative experiments; target
numerical figures remain unreproduced.** Independent Julia implementations now
include coupled DOECLIM heat transport, a mass-conserving carbon-cycle alternative,
geometric Antarctic dynamics, and annual coastal adaptation cash flows. A
converged temperature-only calibration fails held-out observational checks; that
failure is retained, and joint temperature/heat calibrations improve holdout predictions but underestimate AR6 warming. A documented HadCRUT5-version fit passes convergence and held-out checks. A250-member coupled alternative now reaches global/regional coastal costs and planned movement, with explicit coastal sampling errors.
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
overlap and the target joint calibration are unresolved. The250-member tail extension, five sea-level closures and two forcing rules are complete. The SSP4 coastal ensemble uses119distinct probability-sampled coasts with the original200-bin profiles;16draws per region. This is29,750climate/coast combinations. Conditional global samplingSE is6.26%median and9.22%maximum. The highest warming category has only5members/ESS4.23, so its tail percentiles are not converged.

## Coupled alternatives and observation-version recovery

The extended sea-level and coastal experiments retain exact empirical emissions
stratum masses. An initial8/16-substep tail pilot failed the CO2 tolerance;
its preserved results have the `dt8` label. The accepted16/32-substep pilot
passes before250members are run. In the same one-thread environment above:

```bash
nice -n19 julia --startup-file=no --history-file=no scripts/coupled_emissions_experiments.jl --tail-stratified --pilot
nice -n19 julia --startup-file=no --history-file=no scripts/coupled_emissions_experiments.jl --tail-stratified
nice -n19 julia --startup-file=no --history-file=no scripts/sea_level_ensemble.jl --tail-stratified --pilot
nice -n19 julia --startup-file=no --history-file=no scripts/sea_level_ensemble.jl --tail-stratified
nice -n19 julia --startup-file=no --history-file=no scripts/sea_level_reference.jl
python3 scripts/plot_sea_level_alternatives.py
python3 scripts/plot_sea_level_reference.py
python3 scripts/coastal_sampling_design.py
nice -n19 julia --startup-file=no --history-file=no scripts/coastal_coupled_experiments.jl --pilot
python3 scripts/aggregate_coupled_coasts.py --pilot
nice -n19 julia --startup-file=no --history-file=no scripts/coastal_coupled_experiments.jl
python3 scripts/aggregate_coupled_coasts.py
python3 scripts/plot_coastal_coupled.py
python3 scripts/check_coupled_results.py
```

The coastal design requires the completed fine-resolution1m control and raw
original-provider elevation profiles described above. All future paths and
per-coast outputs stay in `.local/`; parameters, endpoints, weighted summaries,
sampling errors and run metadata are retained. `plot_sea_level_reference.py
--from-saved` regenerates its figure from committed quantiles without raw paths.
The full SSP4 run took3016wallseconds including controlled pauses. Its50%-budget
median costs0.208/0.290/0.664/1.217trillion2019PPP use different units, baseline
and horizon from the target. Regional inequality does not reproduce the target
pattern. Planned movement includes initialization, not unique lifetime migrants.

New observation inputs are prepared with
`python3 scripts/prepare_calibration_vintages.py`. The importance-reweighting
experiment (`scripts/climate_vintage_sensitivity.jl`, then
`scripts/assess_vintage_predictive.py`) fails with effective weight sample14.1.
Do not use those weights as an accepted posterior. The independent replacement
fit uses:

```bash
nice -n19 julia --startup-file=no --history-file=no scripts/climate_calibration.jl --joint-heat --hadcrut5
python3 scripts/assess_calibration.py --joint-heat --hadcrut5
nice -n19 julia --startup-file=no --history-file=no scripts/climate_projections.jl --joint-heat --hadcrut5
nice -n19 julia --startup-file=no --history-file=no scripts/carbon_vintage_fit.jl --pilot
nice -n19 julia --startup-file=no --history-file=no scripts/carbon_vintage_fit.jl
python3 scripts/plot_observation_vintages.py
```

HadCRUT5 calibration retains20000draws and passes all declared criteria;
holdouttemperatureRMSE0.0854K. Restricted carbon fits fail transfer to later
CO2 observations; they are retained and are not used in the coastal ensemble.
`scripts/run_coupled_extensions.sh` runs the next serial sensitivity stage:
SSP2 and horizon/interpolation/accounting pilots, a matched SSP2 ensemble,
carbon-response fits, and a separately validated HadCRUT5 climate/sea extension.
This checkpoint was made while that stage was running. Treat only experiments
with completed run metadata and recorded diagnostics as executed results.

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
one used in the target publication. Remaining work includes full joint carbon/sea-level calibration, emissions inversion, matching the original exposure/economic inputs, and recovering compatible fingerprints and vertical-land motion. Independent elevation/exposure/economic alternatives have already been acquired and simulated. These are active
research tasks, not a declaration that reproduction is impossible or complete.

## Repository and instructions

Existing private repository: [mountaingoat321/wong-reproduction](https://github.com/mountaingoat321/wong-reproduction).
Local `master` tracks `origin/master`. Git author is Sophia Ludtke, with the
user-supplied email; global settings are unchanged. Instructions are
[AGENTS.md](AGENTS.md), [Brad Lipovsky's original instructions](AGENTS.upstream.md),
and the [academic style guide](brad-lipovsky-academic-style-guide.md).
Guidance source revisions and hashes, and original environment/authentication
checks, are preserved in [docs/INITIALIZATION.md](docs/INITIALIZATION.md).

The further inversion audit reads Fuller et al.2017's scientific likelihood
method. Four explicitly assumed expert PDFs satisfy the documented budget mass
and SSP460 conditional mode, but give posterior budget probabilities4.56–11.31%.
They are not recovered target distributions. Reproduce the executed lightweight
analyses with `python3 tests/test_emissions_inversion.py`,
`python3 scripts/emissions_inversion_sensitivity.py` and
`python3 scripts/coastal_accounting_sensitivity.py --from-saved`.
The complete offline driver passed372 Julia assertions and9 Python checks;
the3 new inversion checks also passed and have been added to that driver.

Further source recovery and numerical diagnostics:
- `python3 scripts/prepare_glacier_vintage.py` curates the original NSIDC2005
  spreadsheet. Its annual global means differ from OP58; see input audit.
- `julia --startup-file=no --history-file=no scripts/glacier_vintage_fit.jl`
  and `python3 scripts/plot_glacier_vintage.py` regenerate54conditional fits and
  their withheld-data comparison. Executed successfully; no posterior claim.
- `julia --startup-file=no --history-file=no scripts/coastal_coupled_experiments.jl --economic-priors --pilot`
  then `python3 scripts/aggregate_economic_sensitivity.py --pilot` passed.
  Remove `--pilot` to run16economic draws across6purpose paths. That extension
  is queued serially at this checkpoint, not yet reported complete.
- `bash scripts/run_temperature_only_extension.sh` is queued after the economic
  extension. It runs pilots before propagating250temperature-only climate draws.
  `python3 scripts/compare_coupled_climate_vintages.py` requires all three
  completed climate/sea-level variants and also applies the four expert PDFs.
Use the project-local caches and one-thread environment documented above.

The matched SSP2extension and sampling/horizon analyses are now complete.
`scripts/coastal_sampling_sensitivity.py` regenerates500subsamples and the
4/8/16coastal-draw comparison. `scripts/compare_coastal_assumptions.py
--from-saved` rebuilds SSP2/SSP4regional and income-contrast figures without
large inputs. They addressS1/S2/S8/S9as explicitnon-reproductions.

`python3 scripts/prepare_glacier_op58.py` separately acquires the now-recovered
cited observational report; `julia scripts/glacier_vintage_fit.jl --op58` and
`python3 scripts/plot_glacier_vintage.py --op58` completed the54conditionalfits.
The olderNSIDC spreadsheetprep optionally requires `xlrd==2.0.1`, installed
only with `python3 -m pip install --no-deps --target "$PWD/.local/python"
xlrd==2.0.1` after setting the localPIPcache/TMPDIR above. The offlinebuild
reads curatedCSV and needs neitherxlrd nor rawPDF/XLS downloads.

The firstfreecarbonsearch is preserved under `carbon_vintage_free_failed_linesearch_*`: its
trainingobjective failed the nested-model test. The revised solver passes6analytic
checks and adds the restrictedfit as a fourthstart. Thephysicalpilot/refit are
queued after the otheractiveextensions; the initialfreefits are not accepted.
`scripts/run_extension_analysis.sh` rebuilds completedextensionanalyses andthe
report from curatedoutputs; its complete execution is pending these integrations.
