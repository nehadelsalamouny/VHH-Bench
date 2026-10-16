"""
Plot DockQ scores for five ranks (rank1-rank5) across multiple seeds for each benchmark structure.

Input files:
    ../seed1/output/DockQ_seed*_rank*.txt

Output:
    DockQ_allranks_pdb_plot.pdf
"""

import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ==========================================
# Plot settings
# ==========================================
rank_colors = {
    "rank1": "#1f77b4",
    "rank2": "#ff7f0e",
    "rank3": "#2ca02c",
    "rank4": "#d62728",
    "rank5": "#9467bd",
}

offsets = {
    "rank1": -0.20,
    "rank2": -0.10,
    "rank3": 0.00,
    "rank4": 0.10,
    "rank5": 0.20,
}

# ==========================================
# Find DockQ files
# ==========================================
files = sorted(
    glob.glob(
        "../seed1/output/DockQ_seed*_rank*.txt"
    )
)

# ==========================================
# Load data
# ==========================================
all_data = []

for file in files:

    df = pd.read_csv(
        file,
        sep=r"\s+"
    )

    df.columns = df.columns.str.strip()

    filename = os.path.basename(file)

    # Example:
    # DockQ_seed1_rank1.txt
    parts = (
        filename
        .replace(".txt", "")
        .split("_")
    )

    seed = parts[1]
    rank = parts[2]

    if "Folder" not in df.columns:
        raise ValueError(
            f"'Folder' column not found in {file}\n"
            f"Columns found: {df.columns.tolist()}"
        )

    df["PDB_code"] = (
        df["Folder"]
        .astype(str)
        .str.split("/")
        .str[0]
    )

    df["DockQ"] = pd.to_numeric(
        df["DockQ"],
        errors="coerce"
    )

    df["Seed"] = seed
    df["Rank"] = rank

    all_data.append(
        df[
            [
                "PDB_code",
                "DockQ",
                "Seed",
                "Rank"
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

df_all = df_all[
    df_all["Rank"].isin(
        rank_colors.keys()
    )
]

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
plt.figure(figsize=(18, 10))

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

# Region labels
plt.text(
    -1.0,
    0.115,
    "Incorrect",
    fontsize=20,
    color="red",
    rotation=90,
    va="center"
)

plt.text(
    -1.0,
    0.36,
    "Acceptable",
    fontsize=20,
    color="orange",
    rotation=90,
    va="center"
)

plt.text(
    -1.0,
    0.645,
    "Medium",
    fontsize=20,
    color="goldenrod",
    rotation=90,
    va="center"
)

plt.text(
    -1.0,
    0.90,
    "High",
    fontsize=20,
    color="green",
    rotation=90,
    va="center"
)

# ==========================================
# Scatter plot
# ==========================================
for rank in rank_colors:

    subset = df_all[
        df_all["Rank"] == rank
    ]

    jitter = np.random.uniform(
        -0.025,
        0.025,
        len(subset)
    )

    plt.scatter(
        subset["x"]
        + offsets[rank]
        + jitter,
        subset["DockQ"],
        s=220,
        color=rank_colors[rank],
        alpha=0.75,
        edgecolor="black",
        linewidth=0.5,
        label=rank
    )

# ==========================================
# Axis formatting
# ==========================================
plt.xticks(
    range(len(pdb_codes)),
    pdb_codes,
    rotation=45,
    ha="right",
    fontsize=16
)

plt.yticks(fontsize=14)

plt.xlabel(
    "PDB Code",
    fontsize=32
)

plt.ylabel(
    "DockQ",
    fontsize=32
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
output_file = (
    "DockQ_allranks_pdb_plot.pdf"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(
    f"\nSaved plot to "
    f"{output_file}"
)
