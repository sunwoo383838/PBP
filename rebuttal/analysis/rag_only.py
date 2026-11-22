"""rag_only 실행 확인과 need 출처별 분해 (27B, 공통 과제).

    python rag_only.py RUNS_RAG SCEN_DIR [LEDGER_DIR] [COMMON_JSON] [OUT_JSON]
RUNS_RAG: rag_only 조건 폴더(아래에 s12·s13·s14). SCEN_DIR: 시나리오 폴더들의 부모(D5_s12_T45 등).
실행 확인: 창구 결정의 action, 재질의, 과거 문답 인용, 창구가 구성원에게 보낸 메시지, 응답 상태(조립 실패율).
분해: 정답 원장의 원격 need 출처에 db_query 또는 negative가 있는 과제와 없는 과제로 나눈 정확도와 대비(쌍 부트스트랩 1만 회, 95%).
"""
import json,sys,collections,re,gzip,os,random
HERE=os.path.dirname(os.path.abspath(__file__))
RUN=sys.argv[1]; SCEN=sys.argv[2]
LED=sys.argv[3] if len(sys.argv)>3 else os.path.join(HERE,'ledgers')
COMMON=json.load(open(sys.argv[4] if len(sys.argv)>4 else os.path.join(HERE,'common_tasks_27b.json')))
OUTF=sys.argv[5] if len(sys.argv)>5 else os.path.join(HERE,'rag_only.json')
SEEDS=('s12','s13','s14')
CONDS=['direct','routing','retrieve','sidecar','ingress_plain_sym','ingress_no_requery','ingress','rag_only','full_load']
def ledger(c,s):
    for pre in (f'A__{c}',f'B__qwen3.5-27b__{c}'):
        f=f'{LED}/{pre}__{s}.json.gz'
        if os.path.exists(f): return json.load(gzip.open(f))
def boot(d,B=10000,seed=0):
    r=random.Random(seed); N=len(d)
    ms=sorted(sum(d[r.randrange(N)] for _ in range(N))/N for _ in range(B))
    return 100*ms[int(.025*B)],100*ms[int(.975*B)-1]
OUT={}
# ---- 실행 확인 (1~10일 전체 요청)
C=collections.Counter(); grp={}
for s in SEEDS:
    ev=[e for e in map(json.loads,open(f'{RUN}/{s}/wal/events.jsonl')) if e['day']<=10]
    for e in ev:
        if e['type']=='agent_join': grp[(s,e['payload'].get('agent'))]=e['payload'].get('group')
    req={e['payload']['task_id']:e['payload']['agent'] for e in ev if e['type']=='task_delivered'}
    togroup={e['payload']['rid'] for e in ev if e['type']=='message' and e['payload'].get('kind')=='request' and e['payload'].get('to_agent') is None}
    for e in ev:
        p=e['payload']
        if e['type']=='boundary_decision':
            C['decisions']+=1; C['action_'+str(p.get('action'))]+=1; C['requery_nonempty']+=bool(p.get('requery'))
            C['S_source']+=any(re.fullmatch(r'S\d+',x) for x in p.get('sources') or [])
            C['selected_members']+=bool(p.get('selected'))
            its=p.get('items') or []
            C['items']+=len(its); C['items_rule']+=sum(x.get('source')=='rule' for x in its); C['cites_rule']+=any(x.get('source')=='rule' for x in its)
        if e['type']=='message':
            if e['actor'].startswith('boundary') and p.get('kind')=='request': C['desk_requests']+=1
            if p.get('kind')=='request' and p.get('to_agent') is None: C['requests_to_group']+=1
            if p.get('kind')=='request' and p.get('to_agent'):
                C['requests_to_agent']+=1
                C['requests_to_agent_from_assignee']+=p.get('from_agent')==req.get(p.get('task_id'))
            if p.get('kind')=='response' and p.get('to_agent') is None:
                who=e['actor'].split(':')[0]; C[f'resp_{who}_{p["response"]["status"]}']+=1
                if who=='kernel': C['kernel_'+str(p['response'].get('answer'))]+=1
        if e['type']=='llm_call':
            C['llm_'+str(p.get('component'))]+=1
            C['responder_for_desk']+=p.get('component')=='responder' and p.get('serving') in togroup
nb=sum(v for k,v in C.items() if k.startswith('resp_boundary_'))
OUT['checks']=dict(C); OUT['assembly_error_rate']=C['resp_boundary_error']/nb
print("### rag_only 실행 확인 (27B, 시드 3개, 1~10일)\n")
print(f"- 창구 결정 {C['decisions']}건의 action: "+", ".join(f"{k[7:]} {v}" for k,v in C.items() if k.startswith('action_'))+
      f". 재질의가 있는 결정 {C['requery_nonempty']}건, 구성원을 고른 결정 {C['selected_members']}건, 과거 문답([S#])을 근거로 든 결정 {C['S_source']}건.")
print(f"- 창구가 구성원에게 보낸 요청 {C['desk_requests']}건, 그룹 앞 요청을 처리한 구성원 LLM 호출 {C['responder_for_desk']}건.")
print(f"- 요청자가 자기 그룹 동료에게 직접 보낸 요청은 {C['requests_to_agent']}건(다른 조건에도 있는 그룹 내 문의). 이를 처리한 호출이 responder {C['llm_responder']}건이다.")
print(f"- 창구 응답 {nb}건의 상태: "+", ".join(f"{k[14:]} {v}" for k,v in sorted(C.items()) if k.startswith('resp_boundary_'))+
      f". 조립 실패(error) {100*OUT['assembly_error_rate']:.1f}%.")
print(f"- 반환 항목 {C['items']}개 중 규정을 근거로 든 항목 {C['items_rule']}개(결정 {C['cites_rule']}건).")
print(f"- 없는 그룹 id로 보낸 요청(kernel 오류 응답) {C['kernel_unknown_group']}건.")
# ---- need 출처별 분해
L={c:{s:ledger(c,s) for s in SEEDS} for c in CONDS}
flag={}
for s in SEEDS:
    for l in open(f'{SCEN}/D5_{s}_T45/private/gold.jsonl'):
        g=json.loads(l)
        if g['wid'] not in COMMON[s]: continue
        rem=[n for n in g['needs'] if not n['local']]
        ty={x['type'] for n in rem for x in n['sources']}
        flag[(s,g['wid'])]={'db_query':'db_query' in ty,'negative':'negative' in ty,'frag':'frag' in ty,'class':g['state_class']}
keys=sorted(flag)
X={c:{(s,t['task_id']):int(t['exact']) for s in SEEDS for t in L[c][s]['tasks'] if t['task_id'] in COMMON[s]} for c in CONDS}
SUB=[('전체',lambda f:True),
     ('DB 목록 조회 또는 부재 확인 필요',lambda f:f['db_query'] or f['negative']),
     ('  DB 목록 조회(db_query) 필요',lambda f:f['db_query']),
     ('  부재 확인(negative) 필요',lambda f:f['negative']),
     ('둘 다 불필요',lambda f:not(f['db_query'] or f['negative'])),
     ('원격 need에 조각 출처 있음',lambda f:f['frag']),
     ('원격 need에 조각 출처 없음',lambda f:not f['frag']),
     ('등급 A',lambda f:f['class']=='A'),('등급 B',lambda f:f['class']=='B'),('등급 C',lambda f:f['class']=='C'),('등급 D',lambda f:f['class']=='D')]
print("\n### need 출처별 정확도 (27B, 공통 285과제)\n")
print("출처는 정답 원장의 원격 need 기준. rag_only의 창구에는 DB 조회 도구가 없고, 등록된 DB 버전 표시([V#])만 본다.\n")
print("| 과제 집합 | 과제 | "+" | ".join(CONDS)+" | sidecar − rag_only [95% CI] | rag_only − direct [95% CI] |")
print("|"+"---|"*(len(CONDS)+4))
OUT['split']={}
for name,f in SUB:
    ks=[k for k in keys if f(flag[k])]
    if not ks: continue
    acc={c:100*sum(X[c][k] for k in ks)/len(ks) for c in CONDS}
    d1=[X['sidecar'][k]-X['rag_only'][k] for k in ks]; d2=[X['rag_only'][k]-X['direct'][k] for k in ks]
    c1=boot(d1); c2=boot(d2)
    OUT['split'][name.strip()]={'n':len(ks),'acc':acc,'sidecar_minus_rag':(100*sum(d1)/len(ks),)+c1,'rag_minus_direct':(100*sum(d2)/len(ks),)+c2}
    print(f"| {name} | {len(ks)} | "+" | ".join(f"{acc[c]:.1f}" for c in CONDS)+
          f" | {100*sum(d1)/len(ks):+.1f} [{c1[0]:+.1f}, {c1[1]:+.1f}] | {100*sum(d2)/len(ks):+.1f} [{c2[0]:+.1f}, {c2[1]:+.1f}] |")
# ---- sidecar와 어긋난 과제, 비용
dis=collections.Counter((X['sidecar'][k],X['rag_only'][k]) for k in keys)
OUT['discordant_vs_sidecar']={'both':dis[(1,1)],'sidecar_only':dis[(1,0)],'rag_only':dis[(0,1)],'neither':dis[(0,0)]}
print(f"\nsidecar와 교차: 둘 다 정답 {dis[(1,1)]}, sidecar만 {dis[(1,0)]}, rag_only만 {dis[(0,1)]}, 둘 다 오답 {dis[(0,0)]}.")
print("\n| 조건 | 과제당 호출 | 과제당 토큰 | 요청자 호출 | 창구 호출 | 구성원 호출 |\n|---|---|---|---|---|---|")
OUT['cost']={}
for c in ('direct','retrieve','sidecar','ingress','rag_only','full_load'):
    T=[t for s in SEEDS for t in L[c][s]['tasks'] if t['task_id'] in COMMON[s]]
    m=lambda f:sum(map(f,T))/len(T)
    o={'calls':m(lambda t:t['calls']),'tokens':m(lambda t:t['tokens']),**{k:m(lambda t:t['components'].get(k,{}).get('calls',0)) for k in ('requester','boundary','responder')}}
    OUT['cost'][c]=o
    print(f"| {c} | {o['calls']:.1f} | {o['tokens']/1000:.0f}k | {o['requester']:.1f} | {o['boundary']:.1f} | {o['responder']:.1f} |")
OUT['flags']={f'{s}/{t}':v for (s,t),v in flag.items()}
json.dump(OUT,open(OUTF,'w'),indent=1,ensure_ascii=False)
