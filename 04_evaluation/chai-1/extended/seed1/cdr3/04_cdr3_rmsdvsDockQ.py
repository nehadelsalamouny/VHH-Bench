#!/usr/bin/env python3

"""
Assess the relationship between CDR3 RMSD and DockQ scores.

Inputs:
    - DockQ_rank0.txt
    - rank0_cdr3.txt

Outputs:
    - cdr3_rmsdvsDockQ.pdf
    - cdr3_rmsdvsDockQ.csv
    - cdr3_rmsdvsDockQ.txt
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
cdr3_file = "rank0_cdr3.txt"

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
    .str.extract(r"^([^/]+)")[0]
)

dockq["DockQ"] = pd.to_numeric(
    dockq["DockQ"],
    errors="coerce"
)

# ==========================================
# LOAD CDR3 RMSD DATA
# ==========================================

cdr3 = pd.read_csv(
    cdr3_file,
    sep="\t"
)

cdr3 = cdr3.rename(
    columns={"folder": "fold"}
)

cdr3["CDR3_RMSD"] = pd.to_numeric(
    cdr3["CDR3_RMSD"],
    errors="coerce"
)

cdr3 = cdr3.dropna(
    subset=["CDR3_RMSD"]
)

cdr3 = cdr3[
    ["fold", "CDR3_RMSD"]
]

# ==========================================
# MERGE DATASETS
# ==========================================

df = pd.merge(
    dockq[["fold", "DockQ"]],
    cdr3,
    on="fold",
    how="inner"
)

print(
    f"\nMatched structures: {len(df)}"
)

print(df.head())

# ==========================================
# CORRELATION ANALYSIS
# ==========================================

pearson_r, pearson_p = pearsonr(
    df["CDR3_RMSD"],
    df["DockQ"]
)

print(
    f"Pearson r = {pearson_r:.3f} "
    f"(p = {pearson_p:.3e})"
)

# ==========================================
# LINEAR REGRESSION
# ==========================================

z = np.polyfit(
    df["CDR3_RMSD"],
    df["DockQ"],
    1
)

fit = np.poly1d(z)

xfit = np.linspace(
    df["CDR3_RMSD"].min(),
    df["CDR3_RMSD"].max(),
    200
)

# ==========================================
# PLOT
# ==========================================

fig, ax = plt.subplots(
    figsize=(7, 6)
)

ax.scatter(
    df["CDR3_RMSD"],
    df["DockQ"],
    s=90,
    color="#4C78A8",
    edgecolors="black",
    linewidth=0.8,
    alpha=0.85
)

ax.plot(
    xfit,
    fit(xfit),
    color="black",
    linewidth=2.5
)

# ==========================================
# AXIS LABELS
# ==========================================

ax.set_xlabel(
    "CDR3 RMSD (Å)",
    fontsize=18
)

ax.set_ylabel(
    "DockQ",
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
# AXIS STYLING
# ==========================================

for spine in ax.spines.values():
    spine.set_linewidth(1.5)

ax.set_xlim(0, 5)
ax.set_ylim(0, 1)

plt.tight_layout()

# ==========================================
# SAVE FIGURE
# ==========================================

plt.savefig(
    "cdr3_rmsdvsDockQ.pdf",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================
# SAVE MERGED DATA
# ==========================================

df.to_csv(
    "cdr3_rmsdvsDockQ.csv",
    index=False
)

# ==========================================
# SAVE STATISTICS
# ==========================================

with open(
    "cdr3_rmsdvsDockQ.txt",
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
    "\nSaved:"
    "\n - cdr3_rmsdvsDockQ.pdf"
    "\n - cdr3_rmsdvsDockQ.csv"
    "\n - cdr3_rmsdvsDockQ.txt"
)