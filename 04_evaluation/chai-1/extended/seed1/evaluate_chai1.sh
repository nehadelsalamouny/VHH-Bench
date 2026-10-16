#!/bin/bash
###############################################################################
# Evaluate Chai-1 predictions with DockQ
# Requirements:
#   - DockQ
#   - MDAnalysis
#
# Output files:
#   output/all_DockQ_results.txt
#   output/DockQ_rank*.txt
#   output/iptm_rank*.txt
###############################################################################

########################################
# PART 1: RUN DockQ
########################################

mkdir -p output

output_file="output/all_DockQ_results.txt"

echo "DockQ results" > "$output_file"
echo "============================================" >> "$output_file"
echo "" >> "$output_file"

for d in */ ; do

    pdbcode="${d%/}"

    echo "Folder: $pdbcode" >> "$output_file"

    ref_pdb="../../../../01_dataset/${pdbcode}.pdb"

    if [[ ! -f "$ref_pdb" ]]; then
        echo "Reference missing: $ref_pdb" >> "$output_file"
        echo "" >> "$output_file"
        continue
    fi

    for i in 0 1 2 3 4
    do

        model_file="${d}/pred.model_idx_${i}.cif"

        [[ ! -f "$model_file" ]] && continue

        echo "Model: $model_file" >> "$output_file"

        DockQ "$model_file" "$ref_pdb" >> "$output_file" 2>&1

        echo "" >> "$output_file"

    done

    echo "--------------------------------------------" >> "$output_file"
    echo "" >> "$output_file"

done

########################################
# PART 2: PARSE DockQ RESULTS
########################################

input="output/all_DockQ_results.txt"

for rank in 0 1 2 3 4
do
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

while IFS= read -r line
do

    if [[ "$line" == Model:* ]]; then

        current_model="${line#Model: }"

        current_rank=$(echo "$current_model" | \
            sed -E 's/.*pred\.model_idx_([0-4])\.cif/\1/')

        dockq=""
        irmsd=""
        lrmsd=""
        fnat=""
        fnonnat=""

        continue
    fi

    [[ "$line" =~ DockQ:[[:space:]]*([0-9.]+) ]] \
        && dockq="${BASH_REMATCH[1]}"

    [[ "$line" =~ iRMSD:[[:space:]]*([0-9.]+) ]] \
        && irmsd="${BASH_REMATCH[1]}"

    [[ "$line" =~ LRMSD:[[:space:]]*([0-9.]+) ]] \
        && lrmsd="${BASH_REMATCH[1]}"

    [[ "$line" =~ fnat:[[:space:]]*([0-9.]+) ]] \
        && fnat="${BASH_REMATCH[1]}"

    [[ "$line" =~ fnonnat:[[:space:]]*([0-9.]+) ]] \
        && fnonnat="${BASH_REMATCH[1]}"

    if [[ -n "$current_model" && -n "$fnonnat" ]]; then

        echo -e "${current_model}\t${dockq}\t${irmsd}\t${lrmsd}\t${fnat}\t${fnonnat}" \
        >> "output/DockQ_rank${current_rank}.txt"

        current_model=""
        current_rank=""
    fi

done < "$input"

echo "Finished generating DockQ summaries."

########################################
# PART 3: EXTRACT CONFIDENCE SCORES
########################################

for rank in 0 1 2 3 4
do

    outfile="output/iptm_rank${rank}.txt"

    echo -e "Model_Folder\tptm\tiptm\taggregate_score" \
    > "$outfile"

    find . -type f -name "scores.rank_${rank}.json" | sort | \
    while read -r score_file
    do

        folder=$(dirname "$score_file")

        ptm=$(jq -r '.ptm // "NA"' "$score_file")
        iptm=$(jq -r '.iptm // "NA"' "$score_file")
        aggregate=$(jq -r '.aggregate_score // "NA"' "$score_file")

        echo -e "${folder}\t${ptm}\t${iptm}\t${aggregate}" \
        >> "$outfile"

    done

done

echo ""
echo "Pipeline completed."