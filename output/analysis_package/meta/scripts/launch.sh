#!/bin/bash
# 본 실행 1: 기준 셀 D5·R2 × 시드 12~14 × 4조건 × 2모델, 30일. 동결 사본(code/)으로만 실행.
M=/root/project/g2g_main
PY=/root/project/g2g/.venv/bin/python
cd $M/code
export PYTHONPATH=$M/code
for model in qwen3.5-27b qwen3.5-9b; do
 for cond in direct full_load routing ingress; do
  for s in 12 13 14; do
   OUT=$M/runs/$model/$cond/s$s
   mkdir -p $OUT
   nohup $PY -m gbg.cli.supervise $OUT -- $cond $M/scenarios/D5_s${s}_T45 $OUT --max-day 30 \
     --embed-cache $HOME/.cache/gbg/embeddings.sqlite --rerank-cache $HOME/.cache/gbg/rerank.sqlite \
     --model $model > $OUT/supervise.out 2>&1 &
   echo "$! $model $cond s$s" >> $M/pids.txt
  done
 done
done
