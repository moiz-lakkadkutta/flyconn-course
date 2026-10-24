"""The committed teaching subset is intact and means what its provenance says."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest
from flyconn.data.store import Store
from flyconn.graph import ConnectivityMatrix, find_paths

REPO = Path(__file__).resolve().parents[1]
TEACHING = REPO / "data" / "teaching"
SUBSET = TEACHING / "malecns-1.0-gustatory"
sys.path.insert(0, str(REPO / "notebooks"))

import course_utils as cu  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def store() -> Store:
    return Store(SUBSET)


@pytest.fixture(scope="module")
def prov() -> dict:
    return json.loads((SUBSET / "provenance.json").read_text())


def test_checksums_match_provenance(prov: dict) -> None:
    for name, info in prov["files"].items():
        path = TEACHING / name if name == cu.CENSUS else SUBSET / name
        assert path.stat().st_size == info["bytes"], name
        assert sha256(path) == info["sha256"], name


def test_small_enough_for_git(prov: dict) -> None:
    assert sum(f["bytes"] for f in prov["files"].values()) < 10_000_000


def test_store_opens_with_citation(store: Store, prov: dict) -> None:
    assert store.ref == "malecns@1.0"
    assert prov["license"] == "CC-BY-4.0"
    assert "10.1016/j.cell.2026.08.015" in store.citation_text()
    counts = prov["subset"]["counts"]
    assert len(store.neurons()) == counts["neurons"]
    assert len(store.edges()) == counts["edges"]


def test_focus_partner_lists_complete(store: Store) -> None:
    """Every edge in the subset touches a focus neuron, and the core neurons are focus."""
    n = store.neurons()
    focus = set(n.loc[n["focus"], "neuron_id"])
    e = store.edges()
    assert (e["pre"].isin(focus) | e["post"].isin(focus)).all()
    core = n["cell_type"].fillna("").str.match(r"^(LB3|MN9$)")
    assert n.loc[core, "focus"].all()
    assert (n["cell_type"] == "MN9").sum() == 2


def test_lb3_to_mn9_paths_stay_in_focus(store: Store) -> None:
    n = store.neurons()
    m = ConnectivityMatrix.from_store(store, min_weight=5)
    lb3 = n.loc[n["cell_type"].fillna("").str.startswith("LB3"), "neuron_id"]
    mn9 = n.loc[n["cell_type"] == "MN9", "neuron_id"]
    paths = find_paths(m, lb3.tolist(), mn9.tolist(), max_hops=3, min_edge_fraction=0.01)
    assert len(paths) > 0
    on_path = {nid for p in paths["path"] for nid in p}
    assert on_path <= set(n.loc[n["focus"], "neuron_id"])


def test_census_covers_whole_dataset(prov: dict) -> None:
    census = cu.load_census()
    assert len(census) == prov["source_store"]["provenance"]["counts"]["neurons"]
    assert census["neuron_id"].is_unique


def test_data_dir_prefers_checkout() -> None:
    assert cu.data_dir() == TEACHING


def test_download_path_verifies_checksums(tmp_path, monkeypatch) -> None:
    """Outside a checkout, files are fetched by URL and checked against provenance.json."""
    fetched = []

    def fake_download(url: str, dest: Path) -> None:
        rel = url.removeprefix(cu.RAW + "/")
        fetched.append(rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(TEACHING / rel, dest)

    fake_module_dir = tmp_path / "somewhere" / "notebooks"
    fake_module_dir.mkdir(parents=True)
    monkeypatch.setattr(cu, "__file__", str(fake_module_dir / "course_utils.py"))
    monkeypatch.setattr(cu.Path, "home", lambda: tmp_path / "home")
    monkeypatch.setattr(cu, "_download", fake_download)
    monkeypatch.delenv("FLYLAB_DATA", raising=False)

    d = cu.data_dir()
    assert d == tmp_path / "home" / ".cache" / "flylab" / cu.COURSE_REF
    assert set(fetched) == {
        f"{cu.SUBSET}/provenance.json",
        f"{cu.SUBSET}/neurons.parquet",
        f"{cu.SUBSET}/edges.parquet",
        cu.CENSUS,
    }
    # a corrupted file is re-fetched; a corrupted source raises
    (d / cu.CENSUS).write_bytes(b"broken")
    fetched.clear()
    cu.data_dir()
    assert fetched == [cu.CENSUS]

    def bad_download(url: str, dest: Path) -> None:
        dest.write_bytes(b"still broken")

    monkeypatch.setattr(cu, "_download", bad_download)
    (d / cu.CENSUS).write_bytes(b"broken")
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        cu.data_dir()
