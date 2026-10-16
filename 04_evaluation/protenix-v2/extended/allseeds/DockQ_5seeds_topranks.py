"""
Extract DockQ scores from five seeds (101-105) for the top-ranked prediction (rank0).

Input files:
    ../seed1/output/DockQ_seed101_rank0.txt
    ../seed1/output/DockQ_seed102_rank0.txt
    ../seed1/output/DockQ_seed103_rank0.txt
    ../seed1/output/DockQ_seed104_rank0.txt
    ../seed1/output/DockQ_seed105_rank0.txt

Output:
    DockQ_5seeds_topranks.txt
"""

import pandas as pd

# ==========================================
# Input files
# ==========================================
dockq_files = [
    f"../seed1/output/DockQ_seed{seed}_rank0.txt"
    for seed in range(101, 106)
]

# ==========================================
# Load DockQ files
# ==========================================
dfs = []

for file in dockq_files:

    df = pd.read_csv(
        file,
        sep=r"\s+",
        engine="python"
    )

    df.columns = df.columns.str.strip()

    dfs.append(df)

# ==========================================
# Combine all files
# ==========================================
df = pd.concat(
    dfs,
    ignore_index=True
)

# ==========================================
# Clean DockQ values
# ==========================================
df["DockQ"] = pd.to_numeric(
    df["DockQ"],
    errors="coerce"
)

df = df.dropna(
    subset=["DockQ"]
)

# ==========================================
# Save DockQ values
# ==========================================
output_file = "DockQ_5seeds_topranks.txt"

df["DockQ"].to_csv(
    output_file,
    index=False,
    header=False
)

# ==========================================
# Report
# ==========================================
print(
    f"Saved {len(df)} "
    f"DockQ values to {output_file}"
)