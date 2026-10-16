"""
Extract CDR3 RMSD values for top-ranked predictions (model 0).

Input:
    cdr3_rmsd.txt

Output:
    rank0_cdr3.txt
"""

import pandas as pd

# ==========================================
# Load CDR3 RMSD data
# ==========================================

df = pd.read_csv(
    "cdr3_rmsd.txt",
    sep="\t"
)

# ==========================================
# Keep only top-ranked predictions
# ==========================================

df = df[
    df["structure"].str.contains(
        "model_0",
        regex=False,
        na=False
    )
]

# ==========================================
# Save filtered data
# ==========================================

df.to_csv(
    "rank0_cdr3.txt",
    sep="\t",
    index=False
)

print(
    f"Extracted {len(df)} "
    "model_0 entries"
)