#!/usr/bin/env python3
"""
Generate violin plots of CDR3 RMSD distributions for top-ranked models
from multiple structure prediction tools.

Outputs
-------
cdr3_1seed_toprank_plot.pdf
cdr3_1seed_toprank_plot.txt
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------
# SETTINGS
# -----------------------------

np.random.seed(42)

# -----------------------------
# INPUT FILES
# -----------------------------

tool_files = {
    "AF3": "../../04_evaluation/AF3/extended/seed1/cdr3/rank0_cdr3.txt",
    "Boltz-2": "../../04_evaluation/boltz-2/extended/seed1/cdr3/rank0_cdr3.txt",
    "Chai-1": "../../04_evaluation/chai-1/extended/seed1/cdr3/rank0_cdr3.txt",
    "ESMFold2": "../../04_evaluation/ESMFold2/extended/seed1/cdr3/rank0_cdr3.txt",
    "HF3": "../../04_evaluation/HF3/extended/seed1/cdr3/rank0_cdr3.txt",
    "Protenix-v2": "../../04_evaluation/protenix-v2/extended/seed1/cdr3/rank0_cdr3.txt",
}

all_data = []

colors = [
    "#1f77b4",  # blue
    "#ff7f0e",  # orange
    "#2ca02c",  # green
    "#d62728",  # red
    "#9467bd",  # purple
    "#8c564b",  # brown
]

# -----------------------------
# FILTER FUNCTION
# -----------------------------

def filter_top_model(df, tool):

    s = df["structure"].astype(str)

    patterns = {
        "Chai-1": r"model_idx_0",
        "HF3": r"predicted_structure",
        "Protenix-v2": r"sample[_\-]?0",
        "ESMFold2": r"seed0_sample0",
    }

    if tool in patterns:
        return df[
            s.str.contains(
                patterns[tool],
                case=False,
                na=False,
            )
        ]

    return df[
        s.str.contains(
            r"model[_\-]?0",
            case=False,
            na=False,
        )
    ]

# -----------------------------
# LOAD DATA
# -----------------------------

for tool, filepath in tool_files.items():

    print(f"\n=== Processing {tool} ===")

    if not os.path.exists(filepath):
        print("Missing:", filepath)
        continue

    df = pd.read_csv(filepath, sep="\t")

    required_cols = {"structure", "CDR3_RMSD"}

    if not required_cols.issubset(df.columns):
        print("Missing required columns:", filepath)
        continue

    # Keep only top-ranked model
    df = filter_top_model(df, tool)

    # Convert RMSD values
    df["CDR3_RMSD"] = pd.to_numeric(
        df["CDR3_RMSD"],
        errors="coerce",
    )

    df = df.dropna(subset=["CDR3_RMSD"])

    print("Entries after filtering:", len(df))

    for val in df["CDR3_RMSD"]:
        all_data.append(
            {
                "tool": tool,
                "rmsd": val,
            }
        )

# -----------------------------
# BUILD DATAFRAME
# -----------------------------

df_all = pd.DataFrame(all_data)

if df_all.empty:
    print("\nNo data found. Exiting.")
    exit()

print("\nCounts per tool:")
print(df_all["tool"].value_counts())

# -----------------------------
# TOOL ORDER
# -----------------------------

tools_present = [
    tool
    for tool in tool_files.keys()
    if tool in df_all["tool"].unique()
]

# -----------------------------
# COMPUTE STATS
# -----------------------------

stats = (
    df_all.groupby("tool")["rmsd"]
    .agg(
        mean="mean",
        std="std",
        median="median",
    )
    .loc[tools_present]
)

# -----------------------------
# DATA FOR PLOTTING
# -----------------------------

all_values = [
    df_all[df_all["tool"] == tool]["rmsd"].values
    for tool in tools_present
]

means = [np.mean(v) for v in all_values]

medians = [np.median(v) for v in all_values]

q1 = [
    np.percentile(v, 25)
    for v in all_values
]

q3 = [
    np.percentile(v, 75)
    for v in all_values
]

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

# -----------------------------
# COLOR VIOLINS
# -----------------------------

for body, color in zip(
    parts["bodies"],
    colors[: len(parts["bodies"])]
):
    body.set_facecolor(color)
    body.set_edgecolor("black")
    body.set_alpha(0.75)
    body.set_linewidth(1.2)

# -----------------------------
# INDIVIDUAL DATA POINTS
# -----------------------------

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

# -----------------------------
# MEAN MARKER
# -----------------------------

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

# -----------------------------
# MEDIAN LINE
# -----------------------------

for i, median in enumerate(medians):

    ax.hlines(
        median,
        i + 1 - 0.18,
        i + 1 + 0.18,
        colors="black",
        linewidth=3,
        zorder=6,
    )

# -----------------------------
# IQR ERROR BARS
# -----------------------------

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

ax.set_xticks(np.arange(1, len(tools_present) + 1))

ax.set_xticklabels(
    tools_present,
    rotation=45,
    fontsize=30,
)

ax.set_ylabel(
    "CDR3 RMSD (Å)",
    fontsize=40,
)

ax.set_ylim(0, 8)

ax.tick_params(
    axis="y",
    labelsize=35,
)

plt.tight_layout()

plt.savefig(
    "cdr3_1seed_toprank_plot.pdf",
    dpi=300,
    bbox_inches="tight",
)

plt.show()

# -----------------------------
# SAVE STATS
# -----------------------------

with open(
    "cdr3_1seed_toprank_plot.txt",
    "w",
) as f:

    f.write("Tool\tMean\tSD\tMedian\tN\n")

    for tool in tools_present:

        mean_val = stats.loc[tool, "mean"]
        std_val = stats.loc[tool, "std"]
        median_val = stats.loc[tool, "median"]

        n_val = len(
            df_all[
                df_all["tool"] == tool
            ]
        )

        line = (
            f"{tool}\t"
            f"{mean_val:.3f}\t"
            f"{std_val:.3f}\t"
            f"{median_val:.3f}\t"
            f"{n_val}\n"
        )

        f.write(line)

        print(
            f"{tool}: "
            f"mean = {mean_val:.3f}, "
            f"std = {std_val:.3f}, "
            f"median = {median_val:.3f}, "
            f"N = {n_val}"
        )

print(
    "\nStatistics saved to cdr3_1seed_toprank_plot.txt"
)