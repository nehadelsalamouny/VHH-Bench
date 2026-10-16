"""
Calculate DockQ quality percentages from combined DockQ scores across five ranked predictions (rank0-rank4) for a single seed.

Input:
    DockQ_1seed_5ranks.txt

Output:
    DockQ_percentages_1seed_5ranks.txt

"""

import pandas as pd

# ==========================================
# Input file
# ==========================================
input_file = "DockQ_1seed_5ranks.txt"

# ==========================================
# Load DockQ scores
# ==========================================
df = pd.read_csv(
    input_file,
    header=None,
    names=["DockQ"]
)

df["DockQ"] = pd.to_numeric(
    df["DockQ"],
    errors="coerce"
)

df = df.dropna(subset=["DockQ"])

# ==========================================
# Calculate counts
# ==========================================
total = len(df)

failed = (df["DockQ"] < 0.23).sum()

acceptable = (
    (df["DockQ"] >= 0.23)
    & (df["DockQ"] < 0.49)
).sum()

medium = (
    (df["DockQ"] >= 0.49)
    & (df["DockQ"] < 0.80)
).sum()

high = (df["DockQ"] >= 0.80).sum()

acceptable_plus = (df["DockQ"] >= 0.23).sum()

# ==========================================
# Calculate percentages
# ==========================================
failed_pct = 100 * failed / total
acceptable_pct = 100 * acceptable / total
medium_pct = 100 * medium / total
high_pct = 100 * high / total
acceptable_plus_pct = 100 * acceptable_plus / total

# ==========================================
# Save summary
# ==========================================
output_file = "DockQ_percentages_1seed_5ranks.txt"

with open(output_file, "w") as f:
    f.write("DockQ Performance Summary\n")
    f.write("========================\n\n")

    f.write(f"Total structures: {total}\n\n")

    f.write(f"Failed (<0.23): {failed} ({failed_pct:.1f}%)\n")
    f.write(f"Acceptable (0.23-0.49): {acceptable} ({acceptable_pct:.1f}%)\n")
    f.write(f"Medium (0.49-0.80): {medium} ({medium_pct:.1f}%)\n")
    f.write(f"High (≥0.80): {high} ({high_pct:.1f}%)\n\n")
    f.write(
        f"Acceptable+ (≥0.23): "
        f"{acceptable_plus} ({acceptable_plus_pct:.1f}%)\n"
    )

# ==========================================
# Print summary
# ==========================================
print(f"Total structures: {total}")
print(f"Failed (<0.23): {failed} ({failed_pct:.1f}%)")
print(f"Acceptable (0.23-0.49): {acceptable} ({acceptable_pct:.1f}%)")
print(f"Medium (0.49-0.80): {medium} ({medium_pct:.1f}%)")
print(f"High (≥0.80): {high} ({high_pct:.1f}%)")
print(f"Acceptable+ (≥0.23): {acceptable_plus} ({acceptable_plus_pct:.1f}%)")

print(f"\nSaved summary to {output_file}")