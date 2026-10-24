# ADR draft: flyconn-course as a downstream consumer of flyconn

Draft text for an ADR in the flyconn repo (`docs/adr/`), to be added by the flyconn session or
the owner. Not committed to flyconn.

- **Status:** proposed (2026-10-24)
- **Context.** `flyconn-course` ("Fly Lab") is a set of Colab notebooks that teaches
  connectome analysis and in-silico experiments with flyconn. It installs `flyconn` from PyPI
  in Colab and runs its notebooks in CI. Students and instructors will copy its code, so
  breaking changes in flyconn's public API reach people who cannot debug them.
- **Decision.**
  1. The course pins an exact flyconn version per course release (`flyconn==0.4.0` today) in
     `pyproject.toml` and in every notebook's setup cell, and moves the pin deliberately, with
     the notebooks re-executed.
  2. The course uses only public API: `flyconn.data.store.Store` (`neurons`, `edges`, `query`,
     `provenance`, `citation_text`), `flyconn.graph.ConnectivityMatrix` (`from_store`,
     `input_normalized`, `index_of`, `provenance`), and later `find_paths`, `path_stability`,
     `sample_signs`, `flyconn.experiments.spec_from_dict`, `runner.run_experiment` and
     `flyconn.compare.compare_type`. Changes to these are noted in flyconn's CHANGELOG with a
     migration line.
  3. The course's teaching data is a flyconn store directory derived from `malecns@1.0` by
     `scripts/build_teaching_subset.py` in the course repo; it carries the parent store's
     provenance and checksums. When flyconn-bench publishes HF snapshots, the course switches
     to them.
  4. Course notebooks keep flyconn's honesty conventions: predicted transmitters labelled as
     such, simulation outputs labelled "model prediction", controls on by default.
- **Consequences.** flyconn gains a consumer whose CI exercises the public API against real
  data on every course change; flyconn releases should be checked against the course's
  notebooks before a course release moves its pin. Friction found so far is in the course's
  `docs/upstream-notes.md` (notably: MaleCNS `nt_pred` is a consensus label; no first-class
  subset store).
- **Alternatives considered.** Vendoring the needed flyconn code into the course (rejected:
  forks the science and its caveats); depending on flyconn `main` (rejected: notebooks would
  rot between course releases).
