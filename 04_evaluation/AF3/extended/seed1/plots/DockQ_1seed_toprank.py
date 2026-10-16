"""
Extract DockQ values from the top-ranked prediction (rank 0).
"""

import pandas as pd

# ==========================================
# Load DockQ data
# ==========================================

df = pd.read_csv(
    "../output/DockQ_rank0.txt",
    sep="\t"
)

df["DockQ"] = pd.to_numeric(
    df["DockQ"],
    errors="coerce"
)

df["DockQ"] = df["DockQ"].dropna()

# ==========================================
# Save DockQ values
# ==========================================

df["DockQ"].to_csv(
    "DockQ_1seed_toprank.txt",
    index=False,
    header=False
)

print("Saved DockQ_1seed_toprank.txt")