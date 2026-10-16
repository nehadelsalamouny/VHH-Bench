"""
Calculate DockQ quality categories for predictions generated from five ranking positions across the kinked and extended benchmark datasets.

Input:
    ../kinked/seed1/output/DockQ_rank*.txt
    ../extended/seed1/output/DockQ_rank*.txt

Output:
    DockQ_percentages_1seed_5ranks.txt
"""

import pandas as pd

# ==========================================
# Input files
# ==========================================

datasets = ["kinked", "extended"]

dockq_files = [
    f"../{dataset}/seed1/output/DockQ_rank{rank}.txt"
    for rank in range(5)
    for dataset in datasets
]

# ==========================================
# Load and combine DockQ data
# ==========================================

dockq_dfs = []

for file in dockq_files:

    df = pd.read_csv(
        file,
        sep="\t"
    )

    df["DockQ"] = pd.to_numeric(
        df["DockQ"],
        errors="coerce"
    )

    dockq_dfs.append(df)

df_dockq = pd.concat(
    dockq_dfs,
    ignore_index=True
).dropna(subset=["DockQ"])

total_structures = len(df_dockq)

if total_structures == 0:
    raise ValueError("No DockQ values found.")

# ==========================================
# Calculate DockQ categories
# ==========================================

failed = (
    df_dockq["DockQ"] < 0.23
).sum()

acceptable = (
    (df_dockq["DockQ"] >= 0.23)
    & (df_dockq["DockQ"] < 0.49)
).sum()

medium = (
    (df_dockq["DockQ"] >= 0.49)
    & (df_dockq["DockQ"] < 0.80)
).sum()

high = (
    df_dockq["DockQ"] >= 0.80
).sum()

acceptable_plus = (
    df_dockq["DockQ"] >= 0.23
).sum()

# ==========================================
# Calculate percentages
# ==========================================

failed_perc = 100 * failed / total_structures
acceptable_perc = 100 * acceptable / total_structures
medium_perc = 100 * medium / total_structures
high_perc = 100 * high / total_structures
acceptable_plus_perc = 100 * acceptable_plus / total_structures

# ==========================================
# Save summary
# ==========================================

with open(
    "DockQ_percentages_1seed_5ranks.txt",
    "w"
) as f:

    f.write("DockQ Performance Summary\n")
    f.write("========================\n\n")

    f.write(
        f"Total structures: "
        f"{total_structures}\n\n"
    )

    f.write(
        f"Failed (<0.23): "
        f"{failed} "
        f"({failed_perc:.1f}%)\n"
    )

    f.write(
        f"Acceptable (0.23-0.49): "
        f"{acceptable} "
        f"({acceptable_perc:.1f}%)\n"
    )

    f.write(
        f"Medium (0.49-0.80): "
        f"{medium} "
        f"({medium_perc:.1f}%)\n"
    )

    f.write(
        f"High (≥0.80): "
        f"{high} "
        f"({high_perc:.1f}%)\n\n"
    )

    f.write(
        f"Acceptable+ (≥0.23): "
        f"{acceptable_plus} "
        f"({acceptable_plus_perc:.1f}%)\n"
    )

print("Saved DockQ_percentages_1seed_5ranks.txt")