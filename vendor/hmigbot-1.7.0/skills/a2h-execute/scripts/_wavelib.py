#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调度内核共享库（模块，非 CLI）：contract_hash 实算 + plan 索引 + dispatch 分区读取 + 节点有效状态求解。

消费方（三处共用，消灭双算/双实现漂移——IMPLEMENTATION.md §6 缺口 2 的下沉落点）:
    lint_plan.py（a2h-plan/scripts/，经 sys.path 注入跨目录 import）  → compute_contract_hash
    generate_waves.py                                               → compute_contract_hash
    next_batch.py / land_results.py                                 → ContractError / index_plan /
                                                                      dispatch_wave_rec / journal_indexes /
                                                                      approval_granted / make_resolver /
                                                                      infra_waived / trailing_infra_fails

形态申报（IMPL-PLAN §8 决策 3）：下划线前缀共享模块，与 _a2h_findings.py 同先例——无 top-level main()
（IMPL-CONTRACT §2.2 的 main() 硬规适用于 CLI 脚本；本文件是被 import 的库，冻结分发 shim 按 stem
import 模块即可，不经 main 派发）。其余硬规照守：stdlib-only、utf-8、pathlib。

contract_hash 算法（plan.schema.json description 冻结，本模块是唯一实算点，跨脚本禁自算）:
    sha256 over 契约六件，按固定文件名序 CONTRACT_FILES，逐件喂入 b"<文件名>\\n<文件原始字节>\\n"
    （缺席件按空字节计并记 warning），前缀 'sha256:'。

节点有效状态求解（受限 DAG，memo 递归；next_batch/land_results 原双处同语义实现的合一）:
    agent  → done | skipped | failed | waived(U1) | ready | waiting | blocked
    reduce → passed | skipped | failed_esc | failed_handled | approval_pending | ready | waiting | blocked
    含 land_results 侧的防御分支：非审批 reduce 却见 APPROVAL_PENDING 落账行 → 视为 passed。
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

# 契约六件固定文件名序（即排序后清单；plan.schema.json description 与此逐字一致）
CONTRACT_FILES = ("contracts.json", "decision-ledger.md", "decisions.json",
                  "domain-map.json", "ownership.json", "workflow-params.json")

# 波次全序（V1/K0：单一权威序，generate_waves / next_batch 共用——next_batch done 动作
# 按此推导 next 指引）。wiring 是条件波（fix-backlog 批复后才生成）；closeout 是收尾波。
WAVE_ORDER = ("understand", "specfix", "infra", "domains", "depthfix", "orphanwire", "auditfix",
              "wiring", "closure", "closeout")
# specfix（第十五批 S5）：understand 波尾 gate:spec-depth 判薄/缺分节的页，按域回派一轮重写（条件波，有界一次）；
# 派发单 spec/reports/spec-tasks.json 由 spec_depth_gate.py 产。
# depthfix（第十五批 E15）：gate:depth 判浅的页按页面块回派一轮（条件波，有界一次）；派发单
# spec/reports/depth-tasks.json 由 depth_gate.py 产，next_batch 见无待办或本波已跑过即跳过。
# orphanwire（对齐参照运行的 c2 波）：compile#2 判 graph-mismatch 后，按 owner 切块的孤儿
# 接线波。数据源 = gate_check 产出的 spec/reports/orphan-tasks.compile-2.json（每块 ≤12 文件，
# 脚本切粒度、禁主会话手拟）。参照运行此处是 39 个并行 owner-chunk 任务；本方案此前只有
# SKILL.md 的散文指示要主会话照派发单发——能力等价但要模型自觉，故收编为正式波。
# 条件波：派发单缺失 / tasks 为空时 next_batch 跳过。
# closure（V-830）：Final Structural Closure 自动修复波，条件波——closure-backlog.json
# 缺失 / open=0 / 已 defer 时 next_batch 跳过；未收敛且 round<max_iter 时可再入一轮。

# debt（E207，AIPPT_930 2026-09-17 15:38 实证）：closeout 波尾 gate:handoff-check 判 BLOCKED 后的**机械有界补账波**。
# 主会话此前只能宣告 done 停机，用户说「继续跑完欠账」才临场拼出 wiring r2 + infra r2 + grill_autodecide + 重跑冒烟。
# 本波把那次即兴还债固化：handoffs / fix-backlog 按 owner 派任务，decision-gaps / smoke-1page 走 reduce，
# escalated-ratio 只报不派；gates.debt_max_rounds（缺省 2）封顶，到顶落 spec/reports/debt-exhausted.json 交 handoff 呈报。
# 不进 WAVE_ORDER：closeout 之后由 next_batch 按 handoff-check.json 判 BLOCKED 才出，`--wave all` 不含它。
DEBT_WAVE = "debt"
# E266⑧（2026-09-23 用户裁决）：交棒面判 blocked **只等于停机呈报，不等于会被修**——只有进了本清单的类别
# 才会被 debt 波按 owner 派任务 / 走 reduce 真返工。E265 把一批门禁改成阻断之后复核发现：findings 与
# shared-holders 明明是「派代理改 .ets 就能修」的质量欠账，却落在清单外，于是 handoff-check 红着、debt 波
# 判「BLOCKED 项全为只报不派」直接记 debt-exhausted，账面上只剩一句话。用户口径「所有只审计不修复的都是
# 无用功」，故收编这两类：
#   findings        round0 P0/P1 未销账（findings-gate.json）——修法就是按 finding 逐条改产物，与 fix-backlog 同形；
#   shared-holders  契约声明的共享实例未按单例收口——未核销的 wire = 声明了没实装，repair 能逐条点名 from→to。
# 刻意**不进**清单、维持停机呈报的四类（进来反而制造新缺口）：
#   hotfixes       要人裁定「回滚热改」还是「补签名认领」（E219 后热改本身属禁止行为）——模型替签就正是这条
#                  想堵的缺口本身，派代理去改只会把未经授权的热改洗成既成事实；
#   build-graph    数据不可得：compile#4 判决没落账 / 构建图缺失，派代理改 .ets 变不出一条编译判决；
#   state-accounts 账本损坏：state 任务数 < domain-map 域数，要的是查账（谁没落账）不是改产物；
#   report         迁移报告缺失 / nodata，同属数据不可得，改 .ets 补不出报告。
# 任务生成侧（handoffs/fix-backlog 之外这两类怎么切任务）在 generate_waves.build_debt_tasks，不在本文件。
DEBT_ACTIONABLE = ("handoffs", "fix-backlog", "decision-gaps", "smoke-1page",
                   "findings", "shared-holders")                                  # 可派 / 可 reduce 的阻断类别
DEBT_REPORT_ONLY = ("escalated-ratio",)                                           # 只报不派
DEBT_MAX_ROUNDS_DEFAULT = 2
DEBT_EXHAUSTED_REL = "spec/reports/debt-exhausted.json"
HANDOFF_CHECK_REL = "spec/reports/handoff-check.json"

# 保留组名（K0.1）：parents 引用 "@start" 恒判已满足——承载「无 agent 任务的波」的 reduce 链
# （closeout 在 device_smoke=off 且无 backlog 时没有任何 agent 任务，reduce 仍须可挂）。
# agent 任务禁止声明 map_group="start"（generate_waves 自检与 lint_plan R1 双侧拦截）。
START_GROUP = "start"


class ContractError(Exception):
    """契约违规（消费方按各自 CLI 契约映射退出码，通常 exit 1）。"""


# ── contract_hash 实算（唯一实算点）─────────────────────────────────────────

_ROUND_OR_PART_RE = re.compile(r"^[pr]\d+$")


def domain_key_of(task_id) -> str:
    """任务 id → 域 key。剥掉前缀段与尾部的轮次/分块段：
    impl:app-home → app-home；impl:app-home:p2 → app-home；closure:r1:domain:x → x；seed → seed。
    页面分块（p<N>）与 closure 轮次（r<N>）都是编排层加的段，下游按域记账时必须归一。"""
    segs = [s for s in str(task_id or "").split(":") if s]
    while len(segs) > 1 and _ROUND_OR_PART_RE.match(segs[-1]):
        segs.pop()
    return segs[-1] if segs else ""


def compute_contract_hash(blueprint: Path, warnings: list) -> str:
    """契约六件内容 hash。缺席件按空字节计入并向 warnings 追加一条说明。"""
    h = hashlib.sha256()
    for name in CONTRACT_FILES:
        f = Path(blueprint) / name
        h.update(name.encode("utf-8") + b"\n")
        if f.is_file():
            h.update(_contract_bytes(name, f))
        else:
            warnings.append(f"契约件缺席按空字节计入 hash: {name}")
        h.update(b"\n")
    return "sha256:" + h.hexdigest()


def _contract_bytes(name: str, f: Path) -> bytes:
    """E59：workflow-params.json 的 `gates` 是运行期旋钮（dispatch_burst / max_in_flight / dispatch_paused / unattended…），
    E34–E36、U1 都声明「现场可改、不进契约哈希」——但此前实现按整文件字节计入，改任何旋钮都让全部已生成计划在 lint / E58
    漂移对账上失配（AIPPT_0903 test4 2026-09-05 实证：仅加 gates.unattended，plan-closure 即判 MISMATCH）。
    现按去掉 gates 后的规范化 JSON 计入；解析失败回落原字节。"""
    raw = f.read_bytes()
    # E65：contracts.json#deferred 是运行期账面（merge-deferred 每波追加、verify_handoffs 改 status=resolved），
    # 与 workflow-params.gates 同理不进契约哈希——否则 closeout 里 gate:handoffs 每兑现一条 forward-ref 就让所有计划失配
    # （AIPPT_0903 2026-09-05 11:27：handoffs 清零后重生成 wiring 计划撞 pin，主会话再次手改 dispatch.json）。
    drop = {"workflow-params.json": ("gates",), "contracts.json": ("deferred",)}.get(name)
    if not drop:
        return raw
    try:
        obj = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return raw
    if not isinstance(obj, dict):
        return raw
    obj = {k: v for k, v in obj.items() if k not in drop}
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


# ── plan / 三账索引 ──────────────────────────────────────────────────────────

def index_plan(plan: dict) -> tuple[dict, dict]:
    """plan → (by_id, groups)。groups: map_group 名 → [agent 任务 id]（plan 序）。"""
    by_id: dict[str, dict] = {}
    groups: dict[str, list[str]] = {}
    for t in plan["tasks"]:
        by_id[t["id"]] = t
        if t.get("kind") == "agent" and t.get("map_group"):
            groups.setdefault(t["map_group"], []).append(t["id"])
    return by_id, groups


def dispatch_wave_rec(dispatch: dict, wave: str) -> dict:
    """dispatch.json 按 wave 分区取本 wave 记录 {contract_hash, dispatched}（无记录返回 {}）。
    旧扁平结构（顶层 dispatched/contract_hash，跨 wave 串账）→ 报错提示删除重跑（试点期无存量数据，不做迁移）。"""
    if any(k in dispatch for k in ("dispatched", "contract_hash", "wave")):
        raise ContractError(
            "dispatch.json 为旧版跨 wave 扁平结构（已废除，会串账）：请删除 spec/state/dispatch.json 后重跑")
    rec = (dispatch.get("waves") or {}).get(wave)
    return rec if isinstance(rec, dict) else {}


_RUN_TAG_RE = re.compile(r"^[a-z][a-z0-9]*:(r\d+):")   # E167（AIPPT_930 移植）：首段允许数字（b4:r2:factchain）


def plan_run_tag(plan: dict) -> str | None:
    """E55：可重入波（closure 第 N 轮）的轮次标签——取 agent 任务 id 的 `<wave>:rN:` 段；非重入波返回 None。"""
    tags = set()
    for t in (plan.get("tasks") or []):
        if isinstance(t, dict) and t.get("kind") == "agent":
            m = _RUN_TAG_RE.match(str(t.get("id") or ""))
            if m:
                tags.add(m.group(1))
    return sorted(tags, key=lambda x: int(x[1:]))[-1] if tags else None


def journal_indexes(journal: dict, wave: str, run_tag: str | None = None) -> tuple[dict, dict]:
    """journal → (agent 任务落账最大 attempt, reduce 任务最近一行 status)。
    E55：run_tag 给定时，reduce 行只认同轮（row.run == run_tag）——同名波重入（closure r4）不得继承上一轮的 REDUCE_PASS。
    AIPPT_0903 test4 实证（2026-09-05 09:07–09:12）：closure r4 六个代理落地后，build/compile/rescan 全部沿用 r3 的 PASS 行，
    5 分钟判 SUCCESS，一条 finding 都没重扫。"""
    landed: dict[str, int] = {}
    reduce_last: dict[str, str] = {}
    for row in journal.get("operation_outputs", []):
        if not isinstance(row, dict) or row.get("workflow_id") != wave:
            continue
        tid = row.get("task_id")
        if row.get("kind") == "reduce":
            if run_tag is not None and row.get("run") != run_tag:
                continue
            reduce_last[tid] = row.get("status")
        else:
            att = row.get("attempt")
            if isinstance(att, int):
                landed[tid] = max(landed.get(tid, 0), att)
    return landed, reduce_last


def infra_waived(journal: dict, wave: str) -> dict:
    """各 agent 任务的 INFRA_FAIL 落账行计数（OPT-PLAN K7：基础设施失败豁免 attempts）。

    有效派发计数 = dispatch attempts − waived；next_batch 的 fresh/retryable/exhausted
    判定与 land_results 的 RETRY_EXHAUSTED 判定统一按有效计数走。"""
    # 按 (task, attempt) 去重：同一次派发被 runner 与续跑主会话各改判一次时只豁免一次
    # （AIPPT_token3：18 行 INFRA_FAIL 实为 12 次被杀派发；按行计会多豁免、放出额外重试）。无 attempt 字段的旧行逐行计。
    seen: dict[str, set] = {}
    waived: dict[str, int] = {}
    for i, row in enumerate(journal.get("operation_outputs", [])):
        if isinstance(row, dict) and row.get("workflow_id") == wave \
                and row.get("kind") != "reduce" and row.get("status") == "INFRA_FAIL":
            tid = row.get("task_id")
            if not isinstance(tid, str):
                continue
            att = row.get("attempt")
            key = att if isinstance(att, int) else ("row", i)
            bucket = seen.setdefault(tid, set())
            if key in bucket:
                continue
            bucket.add(key)
            waived[tid] = waived.get(tid, 0) + 1
    return waived


def trailing_infra_fails(journal: dict, wave: str) -> int:
    """本 wave agent 落账行按 journal 序的尾部连续 INFRA_FAIL 计数（健康探测判据，K7）。

    连续 ≥ 阈值 ⇒ 疑似平台侧故障（529 潮/整批白跑），next_batch 输出 health_probe wait，
    主会话探测恢复后以 --assume-healthy 重取批。"""
    n = 0
    for row in reversed(journal.get("operation_outputs", [])):
        if not isinstance(row, dict) or row.get("workflow_id") != wave \
                or row.get("kind") == "reduce":
            continue
        if row.get("reclassified"):
            # 事后改判（--infra-fail 重记既有落账）不是新发生的失败，不计入平台健康判据，
            # 也不打断连续性——否则一次批量改判就会把探测器顶死（实证：改判 10 个 → 尾部 19）。
            continue
        if row.get("status") == "INFRA_FAIL":
            n += 1
        else:
            break
    return n


def approval_granted(root: Path, payload_rel: str) -> bool:
    """suspend payload 文件即批复真源：顶层 approved:true 或 resolution.approved:true。"""
    p = Path(payload_rel)
    if not p.is_absolute():
        p = Path(root) / p
    if not p.exists():
        return False
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(data, dict):
        return False
    res = data.get("resolution") if isinstance(data.get("resolution"), dict) else {}
    if data.get("approved") is not True and res.get("approved") is not True:
        return False
    # E47：批复真源是人。脚本自动批复（fix_backlog open=0 → auto:true）照旧；人工批复必须带 by（谁）+ quote（用户原话），
    # 缺一不算批复——AIPPT_0903 test4 实证（2026-09-04 17:15）：主会话在 13 条 open / 7 条 P0 的 fix-backlog 审批文件里
    # 自己写了 {"approved": true, "by": "user"}，用户从未被问到；quote 字段把「替用户批」变成必须伪造原话的显性谎言，
    # 且 handoff_check 会把每份批复的 quote 原样呈报给用户复核。
    if data.get("auto") is True or res.get("auto") is True:
        return True
    by = data.get("by") or res.get("by")
    quote = data.get("quote") or res.get("quote")
    return isinstance(by, str) and by.strip() != "" and isinstance(quote, str) and quote.strip() != ""


def approval_rejection_reason(root: Path, payload_rel: str) -> str | None:
    """approved:true 但不满足 E47 时给出一句原因（供 next_batch 的 approval 动作提示）；正常/未批复返回 None。"""
    p = Path(payload_rel)
    if not p.is_absolute():
        p = Path(root) / p
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    res = data.get("resolution") if isinstance(data.get("resolution"), dict) else {}
    if data.get("approved") is not True and res.get("approved") is not True:
        return None
    if approval_granted(root, payload_rel):
        return None
    return "approved:true 但缺 by/quote（E47）：人工批复必须写 {\"approved\": true, \"by\": \"<谁>\", \"quote\": \"<用户原话>\"}；不得替用户批"


# ── 节点有效状态求解（原 next_batch.build_resolver / land_results.make_resolver 合一）──

# ── 无人值守（U1）：每个人工停点一条确定性默认策略，全部留痕 spec/state/auto-adjudications.json ──
ADJ_REL = "spec/state/auto-adjudications.json"


def unattended(root) -> bool:
    """gates.unattended=true（运行期开关，不进契约哈希）：审批门自动 approve、质量线升级记欠账继续、
    阻断型门自动派一次 repair 再记欠账、closure STALLED 刷新任务书重跑一轮再 defer、超时在途按缺失重派。"""
    try:
        g = json.loads((Path(root) / "spec" / "blueprint" / "workflow-params.json").read_text(encoding="utf-8")).get("gates") or {}
        return g.get("unattended") is True
    except (OSError, ValueError, TypeError, AttributeError):
        return False


def debt_cap(root) -> int:
    """E207：gates.debt_max_rounds（缺省 2；0 = 关闭 debt 波）。运行期开关，不进契约哈希。"""
    try:
        g = json.loads((Path(root) / "spec" / "blueprint" / "workflow-params.json").read_text(encoding="utf-8")).get("gates") or {}
        v = g.get("debt_max_rounds", DEBT_MAX_ROUNDS_DEFAULT)
        return int(v) if isinstance(v, int) and not isinstance(v, bool) else DEBT_MAX_ROUNDS_DEFAULT
    except (OSError, ValueError, TypeError, AttributeError):
        return DEBT_MAX_ROUNDS_DEFAULT


_DEBT_REDUCE_ROUND_RE = re.compile(r":r(\d+)$")


def debt_round(journal_path) -> int:
    """E207：debt 波本轮轮次 = journal 里该波已落账行的最大轮次 + 1（无记录 → 1）。
    与 generate_waves._wave_round 同口径（agent 行按 `<prefix>:rN:` 段），**另计 reduce 行**：只派 reduce 的轮
    （只有 decision-gaps / smoke-1page 阻断时没有 agent）reduce id 尾部带 `:rN`（generate_waves 第二轮起加），
    否则 reduce-only 轮永远算第 1 轮、既不封顶也不按轮隔离 reduce 行（E55）。"""
    try:
        j = json.loads(Path(journal_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 1
    seen = 0
    for r in (j.get("operation_outputs") or []) if isinstance(j, dict) else []:
        if not (isinstance(r, dict) and r.get("workflow_id") == DEBT_WAVE):
            continue
        tid = str(r.get("task_id") or "")
        if r.get("kind") == "agent":
            m = _RUN_TAG_RE.match(tid)
            seen = max(seen, int(m.group(1)[1:]) if m else 1)
        else:
            m = _DEBT_REDUCE_ROUND_RE.search(tid)
            seen = max(seen, int(m.group(1)) if m else 1)
    return seen + 1


def debt_state(root) -> dict:
    """E207：debt 波的判读（next_batch / generate_waves 共用，单一口径）：
    present（handoff-check.json 存在）/ ok / blocked[] / actionable[]（可派或可 reduce 的阻断类别）/
    round（本轮轮次）/ cap / exhausted（cap<=0 或 round>cap，或 debt-exhausted.json 已对本份 handoff-check 记账）。"""
    root = Path(root)
    try:
        hc = json.loads((root / HANDOFF_CHECK_REL).read_text(encoding="utf-8"))
        hc = hc if isinstance(hc, dict) else None
    except (OSError, ValueError):
        hc = None
    blocked = [str(x) for x in ((hc or {}).get("blocked") or []) if isinstance(x, str)]
    rnd = debt_round(root / "spec" / "state" / "journal.json")
    cap = debt_cap(root)
    exhausted = cap <= 0 or rnd > cap
    stamp = (hc or {}).get("generated_at")
    if not exhausted and hc is not None:
        try:
            ex = json.loads((root / DEBT_EXHAUSTED_REL).read_text(encoding="utf-8"))
            if isinstance(ex, dict) and stamp and ex.get("handoff_check_generated_at") == stamp:
                exhausted = True   # 同一份交棒判决已记「无可派 / 到顶」，不再反复出 debt
        except (OSError, ValueError):
            pass
    return {"present": hc is not None, "ok": bool((hc or {}).get("ok")) if hc is not None else None,
            "blocked": blocked, "actionable": [b for b in blocked if b in DEBT_ACTIONABLE],
            "report_only": [b for b in blocked if b in DEBT_REPORT_ONLY],
            "round": rnd, "cap": cap, "exhausted": exhausted, "generated_at": stamp}


def load_adjudications(root) -> list:
    p = Path(root) / ADJ_REL
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, list) else []
    except (OSError, ValueError):
        return []


# E266⑦（2026-09-23 用户裁决）：审批材料里「还没销完的待办」字段名——命中任一即**禁止自动批复**。
# 各产材料的脚本字段名不统一（fix_backlog 写 open/p0，别的门可能写 open_items/unresolved/remaining），
# 故按名单取并集；值可以是计数（int>0）也可以是清单（非空 list/dict）。bool 不算数（True 不是「1 条」）。
APPROVAL_OPEN_FIELDS = ("open", "open_items", "unresolved", "remaining", "p0")


def _payload_open_debt(d: dict) -> dict:
    """payload 里未销待办的计数表（字段名 → 条数）；空表 = 材料自称无待办。"""
    out = {}
    for k in APPROVAL_OPEN_FIELDS:
        v = (d or {}).get(k)
        if isinstance(v, bool):
            continue
        if isinstance(v, int) and v > 0:
            out[k] = v
        elif isinstance(v, (list, tuple, dict)) and len(v) > 0:
            out[k] = len(v)
    return out


def approval_open_debt(root, rel: str) -> dict:
    """E266⑦：审批材料里未销的待办计数（供三处调用方同口径呈报）；材料缺席 / 不可解析 → 空表。"""
    p = Path(rel)
    if not p.is_absolute():
        p = Path(root) / p
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return _payload_open_debt(d if isinstance(d, dict) else {})


def approval_debt_note(root, rel: str) -> str | None:
    """E266⑦：自动批复时「材料里还欠着什么 + 返工通道走到哪一步」的一句话（三处调用方同口径呈报）。
    材料无待办 / 缺席 → None。本函数纯读不写账；留痕由 auto_approve_payload 落 auto-adjudications.json。"""
    debt = approval_open_debt(root, rel)
    if not debt:
        return None
    st = debt_state(root)
    counts = "、".join("%s=%d" % (k, n) for k, n in sorted(debt.items()))
    if st["present"] and st["exhausted"]:
        return ("审批材料仍有未销待办（%s）且返工通道已用尽（debt 波 %s/%s 轮）："
                "本次自动批复 = 记欠账放行，欠账逐条进 handoff-check 与迁移报告（E266⑦）"
                % (counts, st["round"], st["cap"]))
    return ("审批材料仍有未销待办（%s）：本次自动批复 **即是派返工**——approve 之后 wiring 波按 owner 接线，"
            "closeout 后 debt 波最多再补 %s 轮；通道跑完仍有剩余才算记欠账放行（E266⑦）"
            % (counts, st["cap"] if st["present"] else DEBT_MAX_ROUNDS_DEFAULT))


def auto_approve_payload(root, wave: str, tid: str, rel: str) -> bool:
    """U1：审批材料（suspend payload）已实存且未批 → 写自动批复（approve 路径 = 多做）并留痕 kind=approve。返回是否本次写入。
    E157：从 next_batch 抽出来给 land_results 复用——审批节点一进 APPROVAL_PENDING 就批，主会话不会再看到『等用户答复』的摘要
    （AIPPT_0906 2026-09-07 03:39：fix-backlog 挂起，主会话按 E47 停下等人，无人值守跑批在凌晨停了 4 个多小时）。

    E266⑦（2026-09-23 用户裁决）：**open>0 照批**，但批复这件事要按「先派修、修不动才算放行」分清两种性质。
    复核起点：E157 落地后真正命中的就是 gate:fix-backlog，材料形态恰恰是 open=13 / p0=7（跨域待办一条没销），
    留痕里却只有一句 approve，看不出这 13 条后来有没有人修。当天先按「open>0 不得自动批」收紧过，随即推翻——
    对 fix-backlog 而言 **approve 本身就是派返工**：approve → wiring 波按 owner 接线 → backlog_settle 销账；
    defer 才是放行。拦住 approve 等于把唯一的返工通道也一起拦掉，是反效果。
    故现在照批，把力气放在留痕上：批复时一并记下未销待办计数、返工通道（wiring 波 + closeout 后的 debt 波，
    上限 gates.debt_max_rounds）走到哪一轮；通道已用尽还批的，裁决直接标成 `waive-approval`（这才是记欠账放行）。
    open=0 的材料照旧自动批（那本来就是 fix_backlog 自己写的 auto:true，不是替人签字）。"""
    p = Path(root) / rel
    if not p.is_file() or approval_granted(root, rel):
        return False
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        d = d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        d = {}
    debt = _payload_open_debt(d)
    d.update({"approved": True, "auto": True, "by": "auto-policy", "policy": "approve",
              "quote": "unattended：审批门默认 approve（多做派）——见 spec/state/auto-adjudications.json"})
    if debt:
        d["open_debt_at_approval"] = debt
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    entry = {"kind": "approve", "wave": wave, "id": tid, "payload": rel,
             "detail": {k: d.get(k) for k in ("open", "p0") if k in d}}
    if debt:
        st = debt_state(root)
        spent = st["exhausted"] if st["present"] else False
        entry.update({
            "open_debt": debt,
            "repair_channel": {"approve_dispatches": "wiring 波（按 owner 接线）",
                               "followup": "closeout 后 debt 波 fix-backlog 补账",
                               "debt_round": st["round"], "debt_cap": st["cap"], "exhausted": bool(spent)},
            "note": approval_debt_note(root, rel)})
        if spent:
            # 返工通道已经跑完（wiring + debt 满轮）仍有未销待办：这一次批复的性质是记欠账放行，不是派返工
            entry["kind"] = "waive-approval"
            entry["terminal"] = "waive"
            entry["unfixable_reason"] = ("wiring 波 + debt 波（%s/%s 轮）跑完仍有未销跨域待办——"
                                         "机械补账通道已用尽" % (st["round"], st["cap"]))
            entry["decision"] = "记欠账放行：批复放过剩余待办，逐条进 handoff-check 与迁移报告（E266⑦）"
        else:
            entry["decision"] = "自动批复 = 派返工：approve 后 wiring 波接线、debt 波补账，不是放行（E266⑦）"
    record_adjudication(root, entry)
    return True


def record_adjudication(root, entry: dict) -> None:
    p = Path(root) / ADJ_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    rows = load_adjudications(root)
    e = dict(entry); e.setdefault("at", _dt.now(_tz.utc).isoformat(timespec="seconds")); e.setdefault("by", "auto-policy")
    rows.append(e)
    p.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _same_run(e: dict, run_tag) -> bool:
    """U1.2：裁决按轮次隔离——closure r4 记的 waive/repair 不得延到 r5（AIPPT_0903 2026-09-05 10:04：r5 的 compile-closure
    一开始就被 r4 的 waive 视为已处置，红着也放行了 rescan）。无 run tag 的波不过滤。"""
    return run_tag is None or e.get("run") == run_tag


def waived_ids(root, wave: str, run_tag=None) -> set:
    """已记欠账放行的节点 id（resolver 据此把该节点当已处置）。

    E266①：`waive-task`（agent 任务重试耗尽即记欠账放行）**自 2026-09-23 起不再产生**——next_batch 改为
    升级停机呈报。这里仍认这个 kind，只为已在跑的工程里那些历史条目不被突然改判（中途改判会让一批
    早已 waive 的任务同时回红、整波重算）；新账里不会再出现。"""
    return {e.get("id") for e in load_adjudications(root)
            if e.get("wave") == wave and e.get("kind") in ("waive-gate", "waive-task") and e.get("id") and _same_run(e, run_tag)}


def last_repair_at(root, wave: str, gate: str, run_tag=None) -> str | None:
    ats = [e.get("at") for e in load_adjudications(root)
           if e.get("wave") == wave and e.get("kind") == "repair" and e.get("id") == gate and e.get("at") and _same_run(e, run_tag)]
    return max(ats) if ats else None


def repair_pending(root, wave: str, gate: str, journal: dict, run_tag=None) -> bool:
    """U1：已派 repair 但该门此后还没重跑过（journal 无晚于 repair.at 的同轮 reduce 行）→ 仍在途，不得急着 waive。
    AIPPT_0903 test4 实证（2026-09-05 09:51:34→09:51:37）：repair 动作返回 3 秒后主会话又拍①，门被当作「repair 一次仍红」记欠账。"""
    at = last_repair_at(root, wave, gate, run_tag)
    if not at:
        return False
    for row in (journal.get("operation_outputs") or []):
        if not isinstance(row, dict) or row.get("workflow_id") != wave or row.get("task_id") != gate or row.get("kind") != "reduce":
            continue
        if run_tag is not None and row.get("run") != run_tag:
            continue
        if str(row.get("ended_at") or "") > at:
            return False
    return True


def repair_count(root, wave: str, gate: str, run_tag=None) -> int:
    return sum(1 for e in load_adjudications(root) if e.get("wave") == wave and e.get("kind") == "repair" and e.get("id") == gate and _same_run(e, run_tag))


# ── 阶段门机械策略（E205 → 2026-09-21 用户裁决改为默认关闭）───────────────────────────
# 历史：AIPPT_930 2026-09-17 实跑，主会话在 4 个阶段门停下等人，E205 把「修一次仍 FAIL → 记欠账 PASS_WITH_DEBT、exit 0」
# 做成所有阶段门共用单点（hygiene_gate / lint_interface / lint_blueprint / lint_plan / lint_coverage 经 sys.path 注入 import）。
# 2026-09-21 全量实跑证明带欠账放行直接拉低产品质量，用户裁决**行为级回退**：
#   缺省（gates.stage_debt 未开）：阶段门 FAIL → exit 非 0，**每次都非 0**；不写 spec/state/gate-attempts.json、
#   不写 spec/reports/<gate>-debt.json、不记 auto-adjudication；无人值守下仍吐机器可读 retry_hint（失败项 + 唯一一条范围限定
#   修复），主会话按 retry_hint 派修复并重跑，直到 PASS——不记欠账、不放行。
#   gates.stage_debt=true（显式开启；仅设备/账号类门允许欠账）：才走原 E205 机制——第 1 次 FAIL exit 非 0 + retry_hint、attempts=1；
#   第 2 次 FAIL（attempt ≥ 2）写 <gate>-debt.json、记 auto-adjudication kind=<gate>-debt、判 PASS_WITH_DEBT、exit 0；PASS 归零撤欠账。
#   attended（gates.unattended 未开）：不读不写，行为与此前完全一致。
# 计数器 spec/state/gate-attempts.json 单写者 = 门脚本自身（读-改-写，键 = gate 名）；只在 stage_debt 开启时存在。
# F8（2026-09-21）：「仅设备/账号类门允许欠账」由散文变成机械白名单 DEBT_ALLOWED_GATES——stage_debt 开着但 gate 不在表内
# （lint-blueprint / lint-plan-* / hygiene / interface / depth-gate 这些纯静态门）→ 与 stage_debt 未开完全同行为：只给 retry_hint、
# 永不 PASS_WITH_DEBT、不落计数/欠账文件。匹配大小写不敏感，允许 `<name>` 精确或 `<name>-*` 前缀（如 cold-start-hmos）。
GATE_ATTEMPTS_REL = "spec/state/gate-attempts.json"
DEBT_ALLOWED_GATES = ("auth-probe", "cold-start", "smoke-1page", "b4", "device-smoke")
GATE_RETRY_NEXT = "按 fix 派范围限定修复后重跑同一命令，直到 PASS；不记欠账、不放行（gates.stage_debt=true 时例外）"
GATE_RETRY_NEXT_DEBT = "按 fix 派一次范围限定修复后重跑同一命令；再 FAIL 脚本自动记欠账 PASS_WITH_DEBT（exit 0），不停机（gates.stage_debt=true）"


def debt_allowed(gate: str) -> bool:
    """F8：gate 是否属于允许欠账的设备/账号类门（DEBT_ALLOWED_GATES；大小写不敏感，精确名或 `<name>-*` 前缀）。"""
    g = str(gate or "").strip().lower()
    return any(g == a or g.startswith(a + "-") for a in DEBT_ALLOWED_GATES)


def stage_debt(root) -> bool:
    """gates.stage_debt=true（运行期开关，不进契约哈希；缺省 false）：阶段门「修一次仍 FAIL → 记欠账 PASS_WITH_DEBT 放行」
    的显式开关。仅设备/账号类门（DEBT_ALLOWED_GATES，见 debt_allowed）允许欠账，需显式开启；
    缺省下阶段门 FAIL 永远 exit 非 0、不落任何欠账文件。"""
    try:
        g = json.loads((Path(root) / "spec" / "blueprint" / "workflow-params.json").read_text(encoding="utf-8")).get("gates") or {}
        return g.get("stage_debt") is True
    except (OSError, ValueError, TypeError, AttributeError):
        return False


def load_gate_attempts(root) -> dict:
    try:
        d = json.loads((Path(root) / GATE_ATTEMPTS_REL).read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_gate_attempts(root, data: dict) -> None:
    p = Path(root) / GATE_ATTEMPTS_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def gate_debt_path(root, gate: str) -> Path:
    return Path(root) / "spec" / "reports" / ("%s-debt.json" % gate)


def _gate_fingerprint(items) -> str:
    """E213：失败项集合的指纹（顺序无关；项是 dict 时取 json 规范串）。"""
    import hashlib
    keys = sorted(json.dumps(x, ensure_ascii=False, sort_keys=True) if isinstance(x, (dict, list)) else str(x) for x in (items or []))
    return hashlib.sha1("\n".join(keys).encode("utf-8")).hexdigest()[:16]


def _repair_marker(root) -> str:
    """E213：「有没有修过东西」的机械证据：spec/ 下（不含 state/reports/waves/prompts）最新 mtime + journal 代理落账行数。"""
    base = Path(root) / "spec"
    newest = 0.0
    skip = {base / "state", base / "reports", base / "waves" / "prompts"}
    if base.is_dir():
        for p in base.rglob("*"):
            if any(s in p.parents or s == p for s in skip) or not p.is_file():
                continue
            try:
                newest = max(newest, p.stat().st_mtime)
            except OSError:
                pass
    rows = 0
    try:
        j = json.loads((base / "state" / "journal.json").read_text(encoding="utf-8"))
        rows = sum(1 for r in (j.get("operation_outputs") or []) if isinstance(r, dict) and r.get("kind") == "agent")
    except (OSError, ValueError):
        pass
    return "%d:%d" % (int(newest), rows)


def gate_policy(root, gate: str, failed: bool, items: list, fix: str, *, wave: str = "stage",
                rule: str = None, adj_id: str = None, extra: dict = None, max_items: int = 60) -> dict:
    """阶段门统一处置。返回 {mode, gate, attempt, verdict, exit_code, retry_hint, debt_file}：
    attended → verdict PASS/FAIL、exit 0/1、不落任何文件；
    unattended 且 gates.stage_debt 未开（缺省）→ verdict PASS/FAIL、exit 0/1、不落任何文件，FAIL 时带 retry_hint（修到 PASS 为止）；
    unattended 且 gates.stage_debt=true 但 gate ∉ DEBT_ALLOWED_GATES（F8：只有 auth-probe / cold-start / smoke-1page / b4 /
    device-smoke 这些设备/账号类门允许欠账）→ 与 stage_debt 未开完全同行为；
    unattended 且 gates.stage_debt=true 且 gate 在白名单内 → 见本段头注（修一次仍 FAIL 记欠账 PASS_WITH_DEBT）。"""
    stamp = _dt.now(_tz.utc).isoformat(timespec="seconds")
    res = {"mode": "attended", "gate": gate, "attempt": 0, "verdict": "FAIL" if failed else "PASS",
           "exit_code": 1 if failed else 0, "retry_hint": None, "debt_file": None}
    if not unattended(root):
        return res
    res["mode"] = "unattended"
    if not stage_debt(root) or not debt_allowed(gate):
        # 缺省：FAIL 永远 exit 非 0，不读不写任何计数/欠账文件；只给 retry_hint 让主会话派修复后重跑，直到 PASS。
        # F8：stage_debt 开着但 gate 不在 DEBT_ALLOWED_GATES → 同此分支（静态门永不欠账）。
        if failed:
            items = list(items or [])
            res["retry_hint"] = {"gate": gate, "failing": len(items), "items": items[:max_items],
                                 "fix": fix, "next": GATE_RETRY_NEXT}
            if stage_debt(root):
                res["retry_hint"]["note"] = ("F8：gate %s 不在 DEBT_ALLOWED_GATES=%s 内，stage_debt 对它无效——修到 PASS 为止"
                                             % (gate, list(DEBT_ALLOWED_GATES)))
        return res
    data = load_gate_attempts(root)
    rec = data.get(gate) if isinstance(data.get(gate), dict) else {}
    debt = gate_debt_path(root, gate)
    if not failed:
        data[gate] = {"attempts": 0, "last_verdict": "PASS", "updated_at": stamp}
        _save_gate_attempts(root, data)
        if debt.is_file():
            try:
                debt.unlink()
            except OSError:
                pass
        return res
    items = list(items or [])
    shown = items[:max_items]
    fp = _gate_fingerprint(items)
    marker = _repair_marker(root)
    prev_attempts = int(rec.get("attempts") or 0)
    # E213（token2 实证 08:06:51 → 08:06:59）：同一门 8 秒内被重跑（第二次只是加 --emit-spec-tasks 出派发单），
    # 中间没有任何修复，却被计成第 2 次 FAIL 直接 PASS_WITH_DEBT。规则：失败项指纹未变 **且** spec/ 无新改动、
    # journal 无新落账 → 不是修复后的重跑，不计 attempts，原样再给 retry_hint。
    if prev_attempts >= 1 and rec.get("last_verdict") == "FAIL" and rec.get("fingerprint") == fp and rec.get("repair_marker") == marker:
        res["attempt"] = prev_attempts
        res["retry_hint"] = {"gate": gate, "attempt": prev_attempts, "failing": len(items), "items": shown,
                             "fix": fix, "next": GATE_RETRY_NEXT_DEBT,
                             "note": "E213：距上次 FAIL 未见任何修复改动（失败项、spec/ 文件、journal 均未变），本次不计入 attempts"}
        return res
    attempt = prev_attempts + 1
    res["attempt"] = attempt
    if attempt < 2:
        data[gate] = {"attempts": attempt, "last_verdict": "FAIL", "updated_at": stamp,
                      "fingerprint": fp, "repair_marker": marker}
        _save_gate_attempts(root, data)
        res["retry_hint"] = {"gate": gate, "attempt": attempt, "failing": len(items), "items": shown,
                             "fix": fix, "next": GATE_RETRY_NEXT_DEBT}
        return res
    rule_txt = rule or ("阶段门 %s 修复一次仍 FAIL → 记欠账 PASS_WITH_DEBT 继续（E205）；欠账只能由本门重跑 PASS 关闭" % gate)
    rep = {"gate": gate, "attempt": attempt, "items": shown, "failing": len(items), "rule": rule_txt,
           "fix": fix, "generated_at": stamp}
    if extra:
        rep.update(extra)
    debt.parent.mkdir(parents=True, exist_ok=True)
    debt.write_text(json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        record_adjudication(root, {"kind": "%s-debt" % gate, "wave": wave, "id": adj_id or ("gate:%s" % gate),
                                   "decision": "阶段门 %s 第 %d 次 FAIL（%d 项）→ 记欠账 PASS_WITH_DEBT 继续（E205）" % (gate, attempt, len(items)),
                                   "detail": {"debt_file": str(debt.relative_to(Path(root))).replace("\\", "/"), "failing": len(items)},
                                   "by": "auto-policy"})
    except Exception:  # noqa: BLE001 —— 留痕失败不影响欠账文件与放行
        pass
    data[gate] = {"attempts": attempt, "last_verdict": "PASS_WITH_DEBT", "updated_at": stamp,
                  "fingerprint": fp, "repair_marker": marker}
    _save_gate_attempts(root, data)
    res.update({"verdict": "PASS_WITH_DEBT", "exit_code": 0,
                "debt_file": str(debt.relative_to(Path(root))).replace("\\", "/")})
    return res


def gate_policy_line(res: dict) -> str:
    """非 --json 模式的一行人读输出（stdout）：FAIL 时带 retry_hint JSON，PASS_WITH_DEBT（仅 gates.stage_debt）时指向欠账文件。"""
    if res.get("mode") != "unattended":
        return ""
    if res.get("verdict") == "PASS_WITH_DEBT":
        return "PASS_WITH_DEBT: gate=%s attempt=%d debt=%s（已记 auto-adjudication，继续，不停机）" % (
            res["gate"], res["attempt"], res["debt_file"])
    if res.get("retry_hint"):
        return "retry_hint: " + json.dumps(res["retry_hint"], ensure_ascii=False)
    return ""


def make_resolver(by_id: dict, groups: dict, st: dict, reduce_last: dict, root: Path, waived=None):
    """返回 resolve(tid) -> 有效状态。memo 随本次 make 持久（输入不变时纯函数，跨调用复用安全；
    调用方在三账发生变化后须重新 make——land_results 的 reduce 执行循环即按此使用）。"""
    memo: dict[str, str] = {}
    waived = set(waived or ())   # U1：无人值守下已记欠账的门/任务——对下游视同满足

    def parent_state(ref: str) -> str:
        """parents 引用 → ok | pending | failed | skipped。"""
        if ref == "@" + START_GROUP:
            return "ok"  # K0.1 保留组：恒已满足（无 agent 任务的波的 reduce 挂载点）
        if ref.startswith("@"):
            members = groups.get(ref[1:], [])
            if not members:
                raise ContractError(f"parents 引用了不存在的 map 组: {ref!r}")
            states = [resolve(m) for m in members]
            if any(s == "skipped" for s in states):
                return "skipped"
            if any(s in ("failed", "blocked", "failed_esc") for s in states):
                return "failed"
            if all(s in ("done", "passed", "failed_handled", "waived") for s in states):
                return "ok"
            return "pending"
        if ref not in by_id:
            raise ContractError(f"parents 引用了不存在的任务 id: {ref!r}")
        s = resolve(ref)
        # E44：failed_handled（REDUCE_FAIL 且 on_fail.escalate=False）= 已处置的 best-effort 失败，
        # 对下游视同满足——它要裁掉的子任务由 on_fail.skip 显式列出并在 land 侧标 skipped，
        # 未列出的子任务照常就绪。此前把它当 failed → 子任务 blocked → 拍①「不可达」升级：
        # AIPPT_0903 test4 depthfix 波 gate:depth-2（escalate=False）FAIL 后 reduce:product-write-audit 被判不可达，
        # 主会话拿到一个无事可裁的 escalate，自派了 4 个计划外代理。
        if s in ("done", "passed", "failed_handled", "waived"):
            return "ok"
        if s == "skipped":
            return "skipped"
        if s in ("failed", "blocked", "failed_esc"):
            return "failed"
        return "pending"

    def resolve(tid: str) -> str:
        if tid in memo:
            return memo[tid]
        memo[tid] = "waiting"  # 占位防环（受限 DAG 不应有环；有环即按 waiting 处理并由 lint 兜底）
        t = by_id[tid]
        parents = t.get("parents") or []
        if t["kind"] == "agent":
            status = (st.get(tid) or {}).get("status")
            if status == "done":
                r = "done"
            elif status == "folded":
                r = "skipped"
            elif status == "failed":
                r = "waived" if tid in waived else "failed"
            else:
                ps = [parent_state(p) for p in parents]
                if any(p == "skipped" for p in ps):
                    r = "skipped"          # 祖先被裁 → 传递性跳过（land 未及标记时的安全网）
                elif any(p == "failed" for p in ps):
                    r = "blocked"
                elif all(p == "ok" for p in ps):
                    r = "ready"
                else:
                    r = "waiting"
        else:
            last = reduce_last.get(tid)
            approval = t.get("approval") if isinstance(t.get("approval"), dict) else None
            if last == "SKIPPED":
                r = "skipped"
            elif last == "REDUCE_FAIL":
                r = "failed_esc" if ((t.get("on_fail") or {}).get("escalate") and tid not in waived) else "failed_handled"
            elif last == "REDUCE_PASS" and not approval:
                r = "passed"
            else:
                ps = [parent_state(p) for p in parents]
                if any(p == "skipped" for p in ps):
                    r = "skipped"
                elif any(p == "failed" for p in ps):
                    r = "blocked"
                elif all(p == "ok" for p in ps):
                    if approval:
                        r = "passed" if approval_granted(root, approval["suspend_payload"]) else "approval_pending"
                    elif last == "APPROVAL_PENDING":
                        r = "passed"   # 防御：非审批节点却有挂起行，视为已就绪已处置
                    else:
                        r = "ready"
                else:
                    r = "waiting"
        memo[tid] = r
        return r

    return resolve


# ── 禁写面（forbidden surface）与快照还原 ──────────────────────────────────────
# 为什么要这个：围栏此前只分 cross_owner / unowned 两档且都只记账。AIPPT_915_test3 实证
# 30 条越界里 21 条写进 spec/（域 spec 被并发改写），资源 JSON 又被任务书明令让 agent 自己加——
# 这些面要么是 execute 期只读的契约，要么有专职 reduce 单写。落在自身围栏内的写入永远合法
# （围栏优先：understand 读任务的 spec 写权、mainloop 的资源写权都在自身 ownership 里）。
import fnmatch as _fnmatch
import os as _os
import shutil as _shutil
from datetime import datetime as _dt, timezone as _tz

FORBIDDEN_GLOBS = (
    "spec/**",                              # 契约 / 域 spec / 台账 / 三本账：execute 期只读
    "*/src/main/resources/**",              # 资源 JSON：seed_resources.py 单写
    "**/entryability/EntryAbility.ets",     # mount_wiring.py 单写
    "**/wiring/WiringRoot.ets",
    "AGENTS.md", ".agents/**", ".codex/**",
)
FORBIDDEN_EXEMPT = (
    "spec/waves/results/**",                # 回执文件本来就由代理写
    # E39：任务书明文要求 worker 写、脚本侧机械消费的两类 spec/ 产物——不是契约、不在快照恢复范围
    "spec/execution/theme-receipts/**",     # 按页分片主题回执（theme_gate.py 聚合；分片正是为并发写而设）
    "spec/domains/*.source-notes.md",       # complex 域理解笔记（round-1 审计 prompt 复用；understand 波已给 ownership）
    "spec/domains/*/source-notes.md",       # 目录式分册形态（assemble_prompt 两种形态）
    # E214（token2 实证 17:29）：E200 深度自检让页面任务自跑 depth_gate 写 spec/reports/depth-selfcheck/<task>.json
    # （含同目录 depth-tasks.json），这是代理自己的证据文件、由 land_results 复核消费，不是契约——此前落在 spec/** 禁写面，
    # 第一个带自检的回执就被判 FENCE_FORBIDDEN → RETRY_NEEDED（impl:app-recommend:p1）。
    "spec/reports/depth-selfcheck/**",
)
SNAPSHOT_DIR = "spec/state/fence-snapshot"
SNAPSHOT_SCOPE = ("spec/blueprint/**", "spec/domains/**", "spec/baseline/**", "spec/reports/**",
                  "spec/*.md", "*/src/main/resources/**", "**/entryability/EntryAbility.ets",
                  "**/wiring/WiringRoot.ets", "AGENTS.md")
_SNAPSHOT_PRUNE = {".git", "node_modules", "oh_modules", "build", ".hvigor", ".idea", ".agents", ".codex"}


def _norm_rel_path(rel: str) -> str:
    r = str(rel or "").replace("\\", "/")
    while r.startswith("./"):
        r = r[2:]
    return r.lstrip("/")


def _match_any(rel: str, globs) -> bool:
    return any(_fnmatch.fnmatch(rel, g) for g in globs)


def is_forbidden(rel: str) -> bool:
    """文件是否落在禁写面（调用方须先排除自身围栏内的合法写入）。"""
    r = _norm_rel_path(rel)
    return _match_any(r, FORBIDDEN_GLOBS) and not _match_any(r, FORBIDDEN_EXEMPT)


def _scope_files(root):
    root = Path(root)
    for dirpath, dirnames, filenames in _os.walk(root):
        rel_dir = _norm_rel_path(_os.path.relpath(dirpath, root))
        if rel_dir == ".":
            rel_dir = ""
        dirnames[:] = [d for d in dirnames if d not in _SNAPSHOT_PRUNE
                       and not (rel_dir == "spec" and d in ("waves", "state"))]
        for fn in filenames:
            rel = (rel_dir + "/" + fn) if rel_dir else fn
            if _match_any(rel, SNAPSHOT_SCOPE):
                yield rel


def snapshot_forbidden(root) -> dict:
    """在无在途代理时拍禁写面快照（拍① dispatch 前调用）。reduce 是唯一合法写者且只在零在途时跑，
    所以此刻的快照就是「本窗口所有代理开工前」的真值。"""
    root = Path(root)
    snap = root / SNAPSHOT_DIR
    if snap.exists():
        _shutil.rmtree(snap)
    n = 0
    for rel in _scope_files(root):
        dst = snap / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            _shutil.copy2(root / rel, dst)
            n += 1
        except OSError:
            continue
    snap.mkdir(parents=True, exist_ok=True)
    (snap / ".manifest.json").write_text(json.dumps(
        {"at": _dt.now(_tz.utc).isoformat(timespec="seconds"), "files": n}) + "\n", encoding="utf-8")
    return {"files": n, "dir": SNAPSHOT_DIR}


def restore_forbidden(root, rel: str) -> str:
    """把一个禁写面文件还原到快照态：有快照 → restored；快照无此文件（代理新建）→ deleted；
    无快照可依 → kept_no_snapshot（只记账不动文件）。"""
    root = Path(root)
    r = _norm_rel_path(rel)
    if not r or ".." in r.split("/"):
        return "refused_path"
    snap = root / SNAPSHOT_DIR
    src, dst = snap / r, root / r
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        _shutil.copy2(src, dst)
        return "restored"
    if not (snap / ".manifest.json").is_file():
        return "kept_no_snapshot"
    if dst.is_file():
        try:
            dst.unlink()
            return "deleted"
        except OSError:
            return "delete_failed"
    return "absent"
