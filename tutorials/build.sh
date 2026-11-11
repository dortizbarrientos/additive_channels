#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "$0")/.." && pwd)"
cd "$repo_dir"
python_bin="${PYTHON_BIN:-python3}"
for exe in latexmk pdflatex bibtex node npm soffice; do command -v "$exe" >/dev/null || { echo "Missing tutorial-build dependency: $exe" >&2; exit 1; }; done
"$python_bin" code/guide_figures.py
"$python_bin" tutorials/introduction/make_figures.py
for src in tutorials/introduction/{notes,worksheet}.tex tutorials/mathematics/guide.tex examples/estimating_variance_share/worked_example.tex; do
  (cd "$(dirname "$src")"; base="$(basename "$src")"; latexmk -pdf -halt-on-error -interaction=nonstopmode "$base"; latexmk -c "$base")
done
(cd tutorials/introduction; if ! node -e "require('pptxgenjs')" >/dev/null 2>&1; then npm install --no-audit --no-fund; fi; node build_slides.js; soffice --headless --convert-to pdf --outdir . slides.pptx)
