#!/bin/bash
# 모든 런의 need 원장 → gates/<run_id>.json (4개 병렬)
M=/root/project/g2g_main; cd /root/project/g2g
{
for p in $M/runs/*/*/s1[234]; do echo "$p $M/scenarios/D5_$(basename $p)_T45 15 $M/gates/main__base__$(basename $(dirname $(dirname $p)))__$(basename $(dirname $p))__$(basename $p).json"; done
for p in $M/runs_g/*/*/s1[234]; do c=$(basename $(dirname $(dirname $p))); echo "$p $(ls -d $M/scenarios_g/$c/D*_$(basename $p)_T45) 10 $M/gates/gcell__${c}__qwen3.5-27b__$(basename $(dirname $p))__$(basename $p).json"; done
for p in $M/runs_appx/*/s1[234]; do echo "$p $M/scenarios/D5_$(basename $p)_T45 10 $M/gates/appendix__base__qwen3.5-27b__$(basename $(dirname $p))__$(basename $p).json"; done
} | xargs -P 4 -L 1 bash -c 'uv run --no-sync python /root/project/g2g_main/gates/run_ledger.py $0 $1 $2 $3 >> /root/project/g2g_main/gates/run_all.log 2>&1'
echo ALL_DONE >> /root/project/g2g_main/gates/run_all.log
