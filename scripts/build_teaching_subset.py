"""Build the Fly Lab teaching subset from a cached flyconn MaleCNS v1.0 store.

Writes two things under ``data/teaching/``:

- ``malecns-1.0-gustatory/``: a small flyconn store (``neurons.parquet``, ``edges.parquet``,
  ``provenance.json``) that ``flyconn.data.store.Store`` opens directly. The *focus* neurons are
  the labellar GRNs (``LB3*``), the proboscis motor neuron ``MN9``, every neuron that receives at
  least one synapse from an ``LB3*`` neuron and every neuron that sends at least one synapse to
  ``MN9``. Every LB3* -> MN9 path of at most 3 hops runs through focus neurons only. ``edges``
  holds every edge with a focus neuron at either end, so a focus neuron's partner list is
  complete; ``neurons`` holds the focus neurons and all their partners, with a ``focus`` column.
- ``malecns-1.0-census.parquet``: one row per MaleCNS neuron with a few annotation columns, for
  whole-CNS counts.

Run from the repo root (needs the full store, about 150 MB; see ``flyconn data pull``):

    uv run python scripts/build_teaching_subset.py \
        --source ~/google-fly/.cache/flyconn/store/malecns/1.0

Without ``--source`` it uses ``Store.open("malecns@1.0")`` (``$FLYCONN_CACHE``).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from flyconn.data.store import Store

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / "teaching"
SUBSET = "malecns-1.0-gustatory"

FOCUS_SQL = """
    SELECT neuron_id AS id FROM neurons WHERE cell_type LIKE 'LB3%' OR cell_type = 'MN9'
    UNION SELECT post FROM edges
          WHERE pre IN (SELECT neuron_id FROM neurons WHERE cell_type LIKE 'LB3%')
    UNION SELECT pre FROM edges
          WHERE post IN (SELECT neuron_id FROM neurons WHERE cell_type = 'MN9')
"""

NEURON_COLUMNS = [
    "neuron_id",
    "super_class",
    "cell_class",
    "cell_sub_class",
    "cell_type",
    "side",
    "hemilineage",
    "nt_pred",
    "nt_conf",
    "nt_p_acetylcholine",
    "nt_p_glutamate",
    "nt_p_gaba",
    "nt_p_dopamine",
    "nt_p_octopamine",
    "nt_p_serotonin",
    "nt_p_histamine",
    "nt_p_tyramine",
    "nt_known",
    "fafb_783_cell_type",
    "dimorphism",
    "input_synapses_total",
    "output_synapses_total",
]

CENSUS_COLUMNS = """
    neuron_id, super_class, cell_class, cell_type, side, nt_pred, nt_known,
    round(nt_conf, 3)::FLOAT AS nt_conf, dimorphism,
    input_synapses_total::INTEGER AS input_synapses_total,
    output_synapses_total::INTEGER AS output_synapses_total
"""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_sha() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip()


def copy(store: Store, sql: str, dest: Path) -> None:
    path = str(dest).replace("'", "''")
    store.query(f"COPY ({sql}) TO '{path}' (FORMAT parquet, COMPRESSION zstd)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", type=Path, help="full malecns@1.0 store directory")
    args = ap.parse_args()

    store = Store(args.source) if args.source else Store.open("malecns@1.0")
    if store.ref != "malecns@1.0":
        msg = f"expected a malecns@1.0 store, got {store.ref}"
        raise SystemExit(msg)

    sub = OUT / SUBSET
    sub.mkdir(parents=True, exist_ok=True)
    store.query(f"CREATE TEMP TABLE focus AS {FOCUS_SQL}")
    store.query(
        "CREATE TEMP TABLE sub_edges AS SELECT pre, post, weight FROM edges "
        "WHERE pre IN (SELECT id FROM focus) OR post IN (SELECT id FROM focus)"
    )
    cols = ", ".join(f'"{c}"' for c in NEURON_COLUMNS)
    copy(store, "SELECT * FROM sub_edges ORDER BY pre, post", sub / "edges.parquet")
    copy(
        store,
        f"SELECT {cols}, neuron_id IN (SELECT id FROM focus) AS focus FROM neurons "
        "WHERE neuron_id IN (SELECT pre FROM sub_edges UNION SELECT post FROM sub_edges) "
        "ORDER BY neuron_id",
        sub / "neurons.parquet",
    )
    census = OUT / "malecns-1.0-census.parquet"
    copy(store, f"SELECT {CENSUS_COLUMNS} FROM neurons ORDER BY neuron_id", census)

    counts = store.query(
        "SELECT (SELECT count(*) FROM focus) AS focus_neurons, "
        "(SELECT count(*) FROM (SELECT pre FROM sub_edges UNION SELECT post FROM sub_edges)) "
        "AS neurons, (SELECT count(*) FROM sub_edges) AS edges, "
        "(SELECT sum(weight) FROM sub_edges)::BIGINT AS synapses"
    ).iloc[0]
    src = store.provenance
    citation = store.citations()[0]
    prov = {
        # dataset/version stay "malecns"/"1.0" so Store.citations() resolves; `subset` says
        # this is not the full dataset.
        "dataset": src["dataset"],
        "version": src["version"],
        "registry_ref": src["registry_ref"],
        "subset": {
            "name": SUBSET,
            "description": (
                "LB3* labellar GRNs, MN9, every neuron receiving >= 1 synapse from LB3* and "
                "every neuron sending >= 1 synapse to MN9 (focus); all edges with a focus "
                "neuron at either end; neurons = focus plus all their partners."
            ),
            "focus_sql": " ".join(FOCUS_SQL.split()),
            "counts": {k: int(v) for k, v in counts.items()},
            "complete_partner_lists": "focus neurons only",
            "input_totals": (
                "input_synapses_total / output_synapses_total are whole-CNS totals from the "
                "full dataset (they include unannotated fragments), so input fractions match "
                "the full connectome"
            ),
        },
        "edge_threshold": src["edge_threshold"],
        "nt_source": src["nt_source"],
        "nt_probs": src.get("nt_probs"),
        "license": "CC-BY-4.0",
        "citation": {"text": citation.text, "doi": citation.doi},
        "attribution": (
            "Derived from the MaleCNS v1.0 connectome (Berg et al. 2026, CC BY 4.0) via flyconn; "
            "subset and column selection by flyconn-course."
        ),
        "source_store": {
            "provenance": src,
            "files": {
                f"{t}.parquet": sha256(store.root / f"{t}.parquet") for t in ("neurons", "edges")
            },
        },
        "files": {
            p.name: {"bytes": p.stat().st_size, "sha256": sha256(p)}
            for p in (sub / "neurons.parquet", sub / "edges.parquet", census)
        },
        "built_by": "scripts/build_teaching_subset.py",
        "course_git_sha": git_sha(),
        "flyconn_version": version("flyconn"),
        "duckdb_version": version("duckdb"),
        "created_utc": datetime.now(UTC).isoformat(timespec="seconds"),
    }
    (sub / "provenance.json").write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")
    print(json.dumps(prov["subset"]["counts"]), json.dumps(prov["files"], indent=1))


if __name__ == "__main__":
    main()
