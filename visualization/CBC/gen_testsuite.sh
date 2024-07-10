#!/bin/bash

# Count the number of files that start with 'level_' in the Microban/ folder
file_count=$(ls CBC/level_* 2>/dev/null | wc -l)

# Iterate from 1 to the number of files
for i in $(seq 1 $file_count)
do
    python3 visualization/save_board_image.py --level_id=$i --folder=CBC/
done
