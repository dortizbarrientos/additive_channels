#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "$0")" && pwd)"
source "$repo_dir/code/environment.sh"
setup_python numeric
exec "$python_bin" "$repo_dir/examples/estimating_variance_share/run_case.py" --output "$repo_dir/outputs/estimation" "$@"
