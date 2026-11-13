#!/usr/bin/env bash
# Build only the derivation companion; no numerical refits or apps.
set -euo pipefail
module_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$module_dir"
python_bin="${PYTHON_BIN:-python3}"
for executable in latexmk pdflatex bibtex; do
  command -v "$executable" >/dev/null || {
    echo "Missing derivation-build dependency: $executable" >&2
    exit 1
  }
done
"$python_bin" check_coverage.py --write
mkdir -p build
latexmk -pdf -halt-on-error -interaction=nonstopmode -outdir=build derivations.tex
cp build/derivations.pdf derivations.pdf
echo "Built tutorials/derivations/derivations.pdf"
