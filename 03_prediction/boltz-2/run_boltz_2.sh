#!/bin/bash

for i in *.fasta; do
boltz predict "$i" --diffusion_samples 5 --use_msa_server;
done
