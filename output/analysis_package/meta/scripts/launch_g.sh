#!/bin/bash
# 본 실행 2: G 셀 R1(D5,G5)·R3(D5,G15)·D3(R2,G6) × 시드 12~14 × 4조건, 27B만, 15일. 1차와 같은 동결 사본(code/).
M=/root/project/g2g_main
PY=/root/project/g2g/.venv/bin/python
cd $M/code
export PYTHONPATH=$M/code
for cell in R1:5 R3:5 D3:3; do
 c=${cell%%:*}; D=${cell##*:}
 for cond in direct full_load routing ingress; do
  for s in 12 13 14; do
   OUT=$M/runs_g/$c/$cond/s$s
   mkdir -p $OUT
   nohup $PY -m gbg.cli.supervise $OUT -- $cond $M/scenarios_g/$c/D${D}_s${s}_T45 $OUT --max-day 15 \
     --embed-cache $HOME/.cache/gbg/embeddings.sqlite --rerank-cache $HOME/.cache/gbg/rerank.sqlite \
     --model qwen3.5-27b > $OUT/supervise.out 2>&1 &
   echo "$! $c $cond s$s" >> $M/pids_g.txt
  done
 done
done
