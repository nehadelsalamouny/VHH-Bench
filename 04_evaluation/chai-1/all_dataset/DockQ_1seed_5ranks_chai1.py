"""
DockQ Performance Summary

This script combines DockQ results from multiple prediction ranks (rank0-rank4) across the kinked and extended nanobody datasets and
calculates the percentage of predictions in each DockQ quality class.

Output:
    DockQ_percentages_1seed_5ranks.txt
"""

import pandas as pd
import glob
import os

# ==========================================
# 1. Find all DockQ files
# ==========================================

dockq_files = sorted(
    glob.glob("../kinked/seed1/output/DockQ_rank*.txt") +
    glob.glob("../extended/seed1/output/DockQ_rank*.txt")
)


# ==========================================
# 2. Read and combine DockQ files
# ==========================================

dockq_dfs = []

for file in dockq_files:
    df = pd.read_csv(file, sep="\t")

    rank = int(file.split("rank")[1].split(".txt")[0])
    df["Rank"] = rank

    dockq_dfs.append(df)

df_dockq = pd.concat(dockq_dfs, ignore_index=True)

# ==========================================
# 3. DockQ classification
# ==========================================

total_structures = len(df_dockq)

failed = (df_dockq["DockQ"] <= 0.23).sum()
acceptable = ((df_dockq["DockQ"] > 0.23) & (df_dockq["DockQ"] <= 0.49)).sum()
medium = ((df_dockq["DockQ"] > 0.49) & (df_dockq["DockQ"] <= 0.80)).sum()
high = (df_dockq["DockQ"] > 0.80).sum()

acceptable_plus = (df_dockq["DockQ"] > 0.23).sum()

# ==========================================
# 4. Percentages
# ==========================================

failed_perc = 100 * failed / total_structures
acceptable_perc = 100 * acceptable / total_structures
medium_perc = 100 * medium / total_structures
high_perc = 100 * high / total_structures
acceptable_plus_perc = 100 * acceptable_plus / total_structures

# ==========================================
# 5. Save summary
# ==========================================

with open("DockQ_percentages_1seed_5ranks.txt", "w") as f:

    f.write("\nDockQ Performance Summary\n")
    f.write("========================\n\n")

    f.write(f"Total structures: {total_structures}\n\n")
    f.write(f"Failed (≤0.23): {failed} ({failed_perc:.1f}%)\n")
    f.write(f"Acceptable (0.23-0.49): {acceptable} ({acceptable_perc:.1f}%)\n")
    f.write(f"Medium (0.49-0.80): {medium} ({medium_perc:.1f}%)\n")
    f.write(f"High (>0.80): {high} ({high_perc:.1f}%)\n\n")
    f.write(f"Acceptable+ (>0.23): {acceptable_plus} ({acceptable_plus_perc:.1f}%)\n")