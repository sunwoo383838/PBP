"""모델별 direct·sidecar 비교: need 고리 분포와 전달률, need가 전부 전달된 과제와 그중 정답(등급별), 필요한 그룹 전부에 요청한
과제 비율, direct와 sidecar 양쪽에서 필요한 그룹 전부에 요청한 과제만의 이득(쌍 부트스트랩 1만 회, 95%).

    python request_delivery.py [LEDGER_DIR] [REQUESTS.json.gz] [OUT_JSON]
기본값: ledgers/, requests.json.gz, request_delivery.json (이 파일 기준). 과제 집합은 그 모델의 다섯 조건(direct·routing·sidecar·
ingress·full_load)이 모두 채점한 공통 과제. 판정 가능한 과제 = 판정 가능한 need(조각이 있는 원격 need)가 1개 이상인 과제.
"""
import json,sys,collections,random,os,gzip
HERE=os.path.dirname(os.path.abspath(__file__))
LED=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'ledgers')
REQ=json.load(gzip.open(sys.argv[2] if len(sys.argv)>2 else os.path.join(HERE,'requests.json.gz')))
OUTF=sys.argv[3] if len(sys.argv)>3 else os.path.join(HERE,'request_delivery.json')
SEEDS=('s12','s13','s14'); GATES=['ok','L_request','L_reach','L_observe.window','L_observe.search','L_respond','L_select']
def led(model,cond,s):
    f=f'{LED}/C__{model}__sidecar__{s}.json.gz' if cond=='sidecar' and model!='qwen3.5-27b' else f'{LED}/B__{model}__{cond}__{s}.json.gz'
    return json.load(gzip.open(f))
def scored_tasks(d): return {t['task_id']:t for t in d['tasks'] if not t['unreachable'] and t['day']<=10 and t.get('outcome') is not None}
def boot(d,B=10000,seed=0):
    r=random.Random(seed); N=len(d); ms=sorted(sum(d[r.randrange(N)] for _ in range(N))/N for _ in range(B)); return ms[int(.025*B)],ms[int(.975*B)-1]
OUT={}
for model,conds in REQ.items():
    L={c:{s:led(model,c,s) for s in SEEDS} for c in ('direct','sidecar')}
    common={s:set.intersection(*[set(scored_tasks(led(model,c,s))) for c in ('direct','routing','sidecar','ingress','full_load')]) for s in SEEDS}
    R={}; n=sum(map(len,common.values()))
    print(f"\n## {model} (공통 과제 {n})")
    for c in ('direct','sidecar'):
        g=collections.Counter(); T={}
        for s in SEEDS:
            tk=scored_tasks(L[c][s]); rq=conds[c][s]
            byt=collections.defaultdict(list)
            for nd in L[c][s]['needs']:
                if nd['task_id'] in common[s]:
                    byt[nd['task_id']].append(nd)
                    if nd.get('scored',True): g[nd['gate'] if nd['gate'] in GATES else 'E_*']+=1
            for t in common[s]:
                sc=[x for x in byt[t] if x.get('scored',True)]
                T[(s,t)]={'exact':bool(tk[t]['exact']),'cls':tk[t]['class'],'judgeable':len(sc)>0,
                          'all_delivered':all(x['gate']=='ok' for x in sc),'n_need':len(sc),'n_ok':sum(x['gate']=='ok' for x in sc),
                          'asked_all':set(rq[t]['needed'])<=set(rq[t]['asked']),'n_groups_needed':len(rq[t]['needed']),'n_groups_asked':len(set(rq[t]['needed'])&set(rq[t]['asked']))}
        R[c]=(g,T)
    print("\n**need 단위 고리 분포** (판정 가능한 need)\n\n| 조건 | need | 전달률(ok) | "+" | ".join(GATES[1:])+" | 오류 코드 |\n|"+"---|"*(len(GATES)+3))
    OUT[model]={'n':n}
    for c,(g,T) in R.items():
        tot=sum(g.values()); OUT[model][c]={'needs':tot,'gates':dict(g)}
        print(f"| {c} | {tot} | {100*g['ok']/tot:.1f}% ({g['ok']}) | "+" | ".join(f"{100*g[x]/tot:.1f}%" for x in GATES[1:])+f" | {g['E_*']} |")
    print("\n**과제 단위** (판정 가능한 과제 = 판정 가능한 need가 1개 이상)\n\n| 조건 | 등급 | 판정 가능한 과제 | need 전부 전달 | 그중 정답 | 전부 전달 중 정답률 | 전부 전달 아님 | 그중 정답 |\n|"+"---|"*8)
    for c,(g,T) in R.items():
        for cls in ('전체','A','B','C','D'):
            J=[v for v in T.values() if v['judgeable'] and (cls=='전체' or v['cls']==cls)]
            ad=[v for v in J if v['all_delivered']]; nd=[v for v in J if not v['all_delivered']]
            OUT[model][c].setdefault('tasks',{})[cls]={'judgeable':len(J),'all_delivered':len(ad),'all_delivered_correct':sum(v['exact'] for v in ad),'not_delivered':len(nd),'not_delivered_correct':sum(v['exact'] for v in nd)}
            if not J: print(f"| {c} | {cls} | 0 | – | – | – | – | – |"); continue
            print(f"| {c} | {cls} | {len(J)} | {len(ad)} | {sum(v['exact'] for v in ad)} | "+(f"{100*sum(v['exact'] for v in ad)/len(ad):.0f}%" if ad else "–")+f" | {len(nd)} | {sum(v['exact'] for v in nd)} |")
        nj=sum(1 for v in T.values() if not v['judgeable']); OUT[model][c]['unjudgeable']={'n':nj,'correct':sum(v['exact'] for v in T.values() if not v['judgeable'])}
        print(f"| {c} | 판정 불가(조각 need 없음) | {nj} | – | {OUT[model][c]['unjudgeable']['correct']} (정답) | – | – | – |")
    print("\n**필요한 그룹 전부에 요청한 과제**\n\n| 조건 | 전체 285 | 판정 가능한 과제 | 등급 A / B / C / D | 필요한 그룹 중 요청한 비율 |\n|---|---|---|---|---|")
    for c,(g,T) in R.items():
        V=list(T.values()); J=[v for v in V if v['judgeable']]
        bc=" / ".join(f"{100*sum(v['asked_all'] for v in V if v['cls']==k)/max(1,sum(v['cls']==k for v in V)):.0f}%" for k in 'ABCD')
        OUT[model][c]['asked_all']={'all':sum(v['asked_all'] for v in V),'judgeable':sum(v['asked_all'] for v in J),'n_judgeable':len(J),
            'group_coverage':sum(v['n_groups_asked'] for v in V)/sum(v['n_groups_needed'] for v in V)}
        print(f"| {c} | {100*sum(v['asked_all'] for v in V)/len(V):.1f}% ({sum(v['asked_all'] for v in V)}) | {100*sum(v['asked_all'] for v in J)/len(J):.1f}% ({sum(v['asked_all'] for v in J)}/{len(J)}) | {bc} | {100*OUT[model][c]['asked_all']['group_coverage']:.1f}% |")
    Td,Ts=R['direct'][1],R['sidecar'][1]; keys=sorted(Td)
    print("\n**sidecar − direct 이득, 요청 여부로 나눈 부분집합**\n\n| 과제 집합 | 과제 | direct | sidecar | Δ (pp) [95% CI] |\n|---|---|---|---|---|")
    OUT[model]['gain']={}
    for name,sel in (('전체',lambda k:True),('양쪽 모두 필요한 그룹 전부에 요청',lambda k:Td[k]['asked_all'] and Ts[k]['asked_all']),
                     ('한쪽이라도 빠뜨림',lambda k:not(Td[k]['asked_all'] and Ts[k]['asked_all'])),
                     ('양쪽 모두 전부 요청 · 판정 가능한 과제만',lambda k:Td[k]['asked_all'] and Ts[k]['asked_all'] and Td[k]['judgeable']),
                     ('양쪽 모두 전부 요청 · 등급 B·C·D',lambda k:Td[k]['asked_all'] and Ts[k]['asked_all'] and Td[k]['cls']!='A')):
        ks=[k for k in keys if sel(k)]
        if not ks: continue
        d=[int(Ts[k]['exact'])-int(Td[k]['exact']) for k in ks]; lo,hi=boot(d)
        a=lambda T:100*sum(T[k]['exact'] for k in ks)/len(ks)
        OUT[model]['gain'][name]={'n':len(ks),'direct':a(Td),'sidecar':a(Ts),'gain':100*sum(d)/len(d),'ci':[100*lo,100*hi]}
        print(f"| {name} | {len(ks)} | {a(Td):.1f} | {a(Ts):.1f} | {100*sum(d)/len(d):+.1f} [{100*lo:+.1f}, {100*hi:+.1f}] |")
    x=collections.Counter((Td[k]['asked_all'],Ts[k]['asked_all']) for k in keys)
    OUT[model]['asked_cross']={f"direct={a},sidecar={b}":v for (a,b),v in x.items()}
    print("\n요청 교차 (direct 전부 요청, sidecar 전부 요청):",dict(x))
json.dump(OUT,open(OUTF,'w'),indent=1,ensure_ascii=False)
