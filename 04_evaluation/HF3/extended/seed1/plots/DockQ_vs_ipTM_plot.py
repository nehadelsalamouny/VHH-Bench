"""
Plot DockQ versus ipTM for the top-ranked prediction (seed1, rank1) and generate DockQ performance statistics.

Input files:
    ../output/DockQ_seed1_rank1.txt
    ../output/iptm_seed1_rank1.txt

Outputs:
    DockQ_vs_ipTM.pdf
    DockQ_percentages_1seed_toprank.txt
"""

import re
from itertools import cycle

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import pandas as pd

# ==========================================
# Input files
# ==========================================
dockq_file = "../output/DockQ_seed1_rank1.txt"
iptm_file = "../output/iptm_seed1_rank1.txt"

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

df_dockq["DockQ"] = pd.to_numeric(
    df_dockq["DockQ"],
    errors="coerce"
)

df_iptm["iptm"] = pd.to_numeric(
    df_iptm["iptm"],
    errors="coerce"
)

# ==========================================
# Extract PDB IDs
# ==========================================
def extract_pdb(text):

    text = str(text).upper()

    match = re.search(
        r"([0-9][A-Z0-9]{3}(?:_[A-Z]+)?)",
        text
    )

    if match:
        return match.group(1)

    return None


df_dockq["PDB"] = (
    df_dockq["Folder"]
    .apply(extract_pdb)
)

df_iptm["PDB"] = (
    df_iptm["Folder"]
    .apply(extract_pdb)
)

df_dockq = df_dockq.dropna(
    subset=["PDB"]
)

df_iptm = df_iptm.dropna(
    subset=["PDB"]
)

# ==========================================
# Merge DockQ and ipTM
# ==========================================
df_merged = pd.merge(
    df_dockq[["PDB", "DockQ"]],
    df_iptm[["PDB", "iptm"]],
    on="PDB",
    how="inner"
)

print(f"Merged entries: {len(df_merged)}")

# ==========================================
# Marker and color styles
# ==========================================
pdb_list = sorted(
    df_merged["PDB"].unique()
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
    for pdb in pdb_list
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
for pdb in pdb_list:

    subset = df_merged[
        df_merged["PDB"] == pdb
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
        alpha=0.9
    )

# ==========================================
# Legend
# ==========================================
handles = [
    mlines.Line2D(
        [],
        [],
        linestyle="",
        marker=pdb_style[pdb][1],
        color=pdb_style[pdb][0],
        markeredgecolor="black",
        markersize=12,
        label=pdb.upper()
    )
    for pdb in pdb_list
]

plt.legend(
    handles=handles,
    loc="center left",
    bbox_to_anchor=(1, 0.5),
    fontsize=16,
    frameon=True,
    ncol=1
)

# ==========================================
# Region labels
# ==========================================
plt.text(
    0.05,
    0.115,
    "Incorrect",
    rotation=90,
    color="red",
    fontsize=28,
    va="center",
    ha="right"
)

plt.text(
    0.05,
    0.36,
    "Acceptable",
    rotation=90,
    color="orange",
    fontsize=28,
    va="center",
    ha="right"
)

plt.text(
    0.05,
    0.645,
    "Medium",
    rotation=90,
    color="goldenrod",
    fontsize=28,
    va="center",
    ha="right"
)

plt.text(
    0.05,
    0.90,
    "High",
    rotation=90,
    color="green",
    fontsize=28,
    va="center",
    ha="right"
)

plt.text(
    0.30,
    1.01,
    "Failed",
    fontsize=28,
    color="red",
    ha="center"
)

plt.text(
    0.70,
    1.01,
    "Uncertain",
    fontsize=28,
    color="orange",
    ha="center"
)

plt.text(
    0.90,
    1.01,
    "High",
    fontsize=28,
    color="green",
    ha="center"
)

# ==========================================
# Axis formatting
# ==========================================
plt.xlabel(
    "ipTM",
    fontsize=40
)

plt.ylabel(
    "DockQ",
    fontsize=40
)

plt.xlim(0, 1)
plt.ylim(0, 1)

plt.tick_params(
    axis="both",
    labelsize=26
)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
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
# DockQ statistics
# ==========================================
total = len(df_merged)

failed = (
    df_merged["DockQ"] <= 0.23
).sum()

acceptable = (
    (df_merged["DockQ"] > 0.23)
    & (df_merged["DockQ"] <= 0.49)
).sum()

medium = (
    (df_merged["DockQ"] > 0.49)
    & (df_merged["DockQ"] <= 0.80)
).sum()

high = (
    df_merged["DockQ"] > 0.80
).sum()

acceptable_plus = (
    df_merged["DockQ"] > 0.23
).sum()

# ==========================================
# Percentage helper
# ==========================================
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

    f.write("DockQ Rank1 Percentages\n")
    f.write("=======================\n\n")

    f.write(f"Total structures: {total}\n")
    f.write(f"Failed: {failed} ({pct(failed):.1f}%)\n")
    f.write(f"Acceptable: {acceptable} ({pct(acceptable):.1f}%)\n")
    f.write(f"Medium: {medium} ({pct(medium):.1f}%)\n")
    f.write(f"High: {high} ({pct(high):.1f}%)\n")
    f.write(
        f"Acceptable+: "
        f"{acceptable_plus} "
        f"({pct(acceptable_plus):.1f}%)\n"
    )

# ==========================================
# Report
# ==========================================
print("\nDockQ Rank1 Percentages")
print("=======================")
print(f"Total structures: {total}")
print(f"Failed: {failed} ({pct(failed):.1f}%)")
print(f"Acceptable: {acceptable} ({pct(acceptable):.1f}%)")
print(f"Medium: {medium} ({pct(medium):.1f}%)")
print(f"High: {high} ({pct(high):.1f}%)")
print(
    f"Acceptable+: "
    f"{acceptable_plus} ({pct(acceptable_plus):.1f}%)"
)

print(f"\nSaved plot to {figure_file}")
print(f"Saved summary to {summary_file}")