#!/usr/bin/env bash
# Build the course website into site/. Notebooks and PROGRESS.md are copied into docs/ first
# because MkDocs only reads files under docs_dir. Extra arguments go to `mkdocs build`.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf docs/notebooks
mkdir -p docs/notebooks
cp notebooks/0*.ipynb docs/notebooks/
cp PROGRESS.md docs/PROGRESS.md
uv run mkdocs build "$@"
