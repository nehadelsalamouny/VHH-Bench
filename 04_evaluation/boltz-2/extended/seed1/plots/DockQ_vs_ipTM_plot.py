"""
Plot DockQ versus ipTM for top-ranked predictions and calculate DockQ performance.

Inputs:
    ../output/all_DockQ.txt
    ../output/iptm_rank0.txt

Outputs:
    DockQ_vs_ipTM.pdf
    DockQ_percentages_1seed_toprank.txt
"""

import os
import re
from itertools import cycle

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import pandas as pd

# ==========================================
# Parse DockQ log file
# ==========================================

dockq_models = []
dockq_scores = []

with open("../output/all_DockQ.txt") as f:

    current_model = None

    for line in f:

        model_match = re.search(
            r"Model\s*:\s*(.+_model_0\.cif)",
            line
        )

        if model_match:
            current_model = model_match.group(1).strip()

        score_match = re.search(
            r"\bDockQ:\s*([0-9.]+)",
            line
        )

        if score_match and current_model:

            dockq_models.append(current_model)

            dockq_scores.append(
                float(score_match.group(1))
            )

            current_model = None

df_dockq = pd.DataFrame(
    {
        "Model": dockq_models,
        "DockQ": dockq_scores
    }
)

# ==========================================
# Load ipTM data
# ==========================================

df_iptm = pd.read_csv(
    "../output/iptm_rank0.txt",
    sep="\t"
)

df_iptm.columns = (
    df_iptm.columns.str.strip()
)

# ==========================================
# Normalise model names
# ==========================================

df_dockq["Model_file"] = (
    df_dockq["Model"]
    .apply(os.path.basename)
    .str.replace(".cif", "", regex=False)
)

df_iptm["Model_file"] = (
    df_iptm["Model"]
    .astype(str)
    .str.replace(
        r"^confidence_",
        "",
        regex=True
    )
)

# ==========================================
# Merge DockQ and ipTM
# ==========================================

df = pd.merge(
    df_dockq[
        ["Model_file", "DockQ"]
    ],
    df_iptm[
        ["Model_file", "ipTM"]
    ],
    on="Model_file",
    how="inner"
)

df = df.rename(
    columns={"ipTM": "iptm"}
)

if len(df) == 0:
    raise ValueError(
        "No matching structures found."
    )

# ==========================================
# Extract PDB codes
# ==========================================

def get_pdb_code(model_file):

    match = re.match(
        r"(.+?)_model_0$",
        model_file
    )

    return (
        match.group(1)
        if match
        else "NA"
    )

df["PDB_code"] = (
    df["Model_file"]
    .apply(get_pdb_code)
)

pdb_codes = sorted(
    df["PDB_code"].unique()
)

# ==========================================
# Style settings
# ==========================================

markers = [
    "o", "^", "s", "D", "v",
    "P", "X", "*", "<", ">",
    "d", "p", "h", "H", "8"
]

colors = [
    "#0097A7", "#7B1FA2", "#43A047",
    "#FF7F50", "#C0CA33", "#8E24AA",
    "#004D40", "#42A5F5", "#0D47A1",
    "#FFC107", "#999999", "#FF5722",
    "#795548", "#607D8B", "#673AB7",
    "#CDDC39", "#00BCD4", "#D81B60",
    "#E53935", "#6D4C41"
]

style_cycle = zip(
    cycle(colors),
    cycle(markers)
)

pdb_style = {
    pdb: next(style_cycle)
    for pdb in pdb_codes
}

# ==========================================
# Plot
# ==========================================

plt.figure(figsize=(16, 12))

plt.axhspan(
    0.80, 1.00,
    color="green",
    alpha=0.10
)

plt.axhspan(
    0.49, 0.80,
    color="yellow",
    alpha=0.10
)

plt.axhspan(
    0.23, 0.49,
    color="orange",
    alpha=0.10
)

plt.axhspan(
    0.00, 0.23,
    color="red",
    alpha=0.10
)

plt.axvline(
    0.80,
    color="green",
    linestyle="--",
    linewidth=3
)

plt.axvline(
    0.60,
    color="orange",
    linestyle="--",
    linewidth=3
)

plt.axhline(
    0.80,
    color="green",
    linestyle="--",
    linewidth=3
)

plt.axhline(
    0.49,
    color="orange",
    linestyle="--",
    linewidth=3
)

plt.axhline(
    0.23,
    color="red",
    linestyle="--",
    linewidth=3
)

for pdb in pdb_codes:

    subset = df[
        df["PDB_code"] == pdb
    ]

    color, marker = (
        pdb_style[pdb]
    )

    plt.scatter(
        subset["iptm"],
        subset["DockQ"],
        s=300,
        marker=marker,
        color=color,
        edgecolor="black",
        alpha=0.9,
        label=pdb
    )

# ==========================================
# Region labels
# ==========================================

plt.text(
    0.05, 0.115,
    "Incorrect",
    fontsize=30,
    color="red",
    rotation=90,
    ha="right",
    va="center"
)

plt.text(
    0.05, 0.36,
    "Acceptable",
    fontsize=30,
    color="orange",
    rotation=90,
    ha="right",
    va="center"
)

plt.text(
    0.05, 0.645,
    "Medium",
    fontsize=30,
    color="goldenrod",
    rotation=90,
    ha="right",
    va="center"
)

plt.text(
    0.05, 0.90,
    "High",
    fontsize=30,
    color="green",
    rotation=90,
    ha="right",
    va="center"
)

plt.text(
    0.30, 1.01,
    "Failed",
    fontsize=30,
    color="red",
    ha="center"
)

plt.text(
    0.70, 1.01,
    "Uncertain",
    fontsize=30,
    color="orange",
    ha="center"
)

plt.text(
    0.90, 1.01,
    "High",
    fontsize=30,
    color="green",
    ha="center"
)

# ==========================================
# Formatting
# ==========================================

plt.xlabel(
    "ipTM",
    fontsize=40
)

plt.ylabel(
    "DockQ",
    fontsize=40
)

plt.xlim(0, 1)
plt.ylim(0, 1)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

handles = [
    mlines.Line2D(
        [],
        [],
        linestyle="",
        marker=pdb_style[pdb][1],
        color=pdb_style[pdb][0],
        markeredgecolor="black",
        markersize=12,
        label=pdb.upper()
    )
    for pdb in pdb_codes
]

plt.legend(
    handles=handles,
    bbox_to_anchor=(1, 1),
    loc="upper left",
    fontsize=16,
    frameon=True
)

plt.tick_params(
    axis="both",
    which="major",
    labelsize=24
)

plt.tight_layout()

plt.savefig(
    "DockQ_vs_ipTM.pdf",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ==========================================
# DockQ statistics
# ==========================================

total_structures = len(df)

failed = (
    df["DockQ"] < 0.23
).sum()

acceptable = (
    (df["DockQ"] >= 0.23)
    & (df["DockQ"] < 0.49)
).sum()

medium = (
    (df["DockQ"] >= 0.49)
    & (df["DockQ"] < 0.80)
).sum()

high = (
    df["DockQ"] >= 0.80
).sum()

acceptable_plus = (
    df["DockQ"] >= 0.23
).sum()

with open(
    "DockQ_percentages_1seed_toprank.txt",
    "w"
) as f:

    f.write(
        "DockQ Complete Benchmark Summary\n"
    )

    f.write(
        "================================\n\n"
    )

    f.write(
        f"Total structures evaluated: "
        f"{total_structures}\n\n"
    )

    f.write(
        f"Failed (<0.23): "
        f"{failed} "
        f"({100 * failed / total_structures:.1f}%)\n"
    )

    f.write(
        f"Acceptable (0.23-0.49): "
        f"{acceptable} "
        f"({100 * acceptable / total_structures:.1f}%)\n"
    )

    f.write(
        f"Medium (0.49-0.80): "
        f"{medium} "
        f"({100 * medium / total_structures:.1f}%)\n"
    )

    f.write(
        f"High (≥0.80): "
        f"{high} "
        f"({100 * high / total_structures:.1f}%)\n\n"
    )

    f.write(
        f"Acceptable+ (≥0.23): "
        f"{acceptable_plus} "
        f"({100 * acceptable_plus / total_structures:.1f}%)\n"
    )

print(
    f"\nTotal structures: {total_structures}"
)
print(
    f"Number of unique PDB codes: "
    f"{len(pdb_codes)}"
)

print(
    "\nSaved:"
    "\n - DockQ_vs_ipTM.pdf"
    "\n - DockQ_percentages_1seed_toprank.txt"
)
