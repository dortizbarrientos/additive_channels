#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
py="${PYTHON_BIN:-python3}"
export OPENBLAS_NUM_THREADS=1
"$py" code/calculate.py
"$py" code/draw.py
"$py" code/export_interactive.py
