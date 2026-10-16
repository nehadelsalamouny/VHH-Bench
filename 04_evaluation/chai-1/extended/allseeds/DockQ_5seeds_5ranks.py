#!/usr/bin/env python3

"""
Combine DockQ scores from 5 AlphaFold seeds and 5 ranked models.

Input:
    ../seed1/output/DockQ_rank0.txt
    ...
    ../seed5/output/DockQ_rank4.txt

Output:
    DockQ_5seeds_5ranks.txt

"""

import os
import pandas as pd

# ==========================================
# INPUT FILES
# ==========================================

dockq_files = [
    f"../seed{seed}/output/DockQ_rank{rank}.txt"
    for rank in range(5)
    for seed in range(1, 6)
]

# ==========================================
# LOAD DOCKQ VALUES
# ==========================================

all_dockq = []

for file in dockq_files:

    if not os.path.exists(file):
        print(f"Warning: File not found: {file}")
        continue

    try:
        df = pd.read_csv(
            file,
            sep=r"\s+",
            engine="python"
        )

        if "DockQ" not in df.columns:
            print(f"Warning: 'DockQ' column not found in {file}")
            continue

        df["DockQ"] = pd.to_numeric(
            df["DockQ"],
            errors="coerce"
        )

        all_dockq.append(df["DockQ"])

    except Exception as e:
        print(f"Error reading {file}: {e}")

# ==========================================
# COMBINE
# ==========================================

if not all_dockq:
    raise ValueError("No valid DockQ data were loaded.")

df_all = pd.concat(
    all_dockq,
    ignore_index=True
).dropna()

# ==========================================
# SAVE OUTPUT
# ==========================================

output_file = "DockQ_5seeds_5ranks.txt"

df_all.to_csv(
    output_file,
    index=False,
    header=False
)

# ==========================================
# SUMMARY
# ==========================================

print(f"Saved {len(df_all)} DockQ values")
print(f"Output file: {output_file}")