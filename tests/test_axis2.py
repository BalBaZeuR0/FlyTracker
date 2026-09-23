from pathlib import Path

from flyconnectome_compare.compare.axis2_reconstruction import (
    DATASETS,
    _load_optic_neurons,
    cell_type_coverage,
    cell_type_count_table,
)

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_load_optic_neurons_nonempty():
    for dataset in DATASETS:
        neurons = _load_optic_neurons(DATA_DIR, dataset)
        assert not neurons.empty
        assert neurons["cell_type"].notna().all()


def test_cell_type_coverage_has_shared_types():
    neurons_by_dataset = {ds: _load_optic_neurons(DATA_DIR, ds) for ds in DATASETS}
    coverage = cell_type_coverage(neurons_by_dataset)
    assert coverage["n_types_shared"] > 0
    assert 0 < coverage["jaccard"] <= 1


def test_cell_type_count_table_columns():
    neurons_by_dataset = {ds: _load_optic_neurons(DATA_DIR, ds) for ds in DATASETS}
    coverage = cell_type_coverage(neurons_by_dataset)
    table = cell_type_count_table(neurons_by_dataset, coverage["shared_types"])
    assert {"cell_type", "fafb", "maol", "ratio_maol_fafb"} <= set(table.columns)
    assert len(table) == coverage["n_types_shared"]
