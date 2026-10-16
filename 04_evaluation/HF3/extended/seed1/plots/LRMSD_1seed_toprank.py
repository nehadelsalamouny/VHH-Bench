"""
Extract LRMSD values for the top-ranked prediction (rank1) from a single seed.

Input file:
    ../output/DockQ_seed1_rank1.txt

Output:
    LRMSD_1seed_toprank.txt
"""

import pandas as pd

# ==========================================
# Input file
# ==========================================
input_file = "../output/DockQ_seed1_rank1.txt"

# ==========================================
# Load LRMSD values
# ==========================================
df = pd.read_csv(
    input_file,
    sep="\t"
)

df["LRMSD"] = pd.to_numeric(
    df["LRMSD"],
    errors="coerce"
)

df = df.dropna(subset=["LRMSD"])

# ==========================================
# Save LRMSD values
# ==========================================
output_file = "LRMSD_1seed_toprank.txt"

df["LRMSD"].to_csv(
    output_file,
    index=False,
    header=False
)

# ==========================================
# Report
# ==========================================
print(
    f"Saved {len(df)} "
    f"LRMSD values to {output_file}"
)