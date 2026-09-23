"""Axis 2: FAFB's optic-lobe neurons vs MAOL (dedicated optic-lobe reconstruction) — reconstruction
consistency, following Schlegel et al. 2024's cross-brain cell-type-matching methodology (there
applied to FAFB vs hemibrain, not to this pair)."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

from flyconnectome_compare.io.loaders import load_edges, load_neurons
from flyconnectome_compare.viz import apply_style

OPTIC_SUPER_CLASSES = ("optic_lobe_intrinsic", "visual_projection", "visual_centrifugal")
DATASETS = ("fafb", "maol")
DATASET_LABELS = {"fafb": "FAFB (görsel lob kısmı)", "maol": "MAOL (dedike görsel lob)"}
DATASET_COLORS = {"fafb": "#2a78d6", "maol": "#4a3aa7"}


def _load_optic_neurons(data_dir: Path, dataset: str) -> pd.DataFrame:
    neurons = load_neurons(data_dir, dataset)
    return neurons[neurons["super_class"].isin(OPTIC_SUPER_CLASSES) & neurons["cell_type"].notna()]


def cell_type_coverage(neurons_by_dataset: dict) -> dict:
    type_sets = {ds: set(df["cell_type"].unique()) for ds, df in neurons_by_dataset.items()}
    shared = type_sets["fafb"] & type_sets["maol"]
    only_fafb = type_sets["fafb"] - type_sets["maol"]
    only_maol = type_sets["maol"] - type_sets["fafb"]
    union = type_sets["fafb"] | type_sets["maol"]
    return {
        "n_types_fafb": len(type_sets["fafb"]),
        "n_types_maol": len(type_sets["maol"]),
        "n_types_shared": len(shared),
        "n_types_only_fafb": len(only_fafb),
        "n_types_only_maol": len(only_maol),
        "jaccard": len(shared) / len(union) if union else float("nan"),
        "shared_types": shared,
    }


def cell_type_count_table(neurons_by_dataset: dict, shared_types: set) -> pd.DataFrame:
    counts = {
        ds: df[df["cell_type"].isin(shared_types)]["cell_type"].value_counts() for ds, df in neurons_by_dataset.items()
    }
    table = pd.DataFrame({"fafb": counts["fafb"], "maol": counts["maol"]}).fillna(0)
    table["ratio_maol_fafb"] = table["maol"] / table["fafb"].replace(0, pd.NA)
    return table.sort_values("ratio_maol_fafb", ascending=False).reset_index(names="cell_type")


def total_synapse_count_by_type(data_dir: Path, dataset: str, neurons: pd.DataFrame) -> pd.Series:
    edges = load_edges(data_dir, dataset)
    type_of = neurons.set_index("root_id")["cell_type"]
    pre_type = edges["pre_root_id"].map(type_of)
    return edges.assign(cell_type=pre_type).dropna(subset=["cell_type"]).groupby("cell_type")["syn_count"].sum()


def _plot_count_ratio(count_table: pd.DataFrame, path: Path, top_n: int = 25) -> None:
    apply_style()
    subset = count_table.dropna(subset=["ratio_maol_fafb"]).sort_values("ratio_maol_fafb", ascending=False)
    subset = pd.concat([subset.head(top_n), subset.tail(top_n)]).drop_duplicates(subset="cell_type")
    subset = subset.sort_values("ratio_maol_fafb")
    fig, ax = plt.subplots(figsize=(7, max(6, 0.22 * len(subset))))
    ax.barh(subset["cell_type"], subset["ratio_maol_fafb"], color="#4a3aa7")
    ax.axvline(1.0, color="#898781", linewidth=1.5, linestyle="--")
    ax.set_xscale("log")
    ax.set_xlabel("Nöron sayısı oranı (MAOL / FAFB), log ölçek")
    fig.suptitle("Axis 2 — Ortak hücre tiplerinde sayı oranı (en uç 2x25 tip)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_count_scatter(count_table: pd.DataFrame, path: Path) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(count_table["fafb"], count_table["maol"], s=12, alpha=0.5, color="#2a78d6")
    lim = [1, max(count_table["fafb"].max(), count_table["maol"].max()) * 1.5]
    ax.plot(lim, lim, color="#898781", linewidth=1, linestyle="--")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("FAFB'de nöron sayısı (log)")
    ax.set_ylabel("MAOL'de nöron sayısı (log)")
    rho, _ = stats.spearmanr(count_table["fafb"], count_table["maol"])
    ax.text(0.05, 0.95, f"Spearman ρ = {rho:.2f}", transform=ax.transAxes, va="top")
    fig.suptitle("Axis 2 — Ortak hücre tiplerinde nöron sayısı tutarlılığı")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _plot_synapse_scatter(synapse_table: pd.DataFrame, rho: float, path: Path) -> None:
    apply_style()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(synapse_table["fafb"], synapse_table["maol"], s=12, alpha=0.5, color="#eb6834")
    lim = [1, max(synapse_table["fafb"].max(), synapse_table["maol"].max()) * 1.5]
    ax.plot(lim, lim, color="#898781", linewidth=1, linestyle="--")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_xlabel("FAFB'de toplam sinaps sayısı, tip başına (log)")
    ax.set_ylabel("MAOL'de toplam sinaps sayısı, tip başına (log)")
    ax.text(0.05, 0.95, f"Spearman ρ = {rho:.2f}", transform=ax.transAxes, va="top")
    fig.suptitle("Axis 2 — Ortak hücre tiplerinde bağlantı-gücü tutarlılığı")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run_axis2(data_dir: Path, output_dir: Path) -> dict:
    tables_dir = output_dir / "tables"
    figures_dir = output_dir / "figures"
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    neurons_by_dataset = {ds: _load_optic_neurons(data_dir, ds) for ds in DATASETS}

    coverage = cell_type_coverage(neurons_by_dataset)
    coverage_table = pd.DataFrame([{k: v for k, v in coverage.items() if k != "shared_types"}])
    coverage_table.to_csv(tables_dir / "axis2_type_coverage.csv", index=False)

    count_table = cell_type_count_table(neurons_by_dataset, coverage["shared_types"])
    count_table.to_csv(tables_dir / "axis2_type_count_ratio.csv", index=False)

    synapse_by_type = {ds: total_synapse_count_by_type(data_dir, ds, neurons_by_dataset[ds]) for ds in DATASETS}
    synapse_table = pd.DataFrame(synapse_by_type).loc[list(coverage["shared_types"])].dropna()
    synapse_table.to_csv(tables_dir / "axis2_type_synapse_totals.csv")
    synapse_rho, _ = stats.spearmanr(synapse_table["fafb"], synapse_table["maol"])

    _plot_count_ratio(count_table, figures_dir / "axis2_type_count_ratio.png")
    _plot_count_scatter(count_table, figures_dir / "axis2_type_count_scatter.png")
    _plot_synapse_scatter(synapse_table, synapse_rho, figures_dir / "axis2_type_synapse_scatter.png")

    return {
        "coverage": coverage,
        "count_table": count_table,
        "synapse_table": synapse_table,
        "synapse_rho": synapse_rho,
    }
