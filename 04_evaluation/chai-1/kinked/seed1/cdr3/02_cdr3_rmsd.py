#!/usr/bin/env python3

"""
Calculate CDR3 RMSD values for predicted nanobody structures.

Requirements:
    - PyMOL
    - ANARCI
    - pdb-tools

Inputs:
    - Predicted structure files (*.cif)
    - Reference nanobody structures (*.pdb)

Output:
    - cdr3_rmsd.txt
"""

import os
import glob
import subprocess
from pymol import cmd

# ==========================================
# SETUP
# ==========================================

ROOT = os.getcwd()
START_DIR = ROOT

MASTER_FILE = os.path.join(
    ROOT,
    "cdr3_rmsd.txt"
)

with open(MASTER_FILE, "w") as f:
    f.write("folder\tstructure\tCDR3_RMSD\n")

# ==========================================
# CONVERT CIF TO PDB
# ==========================================

cif_files = glob.glob(
    "../**/pred.model_*.cif",
    recursive=True
)

for file in cif_files:

    obj = (
        file
        .replace("/", "_")
        .replace(".", "_")
    )

    try:

        cmd.load(file, obj)

        atoms = cmd.count_atoms(obj)

        if atoms == 0:

            print(f"Empty structure: {file}")

        else:

            output_pdb = file.replace(
                ".cif",
                ".pdb"
            )

            cmd.save(
                output_pdb,
                obj
            )

            print(
                f"Converted: {file} "
                f"-> {output_pdb} "
                f"({atoms} atoms)"
            )

        cmd.delete(obj)

    except Exception as e:

        print(
            f"Failed conversion: "
            f"{file} -> {e}"
        )

# ==========================================
# FIND TARGET FOLDERS
# ==========================================

folders = sorted(
    folder
    for folder in glob.glob("../*")
    if os.path.isdir(folder)
)

print(
    f"Found {len(folders)} target folders"
)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def run(command):
    subprocess.run(
        command,
        shell=True,
        check=True
    )

def pick_main_chain(obj):

    chains = cmd.get_chains(obj)

    best_chain = None
    max_ca = 0

    for chain in chains:

        count = cmd.count_atoms(
            f"{obj} and chain {chain} and name CA"
        )

        if count > max_ca:
            max_ca = count
            best_chain = chain

    return best_chain

# ==========================================
# PROCESS STRUCTURES
# ==========================================

for folder_path in folders:

    folder = os.path.basename(
        folder_path
    )

    print(f"\n=== {folder} ===")

    try:

        os.chdir(folder_path)

        # ==================================
        # STEP 1: CHOTHIA RENUMBERING
        # ==================================

        print(
            "Renumbering structures using Chothia numbering"
        )

        pdb_files = sorted(
            glob.glob(
                "pred.model_*.pdb"
            )
        )

        for pdb in pdb_files:

            base = os.path.splitext(
                pdb
            )[0]

            try:

                chains = (
                    subprocess.check_output(
                        f"grep '^ATOM' '{pdb}' "
                        "| cut -c22 | sort | uniq",
                        shell=True
                    )
                    .decode()
                    .split()
                )

            except Exception:
                continue

            for chain in chains:

                chain_pdb = (
                    f"{base}_{chain}.pdb"
                )

                run(
                    f"awk "
                    f"'length($0)>21 && "
                    f"substr($0,22,1)==\"{chain}\"' "
                    f"'{pdb}' > '{chain_pdb}'"
                )

                fasta = chain_pdb.replace(
                    ".pdb",
                    ".fasta"
                )

                run(
                    f"python -m pdbtools.pdb_tofasta "
                    f"'{chain_pdb}' > '{fasta}'"
                )

                sequence = ""

                with open(fasta) as fh:

                    for line in fh:

                        if not line.startswith(">"):
                            sequence += line.strip()

                # --------------------------
                # Trim N-terminal tags
                # --------------------------

                for motif in [
                    "QVQL",
                    "EVQL",
                    "DVQL"
                ]:

                    pos = sequence.find(motif)

                    if pos != -1:

                        if pos > 0:

                            print(
                                f"Trimming N-terminal tag "
                                f"from {chain_pdb}"
                            )

                        sequence = sequence[pos:]
                        break

                # --------------------------
                # Trim C-terminal tails
                # --------------------------

                for motif in [
                    "WGQGTQVTVSS",
                    "QGTQVTVSS"
                ]:

                    pos = sequence.find(motif)

                    if pos != -1:

                        sequence = (
                            sequence[
                                : pos + len(motif)
                            ]
                        )

                        print(
                            f"Trimming C-terminal tail "
                            f"from {chain_pdb}"
                        )

                        break

                with open(fasta, "w") as fh:

                    fh.write(">sequence\n")
                    fh.write(sequence + "\n")

                length = len(sequence)

                if length < 90 or length > 140:

                    try:
                        os.remove(chain_pdb)
                        os.remove(fasta)
                    except OSError:
                        pass

                    continue

                anarci_out = fasta.replace(
                    ".fasta",
                    ".anarci"
                )

                try:

                    run(
                        f"ANARCI "
                        f"-i '{fasta}' "
                        f"-s chothia "
                        f"-o '{anarci_out}' "
                        f"> /dev/null 2>&1"
                    )

                except Exception:
                    continue

                mapping = []

                try:

                    with open(anarci_out) as fh:

                        for line in fh:

                            if line.startswith("H "):

                                parts = line.split()

                                if len(parts) >= 3:

                                    residue = parts[1]

                                    if len(parts) == 4:
                                        residue += parts[2]

                                    mapping.append(
                                        residue
                                    )

                except Exception:
                    continue

                if not mapping:

                    print(
                        "ANARCI failed:",
                        chain_pdb,
                        "length:",
                        len(sequence)
                    )

                    continue

                out_pdb = chain_pdb.replace(
                    ".pdb",
                    "_chothia.pdb"
                )

                index = 0
                current_residue = None

                with open(chain_pdb) as fin, \
                     open(out_pdb, "w") as fout:

                    for line in fin:

                        if not line.startswith("ATOM"):

                            fout.write(line)
                            continue

                        residue = line[22:26]

                        if residue != current_residue:

                            current_residue = residue

                            if index < len(mapping):
                                new_id = mapping[index]
                            else:
                                new_id = "999"

                            index += 1

                        num = "".join(
                            filter(
                                str.isdigit,
                                new_id
                            )
                        )

                        ins = "".join(
                            filter(
                                str.isalpha,
                                new_id
                            )
                        ) or " "

                        fout.write(
                            line[:22]
                            + f"{int(num):4d}"
                            + ins
                            + line[27:]
                        )

                for temp in [
                    chain_pdb,
                    fasta,
                    anarci_out
                ]:

                    try:
                        os.remove(temp)
                    except OSError:
                        pass

        # ==================================
        # STEP 2: CDR3 RMSD
        # ==================================

        print(
            "Calculating CDR3 RMSD"
        )

        cdr3_selection = (
            "resi 95-102+100A+100B+100C+"
            "100D+100E+100F+100G+100H"
        )

        structures = sorted(
            glob.glob("*_chothia.pdb")
        )

        pdb_id = folder.lower()

        for pdb in structures:

            print("FILE:", pdb)
            print("PDB ID:", pdb_id)

            all_refs = glob.glob(
                "../../../../../02_classification/kinked/*.pdb"
            )

            refs = [
                ref
                for ref in all_refs
                if os.path.basename(ref)
                .lower()
                .startswith(pdb_id)
            ]

            print("REFS:", refs)

            if not refs:

                with open(
                    MASTER_FILE,
                    "a"
                ) as f:

                    f.write(
                        f"{folder}\t"
                        f"{os.path.basename(pdb)}\t"
                        "NaN\n"
                    )

                continue

            ref = next(
                (
                    x for x in refs
                    if x.endswith("_C.pdb")
                ),
                refs[0]
            )

            cmd.delete("all")

            try:

                cmd.load(ref, "ref")
                cmd.load(pdb, "mob")

                ref_chain = pick_main_chain("ref")
                mob_chain = pick_main_chain("mob")

                if (
                    ref_chain is None
                    or mob_chain is None
                ):

                    with open(
                        MASTER_FILE,
                        "a"
                    ) as f:

                        f.write(
                            f"{folder}\t"
                            f"{os.path.basename(pdb)}\t"
                            "NaN\n"
                        )

                    continue

                cmd.super(
                    f"mob and chain {mob_chain} and name CA",
                    f"ref and chain {ref_chain} and name CA"
                )

                rmsd = cmd.align(
                    f"mob and chain {mob_chain} "
                    f"and name CA and "
                    f"({cdr3_selection})",
                    f"ref and chain {ref_chain} "
                    f"and name CA and "
                    f"({cdr3_selection})"
                )[0]

                with open(
                    MASTER_FILE,
                    "a"
                ) as f:

                    f.write(
                        f"{folder}\t"
                        f"{os.path.basename(pdb)}\t"
                        f"{rmsd:.3f}\n"
                    )

            except Exception:

                with open(
                    MASTER_FILE,
                    "a"
                ) as f:

                    f.write(
                        f"{folder}\t"
                        f"{os.path.basename(pdb)}\t"
                        "NaN\n"
                    )

        # ==================================
        # CLEANUP
        # ==================================

        print(
            "Cleaning intermediate files"
        )

        for root, dirs, files in os.walk("."):

            for file in files:

                path = os.path.join(
                    root,
                    file
                )

                if file.endswith("_chothia.pdb"):
                    continue

                if (
                    file.startswith("pred.rank_")
                    and file.endswith(".pdb")
                ):
                    continue

                if file.endswith(".json"):
                    continue

                if file.endswith(".npy"):
                    continue

                if file.endswith(".pdf"):
                    continue

                if (
                    file.endswith(".fasta")
                    or file.endswith(".anarci")
                ):

                    try:
                        os.remove(path)
                    except OSError:
                        pass

        print("Done")

    except Exception as e:

        print(f"FAILED: {folder}")
        print(e)

    finally:

        os.chdir(START_DIR)

# ==========================================
# FINISHED
# ==========================================

print("\nALL DONE")