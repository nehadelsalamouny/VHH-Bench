#!/usr/bin/env bash

########################################
# DockQ Evaluation Pipeline
#
# Requirements:
#   - DockQ
#   - MDAnalysis
#
# Outputs:
#   output/DockQ_seed*_rank*.txt
#   output/iptm_seed*_rank*.txt
########################################

mkdir -p output

########################################
# PART 1: RUN DockQ
########################################

dockq_raw="output/DockQ_results.txt"

echo "DockQ results" > "$dockq_raw"
echo "============================================" >> "$dockq_raw"
echo "" >> "$dockq_raw"

for pdb_dir in */; do

    [[ -d "$pdb_dir" ]] || continue

    pdbcode="${pdb_dir%/}"
    base_pdb="${pdbcode:0:4}"

    ref_pdb="../../../../01_dataset/${base_pdb}.pdb"

    echo "Folder: $pdbcode" >> "$dockq_raw"

    if [[ ! -f "$ref_pdb" ]]; then
        echo "Reference missing: $ref_pdb" >> "$dockq_raw"
        echo "" >> "$dockq_raw"
        continue
    fi

    echo "Reference: $ref_pdb" >> "$dockq_raw"

    for seed in 0 1 2 3 4; do
        for rank in 0 1 2 3 4; do

            model_file="${pdb_dir}/model_seed${seed}_sample${rank}.pdb"

            [[ -f "$model_file" ]] || continue

            if ! grep -q "^ATOM" "$model_file"; then
                echo "Empty PDB: $model_file" >> "$dockq_raw"
                continue
            fi

            echo "Model: $model_file" >> "$dockq_raw"

            DockQ "$model_file" "$ref_pdb" >> "$dockq_raw" 2>&1

            echo "" >> "$dockq_raw"

        done
    done

    echo "--------------------------------------------" >> "$dockq_raw"
    echo "" >> "$dockq_raw"

done

echo "DockQ calculations finished."

########################################
# PART 2: PARSE DockQ RESULTS
########################################

for seed in 0 1 2 3 4; do
    for rank in 0 1 2 3 4; do

        echo -e \
"PDB\tseed\trank\tModel\tDockQ\tiRMSD\tLRMSD\tfnat\tfnonnat" \
> "output/DockQ_seed${seed}_rank${rank}.txt"

    done
done

current_model=""
current_pdb=""
current_seed=""
current_rank=""

dockq=""
irmsd=""
lrmsd=""
fnat=""
fnonnat=""

while IFS= read -r line; do

    if [[ "$line" == Folder:* ]]; then
        current_pdb=$(echo "$line" | awk '{print $2}')
        continue
    fi

    if [[ "$line" =~ Model:\ (.*model_seed([0-4])_sample([0-4])\.pdb)$ ]]; then

        current_model=$(basename "${BASH_REMATCH[1]}")
        current_seed="${BASH_REMATCH[2]}"
        current_rank="${BASH_REMATCH[3]}"

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

        echo -e \
"${current_pdb}\t${current_seed}\t${current_rank}\t${current_model}\t${dockq}\t${irmsd}\t${lrmsd}\t${fnat}\t${fnonnat}" \
>> "output/DockQ_seed${current_seed}_rank${current_rank}.txt"

        current_model=""
        current_seed=""
        current_rank=""

    fi

done < "$dockq_raw"

echo "DockQ parsing finished."

########################################
# PART 3: EXTRACT pTM, ipTM,
#           AND RANKING SCORES
########################################

for seed in 0 1 2 3 4; do
    for rank in 0 1 2 3 4; do

        outfile="output/iptm_seed${seed}_rank${rank}.txt"

        echo -e \
"PDB\tseed\trank\tptm\tiptm\tranking_score" \
> "$outfile"

    done
done

find . -name "results_scores.csv" | sort |
while read -r csv; do

    pdb=$(basename "$(dirname "$csv")")

    tail -n +2 "$csv" |
    while IFS=',' read -r seed rank ptm iptm ranking_score; do

        outfile="output/iptm_seed${seed}_rank${rank}.txt"

        echo -e \
"${pdb}\t${seed}\t${rank}\t${ptm}\t${iptm}\t${ranking_score}" \
>> "$outfile"

    done

done

########################################
# DONE
########################################

echo ""
echo "Pipeline completed."