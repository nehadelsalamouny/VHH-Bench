"""
Plot DockQ versus ipTM for the top-ranked prediction (rank0) from seed101 and generate DockQ
performance statistics.

Input files:
    ../output/DockQ_seed101_rank0.txt
    ../output/iptm_seed101_rank0.txt

Outputs:
    DockQ_vs_ipTM.pdf
    DockQ_percentages_1seed_toprank.txt
"""

import os
from itertools import cycle

import matplotlib.pyplot as plt
import pandas as pd

# ==========================================
# Input files
# ==========================================
dockq_file = "../output/DockQ_seed101_rank0.txt"
iptm_file = "../output/iptm_seed101_rank0.txt"

target_seed = 101

# ==========================================
# Load data
# ==========================================
df_dockq = pd.read_csv(
    dockq_file,
    sep="\t"
)

df_iptm = pd.read_csv(
    iptm_file,
    sep="\t"
)

# ==========================================
# Extract PDB identifiers
# ==========================================
def extract_pdb_from_model(model):

    model = os.path.basename(str(model))

    return model.replace(
        "_sample_0.cif",
        ""
    )


df_dockq["PDB"] = (
    df_dockq["Model"]
    .apply(extract_pdb_from_model)
)

df_dockq["PDB"] = (
    df_dockq["PDB"]
    .astype(str)
)

df_iptm["PDB"] = (
    df_iptm["PDB"]
    .astype(str)
)

# Keep one entry per structure
df_dockq = (
    df_dockq[
        ["PDB", "DockQ"]
    ]
    .drop_duplicates(
        subset=["PDB"]
    )
)

# ==========================================
# Standardize ipTM column name
# ==========================================
if "ipTM" in df_iptm.columns:
    df_iptm = df_iptm.rename(
        columns={"ipTM": "iptm"}
    )

df_dockq["DockQ"] = pd.to_numeric(
    df_dockq["DockQ"],
    errors="coerce"
)

df_iptm["iptm"] = pd.to_numeric(
    df_iptm["iptm"],
    errors="coerce"
)

# ==========================================
# Merge datasets
# ==========================================
df = pd.merge(
    df_dockq[["PDB", "DockQ"]],
    df_iptm[["PDB", "iptm"]],
    on="PDB",
    how="inner"
)

print(
    f"Structures retained: {len(df)}"
)

if len(df) == 0:
    raise ValueError(
        "No matching structures found "
        "between DockQ and ipTM files."
    )

# ==========================================
# Plot styles
# ==========================================
pdb_codes = sorted(
    df["PDB"].unique()
)

colors = [
    "#0097A7", "#7B1FA2", "#43A047",
    "#FF7F50", "#C0CA33", "#8E24AA",
    "#004D40", "#42A5F5", "#0D47A1",
    "#FFC107", "#999999", "#FF5722",
    "#795548", "#607D8B", "#673AB7",
    "#CDDC39", "#00BCD4", "#D81B60",
    "#E53935", "#6D4C41"
]

markers = [
    "o", "^", "s", "D", "v",
    "P", "X", "*", "<", ">",
    "d", "p", "h", "H", "8"
]

style_cycle = zip(
    cycle(colors),
    cycle(markers)
)

pdb_style = {
    pdb: next(style_cycle)
    for pdb in pdb_codes
}

# ==========================================
# Create plot
# ==========================================
plt.figure(figsize=(16, 12))

# DockQ quality regions
plt.axhspan(
    0.80, 1.00,
    color="green",
    alpha=0.10
)

plt.axhspan(
    0.49, 0.80,
    color="yellow",
    alpha=0.10
)

plt.axhspan(
    0.23, 0.49,
    color="orange",
    alpha=0.10
)

plt.axhspan(
    0.00, 0.23,
    color="red",
    alpha=0.10
)

# Threshold lines
plt.axvline(
    0.80,
    color="green",
    linestyle="--",
    linewidth=3
)

plt.axvline(
    0.60,
    color="orange",
    linestyle="--",
    linewidth=3
)

plt.axhline(
    0.80,
    color="green",
    linestyle="--",
    linewidth=3
)

plt.axhline(
    0.49,
    color="orange",
    linestyle="--",
    linewidth=3
)

plt.axhline(
    0.23,
    color="red",
    linestyle="--",
    linewidth=3
)

# ==========================================
# Scatter plot
# ==========================================
for pdb in pdb_codes:

    subset = df[
        df["PDB"] == pdb
    ]

    color, marker = pdb_style[pdb]

    plt.scatter(
        subset["iptm"],
        subset["DockQ"],
        s=300,
        color=color,
        marker=marker,
        edgecolor="black",
        linewidth=1,
        alpha=0.9,
        label=pdb.upper()
    )

# ==========================================
# Region labels
# ==========================================
plt.text(
    0.05, 0.115,
    "Incorrect",
    rotation=90,
    fontsize=30,
    color="red",
    va="center",
    ha="right"
)

plt.text(
    0.05, 0.36,
    "Acceptable",
    rotation=90,
    fontsize=30,
    color="orange",
    va="center",
    ha="right"
)

plt.text(
    0.05, 0.645,
    "Medium",
    rotation=90,
    fontsize=30,
    color="goldenrod",
    va="center",
    ha="right"
)

plt.text(
    0.05, 0.90,
    "High",
    rotation=90,
    fontsize=30,
    color="green",
    va="center",
    ha="right"
)

plt.text(
    0.30,
    1.01,
    "Failed",
    fontsize=30,
    color="red"
)

plt.text(
    0.70,
    1.01,
    "Uncertain",
    fontsize=30,
    color="orange"
)

plt.text(
    0.90,
    1.01,
    "High",
    fontsize=30,
    color="green"
)

# ==========================================
# Axis formatting
# ==========================================
plt.xlabel(
    "ipTM",
    fontsize=44
)

plt.ylabel(
    "DockQ",
    fontsize=44
)

plt.xlim(0, 1)
plt.ylim(0, 1)

plt.tick_params(
    axis="both",
    labelsize=24
)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

plt.legend(
    loc="center left",
    bbox_to_anchor=(1, 0.5),
    fontsize=16,
    frameon=True,
    ncol=1
)

plt.tight_layout()

# ==========================================
# Save figure
# ==========================================
figure_file = "DockQ_vs_ipTM.pdf"

plt.savefig(
    figure_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================
# Calculate statistics
# ==========================================
total = len(df)

failed = (
    df["DockQ"] <= 0.23
).sum()

acceptable = (
    (df["DockQ"] > 0.23)
    & (df["DockQ"] <= 0.49)
).sum()

medium = (
    (df["DockQ"] > 0.49)
    & (df["DockQ"] <= 0.80)
).sum()

high = (
    df["DockQ"] > 0.80
).sum()

acceptable_plus = (
    df["DockQ"] > 0.23
).sum()

def pct(count):
    return (
        100 * count / total
        if total > 0
        else 0
    )

# ==========================================
# Save summary
# ==========================================
summary_file = "DockQ_percentages_1seed_toprank.txt"

with open(summary_file, "w") as f:

    f.write("DockQ Benchmark Summary\n")
    f.write("=======================\n")
    f.write(f"Seed: {target_seed}\n")
    f.write(f"Total structures: {total}\n")

    f.write(
        f"Failed (<=0.23): "
        f"{failed} ({pct(failed):.1f}%)\n"
    )

    f.write(
        f"Acceptable (0.23-0.49): "
        f"{acceptable} ({pct(acceptable):.1f}%)\n"
    )

    f.write(
        f"Medium (0.49-0.80): "
        f"{medium} ({pct(medium):.1f}%)\n"
    )

    f.write(
        f"High (>0.80): "
        f"{high} ({pct(high):.1f}%)\n"
    )

    f.write(
        f"Acceptable+ (>0.23): "
        f"{acceptable_plus} "
        f"({pct(acceptable_plus):.1f}%)\n"
    )

# ==========================================
# Report
# ==========================================
print("\nDockQ Benchmark Summary")
print("=======================")
print(f"Seed: {target_seed}")
print(f"Total structures: {total}")
print(f"Failed: {failed} ({pct(failed):.1f}%)")
print(f"Acceptable: {acceptable} ({pct(acceptable):.1f}%)")
print(f"Medium: {medium} ({pct(medium):.1f}%)")
print(f"High: {high} ({pct(high):.1f}%)")
print(
    f"Acceptable+: "
    f"{acceptable_plus} "
    f"({pct(acceptable_plus):.1f}%)"
)

print(f"\nSaved plot to {figure_file}")
print(f"Saved summary to {summary_file}")
