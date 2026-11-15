#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
py="${PYTHON_BIN:-python3}"
"$py" code/geometry.py
"$py" code/figure.py
"$py" code/explorer.py
