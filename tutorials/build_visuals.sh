#!/usr/bin/env bash
# Rebuild the matrix-free illustration and the two numerical visual modules.
# All outputs are local to the module directories. No network is required.
set -euo pipefail
repo_dir="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd -- "$repo_dir"
python_bin="${PYTHON_BIN:-python3}"
"$python_bin" tutorials/one_trait_visual/make_figure.py
bash tutorials/geometry/run.sh
bash tutorials/parental_weighting/run.sh
