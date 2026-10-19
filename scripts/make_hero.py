"""README hero image: a fruit fly and which part of its CNS each of the five connectomes covers.

Requires `pip install flybrains` (bundles the template meshes). The CNS outline is the male CNS
template (JRCFIB2022M brain + VNC) used as a common schematic for all five panels; neuron counts come
from outputs/tables/table0_overview.csv.

Photo: "Drosophila melanogaster 53362116" by Alexis, CC BY 4.0, via Wikimedia Commons.
"""
from pathlib import Path

import flybrains
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection
from matplotlib.patches import Patch

from flyconnectome_compare.viz import FEMALE_COLOR, MALE_COLOR, MUTED_COLOR, TEXT_COLOR

ROOT = Path(__file__).resolve().parents[1]
MESHES = Path(flybrains.__file__).parent / "meshes"
BG = "#fcfcfb"
BASE = "#d9d8d2"
OPTIC_LOBE_X = 215_000  # lateral edge of the left optic lobe in the template (x, nm)

# dataset, covered part, sex, neurons (table0_overview.csv)
PANELS = [
    ("FAFB", "brain", "female", 138_533),
    ("BANC", "brain + VNC", "female", 145_019),
    ("MANC", "VNC", "male", 23_537),
    ("MAOL", "optic lobe", "male", 51_175),
    ("MCNS", "brain + VNC", "male", 165_823),
]


def triangles(name: str) -> np.ndarray:
    m = trimesh.load(MESHES / f"{name}.ply")
    return m.vertices[m.faces][:, :, [0, 2]]  # x (left-right) vs z (anterior-posterior)


def draw(ax, tri, color, alpha=0.25):
    ax.add_collection(PolyCollection(tri, facecolor=color, edgecolor="none", alpha=alpha))


def main() -> None:
    brain, vnc = triangles("JRCFIB2022M_brain"), triangles("JRCFIB2022M_vnc")
    optic = brain[brain[:, :, 0].mean(axis=1) < OPTIC_LOBE_X]
    parts = {"brain": [brain], "VNC": [vnc], "brain + VNC": [brain, vnc], "optic lobe": [optic]}

    fig = plt.figure(figsize=(16, 5.6), facecolor=BG)
    photo = fig.add_axes([0.01, 0.1, 0.33, 0.74])
    img = plt.imread(ROOT / "assets" / "fruit_fly_photo.jpg")
    photo.imshow(img[200:560, 270:930])
    photo.axis("off")
    photo.set_title("The fruit fly, Drosophila melanogaster", fontsize=15, color=TEXT_COLOR, pad=10)
    fig.text(0.175, 0.1, "Photo: Alexis, CC BY 4.0, via Wikimedia Commons", ha="center", fontsize=8.5,
             color=MUTED_COLOR)

    fig.text(0.675, 0.94, "Five electron-microscopy connectomes of its central nervous system",
             ha="center", fontsize=15, color=TEXT_COLOR)
    for i, (name, part, sex, n) in enumerate(PANELS):
        ax = fig.add_axes([0.36 + i * 0.128, 0.19, 0.12, 0.64])
        for t in (brain, vnc):
            draw(ax, t, BASE, alpha=0.15)
        for t in parts[part]:
            draw(ax, t, FEMALE_COLOR if sex == "female" else MALE_COLOR)
        ax.set_xlim(20_000, 750_000)
        ax.set_ylim(1_080_000, 70_000)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(name, fontsize=15, fontweight="bold", color=TEXT_COLOR, pad=4)
        ax.text(0.5, -0.02, f"{part}\n{sex}\n{n:,} neurons", transform=ax.transAxes, ha="center", va="top",
                fontsize=10.5, color=TEXT_COLOR, linespacing=1.4)

    fig.legend(handles=[Patch(color=FEMALE_COLOR, label="covered, female"),
                        Patch(color=MALE_COLOR, label="covered, male"),
                        Patch(color=BASE, label="not in dataset")],
               loc="upper center", bbox_to_anchor=(0.675, 0.925), ncol=3, frameon=False, fontsize=10.5)
    out = ROOT / "assets" / "hero.png"
    fig.savefig(out, dpi=150, facecolor=BG)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
