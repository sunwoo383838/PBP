"""그룹 경계 모듈: 들어오는 요청은 Ingress, 나가는 요청은 Egress(I+E)로 처리한다.

Ingress (모든 경계 조건에서 담당자 선택은 같다. 조건마다 다른 것은 전달 방식뿐):
    1 해석(LLM ①) → 2 별칭 해소 → 3 need_more(해석에 빠진 항목) → 4 그룹 기록 검색(색인 entities + catalog 연결 +
    하이브리드 이력 검색) → 5 LLM이 검색 결과로 담당자 선택 또는 referral(소유권 예외 기록) → 6 내부 질의(요청 원문,
    인원 상한 없음, 과제 예산이 상한) → 전달
        forward   응답 원문을 그대로 돌려준다 (Routing). 검색 결과는 선택에만 쓰고, 출력은 router_guard로 검사
        assemble  LLM ②가 증거 + 응답으로 조립 (ingress_sel · Ingress · I+E)
                  boundary_state: 이 창구의 과거 교차 문답·제공 버전·진행 중 요청을 조립에 쓴다
                  version_marks: DB 버전(같은 키·버전 번호)을 보여 주고 버전을 표시하게 한다
                  requery: 빠진 항목만 1회 재질의 (활동 중 담당자에게, 떠났으면 그 이력 구간을 같은 역할 담당자에게)
Egress (I+E):
    관련 기록(egress_log: 같은 엔티티, 유효한 referral, 1k 토큰 상한) → LLM ③ 대상 그룹·보완 질문 → referral 기록이
    있으면 그 그룹으로(코드가 덮어씀) → 결과 처리(referral 1회 재전송, need_more 1회 보완 재전송) → egress_log 기록

모든 결정은 boundary_decision 사건으로 WAL에 남기고, 검색 기록은 obs/retrievals.jsonl에 남긴다.
"""
import json
from dataclasses import dataclass, field

from gbg.contracts.conditions import Condition
from gbg.contracts.envelope import Request, Response, SourcedValue
from gbg.retrieval.evidence import Evidence, build_evidence
from gbg.retrieval.hybrid import GroupRetriever, authorize
from gbg.retrieval.normalize import normalize

from . import prompts as P
from .router_guard import check_router_output


def _dumps(x) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def _fn(tool: dict) -> dict:
    return {"type": "function", "function": tool}


@dataclass
class Interpretation:
    entities: list[str]
    attribute: str
    purpose: str
    missing: list[str]


@dataclass
class _Trace:
    """경계 결정 하나의 기록 (boundary_decision 사건)."""
    rec: dict = field(default_factory=dict)


class BoundaryModule:
    def __init__(self, group: str, cond: Condition, *, retriever: GroupRetriever, resolver, count, format_retries: int,
                 egress_cap: int = 1000):
        self.group, self.cond = group, cond
        self.retriever, self.resolver, self.count = retriever, resolver, count
        self.format_retries, self.egress_cap = format_retries, egress_cap
        self.in_progress: list[dict] = []                                 # 이 창구가 지금 처리 중인 요청

    # ─────────────────────────── 공통 ───────────────────────────
    def _ctx(self, ctx, span, req: Request):
        from gbg.kernel.scheduler import AgentContext
        return AgentContext(ctx.kernel, span, f"boundary:{self.group}", self.group, "boundary", ctx.day, ctx.round,
                            ctx.task_id, req.hop, req.lineage, (), serving=req.rid, boundary=self.group)

    def _group_desc(self, stores) -> str:
        c = stores.cards.group_cards[self.group]
        return f"{self.group} ({c.description}). Work: " + "; ".join(f"{s.name}: {s.description}" for s in c.skills)

    async def _tool(self, bctx, step: list, name: str, system: str, user: str, tool: dict, check):
        """도구 하나만 부르게 하고 인자를 검사한다. 형식 오류는 format_retries번까지 다시 묻고, 끝내 실패하면 None."""
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        tools = [_fn(tool)]
        tdt = self.count(_dumps(tools))
        for _ in range(self.format_retries + 1):
            step[0] += 1
            est = self.count(_dumps(messages)) + tdt
            res = await bctx.llm(messages, tools, step[0], {"boundary_step": name, "tool_def_tokens": tdt}, estimate=est)
            why = "no_tool_call"
            for c in res.message["tool_calls"]:
                if c["name"] != tool["name"]:
                    continue
                try:
                    args = json.loads(c["arguments"])
                except ValueError:
                    why = "arguments are not JSON"
                    break
                ok, val = check(args) if isinstance(args, dict) else (False, "arguments are not an object")
                if ok:
                    return val
                why = val
                break
            messages += [{"role": "assistant", "content": res.message["content"] or ""},
                         {"role": "user", "content": P.FORMAT_NUDGE.format(tool=tool["name"]) + f" ({why})"}]
        return None

    # ─────────────────────────── Ingress ───────────────────────────
    async def ingress(self, ctx, span, req: Request) -> Response:
        k = ctx.kernel
        stores = k.stores
        bctx = self._ctx(ctx, span, req)
        step = [0]
        trace = {"stage": "ingress", "group": self.group, "rid": req.rid, "from_group": req.from_group,
                 "question": req.question, "deliver": self.cond.ingress.deliver}
        self.in_progress.append({"rid": req.rid, "question": req.question, "from_group": req.from_group})
        try:
            resp = await self._ingress(bctx, span, req, stores, step, trace)
        finally:
            self.in_progress.pop()
        trace["status"] = resp.status
        span.emit("boundary_decision", bctx.actor, {"task_id": ctx.task_id, **trace})
        return resp

    async def _ingress(self, bctx, span, req, stores, step, trace) -> Response:
        cfg = self.cond.ingress
        day = bctx.day
        text = req.question + (f"\nPurpose: {req.purpose}" if req.purpose else "")

        # 1 해석
        def check_interp(a):
            ents, missing = a.get("entities", []), a.get("missing", [])
            if not (isinstance(ents, list) and all(isinstance(x, str) for x in ents)):
                return False, "entities must be a list of strings"
            if not (isinstance(missing, list) and all(isinstance(x, str) for x in missing)):
                return False, "missing must be a list of strings"
            if not isinstance(a.get("attribute", ""), str):
                return False, "attribute must be a string"
            return True, Interpretation(ents, a.get("attribute", ""), a.get("purpose", "") or "", missing)
        it = await self._tool(bctx, step, "interpret", P.INTERPRET_SYSTEM.format(group_desc=self._group_desc(stores)),
                              text, P.INTERPRET_TOOL, check_interp) or Interpretation([], "", "", [])
        trace["interpretation"] = it.__dict__

        # 2 별칭 해소 (표면형마다 + 요청 전체 태깅)
        resolved: dict[str, None] = {}
        for surface in it.entities:
            for e in (await self.resolver.resolve(surface)).entities:
                resolved[e] = None
        for e in self.resolver.tag(req.question):
            resolved[e] = None
        entities = list(resolved)
        trace["entities"] = entities

        # 3 need_more: 해석에 빠진 항목이 있으면 되묻는다
        if it.missing:
            trace["action"] = "need_more"
            return Response(rid=req.rid, status="need_more", answer="More information is needed: " + "; ".join(it.missing),
                            values=[], missing=[], referral_to=None, need=list(it.missing), as_of=day)

        # 4 그룹 기록 검색
        rec = authorize(bctx.kernel.guard, bctx.actor, self.group, self.group)
        query = f"{req.question} {it.attribute}".strip()
        ev = await build_evidence(self.retriever, query, entities)
        span.emit("retrieval", bctx.actor, {"task_id": bctx.task_id, "rid": req.rid, "group": self.group,
                                             "selected": ev.log["selected"], "cap_reached": ev.cap_reached},
                  obs=[("access", {"day": day, "round": bctx.round, **rec}),
                       ("retrievals", {"day": day, "round": bctx.round, "rid": req.rid, **ev.log})])

        # 5 담당자 선택 또는 referral
        members = self._members(stores)
        others = [c for c in stores.cards.directory("group_cards") if c.group != self.group]
        route_user = (f"Request from {req.from_group}:\n{text}\n\nUnderstood as: attribute={it.attribute!r}, "
                      f"entities={entities or it.entities}\n\nMembers:\n"
                      + "\n".join(f"- {a} | {role} | {desc}" for a, role, desc in members)
                      + "\n\nOther groups:\n" + "\n".join(f"- {c.group} | {c.description}" for c in others)
                      + "\n\nGroup records found:\n" + (ev.text or "(none)"))
        active = {a for a, _, _ in members}

        def check_route(a):
            if a.get("action") not in ("select", "referral"):
                return False, "action must be select or referral"
            if a["action"] == "referral" and a.get("referral_to") not in {c.group for c in others}:
                return False, "referral_to must be a group id from the group list"
            agents = a.get("agents", [])
            if not (isinstance(agents, list) and all(isinstance(x, str) for x in agents)):
                return False, "agents must be a list of member ids"
            return True, a
        route = await self._tool(bctx, step, "route", P.ROUTE_SYSTEM.format(group_desc=self._group_desc(stores)),
                                 route_user, P.ROUTE_TOOL, check_route) or {"action": "select", "agents": []}
        if route["action"] == "referral":
            trace.update(action="referral", referral_to=route["referral_to"], reason=route.get("reason"))
            return Response(rid=req.rid, status="referral", answer=f"This is handled by {route['referral_to']}.",
                            values=[], missing=[], referral_to=route["referral_to"], need=[], as_of=day)
        chosen = [a for a in dict.fromkeys(route.get("agents", [])) if a in active]
        if not chosen:                                                     # LLM이 고르지 못함: 검색된 처리자 중 활동 중인 사람
            chosen = [a for a in ev.log.get("holders", []) if a in active]
        trace.update(action="select", selected=chosen, proposed=route.get("agents", []), reason=route.get("reason"))
        if not chosen:
            return Response(rid=req.rid, status="partial", answer="No member of this group could be identified for "
                            "this request.", values=[], missing=[it.attribute or req.question], referral_to=None,
                            need=[], as_of=day)

        # 6 내부 질의 (요청 원문 그대로)
        replies = [(a, await bctx.ask(a, req.question, req.purpose, hop=req.hop)) for a in chosen]

        if cfg.deliver == "forward":
            return self._forward(bctx, req, replies, ev, trace)
        return await self._assemble(bctx, span, req, text, it, entities, ev, replies, stores, step, trace)

    def _members(self, stores) -> list[tuple[str, str, str]]:
        cards = stores.cards
        out = []
        for a, (g, role) in sorted(stores.members.items()):
            if g != self.group or a not in cards.active:
                continue
            card = cards.agent_cards.get(a)
            desc = "; ".join(s.description for s in card.skills) if card else role
            out.append((a, role, desc))
        return out

    def _forward(self, bctx, req, replies, ev: Evidence, trace) -> Response:
        pieces = [r.answer for _, r in replies]
        answer = "\n\n".join(f"[Reply {i}] {p}" for i, p in enumerate(pieces, 1))
        values = [SourcedValue(value=v.value, source=f"reply {i}") for i, (_, r) in enumerate(replies, 1) for v in r.values]
        missing = list(dict.fromkeys(m for _, r in replies for m in r.missing))
        ok = [r for _, r in replies if r.status in ("ok", "partial")]
        status = "error" if not ok else ("ok" if all(r.status == "ok" for r in ok) and not missing else "partial")
        guard = check_router_output(req.question, {a: req.question for a, _ in replies}, pieces, pieces,
                                    [it.text for it in ev.items])
        trace["router_guard"] = guard.violations
        if not guard.ok:                                                   # 검색 결과가 라우터 출력으로 샘: 런 무효
            bctx.span.emit("boundary_decision", bctx.actor, {"task_id": bctx.task_id, "stage": "router_guard",
                                                               "group": self.group, "rid": req.rid,
                                                               "violations": guard.violations},
                           obs=[("run_invalid", {"reason": "router_output_leak", "rid": req.rid,
                                                 "violations": guard.violations})])
        return Response(rid=req.rid, status=status, answer=answer, values=values, missing=missing, referral_to=None,
                        need=[], as_of=bctx.day)

    def _versions(self, stores, entities: list[str], day: int) -> list[str]:
        """같은 DB 키·버전 번호로 묶은 사실: 엔티티가 키에 들어간 레코드의 등록된 버전들."""
        out = []
        for key in stores.db.keys(self.group):
            if not set(key.split("/")[1:]) & set(entities):
                continue
            for v in stores.db.versions(self.group, key):
                if v.db_day <= day:
                    out.append(f"{key} v{v.v} (registered day {v.db_day}): {_dumps(v.value)}")
        return out

    def _state(self, stores, entities: list[str]) -> list[str]:
        """경계 상태: 이 창구의 과거 교차 문답(같은 엔티티)과 제공 버전, 진행 중 요청."""
        out = [f"day {x['day']}: request from {x['from_group']}: {x['question']!r} → answered {x['answer']!r}"
               + (f" (versions given: {', '.join(x['versions'])})" if x["versions"] else "")
               for x in stores.boundary_log.lookup(self.group, entities)]
        out += [f"in progress: request from {x['from_group']}: {x['question']!r}" for x in self.in_progress[:-1]]
        return out

    async def _assemble(self, bctx, span, req, text, it, entities, ev: Evidence, replies, stores, step, trace):
        cfg = self.cond.ingress
        versions = self._versions(stores, entities, bctx.day) if cfg.version_marks else []
        state = self._state(stores, entities) if cfg.boundary_state else []
        system = P.ASSEMBLE_SYSTEM.format(state_cite=P.STATE_CITE if state else "",
                                          version_rule=P.VERSION_RULE if cfg.version_marks else "")

        def user_text(replies):
            parts = [f"Request from {req.from_group}:\n{text}", "Replies:\n" + "\n".join(
                f"[R{i}] ({r.status}) {r.answer}" + (f" | values: {_dumps([v.model_dump() for v in r.values])}" if r.values else "")
                + (f" | missing: {r.missing}" if r.missing else "") for i, (_, r) in enumerate(replies, 1))]
            parts.append("Group records:\n" + (ev.text or "(none)"))
            if versions:
                parts.append("Database versions:\n" + "\n".join(f"[D{i}] {v}" for i, v in enumerate(versions, 1)))
            if state:
                parts.append("Earlier exchanges of this desk:\n" + "\n".join(f"[S{i}] {s}" for i, s in enumerate(state, 1)))
            return "\n\n".join(parts)

        def check_answer(a):
            if not isinstance(a.get("answer"), str):
                return False, "answer must be a string"
            try:
                vals = [SourcedValue(value=x["value"], source=x["source"]) for x in a.get("values", [])]
            except (KeyError, TypeError):
                return False, "each values item needs value and source"
            miss = a.get("missing", [])
            if not (isinstance(miss, list) and all(isinstance(x, str) for x in miss)):
                return False, "missing must be a list of strings"
            return True, (a["answer"], vals, miss)

        out = await self._tool(bctx, step, "assemble", system, user_text(replies), P.ANSWER_TOOL, check_answer)
        requeried = []
        if out is not None and out[2] and cfg.requery:                     # 빠진 항목만 1회 재질의
            more = await self._requery(bctx, req, out[2], replies, ev, stores)
            requeried = [a for a, _ in more]
            if more:
                replies = replies + more
                out = await self._tool(bctx, step, "assemble", system, user_text(replies), P.ANSWER_TOOL,
                                       check_answer) or out
        trace["requery"] = requeried
        if out is None:
            return Response(rid=req.rid, status="error", answer="assembly_failed", values=[], missing=[],
                            referral_to=None, need=[], as_of=bctx.day)
        answer, values, missing = out
        cited = sorted({v.source for v in values})
        trace.update(sources=cited, versions_given=[versions[int(s[1:]) - 1].split(" (")[0] for s in cited
                                                    if s[:1] == "D" and s[1:].isdigit() and 0 < int(s[1:]) <= len(versions)],
                     answer=answer)
        return Response(rid=req.rid, status="partial" if missing else "ok", answer=answer, values=values,
                        missing=missing, referral_to=None, need=[], as_of=bctx.day)

    async def _requery(self, bctx, req, missing, replies, ev: Evidence, stores):
        k = bctx.kernel
        asked = {a for a, _ in replies}
        targets = {a: "" for a in asked if k.is_active(a)}
        role_of = {a: r for a, (g, r) in stores.members.items() if g == self.group}
        for it in ev.items:                                                # 떠난 처리자의 이력 구간 → 같은 역할 담당자
            if it.agent in role_of and not k.is_active(it.agent):
                heir = next((a for a, r in sorted(role_of.items()) if r == role_of[it.agent] and k.is_active(a)), None)
                if heir:
                    targets[heir] = targets.get(heir, "") + f"- day {it.day}: {it.text}\n"
        out = []
        for a, records in targets.items():
            q = P.REQUERY_TEXT.format(question=req.question, missing="; ".join(missing),
                                      excerpt=P.EXCERPT_TEXT.format(records=records.rstrip()) if records else "")
            out.append((a, await bctx.ask(a, q, req.purpose, hop=req.hop)))
        return out

    # ─────────────────────────── Egress (I+E) ───────────────────────────
    def _related(self, stores, question: str) -> list[str]:
        """egress_log에서 요청에 언급된 엔티티의 기록(최신부터)과 유효한 referral. 1k 토큰 상한."""
        q = normalize(question)
        recs = [r for r in stores.egress_log.all(self.group) if normalize(r.entity) and normalize(r.entity) in q]
        lines, total = [], 0
        for r in sorted(recs, key=lambda r: -r.day):
            line = (f"day {r.day}: {r.entity} / {r.attr} → {r.to_group}: {r.status}"
                    + (f" (referred to {r.referral_to})" if r.referral_to else ""))
            t = self.count(line)
            if total + t > self.egress_cap:
                break
            lines.append(line)
            total += t
        return lines

    async def egress(self, ctx, span, req: Request) -> Response:
        k = ctx.kernel
        stores = k.stores
        bctx = self._ctx(ctx, span, req)
        step = [0]
        others = [c for c in stores.cards.directory("group_cards") if c.group != self.group]
        related = self._related(stores, req.question)
        trace = {"stage": "egress", "group": self.group, "rid": req.rid, "question": req.question, "related": related}
        directory = "\n".join(f"- {c.group} | {c.description} | work: {', '.join(s.name for s in c.skills)}" for c in others)
        user = (f"Question: {req.question}\nPurpose: {req.purpose or ''}\n\nRelated records of this desk:\n"
                + ("\n".join(related) or "(none)"))
        valid = {c.group for c in others}

        def check_dispatch(a):
            ts = a.get("targets")
            if not (isinstance(ts, list) and ts and all(isinstance(t, dict) and t.get("group") in valid
                                                         and isinstance(t.get("question"), str) for t in ts)):
                return False, "targets must be a non-empty list of {group, question} with groups from the list"
            if not isinstance(a.get("entity"), str) or not isinstance(a.get("attr"), str):
                return False, "entity and attr must be strings"
            return True, a
        d = await self._tool(bctx, step, "dispatch", P.DISPATCH_SYSTEM.format(directory=directory), user,
                             P.DISPATCH_TOOL, check_dispatch)
        if d is None:
            trace["action"] = "dispatch_failed"
            span.emit("boundary_decision", bctx.actor, {"task_id": ctx.task_id, **trace})
            return Response(rid=req.rid, status="error", answer="dispatch_failed", values=[], missing=[],
                            referral_to=None, need=[], as_of=ctx.day)
        # 경로 확정: 같은 (엔티티, 속성)에 유효한 referral 기록이 있으면 그 그룹으로 (코드가 LLM 결정을 덮어씀)
        ref = stores.egress_log.referral(self.group, d["entity"], d["attr"], ctx.day)
        targets = [dict(t) for t in d["targets"]]
        if ref:
            targets = [{"group": ref, "question": targets[0]["question"]}]
        trace.update(entity=d["entity"], attr=d["attr"], targets=targets, referral_override=ref)
        results = []
        for t in targets:
            r = await bctx.ask_group(t["group"], t["question"], req.purpose)
            sent = [(t["group"], t["question"], r)]
            if r.status == "referral" and r.referral_to in valid:          # referral → 그 그룹에 1회 재전송
                r = await bctx.ask_group(r.referral_to, t["question"], req.purpose)
                sent.append((sent[0][2].referral_to, t["question"], r))
            elif r.status == "need_more":                                  # 기록으로 보완해 1회 재전송
                fill = await self._tool(bctx, step, "dispatch", P.DISPATCH_SYSTEM.format(directory=directory),
                                        user + f"\n\n{t['group']} needs more information: {'; '.join(r.need)}",
                                        P.DISPATCH_TOOL, check_dispatch)
                q2 = next((x["question"] for x in (fill or {}).get("targets", []) if x["group"] == t["group"]), None)
                if q2 and q2 != t["question"]:
                    r = await bctx.ask_group(t["group"], q2, req.purpose)
                    sent.append((t["group"], q2, r))
            results.append(r)
            for g, q, x in sent:
                trace.setdefault("log", []).append({"day": ctx.day, "entity": d["entity"], "attr": d["attr"],
                                                    "to_group": g, "question": q, "status": x.status,
                                                    "referral_to": x.referral_to})
        span.emit("boundary_decision", bctx.actor, {"task_id": ctx.task_id, **trace})
        if len(results) == 1:
            return results[0].model_copy(update={"rid": req.rid})
        answer = "\n\n".join(f"[From {t['group']}] ({r.status}) {r.answer}" for t, r in zip(targets, results))
        values = [SourcedValue(value=v.value, source=f"{t['group']}:{v.source}") for t, r in zip(targets, results)
                  for v in r.values]
        missing = list(dict.fromkeys(m for r in results for m in r.missing))
        need = list(dict.fromkeys(n for r in results if r.status == "need_more" for n in r.need))
        ok = any(r.status in ("ok", "partial") for r in results)
        status = ("ok" if all(r.status == "ok" for r in results) else "partial") if ok else ("need_more" if need else "error")
        return Response(rid=req.rid, status=status, answer=answer, values=values, missing=missing, referral_to=None,
                        need=need if status == "need_more" else [], as_of=ctx.day)
