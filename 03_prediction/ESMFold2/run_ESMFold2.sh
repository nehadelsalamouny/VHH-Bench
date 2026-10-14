#!/bin/bash

for dir in */; do
    cd "$dir" || continue

    for file in *.py; do
        [[ -f "$file" ]] || continue
        python "$file"
    done

    cd ..
done
