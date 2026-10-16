#!/usr/bin/env python3
"""
Generate stacked bar plots showing DockQ quality category percentages for multiple structure prediction tools using 5 seeds and top-ranked models.

Inputs
------
../../04_evaluation/AF3/extended/allseeds/DockQ_percentages_5seeds_topranks.txt
../../04_evaluation/boltz-2/extended/allseeds/DockQ_percentages_5seeds_topranks.txt
../../04_evaluation/chai-1/extended/allseeds/DockQ_percentages_5seeds_topranks.txt
../../04_evaluation/ESMFold2/extended/allseeds/DockQ_percentages_5seeds_topranks.txt
../../04_evaluation/HF3/extended/allseeds/DockQ_percentages_5seeds_topranks.txt
../../04_evaluation/protenix-v2/extended/allseeds/DockQ_percentages_5seeds_topranks.txt

Outputs
-------
percentages_DockQ_5seeds_toprank.pdf
"""

import os
import re
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# INPUT
# ==========================================

folders = [
    "../../04_evaluation/AF3/extended/allseeds",
    "../../04_evaluation/boltz-2/extended/allseeds",
    "../../04_evaluation/chai-1/extended/allseeds",
    "../../04_evaluation/ESMFold2/extended/allseeds",
    "../../04_evaluation/HF3/extended/allseeds",
    "../../04_evaluation/protenix-v2/extended/allseeds",
]

tools = [
    "AF3",
    "Boltz-2",
    "Chai-1",
    "ESMFold2",
    "HF3",
    "Protenix-v2",
]

categories = [
    "High",
    "Medium",
    "Acceptable",
    "Failed",
]

colors = {
    "High": "green",
    "Medium": "orange",
    "Acceptable": "dodgerblue",
    "Failed": "red",
}

# ==========================================
# READ DATA
# ==========================================

data = {cat: [] for cat in categories}

for folder in folders:

    file = os.path.join(
        folder,
        "DockQ_percentages_5seeds_topranks.txt",
    )

    values = {cat: 0.0 for cat in categories}

    with open(file) as f:

        for line in f:

            # High, Medium, Failed
            for cat in ["High", "Medium", "Failed"]:

                match = re.search(
                    rf"^{re.escape(cat)}.*?\(([\d\.]+)%\)",
                    line.strip(),
                    re.IGNORECASE,
                )

                if match:
                    values[cat] = float(match.group(1))

            # Acceptable only (exclude Acceptable+)
            match = re.search(
                r"^Acceptable(?!\+).*?\(([\d\.]+)%\)",
                line.strip(),
                re.IGNORECASE,
            )

            if match:
                values["Acceptable"] = float(match.group(1))

    for cat in categories:
        data[cat].append(values[cat])

# ==========================================
# STACKED BAR PLOT
# ==========================================

x = np.arange(len(tools))

fig, ax = plt.subplots(figsize=(16, 12))

bottom = np.zeros(len(tools))

for cat in categories:

    bars = ax.bar(
        x,
        data[cat],
        width=0.8,
        bottom=bottom,
        color=colors[cat],
        edgecolor="black",
        linewidth=1,
        label=cat,
    )

    # Labels inside segments
    for bar, value, btm in zip(
        bars,
        data[cat],
        bottom,
    ):

        if value > 3:

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                btm + value / 2,
                f"{value:.1f}",
                ha="center",
                va="center",
                fontsize=20,
            )

    bottom += np.array(data[cat])

# ==========================================
# STYLING
# ==========================================

ax.set_xticks(x)

ax.set_xticklabels(
    tools,
    rotation=45,
)

ax.set_ylabel(
    "DockQ Percentage (%)",
    fontsize=40,
)

ax.tick_params(
    axis="x",
    labelsize=35,
)

ax.tick_params(
    axis="y",
    labelsize=35,
)

ax.set_ylim(0, 100)

ax.legend(
    fontsize=20,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.12),
    ncol=4,
)

plt.tight_layout()

# ==========================================
# SAVE FIGURE
# ==========================================

plt.savefig(
    "percentages_DockQ_5seeds_toprank.pdf",
    dpi=300,
    bbox_inches="tight",
)

plt.show()