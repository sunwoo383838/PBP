#!/bin/bash
cd "$(dirname "$0")/batches"
for b in b*; do n=$(ls $b/*.md | wc -l); d=$(ls $b/*.tsv 2>/dev/null | wc -l); [ "$d" != "0" ] && echo "$b $d/$n"; done | column -c 160
echo "parts done: $(ls */*.tsv 2>/dev/null | wc -l) / $(ls */*.md | wc -l)"
