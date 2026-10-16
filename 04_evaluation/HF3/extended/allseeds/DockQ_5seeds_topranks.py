"""
Extract DockQ scores from five seeds for the
top-ranked prediction (rank1).

Input files:
    ../seed1/output/DockQ_seed1_rank1.txt
    ../seed1/output/DockQ_seed2_rank1.txt
    ../seed1/output/DockQ_seed3_rank1.txt
    ../seed1/output/DockQ_seed4_rank1.txt
    ../seed1/output/DockQ_seed5_rank1.txt

Output:
    DockQ_5seeds_topranks.txt
"""

import pandas as pd

# ==========================================
# Input files
# ==========================================
dockq_files = [
    f"../seed1/output/DockQ_seed{seed}_rank1.txt"
    for seed in range(1, 6)
]

# ==========================================
# Load and combine DockQ files
# ==========================================
df_dockq = pd.concat(
    [
        pd.read_csv(
            file,
            sep=r"\s+",
            engine="python",
            on_bad_lines="skip"
        )
        for file in dockq_files
    ],
    ignore_index=True
)

df_dockq.columns = (
    df_dockq.columns.str.strip()
)

# ==========================================
# Clean DockQ values
# ==========================================
df_dockq["DockQ"] = pd.to_numeric(
    df_dockq["DockQ"],
    errors="coerce"
)

df_dockq = df_dockq.dropna(
    subset=["DockQ"]
)

# ==========================================
# Save DockQ values
# ==========================================
output_file = "DockQ_5seeds_topranks.txt"

df_dockq["DockQ"].to_csv(
    output_file,
    index=False,
    header=False
)

# ==========================================
# Report
# ==========================================
print(
    f"Saved {len(df_dockq)} "
    f"DockQ values to {output_file}"
)