#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "$0")" && pwd)"
source "$repo_dir/code/environment.sh"
setup_python app
cd "$repo_dir/examples/estimating_variance_share"
exec "$python_bin" -m shiny run --host 127.0.0.1 --port "${SHINY_PORT:-8000}" --launch-browser "$@" app.py
