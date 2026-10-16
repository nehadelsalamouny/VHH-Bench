"""
Plot DockQ scores for all ranks (rank0-rank4) across five seeds for each benchmark structure.

Input files:
    ../seed1/output/DockQ_seed*_rank*.txt

Output:
    DockQ_allranks_pdb_plot.pdf
"""

import matplotlib.pyplot as plt
import pandas as pd

# ==========================================
# Input files
# ==========================================
dockq_files = {
    f"rank{rank}": [
        f"../seed1/output/DockQ_seed{seed}_rank{rank}.txt"
        for seed in range(5)
    ]
    for rank in range(5)
}

# ==========================================
# Plot settings
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
# Read DockQ files
# ==========================================
all_data = []

for rank, files in dockq_files.items():

    rank_dfs = []

    for file in files:
        df = pd.read_csv(file, sep=r"\s+")
        df.columns = df.columns.str.strip()

        df["PDB_code"] = df["PDB"]
        df["Rank"] = rank

        rank_dfs.append(df[["PDB_code", "DockQ", "Rank"]])

    all_data.append(pd.concat(rank_dfs, ignore_index=True))

# ==========================================
# Combine all data
# ==========================================
df_all = pd.concat(all_data, ignore_index=True)

df_all["DockQ"] = pd.to_numeric(df_all["DockQ"], errors="coerce")
df_all = df_all.dropna(subset=["PDB_code", "DockQ"])

# ==========================================
# Assign x positions
# ==========================================
pdb_codes = sorted(df_all["PDB_code"].unique())
pdb_to_x = {pdb: i for i, pdb in enumerate(pdb_codes)}

df_all["x"] = df_all["PDB_code"].map(pdb_to_x)

# ==========================================
# Create plot
# ==========================================
plt.figure(figsize=(18, 10))

# DockQ quality regions
plt.axhspan(0.80, 1.00, color="green", alpha=0.10)
plt.axhspan(0.49, 0.80, color="yellow", alpha=0.10)
plt.axhspan(0.23, 0.49, color="orange", alpha=0.10)
plt.axhspan(0.00, 0.23, color="red", alpha=0.10)

plt.axhline(0.80, color="green", linestyle="--")
plt.axhline(0.49, color="orange", linestyle="--")
plt.axhline(0.23, color="red", linestyle="--")

# Region labels
plt.text(
    -0.3, 0.115, "Incorrect",
    fontsize=20, color="red",
    rotation=90, va="center", ha="right"
)

plt.text(
    -0.3, 0.36, "Acceptable",
    fontsize=20, color="orange",
    rotation=90, va="center", ha="right"
)

plt.text(
    -0.3, 0.645, "Medium",
    fontsize=20, color="goldenrod",
    rotation=90, va="center", ha="right"
)

plt.text(
    -0.3, 0.90, "High",
    fontsize=20, color="green",
    rotation=90, va="center", ha="right"
)

# Plot each rank
for rank in dockq_files:

    subset = df_all[df_all["Rank"] == rank]

    plt.scatter(
        subset["x"] + offsets[rank],
        subset["DockQ"],
        s=220,
        alpha=0.85,
        color=rank_colors[rank],
        edgecolor="black",
        linewidth=0.8,
        label=rank,
    )

# ==========================================
# Axis formatting
# ==========================================
plt.xlabel("PDB Code", fontsize=32)
plt.ylabel("DockQ", fontsize=32)

plt.xticks(
    range(len(pdb_codes)),
    pdb_codes,
    rotation=45,
    fontsize=16,
)

plt.yticks(fontsize=16)

plt.ylim(0, 1)
plt.grid(axis="y", linestyle="--", alpha=0.3)

plt.legend(fontsize=16)
plt.tight_layout()

# ==========================================
# Save figure
# ==========================================
output_file = "DockQ_allranks_pdb_plot.pdf"

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight",
)

plt.show()

print(f"Saved plot to {output_file}")
print(f"Total PDB structures: {len(pdb_codes)}")