"""
Assess the relationship between CDR3 length and DockQ.

Input files:
    ../output/DockQ_seed0_rank0.txt
    CDR3_length.txt

Outputs:
    CDR3_length_vs_<metric>.pdf
    CDR3_length_vs_<metric>.csv
    CDR3_length_vs_<metric>.txt
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
# Load DockQ results
# ==========================================
dockq = pd.read_csv(
    "../output/DockQ_seed0_rank0.txt",
    sep=r"\s+",
    engine="python"
)

dockq["fold"] = (
    dockq["PDB"]
    .str.upper()
    .str.replace(r"_.*$", "", regex=True)
)

# ==========================================
# Convert numeric columns
# ==========================================
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
# Load CDR3 lengths
# ==========================================
cdr3 = pd.read_csv(
    "CDR3_length.txt",
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
# Merge datasets
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

print(f"Matched structures: {len(df)}")

# ==========================================
# Select metric
# ==========================================
metric = "DockQ"

# Alternative metrics:
# metric = "iRMSD"
# metric = "LRMSD"
# metric = "fnat"
# metric = "fnonnat"

# ==========================================
# Correlation analysis
# ==========================================
pearson_r, pearson_p = pearsonr(
    df["CDR3_length"],
    df[metric]
)

print(f"Pearson r = {pearson_r:.4f}")
print(f"Pearson p = {pearson_p:.4e}")

# ==========================================
# Create plot
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
# Regression line
# ==========================================
z = np.polyfit(
    df["CDR3_length"],
    df[metric],
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

# ==========================================
# Axis labels
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
# Frame styling
# ==========================================
for spine in ax.spines.values():
    spine.set_linewidth(1.5)

if metric == "DockQ":
    ax.set_ylim(0, 1)

plt.tight_layout()

# ==========================================
# Save figure
# ==========================================
figure_file = f"CDR3_length_vs_{metric}.pdf"

plt.savefig(
    figure_file,
    dpi=300,
    bbox_inches="tight"
)

# ==========================================
# Save merged data
# ==========================================
data_file = f"CDR3_length_vs_{metric}.csv"

df.to_csv(
    data_file,
    index=False
)

# ==========================================
# Save statistics
# ==========================================
stats_file = f"CDR3_length_vs_{metric}.txt"

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