"""
Extract DockQ scores from five seeds (101-105) and five ranks (0-4).

Input files:
    ../seed1/output/DockQ_seed{101-105}_rank{0-4}.txt

Output:
    DockQ_5seeds_5ranks.txt
"""

import pandas as pd

# ==========================================
# Input files
# ==========================================
dockq_files = [
    f"../seed1/output/DockQ_seed{seed}_rank{rank}.txt"
    for rank in range(5)
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
output_file = "DockQ_5seeds_5ranks.txt"

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