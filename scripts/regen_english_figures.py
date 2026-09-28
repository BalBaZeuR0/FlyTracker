"""Re-renders every figure with the now-English plotting code, reusing already-computed results
(CSVs) wherever possible instead of re-running expensive Louvain/null-model computation."""

from pathlib import Path

import pandas as pd

from flyconnectome_compare.compare import axis1_sex_cns as a1
from flyconnectome_compare.compare import table0_overview as t0
from flyconnectome_compare.compare.axis2_reconstruction import run_axis2
from flyconnectome_compare.graph.build import build_graph, load_filtered_aggregated_edges
from flyconnectome_compare.graph.stats import degree_summary

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"

# ---- Axis 1: class breakdown + class ratio (from cached CSVs) ----
class_table = pd.read_csv(TABLES / "axis1_class_breakdown.csv")
ratio_table = pd.read_csv(TABLES / "axis1_class_density_ratio.csv")
global_table = pd.read_csv(TABLES / "axis1_global_stats.csv").set_index("dataset")
global_ratio = global_table.loc["mcns", "density"] / global_table.loc["banc", "density"]

a1._plot_class_breakdown(class_table, FIGURES / "axis1_class_breakdown.png")
a1._plot_class_ratio(ratio_table, global_ratio, FIGURES / "axis1_class_ratio.png")

# ---- Axis 1: rich-club (from cached CSVs) ----
rich_club_frames = {ds: pd.read_csv(TABLES / f"axis1_rich_club_{ds}.csv") for ds in a1.DATASETS}
a1._plot_rich_club(rich_club_frames, FIGURES / "axis1_rich_club.png")

# ---- Axis 1: degree distribution (cheap to rebuild — no Louvain/null model needed) ----
degree_frames = {}
for dataset in a1.DATASETS:
    edges = load_filtered_aggregated_edges(ROOT / "data", dataset, a1.MIN_SYN_COUNT)
    graph = build_graph(edges)
    degree_frames[dataset] = degree_summary(graph)
a1._plot_degree_distributions(degree_frames, FIGURES / "axis1_degree_distribution.png")

# ---- Axis 1: headline + sensitivity (validated numbers, see Axis1_Sonuclar.md) ----
headline = pd.DataFrame(
    [
        {"dataset": "banc", "modularity_observed": 0.758393, "modularity_null_mean": 0.175262, "modularity_null_std": 0.002081},
        {"dataset": "mcns", "modularity_observed": 0.715945, "modularity_null_mean": 0.095442, "modularity_null_std": 0.000455},
    ]
)
a1.plot_modularity_headline(headline, FIGURES / "axis1_modularity_headline.png")

sensitivity = pd.DataFrame(
    [
        {"dataset": "banc", "min_syn_count": 3, "modularity_ratio": 5.828900},
        {"dataset": "banc", "min_syn_count": 5, "modularity_ratio": 4.315295},
        {"dataset": "banc", "min_syn_count": 10, "modularity_ratio": 2.845850},
        {"dataset": "mcns", "min_syn_count": 3, "modularity_ratio": 7.689512},
        {"dataset": "mcns", "min_syn_count": 5, "modularity_ratio": 7.515004},
        {"dataset": "mcns", "min_syn_count": 10, "modularity_ratio": 5.101950},
    ]
)
a1.plot_sensitivity(sensitivity, FIGURES / "axis1_sensitivity.png")

# ---- Table 0 (from cached CSVs) ----
table0 = pd.read_csv(TABLES / "table0_overview.csv")
t0._plot_overview_bars(table0, FIGURES / "table0_overview.png")
table0_rich_club = {ds: pd.read_csv(TABLES / f"table0_rich_club_{ds}.csv") for ds in t0.DATASETS}
t0._plot_rich_club_all(table0_rich_club, FIGURES / "table0_rich_club.png")

# ---- Axis 2: cheap enough to just rerun fully ----
run_axis2(ROOT / "data", ROOT / "outputs")

print("All figures regenerated in English.")
