"""Embers-style figure: one panel per task, one line per model, accuracy vs output log probability.

Files are chosen by hand in PANELS and assigned to a probability level BY NAME
("low" / "medium" / "high"), so file order or sorting never matters.
Accuracy and standard error come from each JSON's own per-example 'accs'.
The only constants are the stimulus log-probabilities (x-axis) from embers_0504_alldecoding.R.
"""
import json
import math
import os

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

# ============================== Inputs (edit this) ==============================
DATA_DIR = "viz_data/logs_ollama"
OUTPUT_DIR = "graphs"
OUT_NAME = "ollama_graphs"
SUFFIX = "n=1.json"

COND = {"low": "lowprob", "medium": "mediumprob", "high": "highprob"}


def levels(prefix, model):
    """Paths for the three probability levels of one task/variant and model."""
    return {lvl: os.path.join(DATA_DIR, f"{prefix}_{cond}_{SUFFIX}")
            for lvl, cond in COND.items()}


# panel title, which stimulus log-prob set to use, {model label: {level name: path}}.
# Remove a level from a dict (or a whole model/panel) if you don't have it.
PANELS = [
    dict(title="Shift cipher (rot-13)", logprob="rot", runs={
        "ollama": levels("rot13enc", "Qwen3.8-27B"),
    }),
    dict(title="Pig Latin Enc", logprob="pig", runs={
        "ollama": levels("pigenc_ay", "Qwen3.8-27B"),
    }),
    dict(title="Pig Latin Dec", logprob="pig", runs={
            "ollama": levels("pigdec_ay", "Qwen3.8-27B"),
        }),
    dict(title="Rev Enc", logprob="reversal", runs={
        "ollama": levels("revenc", "Qwen3.8-27B"),
    }),
    dict(title="Rev Dec", logprob="reversal", runs={
        "ollama": levels("revdec", "Qwen3.8-27B"),
    }),
    # Another model: add  "other-model": levels("rot13dec", "other-model")  to a panel's runs.
]

# Stimulus log probabilities (properties of the task data, not results).
# Source: logprob_rot / logprob_pig / logprob_rev / logprob_swap in embers_0504_alldecoding.R
STIMULUS_LOGPROB = {
    "rot":      {"low": -144.54, "medium": -86.25, "high": -58.38},
    "pig":      {"low": -132.26, "medium": -86.86, "high": -62.54},
    "reversal": {"low": -144.54, "medium": -86.25, "high": -58.38},
    "swap":     {"low": -161.4,  "medium": -101.7, "high": -68.4},
}

PALETTE = ["#C77CFF", "#00BFC4", "#F8766D", "#B79F00", "#00BA38", "#00A9FF"]
MARKERS = ["s", "^", "o", "D", "o", "v"]
MARKER_SIZES = [8, 8, 8, 8, 6, 8]
REQUIRED_KEYS = {"prompts", "gts", "res", "accs", "acc", "eds", "ed"}


# ============================== Loading ==============================
def load_point(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    missing = REQUIRED_KEYS - d.keys()
    if missing:
        raise ValueError(f"{path}: missing keys {sorted(missing)}")
    v = np.asarray(d["accs"], dtype=float)
    if not (len(v) == len(d["res"]) == len(d["gts"])):
        raise ValueError(f"{path}: accs/res/gts lengths differ")
    acc, n = float(v.mean()), len(v)
    return acc, math.sqrt(acc * (1 - acc) / n)


def build(panels):
    data = []
    for panel in panels:
        xs = STIMULUS_LOGPROB[panel["logprob"]]
        series = {}
        for model, paths in panel["runs"].items():
            pts = []
            for lvl, path in paths.items():
                if lvl not in xs:
                    raise ValueError(f"{panel['title']}/{model}: unknown level '{lvl}' (use {list(xs)})")
                if not os.path.exists(path):
                    print(f"NOT FOUND, skipped: {path}")
                    continue
                acc, se = load_point(path)
                pts.append((xs[lvl], acc, se))
            if pts:
                series[model] = pts
        if series:
            data.append((panel["title"], series))
        else:
            print(f"Panel '{panel['title']}' has no usable files; skipped.")
    return data


# ============================== Plotting ==============================
def add_strip(ax, title):
    strip = make_axes_locatable(ax).append_axes("top", size="14%", pad=0)
    strip.set_facecolor("#D9D9D9")
    strip.set_xticks([]); strip.set_yticks([])
    for sp in strip.spines.values():
        sp.set_edgecolor("#333333")
    strip.text(0.5, 0.5, title, ha="center", va="center", fontsize=10)


def main():
    data = build(PANELS)
    if not data:
        raise SystemExit("No usable files in PANELS.")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    models = list(dict.fromkeys(m for _, s in data for m in s))
    style = {m: dict(color=PALETTE[i % len(PALETTE)], marker=MARKERS[i % len(MARKERS)],
                     ms=MARKER_SIZES[i % len(MARKER_SIZES)]) for i, m in enumerate(models)}

    n = len(data)
    fig, axes = plt.subplots(1, n, figsize=(max(10.5, 2.7 * n), 4.3), sharey=True, squeeze=False)
    plt.subplots_adjust(top=0.74, bottom=0.2, left=0.06, right=0.99, wspace=0.08)
    for ax, (title, series) in zip(axes[0], data):
        for model, pts in series.items():
            pts = sorted(pts)                                    # sorted by x, so file order is irrelevant
            x, y, se = (np.array(c, dtype=float) for c in zip(*pts))
            st = style[model]
            ax.fill_between(x, np.clip(y - se, 0, 1), np.clip(y + se, 0, 1),
                            color=st["color"], alpha=0.2, linewidth=0)
            ax.plot(x, y, color=st["color"], marker=st["marker"], markersize=st["ms"],
                    linewidth=2.0, label=model)
            if len(x) == 1:
                ax.errorbar(x, y, yerr=se, color=st["color"], capsize=4)
        ax.set_ylim(-0.02, 1.02)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.margins(x=0.15)
        ax.grid(True, color="#E5E5E5", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(axis="both", labelsize=9, colors="#4D4D4D")
        for sp in ax.spines.values():
            sp.set_edgecolor("#333333")
        add_strip(ax, title)
    axes[0][0].set_ylabel("Accuracy", fontsize=11)
    fig.supxlabel("Output log probability", fontsize=11, y=0.0)

    handles = {}
    for ax in axes[0]:
        h, l = ax.get_legend_handles_labels()
        handles.update(dict(zip(l, h)))
    fig.legend(handles.values(), handles.keys(), loc="upper center", ncol=min(5, len(handles)),
               frameon=False, fontsize=10, bbox_to_anchor=(0.53, 0.98))

    out = os.path.join(OUTPUT_DIR, f"{OUT_NAME}.png")
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print("Saved:", out)


if __name__ == "__main__":
    main()