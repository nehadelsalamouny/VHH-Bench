"""
Combine DockQ scores from all prediction ranks generated with a single random seed. 

Input:
    ../output/DockQ_rank*.txt

Output:
    DockQ_1seed_5ranks.txt
"""

import pandas as pd

# ==========================================
# Input files
# ==========================================

dockq_files = [
    f"../output/DockQ_rank{rank}.txt"
    for rank in range(5)
]

# ==========================================
# Load and combine DockQ values
# ==========================================

all_dockq = []

for file in dockq_files:

    df = pd.read_csv(
        file,
        sep="\t"
    )

    df["DockQ"] = pd.to_numeric(
        df["DockQ"],
        errors="coerce"
    )

    all_dockq.append(
        df["DockQ"]
    )

df_all = pd.concat(
    all_dockq,
    ignore_index=True
).dropna()

# ==========================================
# Save DockQ values
# ==========================================

df_all.to_csv(
    "DockQ_1seed_5ranks.txt",
    index=False,
    header=False
)

print(
    f"Saved {len(df_all)} DockQ values to "
    "DockQ_1seed_5ranks.txt"
)
