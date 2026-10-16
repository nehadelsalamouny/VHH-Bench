#!/usr/bin/env python3

"""
Extract LRMSD values from the top-ranked prediction summary file and save them as a single-column dataset for downstream analysis.

Input:
    - DockQ_rank0.txt

Output:
    - LRMSD_1seed_toprank.txt
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

all_lrmsd = []

for file in dockq_files:

    df = pd.read_csv(
        file,
        sep="\t"
    )

    df["LRMSD"] = pd.to_numeric(
        df["LRMSD"],
        errors="coerce"
    )

    all_lrmsd.append(
        df["LRMSD"]
    )

df_all = pd.concat(
    all_lrmsd,
    ignore_index=True
)

df_all = df_all.dropna()

# ==========================================
# SAVE OUTPUT
# ==========================================

df_all.to_csv(
    "LRMSD_1seed_toprank.txt",
    index=False,
    header=False
)

# ==========================================
# SUMMARY
# ==========================================

print(
    f"Saved {len(df_all)} LRMSD values "
    f"to LRMSD_1seed_toprank.txt"
)
