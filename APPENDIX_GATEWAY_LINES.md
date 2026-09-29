# 부록: 경계 모듈 전용 문구의 지식·메커니즘 분류 (2026-09-30)

원칙: **게이트웨이를 끌어내리지 않고, 공통 지식은 모두에게 끌어올린다.**

- **지식:** 세계·규칙에 대한 사실로, 어떤 조건의 에이전트든 데이터를 해석하려면 필요한 것입니다. 게이트웨이에서 빼지 않고, 같은 문장을 모든 조건·모든 역할의 공통 규정 블록(`render_rules`의 끝, `KNOWLEDGE`)에 넣습니다. 게이트웨이 쪽 문구는 공통 문장과 글자 그대로 같게 맞추고, 메커니즘 지시만 덧붙입니다.
- **메커니즘:** 게이트웨이만 할 수 있는 일을 시키는 것입니다. 그대로 둡니다.
- **형식(공통):** 출력 형식에 관한 지시로, 같은 취지의 문구가 이미 모든 조건의 요청자·응답자 프롬프트에 있습니다. 그대로 둡니다.

대상: PROMPT_MANIFEST의 조건 간 diff에서 경계 모듈 호출(해석·선택·조립·재조립·Egress 정리·재질의·재발신)에만 있는 줄 전부입니다.

## 공통 규정 블록에 들어간 지식 문장 (모든 조건·모든 역할·모든 LLM 호출)

| # | 문장 |
|---|---|
| K1 | When sources disagree, the most recent record counts. |
| K2 | Database versions of the same key are the same fact: the latest registered version replaces earlier ones. |
| K3 | A reply covers only what its sender's records hold and can be incomplete. |
| K4 | Task IDs (such as W-00070) appear only in tasks, not in other areas' records. |

이 네 문장 앞에는 이미 공통인 두 문장이 있습니다. 기간 규약("until day N" 당일 포함)과 "Records and the database" 문장입니다.

## 분류표

| 호출 | 줄 (변경 전 원문) | 분류 | 조치 |
|---|---|---|---|
| 해석 | You are the intake desk … Read the request and extract, without answering it: entities / attribute / purpose | 메커니즘 | 유지 |
| 해석 | First think it through step by step …, then call the interpret tool once. | 메커니즘 (호출 형식) | 유지 |
| 선택 | Decide who in this group should answer … You see the request, the members …, and the group records found | 메커니즘 | 유지 |
| 선택 | Choose every member who is likely to hold the requested information. There is no limit on the number of members. | 메커니즘 | 유지 |
| 선택 | Prefer members that the records show handling this subject; departed members cannot be asked. | 메커니즘 (구성원 선택 제약) | 유지 |
| 선택 | Refer the request to another group only if a record states that another group has been agreed to execute or own this subject for the relevant period. Cite that record … | 메커니즘 (referral 판단). 사실 부분(집행 주체 예외)은 이미 해당 그룹 규정 owner_exception에 있음 | 유지 |
| 선택 | A group's usual area of work is not a reason to refer; in that case choose members of this group. | 메커니즘 | 유지 |
| 선택 | In items, list the requested items. Mark an item "elsewhere" only if this group keeps no records or rules of that kind … | 메커니즘 (소관 밖 표시) | 유지 |
| 선택 | Do not answer the request yourself. First review … then call the route tool once. | 메커니즘 | 유지 |
| 선택 입력 | This group's record types / rules, Other groups (설명·skills), Group records found | 메커니즘 (게이트웨이 입력) | 유지 |
| 조립 | Write this group's answer … using only the replies … and the group records | 메커니즘 | 단조 조립으로 재작성: 담당자 답은 그대로 전달, 게이트웨이는 additions·conflicts·proposals·missing만 |
| 조립 | Give one item per value, with entity and value copied exactly as they appear … | 형식(공통): 응답자 질문에 같은 취지 문구 있음 | additions에만 적용하도록 유지 |
| 조립 | In ref, cite where it is taken from: a reply as [R1], a record as [E1], a database version as [D1] (, an earlier exchange as [S1]) | 메커니즘 (인용) | 유지 |
| 조립 | If sources disagree, use the most recent one and say which one you used. | **지식(K1)** + 메커니즘 | K1을 공통 블록에 넣음. 게이트웨이 문구 = K1 원문 + "Raise such cases as conflicts or proposals." |
| 조립 (Ingress·I+E, version_marks) | Database versions of the same key are the same fact: use the latest registered version and state it (for example "v3, registered day 12"). | **지식(K2)** + 메커니즘 | K2를 공통 블록에 넣음. 게이트웨이 문구 = K2 원문 + "State the version you use …" |
| 조립 | Cross-check the replies against the group records: … entries of the same kind about the same subject that the replies did not mention, and include them with their record citation. | 메커니즘 (그룹 기록 교차 확인) | 유지 (additions로) |
| 조립 | Replies can be incomplete. | **지식(K3)** | K3을 공통 블록에 넣음. 게이트웨이 문구를 K3 원문으로 교체 |
| 조립 | List every requested item you could not confirm in missing. Do not guess. | 형식(공통): 공통 프롬프트 "Do not guess", 응답자 missing 지시 | 유지 |
| 조립 | First work through … then call the answer tool once. | 메커니즘 (호출 형식) | 유지 |
| 조립 입력 | Evidence not covered by any reply: [E#] | 메커니즘 | 유지 |
| 조립 입력 | Database versions: [D#] / Earlier exchanges of this desk: [S#] | 메커니즘 (Ingress·I+E 조건 정의) | 유지 |
| 재질의 | Follow-up from your group's intake desk … For context, the original request was … Answer only these items … | 메커니즘 | 유지 |
| 재질의 | Records of your group on these items (they may be yours or a former member's) | 메커니즘 | 유지 |
| 재조립 | Your first answer … (draft) … Keep every draft item unless a new reply or record contradicts it … | 메커니즘 | 단조 조립에 맞춰 "additions, conflicts and proposals (draft)"로 |
| Egress | You are the outgoing desk … Decide which group(s) to ask and rewrite the question … | 메커니즘 | 유지 |
| Egress | keep every name, ID and amount of the subject as written, so that each rewritten question names what it is about | 형식(공통): 요청자 공통 프롬프트 "When you ask, name the subject …" | 유지 |
| Egress | add what the related records below make clear (for example the group that handled this before) | 메커니즘 | 유지 |
| Egress | Do not add task IDs (such as W-00070); other groups do not have them in their records. | **지식(K4)** + 메커니즘 | K4를 공통 블록에 넣음. 게이트웨이 문구 = "Do not add task IDs to the question." + K4 원문 |
| Egress 재발신 | {question} From your group, only this part is needed: {item} | 메커니즘 | 유지 |
| 소관 밖 안내 | Not handled by this group: {items}. | 메커니즘 | 유지 |

## 함께 바뀐 것 (조립 출력의 단조성)

- 담당자 items는 그대로 전달합니다. 삭제하거나 수정할 수 없고, ref에 "Reply i:"가 붙습니다.
- 게이트웨이는 세 가지만 더합니다.
  - additions: 보충 사실. 기록 인용이 필수입니다.
  - conflicts: 충돌 표시. 인용이 필수입니다.
  - proposals: 제안 값 `{item, value, refs, rationale}`. 근거 인용이 필수이고, 없는 인용은 형식 오류로 되돌립니다.
- 최종 메시지는 코드가 조립합니다: 담당자 items + additions + conflicts + proposals.
- `ask_group` 설명은 조건에 따라 다릅니다.
  - Ingress·I+E: "returns each member's reply as is, plus supplementary items, conflict notes and proposed values with their sources from the group's records."
  - Routing: "returns each member's reply as is."
  - I+E의 `ask`에도 Ingress와 같은 반환 설명을 넣었습니다.
