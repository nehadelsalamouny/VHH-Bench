#!/usr/bin/env bash

##################################################
# DockQ Analysis Pipeline
#
# Requirements:
#   - DockQ
#   - MDAnalysis
#
# Outputs:
#   output/DockQ_seed1_rank1.txt
#   ...
#   output/DockQ_seed5_rank5.txt
#
#   output/iptm_seed1_rank1.txt
#   ...
#   output/iptm_seed5_rank5.txt
#
#   output/DockQ_rank1_all_seeds.txt
#   output/percentages.txt
##################################################

mkdir -p output

##################################################
# PART 1: RUN DockQ
##################################################

dockq_log="output/all_DockQ_results.txt"

echo "DockQ results" > "$dockq_log"
echo "============================================" >> "$dockq_log"
echo "" >> "$dockq_log"

for pdb_dir in */; do

    pdb=$(basename "$pdb_dir")

    [[ "$pdb" == "__pycache__" ]] && continue
    [[ "$pdb" == "output" ]] && continue

    base_pdb=$(echo "$pdb" | cut -d'_' -f1)

    ref_pdb="../../../../01_dataset/${base_pdb}.pdb"

    if [[ ! -f "$ref_pdb" ]]; then
        echo "Reference PDB missing: $ref_pdb" >> "$dockq_log"
        continue
    fi

    find "$pdb_dir" -type d -name "*-pred-*" | sort |
    while read -r pred_dir; do

        cif_file="${pred_dir}/predicted_structure.cif"

        [[ -f "$cif_file" ]] || continue

        echo "Folder: $pred_dir" >> "$dockq_log"

        DockQ "$cif_file" "$ref_pdb" >> "$dockq_log" 2>&1

        echo "" >> "$dockq_log"
        echo "--------------------------------------------" >> "$dockq_log"
        echo "" >> "$dockq_log"

    done

done

echo "DockQ calculations finished."

##################################################
# PART 2: CREATE DockQ_seedX_rankY FILES
##################################################

for seed in {1..5}; do
    for rank in {1..5}; do

        echo -e \
"Folder\tSeed\tRank\tModel\tDockQ\tiRMSD\tLRMSD\tFnat\tFnonnat" \
> "output/DockQ_seed${seed}_rank${rank}.txt"

    done
done

awk '
BEGIN {
    FS="\n"
    RS="--------------------------------------------\n"
}

{
    folder=""
    dockq=""
    irmsd=""
    lrmsd=""
    fnat=""
    fnonnat=""

    for(i=1;i<=NF;i++) {

        if($i ~ /^Folder:/) {
            sub(/^Folder: /,"",$i)
            folder=$i
        }

        if($i ~ /DockQ:/ && $i !~ /legend/) {
            split($i,a,":")
            dockq=a[2]
            gsub(/^[ \t]+|[ \t]+$/,"",dockq)
        }

        if($i ~ /iRMSD:/) {
            split($i,a,":")
            irmsd=a[2]
            gsub(/^[ \t]+|[ \t]+$/,"",irmsd)
        }

        if($i ~ /LRMSD:/) {
            split($i,a,":")
            lrmsd=a[2]
            gsub(/^[ \t]+|[ \t]+$/,"",lrmsd)
        }

        if($i ~ /fnat:/) {
            split($i,a,":")
            fnat=a[2]
            gsub(/^[ \t]+|[ \t]+$/,"",fnat)
        }

        if($i ~ /fnonnat:/) {
            split($i,a,":")
            fnonnat=a[2]
            gsub(/^[ \t]+|[ \t]+$/,"",fnonnat)
        }
    }

    if(folder != "") {

        n = split(folder,p,"/")
        foldername = p[n]

        if(match(foldername,/pred-([0-9]+)-([0-9]+)/)) {

            seed = substr(foldername,RSTART+5,1)
            rank = substr(foldername,RSTART+7,1)

            print folder "\t" seed "\t" rank "\t" \
                  folder "/predicted_structure.cif\t" \
                  dockq "\t" irmsd "\t" lrmsd "\t" \
                  fnat "\t" fnonnat \
            >> sprintf("output/DockQ_seed%s_rank%s.txt",seed,rank)
        }
    }
}
' output/all_DockQ_results.txt

##################################################
# PART 3: EXTRACT pTM AND ipTM
##################################################

for seed in {1..5}; do
    for rank in {1..5}; do

        echo -e \
"Folder\tSeed\tRank\tModel\tptm\tiptm\tranking_confidence" \
> "output/iptm_seed${seed}_rank${rank}.txt"

    done
done

find . -type d -name "*-pred-*" | sort |
while read -r pred_dir; do

    json_file="${pred_dir}/all_results.json"

    [[ -f "$json_file" ]] || continue

    if [[ "$(basename "$pred_dir")" =~ -pred-([0-9]+)-([0-9]+)$ ]]; then
        seed="${BASH_REMATCH[1]}"
        rank="${BASH_REMATCH[2]}"
    else
        continue
    fi

    ptm=$(jq -r '.ptm // .global_ptm // "NA"' "$json_file")
    iptm=$(jq -r '.iptm // .global_iptm // "NA"' "$json_file")
    confidence=$(jq -r '.ranking_confidence // "NA"' "$json_file")

    echo -e \
"${pred_dir}\t${seed}\t${rank}\t${pred_dir}/predicted_structure.cif\t${ptm}\t${iptm}\t${confidence}" \
>> "output/iptm_seed${seed}_rank${rank}.txt"

done

##################################################
# PART 4: COMBINE RANK1 FILES
##################################################

first=1

for seed in {1..5}; do

    file="output/DockQ_seed${seed}_rank1.txt"

    [[ -f "$file" ]] || continue

    if [[ $first -eq 1 ]]; then

        cat "$file" > output/DockQ_rank1_all_seeds.txt
        first=0

    else

        tail -n +2 "$file" >> output/DockQ_rank1_all_seeds.txt

    fi

done

##################################################
# PART 5: CALCULATE DOCKQ STATISTICS
##################################################

file="output/DockQ_rank1_all_seeds.txt"

total=$(tail -n +2 "$file" | wc -l)

failed=$(awk -F'\t' \
'NR>1 && $5<=0.23 {c++} END{print c+0}' "$file")

acceptable=$(awk -F'\t' \
'NR>1 && $5>0.23 && $5<=0.49 {c++} END{print c+0}' "$file")

medium=$(awk -F'\t' \
'NR>1 && $5>0.49 && $5<=0.80 {c++} END{print c+0}' "$file")

high=$(awk -F'\t' \
'NR>1 && $5>0.80 {c++} END{print c+0}' "$file")

acceptable_plus=$(awk -F'\t' \
'NR>1 && $5>0.23 {c++} END{print c+0}' "$file")

failed_pct=$(awk "BEGIN {printf \"%.1f\",100*$failed/$total}")
acceptable_pct=$(awk "BEGIN {printf \"%.1f\",100*$acceptable/$total}")
medium_pct=$(awk "BEGIN {printf \"%.1f\",100*$medium/$total}")
high_pct=$(awk "BEGIN {printf \"%.1f\",100*$high/$total}")
acceptable_plus_pct=$(awk "BEGIN {printf \"%.1f\",100*$acceptable_plus/$total}")

cat > output/percentages.txt << EOF
DockQ Rank-1 Statistics (All Seeds)
===================================

Total structures: $total

Failed (<=0.23): $failed (${failed_pct}%)

Acceptable (0.23-0.49): $acceptable (${acceptable_pct}%)

Medium (0.49-0.80): $medium (${medium_pct}%)

High (>0.80): $high (${high_pct}%)

Acceptable+ (>0.23): $acceptable_plus (${acceptable_plus_pct}%)
EOF

##################################################
# DONE
##################################################

echo ""
echo "Pipeline completed."
