#!/usr/bin/env python3

"""
Extract iRMSD values from the top-ranked prediction summary file and save them as a single-column dataset for downstream analysis.

Input:
    - DockQ_rank0.txt

Output:
    - iRMSD_1seed_toprank.txt
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

all_irmsd = []

for file in dockq_files:

    df = pd.read_csv(
        file,
        sep="\t"
    )

    df["iRMSD"] = pd.to_numeric(
        df["iRMSD"],
        errors="coerce"
    )

    all_irmsd.append(
        df["iRMSD"]
    )

df_all = pd.concat(
    all_irmsd,
    ignore_index=True
)

df_all = df_all.dropna()

# ==========================================
# SAVE OUTPUT
# ==========================================

df_all.to_csv(
    "iRMSD_1seed_toprank.txt",
    index=False,
    header=False
)

# ==========================================
# SUMMARY
# ==========================================

print(
    f"Saved {len(df_all)} iRMSD values "
    f"to iRMSD_1seed_toprank.txt"
)