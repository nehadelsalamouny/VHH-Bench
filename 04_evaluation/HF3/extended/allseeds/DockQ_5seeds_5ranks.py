"""
Extract DockQ scores from all seed and rank combinations.

Input files:
    ../seed1/output/DockQ_seed{1-5}_rank{1-5}.txt

Output:
    DockQ_5seeds_5ranks.txt
"""

import re
import pandas as pd

# ==========================================
# Input files
# ==========================================
dockq_files = [
    f"../seed1/output/DockQ_seed{seed}_rank{rank}.txt"
    for rank in range(1, 6)
    for seed in range(1, 6)
]

# ==========================================
# Load DockQ files
# ==========================================
df_dockq = pd.concat(
    [
        pd.read_csv(
            file,
            sep=r"\s+",
            engine="python",
            on_bad_lines="skip"
        )
        for file in dockq_files
    ],
    ignore_index=True
)

# ==========================================
# Clean column names
# ==========================================
df_dockq.columns = df_dockq.columns.str.strip()

# ==========================================
# Extract PDB code and rank
# ==========================================
def extract_pdb_rank(model):

    model = str(model)

    match = re.search(
        r"job-([0-9A-Za-z]{4})",
        model
    )

    if match:
        pdb = match.group(1).lower()

    else:
        match = re.search(
            r"/([0-9A-Za-z]{4})[/-]",
            model
        )

        pdb = (
            match.group(1).lower()
            if match
            else "NA"
        )

    rank_match = re.search(
        r"rank(\d+)",
        model
    )

    pred_match = re.search(
        r"pred-(\d+)",
        model
    )

    if rank_match:
        rank = int(rank_match.group(1))

    elif pred_match:
        rank = int(pred_match.group(1))

    else:
        rank = 1

    return pd.Series([pdb, rank])


df_dockq[["PDB_code", "Rank"]] = (
    df_dockq["Model"]
    .apply(extract_pdb_rank)
)

# ==========================================
# Clean DockQ values
# ==========================================
df_dockq = df_dockq[
    df_dockq["PDB_code"] != "NA"
]

df_dockq["DockQ"] = pd.to_numeric(
    df_dockq["DockQ"],
    errors="coerce"
)

df_dockq = df_dockq.dropna(
    subset=["DockQ"]
)

# ==========================================
# Save DockQ values
# ==========================================
output_file = "DockQ_5seeds_5ranks.txt"

df_dockq["DockQ"].to_csv(
    output_file,
    index=False,
    header=False
)

# ==========================================
# Summary
# ==========================================
print(
    f"Saved {len(df_dockq)} "
    f"DockQ values to {output_file}"
)