"""
Extract iRMSD values for the top-ranked prediction (rank1) from a single seed (seed101).

Input file:
    ../output/DockQ_seed101_rank1.txt

Output:
    iRMSD_1seed_toprank.txt
"""

import pandas as pd

# ==========================================
# Input file
# ==========================================
input_file = "../output/DockQ_seed101_rank1.txt"

# ==========================================
# Load iRMSD values
# ==========================================
df = pd.read_csv(
    input_file,
    sep="\t"
)

df["iRMSD"] = pd.to_numeric(
    df["iRMSD"],
    errors="coerce"
)

df = df.dropna(
    subset=["iRMSD"]
)

# ==========================================
# Save iRMSD values
# ==========================================
output_file = "iRMSD_1seed_toprank.txt"

df["iRMSD"].to_csv(
    output_file,
    index=False,
    header=False
)

# ==========================================
# Report
# ==========================================
print(
    f"Saved {len(df)} "
    f"iRMSD values to {output_file}"
)