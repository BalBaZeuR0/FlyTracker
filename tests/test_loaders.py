from pathlib import Path

import pytest

from flyconnectome_compare import DATASETS
from flyconnectome_compare.graph.build import build_graph
from flyconnectome_compare.io.loaders import UNIFIED_NEURON_COLUMNS, load_edges, load_neurons

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@pytest.mark.parametrize("dataset", DATASETS)
def test_load_edges(dataset):
    edges = load_edges(DATA_DIR, dataset)
    assert not edges.empty
    assert list(edges.columns) == ["pre_root_id", "post_root_id", "neuropil", "syn_count", "nt_type"]


@pytest.mark.parametrize("dataset", DATASETS)
def test_load_neurons(dataset):
    neurons = load_neurons(DATA_DIR, dataset)
    assert not neurons.empty
    assert list(neurons.columns) == UNIFIED_NEURON_COLUMNS


def test_build_graph():
    edges = load_edges(DATA_DIR, "manc")
    graph = build_graph(edges)
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0
