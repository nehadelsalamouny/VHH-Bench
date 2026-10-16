"""
Extract DockQ scores from five seeds for the top-ranked prediction (rank0).

Input files:
    ../seed1/output/DockQ_seed*_rank0.txt

Output:
    DockQ_5seeds_topranks.txt
"""

import pandas as pd

# ==========================================
# Input files
# ==========================================
dockq_files = [
    f"../seed1/output/DockQ_seed{seed}_rank0.txt"
    for seed in range(5)
]

# ==========================================
# Load DockQ files
# ==========================================
dockq_dfs = []

for file in dockq_files:
    df = pd.read_csv(file, sep=r"\s+")
    df.columns = df.columns.str.strip()

    # Extract seed from model name
    df["seed"] = df["Model"].str.extract(r"model_seed(\d+)").astype(int)

    dockq_dfs.append(df)

# ==========================================
# Combine files
# ==========================================
df = pd.concat(dockq_dfs, ignore_index=True)

# ==========================================
# Remove duplicates
# ==========================================
df = df.drop_duplicates(subset=["PDB", "seed"])

# ==========================================
# Clean DockQ values
# ==========================================
df["DockQ"] = pd.to_numeric(df["DockQ"], errors="coerce")
df = df.dropna(subset=["DockQ"])

# ==========================================
# Save DockQ values
# ==========================================
output_file = "DockQ_5seeds_topranks.txt"

df["DockQ"].to_csv(
    output_file,
    index=False,
    header=False
)

print(f"Saved {len(df)} DockQ values to {output_file}")