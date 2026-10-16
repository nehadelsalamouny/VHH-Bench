#!/usr/bin/env python3

"""
Visualize the relationship between DockQ and ipTM scores for top-ranked predictions.

statistics.

Inputs:
    - DockQ_rank0.txt
    - iptm_rank0.txt

Outputs:
    - DockQ_vs_ipTM.pdf
    - DockQ_percentages_1seed_toprank.txt
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from itertools import cycle

# ==========================================
# INPUT FILES
# ==========================================

dockq_file = "../output/DockQ_rank0.txt"
iptm_file = "../output/iptm_rank0.txt"

# ==========================================
# LOAD DATA
# ==========================================

df_dockq = pd.read_csv(
    dockq_file,
    sep="\t"
)

df_iptm = pd.read_csv(
    iptm_file,
    sep="\t"
)

df_dockq.columns = df_dockq.columns.str.strip()
df_iptm.columns = df_iptm.columns.str.strip()

# ==========================================
# EXTRACT PDB CODES
# ==========================================

def get_pdb_from_dockq(model):
    return str(model).split("//")[0]

df_dockq["PDB_code"] = (
    df_dockq["Model"]
    .apply(get_pdb_from_dockq)
)

df_iptm["PDB_code"] = (
    df_iptm["Model_Folder"]
    .astype(str)
    .str.split("/")
    .str[-1]
)

print("\nDockQ PDB codes:")
print(df_dockq["PDB_code"].head())

print("\nipTM PDB codes:")
print(df_iptm["PDB_code"].head())

# ==========================================
# MERGE DockQ AND ipTM
# ==========================================

df = pd.merge(
    df_dockq[["PDB_code", "DockQ"]],
    df_iptm[["PDB_code", "iptm"]],
    on="PDB_code",
    how="inner"
)

print(f"\nMerged structures: {len(df)}")

if len(df) == 0:
    raise ValueError(
        "No structures matched between "
        "DockQ_rank0.txt and iptm_rank0.txt"
    )

# ==========================================
# PLOT SETTINGS
# ==========================================

pdb_codes = sorted(
    df["PDB_code"].unique()
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
# GENERATE PLOT
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

# Scatter points

for pdb in pdb_codes:

    subset = df[
        df["PDB_code"] == pdb
    ]

    color, marker = pdb_style[pdb]

    plt.scatter(
        subset["iptm"],
        subset["DockQ"],
        s=300,
        marker=marker,
        color=color,
        edgecolor="black",
        alpha=0.9
    )

# ==========================================
# REGION LABELS
# ==========================================

plt.text(
    0.05, 0.115,
    "Incorrect",
    va="center",
    ha="right",
    fontsize=30,
    color="red",
    rotation=90
)

plt.text(
    0.05, 0.36,
    "Acceptable",
    va="center",
    ha="right",
    fontsize=30,
    color="orange",
    rotation=90
)

plt.text(
    0.05, 0.645,
    "Medium",
    va="center",
    ha="right",
    fontsize=30,
    color="goldenrod",
    rotation=90
)

plt.text(
    0.05, 0.90,
    "High",
    va="center",
    ha="right",
    fontsize=30,
    color="green",
    rotation=90
)

plt.text(
    0.30, 1.01,
    "Failed",
    ha="center",
    va="bottom",
    fontsize=30,
    color="red"
)

plt.text(
    0.70, 1.01,
    "Uncertain",
    ha="center",
    va="bottom",
    fontsize=30,
    color="orange"
)

plt.text(
    0.90, 1.01,
    "High",
    ha="center",
    va="bottom",
    fontsize=30,
    color="green"
)

# ==========================================
# AXIS FORMATTING
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

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

# ==========================================
# LEGEND
# ==========================================

handles = [
    mlines.Line2D(
        [],
        [],
        linestyle="",
        marker=pdb_style[pdb][1],
        color=pdb_style[pdb][0],
        markeredgecolor="black",
        markersize=10,
        label=pdb.upper()
    )
    for pdb in pdb_codes
]

plt.legend(
    handles=handles,
    loc="center left",
    bbox_to_anchor=(1, 0.5),
    fontsize=16,
    markerscale=1.5,
    ncol=1,
    frameon=True
)

plt.tick_params(
    axis="both",
    which="major",
    labelsize=24
)

plt.tight_layout()

# ==========================================
# SAVE FIGURE
# ==========================================

plt.savefig(
    "DockQ_vs_ipTM.pdf",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================
# DOCKQ PERFORMANCE SUMMARY
# ==========================================

total_structures = len(df)

failed = (
    df["DockQ"] <= 0.23
).sum()

acceptable = (
    (df["DockQ"] > 0.23) &
    (df["DockQ"] <= 0.49)
).sum()

medium = (
    (df["DockQ"] > 0.49) &
    (df["DockQ"] <= 0.80)
).sum()

high = (
    df["DockQ"] > 0.80
).sum()

acceptable_plus = (
    df["DockQ"] > 0.23
).sum()

failed_perc = (
    failed / total_structures * 100
    if total_structures else 0
)

acceptable_perc = (
    acceptable / total_structures * 100
    if total_structures else 0
)

medium_perc = (
    medium / total_structures * 100
    if total_structures else 0
)

high_perc = (
    high / total_structures * 100
    if total_structures else 0
)

acceptable_plus_perc = (
    acceptable_plus / total_structures * 100
    if total_structures else 0
)

# ==========================================
# SAVE SUMMARY
# ==========================================

with open(
    "DockQ_percentages_1seed_toprank.txt",
    "w"
) as f:

    f.write("DockQ Benchmark Summary\n")
    f.write("=======================\n\n")

    f.write(
        f"Total structures: {total_structures}\n\n"
    )

    f.write(
        f"Failed (≤0.23): "
        f"{failed} ({failed_perc:.1f}%)\n"
    )

    f.write(
        f"Acceptable (0.23-0.49): "
        f"{acceptable} ({acceptable_perc:.1f}%)\n"
    )

    f.write(
        f"Medium (0.49-0.80): "
        f"{medium} ({medium_perc:.1f}%)\n"
    )

    f.write(
        f"High (>0.80): "
        f"{high} ({high_perc:.1f}%)\n\n"
    )

    f.write(
        f"Acceptable+ (>0.23): "
        f"{acceptable_plus} "
        f"({acceptable_plus_perc:.1f}%)\n"
    )

# ==========================================
# PRINT SUMMARY
# ==========================================

print("\nDockQ Benchmark Summary")
print("=======================")
print(f"Total structures: {total_structures}")
print(f"Failed: {failed} ({failed_perc:.1f}%)")
print(f"Acceptable: {acceptable} ({acceptable_perc:.1f}%)")
print(f"Medium: {medium} ({medium_perc:.1f}%)")
print(f"High: {high} ({high_perc:.1f}%)")
print(
    f"Acceptable+: {acceptable_plus} "
    f"({acceptable_plus_perc:.1f}%)"
)

print(
    f"\nNumber of unique PDB codes: {len(pdb_codes)}"
)