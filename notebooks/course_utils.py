"""Helpers shared by the Fly Lab notebooks: find (or download) the teaching data and open it.

In a checkout of the course repo the data comes from ``data/teaching/``. Anywhere else (Colab),
it is downloaded once from the course's GitHub repo into ``~/.cache/flylab/`` and checked
against the SHA-256 sums in ``provenance.json``. Set ``FLYLAB_DATA`` to use another directory.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from pathlib import Path

import pandas as pd
from flyconn.data.store import Store

# Pin COURSE_REF (here and in each notebook's setup cell) to a release tag for each course release.
COURSE_REPO = "moiz-lakkadkutta/flyconn-course"
COURSE_REF = "main"
# FLYLAB_RAW points the download at a mirror (or a local server, for testing).
RAW = os.environ.get(
    "FLYLAB_RAW", f"https://raw.githubusercontent.com/{COURSE_REPO}/{COURSE_REF}/data/teaching"
)

SUBSET = "malecns-1.0-gustatory"
CENSUS = "malecns-1.0-census.parquet"

PREDICTED_NT = "NT = predicted by a classifier from EM images, not measured."
MODEL_PREDICTION = "Model prediction from wiring, not a measurement."


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    urllib.request.urlretrieve(url, tmp)
    tmp.replace(dest)


def data_dir() -> Path:
    """Directory holding the teaching data, downloading it first if needed."""
    if env := os.environ.get("FLYLAB_DATA"):
        return Path(env)
    local = Path(__file__).resolve().parents[1] / "data" / "teaching"
    if (local / SUBSET / "provenance.json").exists():
        return local
    cache = Path.home() / ".cache" / "flylab" / COURSE_REF
    prov_path = cache / SUBSET / "provenance.json"
    if not prov_path.exists():
        _download(f"{RAW}/{SUBSET}/provenance.json", prov_path)
    files = json.loads(prov_path.read_text())["files"]
    for name, info in files.items():
        rel = name if name == CENSUS else f"{SUBSET}/{name}"
        dest = cache / rel
        if not dest.exists() or _sha256(dest) != info["sha256"]:
            _download(f"{RAW}/{rel}", dest)
            if _sha256(dest) != info["sha256"]:
                msg = f"checksum mismatch for {rel}; delete {cache} and retry"
                raise RuntimeError(msg)
    return cache


def open_store() -> Store:
    """The teaching subset as a flyconn ``Store`` (neurons and edges around LB3 -> MN9)."""
    return Store(data_dir() / SUBSET)


def load_census() -> pd.DataFrame:
    """One row per neuron of the whole MaleCNS v1.0 connectome (annotations only, no edges)."""
    return pd.read_parquet(data_dir() / CENSUS)


def about(store: Store) -> None:
    """Print what the teaching subset is, where it came from, and how to cite it."""
    prov = store.provenance
    sub = prov["subset"]
    print(f"Dataset: {store.ref} ({prov['license']}), teaching subset '{sub['name']}'")
    print(f"  {sub['description']}")
    print("  " + ", ".join(f"{k}: {v:,}" for k, v in sub["counts"].items()))
    print(f"  Edge threshold in the source: {prov['edge_threshold']}")
    print(f"  Built with flyconn {prov['flyconn_version']} on {prov['created_utc'][:10]}")
    print("Cite:")
    print(store.citation_text())
    print(PREDICTED_NT)
