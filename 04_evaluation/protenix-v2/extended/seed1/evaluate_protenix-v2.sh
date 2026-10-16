#!/usr/bin/env bash

##################################################
# DockQ Analysis Pipeline
#
# # Requirements:
#   - DockQ
#   - MDAnalysis
#
# Outputs:
#   output/DockQ_seed101_rank0.txt
#   ...
#   output/DockQ_seed105_rank4.txt
#
#   output/iptm_seed101_rank0.txt
#   ...
#   output/iptm_seed105_rank4.txt
##################################################

mkdir -p output

##################################################
# PART 1: RUN DockQ
##################################################

dockq_log="output/all_DockQ_results.txt"

echo "DockQ results" > "$dockq_log"
echo "============================================" >> "$dockq_log"
echo "" >> "$dockq_log"

find . -type d -path "*/seed_*/predictions" |
sort |
while read -r pred_dir
do

    pdbcode=$(basename "$(dirname "$(dirname "$pred_dir")")")
    seed=$(basename "$(dirname "$pred_dir")")

    echo "PDB: $pdbcode | Seed: $seed" >> "$dockq_log"

    # Examples:
    # 8OWV_B -> 8OWV
    # 8PIH_B -> 8PIH
    # 7Q3R_G -> 7Q3R
    base_pdb="${pdbcode:0:4}"

    ref_pdb="../../../../01_dataset/${base_pdb}.pdb"

    if [[ ! -f "$ref_pdb" ]]; then
        echo "Reference missing: $ref_pdb" >> "$dockq_log"
        echo "" >> "$dockq_log"
        continue
    fi

    echo "Reference: $ref_pdb" >> "$dockq_log"

    shopt -s nullglob
    model_files=("$pred_dir"/*.cif)
    shopt -u nullglob

    if [[ ${#model_files[@]} -eq 0 ]]; then
        echo "No CIF models found" >> "$dockq_log"
        echo "" >> "$dockq_log"
        continue
    fi

    for model_file in "${model_files[@]}"
    do

        model_name=$(basename "$model_file")

        echo "Running DockQ for: $model_name" >> "$dockq_log"

        DockQ "$model_file" "$ref_pdb" >> "$dockq_log" 2>&1

        echo "" >> "$dockq_log"

    done

    echo "--------------------------------------------" >> "$dockq_log"
    echo "" >> "$dockq_log"

done

echo "DockQ calculations finished."

##################################################
# PART 2: PARSE DockQ OUTPUT
##################################################

input_file="output/all_DockQ_results.txt"

for seed in 101 102 103 104 105
do
    for rank in 0 1 2 3 4
    do

        echo -e \
"PDB\tSeed\tRank\tModel\tDockQ\tiRMSD\tLRMSD\tfnat\tfnonnat" \
> "output/DockQ_seed${seed}_rank${rank}.txt"

    done
done

current_pdb=""
current_seed=""
current_model=""
current_rank=""

dockq=""
irmsd=""
lrmsd=""
fnat=""
fnonnat=""

while IFS= read -r line
do

    if [[ "$line" =~ ^PDB:\ ([^[:space:]]+)\ \|\ Seed:\ seed_([0-9]+)$ ]]
    then
        current_pdb="${BASH_REMATCH[1]}"
        current_seed="${BASH_REMATCH[2]}"
        continue
    fi

    if [[ "$line" =~ Running\ DockQ\ for:\ (.*)$ ]]
    then

        current_model="${BASH_REMATCH[1]}"

        current_rank=$(
            echo "$current_model" |
            sed -nE 's/.*sample_([0-4])\.cif/\1/p'
        )

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

    if [[ -n "$current_model" && -n "$fnonnat" ]]
    then

        outfile="output/DockQ_seed${current_seed}_rank${current_rank}.txt"

        echo -e \
"${current_pdb}\t${current_seed}\t${current_rank}\t${current_model}\t${dockq}\t${irmsd}\t${lrmsd}\t${fnat}\t${fnonnat}" \
>> "$outfile"

        current_model=""
        current_rank=""

        dockq=""
        irmsd=""
        lrmsd=""
        fnat=""
        fnonnat=""

    fi

done < "$input_file"

echo "Finished generating DockQ seed-rank files."

##################################################
# PART 3: EXTRACT pTM AND ipTM
##################################################

for seed in 101 102 103 104 105
do
    for rank in 0 1 2 3 4
    do

        echo -e \
"PDB\tSeed\tRank\tpTM\tipTM" \
> "output/iptm_seed${seed}_rank${rank}.txt"

    done
done

find . -name "*.json" | sort |
while read -r json_file
do

    seed=$(
        echo "$json_file" |
        sed -nE 's#.*seed_([0-9]+).*#\1#p'
    )

    rank=$(
        echo "$json_file" |
        sed -nE 's#.*sample_([0-4]).*#\1#p'
    )

    [[ -z "$seed" ]] && continue
    [[ -z "$rank" ]] && continue

    pdb=$(basename "$(dirname "$(dirname "$(dirname "$json_file")")")")

    ptm=$(jq -r '.ptm // .pTM // .pTMscore // "NA"' "$json_file")
    iptm=$(jq -r '.iptm // .ipTM // "NA"' "$json_file")

    echo -e \
"${pdb}\t${seed}\t${rank}\t${ptm}\t${iptm}" \
>> "output/iptm_seed${seed}_rank${rank}.txt"

done

echo "Finished generating ipTM seed-rank files."

##################################################
# DONE
##################################################

echo ""
echo "Generated files:"
ls -1 output/

echo ""
echo "Pipeline completed."
