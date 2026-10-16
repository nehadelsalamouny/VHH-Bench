#!/usr/bin/env python3

"""
Gather DockQ scores from top-ranked predictions generated using multiple random seeds.

Output:
    DockQ_5seeds_topranks.txt
"""

import pandas as pd

# ==========================================
# INPUT FILES
# ==========================================

dockq_files = [
    f"../seed{seed}/output/DockQ_rank0.txt"
    for seed in range(1, 6)
]

# ==========================================
# LOAD DOCKQ VALUES
# ==========================================

all_dockq = []

for file in dockq_files:

    df = pd.read_csv(
        file,
        sep=r"\s+",
        engine="python"
    )

    df["DockQ"] = pd.to_numeric(
        df["DockQ"],
        errors="coerce"
    )

    all_dockq.append(df["DockQ"])

# ==========================================
# COMBINE VALUES
# ==========================================

df_all = pd.concat(
    all_dockq,
    ignore_index=True
).dropna()

# ==========================================
# SAVE OUTPUT
# ==========================================

df_all.to_csv(
    "DockQ_5seeds_topranks.txt",
    index=False,
    header=False
)

# ==========================================
# SUMMARY
# ==========================================

print(f"Saved {len(df_all)} DockQ values")