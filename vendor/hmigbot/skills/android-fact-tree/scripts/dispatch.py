#!/usr/bin/env python3
"""
dispatch.py — android-fact-tree 的确定性调度/校验 driver。

把「能脚本化的流程」全部脚本化、不可跳过：
  plan 模式：扫源码 → 确定性判架构 → 打印**该走哪条产树路 + 精确步骤计划**（给 agent 执行生成步）。
  gate 模式：对产出的树 → **无差别跑全部产出闸**（output_contract + connectivity）→ 任一红 exit≠0。

⚠️ 本 driver **只调度 + 校验，绝不解析源码成树节点**（那是三个生成器 skill 的事）。
   生成步（toolkit-fact-indexer / app-relationship-tree / compose-fact-tree）是 LLM/子 skill 工作，
   无法纯脚本化——但其**产出必须过本 driver 的 gate 模式**，所以"富化跑了没 / 连通没"是确定性兜底的。

用法:
  python3 dispatch.py plan <android_src>           # 判架构 + 输出产树计划
  python3 dispatch.py gate <tree.json> [<android_src>]   # 跑全部闸，任一红 exit 1
退出码: plan 恒 0（除非源码路径错）; gate 全绿 0 / 有红 1。
"""
import os, sys, json, subprocess


# Windows：stdout/stderr 被管道捕获时默认 cp936，✅/中文会 UnicodeEncodeError；统一 UTF-8（Mac/Linux 无影响）
if sys.platform.startswith("win"):
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script, *args):
    """同 skill 兄弟脚本。本文件按打包器 EXCLUDE_STEMS 以**源码**发运、在系统 python 下跑（永不冻结），兄弟脚本在发行包里是 launcher，
    所以这里 [sys.executable, …] 是对的——冻结态才不能这么写（那时 sys.executable 是 libpython）。"""
    return subprocess.run([sys.executable, os.path.join(HERE, script), *args],   # packaging-contract-ok: keep-source shim
                          capture_output=True, text=True, encoding="utf-8", errors="replace")


PLANS = {
    "pure_traditional": [
        "1. toolkit-fact-indexer：跑 harmony-migration-toolkit → 确定性产 spec/toolkit-fact-tree.json（XML 结构）",
        "2. fork 并行（SKILL.md §2A.2）：腿A=app-relationship-tree 富化(写树) ∥ 腿B=a2h-functional-registry 自产(写 spec/a2h/,registry 已存在则跳过腿B)。fork 前拍树快照;join 必须等两腿都完成",
        "3. a2h-functional-merge：注入 functional_checks（§3.5 ②，需 join 后——merge 同时消费两腿产物）",
        "4. dispatch.py gate <tree> <src>：三闸全绿才可交付",
    ],
    "pure_compose": [
        "1. compose-fact-tree：派 compose-fact-analyzer agent 跑 Phase 0–7（含 enrich_parity 富化）",
        "2. dispatch.py gate <tree> <src>：产出闸（必过）",
    ],
    "hybrid": [
        "1. toolkit-fact-indexer + app-relationship-tree：产 XML 半边基础树（见 SKILL.md §2）",
        "2. compose-fact-tree supplement 模式：读已有树、追加 Compose 节点、解析 Compose→XML 边、fq_class 去重（§2C.2）",
        "3. 反向接缝 XML→Compose（§2C.3，唯一新增源码分析）",
        "4. enrich_parity 富化 Compose 半边",
        "5. dispatch.py gate <tree> <src>：产出闸 + 连通闸（必过，连通闸尤其不可放过）",
    ],
}


def cmd_plan(src):
    r = run("detect_arch.py", src, "--json")
    if r.returncode != 0:
        sys.stderr.write(r.stderr); return r.returncode
    info = json.loads(r.stdout)
    arch = info["arch"]
    print(f"=== android-fact-tree dispatch :: plan ===")
    print(f"架构判定（确定性）: {arch}")
    print(f"launcher: {info.get('launcher_short')} ({info.get('launcher_arch')} 宿主)  "
          f"compose 屏占比≈{info.get('compose_screen_ratio')}")
    print(f"\n产树计划（按 {arch} 路执行；本 skill 只编排，生成由子 skill 完成）:")
    for step in PLANS[arch]:
        print("  " + step)
    if arch == "hybrid" and info.get("launcher_arch") == "xml":
        print("\n⚠️ launcher 在 XML 侧、Compose 在深处 —— 跨边界连通性是成败关键，§2C.3 缝合 + 连通闸务必严格。")
    print(f"\n下一步：执行上述生成步后，必须跑 `dispatch.py gate <tree.json> {src}` —— 任一闸红不得交付。"
          f"\n（gate = 产出契约闸 + (hybrid)连通闸 + 功能维度闸三道；功能维度闸红 = 先走 SKILL.md §3.5 registry 自产/merge 注入再重跑）")
    return 0


def _resolve_skill(rel):
    """跨 skill 路径：同级 skills 根优先 → 用户级 → 工程级；两种平台布局都查（Claude `.claude/skills`、Codex `.agents/skills`），不判环境。
    本文件按打包器 EXCLUDE_STEMS 以源码发运、在系统 python 下跑，不能依赖会被打包器删源的 lib（sibling_exec），故此处内联最小实现。"""
    skills_root = os.path.dirname(os.path.dirname(HERE))  # .../android-fact-tree/scripts → .../skills（源码发运，__file__ 就在 skill 目录里）
    proj = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    # 候选顺序与 sibling_exec.skills_root_candidates 一致：同级根 → 用户级两布局 → 工程级两布局 + <project>/skills
    cands = [os.path.join(skills_root, rel)]
    for base in (os.path.expanduser("~"), proj):
        cands.append(os.path.join(base, ".claude", "skills", rel))   # env-literal-ok：本文件不能 import sibling_exec（见 docstring）
        cands.append(os.path.join(base, ".agents", "skills", rel))   # env-literal-ok
    cands.append(os.path.join(proj, "skills", rel))
    for c in cands:
        if os.path.exists(c):
            return c
    return cands[0]  # 都没有 → 回落同级根下的路径（给报错提示用；改前回落用户级 ~/.claude/skills，两者都只是提示路径）


VV = os.path.dirname(_resolve_skill("arkts-visual-verify/scripts/check_prereq_freshness.py"))


def _vv_cmd(script, args):
    """构造调 arkts-visual-verify 兄弟脚本的 argv（借它的 sibling_exec；取不到则回落系统解释器）。

    不能写死 `[sys.executable, script]`：打包态下 sys.executable 是 Nuitka 的 libpython
    （macOS 上不可执行），且跨 skill 时要找对方自己的编译产物入口。
    """
    try:
        if VV and VV not in sys.path:
            sys.path.insert(0, VV)
        from sibling_exec import sibling_cmd
        return sibling_cmd(script, args)
    except Exception:
        import shutil as _sh
        py = _sh.which("python3") or _sh.which("python") or sys.executable
        return [py, str(script), *args]


def functional_dimension_gate(tree_path):
    """功能维度闸（§3.5 硬断言的机械实现——曾是 SKILL.md 散文 jq，靠 agent 自觉跑，
    真实漏接过：aippt_vvSpeed 2026-07 树 7/1 交付无 functional_checks，merge 7/2 才补，
    Phase 0.5 grounding 结构性跳过、161/189 功能点无安卓真值）。

    判定（N = 树内 functional_checks 总数；registry = <spec>/a2h/functional_registry.json）：
      N > 0                    → PASS（报 N/REG，命中率过低仅提示）
      N==0, registry 不存在     → FAIL（§3.5 ① 未走：先自产/拷贝 registry → merge → 重跑 gate）
      N==0, registry 空(REG==0) → PASS+警告（纯 UI 项目合法：自产过、确无功能点）
      N==0, REG > 0            → FAIL（merge 未注入：契约路径错 / join 全 miss / 漏跑）
    返回 (ok: bool, summary: str)。任何 JSON 损坏 → FAIL（闸必须稳，不静默放行）。
    """
    try:
        with open(tree_path, encoding="utf-8") as f:
            t = json.load(f)
    except Exception as e:
        return False, f"树 JSON 不可读: {e}"
    n = sum(len(r.get("functional_checks") or [])
            for k in ("pages", "fragments", "dialogs")
            for r in (t.get(k) or []))

    reg_path = os.path.join(os.path.dirname(os.path.abspath(tree_path)),
                            "a2h", "functional_registry.json")
    reg_n = None
    if os.path.isfile(reg_path):
        try:
            with open(reg_path, encoding="utf-8") as f:
                reg = json.load(f)
            reg_n = len(reg) if isinstance(reg, list) else len(reg.get("entries") or [])
        except Exception as e:
            return False, f"registry JSON 不可读({reg_path}): {e}"

    if n > 0:
        note = f"functional_checks={n}" + (f" / registry={reg_n}" if reg_n is not None else "（registry 缺失但树已带功能点，放行）")
        if reg_n and n * 3 < reg_n:
            note += "  ⚠️ 注入命中率偏低（N≪REG），建议复查 merge 映射"
        return True, note
    if reg_n is None:
        return False, (f"树 0 条 functional_checks 且契约路径无 registry({reg_path}) "
                       "→ §3.5 ① 未走：先 $a2h-functional-registry 自产（或上游拷贝契约）→ ② merge 注入 → 重跑本 gate")
    if reg_n == 0:
        return True, "registry 近空(0 条) + 树 0 条 → 纯 UI 项目合法放行（建议复查自产提取是否失败）"
    return False, (f"registry 有 {reg_n} 条但树 0 条 functional_checks "
                   "→ merge 未注入（契约路径错 / join 全 miss / 漏跑 a2h-functional-merge）→ 注入后重跑本 gate")


# precondition kind 官方白名单（契约=ART SKILL.md Phase 2.7/2.7b 词汇表；此处是机械强制点）。
# 依据：文档表 7 + 健康树实证 2(login_conditional/intercept_dialog) + 2026-07-10 收编 4
# (permission_required/first_launch_onboarding/business_state/permission_not_granted)。
# 扩词汇必须同时改 ART SKILL.md 词汇表和这里——只改一处 = gate 与契约漂移。
PRECOND_KIND_WHITELIST = {
    "login_required", "vip_required", "login_conditional",
    "param_required", "state_required", "credits_required_amount",
    "nav_redirect_target", "feature_flag", "intercept_dialog",
    "permission_required", "first_launch_onboarding",
    "business_state", "permission_not_granted",
}


def preconditions_gate(tree_path):
    """前置态契约闸（2026-07-10——治两类已发生的真实事故）：
    ① 表外 kind：ART 崩溃抢救的修复 agent 把数据前置自造成 data_required（词汇表没有），
      2.7b rule_a 靠 kind 字符串匹配 → 链式失效 state_required 全丢 → visual-verify 预检假绿，
      trip_2 撞页才暴露。LLM 腿写枚举字段无机械校验 = 系统性风险（同款前科：calibrate 丢 gesture_hints）。
    ② 表内值缺失：整个 phase 被无声丢掉（本例 2.7b），单看"树文件在"发现不了。

    检查（返回 (ok, summary)；JSON 损坏 → FAIL，闸必须稳不静默放行）：
      1. FAIL  preconditions[].kind 出现白名单外值（列出 页/kind）
      2. FAIL  任一 precondition 的 evidence 为空（ART 约束"必须有 evidence"）
      3. FAIL  state_required 缺 data_hint（下游 scenario-builder 规划 fixture 的唯一依据）
      4. FAIL  2.7b 无痕迹：全树 0 条 source 含 state_required_rule 且根无
               _phase_markers.state_required_rule —— 跑了找到 0 也必须写 marker
               （区分"跑了没发现"和"根本没跑"；marker 由 2.7b 收尾写入）
      5. WARN  全树 0 条 login_required（app 可能确无登录，人工确认即可，不 FAIL）
    """
    try:
        with open(tree_path, encoding="utf-8") as f:
            t = json.load(f)
    except Exception as e:
        return False, f"树 JSON 不可读: {e}"

    off_vocab, no_evidence, sr_no_hint = [], [], []
    n_login = 0
    has_rule_trace = bool((t.get("_phase_markers") or {}).get("state_required_rule"))
    for k in ("pages", "fragments", "dialogs"):
        for r in t.get(k) or []:
            for pc in r.get("preconditions") or []:
                kind = pc.get("kind") or "<missing>"
                if kind not in PRECOND_KIND_WHITELIST:
                    off_vocab.append(f"{r.get('id')}:{kind}")
                if not (pc.get("evidence") or "").strip():
                    no_evidence.append(f"{r.get('id')}:{kind}")
                if kind == "state_required":
                    if not (pc.get("data_hint") or "").strip():
                        sr_no_hint.append(r.get("id"))
                if kind == "login_required":
                    n_login += 1
                if "state_required_rule" in (pc.get("source") or ""):
                    has_rule_trace = True

    fails = []
    if off_vocab:
        fails.append(f"表外 kind {len(off_vocab)} 条: {off_vocab[:6]}{'...' if len(off_vocab) > 6 else ''}"
                     "（LLM 自造值；按语义归并到白名单 kind 或走 ART SKILL.md 正式扩表）")
    if no_evidence:
        fails.append(f"evidence 为空 {len(no_evidence)} 条: {no_evidence[:6]}")
    if sr_no_hint:
        fails.append(f"state_required 缺 data_hint: {sr_no_hint}（scenario-builder 无法规划 fixture）")
    if not has_rule_trace:
        fails.append("2.7b 无痕迹（0 条 state_required_rule source 且无 _phase_markers.state_required_rule）"
                     "→ 数据前置态推导没跑或没留痕；补跑 2.7b（找到 0 也要写 marker）")

    if fails:
        return False, " ; ".join(fails)
    note = f"kind 全在白名单 / evidence 齐 / state_required 均带 data_hint / 2.7b 有痕迹"
    if n_login == 0:
        note += "  ⚠️ 全树 0 条 login_required——若 app 有登录功能则前置抽取漏了，人工确认"
    return True, note


def cmd_gate(tree, src=None):
    print("=== android-fact-tree dispatch :: gate（确定性，不可跳过）===\n")
    failed = []

    # 架构上下文（决定连通闸跑不跑 + 产出契约闸的 NEED 映射）。无 src 时按 hybrid（保守多跑）。
    arch = "hybrid"
    if src:
        ra = run("detect_arch.py", src, "--json")
        if ra.returncode == 0:
            arch = json.loads(ra.stdout).get("arch", "hybrid")

    # 1. 产出契约闸 = **复用 visual-verify 自己的 Step 1.0 门控** check_prereq_freshness.py
    #    （v6.5 架构感知：PASS / NEED:<对应生成器>）。它就是 visual-verify 认的那把尺：
    #    验 navigation_contract≥80% / reach≥50% / uncertain≤30%，且兼容 reach_path(s) 双名、
    #    对 compose/hybrid 合法跳过 purpose。比自造闸更准、且失败直接告诉你该跑哪个生成器。
    prereq = os.path.join(VV, "check_prereq_freshness.py")
    args = [tree]
    if src:
        args += ["--source", src]
    else:
        args += ["--arch", arch]
    r1 = subprocess.run(_vv_cmd(prereq, args), capture_output=True, text=True,
                        encoding="utf-8", errors="replace")
    verdict = (r1.stdout or "").strip().splitlines()[0] if r1.stdout.strip() else ""
    print(f"[产出契约闸 check_prereq_freshness.py] {verdict}   {r1.stderr.strip()}")
    if r1.returncode != 0 or not verdict.startswith("PASS"):
        failed.append(f"check_prereq_freshness({verdict})")
    print()

    # 2. 连通闸：**仅 hybrid 跑**（check_prereq 不做跨架构连通）。纯路图上"不可达"多是
    #    am-start 合法可达 / 各自 factcheck B1 管，跑连通闸会误报。
    if arch == "hybrid":
        r2 = run("connectivity_gate.py", tree)
        print(r2.stdout.rstrip())
        if r2.returncode != 0:
            failed.append("connectivity_gate")
        print()
        print("[arch=hybrid] 注：compose-fact-tree/factcheck.py 的 15 闸仅核验 Compose 半边，"
              "其 B 闸对 XML 节点误报，以上两闸为准。\n")
    else:
        print(f"[arch={arch}] 连通闸跳过（仅 hybrid 跑；纯路可达性由 am-start 兜底 / 各自 factcheck 管）\n")

    # 3. 功能维度闸：§3.5 硬断言的机械实现（A2H 项目树必带 functional_checks，
    #    否则 visual-verify Phase 0.5 grounding + B.4.5 静默跳过、功能测试不发生且不报错）
    f_ok, f_msg = functional_dimension_gate(tree)
    print(f"[功能维度闸] {'✅ PASS' if f_ok else '❌ FAIL'}   {f_msg}\n")
    if not f_ok:
        failed.append("functional_dimension")

    # 4. 前置态契约闸：kind 白名单 + evidence/data_hint 完备 + 2.7b 痕迹
    #    （表外值和"整个 phase 无声丢失"都在这里拦——2026-07-10 data_required 事故的机械化）
    p_ok, p_msg = preconditions_gate(tree)
    print(f"[前置态契约闸] {'✅ PASS' if p_ok else '❌ FAIL'}   {p_msg}\n")
    if not p_ok:
        failed.append("preconditions_contract")

    if failed:
        print(f"❌ 闸未全过: {failed} —— 不得交付。NEED:<x> 即该补跑的生成器/补接缝边后重跑 gate")
        return 1
    print("✅ 全部闸 PASS —— 树可交付给 arkts-visual-verify（visual-verify 自己的门控认它）")
    return 0


def main(argv):
    if len(argv) < 2 or argv[1] not in ("plan", "gate"):
        print(__doc__); return 2
    if argv[1] == "plan":
        if len(argv) < 3:
            print("用法: dispatch.py plan <android_src>"); return 2
        return cmd_plan(argv[2])
    if argv[1] == "gate":
        if len(argv) < 3:
            print("用法: dispatch.py gate <tree.json> [<android_src>]"); return 2
        return cmd_gate(argv[2], argv[3] if len(argv) > 3 else None)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
