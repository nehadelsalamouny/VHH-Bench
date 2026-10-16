"""
Extract iRMSD values for the top-ranked prediction (rank0) from a single seed.

Input file:
    ../output/DockQ_seed0_rank0.txt

Output:
    iRMSD_1seed_toprank.txt
"""

import pandas as pd

# ==========================================
# Input file
# ==========================================
input_file = "../output/DockQ_seed0_rank0.txt"

# ==========================================
# Load iRMSD values
# ==========================================
df = pd.read_csv(input_file, sep="\t")

df["iRMSD"] = pd.to_numeric(
    df["iRMSD"],
    errors="coerce"
)

df = df.dropna(subset=["iRMSD"])

# ==========================================
# Save iRMSD values
# ==========================================
output_file = "iRMSD_1seed_toprank.txt"

df["iRMSD"].to_csv(
    output_file,
    index=False,
    header=False
)

print(f"Saved {len(df)} iRMSD values to {output_file}")