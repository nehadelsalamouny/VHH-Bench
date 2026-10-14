#!/bin/bash

for i in *.fasta; do
    name=$(basename "$i" .fasta)
    mkdir -p "$name"
    chai-lab fold "$i" --use-msa-server --use-templates-server "$name"
done
