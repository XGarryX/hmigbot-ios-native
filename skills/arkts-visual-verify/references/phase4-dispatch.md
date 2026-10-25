> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# Phase 4 主会话调度

> **Codex 子代理派发约定**
>
> - 通用执行任务调用真实工具 `spawn_agent`，设 `agent_type="worker"`。
> - 具名 agent 调用 `spawn_agent`，设 `agent_type="<name>"`；定义位于 `.codex/agents/<name>.toml`。
> - `task_name` 必须是本会话内唯一的 snake_case；任务正文放在 `message`。
> - 派发后调用 `wait_agent`，等目标任务发回 FINAL_ANSWER 再继续。不要把 `spawn_agent` 返回的任务句柄当成最终结果。

> 主会话只做调度——每个 batch 派一个 sub-agent 进独立上下文跑批内全部页面。本会话**不读截图**、**不直接遍历 page**。
>
> 跨 batch **阻塞传递**和**carry-forward 重测**是核心机制（见 §4.A 第 5 步、§4.C）。

---

## Step 4.A 调度循环

### Step 4.A.0 增量重验前置（④，2026-07-12；round-2+ 才有意义，round-1 恒全量）

> pass 不是豁免、是带指纹的缓存。本步产"本轮该重验的页清单"，其余 pass 页沿用上轮结论
> （常规轮 100%→25-45%）。**PIPELINE_VERSION 铁律**：判定管线任一变更（本 prompt / oracle
> 三源逻辑 / R9 等新规则 / 相似度阈值）→ 必须 bump 版本号，否则旧 pass 会带着旧管线的盲区
> 复用。当前 PIPELINE_VERSION 见 SKILL.md 顶部常量。

```text
# fixer 上轮改动文件 = 上一轮 spec/fix/round-{N-1}/*/*.md 的 §6 attempt "改动文件" 行汇总
#   （或 --changed-from-git 直接取 git diff HEAD——两者取并集最保守）
# 第一步：汇总上轮 fixer 改动文件（stdout 是逗号分隔清单，记为 <CHANGED>；<N-1> 手工代入）
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/collect_changed_files.py \
    --round <N-1> --project-root .
# 第二步：把上一步 stdout 原样填进 --changed-files（两平台通用；bash 里也可用 $(...) 一步串起来，PowerShell 语法不同，见 windows-setup.md）
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/incremental_verify.py \
    --project-root . --round {N} --pipeline-version {PIPELINE_VERSION} \
    --changed-files "<CHANGED>" --changed-from-git --sample-rate 0.10 \
    > spec/visual-verify/_incr_plan.json
# ⚠️ stdout 重定向在 Windows PowerShell 5.1 默认写 UTF-16，会毁掉 JSON——PowerShell 里请用
#    `python3 ... | Out-File -Encoding utf8 spec/visual-verify/_incr_plan.json`（或 pwsh 7+ 默认即 utf8）
# 终局 sweep（收敛宣告/交付前）：加 --full，全量重验一次消除增量残余
```
`_incr_plan.json.to_verify` = 本轮要跑的页；`reused_pass` = 沿用上轮 pass 不重跑。
degraded_full=true（公共组件/资源/路由类 C 桶改动 → GLOBAL 失效）时 to_verify=全池。
**下面主循环只对 to_verify 里的页真跑 batch**；reused_pass 页直接沿用上轮 round 目录结论
（不写新 finding=符合"文件存在即失败"invariant）。round-1 或缓存不存在 → to_verify=全部（等价全量）。

### Step 4.A.1 verify 跑完回写缓存（两阶段的第二阶段）

本轮所有 batch 跑完、Phase 6 汇总后**必须回调 commit-pass**，把本轮判 pass 的页写进缓存
（带当前代码/oracle/管线指纹），否则下轮它们仍算 never_passed 白跑：
```text
PASS_IDS=<本轮 manifest 里 status=pass 的 page_id 逗号拼接>
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/incremental_verify.py \
    --project-root . --round {N} --pipeline-version {PIPELINE_VERSION} \
    --commit-pass --pass-ids "$PASS_IDS"
```

```python
# ─── 准备 ──────────────────────────────────────────────────────────
batches = read_json("spec/visual-verify/batches.json")
incr = read_json("spec/visual-verify/_incr_plan.json")   # ④ 增量重验清单（Step 4.A.0 产）
verify_set = set(incr["to_verify"])                       # 只对这些页真跑；reused_pass 沿用上轮
sentinels  = set(incr.get("sentinel_pages", []))          # 抽样哨兵页：批内注入"加严模式"标记

# ④ 消费点（两处，必须都做）：
#   a) 派 batch 前过滤：batch.pages = [p for p in batch.pages if p in verify_set]；
#      过滤后空 batch → mark_batch_done(skip_reason=all_cached)，不派 sub-agent；
#      reused_pass 页在本轮 manifest 记 {status: reused_pass, from_round: cache.round}（留痕非静默）
#   b) 派 batch 的 prompt 注入哨兵清单：batch 内 ∈ sentinels 的页加一行
#      "本页为抽样哨兵：加严模式——相似度阈值收紧 0.05 + 行为对账全元素扫（勿用轻量路径）；
#       若翻出上轮漏判，finding 照常写 + manifest 记 sentinel_catch=true（管线有洞信号，
#       主会话据此扩大重验面并把洞修进管线后 bump PIPELINE_VERSION）"

# carry-forward: 扫上一轮 NAV_FAILED 的 edge
retry_edges = []
prior_round_dir = f"spec/fix/round-{N-1}/ui"
if exists(prior_round_dir):
    for md in glob(f"{prior_round_dir}/CRASH_P*_nav_failed_*.md"):
        fm = parse_frontmatter(md)
        if fm.disposition not in ("resolved", "wont_fix"):
            retry_edges.append({
                "from_page": fm.v4_edge.from_page,
                "to_page":   fm.v4_edge.to_page,
                "prior_md":  md,
                "prior_round": fm.round,
            })

# 全局 blocked_pages 累积（跨 batch）
global_blocked_pages = {}   # page_id → blocked_by_md_path

# ─── 主循环（**机械化 per-batch dispatch**，遵守 SKILL.md §0.8）─────────────
# ★2026-07-20 起默认走 Step 4.A.2 双派并行（本串行循环降级为兜底/单 batch 调试）——
#   batch 内各步骤（scenario/validate/B 审核/mark done）语义不变，只是调度时序变了
# 主代理不许自己 iterate batches；必须靠 next_batch.py 一个个取
# 伪代码约定：run(<命令串>) = 在当前 shell（PowerShell / bash 皆可）执行该命令并取 stdout；不是真函数
WHILE True:
    # ── 0) 拿下一个 batch ──────────────────────────────────────
    rc, next_json = run(
      "python3 $SKILLS_ROOT/arkts-visual-verify/scripts/next_batch.py "
      "--batches spec/visual-verify/batches.json "
      "--progress spec/visual-verify/progress.json"
    )
    IF rc == 2:
        break                              # 全部 batch 完成，整轮收工
    IF rc != 0:
        raise BatchDispatchError(next_json)

    next_batch = json.loads(next_json)
    batch_id   = next_batch["batch_id"]
    trip_id    = next_batch["trip_id"]

    # ── 0.a) trip 起点 reset + scenario_chain（首 batch 才跑）──────
    # ★单侧化 2026-07-12：只驱动 **HMOS**——iOS基线是 Phase 2 录制产物，Phase 4 不再
    # reset/造态iOS端（旧"双端各跑"废止；iOS pm clear 在此除烧时间外还会毁掉iOS侧登录态）。
    # HMOS 侧必须 kill + 清数据（仅 force-stop 会让 isFirstLaunch=false 残留跳过首启链）；
    # 清完由 scenario_chain 重建到态。详见 references/batch-classification.md 的 data_cleared 定义
    IF next_batch["trip_scenarios_needed"]:
        reset_app_hmos()                   # aa force-stop + bm clean -d（仅 HMOS）
        device_id  = {"harmonyos": hmos_target}
        package    = {"harmonyos": hmos_bundle}

        for sc in next_batch["scenario_chain"]:
            # 必走 run_scenario_with_verify.py 包装脚本
            # （禁止直跑 scenario_run.py — 包装脚本管失败计数 + transient retry + exit code 路由）
            for device in ["harmonyos"]:
                while True:  # exit 10 自修循环（计数器在脚本内，超 3 次会自动 exit 40）
                    rc = run(
                        f"python3 $SKILLS_ROOT/arkts-visual-verify/scripts/run_scenario_with_verify.py "
                        f"{sc} {device} --trip {trip_id} "
                        f"--device-id {device_id[device]} --package {package[device]}"
                    )
                    IF rc == 0: break                                  # 跑通，继续 chain
                    IF rc == 10:                                       # selector miss / 跑挂
                        # 必派 scenario-builder agent 学·修（无判断空间；学习/修配方统一归 builder，
                        # runner 只回放不学习——2026-07-10 裁撤其探索职能，与末尾路由表一致）
                        artifact_dir = run("python3 -c \"import glob,os;print(max(glob.glob('spec/scenarios/artifacts/*/'),key=os.path.getmtime))\"").strip()   # 最新一次 artifacts 目录
                        scenario_task = spawn_agent(            # 定义于 .codex/agents/scenario-builder.toml
                              agent_type="scenario-builder",
                              task_name=f"repair_scenario_{sc}_{device}",
                              message=f"""scenario={sc} device={device} 回放跑挂，修配方（不要重跑验证）：
1. Read {artifact_dir}/ui_dump_after.xml + {artifact_dir}/result.json 看哪步 selector miss
2. Read spec/scenarios/{sc}.yaml
3. 改 selector / 加 wait_for / 调坐标兜底，**保留原 token/preconditions 配置不动**
4. **不要**调 scenario_run.py 重跑——主代理会重跑包装脚本验证
5. 改完直接 return""")
                        wait_agent()                              # 等 scenario_task FINAL_ANSWER
                        continue                                       # 重跑包装脚本（attempt 计数器已 +1）
                    IF rc in (20, 30, 40, 50):                         # 升级用户（凭据 / needs_input / 自修超限 / 环境）
                        # 按 alignment-rules.md §3 升级用户格式
                        # ★留痕闸（2026-07-11）：升级前必跑对照实验执行器，JSON 附进升级信息（缺=无效升级）
                        gate_json = run(f"python3 $SKILLS_ROOT/arkts-visual-verify/scripts/gate_experiment.py "
                                         f"--scenario {sc} --failed-device {device} --ios-id ... --hmos-id ... "
                                         f"--ios-pkg ... --hmos-pkg ...")   # verdict=functional_regression → 改写 P0 单，不升级
                        attempts_summary = run("python3 -c \"import json;print(json.dumps(json.load(open('spec/visual-verify/progress.json'))['scenario_attempts'],ensure_ascii=False))\"")
                        ESCALATE_TO_USER(format=f"""
⚠️ visual-verify 卡死请示
阶段: scenario
scenario: {sc}, device: {device}
失败现象: run_scenario_with_verify.py exit {rc}（20=凭据缺/30=needs_input/40=自修 3 次超限）
已尝试: {attempts_summary}
对照实验: {gate_json}   ← 必附，缺=无效升级
建议: (a) 用户介入跑 --save-creds 建档 / (b) 跳过本 trip / (c) 终止本轮 visual-verify
""")
                        return                                          # 整 round 中止

    # ── 0.b) 数据态阶梯 checkpoint（2026-07-10 ③；与 Phase 2 SKILL 步骤 2.5 同款，设备=harmonyos）──
    #    本 batch 页面的 state_required（python 读树取 preconditions）按 trip 去重后逐个：progress.json.states_provisioned
    #    已 green → 秒过；有配方 → check（包装脚本）红则 create 造一次；无配方 → 派 scenario-builder
    #    学（带 data_hint）。⚠️ HMOS 数据态与iOS**不共享**（作品在本地 DB，两端各造各的——
    #    HMOS 侧 create 需同账号单独跑一次 + fixture 文档 hdc file send）。NEED_HUMAN_FIXTURE →
    #    只冻结含该 state 的页面，其余照跑。states_provisioned 按 (trip, device) 分键。

    # ── 以下 batch 内逻辑：**只处理 next_batch，不要 iterate 其它 batch** ───
    # ── 1) 整 batch 全 blocked → 直接写占位，不派 sub-agent
    all_blocked = all(p["page_id"] in global_blocked_pages for p in next_batch["pages"])
    IF all_blocked:
        log(f"batch {batch_id} 全部 blocked，跳过派发")
        for p in next_batch["pages"]:
            write_blocked_placeholder(p["page_id"], global_blocked_pages[p["page_id"]])
        run(f"python3 mark_batch_done.py --batch_id {batch_id} "
             f"--manifest <empty/placeholder> --status all_blocked")
        continue

    # ── 2) 准备 sub-agent prompt（注入 blocked_pages / retry_edges / nav_mode）
    # nav_mode：复用上游已判定的架构（tree.source.toolkit），不重判。
    #   swiftui-fact-tree → "compose"（子代理自导航,不调 walk_to/click_and_verify,见 sub-agent-batch-prompt.md §导航方式）
    #   harmony-migration-toolkit / 其它 → "xml"（原确定性 walk_to 流程,零改动）
    # 一次性算即可（整轮不变）：
    #   tk = 读 spec/toolkit-fact-tree.json 的 .source.toolkit 字段
    #        （python3 -c "import json;print(json.load(open('spec/toolkit-fact-tree.json'))['source']['toolkit'])"）
    #   nav_mode = "compose" if tk=="swiftui-fact-tree" else "xml"
    batch_blocked = [
        {"page_id": p["page_id"], "blocked_by_md_path": global_blocked_pages[p["page_id"]]}
        for p in next_batch["pages"] if p["page_id"] in global_blocked_pages
    ]
    batch_retry_edges = [
        e for e in retry_edges if any(p["page_id"] == e["from_page"] for p in next_batch["pages"])
    ]
    prompt = render(
        "references/sub-agent-batch-prompt.md",
        batch_json_ref = f"batches.json > {trip_id} > {batch_id}",
        current_round  = N,
        ios_serial = config.ios_serial,
        hmos_target    = config.hmos_target,
        ios_pkg    = config.ios_pkg,
        hmos_bundle    = config.hmos_bundle,
        hmos_ability   = config.hmos_ability,
        blocked_pages  = batch_blocked,
        retry_edges    = batch_retry_edges,
        nav_mode       = nav_mode,        # "compose" → 子代理自导航；"xml" → 原 walk_to 流程
    )

    # ── 3) 派 sub-agent（每次 dispatch 必须只含 1 个 batch_id；自查 prompt 不超 1 个）
    batch_task = spawn_agent(
        agent_type = "worker",
        task_name  = f"visual_verify_batch_{batch_id}",
        message    = prompt,
    )
    wait_agent()  # 等 batch_task FINAL_ANSWER 后才读 manifest

    # ── 4) 读 manifest 累计 blocked / findings
    manifest_path = f"spec/visual-verify/batches/{batch_id}/manifest.json"
    manifest = read_json(manifest_path)
    for prop in manifest.get("blocks_subtree_propagation", []):
        for blocked_pid in prop["blocked_pages"]:
            global_blocked_pages.setdefault(blocked_pid, prop["root_cause"])

    # ── 5) 机械化产出闭环校验（脚本层，查 enumerable 形式漏）
    #    含 UI 交付(截图/disposition/md5) + **feat 交付**(树声明 functional_checks[N] → manifest
    #    须交付 N 点，否则 issues.feat_not_delivered = feat 维度静默跳过；--fact-tree 默认标准树路径，
    #    纯 UI/缺树自动跳过不误伤)。信号分离：feat 漏与 UI 漏各自独立成 issue。
    run(f"python3 $SKILLS_ROOT/arkts-visual-verify/scripts/validate_batch_output.py "
         f"--batches spec/visual-verify/batches.json --round {N} --only-batch {batch_id}")
    # exit 2 最多重派 1 次

    # ── 5.5) **必派 B 审核员**（契约-交付对比，覆盖未知 unknowns；详见 本文件 §B 审核员 prompt 段）
    # 每 batch 必派 1 次，3 分钟硬卡，跨项目通用（不依赖项目语义）
    verifier_prompt = render(
        "本文件 §B 审核员 prompt 段",
        batch_id = batch_id,
        batch_page_ids_json = json.dumps([p["page_id"] for p in next_batch["pages"]]),
        trip_id = trip_id,
        N = N,
    )
    b_attempt = 0
    WHILE b_attempt < 2:  # 最多 2 轮 A↔B 补漏循环
        b_task = spawn_agent(
            agent_type = "default",
            task_name  = f"b_verifier_{batch_id}_{b_attempt + 1}",
            message    = verifier_prompt,
        )
        wait_agent(timeout_ms=180000)
        b_result_raw = <从 b_task 的 FINAL_ANSWER 消息取回的文本>
        b_result = json.loads(extract_last_json(b_result_raw))
        IF b_result["result"] == "PASS" OR b_result["result"] == "TIMEOUT":
            break  # PASS 进下一步；TIMEOUT 不阻塞但记 alert
        # FAIL: 回 A 给具体 gaps 补漏
        retry_prompt = render(
            "references/sub-agent-batch-prompt.md",
            batch_json_ref = ...,           # 同原 prompt
            current_round  = N,
            ...,
            b_gaps         = b_result["gaps"],   # 新增字段：A 必须按 gaps 列表补
            retry_reason   = "B 审核发现以下契约-交付漏对齐项，必须补齐",
        )
        a_retry_task = spawn_agent(
            agent_type = "worker",
            task_name  = f"a_retry_{batch_id}_{b_attempt + 1}",
            message    = retry_prompt,
        )
        wait_agent()  # 等 a_retry_task FINAL_ANSWER
        # A 补完后再读 manifest，进下一次 B（最多 2 次）
        manifest = read_json(manifest_path)
        b_attempt += 1
    IF b_attempt == 2 AND b_result["result"] == "FAIL":
        # 2 轮 A↔B 仍 FAIL → 升级用户（alignment-rules.md §3 升级格式）
        escalate_user(stage="b_verifier", batch_id=batch_id, gaps=b_result["gaps"])

    # ── 6) 必跑 mark_batch_done.py，否则下次 next_batch.py 会把同一 batch 再派一次
    run(f"python3 $SKILLS_ROOT/arkts-visual-verify/scripts/mark_batch_done.py "
         f"--batch_id {batch_id} --manifest {manifest_path} "
         f"--progress spec/visual-verify/progress.json")
    # ↑ next iteration 再跑 next_batch.py，自动拿到下一个未完成的 batch

# 跨 trip 结束后
# Phase 5 跨 batch systemic 聚类
# Phase 6 汇总
```

### Step 4.A.2 双派并行调度（**默认模式**，2026-07-20 移植自 Phase 2 §3；上面的串行循环降级为兜底/单 batch 调试用）

原理：采集占设备，判定/审核零设备——两条线时间片分离，判定藏进下一批采集的飞行期
（iOS侧同协议实测 +21.9 分；鸿蒙侧对比+写单更重，收益更大）。**并行只发生在主会话层**，
sub-agent 仍单输入单动作单返回；角色拆分按判读制（采集只出观察，判定独立判），
见 sub-agent-batch-prompt.md §角色模式。

```
设备      [采集b01]           [采集b02]           [采集b03]
主会话  W0↑派        ↓W1双派           ↓W2双派           ↓W3
判定线             [判定b01→B审→done] [判定b02→B审→done] [判定b03→B审→done]
```

节拍（主会话逐字执行）：
- **W0**：`next_batch.py --stage capture` → b01；trip 首批先跑 scenario_chain（占设备）；
  派采集 b01（role=capture）。
- **Wk（采集 bk 归队）**：
  1. `mark_batch_done.py --stage capture --batch_id bk --manifest <capture_manifest>`
  2. `next_batch.py --stage capture` → b(k+1)；**跨 trip 时先跑新 trip 的 scenario_chain**
     （占设备；判定线此刻照常在飞，不受影响）
  3. **同时派**：采集 b(k+1)（占设备）∥ 判定 bk（零设备，吃 capture_manifest）
  4. 处理已归队的判定 bj：validate_batch_output → B 审核员（原 §5.5 循环）→
     `mark_batch_done.py`（full）——这一串全零设备，藏在采集飞行期里
- 末批采集归队：派判定末批 ∥ 主会话做归因/Phase 5 预聚类；全部 done → Phase 5/6。

**B-gaps 补漏的设备排队**：gaps 分两类——零设备可补（判定重写/补分类）→ 立即重派判定；
**需设备的补漏（补采/补实点）→ 进 capture 补漏队列，下一个边界窗口优先于新批采集执行**
（设备单占，绝不与在飞采集并发）。

**判定线多开（2026-07-21）**：判定 agent 零设备约束——边界窗口发现判定积压 ≥2 批
（capture_done 而未 done 的批数）时，**一次并发派多个判定 agent**（每个吃各自批的
capture_manifest，按批分文件零竞态，上面的写冲突分析原样成立；上限 3，防 token 洪峰）。
对比+写单是历史批次的墙钟大头，判定比采集慢时积压会把末批判定裸露在墙钟里——多开把它藏干净。
判定内容/质量与单开完全一致，纯调度改动。每批的 validate→B 审核仍在该批判定归队后串行做。

**写冲突分析（为什么不需要 Phase 2 的 run_meta 式快照）**：
- 采集写：`screenshots/harmony/*` / `hmos_evidence/*` / `batches/<id>/capture_manifest.json`——按批分文件；
- 判定写：`spec/fix/round-N/{ui,feat}/*.md` / `batches/<id>/manifest.json`——按批分文件，与采集零交集；
- `progress.json`/`batches.json`：**只有主会话在边界窗口写**（mark_batch_done），agent 一律不碰。
⟹ 天然零竞态。两条铁律代替快照：**判定 agent 禁 adb/hdc（零设备）；采集 agent 禁写 fix md（零判定）**。

**兜底（数据最多晚到不会丢）**：capture_done 但判定挂了/漏派 → batch 永不 done →
judge 游标（`next_batch.py` 默认 stage）下轮仍返回它 → 按 capture_manifest 重派判定即可
（采集产物已落盘，无需重采）。反向同理：采集半途挂 → 没标 capture_done → capture 游标重派该批
（幂等：已截的图按"已有即复用"跳过）。

---

## Step 4.B 阻塞子树计算（fact-tree BFS）

当 sub-agent 在 manifest 里报 `blocks_subtree_propagation` 时，它已经计算好了 `blocked_pages`：

```python
def compute_subtree_blocked(failed_edge_target: str, fact_tree: dict, visited: set) -> list[str]:
    """从 failed_edge_target 出发 BFS，找出所有通过该 edge 才能到达的 page。"""
    # 简化版：无脑 BFS（接受过度阻塞）；后续按需精化
    blocked = set()
    queue = [failed_edge_target]
    blocked.add(failed_edge_target)
    while queue:
        cur = queue.pop(0)
        for e in fact_tree.flow_graph.edges_from(cur):
            if e.to not in blocked and e.to not in visited:
                blocked.add(e.to)
                queue.append(e.to)
    return sorted(blocked)
```

**关于过度阻塞**：如果某 page 有 2 条 reach_path（其中 1 条通过失败 edge、另 1 条没），无脑 BFS 会把它误标 blocked。**MVP 接受这个不完美**——本轮少测几页 vs 算法复杂度，权衡选简单。下轮重测时只有 root cause 在 retry_edges 里，其它 path 可能正常工作 → "假 blocked" 自动解锁。

---

## Step 4.C carry-forward 状态机

```
每个 NAV_FAILED markdown 有 disposition 字段，轮间状态机：

  round N:    新建 NAV_FAILED markdown, disposition=null
  round N+1:  主会话 carry-forward 把 edge 加入 retry_edges
              sub-agent 重测该 edge:
                ok        → 跑完后把 markdown disposition 设 "resolved"
                still fail → 写新一份 NAV_FAILED markdown (created_at 更晚) 覆盖旧的
  round N+M:  resolved disposition 的 markdown 不再 carry-forward

  "wont_fix" disposition (人工设): 永久不再 carry-forward
```

---

## 最小可行调度示例（伪代码）

```python
def dispatch(round_n: int, project_root: Path):
    batches = json.load(open("spec/visual-verify/batches.json"))
    retry_edges = collect_retry_edges_from_prior_round(round_n - 1)
    global_blocked: dict[str, str] = {}

    for trip in batches["trips"]:
        run_scenarios(trip["scenario_chain"])
        for batch in trip["batches"]:
            batch_blocked = [
                {"page_id": p["page_id"], "blocked_by_md_path": global_blocked[p["page_id"]]}
                for p in batch["pages"] if p["page_id"] in global_blocked
            ]
            if len(batch_blocked) == len(batch["pages"]):
                for p in batch["pages"]:
                    write_blocked_placeholder(p["page_id"], global_blocked[p["page_id"]], round_n)
                continue

            prompt = render_template("sub-agent-batch-prompt.md", {
                **batch_context(trip, batch),
                "blocked_pages": batch_blocked,
                "retry_edges": [e for e in retry_edges if any(p["page_id"]==e["from_page"] for p in batch["pages"])],
            })
            run_subagent(prompt)

            manifest = json.load(open(f"spec/visual-verify/batches/{batch['batch_id']}/manifest.json"))
            for prop in manifest.get("blocks_subtree_propagation", []):
                for pid in prop["blocked_pages"]:
                    global_blocked.setdefault(pid, prop["root_cause"])

            validate_batch_output(batch["batch_id"], round_n)

    phase2_5_cross_batch_cluster(round_n)  # 主会话 inline 读 manifest 聚类（见 phase5-systemic.md），无对应独立脚本
    write_summary(round_n)
```

---

# Phase 4 B 审核员 prompt（契约-交付对比，项目无关）


> 主会话在每个 batch sub-agent (A) 完成后必派一个 sub-agent (B) 跑契约-交付对比，**3 分钟硬卡**。
> B 不知道任何项目语义（不知道"back"/"H5"/"login"等具体含义），只看 skill 声明的形式契约。

## 派发时机（见 phase4-dispatch.md §Step 4.A）

```
A 跑完 batch + validate_batch_output.py 通过
  ↓
派 B（必派，每 batch 1 次）
  ↓
B PASS → mark_batch_done.py → next batch
B FAIL → 主会话回 A 补 gaps → 再 B → 最多 2 轮 → 仍 FAIL 升级用户
```

## B 的 prompt 模板（主会话 render 后派发）

```
你是 visual-verify B 审核员（契约-交付对比专员）。

任务：对 batch={batch_id} 的 A 交付做契约-交付对比，找出任何"声明的期望但无对应交付证据"的项。

═══ 契约（先全读，约 2 分钟）══════════════════════════════════════

1. **fact-tree 期望**（该 batch 每个 page 的结构声明）:
   ```text
   # 取 pages+fragments 里 id ∈ batch_page_ids 的节点（跨平台 python 一行式；勿整读树）
   python3 -c "import json,sys;t=json.load(open('spec/toolkit-fact-tree.json'));ids=set(json.loads(sys.argv[1]));print(json.dumps([n for n in (t.get('pages') or [])+(t.get('fragments') or []) if n.get('id') in ids],ensure_ascii=False,indent=1))" '[{batch_page_ids_json}]'
   ```

2. **batch 期望**（该 batch 应处理的 page 列表 + scenario_chain）:
   ```text
   # 取 batches.json 里 batch_id=={batch_id} 的那条
   python3 -c "import json;print(json.dumps([b for b in json.load(open('spec/visual-verify/batches.json'))['batches'] if b['batch_id']=='{batch_id}'],ensure_ascii=False,indent=1))"
   ```

3. **skill 契约**（sub-agent 必须输出的字段）:
   用 Grep 工具（或 `grep -E`）在 `$SKILLS_ROOT/arkts-visual-verify/references/{sub-agent-batch-prompt,phase4-classify-write,fix-file-schema}.md`
   里搜 `必须|强制|必填|MUST|REQUIRED`，只看前 40 条命中（Windows 无 grep/head 管道时直接用 Grep 工具）。

═══ 交付（再全读，约 30 秒）══════════════════════════════════════

- manifest: `spec/visual-verify/batches/{batch_id}/manifest.json`
- 落盘 finding md: 列 `spec/fix/round-{N}/ui/` 里文件名含相关 page 的条目（Glob 工具 / `ls` / `dir` 均可）
- HMOS 截图存在性: `ls spec/visual-verify/screenshots/harmony/round-{N}/{trip_id}/`
- iOS 截图存在性: `ls spec/visual-verify/screenshots/ios/{trip_id}/`

═══ 对比规则（4 条全通用，不依赖项目语义）═════════════════════════

1. **数量对齐**：契约声明 N 个对象 → 交付应有 N 个对应记录
   - 例：batches.json 该 batch 有 8 个 page → manifest.pages_status 有 8 个 key
   - 例：fact-tree.pages[X].edges_to_test 列 3 条 → manifest.pages_status[X].edges_tested 应 ≥ 3（或显式 skip_reason）

2. **字段完备**：契约要求字段 X 必填 → manifest 该字段非 null 非空字符串
   - 例：sub-agent prompt 说 "back_tested 字段必须明确 true/false" → manifest 不允许 null
   - 例：fix-file-schema 说 "differences[] 必须穷举" → similarity < 1.0 但 differences=[] 必填异常

3. **状态-证据匹配**：交付声明 status=X → 必须有契约规定的 evidence
   - status=fail → 必须有至少 1 个 fix_files 引用的 ALIGN/CRASH md 真存在
   - status=pass → 必须有 HMOS 截图存在
   - status=blocked → 必须有 BLOCKED_* md 占位（含 disposition: skipped 或 blocked）

4. **类型隐含**：fact-tree.pages[i].kind 决定隐含期望——**不要硬编码类型清单**，按 fact-tree 实际给的 kind 检 manifest 是否有相应字段记录
   - kind=Activity 或 NavDestination → 隐含可 back → 检 back_tested 字段
   - kind=Dialog → 隐含可 dismiss → 检 dismiss_tested 字段
   - kind=WebView → 隐含 URL 验证 → 检 url_verified 字段
   - kind=Fragment → 隐含父 page 内嵌渲染 → 检 host_page 在 manifest 中已 pass
   - 任何 fact-tree.pages[i] 的字段（不限于 kind）若声明了 X → 隐含 X 应在 manifest 有对应交付

5. **行为对齐铁律完备性**（与 sub-agent prompt "行为对齐铁律" 段联动）：
   若 sub-agent prompt 含 "行为对齐铁律" 段（grep `行为对齐铁律` 验证存在），则 manifest.pages_status 内每个非 BLOCKED page 必须含 `interaction_test_summary` 字段（含 `tested_count` / `diff_count` / `untested_skipped[]` 三子字段）。
   缺字段 / `tested_count == 0` 但 status=pass / `untested_skipped` 列出可测但跳过的交互 → A 跳过了行为铁律 → gap，action="本 page N 个可见交互元素需补双端测试，记录差异立独立 finding"。

6. **功能维度(feat)交付完备性**（契约 = fact-tree functional_checks；与机械闸 `validate_batch_output.py` 的 `feat_not_delivered` 同判据，B 作 LLM 兜底）：
   对每个**可达**（截到图、status≠blocked）且 fact-tree 该 page 声明 `functional_checks[N>0]` 的 page，manifest.pages_status[name] 必须含 `functional_checks` 记录且把 N 点交代清楚：
   - 无 `functional_checks` 记录 / `total==0` → gap「feat 维度未执行」，action="本 page 树声明 N 功能点，须逐点 B.4.5 dual-oracle 判定产 feat 单"
   - `total < N`（树 N vs manifest total 不符）→ gap「功能点被丢弃」
   - `tested==0` 且 `interaction_test_summary.untested_skipped` 无理由 → gap「N 点既没测也没记跳过理由」
   —— 这是 Q1 执行段"feat 静默跳过"的 LLM 防线，**与 UI 信号分离**：报 gap 时明确标"功能维度缺，非 UI"。

═══ 不做的事 ════════════════════════════════════════════════

- ❌ **不做视觉对比**——A 已做过 multimodal，B 不重复
- ❌ **不做项目语义判断**——不知道"back"/"wallpaper"是什么含义，只看声明 vs 交付
- ❌ **不读截图**——只看数据 + 抽 1-2 finding md 摘要
- ❌ **不为凑业绩编造 gap**——找不到漏测 = 输出 PASS

═══ 输出（严格 JSON）═════════════════════════════════════════

```jsonc
{"result": "PASS"}
```
或
```jsonc
{
  "result": "FAIL",
  "gaps": [
    {
      "page": "<page_id>",
      "contract_source": "fact-tree.pages[X].edges_to_test 声明 3 条 / sub-agent-batch-prompt L278 要求 back_tested 必填 / ...",
      "delivery_evidence_missing": "manifest.pages_status[X].edges_tested = 1 / back_tested = null / ...",
      "action": "<一句具体补漏指令，给 A 看>"
    }
  ]
}
```

═══ 铁律 ═══════════════════════════════════════════════════

- **3 分钟硬卡**（超时 → 写 `{"result":"TIMEOUT"}` 退出）
- **gaps 必须含** page + contract_source + delivery_evidence_missing + action 四字段（缺一作废）
- **contract_source 必须可追溯**到具体文件 + 行号 / JSON 字段路径，否则视为编造
- **跨项目不变**：本 prompt 任何字面值都不含项目语义（"back"/"login"等），换 App 直接复用
```

## 主会话调用示例

```python
# render B prompt
batch_page_ids_json = json.dumps([p["page_id"] for p in batch["pages"]])
verifier_prompt = render(
    "本文件 §B 审核员 prompt 段",
    batch_id = batch_id,
    batch_page_ids_json = batch_page_ids_json,
    trip_id = trip_id,
    N = current_round,
)

# 派 B
b_task = spawn_agent(
    agent_type = "default",
    task_name = f"b_verifier_{batch_id}",
    message = verifier_prompt,
)
wait_agent(timeout_ms=180000)  # 3 分钟硬卡；后续从 b_task 的 FINAL_ANSWER 取结果

# 解析结果
b_result = json.loads(extract_last_json(result.message))
if b_result["result"] == "FAIL":
    # 回 A 补漏
    retry_prompt = render_a_retry(batch, gaps=b_result["gaps"])
    a_retry_task = spawn_agent(
        agent_type="worker",
        task_name=f"a_retry_{batch_id}",
        message=retry_prompt,
    )
    wait_agent()
    # 再 B（最多 2 轮）
elif b_result["result"] == "TIMEOUT":
    log_warning(f"B timeout on {batch_id}, 仍走 mark_batch_done 但记 alert")
else:
    pass  # PASS, 进 mark_batch_done
```

## 扩展契约（新增检查无需改 B）

需要 B 检新维度时**只改 skill 契约**，B prompt 不变：

| 场景 | 改契约的位置 |
|---|---|
| 要求每页测特定交互（如长按 / 双击）| `sub-agent-batch-prompt.md` 加"必须"段；`fact-tree` 给相应字段；B 按"字段完备" + "类型隐含"自动覆盖 |
| 要求每页截特定 mode（如 web / long）| fact-tree.pages[i].capture_mode 字段；B 按"字段完备"对照检 |
| 要求 finding 必含某段（如 §7 reach_path）| `fix-file-schema.md` 用"必填"措辞声明；B 按"字段完备"自动检 |

**B 永远只做一件事：契约 vs 交付的形式对齐**。

---

## scenario 包装脚本 exit code 路由（机械，无判断空间）

`run_scenario_with_verify.py` 调用时必须传 `TRIP_ID` env（否则跨 trip 计数器串扰）：
```text
python3 run_scenario_with_verify.py {scenario} {device} --trip {trip_id} --device-id {...} --package {...}   # bash 亦可 env 前缀 TRIP_ID={trip_id}
```

> **本表是全 skill 的 scenario 失败统一路由**（v2026-07-10c 起无独立"预检"环节——状态验证=各
> trip/batch 边界**真跑 scenario 本身**，失败按本表 at-need 分诊：派 builder 学·修 / 要凭据 /
> 对照实验。Phase 2 步骤 2（trip 态建立）与本处 0.a 用同一张表、同一个包装脚本）。
> 配方文件不存在 → 不算失败，直接派 scenario-builder 学（等价 exit 10 路由）。

| exit | 必须执行 |
|---|---|
| 0 | 继续 dispatch sub-agent |
| 10 | **必** 派 `scenario-builder` agent 修配方（学习归 builder；scenario-runner 只回放不学习），learned 后再调本脚本（不许直接升级用户）。**device=harmonyos 且iOS侧存在同名已验收配方时，派发 prompt 必须注入iOS先验**（yaml ios 分段 + artifacts 最近成功 run.log + creds 共享说明——builder 走 S0.7 对位翻译，禁从零盲探）。builder 返回 NEED_APP_FIX + divergence（四证归因，见其铁律 11）时：divergence 转 Phase 4 出单素材；**该态若为门禁/被测功能态（登录/授权）且挡整个 trip → 冻结该 trip、其页写 blocked 引用该 P0（blocks_subtree 列全量下游），修好后重验自然解锁**。★2026-07-12 用户拍板：**删掉"显式授权再派 builder 做绕路注入"这条路**——注入绕行不产单、腐化、污染验证语义（实爆见 memory baseline-gate-per-page）；被测功能撞缺就诚实报 P0 冻结，绝不注入维持假环境。（测试数据前置态如作品/文档的注入仍合法，见 builder 铁律 9 边界）|
| 20 | **先查 `spec/baseline/dev_info.json`**（契约参考文件，存在才读）：有手机号/万能码 → 主线程自动跑 `--save-creds` 建档并重跑本脚本，**不打扰用户**；dev_info 缺失或无凭据字段才升级用户（账号资产是人工的，builder 不发明）|
| 30 | **必跑 gate_experiment.py（对照实验执行器，见下）**；verdict=functional_regression→P0 单；否则派 `scenario-builder`；builder 报 NEED_HUMAN_FIXTURE（附证据+GATE_EXPERIMENT_JSON）才升级用户 |
| 40 | 同上：先跑 gate_experiment.py → 派 `scenario-builder`（prompt 附 §6 失败历史）；builder 报缺才升级用户（升级必附 JSON）|
| 50 | 升级用户（环境问题，如 hdc/adb 不在 PATH、Pillow 未装，让用户装环境，不是改 scenario）**——先跑 gate_experiment.py，升级必附 JSON** |

### 门禁功能对照实验铁律（HARD-GATE，违反算漏测事故）

**背景**：登录 / 上传图 / 授权 / 跳转到态 这类 scenario/前置步骤，**本身就是被迁移的功能点**。它们失败时，流程的默认归类是「needs_input / blocked / 环境问题 → 升级用户」——**这条路没有 FAIL 通道，会把一个真·功能退化（如鸿蒙登录按钮没真正发起登录）系统性地掩盖成"环境没就绪"**。这是已发生的真实漏测（鸿蒙登录 P0）。

**铁律**：任何 scenario/前置步骤在某端失败、准备升级用户(exit 30/40/50)或标 blocked 之前，**必须先跑对照实验**，不许凭直觉下"环境/网络/数据"结论。
**★机械化+留痕闸（2026-07-11，治"铁律靠自觉迟早被跳"）**：三步实验已脚本化——
```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/gate_experiment.py \
    --scenario <sc> --failed-device <ios|harmonyos> \
    --ios-id <..> --hmos-id <..> --ios-pkg <..> --hmos-pkg <..> \
    [--skip-other-replay]   # 消耗型 scenario 禁例行重放时用（verdict 至多 inconclusive）
```
输出 GATE_EXPERIMENT_JSON（自动落盘 gate_experiments/）按 verdict 机械分支：
`functional_regression` → **必写 P0 feat 单，禁升级环境**；`environment` → 允许升级；
`inconclusive` → 附 JSON 升级人工判。**升级用户/标 blocked 的信息里必须原样附带该 JSON
——没有 JSON = 对照实验没做 = 无效升级，退回重做**（③failure_mode 是 duration 代理指标，
用 dump/日志证据覆盖它时须在升级信息里写明覆盖理由）。
1. **同端可达性**：该前置功能在**另一端(通常iOS)用相同输入**能否成功？(如iOS用同账号同验证码能否登录)
2. **平台健康**：失败端的设备/网络是否本身健康？(ping 通、其它功能可跑、UI 完整)——证通，排除环境。
3. **失败形态**：是「即时失败(<1s 关页/无 loading/无报错)」还是「等待后超时」？即时失败 = 处理逻辑没真执行，强指向功能未实现；超时 = 才考虑网络。

**判定**：
- 另一端相同输入**成功** + 失败端平台健康 + (尤其)即时失败 → **门禁功能退化，不是环境问题**。写 **P0 FAIL feat 单**(kind=IMPL_MISSING，severity=P0)，正文带对照实验三项证据 + `## 6 阻塞影响(blocks_subtree)` 列被它阻塞的全部下游功能点，**绝不**降级成 blocked/skip/needs_input。
- 只有对照实验**证明**是环境(另一端同样失败 / 平台确实不通 / 等待超时)→ 才允许按 exit 30/40/50 升级用户。

**默认假设 = 功能缺陷优先**；"环境"是跑完对照实验后的**结论**，不是遇阻时的**借口**。
