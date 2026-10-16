#!/usr/bin/env python3

"""
Extract top-ranked (model_0) CDR3 RMSD results from a complete CDR3 RMSD dataset.

Input:
    - cdr3_rmsd.txt

Output:
    - rank0_cdr3.txt
"""

import pandas as pd

# ==========================================
# INPUT FILE
# ==========================================

input_file = "cdr3_rmsd.txt"

# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_csv(
    input_file,
    sep="\t"
)

# ==========================================
# FILTER TOP-RANKED MODELS
# ==========================================

df = df[
    df["structure"].str.contains(
        "pred.model_idx_0",
        regex=False
    )
]

# ==========================================
# SAVE OUTPUT
# ==========================================

df.to_csv(
    "rank0_cdr3.txt",
    sep="\t",
    index=False
)

# ==========================================
# SUMMARY
# ==========================================

print(
    f"Extracted {len(df)} "
    f"model_0 entries"
)
