"""Thinking length vs output log probability (cf. Fig. 2 of the o1 'embers' paper).

One panel per task, one line per model; y = median thinking length (characters of the JSON's
'thinking' entries) of each group of examples, x = stimulus log probability of that group.
Files are listed by hand and assigned to a level by name. Everything plotted is computed from the
JSONs; the only constants are the stimulus log-probs (from embers_0504_alldecoding.R).
"""
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

# ============================== Inputs (edit this) ==============================
DATA_DIR = "viz_data/logs_gpt-oss-20B"
DATA_DIR2 = "viz_data/logs_qwen3.8-27B"
OUTPUT_DIR = "graphs"
OUT_NAME = "think_len_graphs"
SUFFIX = "n=1.json"

SHOW_IQR = False       # shade the 25th-75th percentile band around each median
SHARE_Y = True         # paper figure: one shared y axis, free x axis per panel
LOG_Y = False
FALLBACK_TO_RES = False   # True: files without a 'thinking' key use the part of 'res' before 'assistantfinal'

COND = {"low": "lowprob", "medium": "mediumprob", "high": "highprob"}   # change if your files say "medprob"


def levels(prefix, data_dir):
    return {lvl: os.path.join(data_dir, f"{prefix}_{cond}_{SUFFIX}") for lvl, cond in COND.items()}


# panel title, stimulus log-prob set, {model label: {level: path}}
PANELS = [
    dict(title="Shift cipher enc (rot-12)", logprob="rot", runs={
        #"gpt-oss-20B": levels("rot12enc", DATA_DIR),
        "Qwen3.8-27B": levels("rot12enc", DATA_DIR2),
    }),
    dict(title="Shift cipher dec (rot-12)", logprob="rot", runs={
        #"gpt-oss-20B": levels("rot12dec", DATA_DIR),
        "Qwen3.8-27B": levels("rot12dec", DATA_DIR2),
    }),
    dict(title="Shift cipher enc (rot-13)", logprob="rot", runs={
        #"gpt-oss-20B": levels("rot13enc", DATA_DIR),
        "Qwen3.8-27B": levels("rot13enc", DATA_DIR2),
    }),
    dict(title="Shift cipher dec (rot-13)", logprob="rot", runs={
        #"gpt-oss-20B": levels("rot13dec", DATA_DIR),
        "Qwen3.8-27B": levels("rot13dec", DATA_DIR2),
    }),
    dict(title="Pig Latin Enc", logprob="pig", runs={
        #"gpt-oss-20B": levels("pigenc_ay", DATA_DIR),
        "Qwen3.8-27B": levels("pigenc_ay", DATA_DIR2),
    }),
    dict(title="Pig Latin Dec", logprob="pig", runs={
        #"gpt-oss-20B": levels("pigdec_ay", DATA_DIR),
        "Qwen3.8-27B": levels("pigdec_ay", DATA_DIR2),
    }),
    dict(title="Rev Enc", logprob="reversal", runs={
        #"gpt-oss-20B": levels("revenc", DATA_DIR),
        "Qwen3.8-27B": levels("revenc", DATA_DIR2),
    }),
    dict(title="Rev Dec", logprob="reversal", runs={
        #"gpt-oss-20B": levels("revdec", DATA_DIR),
        "Qwen3.8-27B": levels("revdec", DATA_DIR2),
    }),
]

STIMULUS_LOGPROB = {          # source: logprob_* in embers_0504_alldecoding.R
    "rot":      {"low": -144.54, "medium": -86.25, "high": -58.38},
    "pig":      {"low": -132.26, "medium": -86.86, "high": -62.54},
    "reversal": {"low": -144.54, "medium": -86.25, "high": -58.38},
    "swap":     {"low": -161.4,  "medium": -101.7, "high": -68.4},
}

PALETTE = ["#C77CFF", "#F72811", "#F8766D", "#B79F00", "#00BA38", "#00A9FF"] # #C77CFF Qwen Color / #F72811 gpt Color
MARKERS = ["s", "^", "o", "D", "o", "v"]
MARKER_SIZES = [8, 8, 8, 8, 6, 8]
# optional per-model look (the paper draws o1-preview as a blue downward triangle)
MODEL_STYLE = {
    "gpt-oss-20b": dict(color="#00A9FF", marker="v", ms=8),
}


# ============================== Thinking length ==============================
def thinking_lengths(d, path):
    """Character length of each example's thinking.

    - File has a 'thinking' field (e.g. Qwen): length of each thinking string.
    - No 'thinking' field (e.g. gpt-oss, chain of thought lives in 'res'): length of each 'res' string.
    """
    name = os.path.basename(path)
    if "thinking" in d:
        th = d["thinking"]
        if len(th) != len(d["res"]):
            raise ValueError(f"{name}: 'thinking' and 'res' lengths differ")
        return np.array([len(t) if isinstance(t, str) else 0 for t in th], dtype=float)
    print(f"NOTE {name}: no 'thinking' field; using the length of 'res'.")
    return np.array([len(r) if isinstance(r, str) else 0 for r in d["res"]], dtype=float)


def load_point(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    L = thinking_lengths(d, path)
    if L is None:
        return None
    return float(np.median(L)), float(np.percentile(L, 25)), float(np.percentile(L, 75))


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
                stats = load_point(path)
                if stats:
                    pts.append((xs[lvl], *stats))
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
    style = {m: MODEL_STYLE.get(m, dict(color=PALETTE[i % len(PALETTE)], marker=MARKERS[i % len(MARKERS)],
                                        ms=MARKER_SIZES[i % len(MARKER_SIZES)]))
             for i, m in enumerate(models)}
    ymax_all = max(p[1] for _, s in data for pts in s.values() for p in pts) or 1.0

    n = len(data)
    fig, axes = plt.subplots(1, n, figsize=(max(10.5, 2.9 * n), 4.3), sharey=SHARE_Y, squeeze=False)
    plt.subplots_adjust(top=0.78, bottom=0.2, left=0.08, right=0.99, wspace=0.08 if SHARE_Y else 0.28)
    for k, (ax, (title, series)) in enumerate(zip(axes[0], data)):
        for model, pts in series.items():
            x, y, q1, q3 = (np.array(c, dtype=float) for c in zip(*sorted(pts)))
            st = style[model]
            if SHOW_IQR:
                ax.fill_between(x, q1, q3, color=st["color"], alpha=0.2, linewidth=0)
            ax.plot(x, y, color=st["color"], marker=st["marker"], markersize=st["ms"],
                    linewidth=2.0, label=model)
        if LOG_Y:
            ax.set_yscale("log")
        else:
            top = ymax_all if SHARE_Y else (max(p[1] for pts in series.values() for p in pts) or 1.0)
            ax.set_ylim(-0.05 * top, 1.08 * top)
        ax.margins(x=0.12)
        ax.grid(True, color="#E5E5E5", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(axis="both", labelsize=8, colors="#4D4D4D")
        if SHARE_Y and k > 0:
            ax.tick_params(labelleft=False)
        for sp in ax.spines.values():
            sp.set_edgecolor("#333333")
        add_strip(ax, title)
    axes[0][0].set_ylabel("Thinking length (characters)", fontsize=11)
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