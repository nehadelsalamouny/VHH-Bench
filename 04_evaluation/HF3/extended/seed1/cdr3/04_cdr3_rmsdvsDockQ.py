"""
Assess the relationship between CDR3 RMSD and DockQ for HF3 top-ranked predictions (seed1, rank1).

Input files:
    ../output/DockQ_seed1_rank1.txt
    rank0_cdr3.txt

Outputs:
    cdr3_rmsdvsDockQ.pdf
    cdr3_rmsdvsDockQ.csv
    cdr3_rmsdvsDockQ.txt
"""

import numpy as np
import pandas as pd
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
# Load DockQ data
# ==========================================
dockq = pd.read_csv(
    "../output/DockQ_seed1_rank1.txt",
    sep=r"\s+",
    engine="python"
)

# Extract fold identifier from paths such as:
# 7Q3R/7Q3R/7Q3R-pred-1-1
dockq["fold"] = (
    dockq.iloc[:, 0]
    .astype(str)
    .str.extract(
        r"([^/]+-pred-1-1)$"
    )[0]
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
    dockq[["fold", "DockQ"]],
    cdr3,
    on="fold",
    how="inner"
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
    f"Pearson r = {pearson_r:.3f} "
    f"(p = {pearson_p:.3e})"
)

# ==========================================
# Linear regression
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
# Create plot
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
# Axis labels
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
# Tick formatting
# ==========================================
ax.tick_params(
    axis="both",
    which="major",
    labelsize=16,
    width=1.5,
    length=6
)

# ==========================================
# Correlation legend
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
# Axis styling
# ==========================================
for spine in ax.spines.values():
    spine.set_linewidth(1.5)

ax.set_xlim(0, 5)
ax.set_ylim(0, 1)

plt.tight_layout()

# ==========================================
# Save figure
# ==========================================
figure_file = "cdr3_rmsdvsDockQ.pdf"

plt.savefig(
    figure_file,
    dpi=300,
    bbox_inches="tight"
)

# ==========================================
# Save merged data
# ==========================================
data_file = "cdr3_rmsdvsDockQ.csv"

df.to_csv(
    data_file,
    index=False
)

# ==========================================
# Save statistics
# ==========================================
stats_file = "cdr3_rmsdvsDockQ.txt"

with open(stats_file, "w") as f:

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
# Report
# ==========================================
print(
    f"\nSaved:"
    f"\n - {figure_file}"
    f"\n - {data_file}"
    f"\n - {stats_file}"
)

plt.show()