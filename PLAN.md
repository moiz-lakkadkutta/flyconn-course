# flyconn-course — "Fly Lab", a zero-setup Colab course (plan and handoff)

Written 2026-10-24 at the end of a brainstorming session in the `flyconn` repo
(`/Users/moizp/google-fly`, github.com/moiz-lakkadkutta/flyconn, v0.4.0 on PyPI).
A new session starts here. Read this file, then flyconn's `CLAUDE.md`, `docs/caveats.md` and
`docs/tutorials/`.

## What and why

A short course of Colab notebooks where a student goes from "what is a connectome" to running
and **critically judging** an in-silico experiment on a real fly brain. It needs no install, no
tokens and no 10 GB downloads. Each notebook opens with one click and loads its data in under
about 30 s.

The angle no one else covers: **do an experiment, then check it with controls.** Activate or
silence neurons, predict behaviour, then ask "does a rewired brain do the same?". This is the
exciting thing in the press, done with the scepticism the field now asks for.

Owner goals: (1) learn and build skills (teaching, writing, notebooks, the neuroscience itself),
(2) lots of people using it. Courses reach students every year, and instructors reuse them.

Evidence from the 2026-10-24 research pass:
- FlyWire Academy (codex.flywire.ai/academy_home): HS (AP/IB) plus intro college, three
  dry-lab lessons each, with **"Programming exercises: coming soon"** and **"Group project
  prompts: coming soon"**. No simulation or perturbation lesson.
- SJCABS tutorial (`sjcabs/fly_connectome_data_tutorial`, 69★): needs `gsutil`, a ~9.6 GB BANC
  synapse file, and works around 403 errors. **No Colab.**
- CUNEL (QUBES) is browser/CATMAID based, piloted at 5 institutions, and seeking instructors.
- A "Colab sandbox for exploring the Drosophila connectome" (Google Drive link, TUM workshop)
  reached HN on 2026-09-21 with 4 pts. Demand exists, but there's no polished version.
- No Neuromatch fly-connectome module was found (UNVERIFIED absence).
- What educators lack (inferred): zero-setup notebooks, an "experiment" lesson, programming
  exercises, and honest framing of what simulations can and can't say.

## Decisions already made

- The owner picked this direction (a Colab course) as one of the projects to plan.

## Defaults (my calls; owner can override)

- **Standalone repo `flyconn-course`** (free on GitHub on 2026-10-24), rendered as a website
  (Jupyter Book or MkDocs, matching flyconn's MkDocs docs). Each notebook has an
  "Open in Colab" badge. Notebook content licensed CC-BY-4.0; code Apache-2.0.
- **Data:** load the small slices from the `flyconn-bench` HF snapshots (`flyconn/<dataset>`).
  This project depends on `flyconn-bench` M1. Until then, use `flyconn data pull` on a slice, or
  ship a tiny teaching subset.
- **Install in Colab:** `pip install "flyconn[sim]"`, pinned to an exact version per course
  release. Measure install time and RAM on free-tier Colab. Whole-MaleCNS simulation may be too
  heavy for the free tier (W2 with controls took 190 s on an M4 Pro CPU; the robustness screen
  peaked at 12.6 GB), so lessons use subnetworks or short runs and say so.
- **Audience tiers:** a core track for intro college / advanced HS, and "go further" boxes for
  grad students.
- **Every simulation output is labelled** "model prediction". NT signs are labelled
  "predicted". The controls lesson is not optional.
- **Draft notebooks** (6–8):
  1. Meet the connectome: neurons, types, classes. Explore MaleCNS in pandas.
  2. Who talks to whom: partners, weights and thresholds, and how the threshold changes the answer.
  3. Pathways: from taste neurons to the proboscis motor neuron (LB3 → MN9, flyconn's W1).
  4. Signs are guesses: predicted neurotransmitters and sampling signs (uncertainty).
  5. Your first experiment: drive sugar neurons and read out MN9 (the Shiu 2024 idea).
  6. Silence a neuron: the GNG232 experiment (W2). Write a prediction first, then run it.
  7. Is it real? Rewired and sign-shuffled controls; "the digital sphinx" discussion.
  8. Same neuron, different fly: male vs female, FlyWire vs MaleCNS (cross-dataset).
  Plus a capstone project prompt and instructor notes with answer keys.
- Numbers in the notebooks come from running them. Notebooks are executed in CI against the
  pinned flyconn (nbmake / papermill) so they don't rot.

## flyconn material to build on (verified 2026-10-24, flyconn 0.4.0)

- Tutorials already in `docs/tutorials/` (e.g. `robust-screens.md`) and examples in `examples/`:
  `w1_pathways.py`, `w3_male_vs_female.py`, `w4_version_drift.py`, `w5_driver_lines.py`, and
  `examples/specs/w2_*.yaml`.
- APIs: `Store.open`, `ConnectivityMatrix.from_store`, `find_paths`, `path_stability`,
  `sample_signs`, `flyconn.experiments.spec_from_dict` + `runner.run_experiment`,
  `flyconn.compare.compare_type`.

## Milestones (one branch each, tests green per commit)

1. **M0:** repo, site skeleton, CI that executes notebooks; measure Colab install time and RAM;
   ADR in flyconn noting the course as a consumer.
2. **M1 notebooks 1–4** (data and graphs, no simulation) on the HF slices or a teaching subset.
3. **M2 notebooks 5–7** (experiments and controls), sized for free Colab.
4. **M3 notebook 8, capstone and instructor notes;** a pilot with one instructor or student
   group, then fixes.
5. **M4 launch:** offer it to FlyWire Academy (their "programming exercises" slot), CUNEL,
   SJCABS organisers, VFB and Neuromatch. Post to awesome-fly. Link from flyconn's docs.

## Risks

- Colab free-tier RAM and time limits. Size every lesson for them and measure.
- Students over-reading simulations. The controls lesson and the labels are the guard.
- Rot as flyconn changes. Pin versions per course release and execute in CI.

## Open questions for the owner (ask early, one at a time)

- Who is the first real audience: a specific class, a workshop, or self-learners online?
- Do you want to partner with FlyWire Academy or CUNEL from the start, or build first and offer later?
- English only, or plan for translations?
