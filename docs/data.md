# Teaching data

Until the `flyconn-bench` Hugging Face snapshots exist, every notebook loads a small subset of
the **MaleCNS v1.0** connectome (Berg et al. 2026, *Sexual dimorphism in the complete
Drosophila male central nervous system connectome*, Cell 189(18):5504–5526.e15,
doi:10.1016/j.cell.2026.08.015, CC BY 4.0), derived with flyconn 0.4.0.

| File | Contents | Size |
|---|---|---|
| `data/teaching/malecns-1.0-gustatory/` | a flyconn store: `neurons.parquet`, `edges.parquet`, `provenance.json` | 3.8 MB |
| `data/teaching/malecns-1.0-census.parquet` | one row per MaleCNS neuron (166,700), annotations only | 1.6 MB |

## What the subset holds

- **Focus neurons (953):** the labellar gustatory receptor neurons (`LB3`, `LB3a`–`LB3d`), the
  two `MN9` proboscis motor neurons, every neuron receiving at least one synapse from an
  `LB3*` neuron and every neuron sending at least one synapse to `MN9`. Every
  `LB3*` → `MN9` path of at most 3 hops runs through focus neurons only (tested).
- **Edges (502,095; 3,878,833 synapses):** every edge with a focus neuron at either end, at
  the source's synapse confidence threshold (0.5) and no pair threshold. A focus neuron's
  partner lists are complete; other neurons' are not (`focus` column).
- **Neurons (46,108):** focus neurons plus all their partners, with annotations, the consensus
  transmitter label (`nt_pred`, `nt_conf`, `nt_known`) and per-neuron classifier probabilities
  (`nt_p_*`, mean over the neuron's presynapses).
- `input_synapses_total` / `output_synapses_total` are whole-CNS totals from the full dataset,
  so input fractions equal those in the full connectome.

## Rebuilding

```bash
flyconn data pull malecns@1.0 --level nt-probs     # once, about 3.8 GB download
uv run python scripts/build_teaching_subset.py     # or --source <store dir>
```

`provenance.json` records the selection SQL, counts, the source store's provenance and the
SHA-256 of its Parquet files, the SHA-256 of every output file, flyconn and duckdb versions,
and the course git SHA. The helper `notebooks/course_utils.py` checks the files against these
sums when it downloads them.

## Using it

```python
import course_utils as cu

store = cu.open_store()  # flyconn Store: store.neurons(), store.edges(pre=..., post=...)
census = cu.load_census()  # pandas DataFrame
cu.about(store)  # what it is and how to cite it
```

The subset is the data `Store.open("malecns@1.0")` would give, restricted as above, so
flyconn functions (`ConnectivityMatrix.from_store`, `find_paths`, ...) work on it unchanged.
