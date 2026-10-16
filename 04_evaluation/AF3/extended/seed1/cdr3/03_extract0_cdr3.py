"""
Extract model_0 entries from cdr3_rmsd.txt.
"""

import pandas as pd

# Load RMSD results
df = pd.read_csv("cdr3_rmsd.txt", sep="\t")

# Keep only top-ranked predictions (model_0)
df = df[df["structure"].str.contains("model_0", regex=False)]

# Save filtered data
df.to_csv(
    "rank0_cdr3.txt",
    sep="\t",
    index=False
)

print(f"Extracted {len(df)} model_0 entries")