#!/usr/bin/env python3
"""
Plot DockQ success rates (DockQ ≥ 0.23) for multiple structure prediction tools using 5 seeds and 5 ranks.

Inputs
------
../../04_evaluation/AF3/extended/allseeds/DockQ_percentages_5seeds_5ranks.txt
../../04_evaluation/boltz-2/extended/allseeds/DockQ_percentages_5seeds_5ranks.txt
../../04_evaluation/chai-1/extended/allseeds/DockQ_percentages_5seeds_5ranks.txt
../../04_evaluation/ESMFold2/extended/allseeds/DockQ_percentages_5seeds_5ranks.txt
../../04_evaluation/HF3/extended/allseeds/DockQ_percentages_5seeds_5ranks.txt
../../04_evaluation/protenix-v2/extended/allseeds/DockQ_percentages_5seeds_5ranks.txt

Output
------
SR_5seeds_5ranks.pdf
"""

import matplotlib.pyplot as plt
import numpy as np
import re
import os

# Full folder paths
folders = [
    "../../04_evaluation/AF3/extended/allseeds",
    "../../04_evaluation/boltz-2/extended/allseeds",
    "../../04_evaluation/chai-1/extended/allseeds",
    "../../04_evaluation/ESMFold2/extended/allseeds",
    "../../04_evaluation/HF3/extended/allseeds",
    "../../04_evaluation/protenix-v2/extended/allseeds"
]

tools = ["AF3", "Boltz-2", "Chai-1", "ESMFold2", "HF3", "Protenix-v2"]

category = "Acceptable"
color = "lightblue"

data = []

for folder in folders:
    file = os.path.join(folder, "DockQ_percentages_5seeds_5ranks.txt")
    value = 0

    with open(file) as f:
        for line in f:
            match = re.search(r'Acceptable.*?\(([\d\.]+)%\)', line)
            if match:
                value = float(match.group(1))

    data.append(value)

data = np.array(data)

x = np.arange(len(tools))

plt.figure(figsize=(16, 12))

bars = plt.bar(
    x,
    data,
    width=0.5,
    color=color,
    edgecolor='black',
    linewidth=1
)

# Add percentage labels on top of each bar
for bar, value in zip(bars, data):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 1,
        f"{value:.1f}",
        ha='center',
        va='bottom',
        fontsize=28,
        # fontweight='bold'
    )

plt.xticks(x, tools)

plt.ylabel(
    "% Success Rate (DockQ ≥ 0.23)",
    fontsize=40
)

plt.tick_params(
    axis='x',
    which='major',
    labelsize=35,
    labelrotation=45
)

plt.tick_params(
    axis='y',
    which='major',
    labelsize=35
)

plt.ylim(0, 100)

# plt.title("DockQ Acceptable Models", fontsize=40)

plt.tight_layout()

plt.savefig(
    "SR_5seeds_5ranks.pdf",
    dpi=300,
    bbox_inches='tight'
)

plt.show()