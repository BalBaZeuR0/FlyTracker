import argparse
from pathlib import Path

from flyconnectome_compare.compare.axis1_sex_cns import MIN_SYN_COUNT, run_axis1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-syn-count", type=int, default=MIN_SYN_COUNT)
    parser.add_argument("--n-randomizations", type=int, default=3)
    parser.add_argument("--output-dir", type=str, default="outputs")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    result = run_axis1(
        root / "data",
        root / args.output_dir,
        n_randomizations=args.n_randomizations,
        min_syn_count=args.min_syn_count,
    )
    print(result["global_table"].to_string())
