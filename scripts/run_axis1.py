from pathlib import Path

from flyconnectome_compare.compare.axis1_sex_cns import run_axis1

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = run_axis1(root / "data", root / "outputs")
    print(result["global_table"].to_string())
    print(result["class_table"].head(20).to_string())
