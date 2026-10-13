# Regenerating the independent experiments

These commands generate declared alternatives and verification results. They do
not generate the unrecovered target posterior. Run them in dependency order,
serially, from `/data/data2/ludtke/wong-reproduction`. Never fetch target-author
code, processed data bundles, fitted samples or outputs.

## Environment and the offline build

```bash
mkdir -p .local/tmp .local/cache .local/julia .local/matplotlib .local/tex/var .local/tex/config
export TMPDIR="$PWD/.local/tmp" XDG_CACHE_HOME="$PWD/.local/cache"
export JULIA_DEPOT_PATH="$PWD/.local/julia" JULIA_LOAD_PATH=@stdlib
export JULIA_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR="$PWD/.local/matplotlib" MPLBACKEND=Agg
export TEXMFVAR="$PWD/.local/tex/var" TEXMFCONFIG="$PWD/.local/tex/config" TEXMFCACHE="$PWD/.local/tex/var"
bash scripts/run_all.sh
```

The driver requires Julia1.7.2, Python3.6.8 with NumPy1.19.5/SciPy1.5.4/
Matplotlib3.3.4, pdfLaTeX (TeXLive2018), Ghostscript9.27 and Poppler tools.
It uses curated input data, accepted saved posterior samples and ensemble
summaries. It reruns all numerical test suites, small scientific diagnostics,
posterior checks and conditional SSP projections, then regenerates figures and
the PDF. Longer MCMC and geographic/coupled integrations are separate commands
below. Thus an offline build is not a new draw of the full ensemble. The latest
executed build and artifact checksums are recorded in `docs/BUILD_VERIFICATION.json`
and `results/artifact_sha256.json`. A shorter analysis/report rebuild is
`bash scripts/run_extension_analysis.sh`; `--no-build` skips tests and LaTeX.

No global installation or settings changes are needed. All local caches and
raw paths stay under ignored `.local/`. Do not run long commands concurrently.
Input preparation checks source-byte hashes and stops if a live product changes.

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
`scripts/run_coupled_extensions.sh` groups the SSP2 and horizon/interpolation/accounting pilots, matched SSP2 ensemble, corrected carbon-response fits, and HadCRUT5 climate/sea extension. Each component was executed serially; inspect its run metadata and recorded diagnostics. The archived initial carbon optimization failure is not an accepted fit.


## Sampling, economics and climate-constraint extensions

After the base full coastal run, the serial extension driver runs SSP2 and six-
path horizon/interpolation/accounting pilots. Alternatively, select only the
missing commands below to preserve completed work:

```bash
nice -n19 julia --startup-file=no --history-file=no scripts/coastal_coupled_experiments.jl --ssp2 --pilot
python3 scripts/aggregate_coupled_coasts.py --ssp2 --pilot
nice -n19 julia --startup-file=no --history-file=no scripts/coastal_coupled_experiments.jl --ssp2
python3 scripts/aggregate_coupled_coasts.py --ssp2
python3 scripts/aggregate_coupled_coasts.py --draws 4
python3 scripts/aggregate_coupled_coasts.py --draws 8
python3 scripts/coastal_sampling_sensitivity.py
python3 scripts/compare_coastal_assumptions.py
```

`compare_coastal_assumptions.py --from-saved` needs only curated aggregates.
Horizon/within-node pilots use `--pilot` with each of `--horizon-freeze`,
`--horizon-growth`, `--geometric-economy` and `--accounting`, followed by the same
flag on `aggregate_coupled_coasts.py`. These six-path samples are purposive and
must not be assigned ensemble probabilities. Geographic sampling comparisons
use common nested draws; the 500 climate subsamples preserve emissions strata.

Economic sensitivity executes six documented marginal priors with independent
sampling and explicit relative valuation mappings. Each draw has its own
optimized no-rise control:

```bash
nice -n19 julia --startup-file=no --history-file=no scripts/coastal_coupled_experiments.jl --economic-priors --pilot
python3 scripts/aggregate_economic_sensitivity.py --pilot
nice -n19 julia --startup-file=no --history-file=no scripts/coastal_coupled_experiments.jl --economic-priors
python3 scripts/aggregate_economic_sensitivity.py
```

The full run has 16 draws plus the central point, six paths, 31 distinct sampled
coasts and 3,162 cases. Replot with `--from-saved`; sample extrema are not credible
limits. Prior correlations and initial valuation mappings remain assumptions.

The HadCRUT5 climate/sea extension follows the base tail-stratified commands
with `--hadcrut5` added to each Julia climate/sea pilot and full command. Complete
its own reference calculation before the coastal extension:

```bash
nice -n19 julia --startup-file=no --history-file=no scripts/sea_level_reference.jl --hadcrut5
python3 scripts/plot_sea_level_reference.py --hadcrut5
bash scripts/run_temperature_only_extension.sh
python3 scripts/compare_coupled_climate_vintages.py
bash scripts/run_hadcrut5_coastal_extension.sh
```

The temperature-only driver independently checks its pilot, propagates 250
paths through five sea-level closures and both forcing rules, and writes its
own 1995–2014 reference correction. It deliberately tests a posterior that fails
predictive observations; it is not a preferred replacement. The HadCRUT5 coastal
driver has a separate six-path pilot before 250 paths and 59 distinct coasts,
with eight draws per region, then creates its aggregate and comparison plots.
Neither driver overwrites the base HadCRUT4 ensemble. Comparison of independently
sampled physical states is a distribution comparison, not a paired causal effect.

The four explicit expert-density inversions and accounting checks are cheap:

```bash
python3 tests/test_emissions_inversion.py
python3 scripts/emissions_inversion_sensitivity.py
python3 scripts/coastal_accounting_sensitivity.py --from-saved
```

The recovered prior-times-density inversion method does not recover the missing
expert density family or width. It differs from imposing a posterior event mass.

## Glacier versions and carbon optimization audit

```bash
python3 scripts/prepare_glacier_vintage.py
nice -n19 julia --startup-file=no --history-file=no scripts/glacier_vintage_fit.jl
python3 scripts/plot_glacier_vintage.py
python3 scripts/prepare_glacier_op58.py
nice -n19 julia --startup-file=no --history-file=no scripts/glacier_vintage_fit.jl --op58
python3 scripts/plot_glacier_vintage.py --op58
nice -n19 julia --startup-file=no --history-file=no tests/bounded_least_squares.jl
nice -n19 julia --startup-file=no --history-file=no scripts/carbon_vintage_fit.jl --free-physics --pilot
nice -n19 julia --startup-file=no --history-file=no scripts/carbon_vintage_fit.jl --free-physics
python3 scripts/plot_carbon_parameter_sensitivity.py
```

Both glacier sources have 43 annual values but differ; they remain separate.
Each conditional experiment evaluates 27 physical grid points for each of two
temperature versions. The selected boundary minima are not posterior estimates.
OP58 preparation extracts a printed numeric table, never a digitized figure.
Optional original spreadsheet preparation requires `xlrd==2.0.1`, installed only
inside `.local/python` with local `PIP_CACHE_DIR` and `TMPDIR`. The offline build
needs neither spreadsheet libraries nor PDF downloads.

The carbon free-physics pilot first audits the restricted fits with the corrected
solver, then runs synthetic parameter recovery and a nested-start fit. The full
run uses four starts for each of three observational choices. The default command
without `--free-physics` preserves the legacy restricted experiment. Corrected
restricted files use `carbon_vintage_revised_*`; failed original free-search
files remain `carbon_vintage_free_failed_linesearch_*`. Solver stops, gradients,
holdouts, integration and mass checks must all be inspected. Four starts do not
prove global optimality. The new fits do not silently replace coupled carbon
point parameters.

## Historical sea-level budget check

```bash
nice -n19 julia --startup-file=no --history-file=no scripts/sea_level_hindcast.jl --pilot
nice -n19 julia --startup-file=no --history-file=no scripts/sea_level_hindcast.jl
python3 scripts/plot_sea_level_hindcast.py
```

This compares the 1990.5–2009.5 component sum with Church–White observations,
centering each series over 1995.5–2004.5. It retains saved emissions-prior weights,
fixed Antarctic fits and independent component marginals. The observation record
also enters Antarctic boundary forcing; this is a consistency diagnostic, not an
independent holdout or a recovered rejection-sampling calibration. Reported
intervals exclude missing joint covariance and stochastic model discrepancies.
