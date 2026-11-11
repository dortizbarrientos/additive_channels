# Common environment for the public launchers. Install into a local venv only if necessary.
setup_python() {
  local mode="$1" dep_file="$repo_dir/requirements.txt" selected="${PYTHON_BIN:-python3}"
  if [[ "$mode" == app ]]; then dep_file="$repo_dir/requirements-app.txt"; fi
  command -v "$selected" >/dev/null || { echo 'Install Python 3.11 or newer.' >&2; return 1; }
  if ! "$selected" -c 'import sys; sys.exit(sys.version_info < (3,11))'; then echo 'Python 3.11 or newer is required.' >&2; return 1; fi
  probe() {
    "$1" - "$mode" <<'PY'
import sys
from importlib.metadata import version
from packaging.specifiers import SpecifierSet
import numpy,scipy,pandas,matplotlib
targets={'numpy':'>=1.24,<3','scipy':'>=1.11,<2','pandas':'>=2.0,<3','matplotlib':'>=3.7,<4'}
if sys.argv[1]=='app':
    import shiny,jinja2
    targets.update(shiny='>=1.4,<2',jinja2='>=3.1,<4')
assert all(version(k) in SpecifierSet(spec) for k,spec in targets.items())
PY
  }
  if probe "$selected" >/dev/null 2>&1; then python_bin="$selected"
  else
    local vdir="$repo_dir/.venv"
    [[ -x "$vdir/bin/python" ]] || "$selected" -m venv "$vdir"
    python_bin="$vdir/bin/python"
    if ! probe "$python_bin" >/dev/null 2>&1; then "$python_bin" -m pip install -r "$dep_file"; fi
    probe "$python_bin" >/dev/null
  fi
  export PYTHON_BIN="$python_bin" PYTHONDONTWRITEBYTECODE=1 MPLBACKEND=Agg OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
}
