# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/moiz-lakkadkutta/flyconn-course/blob/main/notebooks/01_meet_the_connectome.ipynb)
#
# # 1. Meet the connectome
#
# A **connectome** is a wiring diagram: every neuron in a nervous system, and how many synapses
# each neuron makes onto every other. This one is the **male central nervous system of the fruit
# fly *Drosophila melanogaster*** (MaleCNS v1.0, Berg et al. 2026): brain plus ventral nerve
# cord, reconstructed from electron-microscope (EM) images.
#
# **Learning goals.** By the end of this notebook you can
#
# 1. load a connectome's neuron table with pandas and say what one row means;
# 2. count neurons by class, side and cell type, and explain why "cell type" matters;
# 3. explain why every neurotransmitter label here is a **prediction**, and read its confidence;
# 4. find the neurons this course follows: taste neurons (`LB3*`) and a proboscis motor neuron
#    (`MN9`).
#
# **Time:** about 40 minutes. **You need:** basic Python (lists, functions). No install: in
# Colab, run the setup cell and everything else downloads in seconds.

# %%
# @title Setup: run this cell first { display-mode: "form" }
import sys
import urllib.request
from pathlib import Path

if "google.colab" in sys.modules:
    # %pip install -q flyconn==0.4.0 matplotlib
    pass
if not Path("course_utils.py").exists():
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/moiz-lakkadkutta/flyconn-course/main/notebooks/course_utils.py",
        "course_utils.py",
    )

import matplotlib.pyplot as plt
import pandas as pd

import course_utils as cu

pd.set_option("display.max_rows", 20)

# %% [markdown]
# ## 1. One row per neuron
#
# Start with the **census**: one row for each of the neurons in the whole MaleCNS, with the
# annotations the reconstruction team assigned. It has no connections yet; those come in
# notebook 2.

# %%
census = cu.load_census()
print(f"{len(census):,} neurons, {census.shape[1]} columns")
census.head()

# %% [markdown]
# The columns you will use most:
#
# | column | meaning |
# |---|---|
# | `neuron_id` | the neuron's body ID in this dataset (unique within MaleCNS v1.0 only) |
# | `super_class` | broad category: sensory, motor, intrinsic to a region, descending (brain to nerve cord), ascending (nerve cord to brain), ... |
# | `cell_class`, `cell_type` | finer groupings; a cell type is a set of neurons that look alike and connect alike |
# | `side` | left or right side of the body |
# | `nt_pred`, `nt_conf` | **predicted** neurotransmitter and the classifier's confidence |
# | `input_synapses_total`, `output_synapses_total` | how many synapses the neuron receives and makes |

# %% [markdown]
# ## 2. What kinds of neurons are there?

# %%
by_class = census["super_class"].value_counts()
assert by_class["optic_lobe_intrinsic"] > len(census) / 2  # claim in the text below
by_class

# %%
ax = by_class.head(10).iloc[::-1].plot.barh(figsize=(7, 4))
ax.set_xlabel("number of neurons")
ax.set_title("MaleCNS v1.0: the ten largest super classes")
plt.tight_layout()

# %% [markdown]
# More than half of all neurons sit in the optic lobes, the visual system. A fly's brain is, by
# head count, mostly eyes.
#
# Most neurons come in **left/right pairs**. Check:

# %%
census["side"].value_counts(dropna=False)

# %% [markdown]
# ## 3. Cell types
#
# Studying 166,700 individual neurons is hopeless. Neuroscientists group them into **cell
# types**: neurons with the same shape, position and connections. Many types are a single
# left/right pair; some have thousands of members.

# %%
type_sizes = census["cell_type"].value_counts()
print(f"{type_sizes.size:,} cell types; {census['cell_type'].isna().sum():,} neurons have no type")
print(f"types with exactly 2 neurons: {(type_sizes == 2).sum():,}")
type_sizes.head(5)

# %%
ax = type_sizes.plot.hist(
    bins=[1, 2, 3, 5, 9, 17, 33, 65, 129, 257, 513, 4096], log=True, figsize=(7, 3.5)
)
ax.set_xscale("log")
ax.set_xlabel("neurons per cell type (log scale)")
ax.set_ylabel("number of types")
plt.tight_layout()

# %% [markdown]
# The biggest types (`R1-R6`, `Tm3`, `T3`) are repeated once per facet of the compound eye.

# %% [markdown]
# ## 4. Transmitters: measured, predicted, or combined?
#
# A synapse excites or inhibits its target depending on the **neurotransmitter** it releases.
# EM images show synapses but not which chemical they release. A machine-learning classifier
# looks at each synapse in the images and votes for one of eight transmitters (Eckstein et al.
# 2024).
#
# In this dataset, `nt_pred` is a **consensus label** built in three steps:
#
# 1. if experiments have measured the type's transmitter, use that (`nt_known` is then filled);
# 2. otherwise, use the classifier's vote pooled over all neurons of the cell type;
# 3. otherwise, use the neuron's own vote.
#
# `nt_conf` is the classifier's confidence in the winning label.
#
# > **Honesty label.** Unless `nt_known` is filled, a transmitter in this course is a
# > **prediction**, not a measurement.

# %%
print(f"measured (nt_known filled): {census['nt_known'].notna().mean():.0%} of neurons")
census["nt_pred"].value_counts(dropna=False)

# %%
ax = census["nt_conf"].plot.hist(bins=50, figsize=(7, 3))
ax.set_xlabel("classifier confidence (nt_conf)")
ax.set_title("Confidence of the consensus transmitter label, per neuron")
plt.tight_layout()
print(f"median confidence: {census['nt_conf'].median():.2f}")

# %% [markdown]
# Most labels are confident. But a confident classifier can still be wrong, so test it on a
# case where you know the answer. **Kenyon cells** (`KC*`, in the mushroom body, a learning
# centre) release acetylcholine. Their transmitter is not in `nt_known` here, so their label
# comes from step 2.
#
# The teaching subset also stores the classifier's raw output for each neuron: `nt_p_*`, the
# probability of each transmitter averaged over the neuron's synapses. Compare the consensus
# label with each neuron's own top vote.

# %%
store = cu.open_store()
neurons = store.neurons()
nt_cols = [c for c in neurons.columns if c.startswith("nt_p_")]
neurons["nt_own_vote"] = (
    neurons[nt_cols]
    .fillna(0)
    .idxmax(axis=1)
    .str.removeprefix("nt_p_")
    .where(neurons[nt_cols].notna().any(axis=1))
)
kc = neurons[neurons["cell_type"].fillna("").str.startswith("KC")]
print(f"{len(kc)} Kenyon cells in the teaching subset")
print("consensus label (nt_pred):", kc["nt_pred"].value_counts().to_dict())
print("each neuron's own vote:   ", kc["nt_own_vote"].value_counts().to_dict())
assert (kc["nt_own_vote"] == "dopamine").mean() > 0.9  # claim in the text below

# %% [markdown]
# Neuron by neuron, the classifier calls nearly every Kenyon cell dopaminergic, which is
# wrong. The consensus label is right only because step 2 pooled the votes per cell type.
# (Eckstein et al. report the same misprediction for Kenyon cells.) Lesson: the label you see
# depends on *how* predictions were combined, and a high confidence is not a guarantee.

# %% [markdown]
# ## 5. The cast of this course
#
# The course follows one circuit: from **taste neurons on the fly's mouthparts** to the **motor
# neuron that extends the proboscis** (the fly's tongue) so it can feed.
#
# - `LB3a`–`LB3d`: gustatory receptor neurons (GRNs) of the labellum. In MaleCNS some respond to
#   sugar and some to water; the dataset does not say which is which.
# - `MN9`: a motor neuron for proboscis extension.
#
# The teaching subset holds these neurons, every neuron they connect to directly, and their
# connections. `cu.about` says exactly what it contains and how to cite it.

# %%
cu.about(store)

# %%
cast = neurons[neurons["cell_type"].fillna("").str.match(r"^(LB3|MN9$)")]
cast.groupby("cell_type").agg(
    neurons=("neuron_id", "size"),
    predicted_nt=("nt_pred", lambda s: ", ".join(sorted(s.dropna().unique())) or "none"),
    median_inputs=("input_synapses_total", "median"),
)

# %% [markdown]
# Notice the two `MN9` neurons. Same cell type, but one receives about ten times more synapses
# than the other:

# %%
neurons.loc[
    neurons["cell_type"] == "MN9",
    ["neuron_id", "side", "nt_pred", "nt_conf", "input_synapses_total"],
]

# %% [markdown]
# Possible reasons include biology, a part of one neuron that was harder to reconstruct, or
# where the neuron's branches lie relative to the imaged volume. The connectome alone does not
# tell you which. Keep this in mind in notebook 2: a number from a single neuron can mislead.

# %% [markdown]
# ## Exercises
#
# Try each one before opening the solution. In Colab, the solution cell's code is hidden;
# double-click it to show the code.
#
# **Exercise 1.** How many neurons are `motor` neurons, and what fraction of all neurons is that?

# %%
# your code here

# %%
# @title Solution 1 { display-mode: "form" }
n_motor = (census["super_class"] == "motor").sum()
print(f"{n_motor} motor neurons, {n_motor / len(census):.2%} of all neurons")

# %% [markdown]
# **Exercise 2.** Which super class has the most *different* cell types (not the most neurons)?
# Hint: `groupby(...)["cell_type"].nunique()`.

# %%
# your code here

# %%
# @title Solution 2 { display-mode: "form" }
census.groupby("super_class")["cell_type"].nunique().sort_values(ascending=False).head(5)

# %% [markdown]
# **Exercise 3.** For neurons in the teaching subset with a measured transmitter (`nt_known`),
# how often does the neuron's own classifier vote (`nt_own_vote`) agree with it? Which
# transmitter does worst? Then think: why might this agreement *overestimate* how well the
# classifier does on neurons whose transmitter nobody has measured?

# %%
# your code here

# %%
# @title Solution 3 { display-mode: "form" }
both = neurons.dropna(subset=["nt_own_vote", "nt_known"])
both = both.assign(agree=both["nt_own_vote"] == both["nt_known"])
print(f"{len(both):,} neurons with both; agreement {both['agree'].mean():.1%}")
print(both.groupby("nt_known")["agree"].agg(["size", "mean"]).sort_values("mean"))
print(
    "Why it may overestimate: neurons of known transmitter are the ones classifiers are "
    "typically trained and tuned on, so they are not an independent test; and they are a "
    "biased sample (well-studied types). The Kenyon cells above had no measured label and "
    "were mispredicted."
)

# %% [markdown]
# ## Summary
#
# - The neuron table has one row per neuron; cell types group neurons that look and connect
#   alike.
# - Transmitters are classifier **predictions** unless `nt_known` says otherwise, and how the
#   predictions are combined changes the label (Kenyon cells).
# - The same cell type can show very different numbers in different neurons.
#
# **Next:** notebook 2, *Who talks to whom*, adds the connections and shows how the answer to
# "are these two neurons connected?" depends on a threshold you choose.
#
# *Data: MaleCNS v1.0, Berg et al. 2026, Cell, doi:10.1016/j.cell.2026.08.015 (CC BY 4.0), via
# [flyconn](https://github.com/moiz-lakkadkutta/flyconn). Course text CC BY 4.0, code
# Apache-2.0.*
