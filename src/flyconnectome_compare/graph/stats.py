import networkx as nx
import pandas as pd


def degree_summary(graph: nx.Graph) -> pd.DataFrame:
    degrees = dict(graph.degree())
    return pd.DataFrame({"root_id": list(degrees.keys()), "degree": list(degrees.values())})


def modularity(graph: nx.Graph) -> float:
    raise NotImplementedError("axis 1 metric set not decided yet — see FlyConnectome_Compare/DURUM.md")


def rich_club_coefficients(graph: nx.Graph) -> dict[int, float]:
    raise NotImplementedError("axis 1 metric set not decided yet — see FlyConnectome_Compare/DURUM.md")
