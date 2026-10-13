#!/usr/bin/env bash
# Serial research extensions. Run only after the base coastal run finishes.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
[[ "$ROOT" == /data/data2/ludtke/wong-reproduction ]] || exit 1
cd "$ROOT"
[[ -f results/coastal_coupled_run.toml ]] || { echo 'Complete the base coastal run first'; exit 1; }
export TMPDIR="$ROOT/.local/tmp" PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR="$ROOT/.local/matplotlib"
export JULIA_DEPOT_PATH="$ROOT/.local/julia" JULIA_LOAD_PATH=@stdlib
export JULIA_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
run_julia() { nice -n19 julia --startup-file=no --history-file=no "$@"; }
for choice in --ssp2 --horizon-freeze --horizon-growth --geometric-economy --accounting; do
    run_julia scripts/coastal_coupled_experiments.jl --pilot "$choice"
    nice -n19 python3 scripts/aggregate_coupled_coasts.py --pilot "$choice"
done
python3 - <<'PY'
import csv
from pathlib import Path
for name in ('ssp2','2150_freeze','2150_growth','geometric','accounting'):
    with Path('results/coastal_coupled_'+name+'_pilot_refinement.csv').open() as f:r=list(csv.DictReader(f))
    assert len(r)==12 and all(x['same_policy']=='true' and float(x['relative_quadrature_difference'])<1e-6 for x in r)
print('All five new coastal pilots pass refinement before scaling.')
PY
run_julia scripts/coastal_coupled_experiments.jl --ssp2
nice -n19 python3 scripts/aggregate_coupled_coasts.py --ssp2
nice -n19 python3 scripts/aggregate_coupled_coasts.py --draws 4
nice -n19 python3 scripts/aggregate_coupled_coasts.py --draws 8
nice -n19 python3 scripts/coastal_sampling_sensitivity.py
nice -n19 python3 scripts/compare_coastal_assumptions.py
run_julia tests/scipy_least_squares.jl
run_julia tests/carbon_equilibrium.jl
run_julia scripts/benchmark_carbon_equilibrium.jl
run_julia scripts/carbon_vintage_fit.jl --free-physics --pilot --fast-chemistry --scipy
run_julia scripts/carbon_vintage_fit.jl --free-physics --fast-chemistry --scipy
run_julia scripts/coupled_emissions_experiments.jl --tail-stratified --hadcrut5 --pilot
python3 - <<'PY'
import csv
with open('results/coupled_emissions_stratified_hadcrut5_pilot_refinement.csv') as f:r=list(csv.DictReader(f))
assert len(r)==16
assert max(float(x['max_co2_substep_difference_ppm']) for x in r)<.001
assert max(float(x['max_temperature_substep_difference_K']) for x in r)<.0001
assert max(float(x['max_mass_error_GtC']) for x in r)<1e-8
print('HadCRUT5 coupled pilot passes; proceeding to250members.')
PY
run_julia scripts/coupled_emissions_experiments.jl --tail-stratified --hadcrut5
run_julia scripts/sea_level_ensemble.jl --tail-stratified --hadcrut5 --pilot
python3 - <<'PY'
import csv
with open('results/sea_level_stratified_hadcrut5_pilot_refinement.csv') as f:r=list(csv.DictReader(f))
assert len(r)==80 and max(float(x['max_antarctic_step_difference_m']) for x in r)<1e-5
print('HadCRUT5 sea-level pilot passes; proceeding to250members.')
PY
run_julia scripts/sea_level_ensemble.jl --tail-stratified --hadcrut5
echo 'Serial coupled extensions finished; inspect diagnostics and update the report.'
