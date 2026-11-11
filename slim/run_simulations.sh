#!/usr/bin/env bash
set -euo pipefail
slim_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python_bin="${PYTHON_BIN:-python3}"
slim_bin="${SLIM_BIN:-slim}"
command -v "$slim_bin" >/dev/null || { echo "SLiM 5.2 is required for a fresh simulation run." >&2; exit 1; }
output_dir="${1:-$slim_dir/../outputs/simulation}"
mkdir -p "$output_dir"
output_dir="$(cd "$output_dir" && pwd)"
for rep in $(seq 1 20); do
  seed=$((41+rep))
  tag="$(printf 'rep_%02d_4trait_moving' "$rep")"
  echo "SLiM replicate $rep/20, seed $seed"
  "$slim_bin" -d "OUTPUT_PATH='${output_dir}/${tag}_bv.csv'" \
    -d "OPTIMUM_PATH='${output_dir}/${tag}_opt.csv'" -d "SEED=${seed}" \
    -d 'N_TRAITS=4' -d 'SIGMAS=c(0.346,0.283,0.200,0.141)' \
    -d 'GAMMAS=c(0.10,0.05,0.04,0.03)' -d 'Z_OPT_INITIAL=c(0.0,0.0,0.0,0.0)' \
    -d 'DRIFT_VELOCITY=c(0.3,0.0,0.0,0.0)' -d 'DRIFT_END_GEN=40' \
    "$slim_dir/slim_sim_n_traits.slim"
  "$python_bin" "$slim_dir/compute_diagnostics.py" \
    --bv-input "$output_dir/${tag}_bv.csv" --opt-input "$output_dir/${tag}_opt.csv" \
    --output "$output_dir/${tag}_diag.csv" --gammas 0.10 0.05 0.04 0.03
done
"$python_bin" "$slim_dir/../code/summarize_simulation.py" --input "$output_dir" --output "$output_dir/summary.json"
"$python_bin" "$slim_dir/../code/compare_simulations.py" --fresh "$output_dir" --check-raw
