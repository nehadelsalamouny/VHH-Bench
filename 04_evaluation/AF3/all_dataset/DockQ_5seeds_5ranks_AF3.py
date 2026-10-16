"""
Summarise DockQ across all prediction ranks for 5 seeds for the kinked and extended benchmark subsets.

Input:
    ../kinked/seed*/output/DockQ_rank*.txt
    ../extended/seed*/output/DockQ_rank*.txt

Output:
    DockQ_percentages_5seeds_5ranks.txt
"""


import pandas as pd

# ==========================================
# 1. Define DockQ files
# ==========================================

dockq_files = [
    f"../{dataset}/seed{seed}/output/DockQ_rank{rank}.txt"
    for seed in range(1, 6)
    for rank in range(5)
    for dataset in ["kinked", "extended"]
]

# ==========================================
# 2. Read and combine DockQ data
# ==========================================

dockq_dfs = []

for file in dockq_files:
    df = pd.read_csv(file, sep="\t")
    dockq_dfs.append(df)

df_dockq = pd.concat(dockq_dfs, ignore_index=True)

# ==========================================
# 3. Calculate DockQ statistics
# ==========================================

total_structures = len(df_dockq)

failed = (df_dockq["DockQ"] <= 0.23).sum()
acceptable = ((df_dockq["DockQ"] > 0.23) & (df_dockq["DockQ"] <= 0.49)).sum()
medium = ((df_dockq["DockQ"] > 0.49) & (df_dockq["DockQ"] <= 0.80)).sum()
high = (df_dockq["DockQ"] > 0.80).sum()

acceptable_plus = (df_dockq["DockQ"] > 0.23).sum()

failed_perc = failed / total_structures * 100
acceptable_perc = acceptable / total_structures * 100
medium_perc = medium / total_structures * 100
high_perc = high / total_structures * 100
acceptable_plus_perc = acceptable_plus / total_structures * 100

# ==========================================
# 4. Write summary
# ==========================================

with open("DockQ_percentages_5seeds_5ranks.txt", "w") as f:
    f.write("DockQ Performance Summary\n")
    f.write("========================\n\n")
    f.write(f"Total structures: {total_structures}\n\n")
    f.write(f"Failed (≤0.23): {failed} ({failed_perc:.1f}%)\n")
    f.write(f"Acceptable (0.23–0.49): {acceptable} ({acceptable_perc:.1f}%)\n")
    f.write(f"Medium (0.49–0.80): {medium} ({medium_perc:.1f}%)\n")
    f.write(f"High (>0.80): {high} ({high_perc:.1f}%)\n\n")
    f.write(f"Acceptable+ (>0.23): {acceptable_plus} ({acceptable_plus_perc:.1f}%)\n")