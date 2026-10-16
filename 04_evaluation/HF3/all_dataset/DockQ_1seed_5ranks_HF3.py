"""
Calculate DockQ quality percentages for seed 1 across ranks 1-5 using both kinked and extended nanobody datasets.

Input files:
    ../{kinked,extended}/seed1/output/DockQ_seed1_rank{1-5}.txt

Output:
    DockQ_percentages_1seed_5ranks.txt

DockQ categories:
    Failed       : DockQ ≤ 0.23
    Acceptable   : 0.23 < DockQ ≤ 0.49
    Medium       : 0.49 < DockQ ≤ 0.80
    High         : DockQ > 0.80
"""

import pandas as pd

# ==========================================
# Input files
# ==========================================
dockq_files = [
    f"../{dataset}/seed1/output/DockQ_seed1_rank{rank}.txt"
    for dataset in ["kinked", "extended"]
    for rank in range(1, 6)
]

# ==========================================
# Load and combine DockQ files
# ==========================================
dockq_dfs = []

for file in dockq_files:
    df = pd.read_csv(file, sep="\t")
    dockq_dfs.append(df)

df_dockq = pd.concat(
    dockq_dfs,
    ignore_index=True
)

# ==========================================
# DockQ performance summary
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

high = (
    df_dockq["DockQ"] > 0.80
).sum()

acceptable_plus = (
    df_dockq["DockQ"] > 0.23
).sum()

# ==========================================
# Calculate percentages
# ==========================================
failed_pct = (
    100 * failed / total_structures
    if total_structures > 0 else 0
)

acceptable_pct = (
    100 * acceptable / total_structures
    if total_structures > 0 else 0
)

medium_pct = (
    100 * medium / total_structures
    if total_structures > 0 else 0
)

high_pct = (
    100 * high / total_structures
    if total_structures > 0 else 0
)

acceptable_plus_pct = (
    100 * acceptable_plus / total_structures
    if total_structures > 0 else 0
)

# ==========================================
# Save summary
# ==========================================
output_file = "DockQ_percentages_1seed_5ranks.txt"

with open(output_file, "w") as f:

    f.write("DockQ Performance Summary\n")
    f.write("========================\n\n")

    f.write(f"Total structures: {total_structures}\n\n")

    f.write(
        f"Failed (≤0.23): "
        f"{failed} ({failed_pct:.1f}%)\n"
    )

    f.write(
        f"Acceptable (0.23-0.49): "
        f"{acceptable} ({acceptable_pct:.1f}%)\n"
    )

    f.write(
        f"Medium (0.49-0.80): "
        f"{medium} ({medium_pct:.1f}%)\n"
    )

    f.write(
        f"High (>0.80): "
        f"{high} ({high_pct:.1f}%)\n\n"
    )

    f.write(
        f"Acceptable+ (>0.23): "
        f"{acceptable_plus} "
        f"({acceptable_plus_pct:.1f}%)\n"
    )

# ==========================================
# Print summary
# ==========================================
print(f"Total structures: {total_structures}")
print(f"Failed (≤0.23): {failed} ({failed_pct:.1f}%)")
print(f"Acceptable (0.23-0.49): {acceptable} ({acceptable_pct:.1f}%)")
print(f"Medium (0.49-0.80): {medium} ({medium_pct:.1f}%)")
print(f"High (>0.80): {high} ({high_pct:.1f}%)")
print(
    f"Acceptable+ (>0.23): "
    f"{acceptable_plus} "
    f"({acceptable_plus_pct:.1f}%)"
)

print(f"\nSaved summary to {output_file}")