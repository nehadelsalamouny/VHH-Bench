"""
Plot DockQ scores for five seeds (101-105) and five ranks (0-4) across all benchmark structures.

Input files:
    ../seed1/output/DockQ_seed{101-105}_rank{0-4}.txt

Output:
    DockQ_allranks_pdb_plot.pdf
"""

import glob
import os

import matplotlib.pyplot as plt
import pandas as pd

# ==========================================
# Colors and offsets
# ==========================================
rank_colors = {
    "rank0": "#1f77b4",
    "rank1": "#ff7f0e",
    "rank2": "#2ca02c",
    "rank3": "#d62728",
    "rank4": "#9467bd",
}

offsets = {
    "rank0": -0.20,
    "rank1": -0.10,
    "rank2": 0.00,
    "rank3": 0.10,
    "rank4": 0.20,
}

# ==========================================
# Find DockQ files
# ==========================================
files = sorted(
    glob.glob(
        "../seed1/output/DockQ_seed10*_rank*.txt"
    )
)

# ==========================================
# Load data
# ==========================================
all_data = []

for file in files:

    filename = os.path.basename(file)

    # Example:
    # DockQ_seed101_rank0.txt
    name = filename.replace(".txt", "")
    parts = name.split("_")

    seed = parts[1]
    rank = parts[2]

    df = pd.read_csv(
        file,
        sep=r"\s+",
        engine="python"
    )

    df.columns = df.columns.str.strip()

    if "PDB" not in df.columns:
        raise ValueError(
            f"PDB column missing in {file}\n"
            f"Columns found: {df.columns.tolist()}"
        )

    df["PDB_code"] = df["PDB"].astype(str)

    df["DockQ"] = pd.to_numeric(
        df["DockQ"],
        errors="coerce"
    )

    df["Rank"] = rank
    df["Seed"] = seed

    all_data.append(
        df[
            [
                "PDB_code",
                "DockQ",
                "Rank",
                "Seed"
            ]
        ]
    )

# ==========================================
# Combine data
# ==========================================
df_all = pd.concat(
    all_data,
    ignore_index=True
)

df_all = df_all.dropna(
    subset=["PDB_code", "DockQ"]
)

# ==========================================
# Assign x positions
# ==========================================
pdb_codes = sorted(
    df_all["PDB_code"].unique()
)

pdb_to_x = {
    pdb: i
    for i, pdb in enumerate(pdb_codes)
}

df_all["x"] = (
    df_all["PDB_code"]
    .map(pdb_to_x)
)

print(
    f"Total structures: "
    f"{len(pdb_codes)}"
)

# ==========================================
# Create plot
# ==========================================
plt.figure(figsize=(20, 10))

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
plt.axhline(
    0.80,
    color="green",
    linestyle="--"
)

plt.axhline(
    0.49,
    color="orange",
    linestyle="--"
)

plt.axhline(
    0.23,
    color="red",
    linestyle="--"
)

# ==========================================
# Region labels
# ==========================================
plt.text(
    -0.3,
    0.115,
    "Incorrect",
    va="center",
    ha="right",
    fontsize=20,
    color="red",
    rotation=90
)

plt.text(
    -0.3,
    0.36,
    "Acceptable",
    va="center",
    ha="right",
    fontsize=20,
    color="orange",
    rotation=90
)

plt.text(
    -0.3,
    0.645,
    "Medium",
    va="center",
    ha="right",
    fontsize=20,
    color="goldenrod",
    rotation=90
)

plt.text(
    -0.3,
    0.90,
    "High",
    va="center",
    ha="right",
    fontsize=20,
    color="green",
    rotation=90
)

# ==========================================
# Scatter plot
# ==========================================
for rank in rank_colors:

    subset = df_all[
        df_all["Rank"] == rank
    ]

    plt.scatter(
        subset["x"] + offsets[rank],
        subset["DockQ"],
        s=220,
        alpha=0.85,
        color=rank_colors[rank],
        edgecolor="black",
        linewidth=0.3,
        label=rank
    )

# ==========================================
# Axis formatting
# ==========================================
plt.xlabel(
    "PDB Code",
    fontsize=32
)

plt.ylabel(
    "DockQ",
    fontsize=32
)

plt.xticks(
    range(len(pdb_codes)),
    pdb_codes,
    rotation=45,
    fontsize=16
)

plt.yticks(
    fontsize=14
)

plt.ylim(0, 1)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

plt.legend(
    fontsize=16
)

plt.tight_layout()

# ==========================================
# Save figure
# ==========================================
output_file = "DockQ_allranks_pdb_plot.pdf"

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================
# Report
# ==========================================
print(
    f"\nSaved plot to {output_file}"
)