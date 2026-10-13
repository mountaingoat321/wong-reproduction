#!/usr/bin/env bash
# Conditional diagnostic of the consequential ocean-heat constraint.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
[[ "$ROOT" == /data/data2/ludtke/wong-reproduction ]] || exit 1
cd "$ROOT"
export TMPDIR="$ROOT/.local/tmp" PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR="$ROOT/.local/matplotlib"
export JULIA_DEPOT_PATH="$ROOT/.local/julia" JULIA_LOAD_PATH=@stdlib
export JULIA_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
run_julia() { nice -n19 julia --startup-file=no --history-file=no "$@"; }
run_julia scripts/coupled_emissions_experiments.jl --tail-stratified --temperature-only --pilot
python3 - <<'PY'
import csv
with open('results/coupled_emissions_stratified_temperature_only_pilot_refinement.csv') as f:r=list(csv.DictReader(f))
assert len(r)==16
assert max(float(x['max_co2_substep_difference_ppm']) for x in r)<.001
assert max(float(x['max_temperature_substep_difference_K']) for x in r)<.0001
assert max(float(x['max_mass_error_GtC']) for x in r)<1e-8
print('Temperature-only coupled pilot passes.')
PY
run_julia scripts/coupled_emissions_experiments.jl --tail-stratified --temperature-only
run_julia scripts/sea_level_ensemble.jl --tail-stratified --temperature-only --pilot
python3 - <<'PY'
import csv
with open('results/sea_level_stratified_temperature_only_pilot_refinement.csv') as f:r=list(csv.DictReader(f))
assert len(r)==80 and max(float(x['max_antarctic_step_difference_m']) for x in r)<1e-5
print('Temperature-only sea-level pilot passes.')
PY
run_julia scripts/sea_level_ensemble.jl --tail-stratified --temperature-only

run_julia scripts/sea_level_reference.jl --hadcrut5
nice -n19 python3 scripts/plot_sea_level_reference.py --hadcrut5
run_julia scripts/sea_level_reference.jl --temperature-only
nice -n19 python3 scripts/plot_sea_level_reference.py --temperature-only
