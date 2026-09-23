"""Builds the headline and sensitivity figures from the already-validated axis 1 results
(see Axis1_Sonuclar.md) — these numbers come from real completed runs, not fabricated; this
script just visualizes results that previously only existed as tables."""

from pathlib import Path

import pandas as pd

from flyconnectome_compare.compare.axis1_sex_cns import plot_modularity_headline, plot_sensitivity

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    figures_dir = root / "outputs" / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    headline = pd.DataFrame(
        [
            {"dataset": "banc", "modularity_observed": 0.758393, "modularity_null_mean": 0.175262, "modularity_null_std": 0.002081},
            {"dataset": "mcns", "modularity_observed": 0.715945, "modularity_null_mean": 0.095442, "modularity_null_std": 0.000455},
        ]
    )
    plot_modularity_headline(headline, figures_dir / "axis1_modularity_headline.png")

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
    plot_sensitivity(sensitivity, figures_dir / "axis1_sensitivity.png")
    print("done")
