"""Rare-vs-common bar chart (one row per model), in the style of the Embers/o1 figure.

Files are listed by hand in COLUMNS and assigned to "rare" / "common" by name.
Accuracy and standard error come from each JSON's own per-example 'accs'.
Acronyms: acronym1 = first letter of each word (common), acronym2 = second letter (rare).
"""
import json
import math
import os

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

# ============================== Inputs (edit this) ==============================
DATA_DIR = "viz_data/logs"
OUTPUT_DIR = "graphs"
OUT_NAME = "acronym_bars"
SUFFIX = "temp=0.7_n=1.json"
VARIANTS = ["rare", "common"]
PALETTE = ["#C77CFF", "#00BFC4", "#F8766D", "#B79F00", "#00BA38", "#00A9FF"]


def f(prefix, model):
    return os.path.join(DATA_DIR, f"{prefix}_{model}_{SUFFIX}")


# column title -> {model label: {"rare": path, "common": path}}
# Add more models as extra entries, more columns as extra keys.
COLUMNS = {
    "Acronyms": {
        "gpt-oss-20b": {"rare": f("acronym2_11", "gpt-oss-20b"),
                        "common": f("acronym1_11", "gpt-oss-20b")},
        # "other-model": {"rare": f("acronym2_11", "other-model"), "common": f("acronym1_11", "other-model")},
    },
}
REQUIRED_KEYS = {"prompts", "gts", "res", "accs", "acc", "eds", "ed"}


# ============================== Loading ==============================
def load_point(path):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    missing = REQUIRED_KEYS - d.keys()
    if missing:
        raise ValueError(f"{path}: missing keys {sorted(missing)}")
    v = np.asarray(d["accs"], dtype=float)
    if not (len(v) == len(d["res"]) == len(d["gts"])):
        raise ValueError(f"{path}: accs/res/gts lengths differ")
    p = float(v.mean())
    return p, math.sqrt(p * (1 - p) / len(v))


def collect():
    """acc[(column, model, variant)] = (accuracy, standard error)."""
    acc = {}
    for col, models in COLUMNS.items():
        for model, paths in models.items():
            for var, path in paths.items():
                if var not in VARIANTS:
                    raise ValueError(f"{col}/{model}: unknown variant '{var}' (use {VARIANTS})")
                if not os.path.exists(path):
                    print(f"NOT FOUND, skipped: {path}")
                    continue
                acc[(col, model, var)] = load_point(path)
    return acc


# ============================== Plotting ==============================
def strip(ax, text, where):
    s = make_axes_locatable(ax).append_axes(where, size="14%" if where == "top" else "22%", pad=0)
    s.set_facecolor("#D9D9D9")
    s.set_xticks([]); s.set_yticks([])
    for sp in s.spines.values():
        sp.set_edgecolor("#333333")
    s.text(0.5, 0.5, text, ha="center", va="center", fontsize=9,
           rotation=-90 if where == "right" else 0)


def main():
    acc = collect()
    if not acc:
        raise SystemExit("No usable files in COLUMNS.")
    cols = list(COLUMNS)
    models = list(dict.fromkeys(m for c in COLUMNS.values() for m in c))
    color = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(models)}

    fig, axes = plt.subplots(len(models), len(cols), figsize=(2.0 * len(cols) + 1.2, 1.5 * len(models) + 0.8),
                             sharey=True, squeeze=False)
    plt.subplots_adjust(hspace=0.12, wspace=0.12)
    for r, m in enumerate(models):
        for c, col in enumerate(cols):
            ax = axes[r][c]
            for i, var in enumerate(VARIANTS):
                if (col, m, var) not in acc:
                    print(f"missing: {col} {m} {var}")
                    continue
                p, se = acc[(col, m, var)]
                ax.bar(i, p, width=0.7, color=color[m], edgecolor="black", linewidth=0.8)
                ax.errorbar(i, p, yerr=se, color="black", capsize=3, linewidth=1)
            ax.set_xlim(-0.6, len(VARIANTS) - 0.4)
            ax.set_ylim(0, 1.05)
            ax.set_yticks([0, 0.5, 1.0])
            ax.grid(True, axis="y", color="#E5E5E5")
            ax.set_axisbelow(True)
            ax.set_xticks(range(len(VARIANTS)))
            ax.set_xticklabels([v.capitalize() for v in VARIANTS] if r == len(models) - 1 else [],
                               rotation=45, ha="right", fontsize=8)
            ax.tick_params(labelsize=8)
            for sp in ax.spines.values():
                sp.set_edgecolor("#333333")
            if r == 0:
                strip(ax, col, "top")
            if c == len(cols) - 1:
                strip(ax, m, "right")
    fig.supylabel("Accuracy", fontsize=10)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out = os.path.join(OUTPUT_DIR, f"{OUT_NAME}.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print("Saved:", out)


if __name__ == "__main__":
    main()