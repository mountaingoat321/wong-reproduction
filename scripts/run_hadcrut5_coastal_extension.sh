#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
[[ "$ROOT" == /data/data2/ludtke/wong-reproduction ]] || exit 1
cd "$ROOT"
export TMPDIR="$ROOT/.local/tmp" PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR="$ROOT/.local/matplotlib"
export JULIA_DEPOT_PATH="$ROOT/.local/julia" JULIA_LOAD_PATH=@stdlib
export JULIA_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
[[ -f results/sea_level_stratified_hadcrut5_run.toml ]]
nice -n19 julia --startup-file=no --history-file=no scripts/coastal_coupled_experiments.jl --hadcrut5 --pilot
nice -n19 python3 scripts/aggregate_coupled_coasts.py --hadcrut5 --pilot
python3 - <<'PY'
import csv
with open('results/coastal_coupled_hadcrut5_pilot_refinement.csv') as f:r=list(csv.DictReader(f))
assert len(r)>=8 and all(v['same_policy']=='true' and float(v['relative_quadrature_difference'])<1e-6 for v in r)
print('HadCRUT5 coastal pilot passes before full250paths.')
PY
nice -n19 julia --startup-file=no --history-file=no scripts/coastal_coupled_experiments.jl --hadcrut5
nice -n19 python3 scripts/aggregate_coupled_coasts.py --hadcrut5
nice -n19 python3 scripts/plot_coastal_coupled.py --hadcrut5
nice -n19 python3 scripts/compare_coastal_climate_constraints.py
