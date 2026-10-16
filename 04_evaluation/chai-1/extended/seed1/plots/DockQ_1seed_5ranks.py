#!/usr/bin/env python3

"""
Combine DockQ scores from multiple ranked prediction files into a single dataset for downstream analysis.

Inputs:
    - DockQ_rank0.txt
    - DockQ_rank1.txt
    - DockQ_rank2.txt
    - DockQ_rank3.txt
    - DockQ_rank4.txt

Output:
    - DockQ_1seed_5ranks.txt
"""

import pandas as pd

# ==========================================
# INPUT FILES
# ==========================================

dockq_files = [
    f"../output/DockQ_rank{rank}.txt"
    for rank in range(5)
]

# ==========================================
# LOAD AND COMBINE
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
)

df_all = df_all.dropna()

# ==========================================
# SAVE OUTPUT
# ==========================================

df_all.to_csv(
    "DockQ_1seed_5ranks.txt",
    index=False,
    header=False
)

# ==========================================
# SUMMARY
# ==========================================

print(
    f"Saved {len(df_all)} DockQ values "
    f"to DockQ_1seed_5ranks.txt"
)