#!/usr/bin/env python3
"""
Correlation between CDR3 RMSD and DockQ score.

Inputs
------
../output/DockQ_seed101_rank0.txt
rank0_cdr3.txt

Outputs
-------
cdr3_rmsdvsDockQ.pdf
cdr3_rmsdvsDockQ.csv
cdr3_rmsdvsDockQ.txt
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from matplotlib.lines import Line2D

# ==========================================
# Figure style
# ==========================================

plt.rcParams["font.family"] = "Arial"
plt.rcParams["axes.linewidth"] = 1.5
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

# ==========================================
# Read DockQ file
# ==========================================

dockq = pd.read_csv(
    "../output/DockQ_seed101_rank0.txt",
    sep=r"\s+",
    engine="python"
)

# Examples:
# 7Q3R_F_sample_0.cif -> 7Q3R_F
# 8DAM_B_sample_0.cif -> 8DAM_B
# 8DAM_C_sample_0.cif -> 8DAM_C
# 7T5F_sample_0.cif   -> 7T5F

dockq["fold"] = dockq["Model"].str.replace(
    r"_sample_0\.cif$",
    "",
    regex=True
)

# ==========================================
# Read CDR3 RMSD file
# ==========================================

cdr3 = pd.read_csv(
    "rank0_cdr3.txt",
    sep="\t"
)

cdr3 = cdr3.rename(
    columns={"folder": "fold"}
)

# ==========================================
# Fix IDs where RMSD file omits chain IDs
# ==========================================

cdr3["fold"] = cdr3["fold"].replace({
    "7Q3R": "7Q3R_F",
    "7R1Z": "7R1Z_E"
})

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
# Merge datasets
# ==========================================

df = pd.merge(
    dockq[["fold", "DockQ"]],
    cdr3,
    on="fold",
    how="inner"
)


# ==========================================
# Correlation
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
# Linear fit
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
# Plot
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
# Labels
# ==========================================

ax.set_xlabel(
    "CDR3 RMSD (Å)",
    fontsize=18
)

ax.set_ylabel(
    "DockQ",
    fontsize=18
)

ax.tick_params(
    axis="both",
    which="major",
    labelsize=16,
    width=1.5,
    length=6
)

# ==========================================
# Legend
# ==========================================

legend_text = f"Pearson r = {pearson_r:.2f}"

dummy = Line2D([], [], linestyle="none")

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
    handletextpad=0,
)

# ==========================================
# Axes styling
# ==========================================

for spine in ax.spines.values():
    spine.set_linewidth(1.5)

ax.set_xlim(0, 5)
ax.set_ylim(0, 1)

plt.tight_layout()

plt.savefig(
    "cdr3_rmsdvsDockQ.pdf",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================
# Save merged data
# ==========================================

df.to_csv(
    "cdr3_rmsdvsDockQ.csv",
    index=False
)

# ==========================================
# Save statistics
# ==========================================

with open("cdr3_rmsdvsDockQ.txt", "w") as f:
    f.write(f"Matched structures\t{len(df)}\n")
    f.write(f"Pearson r\t{pearson_r:.4f}\n")
    f.write(f"Pearson p\t{pearson_p:.4e}\n")

print(
    "\nSaved:"
    "\n - cdr3_rmsdvsDockQ.pdf"
    "\n - cdr3_rmsdvsDockQ.csv"
    "\n - cdr3_rmsdvsDockQ.txt"
)