from pathlib import Path

from flyconnectome_compare.compare.table0_overview import run_table0

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    result = run_table0(root / "data", root / "outputs")
    print(result["table"].to_string())
