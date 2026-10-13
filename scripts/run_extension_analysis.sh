#!/usr/bin/env bash
# Rebuild extension analyses from curated outputs; no large integrations or network.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
[[ "$ROOT" == /data/data2/ludtke/wong-reproduction ]] || exit 1
cd "$ROOT"
export TMPDIR="$ROOT/.local/tmp" XDG_CACHE_HOME="$ROOT/.local/cache" MPLCONFIGDIR="$ROOT/.local/matplotlib"
export JULIA_DEPOT_PATH="$ROOT/.local/julia" JULIA_LOAD_PATH=@stdlib
export JULIA_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg SOURCE_DATE_EPOCH=1791849600
export TEXMFVAR="$ROOT/.local/tex/var" TEXMFCONFIG="$ROOT/.local/tex/config" TEXMFCACHE="$ROOT/.local/tex/var"
nice -n19 python3 scripts/coastal_sampling_sensitivity.py
nice -n19 python3 scripts/compare_coastal_assumptions.py --from-saved
nice -n19 python3 scripts/aggregate_economic_sensitivity.py --from-saved
nice -n19 python3 scripts/plot_glacier_vintage.py
nice -n19 python3 scripts/plot_glacier_vintage.py --op58
nice -n19 julia --startup-file=no --history-file=no scripts/carbon_search_diagnostics.jl
nice -n19 python3 scripts/plot_carbon_parameter_sensitivity.py
nice -n19 python3 scripts/plot_sea_level_reference.py --hadcrut5 --from-saved
nice -n19 python3 scripts/plot_sea_level_reference.py --temperature-only --from-saved
nice -n19 python3 scripts/compare_coupled_climate_vintages.py
nice -n19 python3 scripts/plot_sea_level_hindcast.py
nice -n19 python3 scripts/plot_coastal_coupled.py --hadcrut5
nice -n19 python3 scripts/compare_coastal_climate_constraints.py
nice -n19 python3 scripts/coastal_hadcrut5_resampling.py
nice -n19 python3 scripts/check_extension_results.py
if [[ "${1:-}" != --no-build ]]; then
    nice -n19 julia --startup-file=no --history-file=no tests/bounded_least_squares.jl
    nice -n19 python3 tests/test_emissions_inversion.py
    nice -n19 python3 scripts/report_tables.py
    nice -n19 python3 scripts/subset_figure_fonts.py
    nice -n19 pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -output-directory=report report/report.tex > .local/tex/extension_pass1.txt 2>&1
    nice -n19 pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -output-directory=report report/report.tex > .local/tex/extension_pass2.txt 2>&1
    python3 scripts/check_artifacts.py
fi
