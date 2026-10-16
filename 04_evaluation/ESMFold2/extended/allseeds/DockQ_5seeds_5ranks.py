"""
Extract DockQ scores from all seed and rank combinations.

Input files:
    ../seed1/output/DockQ_seed*_rank*.txt

Output:
    DockQ_5seeds_5ranks.txt
"""

import re
import pandas as pd

# ==========================================
# Input files
# ==========================================
dockq_files = [
    f"../seed1/output/DockQ_seed{seed}_rank{rank}.txt"
    for rank in range(5)
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
    df["seed"] = (
        df["Model"]
        .str.extract(r"model_seed(\d+)")
        .astype(int)
    )

    # Extract rank from filename
    rank = int(
        re.search(r"rank(\d+)", file).group(1)
    )
    df["rank"] = rank

    dockq_dfs.append(df)

# ==========================================
# Combine all files
# ==========================================
df = pd.concat(dockq_dfs, ignore_index=True)

# ==========================================
# Remove true duplicates only
# ==========================================
df = df.drop_duplicates(
    subset=["PDB", "seed", "rank"]
)

# ==========================================
# Clean DockQ values
# ==========================================
df["DockQ"] = pd.to_numeric(
    df["DockQ"],
    errors="coerce"
)

df = df.dropna(subset=["DockQ"])

# ==========================================
# Save DockQ values
# ==========================================
output_file = "DockQ_5seeds_5ranks.txt"

df["DockQ"].to_csv(
    output_file,
    index=False,
    header=False
)

print(f"Saved {len(df)} DockQ values to {output_file}")