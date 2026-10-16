#!/usr/bin/env python3

"""
Assess the relationship between CDR3 length and prediction quality.

Inputs:
    - DockQ_rank0.txt
    - CDR3_length.txt

Outputs:
    - CDR3_length_vs_DockQ.pdf
    - CDR3_length_vs_DockQ.csv
    - CDR3_length_vs_DockQ.txt
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from matplotlib.lines import Line2D

# ==========================================
# FIGURE SETTINGS
# ==========================================

plt.rcParams["font.family"] = "Arial"
plt.rcParams["axes.linewidth"] = 1.5
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# ==========================================
# INPUT FILES
# ==========================================

dockq_file = "../output/DockQ_rank0.txt"
cdr3_file = "CDR3_length.txt"

# ==========================================
# LOAD DockQ DATA
# ==========================================

dockq = pd.read_csv(
    dockq_file,
    sep=r"\s+",
    engine="python"
)

dockq["fold"] = (
    dockq["Model"]
    .str.extract(r"^([0-9A-Za-z]{4})")[0]
    .str.upper()
)

numeric_cols = [
    "DockQ",
    "iRMSD",
    "LRMSD",
    "fnat",
    "fnonnat"
]

for col in numeric_cols:
    dockq[col] = pd.to_numeric(
        dockq[col],
        errors="coerce"
    )

dockq = dockq.dropna(
    subset=["fold", "DockQ"]
)

# ==========================================
# LOAD CDR3 LENGTH DATA
# ==========================================

cdr3 = pd.read_csv(
    cdr3_file,
    sep=r"\s+",
    header=None,
    names=[
        "fold",
        "chain",
        "CDR3_length"
    ],
    engine="python"
)

cdr3["fold"] = (
    cdr3["fold"]
    .str.upper()
)

cdr3["CDR3_length"] = pd.to_numeric(
    cdr3["CDR3_length"],
    errors="coerce"
)

cdr3 = cdr3.dropna(
    subset=["CDR3_length"]
)

cdr3 = cdr3[
    ["fold", "CDR3_length"]
]

# ==========================================
# DEBUG INFORMATION
# ==========================================

print("\nDockQ PDBs:")
print(
    sorted(
        dockq["fold"].unique()
    )
)

print("\nCDR3 PDBs:")
print(
    sorted(
        cdr3["fold"].unique()
    )
)

# ==========================================
# MERGE DATASETS
# ==========================================

df = pd.merge(
    dockq[
        [
            "fold",
            "DockQ",
            "iRMSD",
            "LRMSD",
            "fnat",
            "fnonnat"
        ]
    ],
    cdr3,
    on="fold",
    how="inner"
)

print("\nMerged data:")
print(
    df.sort_values("fold")
)

print(
    f"\nMatched structures: {len(df)}"
)

# ==========================================
# SELECT METRIC
# ==========================================

metric = "DockQ"

# Alternative options:
# metric = "iRMSD"
# metric = "LRMSD"
# metric = "fnat"
# metric = "fnonnat"

# ==========================================
# CORRELATION ANALYSIS
# ==========================================

pearson_r, pearson_p = pearsonr(
    df["CDR3_length"],
    df[metric]
)

print(
    f"\nPearson r = {pearson_r:.4f}"
)

print(
    f"Pearson p = {pearson_p:.4e}"
)

# ==========================================
# GENERATE PLOT
# ==========================================

fig, ax = plt.subplots(
    figsize=(7, 6)
)

ax.scatter(
    df["CDR3_length"],
    df[metric],
    s=90,
    color="#4C78A8",
    edgecolors="black",
    linewidth=0.8,
    alpha=0.85
)

# ==========================================
# REGRESSION LINE
# ==========================================

z = np.polyfit(
    df["CDR3_length"],
    df[metric],
    1
)

p = np.poly1d(z)

xline = np.linspace(
    df["CDR3_length"].min(),
    df["CDR3_length"].max(),
    200
)

ax.plot(
    xline,
    p(xline),
    color="black",
    linewidth=2.5
)

# ==========================================
# AXIS LABELS
# ==========================================

ax.set_xlabel(
    "CDR3 length (residues)",
    fontsize=18
)

ax.set_ylabel(
    metric,
    fontsize=18
)

# ==========================================
# TICK FORMATTING
# ==========================================

ax.tick_params(
    axis="both",
    which="major",
    labelsize=16,
    width=1.5,
    length=6
)

# ==========================================
# CORRELATION LEGEND
# ==========================================

legend_text = (
    f"Pearson r = {pearson_r:.2f}"
)

dummy = Line2D(
    [],
    [],
    linestyle="none"
)

ax.legend(
    [dummy],
    [legend_text],
    loc="upper right",
    frameon=True,
    facecolor="white",
    edgecolor="black",
    framealpha=1,
    fontsize=14,
    handlelength=0,
    handletextpad=0
)

# ==========================================
# FRAME THICKNESS
# ==========================================

for spine in ax.spines.values():
    spine.set_linewidth(1.5)

if metric == "DockQ":
    ax.set_ylim(0, 1)

plt.tight_layout()

# ==========================================
# SAVE FIGURE
# ==========================================

plt.savefig(
    f"CDR3_length_vs_{metric}.pdf",
    dpi=300,
    bbox_inches="tight"
)

# ==========================================
# SAVE MERGED DATA
# ==========================================

df.to_csv(
    f"CDR3_length_vs_{metric}.csv",
    index=False
)

# ==========================================
# SAVE STATISTICS
# ==========================================

with open(
    f"CDR3_length_vs_{metric}.txt",
    "w"
) as f:

    f.write(
        f"Matched structures\t{len(df)}\n"
    )

    f.write(
        f"Pearson r\t{pearson_r:.4f}\n"
    )

    f.write(
        f"Pearson p\t{pearson_p:.4e}\n"
    )

# ==========================================
# SUMMARY
# ==========================================

print(
    f"\nSaved:"
    f"\n - CDR3_length_vs_{metric}.pdf"
    f"\n - CDR3_length_vs_{metric}.csv"
    f"\n - CDR3_length_vs_{metric}.txt"
)

plt.show()