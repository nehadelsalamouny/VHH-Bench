"""
Calculate DockQ quality categories for top-ranked predictions across five random seeds.

Input:
    DockQ_5seeds_topranks.txt

Output:
    DockQ_percentages_5seeds_topranks.txt
"""

import pandas as pd

# ==========================================
# Input
# ==========================================

dockq_file = "DockQ_5seeds_topranks.txt"

# ==========================================
# Load data
# ==========================================

df = pd.read_csv(
    dockq_file,
    header=None,
    names=["DockQ"]
)

# Remove missing values
df = df.dropna()

total = len(df)

if total == 0:
    raise ValueError("No DockQ values found.")

# ==========================================
# Count DockQ categories
# ==========================================

failed = (df["DockQ"] < 0.23).sum()

acceptable = (
    (df["DockQ"] >= 0.23) &
    (df["DockQ"] < 0.49)
).sum()

medium = (
    (df["DockQ"] >= 0.49) &
    (df["DockQ"] < 0.80)
).sum()

high = (
    df["DockQ"] >= 0.80
).sum()

acceptable_plus = (
    df["DockQ"] >= 0.23
).sum()

# ==========================================
# Save summary
# ==========================================

with open("DockQ_percentages_5seeds_topranks.txt", "w") as f:

    f.write(f"Total structures: {total}\n\n")

    f.write(
        f"Failed (<0.23): {failed} "
        f"({100 * failed / total:.1f}%)\n"
    )

    f.write(
        f"Acceptable (0.23-0.49): {acceptable} "
        f"({100 * acceptable / total:.1f}%)\n"
    )

    f.write(
        f"Medium (0.49-0.80): {medium} "
        f"({100 * medium / total:.1f}%)\n"
    )

    f.write(
        f"High (≥0.80): {high} "
        f"({100 * high / total:.1f}%)\n"
    )

    f.write(
        f"Acceptable+ (≥0.23): {acceptable_plus} "
        f"({100 * acceptable_plus / total:.1f}%)\n"
    )

# ==========================================
# Print summary
# ==========================================

print(f"Total structures: {total}")
print(f"Failed (<0.23): {failed} ({100 * failed / total:.1f}%)")
print(f"Acceptable (0.23-0.49): {acceptable} ({100 * acceptable / total:.1f}%)")
print(f"Medium (0.49-0.80): {medium} ({100 * medium / total:.1f}%)")
print(f"High (≥0.80): {high} ({100 * high / total:.1f}%)")
print(f"Acceptable+ (≥0.23): {acceptable_plus} ({100 * acceptable_plus / total:.1f}%)")

print("\nSaved DockQ_percentages_5seeds_topranks.txt")