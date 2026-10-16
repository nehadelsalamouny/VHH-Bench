#!/usr/bin/env python3

"""
Calculate CDR3 RMSD for Boltz2-predicted nanobody structures.

Inputs:
    ../boltz_*/
    ../../../../../02_classification/kinked/*.pdb

Output:
    cdr3_rmsd.txt

Output format:
    folder    structure    CDR3_RMSD

Requirements:
    - PyMOL
    - ANARCI
    - pdb-tools
"""

import os
import glob
import subprocess
from pymol import cmd

# ==================================================
# PATHS
# ==================================================

ROOT = os.getcwd()
START_DIR = ROOT

REFERENCE_DIR = (
    "../../../../../02_classification/kinked"
)

MASTER_FILE = os.path.join(
    ROOT,
    "cdr3_rmsd.txt"
)

with open(MASTER_FILE, "w") as f:
    f.write("folder\tstructure\tCDR3_RMSD\n")

folders = sorted(
    f for f in glob.glob(
        os.path.join(ROOT, "../boltz_*")
    )
    if os.path.isdir(f)
)

print(f"Found {len(folders)} fold folders")


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


for folder_path in folders:

    folder = os.path.basename(folder_path)

    print(f"\n=== {folder} ===")

    try:

        os.chdir(folder_path)

        # ==================================================
        # STEP 1: CIF -> PDB
        # ==================================================

        print("Converting CIF files")

        cif_files = glob.glob(
            "**/*.cif",
            recursive=True
        )

        for cif in cif_files:

            obj = (
                cif.replace("/", "_")
                .replace(".", "_")
            )

            try:

                cmd.load(cif, obj)

                atoms = cmd.count_atoms(obj)

                if atoms > 0:

                    pdb_out = cif.replace(
                        ".cif",
                        ".pdb"
                    )

                    cmd.save(
                        pdb_out,
                        obj
                    )

                cmd.delete(obj)

            except Exception as e:

                print(
                    f"Failed CIF conversion: "
                    f"{cif} ({e})"
                )

        # ==================================================
        # STEP 2: CHOTHIA RENUMBERING
        # ==================================================

        print("Renumbering")

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

        for pdb in pdb_files:

            base = os.path.splitext(pdb)[0]

            try:

                chains = subprocess.check_output(
                    f"grep '^ATOM' '{pdb}' "
                    "| cut -c22 | sort | uniq",
                    shell=True
                ).decode().split()

            except Exception:
                continue

            for chain in chains:

                chain_pdb = f"{base}_{chain}.pdb"

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

                seq = ""

                with open(fasta) as fh:

                    for line in fh:

                        if not line.startswith(">"):
                            seq += line.strip()

                # ------------------------------------------
                # Trim N-terminal tags
                # ------------------------------------------

                for motif in [
                    "QVQL",
                    "EVQL",
                    "DVQL"
                ]:

                    pos = seq.find(motif)

                    if pos != -1:

                        if pos > 0:

                            print(
                                f"Trimming N-terminal tag from "
                                f"{chain_pdb}"
                            )

                        seq = seq[pos:]
                        break

                # ------------------------------------------
                # Trim C-terminal linker / tail
                # ------------------------------------------

                for motif in [
                    "WGQGTQVTVSS",
                    "QGTQVTVSS"
                ]:

                    pos = seq.find(motif)

                    if pos != -1:

                        seq = (
                            seq[:pos + len(motif)]
                        )

                        print(
                            f"Trimming C-terminal tail from "
                            f"{chain_pdb}"
                        )

                        break

                with open(fasta, "w") as fh:
                    fh.write(">sequence\n")
                    fh.write(seq + "\n")

                if len(seq) < 90 or len(seq) > 140:

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

                                    resnum = parts[1]

                                    if len(parts) == 4:
                                        resnum += parts[2]

                                    mapping.append(resnum)

                except Exception:
                    continue

                if not mapping:

                    print(
                        "ANARCI failed:",
                        chain_pdb,
                        "length:",
                        len(seq)
                    )

                    continue

                out_pdb = chain_pdb.replace(
                    ".pdb",
                    "_chothia.pdb"
                )

                idx = 0
                current = None

                with open(chain_pdb) as fin, \
                     open(out_pdb, "w") as fout:

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

                for tmp in [
                    chain_pdb,
                    fasta,
                    anarci_out
                ]:
                    try:
                        os.remove(tmp)
                    except OSError:
                        pass

            try:
                os.remove(pdb)
            except OSError:
                pass

        # ==================================================
        # STEP 3: RMSD
        # ==================================================

        print("Calculating RMSD")

        cdr3_sel = (
            "resi 95-102+100A+100B+100C+"
            "100D+100E+100F+100G+100H"
        )

        structures = glob.glob(
            "predictions/**/*_chothia.pdb",
            recursive=True
        )

        for pdb in structures:

            pdb_id = (
                os.path.basename(pdb)[:4]
                .lower()
            )

            all_refs = glob.glob(
                os.path.join(
                    REFERENCE_DIR,
                    "*.pdb"
                )
            )

            refs = [
                r
                for r in all_refs
                if os.path.basename(r)
                .lower()
                .startswith(pdb_id)
            ]

            if not refs:

                with open(MASTER_FILE, "a") as f:
                    f.write(
                        f"{folder}\t"
                        f"{os.path.basename(pdb)}\t"
                        f"NaN\n"
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

                    with open(MASTER_FILE, "a") as f:
                        f.write(
                            f"{folder}\t"
                            f"{os.path.basename(pdb)}\t"
                            f"NaN\n"
                        )

                    continue

                cmd.super(
                    f"mob and chain {mob_chain} and name CA",
                    f"ref and chain {ref_chain} and name CA"
                )

                rmsd = cmd.align(
                    f"mob and chain {mob_chain} "
                    f"and name CA and ({cdr3_sel})",
                    f"ref and chain {ref_chain} "
                    f"and name CA and ({cdr3_sel})"
                )[0]

                with open(MASTER_FILE, "a") as f:
                    f.write(
                        f"{folder}\t"
                        f"{os.path.basename(pdb)}\t"
                        f"{rmsd:.3f}\n"
                    )

            except Exception:

                with open(MASTER_FILE, "a") as f:
                    f.write(
                        f"{folder}\t"
                        f"{os.path.basename(pdb)}\t"
                        f"NaN\n"
                    )

        # ==================================================
        # FINAL CLEANUP
        # ==================================================

        print("Cleaning intermediate files")

        for root, dirs, files in os.walk("."):

            for file in files:

                path = os.path.join(
                    root,
                    file
                )

                if file.endswith("_chothia.pdb"):
                    continue

                if file.endswith(".cif"):
                    continue

                if file.endswith(".json"):
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

    except Exception as e:

        print(f"FAILED: {folder}")
        print(e)

    finally:

        os.chdir(START_DIR)

print(f"\nResults written to: {MASTER_FILE}")