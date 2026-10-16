#!/usr/bin/env python3

"""
Convert AlphaFold3 predictions to Chothia numbering and calculate
CDR3 RMSD relative to reference nanobody structures.

Requirements:
    - PyMOL
    - ANARCI
    - pdb-tools

Outputs:
    - cdr3_rmsd.txt
    - *_chothia.pdb
"""

import glob
import os
import re
import subprocess

from pymol import cmd

# ==========================================
# Settings
# ==========================================

ROOT = os.getcwd()
MASTER_FILE = os.path.join(ROOT, "cdr3_rmsd.txt")

DEBUG = False

# ==========================================
# Helper functions
# ==========================================

def run_command(command):
    """Run shell command."""
    subprocess.run(command, shell=True, check=True)


def pick_main_chain(obj):
    """Return chain containing the most CA atoms."""

    chains = cmd.get_chains(obj)

    best_chain = None
    max_ca = 0

    for chain in chains:

        n_ca = cmd.count_atoms(
            f"{obj} and chain {chain} and name CA"
        )

        if n_ca > max_ca:
            max_ca = n_ca
            best_chain = chain

    return best_chain


# ==========================================
# Initialise output file
# ==========================================

with open(MASTER_FILE, "w") as handle:
    handle.write("folder\tstructure\tCDR3_RMSD\n")

folders = sorted(
    folder
    for folder in glob.glob(os.path.join(ROOT, "../fold_*"))
    if os.path.isdir(folder)
)

print(f"Found {len(folders)} fold folders")

# ==========================================
# Process folders
# ==========================================

for folder_path in folders:

    folder = os.path.basename(folder_path)

    print(f"\n=== {folder} ===")

    try:

        os.chdir(folder_path)

        # ==========================================
        # Step 1. Convert CIF to PDB
        # ==========================================

        print("Converting CIF files")

        cif_files = glob.glob(
            "**/*.cif",
            recursive=True
        )

        for cif_file in cif_files:

            obj = (
                cif_file
                .replace("/", "_")
                .replace(".", "_")
            )

            try:

                cmd.load(cif_file, obj)

                if cmd.count_atoms(obj) > 0:

                    pdb_out = cif_file.replace(
                        ".cif",
                        ".pdb"
                    )

                    cmd.save(pdb_out, obj)

                cmd.delete(obj)

            except Exception as error:

                print(
                    f"Failed CIF conversion: "
                    f"{cif_file} ({error})"
                )

        # ==========================================
        # Step 2. Chothia renumbering
        # ==========================================

        print("Renumbering structures")

        pdb_files = []

        for root, _, files in os.walk("."):

            for file in files:

                if (
                    file.endswith(".pdb")
                    and "_chothia" not in file
                ):
                    pdb_files.append(
                        os.path.join(root, file)
                    )

        for pdb_file in pdb_files:

            base = os.path.splitext(pdb_file)[0]

            try:

                chains = (
                    subprocess.check_output(
                        f"grep '^ATOM' '{pdb_file}' "
                        "| cut -c22 | sort | uniq",
                        shell=True
                    )
                    .decode()
                    .split()
                )

            except Exception:
                continue

            for chain in chains:

                chain_pdb = f"{base}_{chain}.pdb"

                run_command(
                    f"awk "
                    f"'length($0)>21 && "
                    f"substr($0,22,1)==\"{chain}\"' "
                    f"'{pdb_file}' > '{chain_pdb}'"
                )

                fasta_file = chain_pdb.replace(
                    ".pdb",
                    ".fasta"
                )

                run_command(
                    f"python -m pdbtools.pdb_tofasta "
                    f"'{chain_pdb}' > '{fasta_file}'"
                )

                sequence = ""

                with open(fasta_file) as handle:

                    for line in handle:

                        if not line.startswith(">"):
                            sequence += line.strip()

                # Remove N-terminal tags
                for motif in ["QVQL", "EVQL", "DVQL"]:

                    pos = sequence.find(motif)

                    if pos != -1:

                        sequence = sequence[pos:]
                        break

                # Remove C-terminal linker/tail
                for motif in [
                    "WGQGTQVTVSS",
                    "QGTQVTVSS"
                ]:

                    pos = sequence.find(motif)

                    if pos != -1:

                        sequence = sequence[:pos + len(motif)]
                        break

                with open(fasta_file, "w") as handle:

                    handle.write(">sequence\n")
                    handle.write(sequence + "\n")

                if not 90 <= len(sequence) <= 140:

                    for temp in [chain_pdb, fasta_file]:

                        try:
                            os.remove(temp)
                        except OSError:
                            pass

                    continue

                anarci_file = fasta_file.replace(
                    ".fasta",
                    ".anarci"
                )

                try:

                    run_command(
                        f"ANARCI "
                        f"-i '{fasta_file}' "
                        f"-s chothia "
                        f"-o '{anarci_file}' "
                        f"> /dev/null 2>&1"
                    )

                except Exception:
                    continue

                mapping = []

                try:

                    with open(anarci_file) as handle:

                        for line in handle:

                            if line.startswith("H "):

                                parts = line.split()

                                if len(parts) >= 3:

                                    residue = parts[1]

                                    if len(parts) == 4:
                                        residue += parts[2]

                                    mapping.append(residue)

                except Exception:
                    continue

                if not mapping:
                    continue

                output_pdb = chain_pdb.replace(
                    ".pdb",
                    "_chothia.pdb"
                )

                idx = 0
                current = None

                with open(chain_pdb) as fin, \
                        open(output_pdb, "w") as fout:

                    for line in fin:

                        if not line.startswith("ATOM"):
                            fout.write(line)
                            continue

                        residue = line[22:26]

                        if residue != current:

                            current = residue

                            if idx < len(mapping):
                                new_id = mapping[idx]
                            else:
                                new_id = "999"

                            idx += 1

                        number = "".join(
                            filter(str.isdigit, new_id)
                        )

                        insertion = "".join(
                            filter(str.isalpha, new_id)
                        ) or " "

                        fout.write(
                            line[:22]
                            + f"{int(number):4d}"
                            + insertion
                            + line[27:]
                        )

                for temp in [
                    chain_pdb,
                    fasta_file,
                    anarci_file
                ]:
                    try:
                        os.remove(temp)
                    except OSError:
                        pass

            try:
                os.remove(pdb_file)
            except OSError:
                pass

        # ==========================================
        # Step 3. Calculate CDR3 RMSD
        # ==========================================

        print("Calculating RMSD")

        cdr3_selection = (
            "resi 95-102+100A+100B+100C+"
            "100D+100E+100F+100G+100H"
        )

        structures = glob.glob(
            "*_chothia.pdb",
            recursive=True
        )

        for pdb_file in structures:

            match = re.search(
                r"_([0-9A-Za-z]{4})_model_",
                os.path.basename(pdb_file),
                re.IGNORECASE
            )

            if not match:
                continue

            pdb_id = match.group(1).lower()

            refs = glob.glob(
                f"../../../../../02_classification/"
                f"extended/{pdb_id}_*.pdb"
            )

            if not refs:

                with open(MASTER_FILE, "a") as handle:
                    handle.write(
                        f"{folder}\t"
                        f"{os.path.basename(pdb_file)}\tNaN\n"
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
                cmd.load(pdb_file, "mob")

                ref_chain = pick_main_chain("ref")
                mob_chain = pick_main_chain("mob")

                if (
                    ref_chain is None
                    or mob_chain is None
                ):
                    raise ValueError

                cmd.super(
                    f"mob and chain {mob_chain} and name CA",
                    f"ref and chain {ref_chain} and name CA"
                )

                rmsd = cmd.align(
                    f"mob and chain {mob_chain} "
                    f"and name CA and ({cdr3_selection})",
                    f"ref and chain {ref_chain} "
                    f"and name CA and ({cdr3_selection})"
                )[0]

                with open(MASTER_FILE, "a") as handle:
                    handle.write(
                        f"{folder}\t"
                        f"{os.path.basename(pdb_file)}\t"
                        f"{rmsd:.3f}\n"
                    )

            except Exception:

                with open(MASTER_FILE, "a") as handle:
                    handle.write(
                        f"{folder}\t"
                        f"{os.path.basename(pdb_file)}\tNaN\n"
                    )

        # ==========================================
        # Cleanup
        # ==========================================

        print("Cleaning intermediate files")

        for root, _, files in os.walk("."):

            for file in files:

                path = os.path.join(root, file)

                if file.endswith("_chothia.pdb"):
                    continue

                if (
                    file.endswith(".cif")
                    or file.endswith(".json")
                ):
                    continue

                if file == "rmsd_cdr3.txt":
                    continue

                if (
                    file.endswith(".fasta")
                    or file.endswith(".anarci")
                    or file.endswith(".pdb")
                ):
                    try:
                        os.remove(path)
                    except OSError:
                        pass

        print("Done")

    except Exception as error:

        print(f"FAILED: {folder}")
        print(error)

    finally:

        os.chdir(ROOT)

print("\nAll folders processed.")