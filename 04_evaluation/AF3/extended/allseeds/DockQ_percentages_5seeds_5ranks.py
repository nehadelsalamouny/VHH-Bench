"""
Calculate DockQ quality categories from predictions generated across five random seeds and five ranking positions.

Input:
    DockQ_5seeds_5ranks.txt

Output:
    DockQ_percentages_5seeds_5ranks.txt
"""

import pandas as pd

# Input
dockq_file = "DockQ_5seeds_5ranks.txt"

# Load data
df = pd.read_csv(dockq_file, header=None, names=["DockQ"]).dropna()

total = len(df)

if total == 0:
    raise ValueError("No DockQ values found.")

# DockQ categories
failed = (df["DockQ"] < 0.23).sum()
acceptable = ((df["DockQ"] >= 0.23) & (df["DockQ"] < 0.49)).sum()
medium = ((df["DockQ"] >= 0.49) & (df["DockQ"] < 0.80)).sum()
high = (df["DockQ"] >= 0.80).sum()

acceptable_plus = (df["DockQ"] >= 0.23).sum()

# Save summary
with open("DockQ_percentages_5seeds_5ranks.txt", "w") as f:
    f.write(f"Total structures: {total}\n\n")
    f.write(f"Failed (<0.23): {failed} ({100 * failed / total:.1f}%)\n")
    f.write(f"Acceptable (0.23-0.49): {acceptable} ({100 * acceptable / total:.1f}%)\n")
    f.write(f"Medium (0.49-0.80): {medium} ({100 * medium / total:.1f}%)\n")
    f.write(f"High (≥0.80): {high} ({100 * high / total:.1f}%)\n")
    f.write(f"Acceptable+ (≥0.23): {acceptable_plus} ({100 * acceptable_plus / total:.1f}%)\n")

print("Saved DockQ_percentages_5seeds_5ranks.txt")