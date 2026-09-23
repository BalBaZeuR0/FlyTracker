"""Axis 1: BANC (female, whole CNS) vs MCNS (male, whole CNS) network statistics."""

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from flyconnectome_compare.graph.build import build_graph, load_filtered_aggregated_edges
from flyconnectome_compare.graph.stats import degree_summary, modularity_with_null, rich_club_with_null
from flyconnectome_compare.io.loaders import load_neurons
from flyconnectome_compare.viz import apply_style

MIN_SYN_COUNT = 5
DATASETS = ("banc", "mcns")
DATASET_LABELS = {"banc": "BANC (dişi, tüm CNS)", "mcns": "MCNS (erkek, tüm CNS)"}
DATASET_COLORS = {"banc": "#2a78d6", "mcns": "#eb6834"}


def _class_level_breakdown(edges_by_dataset: dict, neurons_by_dataset: dict) -> pd.DataFrame:
    tables = []
    for dataset, edges in edges_by_dataset.items():
        class_of = neurons_by_dataset[dataset].set_index("root_id")["super_class"]
        merged = edges.assign(
            source_class=edges["pre_root_id"].map(class_of),
            target_class=edges["post_root_id"].map(class_of),
        ).dropna(subset=["source_class", "target_class"])
        counts = merged.groupby(["source_class", "target_class"], as_index=False)["syn_count"].agg(
            n_edges="count", total_synapses="sum"
        )
        counts.insert(0, "dataset", dataset)
        tables.append(counts)
    return pd.concat(tables, ignore_index=True)


def _plot_degree_distributions(degree_frames: dict, path: Path) -> None:
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, column, title in zip(axes, ["in_degree", "out_degree"], ["In-degree", "Out-degree"]):
        for dataset, degrees in degree_frames.items():
            values = degrees[column][degrees[column] > 0]
            ax.hist(
                values, bins=60, histtype="step", linewidth=2, log=True,
                color=DATASET_COLORS[dataset], label=DATASET_LABELS[dataset],
            )
        ax.set_xlabel(title)
        ax.set_xscale("log")
    axes[0].set_ylabel("Nöron sayısı (log)")
    axes[0].legend(frameon=False, fontsize=8)
    fig.suptitle("Axis 1 — Derece dağılımı: BANC vs MCNS")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_rich_club(rich_club_frames: dict, path: Path) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for dataset, table in rich_club_frames.items():
        color = DATASET_COLORS[dataset]
        ax.plot(table["k"], table["observed"], color=color, linewidth=2, label=f"{DATASET_LABELS[dataset]} — gözlenen")
        ax.plot(
            table["k"], table["null_mean"], color=color, linewidth=1, linestyle="--", alpha=0.6,
            label=f"{DATASET_LABELS[dataset]} — null ort.",
        )
        ax.fill_between(
            table["k"], table["null_mean"] - table["null_std"], table["null_mean"] + table["null_std"],
            color=color, alpha=0.12,
        )
    ax.set_xlabel("Derece eşiği (k)")
    ax.set_ylabel("Rich-club katsayısı")
    ax.legend(frameon=False, fontsize=7)
    fig.suptitle("Axis 1 — Rich-club: gözlenen vs derece-korumalı null model")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _class_density_ratio(class_table: pd.DataFrame) -> pd.DataFrame:
    """Whether the global density gap between datasets is uniform across cell classes, or
    concentrated in specific ones — a category with a much larger gap than the global ratio
    points at a reconstruction-completeness difference in that region, not a whole-brain effect."""
    totals = class_table.groupby(["dataset", "source_class"])["n_edges"].sum().unstack("dataset")
    totals = totals[(totals.get("banc", 0) > 0) & (totals.get("mcns", 0) > 0)]
    ratio = (totals["mcns"] / totals["banc"]).rename("ratio_mcns_banc")
    return pd.concat([totals, ratio], axis=1).sort_values("ratio_mcns_banc", ascending=False).reset_index()


def _plot_class_ratio(ratio_table: pd.DataFrame, global_ratio: float, path: Path) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(ratio_table["source_class"], ratio_table["ratio_mcns_banc"], color="#4a3aa7")
    ax.axvline(global_ratio, color="#898781", linewidth=1.5, linestyle="--")
    ax.text(
        global_ratio, -0.6, f" global oran {global_ratio:.2f}x", color="#898781", fontsize=8, va="top",
    )
    ax.set_xlabel("Yoğunluk oranı (MCNS / BANC)")
    fig.suptitle("Axis 1 — Sınıf başına yoğunluk oranı, global orana kıyasla")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_class_breakdown(class_table: pd.DataFrame, path: Path) -> None:
    apply_style()
    class_table = class_table[
        (class_table["source_class"] != "unclassified") & (class_table["target_class"] != "unclassified")
    ]
    totals = class_table.groupby(["dataset", "source_class"], as_index=False)["n_edges"].sum()
    pivot = totals.pivot(index="source_class", columns="dataset", values="n_edges").fillna(0)
    pivot = pivot.sort_values("banc", ascending=True)
    fig, ax = plt.subplots(figsize=(7, 5.5))
    positions = range(len(pivot))
    height = 0.35
    ax.barh(
        [p + height / 2 for p in positions], pivot["banc"], height=height,
        color=DATASET_COLORS["banc"], label=DATASET_LABELS["banc"],
    )
    ax.barh(
        [p - height / 2 for p in positions], pivot["mcns"], height=height,
        color=DATASET_COLORS["mcns"], label=DATASET_LABELS["mcns"],
    )
    ax.set_yticks(list(positions))
    ax.set_yticklabels(pivot.index)
    ax.set_xlabel("Kaynak sınıftan giden bağlantı sayısı")
    ax.legend(frameon=False)
    fig.suptitle("Axis 1 — Super Class bazlı çıkan bağlantı sayısı")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run_axis1(
    data_dir: Path, output_dir: Path, n_randomizations: int = 3, seed: int = 0, min_syn_count: int = MIN_SYN_COUNT
) -> dict:
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    edges_by_dataset = {ds: load_filtered_aggregated_edges(data_dir, ds, min_syn_count) for ds in DATASETS}
    neurons_by_dataset = {ds: load_neurons(data_dir, ds) for ds in DATASETS}
    graphs = {ds: build_graph(edges) for ds, edges in edges_by_dataset.items()}

    global_rows = []
    degree_frames = {}
    rich_club_frames = {}
    for dataset, graph in graphs.items():
        degrees = degree_summary(graph)
        degree_frames[dataset] = degrees
        mod = modularity_with_null(graph, n_randomizations=n_randomizations, seed=seed)
        rich_club_frames[dataset] = rich_club_with_null(graph, n_randomizations=n_randomizations, seed=seed)
        global_rows.append(
            {
                "dataset": dataset,
                "min_syn_count": min_syn_count,
                "n_randomizations": n_randomizations,
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

    global_table = pd.DataFrame(global_rows)
    global_table.to_csv(tables_dir / "axis1_global_stats.csv", index=False)
    for dataset, table in rich_club_frames.items():
        table.to_csv(tables_dir / f"axis1_rich_club_{dataset}.csv", index=False)

    class_table = _class_level_breakdown(edges_by_dataset, neurons_by_dataset)
    class_table.to_csv(tables_dir / "axis1_class_breakdown.csv", index=False)

    ratio_table = _class_density_ratio(class_table)
    ratio_table.to_csv(tables_dir / "axis1_class_density_ratio.csv", index=False)
    global_ratio = global_table.set_index("dataset").loc["mcns", "density"] / global_table.set_index("dataset").loc["banc", "density"]

    _plot_degree_distributions(degree_frames, figures_dir / "axis1_degree_distribution.png")
    _plot_rich_club(rich_club_frames, figures_dir / "axis1_rich_club.png")
    _plot_class_breakdown(class_table, figures_dir / "axis1_class_breakdown.png")
    _plot_class_ratio(ratio_table, global_ratio, figures_dir / "axis1_class_ratio.png")

    return {
        "global_table": global_table,
        "class_table": class_table,
        "ratio_table": ratio_table,
        "rich_club": rich_club_frames,
    }
