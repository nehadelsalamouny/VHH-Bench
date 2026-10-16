"""
Assess the relationship between CDR3 RMSD and DockQ score for top-ranked predictions using Pearson correlation analysis.

Inputs:
    ../output/DockQ_rank0.txt
    rank0_cdr3.txt

Outputs:
    cdr3_rmsdvsDockQ.pdf
    cdr3_rmsdvsDockQ.csv
    cdr3_rmsdvsDockQ.txt
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
    .str.extract(
        r"^(boltz_results_[^/]+)"
    )
)

dockq["DockQ"] = pd.to_numeric(
    dockq["DockQ"],
    errors="coerce"
)

dockq = dockq.dropna(
    subset=["fold", "DockQ"]
)

# ==========================================
# Load CDR3 RMSD data
# ==========================================

cdr3 = pd.read_csv(
    "rank0_cdr3.txt",
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
# Merge datasets
# ==========================================

df = pd.merge(
    dockq[
        ["fold", "DockQ"]
    ],
    cdr3,
    on="fold",
    how="inner"
)

if len(df) == 0:
    raise ValueError(
        "No matching structures found."
    )

print(
    f"Matched structures: {len(df)}"
)

# ==========================================
# Correlation analysis
# ==========================================

pearson_r, pearson_p = pearsonr(
    df["CDR3_RMSD"],
    df["DockQ"]
)

print(
    f"Pearson r = {pearson_r:.4f}"
)

print(
    f"Pearson p = {pearson_p:.4e}"
)

# ==========================================
# Linear regression
# ==========================================

coefficients = np.polyfit(
    df["CDR3_RMSD"],
    df["DockQ"],
    1
)

regression = np.poly1d(
    coefficients
)

x_line = np.linspace(
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
    x_line,
    regression(x_line),
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

# ==========================================
# Ticks
# ==========================================

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
# Axes styling
# ==========================================

for spine in ax.spines.values():
    spine.set_linewidth(1.5)

ax.set_xlim(0, 5.5)
ax.set_ylim(0, 1)

plt.tight_layout()

# ==========================================
# Save figure
# ==========================================

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
# Summary
# ==========================================

print(
    "\nSaved:"
    "\n - cdr3_rmsdvsDockQ.pdf"
    "\n - cdr3_rmsdvsDockQ.csv"
    "\n - cdr3_rmsdvsDockQ.txt"
)