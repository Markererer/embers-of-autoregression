"""Rare-vs-common bar chart (one row per model), in the style of the Embers/o1 figure.


Files are listed by hand in COLUMNS and assigned to "rare" / "common" by name.
Edit distance (the JSON's 'ed') and its standard error (from the per-example 'eds') are plotted.
Acronyms: acronym1 = first letter of each word (common), acronym2 = second letter (rare).
"""
import json
import math
import os
import matplotlib.pyplot as plt
import numpy as np


# ============================== Inputs (edit this) ==============================
DATA_DIR = "viz_data/logs_gpt-oss-20B"
DATA_DIR2 = "viz_data/logs_qwen3.8-27B"
OUTPUT_DIR = "graphs"
OUT_NAME = "bars_graphs_ed"
SUFFIX = "n=1.json"
VARIANTS = ["rare", "common"]
PALETTE = ["#C77CFF", "#F72811", "#F8766D", "#B79F00", "#00BA38", "#00A9FF"]  # #C77CFF Qwen Color / #F72811 gpt Color



def f(prefix, data_dir):
    return os.path.join(data_dir, f"{prefix}_{SUFFIX}")




# column title -> {model label: {"rare": path, "common": path}}
# Add more models as extra entries, more columns as extra keys.
COLUMNS = {
    "Shift Enc": {
        #"gpt-oss-20b": {"rare": f("acronym2_11", DATA_DIR), 
        #                "common": f("acronym1_11", DATA_DIR)},
        "Qwen3.8-27B": {"rare": f("rot12enc_mediumprob", DATA_DIR2), 
                        "common": f("rot13enc_mediumprob", DATA_DIR2)},
    },
    "Shift Dec": {
        #"gpt-oss-20b": {"rare": f("conversion_actualinverse", DATA_DIR),
        #                "common": f("conversion_actual", DATA_DIR)},
        "Qwen3.8-27B": {"rare": f("rot12dec_mediumprob", DATA_DIR2), 
                        "common": f("rot13dec_mediumprob", DATA_DIR2)},
    },
    "Pig Dec": {
        #"gpt-oss-20b": {"rare": f("conversion_fakeinverse", DATA_DIR),
        #                "common": f("conversion_fake", DATA_DIR)},
        "Qwen3.8-27B": {"rare": f("pigenc_uv_mediumprob", DATA_DIR2), 
                        "common": f("pigenc_ay_mediumprob", DATA_DIR2)},
    },
    "Pig Enc": {
        #"gpt-oss-20b": {"rare": f("conversion_ood_actualinverse", DATA_DIR),
        #                "common": f("conversion_ood_actual", DATA_DIR)},
        "Qwen3.8-27B": {"rare": f("pigdec_uv_mediumprob", DATA_DIR2), 
                        "common": f("pigdec_ay_mediumprob", DATA_DIR2)},
    },
    "Conversion": {
        #"gpt-oss-20b": {"rare": f("conversion_ood_fakeinverse", DATA_DIR),
        #                "common": f("conversion_ood_fake", DATA_DIR)},
        "Qwen3.8-27B": {"rare": f("conversion_ood_actual", DATA_DIR2), 
                        "common": f("conversion_actual", DATA_DIR2)},
    },
    "Acronyms": {
        #"gpt-oss-20b": {"rare": f("sorting_descending", DATA_DIR),
        #                "common": f("sorting_ascending", DATA_DIR)},
        "Qwen3.8-27B": {"rare": f("acronym2_11", DATA_DIR2), 
                        "common": f("acronym1_11", DATA_DIR2)},
    },
    "Sort": {
        #"gpt-oss-20b": {"rare": f("sorting_fwd", DATA_DIR),
        #                "common": f("sorting_rev", DATA_DIR)},
        "Qwen3.8-27B": {"rare": f("sorting_rev", DATA_DIR2), 
                        "common": f("sorting_fwd", DATA_DIR2)},
    },
}
REQUIRED_KEYS = {"prompts", "gts", "res", "accs", "acc", "eds", "ed"}


# Layout, all in inches
PANEL_W, PANEL_H = 2.0, 1.5        # size of one bar panel
WSPACE, HSPACE = 0.12, 0.12        # gaps between panels, as a fraction of panel size
LEFT, BOTTOM = 0.8, 0.75           # room for the y label / tick labels, and rotated x labels
HEADER_H = 0.3                     # column title strip, attached to the top of each panel
LABEL_GAP, LABEL_W = 0.12, 0.32    # gap between the last panel and the model-name box, and box width



# ============================== Loading ==============================
def load_point(path):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    missing = REQUIRED_KEYS - d.keys()
    if missing:
        raise ValueError(f"{path}: missing keys {sorted(missing)}")
    e = np.asarray(d["eds"], dtype=float)
    if not (len(e) == len(d["res"]) == len(d["gts"])):
        raise ValueError(f"{path}: eds/res/gts lengths differ")
    return float(d["ed"]), float(e.std(ddof=1) / math.sqrt(len(e)))



def collect():
    """acc[(column, model, variant)] = (mean edit distance, standard error)."""
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
def strip(fig, rect, text, rotation=0):
    """Grey ggplot-style label box at an absolute figure rectangle [x0, y0, w, h]."""
    s = fig.add_axes(rect)
    s.set_facecolor("#D9D9D9")
    s.set_xticks([]); s.set_yticks([])
    for sp in s.spines.values():
        sp.set_edgecolor("#333333")
    s.text(0.5, 0.5, text, ha="center", va="center", fontsize=9, rotation=rotation)
    return s



def main():
    acc = collect()
    if not acc:
        raise SystemExit("No usable files in COLUMNS.")
    ymax = max(p + se for p, se in acc.values()) or 1.0
    cols = list(COLUMNS)
    models = list(dict.fromkeys(m for c in COLUMNS.values() for m in c))
    color = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(models)}
    nrows, ncols = len(models), len(cols)


    # Figure size from the layout, so every panel is exactly PANEL_W x PANEL_H inches
    right = LABEL_GAP + LABEL_W + 0.1
    top = HEADER_H + 0.1
    grid_w = ncols * PANEL_W * (1 + WSPACE) - WSPACE * PANEL_W
    grid_h = nrows * PANEL_H * (1 + HSPACE) - HSPACE * PANEL_H
    W, H = LEFT + grid_w + right, BOTTOM + grid_h + top
    fig = plt.figure(figsize=(W, H))
    gs = fig.add_gridspec(nrows, ncols, left=LEFT / W, right=1 - right / W,
                          bottom=BOTTOM / H, top=1 - top / H, wspace=WSPACE, hspace=HSPACE)


    ref = None
    for r, m in enumerate(models):
        for c, col in enumerate(cols):
            ax = fig.add_subplot(gs[r, c], sharey=ref)
            ref = ref or ax
            for i, var in enumerate(VARIANTS):
                if (col, m, var) not in acc:
                    print(f"missing: {col} {m} {var}")
                    continue
                p, se = acc[(col, m, var)]
                ax.bar(i, p, width=0.7, color=color[m], edgecolor="black", linewidth=0.8)
                ax.errorbar(i, p, yerr=se, color="black", capsize=3, linewidth=1)
            ax.set_xlim(-0.6, len(VARIANTS) - 0.4)
            ax.set_ylim(0, ymax * 1.05)
            ax.grid(True, axis="y", color="#E5E5E5")
            ax.set_axisbelow(True)
            ax.set_xticks(range(len(VARIANTS)))
            ax.set_xticklabels([v.capitalize() for v in VARIANTS] if r == nrows - 1 else [],
                               rotation=45, ha="right", fontsize=8)
            ax.tick_params(labelsize=8)
            if c > 0:
                ax.tick_params(labelleft=False)
            for sp in ax.spines.values():
                sp.set_edgecolor("#333333")


            pos = ax.get_position()                     # fixed by the grid, so safe to read now
            if r == 0:                                  # column title, touching the top of the panel
                strip(fig, [pos.x0, pos.y1, pos.width, HEADER_H / H], col)
            if c == ncols - 1:                          # model name, with a clear gap to the right
                strip(fig, [pos.x1 + LABEL_GAP / W, pos.y0, LABEL_W / W, pos.height], m, rotation=-90)


    fig.text(0.15 / W, BOTTOM / H + grid_h / H / 2, "Edit distance (mean)", rotation=90, va="center", ha="center", fontsize=10)


    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out = os.path.join(OUTPUT_DIR, f"{OUT_NAME}.png")
    fig.savefig(out, dpi=300)
    print("Saved:", out)



if __name__ == "__main__":
    main()