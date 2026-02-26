#!/bin/bash
set -euo pipefail

INPUT_DIR="./unlicensed_motion_dataset"
OUTPUT_DIR="./outputs/batch_results"

find "$INPUT_DIR" -type f -name "*.mp4" -print0 | while IFS= read -r -d '' video_path; do
    echo "========================================"
    echo "Processing: $video_path"

    # safety skip
    [[ -f "$video_path" ]] || { echo "WARNING: Missing file, skipping: $video_path"; continue; }

    category=$(basename "$(dirname "$video_path")")
    filename=$(basename -- "$video_path")
    filename_no_ext="${filename%.*}"

    target_out_dir="$OUTPUT_DIR/$category/$filename_no_ext"
    mkdir -p "$target_out_dir"

    python tools/demo/demo.py --video "$video_path" -s --output_root "$target_out_dir"
done

echo "Batch processing complete!"
