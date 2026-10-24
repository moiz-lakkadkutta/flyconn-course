# Progress log

Running log so a later session can resume. Newest entry first.

## 2026-10-24: M0 plus notebooks 1–2 (branch m0-basic, local only)

Asked for by the google-fly session on the owner's behalf: a basic working implementation to
build on. Audience defaulted to **intro college** (PLAN.md open question, not yet answered by
the owner).

- **Built:**
  - repo scaffold: uv project pinned to `flyconn==0.4.0`; MkDocs Material + mkdocs-jupyter
    site (`scripts/build_site.sh`); CC BY 4.0 (content) and Apache-2.0 (code) licences;
  - CI workflow `.github/workflows/ci.yml` (ruff, jupytext pair check, pytest, nbmake, site
    build); written but not pushed;
  - teaching subset (`data/teaching/`, 5.4 MB) built by `scripts/build_teaching_subset.py`
    from the cached `malecns@1.0` store in `~/google-fly/.cache/flyconn/store/malecns/1.0`,
    with provenance; helper `notebooks/course_utils.py` (local data in a checkout, otherwise
    download plus SHA-256 check; `FLYLAB_DATA` and `FLYLAB_RAW` overrides);
  - notebooks `01_meet_the_connectome` and `02_who_talks_to_whom`, each with learning goals,
    exercises with Colab-collapsed solutions, honesty labels and `assert`s guarding numbers
    quoted in the prose; Colab badges at the placeholder `moiz-lakkadkutta/flyconn-course`;
  - `tests/test_teaching_data.py` (8 tests: checksums, size, citation, focus completeness,
    LB3* -> MN9 paths inside focus, census, local and download paths of the helper);
  - `docs/upstream-notes.md` (flyconn friction) and `docs/flyconn-adr-draft.md`.
- **Measured** (README table): fresh-venv pip install 95 s wall / 8 s CPU, 497 MB; notebook
  peak RSS 309–326 MB; nbmake 2 passed in about 4 s; notebooks also run on pandas 2.2.2 /
  duckdb 1.1.3.
- **Findings worth carrying forward:**
  - MaleCNS `nt_pred` is a consensus label (measured > type > body); `nt_known` covers 51 % of
    neurons. Per-neuron classifier votes (`nt_p_*`) call 1,022 of 1,023 Kenyon cells
    dopaminergic. Notebook 1 now teaches this.
  - No direct LB3* -> MN9 edge at any threshold, which sets up notebook 3.
  - The two MN9s differ tenfold in input (6,358 vs 633 synapses); threshold 20 keeps 88 % vs
    34 % of their input.
  - MN9's own `nt_p_*` are spread out (ACh 0.30, GABA 0.20); material for notebook 4.
- **Not done / open:**
  - nothing pushed and no GitHub repo created (needs the owner's yes); the badges and data
    URLs 404 until then;
  - not run on real Colab; the venv measurement is a stand-in;
  - `uv.lock` resolves on macOS; CI on ubuntu not yet run;
  - the site renders solution outputs (fine for instructors; consider hiding them for students);
  - owner questions in PLAN.md (first audience, partnering, translations) still open.
- **Next:** M1 notebooks 3–4 (pathways LB3 -> MN9 with `find_paths` / `path_stability`; signs
  as guesses with `SignPolicy.SAMPLED`). Use the Shiu sugar IDs or MaleCNS `LB3c+LB3d` where
  sugar specificity matters (see flyconn caveats); the subset already contains every
  LB3* -> MN9 path up to 3 hops.
