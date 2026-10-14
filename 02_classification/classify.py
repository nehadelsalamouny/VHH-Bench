import MDAnalysis as mda
import matplotlib.pyplot as plt
from MDAnalysis.lib.distances import calc_angles
from MDAnalysis.lib.distances import calc_dihedrals
import glob
import numpy as np
import re
import shutil
import os
from pymol import cmd

out_dir = "results"
os.makedirs(out_dir, exist_ok=True)

AA = {
    "ALA", "ARG", "ASN", "ASP", "CYS",
    "GLN", "GLU", "GLY", "HIS", "ILE",
    "LEU", "LYS", "MET", "PHE", "PRO",
    "SER", "THR", "TRP", "TYR", "VAL",
    "MSE"
}

files = glob.glob("../01_dataset/*.pdb")

for f in files:

    print(f"\nProcessing: {f}")

    obj = os.path.splitext(os.path.basename(f))[0]

    cmd.load(f, obj)
    chains = cmd.get_chains(obj)

    candidate_chains = []
    insertion_chains = []

    for ch in chains:

        sel_ca = (
            f"{obj} and chain {ch} "
            f"and polymer.protein and name CA"
        )

        length = cmd.count_atoms(sel_ca)

        print(f"  Chain {ch} length: {length}")

        if not (100 <= length <= 140):
            continue

        residues = set()

        cmd.iterate(
            f"{obj} and chain {ch} and polymer.protein and name CA",
            "residues.add(resi)",
            space={"residues": residues}
        )

        res100 = [r for r in residues if r.startswith("100")]

        if not res100:
            continue

        candidate_chains.append((ch, length))

        # has 100A/100B/100C...
        if any(r != "100" for r in res100):
            insertion_chains.append((ch, length))

    # ------------------------------------
    # Prefer insertion-containing chains
    # ------------------------------------
    if insertion_chains:
        chains_to_keep = [ch for ch, _ in insertion_chains]
        print("    -> using chains with 100 insertions")

    elif candidate_chains:
        # use smallest chain having residue 100
        min_len = min(length for _, length in candidate_chains)
        chains_to_keep = [
            ch for ch, length in candidate_chains
            if length == min_len
        ]

        print(
            f"    -> no 100A/100B/100C found, "
            f"using smallest chain(s) with residue 100 "
            f"(length={min_len})"
        )

    else:
        chains_to_keep = []

    # Save selected chains
    for ch in chains_to_keep:

        out_name = os.path.join(
            out_dir,
            f"{obj}_{ch}.pdb"
        )

        print(f"    -> saving nanobody: {out_name}")

        with open(f) as fin, open(out_name, "w") as fout:

            for line in fin:

                if not line.startswith("ATOM"):
                    continue

                if len(line) < 54:
                    continue

                if line[21].strip() != ch:
                    continue

                resname = line[17:20].strip()
                if resname not in AA:
                    continue

                altloc = line[16]
                if altloc not in (" ", "A"):
                    continue

                fout.write(line)

            fout.write("END\n")

        # --------------------------------------------------
        # Write ONLY protein amino-acid ATOM records
        # --------------------------------------------------
        with open(f) as fin, open(out_name, "w") as fout:

            for line in fin:

                if not line.startswith("ATOM"):
                    continue

                if len(line) < 54:
                    continue

                # chain filter
                chain = line[21].strip()
                if chain != ch:
                    continue

                # amino acid filter
                resname = line[17:20].strip()
                if resname not in AA:
                    continue

                # keep only primary altloc
                altloc = line[16]
                if altloc not in (" ", "A"):
                    continue

                fout.write(line)

            fout.write("END\n")

    cmd.delete(obj)

print(f"\nDone. Extracted nanobodies saved in '{out_dir}/'")

output_file = "results/tau101_angle.txt"
pdb_files = sorted(glob.glob("results/*.pdb"))

with open(output_file, "w") as f:
    f.write("# File\tUsedResidue100\tAlpha101_angle(degrees)\n")
    for pdb in pdb_files:
        try:
            u = mda.Universe(pdb)

            # Find all residues with resid == 100 (including insertion codes)
            res100_all = [r for r in u.residues if r.resid == 100]
            if not res100_all:
                print(f"Warning: {pdb} missing residue 100 region.")
                continue

            # Pick the last residue alphabetically by insertion code (closest to 101)
            res100 = sorted(res100_all, key=lambda r: (r.icode or ''))[-1]

            # Collect CA coordinates
            atoms = []
            labels = []

            # Residue 100 (with insertion)
            ca100 = res100.atoms.select_atoms("name CA")
            if len(ca100) == 1:
                atoms.append(ca100.positions[0])
                labels.append(f"100{res100.icode or ''}")
            else:
                continue

            # Residues 101–102
            for resid in [101, 102]:
                ca = u.select_atoms(f"resid {resid} and name CA")
                if len(ca) == 1:
                    atoms.append(ca.positions[0])
                    labels.append(str(resid))

            if len(atoms) != 3:
                print(f"Warning: {pdb} missing required CA atoms (found {len(atoms)}).")
                continue

            # Compute angle 
            ang = calc_angles(*atoms)
            angle_deg = np.degrees(ang)
            f.write(f"{os.path.basename(pdb)}\t{labels[0]}\t{angle_deg:.3f}\n") 


        except Exception as e:
            print(f"Error processing {pdb}: {e}")

print(f"Done! Results saved to {output_file}")

output_file = "results/alpha101_dihedral.txt"
pdb_files = sorted(glob.glob("results/*.pdb"))

with open(output_file, "w") as f:
    f.write("# File\tUsedResidue100\tAlpha101(degrees)\n")
    for pdb in pdb_files:
        try:
            u = mda.Universe(pdb)

            # Find all residues with resid == 100 (including insertion codes)
            res100_all = [r for r in u.residues if r.resid == 100]
            if not res100_all:
                print(f"Warning: {pdb} missing residue 100 region.")
                continue

            # Pick the last residue alphabetically by insertion code (closest to 101)
            res100 = sorted(res100_all, key=lambda r: (r.icode or ''))[-1]

            # Collect CA coordinates
            atoms = []
            labels = []

            # 100 (with insertion)
            ca100 = res100.atoms.select_atoms("name CA")
            if len(ca100) == 1:
                atoms.append(ca100.positions[0])
                labels.append(f"100{res100.icode or ''}")
            else:
                continue

            # 101–103
            for resid in [101, 102, 103]:
                ca = u.select_atoms(f"resid {resid} and name CA")
                if len(ca) == 1:
                    atoms.append(ca.positions[0])
                    labels.append(str(resid))

            if len(atoms) != 4:
                print(f"Warning: {pdb} missing required CA atoms (found {len(atoms)}).")
                continue

            # Compute dihedral 
            dih = calc_dihedrals(*atoms)
            angle_deg = np.degrees(dih)  

            f.write(f"{os.path.basename(pdb)}\t{labels[0]}\t{angle_deg:.3f}\n")
        except Exception as e:
            print(f"Error processing {pdb}: {e}")

print(f"Done! Results saved to {output_file}")

# --- Read alpha101 data ---
alpha_file = "results/alpha101_dihedral.txt"
alpha_data = {}
with open(alpha_file) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        pdb = parts[0]
        alpha = float(parts[2])
        alpha_data[pdb] = alpha

# --- Read tau101 data ---
tau_file = "results/tau101_angle.txt"
tau_data = {}
with open(tau_file) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split()
        pdb = parts[0]
        tau = float(parts[2])
        tau_data[pdb] = tau

# --- Match by PDB ---
common_pdbs = sorted(set(alpha_data.keys()) & set(tau_data.keys()))
alpha_values = [alpha_data[pdb] for pdb in common_pdbs]
tau_values = [tau_data[pdb] for pdb in common_pdbs]

# --- Define colors and solid markers ---
colors = plt.cm.tab20(np.linspace(0, 1, 20))
markers = ['o', 's', '^', 'v', 'D', 'P', '*']  
n_markers = len(markers)
n_colors = len(colors)

# Assign marker and color to each point
point_styles = []
for i in range(len(common_pdbs)):
    color = colors[i % n_colors]
    marker = markers[i % n_markers]
    point_styles.append((color, marker))

# --- Create figure ---
fig, ax = plt.subplots(figsize=(10, 6))

# Scatter plot
for a, t, style in zip(alpha_values, tau_values, point_styles):
    color, marker = style
    ax.scatter(a, t, color=color, marker=marker, s=140, edgecolor='black')

ax.set_xlabel("α101 Angle (°)", fontsize=22)
ax.set_ylabel("τ101 Angle (°)", fontsize=22)

# --- Right panel for PDB codes ---
fig.subplots_adjust(right=0.75)
ax_labels = fig.add_axes([0.77, 0.1, 0.22, 0.8])
ax_labels.axis("off")

n = len(common_pdbs)
cols = 3
rows = int(np.ceil(n / cols))
marker_size = 22
text_fontsize = 8

for i, pdb in enumerate(common_pdbs):
    color, marker = point_styles[i]
    col = i % cols
    row = i // cols
    x_circle = 0.05 + col * 0.3
    x_text = 0.08 + col * 0.3
    y = 1 - (row + 1) / (rows + 1)

    # Draw marker
    ax_labels.scatter(x_circle, y, color=color, s=marker_size, marker=marker, edgecolor='black', transform=ax_labels.transAxes, zorder=2)

    # Black PDB text
    ax_labels.text(
        x_text, y, pdb.split(".pdb")[0],
        color='black', fontsize=text_fontsize,
        va='center', transform=ax_labels.transAxes
    )

ax.set_xlim(-200, 200)
ax.set_ylim(60, 150)

# --- Save PDF ---
plt.savefig("results/alpha101_tau101_plot.pdf", format="pdf", bbox_inches="tight")

print("Plot saved as alpha101_tau101_plot.pdf")

alpha_file = "results/alpha101_dihedral.txt"
tau_file   = "results/tau101_angle.txt"
output_file = "results/classification.txt"

def read_angle_file(filename):
    data = {}
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) < 3:
                continue

            pdb_full = parts[0]       
            angle_str = parts[2]     

            # Skip header or non-numeric
            try:
                angle = float(angle_str)
            except ValueError:
                continue

            # Remove only ".pdb" → keep chain
            pdb = os.path.basename(pdb_full).replace(".pdb", "")
            data[pdb] = angle

    return data


# Load angle data
alpha = read_angle_file(alpha_file)
tau = read_angle_file(tau_file)

# Write output with aligned columns
with open(output_file, "w") as out:

    # header row
    out.write(f"{'PDB':<10}{'alpha101':>12}{'tau101':>12}{'Conformation':>15}\n")

    for pdb in sorted(alpha.keys()):
        if pdb not in tau:
            continue

        a = alpha[pdb]
        t = tau[pdb]

        # Conformation rules
        kinked = (0 < a < 120) and (85 < t < 130)
        extended = (a < -100) and (100 < t < 145)

        if kinked:
            conf = "kinked"
        elif extended:
            conf = "extended"
        else:
            conf = "other"

        # aligned output
        out.write(f"{pdb:<10}{a:>12.3f}{t:>12.3f}{conf:>15}\n")

print(f"Written: {output_file}")

# --------------------------------------------------
# Sort full complexes into extended/kinked
# --------------------------------------------------

tau_file = "results/tau101_angle.txt"
alpha_file = "results/alpha101_dihedral.txt"
classification_file = "results/classification.txt"

os.makedirs("kinked", exist_ok=True)
os.makedirs("extended", exist_ok=True)
os.makedirs("other", exist_ok=True)

with open(classification_file) as f:
    next(f)  # skip header

    for line in f:
        if not line.strip():
            continue

        parts = line.split()

        pdb_chain = parts[0]      
        conf = parts[3].lower()

        source_pdb = os.path.join("results", f"{pdb_chain}.pdb")

        if not os.path.exists(source_pdb):
            print(f"Missing {source_pdb}")
            continue

        if conf == "kinked":
            dest_dir = "kinked"
        elif conf == "extended":
            dest_dir = "extended"
        else:
            dest_dir = "other"

        shutil.move(
            source_pdb,
            os.path.join(dest_dir, os.path.basename(source_pdb))
        )

        print(f"{pdb_chain} -> {dest_dir}")
           
print("Done.")

# ==================================================
# α97 / τ97 analysis for EXTENDED structures only
# ==================================================

extended_dir = "extended"

alpha97_file = "results/extended_alpha97_dihedral.txt"
tau97_file   = "results/extended_tau97_angle.txt"

pdb_files = sorted(glob.glob(os.path.join(extended_dir, "*.pdb")))

# --------------------------------------------------
# Alpha97
# --------------------------------------------------

with open(alpha97_file, "w") as f:

    f.write("# File\tAlpha97_dihedral(degrees)\n")

    for pdb in pdb_files:

        try:

            u = mda.Universe(pdb)

            atoms = []

            for resid in [95, 96, 97, 98]:

                ca = u.select_atoms(
                    f"resid {resid} and name CA"
                )

                if len(ca) != 1:
                    atoms = []
                    print(
                        f"Warning: {pdb} missing residue {resid}"
                    )
                    break

                atoms.append(ca.positions[0])

            if len(atoms) != 4:
                continue

            dih = calc_dihedrals(*atoms)
            dih_deg = np.degrees(dih)

            f.write(
                f"{os.path.basename(pdb)}\t{dih_deg:.3f}\n"
            )

        except Exception as e:

            print(f"Error processing {pdb}: {e}")

print(f"Written: {alpha97_file}")

# --------------------------------------------------
# Tau97
# --------------------------------------------------

with open(tau97_file, "w") as f:

    f.write("# File\tTau97_angle(degrees)\n")

    for pdb in pdb_files:

        try:

            u = mda.Universe(pdb)

            atoms = []

            for resid in [96, 97, 98]:

                ca = u.select_atoms(
                    f"resid {resid} and name CA"
                )

                if len(ca) != 1:
                    atoms = []
                    print(
                        f"Warning: {pdb} missing residue {resid}"
                    )
                    break

                atoms.append(ca.positions[0])

            if len(atoms) != 3:
                continue

            angle = calc_angles(*atoms)
            angle_deg = np.degrees(angle)

            f.write(
                f"{os.path.basename(pdb)}\t{angle_deg:.3f}\n"
            )

        except Exception as e:

            print(f"Error processing {pdb}: {e}")

print(f"Written: {tau97_file}")

# --------------------------------------------------
# Create α97 vs τ97 plot
# --------------------------------------------------

alpha_data = {}

with open(alpha97_file) as f:

    for line in f:

        if line.startswith("#") or not line.strip():
            continue

        parts = line.split()

        alpha_data[parts[0]] = float(parts[1])

tau_data = {}

with open(tau97_file) as f:

    for line in f:

        if line.startswith("#") or not line.strip():
            continue

        parts = line.split()

        tau_data[parts[0]] = float(parts[1])

common_pdbs = sorted(
    set(alpha_data.keys()) &
    set(tau_data.keys())
)

alpha_values = [
    alpha_data[pdb]
    for pdb in common_pdbs
]

tau_values = [
    tau_data[pdb]
    for pdb in common_pdbs
]

colors = plt.cm.tab20(
    np.linspace(0, 1, 20)
)

markers = [
    'o', 's', '^', 'v',
    'D', 'P', '*'
]

point_styles = []

for i in range(len(common_pdbs)):

    point_styles.append(
        (
            colors[i % len(colors)],
            markers[i % len(markers)]
        )
    )

fig, ax = plt.subplots(figsize=(10, 6))

for a, t, style in zip(
    alpha_values,
    tau_values,
    point_styles
):

    color, marker = style

    ax.scatter(
        a,
        t,
        color=color,
        marker=marker,
        s=140,
        edgecolor="black"
    )

ax.set_xlabel("α97 Angle (°)", fontsize=22)
ax.set_ylabel("τ97 Angle (°)", fontsize=22)

fig.subplots_adjust(right=0.75)

ax_labels = fig.add_axes(
    [0.77, 0.1, 0.22, 0.8]
)

ax_labels.axis("off")

n = len(common_pdbs)

cols = 2
rows = int(np.ceil(n / cols))

for i, pdb in enumerate(common_pdbs):

    color, marker = point_styles[i]

    col = i % cols
    row = i // cols

    x_circle = 0.05 + col * 0.30
    x_text = 0.08 + col * 0.30

    y = 1 - (row + 1) / (rows + 1)

    ax_labels.scatter(
        x_circle,
        y,
        color=color,
        marker=marker,
        s=22,
        edgecolor="black",
        transform=ax_labels.transAxes
    )

    ax_labels.text(
        x_text,
        y,
        pdb.replace(".pdb", ""),
        fontsize=8,
        va="center",
        color="black",
        transform=ax_labels.transAxes
    )

ax.set_xlim(-200, 200)
ax.set_ylim(60, 150)

pdf_file = "results/extended_alpha97_tau97_plot.pdf"

plt.savefig(
    pdf_file,
    format="pdf",
    bbox_inches="tight"
)

print(f"Plot saved as {pdf_file}")

# --------------------------------------------------
# Classify EXTENDED structures using tau97
# --------------------------------------------------

classification97_file = "results/extended_97_classification.txt"

with open(tau97_file) as fin, open(classification97_file, "w") as fout:

    fout.write(
        f"{'PDB':<15}{'tau97':>12}{'Class':>12}\n"
    )

    for line in fin:

        if line.startswith("#") or not line.strip():
            continue

        parts = line.split()

        pdb = parts[0]
        tau97 = float(parts[1])

        if tau97 < 100:
            shape = "concave"
        else:
            shape = "loop"

        fout.write(
            f"{pdb:<15}{tau97:>12.3f}{shape:>12}\n"
        )

print(f"Written: {classification97_file}")

os.makedirs("concave", exist_ok=True)
os.makedirs("loop", exist_ok=True)

with open(classification97_file) as f:

    next(f)

    for line in f:

        if not line.strip():
            continue

        pdb = line.split()[0]
        shape = line.split()[2]

        source = os.path.join(
            "extended",
            pdb
        )

        if not os.path.exists(source):
            continue

        if shape == "concave":
            dest = "concave"
        else:
            dest = "loop"

        shutil.copy(
            source,
            os.path.join(dest, pdb)
        )

print("Extended structures sorted into concave/loop")
