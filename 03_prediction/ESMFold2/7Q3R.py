import csv
from esm.models.esmfold2 import (
    ESMFold2InputBuilder,
    ProteinInput,
    StructurePredictionInput,
)
from transformers.models.esmfold2.modeling_esmfold2 import ESMFold2Model

# --- sequences ---
SEQ_A = (
    "AMAEVQLVESGGGLVQAGGSLRLSCAASGRAFSRYFMGWFRQAPGKEREFVAGISRSGGSTDYANFVKGRFTISRDNAKNTVYLQMNSLKPEDTAVYYCAATVDYSGTLTAARGREDYDDWGQGIQVTVSSAAAHHHHHHHH"
)

SEQ_B = (
    "NITNLCPFGEVFNATRFASVYAWNRKRISNCVADYSFLYNSASFSTFKCYGVSPTKLNDLCFTNVYADSFVIRGDEVRQIAPGQTGKIADYNYKLPDDFTGCVIAWNSNNLDSKVGGNYNYLYRLFRKSNLKPFERDISTEIYQAGSTPCNGVEGFNCYFPLQSYGFQPTNGVGYQPYRVVVLSFELLHAPATVCGPK"
)


# --- load model ---
model = ESMFold2Model.from_pretrained("biohub/ESMFold2").cuda().eval()

# --- build input ---
spi = StructurePredictionInput(
    sequences=[
        ProteinInput(id="A", sequence=SEQ_A),
        ProteinInput(id="B", sequence=SEQ_B),
    ]
)

# --- config ---
seeds = [0, 1, 2, 3, 4]
num_samples = 5  # models per seed

results = []

# --- run ---
for seed in seeds:
    print(f"\nRunning seed {seed}...")

    result = ESMFold2InputBuilder().fold(
        model,
        spi,
        num_loops=10,
        num_sampling_steps=200,
        num_diffusion_samples=num_samples,
        seed=seed,
    )

    for i, sample in enumerate(result):
        ptm = float(sample.ptm)
        iptm = float(sample.iptm)
        plddt = float(sample.plddt.mean())

        results.append({
            "seed": seed,
            "sample": i,
            "pTM": ptm,
            "ipTM": iptm,
            "pLDDT_mean": plddt,
        })

        print(
            f"Seed {seed} | Sample {i} | "
            f"pTM={ptm:.3f}, ipTM={iptm:.3f}, pLDDT={plddt:.3f}"
        )

        # optional: save structure
        with open(f"model_seed{seed}_sample{i}.cif", "w") as f:
            f.write(sample.complex.to_mmcif())

with open("results_scores.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["seed", "sample", "pTM", "ipTM", "pLDDT_mean"])
    writer.writeheader()
    writer.writerows(results)

print("All runs completed. Results saved to results_scores.csv")

