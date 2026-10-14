#!/bin/bash

for json in *.json
do
    name=$(basename "$json" .json)

    for seed in 101 102 103 104 105
    do
        echo "Running $name seed $seed"

        protenix pred \
            -i "$json" \
            -o "$name" \
            -n protenix-v2 \
            -s "$seed"
    done
done
