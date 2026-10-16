"""
Plot DockQ versus ipTM for the top-ranked prediction (rank0) from seed 0.

Input files:
    ../output/DockQ_seed0_rank0.txt
    ../output/iptm_seed0_rank0.txt

Outputs:
    DockQ_vs_ipTM.pdf
    DockQ_percentages_1seed_toprank.txt
"""

import matplotlib.pyplot as plt
import pandas as pd
from itertools import cycle

# ==========================================
# Input files
# ==========================================
dockq_file = "../output/DockQ_seed0_rank0.txt"
iptm_file = "../output/iptm_seed0_rank0.txt"

# ==========================================
# Load and merge data
# ==========================================
df_dockq = pd.read_csv(dockq_file, sep=r"\s+")
df_dockq.columns = df_dockq.columns.str.strip()

df_dockq["seed"] = (
    df_dockq["Model"]
    .str.extract(r"model_seed(\d+)")
    .astype(int)
)

df_iptm = pd.read_csv(iptm_file, sep=r"\s+")
df_iptm.columns = df_iptm.columns.str.strip()

df = pd.merge(
    df_dockq[["PDB", "seed", "DockQ"]],
    df_iptm[["PDB", "seed", "iptm"]],
    on=["PDB", "seed"],
    how="inner"
)

df = df.drop_duplicates(subset=["PDB", "seed"])

# Keep seed 0 only
df = df[df["seed"] == 0]

df["PDB_code"] = df["PDB"]

# ==========================================
# Plot styling
# ==========================================
pdb_codes = sorted(df["PDB_code"].unique())

markers = [
    "o", "^", "s", "D", "v", "P", "X", "*",
    "<", ">", "d", "p", "h", "H", "8"
]

colors = [
    "#0097A7", "#7B1FA2", "#43A047", "#FF7F50",
    "#C0CA33", "#8E24AA", "#004D40", "#42A5F5",
    "#0D47A1", "#FFC107", "#999999", "#FF5722",
    "#795548", "#607D8B", "#673AB7", "#CDDC39",
    "#00BCD4", "#D81B60", "#E53935", "#6D4C41",
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

# Background regions
plt.axhspan(0.80, 1.00, color="green", alpha=0.10)
plt.axhspan(0.49, 0.80, color="yellow", alpha=0.10)
plt.axhspan(0.23, 0.49, color="orange", alpha=0.10)
plt.axhspan(0.00, 0.23, color="red", alpha=0.10)

# Threshold lines
plt.axvline(0.80, color="green", linestyle="--", linewidth=3)
plt.axvline(0.60, color="orange", linestyle="--", linewidth=3)

plt.axhline(0.80, color="green", linestyle="--", linewidth=3)
plt.axhline(0.49, color="orange", linestyle="--", linewidth=3)
plt.axhline(0.23, color="red", linestyle="--", linewidth=3)

# Region labels
plt.text(
    0.05, 0.115, "Incorrect",
    fontsize=30, color="red",
    rotation=90,
    va="center", ha="right"
)

plt.text(
    0.05, 0.36, "Acceptable",
    fontsize=30, color="orange",
    rotation=90,
    va="center", ha="right"
)

plt.text(
    0.05, 0.645, "Medium",
    fontsize=30, color="goldenrod",
    rotation=90,
    va="center", ha="right"
)

plt.text(
    0.05, 0.90, "High",
    fontsize=30, color="green",
    rotation=90,
    va="center", ha="right"
)

plt.text(
    0.30, 1.01, "Failed",
    fontsize=30,
    color="red",
    ha="center"
)

plt.text(
    0.70, 1.01, "Uncertain",
    fontsize=30,
    color="orange",
    ha="center"
)

plt.text(
    0.90, 1.01, "High",
    fontsize=30,
    color="green",
    ha="center"
)

# Scatter plot
for pdb in pdb_codes:

    subset = df[df["PDB_code"] == pdb]

    color, marker = pdb_style[pdb]

    plt.scatter(
        subset["iptm"],
        subset["DockQ"],
        color=color,
        marker=marker,
        s=260,
        edgecolor="black",
        alpha=0.7,
        label=pdb.upper()
    )

# ==========================================
# Axis formatting
# ==========================================
plt.xlabel("ipTM", fontsize=44)
plt.ylabel("DockQ", fontsize=44)

plt.xlim(0, 1)
plt.ylim(0, 1)

plt.grid(axis="y", linestyle="--", alpha=0.3)

plt.tick_params(
    axis="both",
    labelsize=26
)

plt.legend(
    loc="center left",
    bbox_to_anchor=(1, 0.5),
    fontsize=16,
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
# DockQ statistics
# ==========================================
total = len(df)

failed = (df["DockQ"] <= 0.23).sum()

acceptable = (
    (df["DockQ"] > 0.23)
    & (df["DockQ"] <= 0.49)
).sum()

medium = (
    (df["DockQ"] > 0.49)
    & (df["DockQ"] <= 0.80)
).sum()

high = (df["DockQ"] > 0.80).sum()

acceptable_plus = (
    df["DockQ"] > 0.23
).sum()

failed_pct = failed / total * 100
acceptable_pct = acceptable / total * 100
medium_pct = medium / total * 100
high_pct = high / total * 100
acceptable_plus_pct = acceptable_plus / total * 100

# ==========================================
# Save summary
# ==========================================
summary_file = "DockQ_percentages_1seed_toprank.txt"

with open(summary_file, "w") as f:
    f.write(f"Total structures: {total}\n")
    f.write(f"Failed: {failed} ({failed_pct:.1f}%)\n")
    f.write(f"Acceptable: {acceptable} ({acceptable_pct:.1f}%)\n")
    f.write(f"Medium: {medium} ({medium_pct:.1f}%)\n")
    f.write(f"High: {high} ({high_pct:.1f}%)\n")
    f.write(
        f"Acceptable+: "
        f"{acceptable_plus} "
        f"({acceptable_plus_pct:.1f}%)\n"
    )

# ==========================================
# Print summary
# ==========================================
print("\nDockQ Summary (seed 0, rank 0)")
print(f"Total structures: {total}")
print(f"High-quality: {high_pct:.1f}%")
print(f"Acceptable+: {acceptable_plus_pct:.1f}%")

print(f"\nSaved plot to {figure_file}")
print(f"Saved summary to {summary_file}")