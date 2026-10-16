"""
Extract iRMSD values from the top-ranked prediction (rank 0).

Input:
    ../output/DockQ_rank0.txt

Output:
    iRMSD_1seed_toprank.txt
"""

import pandas as pd

# ==========================================
# Load data
# ==========================================

df = pd.read_csv(
    "../output/DockQ_rank0.txt",
    sep="\t"
)

df["iRMSD"] = pd.to_numeric(
    df["iRMSD"],
    errors="coerce"
)

irmsd_values = df["iRMSD"].dropna()

# ==========================================
# Save values
# ==========================================

irmsd_values.to_csv(
    "iRMSD_1seed_toprank.txt",
    index=False,
    header=False
)

print(
    f"Saved {len(irmsd_values)} iRMSD values to "
    "iRMSD_1seed_toprank.txt"
)