import networkx as nx
import numpy as np
import pandas as pd


def degree_summary(graph: nx.Graph) -> pd.DataFrame:
    if isinstance(graph, nx.DiGraph):
        in_deg = dict(graph.in_degree())
        out_deg = dict(graph.out_degree())
        return pd.DataFrame(
            {
                "root_id": list(in_deg.keys()),
                "in_degree": list(in_deg.values()),
                "out_degree": [out_deg[n] for n in in_deg],
            }
        )
    degrees = dict(graph.degree())
    return pd.DataFrame({"root_id": list(degrees.keys()), "degree": list(degrees.values())})


def modularity(graph: nx.Graph, seed: int = 0) -> float:
    undirected = graph.to_undirected()
    communities = nx.algorithms.community.louvain_communities(undirected, weight="syn_count", seed=seed)
    return nx.algorithms.community.modularity(undirected, communities, weight="syn_count")


def rich_club_coefficients(graph: nx.Graph) -> dict:
    simple = nx.Graph(graph.to_undirected())
    simple.remove_edges_from(nx.selfloop_edges(simple))
    return nx.rich_club_coefficient(simple, normalized=False)


def directed_configuration_null(graph: nx.DiGraph, seed: int | None = None) -> nx.DiGraph:
    """Degree-preserving random graph used as a null model. Collapsing the configuration
    model's multi-edges/self-loops into a simple DiGraph slightly lowers the realized
    degree sequence versus the target — a standard, documented approximation, not a bug."""
    in_degrees = [d for _, d in graph.in_degree()]
    out_degrees = [d for _, d in graph.out_degree()]
    multi = nx.directed_configuration_model(in_degrees, out_degrees, seed=seed)
    simple = nx.DiGraph(multi)
    simple.remove_edges_from(nx.selfloop_edges(simple))
    return simple


def modularity_with_null(graph: nx.DiGraph, n_randomizations: int = 3, seed: int = 0) -> dict:
    observed = modularity(graph, seed=seed)
    null_values = []
    for i in range(n_randomizations):
        null_graph = directed_configuration_null(graph, seed=seed + i)
        null_values.append(modularity(null_graph, seed=seed))
    null_values = np.array(null_values)
    return {
        "observed": observed,
        "null_mean": float(null_values.mean()),
        "null_std": float(null_values.std()),
        "ratio": float(observed / null_values.mean()) if null_values.mean() else float("nan"),
    }


def rich_club_with_null(graph: nx.DiGraph, n_randomizations: int = 3, seed: int = 0) -> pd.DataFrame:
    observed = rich_club_coefficients(graph)
    null_runs = []
    for i in range(n_randomizations):
        null_graph = directed_configuration_null(graph, seed=seed + i)
        null_runs.append(rich_club_coefficients(null_graph))
    rows = []
    for k, observed_value in observed.items():
        null_values = np.array([run[k] for run in null_runs if k in run])
        if null_values.size == 0:
            continue
        rows.append(
            {
                "k": k,
                "observed": observed_value,
                "null_mean": float(null_values.mean()),
                "null_std": float(null_values.std()),
            }
        )
    return pd.DataFrame(rows).sort_values("k").reset_index(drop=True)
