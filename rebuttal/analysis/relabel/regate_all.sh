#!/bin/bash
# 모든 런의 손실 고리를 LLM 판정으로 다시 계산 (regate_out/<run_id>.json)
cd "$(dirname "$0")"; mkdir -p regate_out
PY=${PY:-python}  # 하네스 의존성이 설치된 파이썬. G2G_CODE, G2G_RUNS, GATE_LEDGER 필요
# 판정 원본(batches/*/*.tsv)과 사례 묶음(out/cases.jsonl)이 있으면 다시 모으고, 없으면 저장된 verdicts.json.gz를 쓴다
if [ -d batches ] && [ -f out/cases.jsonl ]; then "$PY" -I collect.py; V=verdicts.json; else V=verdicts.json.gz; fi
"$PY" -I -c "
import sys; sys.path.insert(0,'.')
from runs import runs
print('\n'.join(r['run_id'] for r in runs()))" | xargs -P 14 -I{} "$PY" -I regate.py {} $V regate_out/{}.json > regate.log 2>&1
grep -c needs regate.log; grep -iv "needs" regate.log | head
