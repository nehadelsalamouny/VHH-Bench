"""
Extract LRMSD values from the top-ranked prediction (rank 0).

Input:
    ../output/DockQ_rank0.txt

Output:
    LRMSD_1seed_toprank.txt
"""

import pandas as pd

# ==========================================
# Load data
# ==========================================

df = pd.read_csv(
    "../output/DockQ_rank0.txt",
    sep="\t"
)

df["LRMSD"] = pd.to_numeric(
    df["LRMSD"],
    errors="coerce"
)

lrmsd_values = df["LRMSD"].dropna()

# ==========================================
# Save values
# ==========================================

lrmsd_values.to_csv(
    "LRMSD_1seed_toprank.txt",
    index=False,
    header=False
)

print(
    f"Saved {len(lrmsd_values)} LRMSD values to "
    "LRMSD_1seed_toprank.txt"
)