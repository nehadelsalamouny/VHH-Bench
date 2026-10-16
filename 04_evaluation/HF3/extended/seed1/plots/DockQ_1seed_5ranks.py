"""
Extract DockQ scores from five ranked predictions (rank1-rank5) for a single seed.

Input files:
    ../output/DockQ_seed1_rank1.txt
    ../output/DockQ_seed1_rank2.txt
    ../output/DockQ_seed1_rank3.txt
    ../output/DockQ_seed1_rank4.txt
    ../output/DockQ_seed1_rank5.txt

Output:
    DockQ_1seed_5ranks.txt
"""

import pandas as pd

# ==========================================
# Input files
# ==========================================
dockq_files = [
    f"../output/DockQ_seed1_rank{rank}.txt"
    for rank in range(1, 6)
]

# ==========================================
# Load DockQ values
# ==========================================
all_dockq = []

for file in dockq_files:

    df = pd.read_csv(file, sep="\t")

    df["DockQ"] = pd.to_numeric(
        df["DockQ"],
        errors="coerce"
    )

    all_dockq.append(df["DockQ"])

# ==========================================
# Combine all ranks
# ==========================================
df_all = pd.concat(
    all_dockq,
    ignore_index=True
)

df_all = df_all.dropna()

# ==========================================
# Save DockQ values
# ==========================================
output_file = "DockQ_1seed_5ranks.txt"

df_all.to_csv(
    output_file,
    index=False,
    header=False
)

# ==========================================
# Report
# ==========================================
print(
    f"Saved {len(df_all)} "
    f"DockQ values to {output_file}"
)