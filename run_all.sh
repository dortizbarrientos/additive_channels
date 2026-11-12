#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$repo_dir"
usage() {
  echo 'Usage: bash run_all.sh [--quick | --simulate | --visuals | --tutorials]'
  echo 'Default: figures, mathematics, archived population diagnostics and the 500-bootstrap estimation example.'
  echo '--quick: reproduce figures, algebra and diagnostics without the bootstrap.'
  echo '--simulate: run and compare all 20 SLiM 5.2 replicates.'
  echo '--visuals: rebuild the visual explanations and offline explorers.'
  echo '--tutorials: rebuild the teaching PDFs and slides (TeX, Node/npm and LibreOffice).'
}
[[ $# -le 1 ]] || { usage >&2; exit 2; }
mode="${1:-default}"
case "$mode" in -h|--help) usage; exit;; default|--quick|--simulate|--visuals|--tutorials) ;; *) usage >&2; exit 2;; esac
source code/environment.sh
setup_python numeric
if [[ "$mode" == --simulate ]]; then exec bash slim/run_simulations.sh; fi
if [[ "$mode" == --visuals ]]; then exec bash tutorials/build_visuals.sh; fi
if [[ "$mode" == --tutorials ]]; then exec bash tutorials/build.sh; fi
mkdir -p outputs
"$python_bin" code/figures.py
"$python_bin" code/verify_mathematics.py
"$python_bin" code/reproduce_result_checks.py
"$python_bin" code/summarize_simulation.py
"$python_bin" tutorials/introduction/check_examples.py
if [[ "$mode" == default ]]; then
  "$python_bin" examples/estimating_variance_share/run_case.py --output outputs/estimation
fi
"$python_bin" code/check_results.py "$mode"
