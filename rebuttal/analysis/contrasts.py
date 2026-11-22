"""리버탈 대비 표. 모델별로 전 조건이 모두 채점한 공통 과제에서 정확도·need 고리 분포·대비(쌍 부트스트랩 1만 회, 95%).
민감도는 셀마다 direct·sidecar 공통 과제에서 관측 이득과 자연 등급 분포로 가중한 이득(등급 안 층화 부트스트랩).

    python contrasts.py [LEDGER_DIR] [NATURAL_JSON] [OUT_JSON]
기본값: ledgers/, ../sensitivity/natural_class.json, contrasts.json (이 파일 기준).
원장 이름: B__<모델>__<조건>__<시드> (기존 런), A__<조건>__<시드> (27B 새 조건), C__<모델>__sidecar__<시드>, D__<셀>__<조건>__s12.
"""
import json,glob,collections,random,os,sys,gzip
HERE=os.path.dirname(os.path.abspath(__file__))
LED=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'ledgers')
NAT=json.load(open(sys.argv[2] if len(sys.argv)>2 else os.path.join(HERE,'..','sensitivity','natural_class.json')))
OUTF=sys.argv[3] if len(sys.argv)>3 else os.path.join(HERE,'contrasts.json')
L={tuple(os.path.basename(f)[:-8].split('__')):json.load(gzip.open(f)) for f in glob.glob(os.path.join(LED,'[ABCD]__*.json.gz'))}
GATES=['ok','L_request','L_reach','L_observe.window','L_observe.search','L_respond','L_select']
SEEDS=('s12','s13','s14')
def tasks(d): return {t['task_id']:t for t in d['tasks'] if not t['unreachable'] and t['day']<=10 and t.get('outcome') is not None}
def runs(model):
    R={}
    for k,d in L.items():
        if k[0]=='B' and k[1]==model: R.setdefault(k[2],{})[k[3]]=d
        if k[0]=='C' and k[1]==model: R.setdefault('sidecar',{})[k[3]]=d
        if k[0]=='A' and model=='qwen3.5-27b': R.setdefault(k[1],{})[k[2]]=d
    return R
def boot(diffs,B=10000,seed=0):
    r=random.Random(seed); N=len(diffs)
    ms=sorted(sum(diffs[r.randrange(N)] for _ in range(N))/N for _ in range(B))
    return ms[int(.025*B)],ms[int(.975*B)-1]
OUT={}
def table(model,conds,contrasts,base='direct'):
    R=runs(model); R={c:R[c] for c in conds if c in R and len(R[c])==3}
    common={s:set.intersection(*[set(tasks(R[c][s])) for c in R]) for s in SEEDS}
    n=sum(map(len,common.values()))
    X={c:{(s,t):int(tasks(R[c][s])[t]['exact']) for s in SEEDS for t in common[s]} for c in R}
    keys=sorted(X[base])
    print(f"\n### {model}: 공통 과제 {n} (조건 {len(R)}개 모두 채점된 과제)")
    print("| 조건 | 정확도 | "+" | ".join(GATES)+" | use | need n |"); print("|"+"---|"*(len(GATES)+4))
    res={'n':n,'conds':{},'contrasts':{}}
    for c in R:
        g=collections.Counter(); use=0
        for s in SEEDS:
            T=tasks(R[c][s]); use+=sum(T[t]['outcome']=='use' for t in common[s])
            for nd in R[c][s]['needs']:
                if nd['task_id'] in common[s] and nd.get('scored',True) and nd['gate'] in GATES: g[nd['gate']]+=1
        tot=sum(g.values()); acc=100*sum(X[c].values())/n
        res['conds'][c]={'acc':acc,'gates':{x:g[x]/tot for x in GATES},'use':use,'needs':tot}
        print(f"| {c} | {acc:.1f}% | "+" | ".join(f"{100*g[x]/tot:.0f}%" for x in GATES)+f" | {use} | {tot} |")
    print("\n| 대비 | Δ정확도 (pp) [95% CI] |\n|---|---|")
    for name,terms in contrasts:   # terms: [(coef,cond),...]
        if not all(c in X for _,c in terms): continue
        d=[sum(k*X[c][key] for k,c in terms) for key in keys]; lo,hi=boot(d)
        res['contrasts'][name]=(100*sum(d)/n,100*lo,100*hi)
        print(f"| {name} | {100*sum(d)/n:+.1f} [{100*lo:+.1f}, {100*hi:+.1f}] |")
    OUT[model]=res
    return common
D=lambda a,b:[(1,a),(-1,b)]
c27=table('qwen3.5-27b',['direct','routing','direct_relay','retrieve','sidecar','ingress_plain_sym','ingress_no_requery','ingress','rag_only','full_load'],[
 ('routing − direct',D('routing','direct')),('direct_relay − direct',D('direct_relay','direct')),('sidecar − direct',D('sidecar','direct')),
 ('retrieve − routing',D('retrieve','routing')),('plain_sym − routing',D('ingress_plain_sym','routing')),('plain_sym − retrieve',D('ingress_plain_sym','retrieve')),
 ('plain_sym − sidecar',D('ingress_plain_sym','sidecar')),
 ('상호작용 (plain_sym − sidecar) − (routing − direct)',[(1,'ingress_plain_sym'),(-1,'sidecar'),(-1,'routing'),(1,'direct')]),
 ('no_requery − plain_sym',D('ingress_no_requery','ingress_plain_sym')),('no_requery − sidecar',D('ingress_no_requery','sidecar')),
 ('상호작용 (no_requery − sidecar) − (routing − direct)',[(1,'ingress_no_requery'),(-1,'sidecar'),(-1,'routing'),(1,'direct')]),('no_requery − retrieve',D('ingress_no_requery','retrieve')),
 ('상호작용 (ingress − sidecar) − (routing − direct)',[(1,'ingress'),(-1,'sidecar'),(-1,'routing'),(1,'direct')]),
 ('ingress − no_requery',D('ingress','ingress_no_requery')),('ingress − sidecar',D('ingress','sidecar')),('ingress − direct',D('ingress','direct')),
 ('full_load − ingress',D('full_load','ingress')),
 ('rag_only − direct',D('rag_only','direct')),('rag_only − retrieve',D('rag_only','retrieve')),('sidecar − rag_only',D('sidecar','rag_only')),('plain_sym − rag_only',D('ingress_plain_sym','rag_only')),
 ('no_requery − rag_only',D('ingress_no_requery','rag_only')),('ingress − rag_only',D('ingress','rag_only')),('full_load − rag_only',D('full_load','rag_only'))])
json.dump({s:sorted(v) for s,v in c27.items()},open(os.path.join(HERE,'common_tasks_27b.json'),'w'))
for m in ('deepseek-v4-flash','qwen3.5-9b'):
    table(m,['direct','routing','sidecar','ingress','full_load'],[('routing − direct',D('routing','direct')),('sidecar − direct',D('sidecar','direct')),
          ('ingress − direct',D('ingress','direct')),('ingress − sidecar',D('ingress','sidecar')),('sidecar − routing',D('sidecar','routing'))])
# 민감도 (s12): 셀마다 그 시나리오의 direct·sidecar 공통 과제. 자연 등급 = 생성기 전체 450과제의 상태 등급 분포
def natural(cell,maxday=None):
    return NAT[cell]['candidates_natural' if maxday is None else 'candidates_day1_10']
print("\n### 민감도 (s12): sidecar − direct")
print("| 셀 | 과제 | direct | sidecar | Δ(관측) [95% CI] | 등급별 Δ pp (n): A / B / C / D | 자연 등급 분포 A/B/C/D | Δ(자연 등급 가중) [95% CI] | Δ(1~10일 후보 분포 가중) |\n|---|---|---|---|---|---|---|---|---|")
OUT['sens']={}
for cell,(dd,sd) in {'base':(L[('B','qwen3.5-27b','direct','s12')],L[('B','qwen3.5-27b','sidecar','s12')]),
                     **{c:(L[('D',c,'direct','s12')],L[('D',c,'sidecar','s12')]) for c in ('K16k','lag1','warm10')}}.items():
    nat=natural(cell); nat10=natural(cell,10)
    Td,Ts=tasks(dd),tasks(sd); com=sorted(set(Td)&set(Ts))
    d={t:int(Ts[t]['exact'])-int(Td[t]['exact']) for t in com}; cls={t:Ts[t]['class'] for t in com}
    lo,hi=boot(list(d.values()))
    byc={k:[d[t] for t in com if cls[t]==k] for k in 'ABCD'}
    def wgain(sample,W):
        b={k:[d[t] for t in sample if cls[t]==k] for k in 'ABCD'}
        return sum(W[k]*sum(b[k])/len(b[k]) for k in 'ABCD' if b[k])/sum(W[k] for k in 'ABCD' if b[k])
    w=wgain(com,nat); w10=wgain(com,nat10); r=random.Random(1); bs=[]
    for _ in range(10000):
        smp=[]
        for k in 'ABCD':   # 등급 안에서 다시 뽑기 (층화)
            pool=[t for t in com if cls[t]==k]; smp+=[pool[r.randrange(len(pool))] for _ in pool]
        bs.append(wgain(smp,nat))
    bs.sort()
    acc=lambda T:100*sum(T[t]['exact'] for t in com)/len(com)
    accc=lambda T,k:100*sum(T[t]['exact'] for t in com if cls[t]==k)/max(1,sum(cls[t]==k for t in com))
    OUT['sens'][cell]={'n':len(com),'direct':acc(Td),'sidecar':acc(Ts),'gain':100*sum(d.values())/len(com),'ci':(100*lo,100*hi),
        'by_class':{k:{'gain':100*sum(v)/len(v) if v else None,'n':len(v),'direct':accc(Td,k),'sidecar':accc(Ts,k)} for k,v in byc.items()},
        'natural':nat,'natural_d1_10':nat10,'gain_weighted':100*w,'ci_w':(100*bs[250],100*bs[9749]),'gain_weighted_d1_10':100*w10}
    o=OUT['sens'][cell]
    print(f"| {cell} | {len(com)} | {o['direct']:.1f} | {o['sidecar']:.1f} | {o['gain']:+.1f} [{o['ci'][0]:+.1f}, {o['ci'][1]:+.1f}] | "+
          " / ".join(f"{v['gain']:+.0f} ({v['n']})" for v in o['by_class'].values())+" | "+"/".join(f"{100*nat[k]:.0f}" for k in 'ABCD')+
          f" | {o['gain_weighted']:+.1f} [{o['ci_w'][0]:+.1f}, {o['ci_w'][1]:+.1f}] | {o['gain_weighted_d1_10']:+.1f} |")
print("\n등급별 정확도 (direct → sidecar):")
for cell,o in OUT['sens'].items(): print(f"- {cell}: "+", ".join(f"{k} {v['direct']:.0f}→{v['sidecar']:.0f} (n={v['n']})" for k,v in o['by_class'].items()))
json.dump(OUT,open(OUTF,'w'),indent=1,ensure_ascii=False)
