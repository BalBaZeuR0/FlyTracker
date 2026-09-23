from pathlib import Path

import networkx as nx
import pandas as pd

from flyconnectome_compare.io.loaders import filter_by_synapse_count, load_edges


def load_filtered_aggregated_edges(data_dir: Path, dataset: str, min_syn_count: int) -> pd.DataFrame:
    edges = load_edges(data_dir, dataset)
    edges = filter_by_synapse_count(edges, min_syn_count)
    return aggregate_edges(edges)


def aggregate_edges(edges: pd.DataFrame) -> pd.DataFrame:
    """Collapses per-neuropil rows into one pre->post total — the raw edge list has one
    row per (pre, post, neuropil), which would silently drop weight if built as a simple
    graph without summing first."""
    return edges.groupby(["pre_root_id", "post_root_id"], as_index=False)["syn_count"].sum()


def build_graph(edges: pd.DataFrame, directed: bool = True) -> nx.DiGraph | nx.Graph:
    graph_cls = nx.DiGraph if directed else nx.Graph
    return nx.from_pandas_edgelist(
        edges, source="pre_root_id", target="post_root_id", edge_attr="syn_count", create_using=graph_cls()
    )
