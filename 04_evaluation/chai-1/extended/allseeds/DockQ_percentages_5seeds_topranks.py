#!/usr/bin/env python3

"""
Calculate DockQ performance statistics from a combined dataset of top-ranked predictions generated using multiple random seeds.

Input:
    DockQ_5seeds_topranks.txt

Output:
    DockQ_percentages_5seeds_topranks.txt
"""

import pandas as pd

# ==========================================
# INPUT FILE
# ==========================================

dockq_file = "DockQ_5seeds_topranks.txt"

# ==========================================
# LOAD DATA
# ==========================================

df = pd.read_csv(
    dockq_file,
    header=None,
    names=["DockQ"]
)

df = df.dropna()

# ==========================================
# CALCULATE COUNTS
# ==========================================

total = len(df)

failed = (
    df["DockQ"] < 0.23
).sum()

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
# SAVE RESULTS
# ==========================================

with open(
    "DockQ_percentages_5seeds_topranks.txt",
    "w"
) as f:

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
# PRINT SUMMARY
# ==========================================

print(f"Total structures: {total}")

print(
    f"Failed (<0.23): {failed} "
    f"({100 * failed / total:.1f}%)"
)

print(
    f"Acceptable (0.23-0.49): {acceptable} "
    f"({100 * acceptable / total:.1f}%)"
)

print(
    f"Medium (0.49-0.80): {medium} "
    f"({100 * medium / total:.1f}%)"
)

print(
    f"High (≥0.80): {high} "
    f"({100 * high / total:.1f}%)"
)

print(
    f"Acceptable+ (≥0.23): {acceptable_plus} "
    f"({100 * acceptable_plus / total:.1f}%)"
)

print(
    "\nSaved DockQ_percentages_5seeds_topranks.txt"
)