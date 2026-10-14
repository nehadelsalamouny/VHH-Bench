import os
import time
import requests
from Bio import SeqIO
from io import StringIO

# Input and output directories
pdb_dir = "../01_dataset"
fasta_dir = "fasta"

# Create output directory 
os.makedirs(fasta_dir, exist_ok=True)

# Get PDB IDs from .pdb filenames
pdb_ids = [
    os.path.splitext(f)[0].upper()
    for f in os.listdir(pdb_dir)
    if f.lower().endswith(".pdb")
]

print(f"Found {len(pdb_ids)} PDB files.")

failed = []

for pdb_id in sorted(pdb_ids):
    url = f"https://www.rcsb.org/fasta/entry/{pdb_id}"

    try:
        response = requests.get(url, timeout=10)

        if response.ok:
            fasta_file = os.path.join(fasta_dir, f"{pdb_id}.fasta")

            with open(fasta_file, "w") as f:
                f.write(response.text)

            print(f"Saved {pdb_id}.fasta")

        else:
            failed.append(pdb_id)
            print(f"Failed: {pdb_id} (HTTP {response.status_code})")

    except Exception as e:
        failed.append(pdb_id)
        print(f"Error for {pdb_id}: {e}")

    time.sleep(0.1)

print("\nDone.")

if failed:
    print(f"\nFailed PDB IDs ({len(failed)}):")
    print("\n".join(failed))