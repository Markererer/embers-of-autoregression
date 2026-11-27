import json
import math
import os
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = "viz_data/logs_gpt-oss-20B"
DATA_DIR2 = "viz_data/logs_qwen3.8-27B"
OUTPUT_DIR = "graphs"
OUT_NAME = "bars_graphs"
SUFFIX = "n=1.json"
VARIANTS = ["rare", "common"]
PALETTE = ["#C77CFF", "#F72811", "#F8766D", "#B79F00", "#00BA38", "#00A9FF"]  # #C77CFF Qwen Color / #F72811 gpt Color


def f(prefix, data_dir):
    return os.path.join(data_dir, f"{prefix}_{SUFFIX}")



COLUMNS = {
    "Shift Dec": {
        #"gpt-oss-20b": {"rare": f("conversion_actualinverse", DATA_DIR),
        #                "common": f("conversion_actual", DATA_DIR)},
        "Qwen3.8-27B": {"rare": f("rot12dec_mediumprob", DATA_DIR2), 
                        "common": f("rot13dec_mediumprob", DATA_DIR2)},
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

PANEL_W, PANEL_H = 2.0, 1.5        
WSPACE, HSPACE = 0.12, 0.12        
LEFT, BOTTOM = 0.8, 0.75           
HEADER_H = 0.3                     
LABEL_GAP, LABEL_W = 0.12, 0.32    

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
    cols = list(COLUMNS)
    models = list(dict.fromkeys(m for c in COLUMNS.values() for m in c))
    color = {m: PALETTE[i % len(PALETTE)] for i, m in enumerate(models)}
    nrows, ncols = len(models), len(cols)

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
            ax.set_ylim(0, 1.05)
            ax.set_yticks([0, 0.5, 1.0])
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

            pos = ax.get_position()                     
            if r == 0:                                 
                strip(fig, [pos.x0, pos.y1, pos.width, HEADER_H / H], col)
            if c == ncols - 1:                         
                strip(fig, [pos.x1 + LABEL_GAP / W, pos.y0, LABEL_W / W, pos.height], m, rotation=-90)

    fig.text(0.15 / W, BOTTOM / H + grid_h / H / 2, "Accuracy", rotation=90, va="center", ha="center", fontsize=10)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out = os.path.join(OUTPUT_DIR, f"{OUT_NAME}.png")
    fig.savefig(out, dpi=300)
    print("Saved:", out)


if __name__ == "__main__":
    main()