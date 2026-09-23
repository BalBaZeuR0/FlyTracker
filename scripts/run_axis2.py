from pathlib import Path

from flyconnectome_compare.compare.axis2_reconstruction import run_axis2

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = run_axis2(root / "data", root / "outputs")
    print("Coverage:", {k: v for k, v in result["coverage"].items() if k != "shared_types"})
    print(result["count_table"].head(15).to_string())
    print(result["count_table"].tail(15).to_string())
    print("Synapse-total Spearman rho:", result["synapse_rho"])
