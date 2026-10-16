"""
Calculate DockQ performance for five ranked predictions (rank0-rank4) from kinked and extended nanobody datasets.

Input files:
    ../{kinked,extended}/seed1/output/DockQ_seed0_rank{0-4}.txt

Output:
    DockQ_performance_summary_1seed_5ranks.txt
"""

import pandas as pd

# ==========================================
# Input DockQ files
# ==========================================
dockq_files = [
    f"../{dataset}/seed1/output/DockQ_seed0_rank{rank}.txt"
    for dataset in ["kinked", "extended"]
    for rank in range(5)
]

# ==========================================
# Read and combine DockQ files
# ==========================================
dockq_dfs = [pd.read_csv(file, sep="\t") for file in dockq_files]
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

# ==========================================
# Save summary
# ==========================================
output_file = "DockQ_percentages_1seed_5ranks.txt"

with open(output_file, "w") as f:
    f.write("DockQ Performance Summary\n")
    f.write("========================\n\n")
    f.write(f"Total structures: {total_structures}\n\n")
    f.write(f"Failed (≤0.23): {failed} ({100*failed/total_structures:.1f}%)\n")
    f.write(f"Acceptable (0.23-0.49): {acceptable} ({100*acceptable/total_structures:.1f}%)\n")
    f.write(f"Medium (0.49-0.80): {medium} ({100*medium/total_structures:.1f}%)\n")
    f.write(f"High (>0.80): {high} ({100*high/total_structures:.1f}%)\n\n")
    f.write(f"Acceptable+ (>0.23): {acceptable_plus} ({100*acceptable_plus/total_structures:.1f}%)\n")

print(f"Summary saved to {output_file}")