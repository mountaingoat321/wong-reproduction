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
for tool in julia python3 pdflatex; do command -v "$tool" >/dev/null; done
nice -n 19 julia --startup-file=no --history-file=no tests/runtests.jl
nice -n 19 julia --startup-file=no --history-file=no tests/recovered_models.jl
nice -n 19 julia --startup-file=no --history-file=no tests/carbon.jl
nice -n 19 julia --startup-file=no --history-file=no tests/coastal_paths.jl
nice -n 19 julia --startup-file=no --history-file=no tests/calibration.jl
nice -n 19 python3 tests/test_mcmc_diagnostics.py
nice -n 19 julia --startup-file=no --history-file=no scripts/diagnostics.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/recovered_diagnostics.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/dais_events.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/carbon_experiments.jl
nice -n 19 julia --startup-file=no --history-file=no scripts/coastal_experiments.jl
nice -n 19 python3 scripts/thermal_observations.py
nice -n 19 python3 scripts/audit_inputs.py
nice -n 19 python3 scripts/assess_calibration.py
nice -n 19 julia --startup-file=no --history-file=no scripts/climate_projections.jl
nice -n 19 python3 scripts/verify_results.py
nice -n 19 python3 scripts/plot_results.py
nice -n 19 python3 scripts/plot_continuation.py
nice -n 19 python3 scripts/report_tables.py
nice -n 19 pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -output-directory=report report/report.tex > .local/tex/pass1.txt 2>&1
nice -n 19 pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -output-directory=report report/report.tex > .local/tex/pass2.txt 2>&1
python3 scripts/check_artifacts.py
echo 'Offline verification, alternative experiments and report build complete. Target global ensemble remains unresolved.'
