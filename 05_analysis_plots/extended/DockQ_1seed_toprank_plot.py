#!/usr/bin/env python3
"""
Generate violin plots of DockQ score distributions for multiple structure prediction tools using top-ranked models.

Inputs
------
../../04_evaluation/AF3/extended/seed1/plots/DockQ_1seed_toprank.txt
../../04_evaluation/boltz-2/extended/seed1/plots/DockQ_1seed_toprank.txt
../../04_evaluation/chai-1/extended/seed1/plots/DockQ_1seed_toprank.txt
../../04_evaluation/ESMFold2/extended/seed1/plots/DockQ_1seed_toprank.txt
../../04_evaluation/HF3/extended/seed1/plots/DockQ_1seed_toprank.txt
../../04_evaluation/protenix-v2/extended/seed1/plots/DockQ_1seed_toprank.txt

Outputs
-------
DockQ_1seed_toprank_plot.pdf
DockQ_1seed_toprank_plot.txt
"""

import os
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# INPUT
# ==========================================

folders = [
    "../../04_evaluation/AF3/extended/seed1/plots",
    "../../04_evaluation/boltz-2/extended/seed1/plots",
    "../../04_evaluation/chai-1/extended/seed1/plots",
    "../../04_evaluation/ESMFold2/extended/seed1/plots",
    "../../04_evaluation/HF3/extended/seed1/plots",
    "../../04_evaluation/protenix-v2/extended/seed1/plots",
]

tools = [
    "AF3",
    "Boltz-2",
    "Chai-1",
    "ESMFold2",
    "HF3",
    "Protenix-v2",
]

colors = [
    "#1f77b4",  # blue
    "#ff7f0e",  # orange
    "#2ca02c",  # green
    "#d62728",  # red
    "#9467bd",  # purple
    "#8c564b",  # brown
]

# ==========================================
# READ DATA
# ==========================================

all_values = []
means = []
stds = []

for folder in folders:

    file = os.path.join(
        folder,
        "DockQ_1seed_toprank.txt",
    )

    values = np.loadtxt(file)

    all_values.append(values)
    means.append(np.mean(values))
    stds.append(np.std(values))

means = np.array(means)
stds = np.array(stds)

# ==========================================
# VIOLIN PLOT
# ==========================================

fig, ax = plt.subplots(figsize=(16, 12))

parts = ax.violinplot(
    all_values,
    showmeans=False,
    showmedians=False,
    showextrema=False,
)

# Color violins
for body, color in zip(parts["bodies"], colors):
    body.set_facecolor(color)
    body.set_edgecolor("black")
    body.set_alpha(0.75)
    body.set_linewidth(1.2)

# Raw points
for i, values in enumerate(all_values):

    jitter = np.random.normal(
        0,
        0.05,
        len(values),
    )

    ax.scatter(
        np.full(len(values), i + 1) + jitter,
        values,
        color="black",
        s=25,
        alpha=0.35,
        zorder=3,
    )

# Mean marker
for i, mean in enumerate(means):

    ax.scatter(
        i + 1,
        mean,
        marker="D",
        s=100,
        facecolors="none",
        edgecolors="black",
        linewidths=2.5,
        zorder=5,
    )

# Median and IQR
medians = [np.median(v) for v in all_values]
q1 = [np.percentile(v, 25) for v in all_values]
q3 = [np.percentile(v, 75) for v in all_values]

# Median line
for i, median in enumerate(medians):

    ax.hlines(
        median,
        i + 1 - 0.18,
        i + 1 + 0.18,
        colors="black",
        linewidth=3,
        zorder=6,
    )

# IQR error bars
for i, (median, low, high) in enumerate(
    zip(medians, q1, q3)
):

    ax.errorbar(
        i + 1,
        median,
        yerr=[
            [median - low],
            [high - median],
        ],
        fmt="none",
        ecolor="black",
        elinewidth=2,
        capsize=8,
        zorder=5,
    )

# ==========================================
# STYLING
# ==========================================

ax.set_xticks(np.arange(1, len(tools) + 1))

ax.set_xticklabels(
    tools,
    rotation=45,
    fontsize=30,
)

ax.set_ylabel(
    "DockQ",
    fontsize=40,
)

ax.set_ylim(0, 1)

ax.tick_params(
    axis="y",
    labelsize=35,
)

plt.tight_layout()

plt.savefig(
    "DockQ_1seed_toprank_plot.pdf",
    dpi=300,
    bbox_inches="tight",
)

plt.show()

# ==========================================
# SAVE SUMMARY
# ==========================================

with open(
    "DockQ_1seed_toprank_plot.txt",
    "w",
) as f:

    for tool, mean, std in zip(
        tools,
        means,
        stds,
    ):

        line = (
            f"{tool}: "
            f"mean = {mean:.3f}, "
            f"std = {std:.3f}"
        )

        print(line)
        f.write(line + "\n")