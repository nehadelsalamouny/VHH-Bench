"""
Plot DockQ versus ipTM for top-ranked predictions.

Inputs:
    ../output/DockQ_rank0.txt
    ../output/iptm_rank0.txt

Outputs:
    DockQ_vs_ipTM.pdf
    DockQ_percentages_1seed_toprank.txt
"""

import os
import re
from itertools import cycle

import matplotlib.pyplot as plt
import pandas as pd

# ==========================================
# Input files
# ==========================================

dockq_file = "../output/DockQ_rank0.txt"
iptm_file = "../output/iptm_rank0.txt"

# ==========================================
# Load data
# ==========================================

dockq = pd.read_csv(
    dockq_file,
    sep="\t"
)

iptm = pd.read_csv(
    iptm_file,
    sep="\t"
)

# ==========================================
# Prepare merge keys
# ==========================================

dockq["Model_chain"] = dockq["Model"].str.replace(
    r"_model_0\.cif$",
    "",
    regex=True
)

iptm["Model_chain"] = iptm["Model"].apply(
    lambda x: os.path.basename(
        os.path.dirname(x)
    )
)

# ==========================================
# Merge datasets
# ==========================================

merged = pd.merge(
    dockq,
    iptm,
    on="Model_chain",
    how="inner"
)

print(f"DockQ rows: {len(dockq)}")
print(f"ipTM rows: {len(iptm)}")
print(f"Merged rows: {len(merged)}")

if len(merged) == 0:

    print("\nNo matching entries found.")

    print("\nDockQ examples:")
    print(dockq["Model_chain"].head())

    print("\nipTM examples:")
    print(iptm["Model_chain"].head())

    raise ValueError(
        "Merged dataframe is empty"
    )

# ==========================================
# Extract PDB code
# ==========================================

def extract_pdb_code(model_chain):

    match = re.search(
        r"([0-9a-z]{4})(?:_[A-Z])?$",
        model_chain
    )

    if match:
        return match.group(1).upper()

    return model_chain


merged["PDB_code"] = merged["Model_chain"].apply(
    extract_pdb_code
)

# ==========================================
# Plot settings
# ==========================================

markers = [
    "o", "^", "s", "D", "v",
    "P", "X", "*", "<", ">",
    "d", "p", "h", "H", "8"
]

colors = [
    "#0097A7", "#7B1FA2", "#43A047",
    "#FF7F50", "#C0CA33", "#8E24AA",
    "#004D40", "#42A5F5", "#0D47A1",
    "#FFC107", "#999999", "#FF5722",
    "#795548", "#607D8B", "#673AB7",
    "#CDDC39", "#00BCD4", "#D81B60",
    "#E53935", "#6D4C41"
]

unique_models = sorted(
    merged["Model_chain"].unique(),
    key=lambda x: extract_pdb_code(x)
)

style_cycle = zip(
    cycle(colors),
    cycle(markers)
)

model_style = {
    model: next(style_cycle)
    for model in unique_models
}

# ==========================================
# Plot
# ==========================================

plt.figure(figsize=(16, 12))

# DockQ quality regions

plt.axhspan(
    0.80, 1.00,
    color="green",
    alpha=0.1
)

plt.axhspan(
    0.49, 0.80,
    color="yellow",
    alpha=0.1
)

plt.axhspan(
    0.23, 0.49,
    color="orange",
    alpha=0.1
)

plt.axhspan(
    0.00, 0.23,
    color="red",
    alpha=0.1
)

# ipTM thresholds

plt.axvline(
    0.8,
    color="green",
    linestyle="--",
    linewidth=3
)

plt.axvline(
    0.6,
    color="orange",
    linestyle="--",
    linewidth=3
)

# DockQ thresholds

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

for model in unique_models:

    subset = merged[
        merged["Model_chain"] == model
    ]

    color, marker = model_style[model]

    plt.scatter(
        subset["iptm"],
        subset["DockQ"],
        color=color,
        marker=marker,
        s=300,
        edgecolor="black",
        alpha=0.9,
        label=extract_pdb_code(model).upper()
    )

# ==========================================
# Region labels
# ==========================================

plt.text(
    0.05, 0.115,
    "Incorrect",
    va="center",
    ha="right",
    fontsize=32,
    color="red",
    rotation=90
)

plt.text(
    0.05, 0.36,
    "Acceptable",
    va="center",
    ha="right",
    fontsize=32,
    color="orange",
    rotation=90
)

plt.text(
    0.05, 0.645,
    "Medium",
    va="center",
    ha="right",
    fontsize=32,
    color="goldenrod",
    rotation=90
)

plt.text(
    0.05, 0.90,
    "High",
    va="center",
    ha="right",
    fontsize=32,
    color="green",
    rotation=90
)

plt.text(
    0.30, 1.01,
    "Failed",
    ha="center",
    va="bottom",
    fontsize=32,
    color="red"
)

plt.text(
    0.70, 1.01,
    "Uncertain",
    ha="center",
    va="bottom",
    fontsize=32,
    color="orange"
)

plt.text(
    0.90, 1.01,
    "High",
    ha="center",
    va="bottom",
    fontsize=32,
    color="green"
)

# ==========================================
# Formatting
# ==========================================

plt.xlabel(
    "ipTM",
    fontsize=40
)

plt.ylabel(
    "DockQ",
    fontsize=40
)

plt.gca().xaxis.set_label_coords(
    0.5,
    -0.05
)

plt.gca().yaxis.set_label_coords(
    -0.05,
    0.5
)

plt.xlim(0, 1)
plt.ylim(0, 1)

plt.tick_params(
    axis="both",
    which="major",
    labelsize=24
)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

plt.legend(
    bbox_to_anchor=(1, 1),
    loc="upper left",
    fontsize=16,
    frameon=True,
    ncol=1
)

plt.tight_layout()

# ==========================================
# Save figure
# ==========================================

plt.savefig(
    "DockQ_vs_ipTM.pdf",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================
# DockQ statistics
# ==========================================

total_structures = len(merged)

failed = (
    merged["DockQ"] < 0.23
).sum()

acceptable = (
    (merged["DockQ"] >= 0.23)
    & (merged["DockQ"] < 0.49)
).sum()

medium = (
    (merged["DockQ"] >= 0.49)
    & (merged["DockQ"] < 0.80)
).sum()

high = (
    merged["DockQ"] >= 0.80
).sum()

acceptable_plus = (
    merged["DockQ"] >= 0.23
).sum()

with open(
    "DockQ_percentages_1seed_toprank.txt",
    "w"
) as f:

    f.write(
        f"Total structures: "
        f"{total_structures}\n\n"
    )

    f.write(
        f"Failed (<0.23): {failed} "
        f"({100 * failed / total_structures:.1f}%)\n"
    )

    f.write(
        f"Acceptable (0.23-0.49): "
        f"{acceptable} "
        f"({100 * acceptable / total_structures:.1f}%)\n"
    )

    f.write(
        f"Medium (0.49-0.80): "
        f"{medium} "
        f"({100 * medium / total_structures:.1f}%)\n"
    )

    f.write(
        f"High (≥0.80): "
        f"{high} "
        f"({100 * high / total_structures:.1f}%)\n"
    )

    f.write(
        f"Acceptable+ (≥0.23): "
        f"{acceptable_plus} "
        f"({100 * acceptable_plus / total_structures:.1f}%)\n"
    )

print("\nDockQ Categories")
print(f"Total structures: {total_structures}")
print(
    f"Failed (<0.23): {failed} "
    f"({100 * failed / total_structures:.1f}%)"
)
print(
    f"Acceptable (0.23-0.49): {acceptable} "
    f"({100 * acceptable / total_structures:.1f}%)"
)
print(
    f"Medium (0.49-0.80): {medium} "
    f"({100 * medium / total_structures:.1f}%)"
)
print(
    f"High (≥0.80): {high} "
    f"({100 * high / total_structures:.1f}%)"
)
print(
    f"Acceptable+ (≥0.23): {acceptable_plus} "
    f"({100 * acceptable_plus / total_structures:.1f}%)"
)

print(
    "\nSaved:"
    "\n - DockQ_vs_ipTM.pdf"
    "\n - DockQ_percentages_1seed_toprank.txt"
)