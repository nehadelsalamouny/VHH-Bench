"""
DockQ Performance Summary

This script combines DockQ results from five random seeds (seed1-seed5) and five ranked predictions (rank0-rank4) for the kinked and extended CDR3 datasets. 

Output:
    DockQ_percentages_5seeds_5ranks.txt
"""

import pandas as pd

# ==========================================
# Input files
# ==========================================

dockq_files = []

for seed in range(1, 6):
    for rank in range(5):
        dockq_files.extend([
            f"../kinked/seed{seed}/output/DockQ_rank{rank}.txt",
            f"../extended/seed{seed}/output/DockQ_rank{rank}.txt"
        ])

# ==========================================
# Read and combine DockQ files
# ==========================================

dockq_dfs = []

for file in dockq_files:
    df = pd.read_csv(file, sep="\t")

    rank = int(file.split("rank")[1].split(".txt")[0])
    seed = int(file.split("seed")[1].split("/")[0])

    df["Rank"] = rank
    df["Seed"] = seed

    dockq_dfs.append(df)

df_dockq = pd.concat(dockq_dfs, ignore_index=True)

# ==========================================
# DockQ classification counts
# ==========================================

total_structures = len(df_dockq)

failed = (df_dockq["DockQ"] <= 0.23).sum()

acceptable = (
    (df_dockq["DockQ"] > 0.23)
    & (df_dockq["DockQ"] <= 0.49)
).sum()

medium = (
    (df_dockq["DockQ"] > 0.49)
    & (df_dockq["DockQ"] <= 0.80)
).sum()

high = (df_dockq["DockQ"] > 0.80).sum()

acceptable_plus = (df_dockq["DockQ"] > 0.23).sum()

# ==========================================
# Calculate percentages
# ==========================================

failed_perc = 100 * failed / total_structures if total_structures > 0 else 0
acceptable_perc = 100 * acceptable / total_structures if total_structures > 0 else 0
medium_perc = 100 * medium / total_structures if total_structures > 0 else 0
high_perc = 100 * high / total_structures if total_structures > 0 else 0
acceptable_plus_perc = (
    100 * acceptable_plus / total_structures
    if total_structures > 0 else 0
)

# ==========================================
# Write summary
# ==========================================

output_file = "DockQ_percentages_5seeds_5ranks.txt"

with open(output_file, "w") as f:
    f.write("DockQ Performance Summary\n")
    f.write("========================\n\n")

    f.write(f"Total structures: {total_structures}\n\n")

    f.write(
        f"Failed (≤0.23): "
        f"{failed} ({failed_perc:.1f}%)\n"
    )

    f.write(
        f"Acceptable (0.23-0.49): "
        f"{acceptable} ({acceptable_perc:.1f}%)\n"
    )

    f.write(
        f"Medium (0.49-0.80): "
        f"{medium} ({medium_perc:.1f}%)\n"
    )

    f.write(
        f"High (>0.80): "
        f"{high} ({high_perc:.1f}%)\n\n"
    )

    f.write(
        f"Acceptable+ (>0.23): "
        f"{acceptable_plus} ({acceptable_plus_perc:.1f}%)\n"
    )

print(f"Summary written to: {output_file}")