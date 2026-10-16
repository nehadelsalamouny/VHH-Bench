"""
Extract DockQ scores for the top-ranked prediction (rank0) from a single seed.

Input file:
    ../output/DockQ_seed0_rank0.txt

Output:
    DockQ_1seed_toprank.txt
"""

import pandas as pd

# ==========================================
# Input file
# ==========================================
input_file = "../output/DockQ_seed0_rank0.txt"

# ==========================================
# Load DockQ values
# ==========================================
df = pd.read_csv(input_file, sep="\t")

df["DockQ"] = pd.to_numeric(
    df["DockQ"],
    errors="coerce"
)

df = df.dropna(subset=["DockQ"])

# ==========================================
# Save DockQ values
# ==========================================
output_file = "DockQ_1seed_toprank.txt"

df["DockQ"].to_csv(
    output_file,
    index=False,
    header=False
)

print(f"Saved {len(df)} DockQ values to {output_file}")