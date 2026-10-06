#!/bin/bash
# 부록 3종: direct_relay, retrieve, sidecar × 기준 셀 D5·R2 × 시드 12~14, 27B, 1~10일. 동결 사본 code_appx/ (d5851f4).
M=/root/project/g2g_main
PY=/root/project/g2g/.venv/bin/python
cd $M/code_appx
export PYTHONPATH=$M/code_appx
for cond in direct_relay retrieve sidecar; do
 for s in 12 13 14; do
  OUT=$M/runs_appx/$cond/s$s
  mkdir -p $OUT
  nohup $PY -m gbg.cli.supervise $OUT -- $cond $M/scenarios/D5_s${s}_T45 $OUT --max-day 10 \
    --embed-cache $HOME/.cache/gbg/embeddings.sqlite --rerank-cache $HOME/.cache/gbg/rerank.sqlite \
    --model qwen3.5-27b > $OUT/supervise.out 2>&1 &
  echo "$! $cond s$s" >> $M/pids_appx.txt
 done
done
