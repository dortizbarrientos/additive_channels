#!/usr/bin/env bash
# Build the short companion from its single maintained text source.
# This command builds a PDF only; it does not commit or publish files.
set -euo pipefail
companion_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$companion_dir"
for executable in latexmk pdflatex bibtex; do
  command -v "$executable" >/dev/null || {
    echo "Missing PDF-build dependency: $executable" >&2
    exit 1
  }
done
mkdir -p build
latexmk -norc -pdf -halt-on-error -interaction=nonstopmode -outdir=build companion.tex
cp build/companion.pdf companion.pdf
