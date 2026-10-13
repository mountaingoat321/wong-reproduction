#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
[[ "$ROOT" == /data/data2/ludtke/wong-reproduction ]] || { echo 'Unexpected project root'; exit 1; }
cd "$ROOT"
mkdir -p .local/tmp .local/cache .local/matplotlib .local/julia .local/tex/var .local/tex/config results figures report
export TMPDIR="$ROOT/.local/tmp" XDG_CACHE_HOME="$ROOT/.local/cache" MPLCONFIGDIR="$ROOT/.local/matplotlib"
export JULIA_DEPOT_PATH="$ROOT/.local/julia" JULIA_LOAD_PATH='@stdlib'
export TEXMFVAR="$ROOT/.local/tex/var" TEXMFCONFIG="$ROOT/.local/tex/config" TEXMFCACHE="$ROOT/.local/tex/var"
export JULIA_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg SOURCE_DATE_EPOCH=1791849600
for tool in julia python3 pdflatex gs pdffonts; do command -v "$tool" >/dev/null; done
nice -n 19 julia --startup-file=no --history-file=no tests/runtests.jl
nice -n 19 julia --startup-file=no --history-file=no tests/recovered_models.jl
nice -n 19 julia --startup-file=no --history-file=no tests/climate_modes.jl
nice -n 19 julia --startup-file=no --history-file=no tests/carbon.jl
nice -n 19 julia --startup-file=no --history-file=no tests/coastal_paths.jl
nice -n 19 julia --startup-file=no --history-file=no tests/geographic_coasts.jl
nice -n 19 julia --startup-file=no --history-file=no tests/ice_models.jl
nice -n 19 julia --startup-file=no --history-file=no tests/calibration.jl
nice -n 19 julia --startup-file=no --history-file=no tests/paleo_dais.jl
nice -n 19 julia --startup-file=no --history-file=no tests/scenario_design.jl
nice -n 19 julia --startup-file=no --history-file=no tests/sea_level_coupling.jl
nice -n 19 python3 tests/test_mcmc_diagnostics.py
nice -n 19 python3 tests/test_coastal_sampling.py
nice -n 19 python3 tests/test_emissions_inversion.py
nice -n 19 julia --startup-file=no --history-file=no scripts/diagnostics.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/recovered_diagnostics.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/dais_events.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/dais_paleo_experiments.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/dais_conditional.jl --check-saved
nice -n 19 julia --startup-file=no --history-file=no scripts/emissions_design.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/coupled_emissions_experiments.jl --pilot
nice -n 19 julia --startup-file=no --history-file=no scripts/carbon_experiments.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/carbon_fit.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/coastal_experiments.jl
nice -n 19 python3 scripts/thermal_observations.py
nice -n 19 python3 scripts/audit_inputs.py
nice -n 19 python3 scripts/assess_calibration.py
nice -n 19 julia --startup-file=no --history-file=no scripts/climate_projections.jl
nice -n 19 python3 scripts/assess_calibration.py --joint-heat
nice -n 19 julia --startup-file=no --history-file=no scripts/climate_projections.jl --joint-heat
nice -n 19 python3 scripts/assess_calibration.py --joint-heat --hadcrut5
nice -n 19 julia --startup-file=no --history-file=no scripts/climate_projections.jl --joint-heat --hadcrut5
nice -n 19 python3 scripts/assess_calibration.py --ice glaciers
nice -n 19 python3 scripts/assess_calibration.py --ice greenland
nice -n 19 julia --startup-file=no --history-file=no scripts/ice_projections.jl
nice -n 19 python3 scripts/audit_geographic_quadrature.py
nice -n 19 python3 scripts/audit_geographic_elevation.py
nice -n 19 python3 scripts/verify_results.py
nice -n 19 python3 scripts/check_coupled_results.py
nice -n 19 python3 scripts/plot_results.py
nice -n 19 python3 scripts/plot_continuation.py
nice -n 19 python3 scripts/plot_extended.py
nice -n 19 python3 scripts/plot_paleo.py
nice -n 19 python3 scripts/plot_scenario_alternatives.py
nice -n 19 python3 scripts/plot_sea_level_alternatives.py
nice -n 19 python3 scripts/plot_sea_level_reference.py --from-saved
nice -n 19 python3 scripts/plot_observation_vintages.py
nice -n 19 python3 scripts/plot_coastal_coupled.py
nice -n 19 python3 scripts/coastal_accounting_sensitivity.py --from-saved
nice -n 19 python3 scripts/emissions_inversion_sensitivity.py
nice -n 19 python3 scripts/report_tables.py
nice -n 19 python3 scripts/extended_tables.py
nice -n 19 python3 scripts/scenario_tables.py
nice -n 19 python3 scripts/subset_figure_fonts.py
nice -n 19 pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -output-directory=report report/report.tex > .local/tex/pass1.txt 2>&1
nice -n 19 pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -output-directory=report report/report.tex > .local/tex/pass2.txt 2>&1
python3 scripts/check_artifacts.py
echo 'Offline verification, alternative experiments and report build complete. Target global ensemble remains unresolved.'
