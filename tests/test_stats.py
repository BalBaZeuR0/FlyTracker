import networkx as nx

from flyconnectome_compare.graph.stats import (
    degree_summary,
    directed_configuration_null,
    modularity,
    modularity_with_null,
    rich_club_coefficients,
)


def _toy_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    edges = [(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4), (1, 4)]
    for u, v in edges:
        graph.add_edge(u, v, syn_count=5)
    return graph


def test_degree_summary():
    degrees = degree_summary(_toy_graph())
    assert set(degrees["root_id"]) == {1, 2, 3, 4, 5, 6}
    assert degrees.loc[degrees["root_id"] == 1, "out_degree"].item() == 2


def test_modularity_is_bounded():
    value = modularity(_toy_graph())
    assert -1.0 <= value <= 1.0


def test_directed_configuration_null_preserves_node_count():
    graph = _toy_graph()
    null_graph = directed_configuration_null(graph, seed=0)
    assert null_graph.number_of_nodes() == graph.number_of_nodes()


def test_rich_club_coefficients_returns_dict():
    coefficients = rich_club_coefficients(_toy_graph())
    assert isinstance(coefficients, dict)


def test_modularity_with_null_shape():
    result = modularity_with_null(_toy_graph(), n_randomizations=2, seed=0)
    assert {"observed", "null_mean", "null_std", "ratio"} <= result.keys()
