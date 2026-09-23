"""Table 0: descriptive structural overview across all 5 Codex datasets, using axis 1's exact
metric battery (density, degree, modularity+null, rich-club) — no sex-difference claim, just
context, so MANC/FAFB aren't left out of the paper despite not having a dedicated deep-dive axis."""

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from flyconnectome_compare.compare.axis1_sex_cns import MIN_SYN_COUNT
from flyconnectome_compare.graph.build import build_graph, load_filtered_aggregated_edges
from flyconnectome_compare.graph.stats import degree_summary, modularity_with_null, rich_club_with_null
from flyconnectome_compare.viz import apply_style

DATASETS = ("fafb", "banc", "manc", "maol", "mcns")
DATASET_LABELS = {
    "fafb": "FAFB (dişi, merkezi beyin)",
    "banc": "BANC (dişi, tüm CNS)",
    "manc": "MANC (erkek, VNC)",
    "maol": "MAOL (erkek, görsel lob)",
    "mcns": "MCNS (erkek, tüm CNS)",
}
DATASET_COLORS = {
    "fafb": "#2a78d6",
    "banc": "#eb6834",
    "manc": "#1baf7a",
    "maol": "#eda100",
    "mcns": "#e87ba4",
}


def _plot_overview_bars(table: pd.DataFrame, path: Path) -> None:
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    colors = [DATASET_COLORS[d] for d in table["dataset"]]

    axes[0].bar(table["dataset"], table["density"], color=colors)
    axes[0].set_ylabel("Yoğunluk")
    axes[0].set_title("Ağ yoğunluğu")

    axes[1].bar(table["dataset"], table["modularity_ratio"], color=colors)
    axes[1].set_ylabel("Modülerlik oranı (gözlenen/null)")
    axes[1].set_title("Null-modele göre modülerlik")

    for ax in axes:
        ax.set_xticks(range(len(table)))
        ax.set_xticklabels([DATASET_LABELS[d] for d in table["dataset"]], rotation=30, ha="right", fontsize=8)

    fig.suptitle("Tablo 0 — 5 dataset'in yapısal genel bakışı (bağlamsal, cinsiyet iddiası yok)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_rich_club_all(rich_club_frames: dict, path: Path) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(7, 5))
    for dataset, table in rich_club_frames.items():
        ax.plot(table["k"], table["observed"], color=DATASET_COLORS[dataset], linewidth=2, label=DATASET_LABELS[dataset])
    ax.set_xlabel("Derece eşiği (k)")
    ax.set_ylabel("Rich-club katsayısı (gözlenen)")
    ax.legend(frameon=False, fontsize=7)
    fig.suptitle("Tablo 0 — 5 dataset'te rich-club eğrisi")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run_table0(data_dir: Path, output_dir: Path, n_randomizations: int = 3, seed: int = 0) -> dict:
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    rich_club_frames = {}
    for dataset in DATASETS:
        edges = load_filtered_aggregated_edges(data_dir, dataset, MIN_SYN_COUNT)
        graph = build_graph(edges)
        degrees = degree_summary(graph)
        mod = modularity_with_null(graph, n_randomizations=n_randomizations, seed=seed)
        rich_club_frames[dataset] = rich_club_with_null(graph, n_randomizations=n_randomizations, seed=seed)
        rows.append(
            {
                "dataset": dataset,
                "n_neurons_with_edges": graph.number_of_nodes(),
                "n_edges": graph.number_of_edges(),
                "density": nx.density(graph),
                "mean_in_degree": degrees["in_degree"].mean(),
                "mean_out_degree": degrees["out_degree"].mean(),
                "reciprocity": nx.reciprocity(graph),
                "modularity_observed": mod["observed"],
                "modularity_null_mean": mod["null_mean"],
                "modularity_null_std": mod["null_std"],
                "modularity_ratio": mod["ratio"],
            }
        )

    table = pd.DataFrame(rows)
    table.to_csv(tables_dir / "table0_overview.csv", index=False)
    for dataset, rc in rich_club_frames.items():
        rc.to_csv(tables_dir / f"table0_rich_club_{dataset}.csv", index=False)

    _plot_overview_bars(table, figures_dir / "table0_overview.png")
    _plot_rich_club_all(rich_club_frames, figures_dir / "table0_rich_club.png")

    return {"table": table, "rich_club": rich_club_frames}
