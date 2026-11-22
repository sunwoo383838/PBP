"""실행 기록(WAL)과 정답 원장에서 과제마다 필요한 그룹과 담당자가 실제로 요청을 보낸 그룹을 뽑는다 (request_delivery.py의 입력).

    python extract_requests.py RUNS_JSON SCEN_DIR OUT.json.gz
RUNS_JSON: {모델: {조건: {시드: 실행 폴더}}}. SCEN_DIR 아래 D5_<시드>_T45/private/gold.jsonl.
필요한 그룹 = 정답 원장의 원격 need(local 아님)가 속한 그룹. 요청한 그룹 = 담당자가 보낸 요청(다른 요청을 처리하는 중이 아닌
것)의 to_group, 없으면 to_agent의 그룹. 1~10일.
"""
import json,sys,gzip,collections
RUNS,SCEN,OUT=json.load(open(sys.argv[1])),sys.argv[2],sys.argv[3]
grp=lambda a:a.split('.')[0].upper() if a else ''
gold={}
out={}
for model,conds in RUNS.items():
    for cond,seeds in conds.items():
        for s,run in seeds.items():
            if s not in gold: gold[s]={g['wid']:g for g in map(json.loads,open(f'{SCEN}/D5_{s}_T45/private/gold.jsonl')) if g['day']<=10}
            asked=collections.defaultdict(set)
            for l in open(run+'/wal/events.jsonl'):
                e=json.loads(l)
                if e['type']!='message' or e['day']>10: continue
                p=e['payload']; t=p.get('task_id')
                if p.get('kind')=='request' and p.get('serving') is None and t in gold[s] and p.get('from_agent')==gold[s][t]['assignee']:
                    asked[t].add(p.get('to_group') or grp(p.get('to_agent')))
            out.setdefault(model,{}).setdefault(cond,{})[s]={t:{'needed':sorted({n['group'] for n in g['needs'] if not n.get('local')}),
                                                               'asked':sorted(asked[t])} for t,g in gold[s].items()}
with gzip.GzipFile(OUT,'wb',mtime=0) as f: f.write(json.dumps(out,separators=(',',':')).encode())
