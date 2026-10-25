# Fly Lab (flyconn-course)

A short course of Colab notebooks: from "what is a connectome?" to running, and critically
judging, an in-silico experiment on a real fruit-fly brain. No install, no tokens, no 10 GB
downloads. Built on [flyconn](https://github.com/moiz-lakkadkutta/flyconn) (pinned:
`flyconn==0.4.0`).

Status: **M0 plus notebooks 1–2** (data and graphs; no simulation yet). Level: intro college /
advanced high school, with "go further" boxes for grad students. See `PLAN.md` for the full
course and `PROGRESS.md` for where work stands.

| # | Notebook | Colab |
|---|---|---|
| 1 | Meet the connectome | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/moiz-lakkadkutta/flyconn-course/blob/main/notebooks/01_meet_the_connectome.ipynb) |
| 2 | Who talks to whom (thresholds change answers) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/moiz-lakkadkutta/flyconn-course/blob/main/notebooks/02_who_talks_to_whom.ipynb) |

The badges and the notebooks' data downloads point at
[`github.com/moiz-lakkadkutta/flyconn-course`](https://github.com/moiz-lakkadkutta/flyconn-course)
(`main`). A course release will pin them to a tag.

## Data

The notebooks use a 5 MB teaching subset of MaleCNS v1.0 (Berg et al. 2026, Cell,
doi:10.1016/j.cell.2026.08.015, CC BY 4.0), committed in `data/teaching/` and rebuilt from a
flyconn store by `scripts/build_teaching_subset.py`. See [`docs/data.md`](docs/data.md). It
stands in until the `flyconn-bench` Hugging Face snapshots exist.

## Measured cost (2026-10-24)

Colab stand-in: a fresh Python 3.12 venv on macOS arm64 (M4 Pro), notebooks run from a
directory outside the repo with the data downloaded over HTTP (`FLYLAB_RAW` pointed at a local
server) and checked against the SHA-256 sums in `provenance.json`.

| Step | Measured |
|---|---|
| `pip install --no-cache-dir flyconn==0.4.0 matplotlib` into an empty venv | 95 s wall (8 s CPU; the rest is download), 497 MB installed, mostly pyarrow, scipy, pandas, duckdb |
| Notebook 1, first run (data download plus matplotlib font-cache build) | 28 s, peak RSS 309 MB |
| Notebook 2 | 2 s, peak RSS 320 MB |
| Both notebooks through `jupyter nbconvert --execute` | 5 s, peak RSS 326 MB |
| `pytest --nbmake notebooks/` in the dev env | 2 passed, about 4 s |

Not yet measured on real Colab. Colab preinstalls numpy, scipy, pandas, pyarrow and
matplotlib at versions that satisfy flyconn's lower bounds, so there `pip` should only fetch
flyconn (and duckdb if missing). The notebooks also ran on an older, Colab-like stack (pandas
2.2.2, numpy 2.0.2, duckdb 1.1.3, matplotlib 3.10.0). Free Colab gives about 12 GB RAM, so
notebooks 1–2 use under 3 % of it.

## Develop

```bash
uv sync                                    # Python >= 3.11; installs flyconn==0.4.0 + dev tools
uv run pytest                              # data-subset and helper tests (offline)
uv run pytest --nbmake notebooks/          # execute every notebook
uv run ruff check . && uv run ruff format --check .
scripts/build_site.sh                      # MkDocs site into site/
```

Notebooks are paired with percent-format `.py` files (jupytext). Edit either side, then
`uv run jupytext --sync notebooks/*.py`; CI fails if the pair is out of sync. Commit notebooks
with outputs from a fresh run (`uv run jupyter nbconvert --to notebook --execute --inplace
notebooks/0*.ipynb`), so numbers on the site and in Colab previews come from execution. Claims
in the prose that depend on a number are guarded by `assert`s in the cell that computes it.

Exercises have the solution in the next cell, titled `# @title Solution` with
`display-mode: "form"`, which Colab shows collapsed. CI executes the solutions too.

The website uses **MkDocs Material + mkdocs-jupyter**, to match flyconn's MkDocs docs (one
toolchain to learn, the same look, and flyconn's docs can link straight in). Jupyter Book
would add executable-book features (cross-references, a glossary, a PDF build) that a course
of 8 notebooks does not need yet.

## Licence

Course text and notebooks' prose: CC BY 4.0 (`LICENSE-CONTENT`). Code (`notebooks/*.py` code
cells, `scripts/`, `tests/`): Apache-2.0 (`LICENSE`). Data: CC BY 4.0, Berg et al. 2026; cite
it when you use the course data.
