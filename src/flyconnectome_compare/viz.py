import matplotlib.pyplot as plt

FEMALE_COLOR = "#2a78d6"
MALE_COLOR = "#eb6834"
GRID_COLOR = "#e1e0d9"
AXIS_COLOR = "#c3c2b7"
TEXT_COLOR = "#0b0b0b"
MUTED_COLOR = "#898781"


def apply_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#fcfcfb",
            "axes.facecolor": "#fcfcfb",
            "axes.edgecolor": AXIS_COLOR,
            "axes.labelcolor": TEXT_COLOR,
            "axes.grid": True,
            "grid.color": GRID_COLOR,
            "grid.linewidth": 0.6,
            "text.color": TEXT_COLOR,
            "xtick.color": MUTED_COLOR,
            "ytick.color": MUTED_COLOR,
            "font.family": "sans-serif",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )
