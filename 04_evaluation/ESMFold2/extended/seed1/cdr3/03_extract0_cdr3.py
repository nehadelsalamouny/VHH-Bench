"""
Extract CDR3 RMSD values for the top-ranked prediction (seed0, sample0).

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
# Keep top-ranked predictions
# ==========================================
df = df[
    df["structure"].str.contains(
        "seed0_sample0",
        regex=False,
        na=False
    )
]

# ==========================================
# Save filtered data
# ==========================================
output_file = "rank0_cdr3.txt"

df.to_csv(
    output_file,
    sep="\t",
    index=False
)

# ==========================================
# Report
# ==========================================
print(
    f"Extracted {len(df)} entries "
    f"to {output_file}"
)