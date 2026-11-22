"""ingress_no_requery − ingress_plain_sym 원인 분해 (27B, 공통 과제).

    python decomposition.py RUNS_PLAIN RUNS_NOREQ SCEN_DIR [LEDGER_DIR] [COMMON_JSON]
RUNS_*: 조건 폴더(아래에 s12·s13·s14). 저장소 루트에서 실행(gbg.scoring 사용).
응답당 길이·붙은 구성원 답 수·상태(partial 등)·조립 실패 처리·과거 문답([S#]) 인용·재요청·과제당 호출과 토큰을 두 조건에서 세고,
plain_sym은 틀리고 no_requery는 맞힌 과제의 오답 슬롯마다 제출 값과 정답 값이 plain_sym 응답의 어디(구성원 답 문장과 그 항목 /
창구 보충 문장·항목·제안)에 있었는지 대조한다. 값 대조는 문자열·숫자 일치라 근사다.
"""
import json,sys,collections,re,gzip,os,statistics as st
sys.path.insert(0,os.getcwd())
from gbg.scoring.proposals import _matches, _nums
from gbg.scoring.delivery import _norm
HERE=os.path.dirname(os.path.abspath(__file__))
RUN={'plain_sym':sys.argv[1],'no_requery':sys.argv[2]}; SCEN=sys.argv[3]
LED=sys.argv[4] if len(sys.argv)>4 else os.path.join(HERE,'ledgers')
COMMON=json.load(open(sys.argv[5] if len(sys.argv)>5 else os.path.join(HERE,'common_tasks_27b.json')))
NOTE='[Notes from the group\'s records]'
SRE=re.compile(r'\bS\d+\b')
def load(c,s):
    ev=[json.loads(l) for l in open(f'{RUN[c]}/{s}/wal/events.jsonl')]
    return [e for e in ev if e['day']<=10]
def ledger(c,s): return {t['task_id']:t for t in json.load(gzip.open(f'{LED}/A__ingress_{c}__{s}.json.gz'))['tasks']}
gold={s:{g['wid']:g for g in map(json.loads,open(f'{SCEN}/D5_{s}_T45/private/gold.jsonl'))} for s in ('s12','s13','s14')}
agg={}; per_task={}
for c in RUN:
    A=collections.defaultdict(list); C=collections.Counter()
    for s in ('s12','s13','s14'):
        ev=load(c,s); L=ledger(c,s)
        keep=set(COMMON[s]) if COMMON else {t for t,x in L.items() if not x['unreachable'] and x['day']<=10}
        bd={e['payload']['rid']:e['payload'] for e in ev if e['type']=='boundary_decision' and e['payload'].get('stage')=='ingress'}
        req={e['payload']['task_id']:e['payload']['agent'] for e in ev if e['type']=='task_delivered'}
        asks=collections.Counter(); resp=collections.defaultdict(list)
        for e in ev:
            p=e['payload']
            if e['type']=='message' and p.get('kind')=='request' and p.get('to_agent') is None and not p.get('serving') and p.get('task_id') in keep:
                asks[(p['task_id'],p['to_group'])]+=1
            if e['type']=='message' and p.get('kind')=='response' and e['actor'].startswith('boundary') and p.get('to_agent') is None and not p.get('serving') and p.get('task_id') in keep:
                r=p['response']; d=bd.get(p['rid'],{})
                txt=r['answer'] or ''
                A['len_chars'].append(len(txt))
                A['n_selected'].append(len(d.get('selected') or []))
                A['n_reply_blocks'].append(len(re.findall(r'^\[Reply \d+\]',txt,re.M)))
                C['resp']+=1; C['status_'+r['status']]+=1
                C['fallback']+=bool(d.get('assembly_fallback'))
                vals=(r.get('items') or [])
                adds=[x for x in vals if not str(x.get('ref','')).startswith('Reply ')]
                C['values']+=len(vals); C['values_desk']+=len(adds)
                srefs=[x for x in vals if SRE.search(str(x.get('ref','')))]
                sonly=[x for x in srefs if not re.search(r'\b[REV]\d+\b|Reply ',str(x.get('ref','')))]
                C['values_S']+=len(srefs); C['values_S_only']+=len(sonly)
                C['resp_with_S_source']+=any(SRE.fullmatch(x) for x in d.get('sources') or [])
                C['resp_S_in_answer']+=bool(re.search(r'\[S\d+\]',txt))
                C['resp_with_proposals']+=bool(r.get('proposals')); C['proposals']+=len(r.get('proposals') or [])
                C['resp_with_missing']+=bool(r.get('missing'))
                resp[p['task_id']].append(r)
        for (t,g),n in asks.items():
            C['task_group_pairs']+=1; C['reasks']+=n-1; C['pairs_reasked']+=n>1
        for t in keep:
            x=L[t]; A['calls'].append(x['calls']); A['tokens'].append(x['tokens'])
            A['req_calls'].append(x['components'].get('requester',{}).get('calls',0)); A['bnd_calls'].append(x['components'].get('boundary',{}).get('calls',0))
            A['asks'].append(sum(n for (tt,g),n in asks.items() if tt==t))
            per_task[(c,s,t)]={'exact':x['exact'],'slots':x['slots'],'resp':resp.get(t,[])}
        C['tasks']+=len(keep)
    agg[c]=(A,C)
print('| 지표 | plain_sym | no_requery |\n|---|---|---|')
def m(c,k): v=agg[c][0][k]; return f"{st.mean(v):.1f} (중앙 {st.median(v):.0f})"
for k in ('len_chars','n_selected','n_reply_blocks','calls','tokens','req_calls','bnd_calls','asks'):
    print(f"| {k} | {m('plain_sym',k)} | {m('no_requery',k)} |")
keys=sorted(set(agg['plain_sym'][1])|set(agg['no_requery'][1]))
for k in keys: print(f"| {k} | {agg['plain_sym'][1][k]} | {agg['no_requery'][1][k]} |")
# 따른 쪽: plain_sym 오답·no_requery 정답
def answer_of(s,t,c):
    for l in open(f'{RUN[c]}/{s}/wal/events.jsonl'):
        e=json.loads(l)
        if e['type']=='answer' and e['payload'].get('task_id',None) in (t,None) and e['actor']=='agent:'+gold[s][t]['assignee'] and e['day']==gold[s][t]['day']:
            return e['payload'].get('answer') or {}
    return {}
def has(v,texts):
    if isinstance(v,bool) or v is None: return None
    if isinstance(v,(list,dict)): v=json.dumps(v)
    v=str(v)
    if _nums(v): return _matches(v,texts)
    return any(_norm(v) and _norm(v) in _norm(x) for x in texts)
F=collections.Counter(); rows=[]; X=collections.Counter()
for s in ('s12','s13','s14'):
    ans_cache={}
    for (c,ss,t),x in per_task.items():
        if c!='plain_sym' or ss!=s or x['exact']: continue
        y=per_task.get(('no_requery',s,t))
        if not y or not y['exact']: continue
        a=answer_of(s,t,'plain_sym'); g=gold[s][t]['gold']
        member=[];desk=[]
        for r in x['resp']:
            txt=r['answer'] or ''; head,_,notes=txt.partition(NOTE)
            member.append(head); member+= [str(i['value']) for i in r['items'] if str(i.get('ref','')).startswith('Reply ')]
            desk.append(notes); desk+=[str(i['value']) for i in r['items'] if not str(i.get('ref','')).startswith('Reply ')]
            desk+=[str(p.get('value')) for p in r.get('proposals') or []]
        for slot,ok in x['slots'].items():
            if ok: continue
            v=a.get(slot); gv=g.get(slot)
            wm,wd=has(v,member),has(v,desk); gm,gd=has(gv,member),has(gv,desk)
            if wm is None: F['wrong_val_bool_or_missing']+=1; continue
            F['slots']+=1
            F['wrong:'+('both' if wm and wd else 'member_text' if wm else 'desk' if wd else 'neither')]+=1
            loc=lambda m_,d_:'both' if m_ and d_ else 'member' if m_ else 'desk' if d_ else 'neither'
            if gm is not None: X[(loc(gm,gd),loc(wm,wd))]+=1
            if gm is not None: F['gold:'+('both' if gm and gd else 'member_text' if gm else 'desk' if gd else 'neither')]+=1
            ytxt=[]
            for r in y['resp']:
                ytxt.append(r['answer'] or ''); ytxt+=[str(i['value']) for i in r['items']]; ytxt+=[str(q.get('value')) for q in r.get('proposals') or []]
            gy=has(gv,ytxt)
            if gm is not None: F['gold_in_no_requery_resp:'+str(gy)]+=1
            if gm is not None: F['gold_plain(any)/gold_noreq: '+str(bool(gm or gd))+'/'+str(gy)]+=1
            rows.append((s,t,slot,v,gv,wm,wd,gm,gd,gy))
        F['tasks']+=1
print('\n따른 쪽 (plain_sym 오답·no_requery 정답):',dict(F))

print('\n교차표 (행: 정답 값이 plain_sym 응답의 어디에 있었나, 열: 제출한 오답 값이 어디에 있었나)')
cats=['member','desk','both','neither']
print('| 정답 위치 \\ 오답 출처 | '+' | '.join(cats)+' | 합 |'); print('|'+'---|'*6)
for g in cats: print(f'| {g} | '+' | '.join(str(X[(g,w)]) for w in cats)+f' | {sum(X[(g,w)] for w in cats)} |')
# 과제 단위 정확도 요약
for c in RUN:
    n=sum(1 for k in per_task if k[0]==c); a=sum(v['exact'] for k,v in per_task.items() if k[0]==c); print(c,'tasks',n,'acc',round(100*a/n,1))
