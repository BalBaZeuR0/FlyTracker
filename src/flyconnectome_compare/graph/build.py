import networkx as nx
import pandas as pd


def build_graph(edges: pd.DataFrame, directed: bool = True) -> nx.DiGraph | nx.Graph:
    graph_cls = nx.DiGraph if directed else nx.Graph
    graph = graph_cls()
    for row in edges.itertuples(index=False):
        graph.add_edge(row.pre_root_id, row.post_root_id, syn_count=row.syn_count, neuropil=row.neuropil)
    return graph
