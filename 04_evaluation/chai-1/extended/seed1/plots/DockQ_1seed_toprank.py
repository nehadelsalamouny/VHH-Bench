#!/usr/bin/env python3

"""
Extract DockQ scores from the top-ranked prediction summary file and save them as a single-column dataset for downstream analysis.

Input:
    - DockQ_rank0.txt

Output:
    - DockQ_1seed_toprank.txt
"""

import pandas as pd

# ==========================================
# INPUT FILE
# ==========================================

dockq_files = [
    "../output/DockQ_rank0.txt"
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
    "DockQ_1seed_toprank.txt",
    index=False,
    header=False
)

# ==========================================
# SUMMARY
# ==========================================

print(
    f"Saved {len(df_all)} DockQ values "
    f"to DockQ_1seed_toprank.txt"
)