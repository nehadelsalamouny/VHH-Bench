"""
Extract DockQ scores from the top-ranked prediction (rank 0).

Input:
    ../output/DockQ_rank0.txt

Output:
    DockQ_1seed_toprank.txt
"""

import pandas as pd

# ==========================================
# Load DockQ data
# ==========================================

df = pd.read_csv(
    "../output/DockQ_rank0.txt",
    sep="\t"
)

dockq_values = pd.to_numeric(
    df["DockQ"],
    errors="coerce"
).dropna()

# ==========================================
# Save DockQ values
# ==========================================

dockq_values.to_csv(
    "DockQ_1seed_toprank.txt",
    index=False,
    header=False
)

print(
    f"Saved {len(dockq_values)} DockQ values to "
    "DockQ_1seed_toprank.txt"
)