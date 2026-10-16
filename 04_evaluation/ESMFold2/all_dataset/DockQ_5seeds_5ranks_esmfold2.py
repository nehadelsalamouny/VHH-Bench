"""
Calculate DockQ performance across five seeds and five ranked predictions (rank0-rank4) for the kinked and extended nanobody datasets.

Input files:
    ../{kinked,extended}/seed*/output/DockQ_seed0_rank*.txt

Output:
    DockQ_percentages_5seeds_5ranks.txt
"""

import pandas as pd

# ==========================================
# Input DockQ files
# ==========================================
dockq_files = [
    f"../{dataset}/seed1/output/DockQ_seed{seed}_rank{rank}.txt"
    for dataset in ["kinked", "extended"]
    for seed in range(5)
    for rank in range(5)
]

# ==========================================
# Read and combine DockQ files
# ==========================================
dockq_dfs = []

for file in dockq_files:
    df = pd.read_csv(file, sep="\t")
    dockq_dfs.append(df)

df_dockq = pd.concat(dockq_dfs, ignore_index=True)

# ==========================================
# DockQ performance summary
# ==========================================
total_structures = len(df_dockq)

failed = (df_dockq["DockQ"] <= 0.23).sum()
acceptable = ((df_dockq["DockQ"] > 0.23) & (df_dockq["DockQ"] <= 0.49)).sum()
medium = ((df_dockq["DockQ"] > 0.49) & (df_dockq["DockQ"] <= 0.80)).sum()
high = (df_dockq["DockQ"] > 0.80).sum()

acceptable_plus = (df_dockq["DockQ"] > 0.23).sum()

failed_perc = (failed / total_structures) * 100 if total_structures > 0 else 0
acceptable_perc = (acceptable / total_structures) * 100 if total_structures > 0 else 0
medium_perc = (medium / total_structures) * 100 if total_structures > 0 else 0
high_perc = (high / total_structures) * 100 if total_structures > 0 else 0
acceptable_plus_perc = (
    (acceptable_plus / total_structures) * 100 if total_structures > 0 else 0
)

# ==========================================
# Save summary
# ==========================================
output_file = "DockQ_percentages_5seeds_5ranks.txt"

with open(output_file, "w") as f:
    f.write("DockQ Performance Summary\n")
    f.write("========================\n\n")
    f.write(f"Total structures: {total_structures}\n\n")
    f.write(f"Failed (≤0.23): {failed} ({failed_perc:.1f}%)\n")
    f.write(f"Acceptable (0.23-0.49): {acceptable} ({acceptable_perc:.1f}%)\n")
    f.write(f"Medium (0.49-0.80): {medium} ({medium_perc:.1f}%)\n")
    f.write(f"High (>0.80): {high} ({high_perc:.1f}%)\n\n")
    f.write(
        f"Acceptable+ (>0.23): {acceptable_plus} "
        f"({acceptable_plus_perc:.1f}%)\n"
    )

print(f"Summary saved to {output_file}")