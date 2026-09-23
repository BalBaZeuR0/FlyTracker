"""Codex's per-dataset Super Class vocabularies don't match even though the file schema
is identical (e.g. BANC's 'central_brain_intrinsic' vs MCNS's 'cb_intrinsic' vs FAFB/MAOL's
'central'/'optic') — this maps each dataset's raw labels onto one canonical set so
cross-dataset class-level comparisons (axis 1/2/3) are apples-to-apples. '_tbc'
(to-be-classified) labels are provisional/uncertain and are deliberately NOT folded into a
real category, to avoid manufacturing false agreement."""

import pandas as pd

CANONICAL_SUPER_CLASSES = (
    "ascending", "descending", "sensory", "sensory_ascending", "sensory_descending",
    "motor", "efferent", "efferent_ascending", "efferent_descending", "endocrine",
    "glia", "visceral_circulatory", "visual_projection", "visual_centrifugal",
    "central_brain_intrinsic", "optic_lobe_intrinsic", "ventral_nerve_cord_intrinsic",
    "other", "unclassified",
)

_SUPER_CLASS_MAPS = {
    "banc": {
        "ascending": "ascending",
        "ascending_visceral_circulatory": "visceral_circulatory",
        "central_brain_intrinsic": "central_brain_intrinsic",
        "descending": "descending",
        "glia": "glia",
        "motor": "motor",
        "not_a_neuron": "other",
        "optic_lobe_intrinsic": "optic_lobe_intrinsic",
        "sensory": "sensory",
        "sensory_ascending": "sensory_ascending",
        "sensory_descending": "sensory_descending",
        "trachea": "other",
        "ventral_nerve_cord_intrinsic": "ventral_nerve_cord_intrinsic",
        "visceral_circulatory": "visceral_circulatory",
        "visual_centrifugal": "visual_centrifugal",
        "visual_projection": "visual_projection",
    },
    "mcns": {
        "ENS": "other",
        "ascending_neuron": "ascending",
        "cb_efferent": "efferent",
        "cb_endocrine": "endocrine",
        "cb_intrinsic": "central_brain_intrinsic",
        "cb_motor": "motor",
        "cb_sensory": "sensory",
        "cb_sensory_tbc": "unclassified",
        "descending_neuron": "descending",
        "descending_neuron_tbc": "unclassified",
        "efferent_ascending": "efferent_ascending",
        "efferent_descending": "efferent_descending",
        "ol_intrinsic": "optic_lobe_intrinsic",
        "ol_sensory": "sensory",
        "sensory_ascending": "sensory_ascending",
        "sensory_ascending_tbc": "unclassified",
        "sensory_descending": "sensory_descending",
        "visual_centrifugal": "visual_centrifugal",
        "visual_projection": "visual_projection",
        "visual_projection_tbc": "unclassified",
        "vnc_efferent": "efferent",
        "vnc_endocrine": "endocrine",
        "vnc_intrinsic": "ventral_nerve_cord_intrinsic",
        "vnc_motor": "motor",
        "vnc_sensory": "sensory",
        "vnc_sensory_tbc": "unclassified",
        "vnc_tbc": "unclassified",
    },
    "manc": {
        "ascending": "ascending",
        "descending": "descending",
        "efferent": "efferent",
        "efferent_ascending": "efferent_ascending",
        "glia": "glia",
        # MANC uses three different labels for what looks like the same VNC-local-interneuron
        # concept within a single dataset — a data-quality quirk worth flagging in the writeup.
        "interneuron": "ventral_nerve_cord_intrinsic",
        "intrinsic": "ventral_nerve_cord_intrinsic",
        "intrinsic_neuron": "ventral_nerve_cord_intrinsic",
        "motor": "motor",
        "sensory": "sensory",
        "sensory_ascending": "sensory_ascending",
    },
    "maol": {
        "ascending": "ascending",
        "central": "other",
        "descending": "descending",
        "motor": "motor",
        "optic": "optic_lobe_intrinsic",
        "sensory": "sensory",
        "visual_centrifugal": "visual_centrifugal",
        "visual_projection": "visual_projection",
    },
    "fafb": {
        "ascending": "ascending",
        "central": "other",
        "descending": "descending",
        "endocrine": "endocrine",
        "motor": "motor",
        "optic": "optic_lobe_intrinsic",
        "sensory": "sensory",
        "sensory_ascending": "sensory_ascending",
        "visual_centrifugal": "visual_centrifugal",
        "visual_projection": "visual_projection",
    },
}


def canonicalize_super_class(dataset: str, raw: pd.Series) -> pd.Series:
    mapping = _SUPER_CLASS_MAPS[dataset]
    unmapped = sorted(set(raw.dropna().unique()) - set(mapping.keys()))
    if unmapped:
        raise ValueError(f"{dataset}: unmapped super_class values {unmapped} — extend taxonomy.py")
    return raw.map(mapping)
