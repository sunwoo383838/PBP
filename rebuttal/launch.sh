#!/bin/bash
# 리버탈 추가 실험 실행기. 환경 변수: M(기준 시나리오·결과 루트), RB(리버탈 결과 루트), PY(파이썬), CODE(동결 코드 사본).
#   ./launch.sh A      ingress_plain_sym, ingress_no_requery, rag_only × 27B × 시드 12~14, 1~10일
#   ./launch.sh C      sidecar × deepseek-v4-flash·qwen3.5-9b × 시드 12~14, 1~10일
#   ./launch.sh D      direct·sidecar × K16k·lag1·warm10 × 27B × 시드 12, 1~10일
#   ./launch.sh one COND SCEN OUT MODEL MAXDAY [CONFIGS]
# 조건마다 쓴 코드 사본(CODE)은 README.md의 표를 따른다. 임베딩·리랭크 캐시는 모든 실행이 같은 파일을 쓴다.
set -e
: "${M:?기준 시나리오 루트}" "${RB:?리버탈 결과 루트}" "${CODE:?동결 코드 사본}"
PY=${PY:-python}
CACHE="--embed-cache $HOME/.cache/gbg/embeddings.sqlite --rerank-cache $HOME/.cache/gbg/rerank.sqlite"
cd $CODE
export PYTHONPATH=$CODE

one() {  # COND SCEN OUT MODEL MAXDAY [CONFIGS]
  local cond=$1 scen=$2 out=$3 model=$4 maxday=$5 cfg=${6:-}
  mkdir -p $out
  nohup $PY -m gbg.cli.supervise $out -- $cond $scen $out --max-day $maxday $CACHE --model $model \
    ${cfg:+--configs $cfg} > $out/supervise.out 2>&1 &
  echo "$! $cond $model $(basename $out) $out" >> $RB/pids.txt
}

case "$1" in
  A)
    for cond in ingress_plain_sym ingress_no_requery rag_only; do
      for s in 12 13 14; do one $cond $M/scenarios/D5_s${s}_T45 $RB/runs/qwen3.5-27b/$cond/s$s qwen3.5-27b 10; done
    done ;;
  C)
    for model in deepseek-v4-flash qwen3.5-9b; do
      for s in 12 13 14; do one sidecar $M/scenarios/D5_s${s}_T45 $RB/runs/$model/sidecar/s$s $model 10; done
    done ;;
  D)
    for cell in K16k lag1 warm10; do
      cfg=""; [ $cell = K16k ] && cfg=$RB/configs_K16k
      for cond in direct sidecar; do
        one $cond $RB/scenarios_d/$cell/D5_s12_T45 $RB/runs_d/$cell/$cond/s12 qwen3.5-27b 10 $cfg
      done
    done ;;
  one)
    shift; one "$@" ;;
  *) echo "usage: $0 A|C|D|one ..."; exit 1 ;;
esac
