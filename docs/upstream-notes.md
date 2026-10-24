# Upstream notes for flyconn

Friction and findings from building the course on `flyconn==0.4.0`. Not filed upstream; the
flyconn repo was not edited. Each item says where it showed up.

## Science and documentation

1. **MaleCNS `nt_pred` is a consensus, not a prediction.** The converter
   (`flyconn/data/convert/malecns.py`) fills `nt_pred` from `consensus_nt` (ground truth >
   type-level > body-level) and `nt_known` from `ground_truth`. 85,484 of 166,700 neurons
   (51 %) have `nt_known`, and for them `nt_pred` equals it exactly (16,451 of 16,451 in the
   teaching subset). `docs/caveats.md` says "MaleCNS body-level file gives argmax + confidence
   only", and the column name suggests a classifier output. Suggest: say in the caveats that
   `nt_pred` is a consensus label for MaleCNS, and consider a per-neuron `nt_label_source`
   (`measured` / `type` / `body`). Found writing notebook 1, whose first draft compared
   `nt_pred` with `nt_known` and got a meaningless 100 %.
2. **Kenyon cells are mispredicted in MaleCNS too, at body level.** The argmax of the
   per-neuron `nt_p_*` (mean of per-presynapse probabilities) is dopamine for 1,022 of the 1,023
   `KC*` neurons in the teaching subset; the consensus `nt_pred` is acetylcholine for all 4,064
   KCs. `docs/caveats.md` mentions this misprediction only for hemibrain. It matters for
   `SignPolicy.PROBABILISTIC` and `SAMPLED`, which use `nt_p_*` and so ignore the type-level
   consensus. (Dopamine and acetylcholine are both +1 under the default sign table, so the KC
   case does not flip a sign, but the same mechanism can elsewhere.)
3. **Sampled signs can be near coin flips for key neurons.** MN9 (the W1/W2 readout) has
   consensus acetylcholine with `nt_conf` 0.54 / 0.57, but its `nt_p_*` are
   ACh 0.30 / GABA 0.20 / serotonin 0.15 (left MN9). MN9's own sign does not enter an MN9
   readout, but its inputs' signs do; worth a line in the robustness tutorial on how `nt_p_*`
   differ from the consensus labels. Material for course notebook 4.
4. **The two MN9 neurons differ tenfold in input** (`input_synapses_total` 6,358 vs 633;
   bodies 10331 and 16949). A synapse threshold of 20 keeps 88 % of the left MN9's input
   synapses but 34 % of the right one's. Any per-neuron threshold result on MN9 depends on
   which MN9; a readout selected by cell type pools both. Worth a caveat if not already known.
5. `flow` is null for every MaleCNS neuron in the store (166,700 of 166,700). Either fill it or
   drop it from the schema docs for MaleCNS.

## API

6. **No first-class derived or subset store.** The teaching subset is a directory with
   `neurons.parquet`, `edges.parquet` and `provenance.json`; `Store` opens it fine. But
   `Store.ref`, `Store.spec` and `Store.citations()` resolve through the registry by
   `dataset@version`, so the subset has to claim to be `malecns@1.0` and records the
   restriction in a `subset` block that flyconn does not read. A `flyconn data slice` command
   (or `Store.write_subset(neuron_ids, ...)`) that writes provenance with the parent's checksums
   would serve this course and flyconn-bench's HF snapshots.
7. `Store.edges()` has no way to request edges where `pre` **or** `post` is in a set (it ANDs
   `pre=` and `post=`). The build script uses raw SQL via `Store.query`, which works but couples
   it to the view names.
8. `ConnectivityMatrix.from_store(neuron_ids=...)` loads every edge above `min_weight` before
   filtering in pandas. Fine at the subset's size; on the full store it reads 25.6 M edges to
   keep a few.
9. Base `pip install flyconn` is 497 MB in a fresh venv (pyarrow 127 MB, scipy 99 MB, pandas
   80 MB, duckdb 49 MB). Fine on Colab, where most of it is preinstalled; not a problem today.
