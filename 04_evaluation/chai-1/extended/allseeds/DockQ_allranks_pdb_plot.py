#!/usr/bin/env python3

"""
Visualize DockQ scores for multiple ranked predictions across all benchmark structures.

Output:
    DockQ_allranks_pdb_plot.pdf
"""

import matplotlib.pyplot as plt
import pandas as pd

# ==========================================
# INPUT FILES
# ==========================================

dockq_files = {
    f"rank{rank}": [
        f"../seed{seed}/output/DockQ_rank{rank}.txt"
        for seed in range(1, 6)
    ]
    for rank in range(5)
}

# ==========================================
# PLOT SETTINGS
# ==========================================

rank_colors = {
    "rank0": "#1f77b4",
    "rank1": "#ff7f0e",
    "rank2": "#2ca02c",
    "rank3": "#d62728",
    "rank4": "#9467bd"
}

offsets = {
    "rank0": -0.20,
    "rank1": -0.10,
    "rank2": 0.00,
    "rank3": 0.10,
    "rank4": 0.20
}

# ==========================================
# LOAD DATA
# ==========================================

all_data = []

for rank, files in dockq_files.items():

    rank_dfs = []

    for file in files:

        try:
            df = pd.read_csv(
                file,
                sep=r"\s+",
                engine="python"
            )

            df["DockQ"] = pd.to_numeric(
                df["DockQ"],
                errors="coerce"
            )

            df["PDB_code"] = (
                df["Model"]
                .str.split("//")
                .str[0]
            )

            df["Rank"] = rank

            rank_dfs.append(
                df[["PDB_code", "DockQ", "Rank"]]
            )

        except FileNotFoundError:
            print(f"Warning: File not found -> {file}")

    if rank_dfs:
        combined_rank_df = pd.concat(
            rank_dfs,
            ignore_index=True
        )

        all_data.append(combined_rank_df)

# ==========================================
# COMBINE DATA
# ==========================================

if not all_data:
    raise ValueError(
        "No data loaded. Check input file paths."
    )

df_all = pd.concat(
    all_data,
    ignore_index=True
)

df_all = df_all.dropna(
    subset=["PDB_code", "DockQ"]
)

# ==========================================
# ASSIGN X POSITIONS
# ==========================================

pdb_codes = sorted(
    df_all["PDB_code"].unique()
)

pdb_to_x = {
    pdb: i
    for i, pdb in enumerate(pdb_codes)
}

df_all["x"] = df_all["PDB_code"].map(
    pdb_to_x
)

# ==========================================
# SUMMARY
# ==========================================

print("\nStructures per rank:")
print(
    df_all.groupby("Rank").size()
)

print("\nCoverage matrix:")
print(
    df_all.groupby(
        ["PDB_code", "Rank"]
    ).size().unstack(fill_value=0)
)

# ==========================================
# PLOT
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

# Quality labels
plt.text(
    -0.3, 0.115,
    "Incorrect",
    va="center",
    ha="right",
    fontsize=24,
    color="red",
    rotation=90
)

plt.text(
    -0.3, 0.36,
    "Acceptable",
    va="center",
    ha="right",
    fontsize=24,
    color="orange",
    rotation=90
)

plt.text(
    -0.3, 0.645,
    "Medium",
    va="center",
    ha="right",
    fontsize=24,
    color="goldenrod",
    rotation=90
)

plt.text(
    -0.3, 0.90,
    "High",
    va="center",
    ha="right",
    fontsize=24,
    color="green",
    rotation=90
)

# Scatter plot
for rank in dockq_files.keys():

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
        linewidth=0.8,
        label=rank
    )

# ==========================================
# FORMATTING
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
    fontsize=14
)

plt.yticks(fontsize=18)

plt.ylim(0, 1)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

plt.legend(fontsize=16)

plt.tight_layout()

# ==========================================
# SAVE FIGURE
# ==========================================

plt.savefig(
    "DockQ_allranks_pdb_plot.pdf",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================
# FINAL SUMMARY
# ==========================================

print("\nTotal PDB structures:", len(pdb_codes))
print("Output file: DockQ_allranks_pdb_plot.pdf")
