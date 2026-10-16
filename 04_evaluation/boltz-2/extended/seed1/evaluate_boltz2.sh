#!/bin/bash

########################################
# Evaluate Boltz-2 predictions with DockQ
# Requirements:
#   - DockQ
#   - MDAnalysis
#  
# Inputs:
#   boltz_results_*/
#   ../../../../01_dataset/*.pdb
#
# Outputs:
#   output/all_DockQ.txt
#   output/DockQ_rank*.txt
#   output/iptm_rank*.txt
########################################

mkdir -p output

########################################
# PART 1: Run DockQ
########################################

output_file="output/all_DockQ.txt"

{
    echo "DockQ results"
    echo "============================================"
    echo
} > "$output_file"

for folder in boltz_results_*; do

    [[ -d "$folder" ]] || continue

    pdb_code="${folder#boltz_results_}"
    prediction_dir="$folder/predictions/$pdb_code"

    [[ -d "$prediction_dir" ]] || continue

    pdb_base="${pdb_code%%_*}"
    pdb_base=$(echo "$pdb_base" | tr '[:upper:]' '[:lower:]')

    reference_pdb="../../../../01_dataset/${pdb_base}.pdb"

    [[ -f "$reference_pdb" ]] || continue

    echo "Folder: $folder" >> "$output_file"

    for rank in {0..4}; do

        model_file="${prediction_dir}/${pdb_code}_model_${rank}.cif"

        [[ -f "$model_file" ]] || continue

        echo "Running DockQ for: $model_file" >> "$output_file"

        DockQ \
            "$model_file" \
            "$reference_pdb" \
            >> "$output_file" 2>&1

        echo >> "$output_file"

    done

done

########################################
# PART 2: Parse DockQ output
########################################

input_file="output/all_DockQ.txt"

for rank in {0..4}; do
    echo -e "Model\tDockQ\tiRMSD\tLRMSD\tfnat\tfnonnat" \
        > "output/DockQ_rank${rank}.txt"
done

current_model=""
current_rank=""
dockq=""
irmsd=""
lrmsd=""
fnat=""
fnonnat=""

while IFS= read -r line; do

    if [[ "$line" == Running\ DockQ\ for:* ]]; then

        current_model="${line#Running DockQ for: }"

        current_rank=$(
            echo "$current_model" |
            sed -E 's/.*_model_([0-4])\.cif/\1/'
        )

        dockq=""
        irmsd=""
        lrmsd=""
        fnat=""
        fnonnat=""

        continue
    fi

    [[ "$line" =~ ^[[:space:]]*DockQ:[[:space:]]*([0-9.]+) ]] &&
        dockq="${BASH_REMATCH[1]}"

    [[ "$line" =~ ^[[:space:]]*iRMSD:[[:space:]]*([0-9.]+) ]] &&
        irmsd="${BASH_REMATCH[1]}"

    [[ "$line" =~ ^[[:space:]]*LRMSD:[[:space:]]*([0-9.]+) ]] &&
        lrmsd="${BASH_REMATCH[1]}"

    [[ "$line" =~ ^[[:space:]]*fnat:[[:space:]]*([0-9.]+) ]] &&
        fnat="${BASH_REMATCH[1]}"

    [[ "$line" =~ ^[[:space:]]*fnonnat:[[:space:]]*([0-9.]+) ]] &&
        fnonnat="${BASH_REMATCH[1]}"

    if [[ -n "$current_model" && -n "$fnonnat" ]]; then

        echo -e \
"${current_model}\t${dockq}\t${irmsd}\t${lrmsd}\t${fnat}\t${fnonnat}" \
>> "output/DockQ_rank${current_rank}.txt"

        current_model=""
        current_rank=""
        dockq=""
        irmsd=""
        lrmsd=""
        fnat=""
        fnonnat=""

    fi

done < "$input_file"

echo "Finished generating DockQ summaries"

########################################
# PART 3: Extract Boltz confidence scores
########################################

for rank in {0..4}; do

    outfile="output/iptm_rank${rank}.txt"

    echo -e "Model\tpTM\tipTM\tconfidence_score" \
        > "$outfile"

    find boltz_results_* \
        -name "confidence_*_model_${rank}.json" |
        sort |
        while read -r json_file
    do

        model_name=$(basename "$json_file" .json)

        ptm=$(jq -r \
            '.pTM // .ptm // .pTMscore // "NA"' \
            "$json_file")

        iptm=$(jq -r \
            '.ipTM // .iptm // "NA"' \
            "$json_file")

        confidence=$(jq -r \
            '.confidence_score // "NA"' \
            "$json_file")

        echo -e \
"${model_name}\t${ptm}\t${iptm}\t${confidence}" \
>> "$outfile"

    done

done

echo "Finished extracting confidence scores"