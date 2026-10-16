#!/bin/bash

# ============================================================
# Calculate DockQ scores and extract AF3 confidence metrics
# Requirements:
#   - DockQ
#   - MDAnalysis
#
# Outputs:
#   output/all_DockQ.txt
#   output/DockQ_rank0.txt - output/DockQ_rank4.txt
#   output/iptm_rank0.txt  - output/iptm_rank4.txt
# ============================================================

mkdir -p output

# ============================================================
# Part 1. Run DockQ
# ============================================================

output_file="output/all_DockQ.txt"

{
    echo "DockQ results"
    echo "============================================"
    echo
} > "$output_file"

for d in */; do

    cd "$d" || continue

    echo "Folder: $d" >> "../$output_file"

    for i in {0..4}; do

        model_file=$(ls *"_model_${i}.cif" 2>/dev/null | head -n 1)

        [[ -z "$model_file" ]] && continue

        pdbcode=$(basename "$PWD" | awk -F'_' '{print $NF}')
        ref_pdb="../../../../../01_dataset/${pdbcode}.pdb"

        [[ ! -f "$ref_pdb" ]] && continue

        echo "Running DockQ for: $model_file" >> "../$output_file"

        DockQ "$model_file" "$ref_pdb" >> "../$output_file"

        echo >> "../$output_file"

    done

    cd ..

done

# ============================================================
# Part 2. Parse DockQ results
# ============================================================

input_file="output/all_DockQ.txt"

for rank in {0..4}; do

    output_files[$rank]="output/DockQ_rank${rank}.txt"

    echo -e "Model\tDockQ\tiRMSD\tLRMSD\tfnat\tfnonnat" \
        > "${output_files[$rank]}"

done

current_model=""
current_rank=""
dockq=""
irmsd=""
lrmsd=""
fnat=""
fnonnat=""

while IFS= read -r line; do

    if [[ "$line" =~ Running\ DockQ\ for:\ ([A-Za-z0-9._-]+_model_([0-4])\.cif) ]]; then

        current_model="${BASH_REMATCH[1]}"
        current_rank="${BASH_REMATCH[2]}"

        dockq=""
        irmsd=""
        lrmsd=""
        fnat=""
        fnonnat=""

        continue
    fi

    if [[ -n "$current_model" ]]; then

        [[ "$line" =~ ^[[:space:]]*DockQ:[[:space:]]*([0-9.]+) ]] \
            && dockq="${BASH_REMATCH[1]}"

        [[ "$line" =~ ^[[:space:]]*iRMSD:[[:space:]]*([0-9.]+) ]] \
            && irmsd="${BASH_REMATCH[1]}"

        [[ "$line" =~ ^[[:space:]]*LRMSD:[[:space:]]*([0-9.]+) ]] \
            && lrmsd="${BASH_REMATCH[1]}"

        [[ "$line" =~ ^[[:space:]]*fnat:[[:space:]]*([0-9.]+) ]] \
            && fnat="${BASH_REMATCH[1]}"

        [[ "$line" =~ ^[[:space:]]*fnonnat:[[:space:]]*([0-9.]+) ]] \
            && fnonnat="${BASH_REMATCH[1]}"

        if [[ -n "$fnonnat" ]]; then

            echo -e \
                "${current_model}\t${dockq}\t${irmsd}\t${lrmsd}\t${fnat}\t${fnonnat}" \
                >> "${output_files[$current_rank]}"

            current_model=""
            current_rank=""
            dockq=""
            irmsd=""
            lrmsd=""
            fnat=""
            fnonnat=""

        fi
    fi

done < "$input_file"

echo "Finished generating DockQ summary files."

# ============================================================
# Part 3. Extract AF3 confidence scores
# ============================================================

for rank in {0..4}; do

    outfile="output/iptm_rank${rank}.txt"

    echo -e "Model\tptm\tiptm\tranking_score" > "$outfile"

    find . -name "*_model_${rank}.cif" | while read -r model; do

        json_file=$(echo "$model" | \
            sed "s/_model_${rank}\.cif/_summary_confidences_${rank}.json/")

        if [[ ! -f "$json_file" ]]; then
            echo "Warning: JSON file not found for $model"
            continue
        fi

        ptm=$(jq -r '.pTMscore // .ptm // "NA"' "$json_file")
        iptm=$(jq -r '.ipTM // .iptm // "NA"' "$json_file")
        ranking=$(jq -r '.ranking_score // "NA"' "$json_file")

        echo -e \
            "${model}\t${ptm}\t${iptm}\t${ranking}" \
            >> "$outfile"

    done

done

echo "Finished generating iptm_rank0.txt through iptm_rank4.txt"
echo "Pipeline completed."