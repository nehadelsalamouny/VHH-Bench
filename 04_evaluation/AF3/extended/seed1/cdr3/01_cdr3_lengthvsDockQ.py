"""
Analyse the relationship between CDR3 length and DockQ score.

Inputs:
    ../output/DockQ_rank0.txt
    CDR3_length.txt

Outputs:
    CDR3_length_vs_DockQ.pdf
    CDR3_length_vs_DockQ.csv
    CDR3_length_vs_DockQ.txt
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.stats import pearsonr

# ==========================================
# Figure style
# ==========================================

plt.rcParams["font.family"] = "Arial"
plt.rcParams["axes.linewidth"] = 1.5
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

DEBUG = False

# ==========================================
# Load DockQ data
# ==========================================

dockq = pd.read_csv(
    "../output/DockQ_rank0.txt",
    sep=r"\s+",
    engine="python"
)

dockq["fold"] = (
    dockq["Model"]
    .str.extract(r"_([0-9a-z]{4})_model")[0]
    .str.upper()
)

dockq["DockQ"] = pd.to_numeric(
    dockq["DockQ"],
    errors="coerce"
)

# ==========================================
# Load CDR3 lengths
# ==========================================

cdr3 = pd.read_csv(
    "CDR3_length.txt",
    sep=r"\s+",
    header=None,
    names=["fold", "chain", "CDR3_length"],
    engine="python"
)

cdr3["fold"] = cdr3["fold"].str.upper()

cdr3["CDR3_length"] = pd.to_numeric(
    cdr3["CDR3_length"],
    errors="coerce"
)

cdr3 = (
    cdr3
    .dropna(subset=["CDR3_length"])
    [["fold", "CDR3_length"]]
)

# ==========================================
# Merge datasets
# ==========================================

df = pd.merge(
    dockq[["fold", "DockQ"]],
    cdr3,
    on="fold",
    how="inner"
)

if len(df) == 0:
    raise ValueError("No matching structures found.")

if DEBUG:
    print("\nDockQ PDBs:")
    print(sorted(dockq["fold"].dropna().unique()))

    print("\nCDR3 PDBs:")
    print(sorted(cdr3["fold"].unique()))

    print("\nMerged data:")
    print(df.sort_values("fold"))

print(f"\nMatched structures: {len(df)}")

# ==========================================
# Correlation analysis
# ==========================================

pearson_r, pearson_p = pearsonr(
    df["CDR3_length"],
    df["DockQ"]
)

print(f"Pearson r = {pearson_r:.4f}")
print(f"Pearson p = {pearson_p:.4e}")

# ==========================================
# Plot
# ==========================================

fig, ax = plt.subplots(figsize=(7, 6))

ax.scatter(
    df["CDR3_length"],
    df["DockQ"],
    s=90,
    color="#4C78A8",
    edgecolors="black",
    linewidth=0.8,
    alpha=0.85
)

# Regression line
z = np.polyfit(
    df["CDR3_length"],
    df["DockQ"],
    1
)

regression = np.poly1d(z)

xline = np.linspace(
    df["CDR3_length"].min(),
    df["CDR3_length"].max(),
    200
)

ax.plot(
    xline,
    regression(xline),
    color="black",
    linewidth=2.5
)

# Labels
ax.set_xlabel(
    "CDR3 length (residues)",
    fontsize=18
)

ax.set_ylabel(
    "DockQ",
    fontsize=18
)

# Axes formatting
ax.tick_params(
    axis="both",
    which="major",
    labelsize=16,
    width=1.5,
    length=6
)

for spine in ax.spines.values():
    spine.set_linewidth(1.5)

ax.set_ylim(0, 1)

# Legend
legend_text = f"Pearson r = {pearson_r:.2f}"

ax.legend(
    [Line2D([], [], linestyle="none")],
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

plt.tight_layout()

# ==========================================
# Save outputs
# ==========================================

plt.savefig(
    "CDR3_length_vs_DockQ.pdf",
    dpi=300,
    bbox_inches="tight"
)

df.to_csv(
    "CDR3_length_vs_DockQ.csv",
    index=False
)

with open(
    "CDR3_length_vs_DockQ.txt",
    "w"
) as f:

    f.write(f"Matched structures\t{len(df)}\n")
    f.write(f"Pearson r\t{pearson_r:.4f}\n")
    f.write(f"Pearson p\t{pearson_p:.4e}\n")

print(
    "\nSaved:"
    "\n - CDR3_length_vs_DockQ.pdf"
    "\n - CDR3_length_vs_DockQ.csv"
    "\n - CDR3_length_vs_DockQ.txt"
)

plt.show()