from pathlib import Path

import pandas as pd

UNIFIED_NEURON_COLUMNS = ["root_id", "super_class", "class", "sub_class", "cell_type", "side", "nerve"]

_NEURONS_CSV_RENAME = {
    "Root ID": "root_id",
    "Super Class": "super_class",
    "Class": "class",
    "Sub Class": "sub_class",
    "Primary Cell Type": "cell_type",
    "Soma side": "side",
    "Nerve": "nerve",
}


def load_edges(data_dir: Path, dataset: str) -> pd.DataFrame:
    return pd.read_csv(data_dir / dataset / "connections_princeton.csv.gz")


def load_neurons(data_dir: Path, dataset: str) -> pd.DataFrame:
    if dataset == "fafb":
        classification = pd.read_csv(data_dir / "fafb" / "classification.csv.gz")
        cell_types = pd.read_csv(data_dir / "fafb" / "consolidated_cell_types.csv.gz")
        neurons = classification.merge(cell_types, on="root_id", how="left")
        neurons = neurons.rename(columns={"primary_type": "cell_type"})
    else:
        raw = pd.read_csv(data_dir / dataset / "neurons.csv.gz")
        neurons = raw.rename(columns=_NEURONS_CSV_RENAME)
    return neurons[UNIFIED_NEURON_COLUMNS]


def load_fafb_visual_neurons(data_dir: Path) -> pd.DataFrame:
    return pd.read_csv(data_dir / "fafb" / "visual_neuron_types.csv.gz")
