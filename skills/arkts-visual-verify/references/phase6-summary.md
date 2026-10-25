# Phase 6 — 写汇总文件 + 自检 + 退出

> **Codex 子代理派发约定**
>
> - 具名 agent 调用真实工具 `spawn_agent`，设 `agent_type="<name>"`；定义位于 `.codex/agents/<name>.toml`。
> - `task_name` 必须是本会话内唯一的 snake_case；任务正文放在 `message`。
> - 派发后调用 `wait_agent`，等目标任务发回 FINAL_ANSWER 再继续。
> - visual-fixer 和 visual-fixer-reviewer 均由主会话串行派发，不嵌套，不依赖任何子代理深度配置。

> 从 SKILL.md §4 Phase 6 抽出。所有 batch 完成 + Phase 5 完成后 Read。
>
> **这是本 skill 的收尾阶段，必须完整执行 6 步，缺一视为整轮 visual-verify 失败。**

---

## Step 6.1: 写 spec/fix/round-N/_index.md

> schema §八 _index.md 规范

```markdown
# Round {N} 索引（visual-verify）

> 生成时间：<ISO8601>

## UI 层（{count} 条）
- [P0010 标题栏背景偏亮](ui/ALIGN_P0002_color_mismatch_titlebar-bg.md) [ALIGNMENT_DIFF][P1]
- [P0023 H5 详情页 lang 参数缺失](ui/URL_P0023_query_lang.md) [URL_MISMATCH][P0]
- [P0017 订单状态页加载崩溃](ui/CRASH_P0017_app_crash_on_load.md) [CRASH][P0]
- ...
```

> visual-verify 不写 "Feature 层" 段（那是 dt-verifier 的职责）。如果 dt-verifier 在同一轮也跑了，由 a2h-verify 在 round-N/ 顶层合并 _index.md。

---

## Step 6.2: 写 spec/fix/round-N/_summary.md

> schema §八 _summary.md 规范，包含「总计 / 页面维度 / checks performed / Top10 / 未变化项」5 段。visual-verify 必填的是后 3 段：

```markdown
# Round {N} 统计（visual-verify 部分）

> 跑测时间：<ISO8601>

## 总计（按 kind，仅 visual-verify 产出的部分）

| 维度 | ALIGNMENT_DIFF | URL_MISMATCH | CRASH | SYSTEMIC | 合计 |
|---|---|---|---|---|---|
| ui | x | x | x | x | x |

## 页面维度（每页一行）

| page_id | 页面名称 | reachability | capture_mode | similarity | high | medium | low | rounds | status |
|---|---|---|---|---|---|---|---|---|---|
| P0001 | Index 首页 | public | single | 0.92 | 0 | 1 | 2 | 2 | ✅ pass |
| P0010 | MineSettingPage | public | long | 0.85 | 1 | 2 | 1 | 5 | 🔄 partial |
| P0017 | OrderStatusPage | public | - | - | - | - | - | - | 💥 blocked |
| P0023 | H5 详情页 | public | web | - | 1 | 0 | 0 | 1 | ❌ fail (URL) |

## 缓存性能

| 指标 | 值 |
|---|---|
| iOS 命中数 | x |
| iOS 未命中数 | x |
| 命中率 | x% |
| 节省截图时间（估算） | xx 秒 |
| 节省 scenario 时间（估算） | xx 秒 |
| 缓存条目总数 | x |
| 本轮新写入 | x |

## Checks performed（证明 verifier 跑过）

| verifier | check | 总数 | 失败 | pass 率 |
|---|---|---|---|---|
| visual-verify | pages screenshot-compared | N | x | x% |
| visual-verify | siblings_order_checks | N | x | x% |
| visual-verify | icon_semantic_checks | N | x | x% |
| visual-verify | url consistency (web pages) | N | x | x% |

## Top 10（按 severity + affects 排序，systemic 优先）

1. [SYSTEMIC missing-nav-destination](ui/_systemic/SYSTEMIC_missing-nav-destination.md) — affects 8
2. ...

## 未变化项（与 round-{N-1} 比）

无变化的开放问题数：x（详见 _delta.md）
```

---

## Step 6.3: 写 spec/fix/round-N/_delta.md（round-0 跳过）

> 与上一轮对比；模板见 schema §八 提到的 `reconcile-rules.md`。如该 reconcile-rules 文件不存在，至少要给出：fixed（上轮有本轮没了）、new（本轮新增）、regressed（GREEN→RED）、unchanged 四个 section。

---

## Step 6.4: 更新 spec/fix/_state.yaml

> **本步不手改 current_round / invocation** —— 轮次推进只经 `round_budget.py`（Phase 6.5）。
> 手改会绕过预算闸，正是要杜绝的事。本步只更新 visual-verify 自己的统计字段：

```yaml
last_verifier_run_at: <ISO8601>
last_verifier_sources: [..., visual-verify]      # 追加，不覆盖（dt-verifier 可能也在跑）
last_verifier_results:
  visual-verify:
    pages_compared: N
    pages_blocked: x
    siblings_order_checks: N
    icon_semantic_checks: N
    url_consistency_checks: N
    failed_total: x
```

---

## Step 6.5: 跑 schema §十 自检脚本（必跑，不通过整轮失败）

```text
# N = python3 $SKILLS_ROOT/arkts-visual-verify/scripts/lib_resolve_round.py 打印的 round 号（读 _state.yaml.current_round，无 yq 依赖）
# ROUND_DIR = spec/fix/round-<N>
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/run_fix_self_check.py <N>
# 完整说明见 references/fix-file-schema.md §十；至少跑 9 项检查：
# 1) 文件名 = id  2) 必填字段齐全  3) fixer_layer 合法  4) 5 sections 齐全
# 5) SYSTEMIC.affects 非空  6) visual-verify 必填字段非 null  7) similarity ∈ [0,1]
# 8) dt 来源不应有 visual 专属字段（visual-verify 不影响这条，但执行无害）  9) ID 唯一
```

任一 ❌ → 重写对应 markdown，再次跑自检；连续 3 次失败 → 走 alignment-rules.md §3 升级用户（schema_self_check 阶段）。

---

## Step 6.6: ★主动派 visual-fixer 闭环修复★（2026-05-23 新加）

写完 _summary.md / _delta.md / _state.yaml 并通过自检后，本 skill **主动**派 visual-fixer agent 处理本轮 **ui/ + feat/** markdown（独立工具模式：单派一个 visual-fixer，按 `fixer_layer` 自分流修 ui+feat 两层，**不再转 a2h-fixer**）。visual-fixer 是本 skill 专属修复 agent。

**派发前先清新鲜戳**（fixer 要改代码了，设备包即将过期）：

```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/auto_install_artifacts.py \
  --hmos-root {hmos_project_root} --clear-stamp
```

> 清戳放在**派发前**而不是 fixer 落盘后：会话若在 fixer 跑完后中断，无戳状态会让下次
> Phase 1.1.d 老老实实重编——宁可多编一次，也不许拿旧包截图。

```python
# Phase 6 自检通过后立即执行
import os
round_dir = f"spec/fix/round-{N}"
def _has(sub):                              # sub ∈ {"ui","feat"}
    d = os.path.join(round_dir, sub)
    return os.path.isdir(d) and any(
        f.endswith(".md") and not f.startswith("_") for f in os.listdir(d))

has_ui, has_feat = _has("ui"), _has("feat")

# ★ feat-only 轮也要派（修复缺口：旧逻辑 ui/ 空就 skip，会漏掉只有 feat 单的轮）
if has_ui or has_feat:
    # 调用真实 Codex 工具 spawn_agent；具名 agent 定义于 .codex/agents/visual-fixer.toml
    fixer_task = spawn_agent(
        agent_type="visual-fixer",
        task_name=f"visual_fixer_round_{N}",
        message=f"""
PROJECT_ROOT: {abs_project_root}
ROUND: {N}
INPUT_DIR: spec/fix/round-{N}/            # 扫 {{ui,feat}}/ 两个子目录（本 agent §2 Step 1 自分流）
SBS_DIR: spec/visual-verify/screenshots/sbs/round-{N}/        # ui 单双端对比图
GROUNDING_DIR: /tmp/grounding/                                # feat 单 grounding 截图

按 `fixer_layer` 双通道处理（详见你 agent 定义 §2）：
- **ui 单**（ALIGN_/URL_/CRASH_/PAGE_MISSING_ + _systemic/SYSTEMIC_*）→ §2.2 通道：
  强制读 evidence 指向的 sbs 双端对比图，按 page_id 整体诊断，改 view 层
  （features/business_*/src/main/ets/{{pages,components,widgets,router}}/ + resources）。
- **feat 单**（feat/*.md，kind=IMPL_MISSING，dual-oracle 产，无 sbs/无 page_id）→ §2.7 通道：
  读 grounding 截图 + 正文 §2 的 expected_ios(主判据) + ios_anchor，自己定位实装点，
  **端到端实装**（onClick → ViewModel 方法 → 数据流 → 副作用），feat 白名单（§4.2）已放行
  features/business_*/src/main/ets/{{viewmodels,services,model,repository,api}}/。

约束：
- 修完代码落盘即退，**不动 git、不重编、不复测**（下一轮 visual-verify 重截兜底）
- **disposition 字段不许动**（v4 起 fixer 完全不写 disposition，由下轮 verifier 单一裁判）。只追加 §6 attempt + 改代码
- **feat 层就是你的活，不转 a2h-fixer**（独立工具模式全包）；ui 单缺 ViewModel 方法 → 另立 feat side-finding
- **不要派 reviewer**（你没有子代理派发权（`spawn_agent` 归主会话））。Step 5 只备料：写 attempts.json + git-diff.patch 后直接 return，reviewer 由本主会话在 Step 6.7 派
- 真修不动（OG 私仓完全黑盒 / OS API 缺失 / 需后端配合 / 客户必须决策）→ 直接升级用户
"""
    )
    wait_agent()
    # 确认 fixer_task 已发回 FINAL_ANSWER 后再进 Step 6.7；spawn_agent 首次返回的只是任务句柄。
else:
    print(f"[phase3] round-{N} ui/ 与 feat/ 均空，跳过 visual-fixer 派发")
```

**为什么自带闭环不像旧设计那样等 a2h-verify 调度**：

| 维度 | 旧 (a2h-verify 调 a2h-fixer) | 新 (visual-verify 自调 visual-fixer) |
|---|---|---|
| 多模态信号 | a2h-fixer 只读 markdown 文字 | visual-fixer 强制读 sbs 图，多模态诊断 |
| 信息密度 | 跨多个 verifier 共调度，markdown 是唯一接口 | sbs 图 + page 上下文一次传，单 page 整体修 |
| 跨域适配 | a2h-fixer 修 feat/ + ui/ 通用 | visual-fixer 同样修 ui+feat 两层全包；按 `fixer_layer` 分流到对应通道（ui→§2.2 sbs+page_id；feat→§2.7 grounding+expected_ios+端到端实装）+ 对应写盘白名单 |
| 解耦 | 每轮 a2h-verify 决定是否调 fixer | visual-verify 自治，结果直接落盘 |

**git 边界约定**：visual-fixer 改完文件**落盘即返回**，本 skill 与 visual-fixer 都**不动 git**（既不 add 也不 commit）。git 操作完全归用户或上游调用方（如 a2h-verify）统筹。

---

## Step 6.7: ★派 visual-fixer-reviewer 反摸鱼质检★（2026-08-04 新加，派发权从 fixer 上提）

> **为什么在这里而不在 fixer 内部**：`visual-fixer` 的 tools 白名单是
> `Read, Glob, Grep, Edit, Write, Bash, Skill`，**没有子代理派发权（不能调 `spawn_agent`）**——旧设计让它自己
> 旧设计要求 fixer 内部再派 `visual-fixer-reviewer`，结构上派不出去，reviewer 从未真正跑过；
> 而 fixer 自检里那条只 `echo ⚠️` 不中止，下轮 Step 1.5 读不到上轮 report 又静默跳过，
> **反摸鱼闭环两头俱断、整轮空转零报错**。主会话有 `spawn_agent`，且这里能架真闸——
> 故派发权上提。这是「凡没有机械物件承接的步骤都会在边界上掉」的又一实例。

Step 6.6 的 visual-fixer **return 之后立即执行**（同一主会话，串行）：

```python
import json, os, subprocess
log_dir       = f"docs/autofix-log/round-{N}"
attempts_json = f"{log_dir}/attempts.json"
report_md     = f"{log_dir}/visual-fixer-reviewer-report.md"

# 有 attempt 才有得审：无 attempt（本轮全 skip/blocked）合法跳过
n_attempts = 0
if os.path.isfile(attempts_json):
    with open(attempts_json) as f:
        n_attempts = len(json.load(f))

    # 调用真实 Codex 工具 spawn_agent；具名 agent 定义于 .codex/agents/visual-fixer-reviewer.toml
    reviewer_task = spawn_agent(
        agent_type="visual-fixer-reviewer",
        task_name=f"visual_fixer_reviewer_round_{N}",
        message=f"""审 visual-fixer round-{N} 的 attempt（4-check：empty_diff / duplicate_hypothesis / wrong_edit / lazy_escalation）。参数：
    round               = {N}
    project_root        = {abs_project_root}
    attempts_json_path  = {log_dir}/attempts.json      # fixer Step 5 已写
    git_diff_path       = {log_dir}/git-diff.patch     # fixer Step 5 已写
    sbs_dir             = spec/visual-verify/screenshots/sbs/round-{N}/
    need_info_json_path = {log_dir}/need-info.json     # 仅本轮有 C.6 报缺时存在；无则跳过 Check 4
先 Read attempts_json_path + git_diff_path（+ need_info_json_path 若存在），按你定义里的算法审，
写 {report_md} 并返回结构化 JSON。"""
    )
    wait_agent()
    # 确认 reviewer_task 已发回 FINAL_ANSWER，再执行下方 report 硬闸。
else:
    print(f"[phase6] round-{N} 无 attempt，跳过 reviewer")
```

**★ 硬闸（HARD-GATE，不是警告）**：reviewer 派完必须验产物，缺则**中止本轮 Phase 6**，
不许带着"没质检过的修复"进下一轮：

```text
# LOG_DIR = docs/autofix-log/round-<N>；规则：attempts.json 条数>0 时 reviewer report 必须存在非空且含 "## flag" 段
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/check_reviewer_report.py docs/autofix-log/round-<N>
# exit 1 = 硬闸红，中止本轮 Phase 6
```

**flag 落位（主会话做，fixer 不做）**：Read report 的 `## flag 列表` 段 → 追加到
`{log_dir}/visual-fixer-summary.md` 末尾的 `## Reviewer flag` 段（含 flag 类型 +
evidence + suggested_action）。**不改 disposition**——那是下轮 verifier 的单一裁判权。
下轮 fixer 的 Step 1.5 从 `docs/autofix-log/round-<N-1>/visual-fixer-reviewer-report.md`
读它，**路径契约与旧设计完全一致**，只换了写这份 report 的派发方。

**fail-soft 边界**：reviewer 自身跑挂（parse error / 超时）→ 允许在 summary 记
`- reviewer_skipped: <原因>，下轮所有 finding 视同 flag=reviewer_unavailable 全部换方向`，
但**必须是 reviewer 真被派出后才失败**；"根本没派"不在 fail-soft 范围内，由上面的硬闸挡住。

---

## Step 6.8: ★fix 后置构建（构建锚点①）★（2026-08-12 构建点重排）

Step 6.6 派过 fixer（`has_ui or has_feat` 为真、代码已落盘）时**必跑**；本轮零 finding、fixer 没派则跳过（代码没变，无需重编）。

```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/auto_install_artifacts.py \
  --ios-root {ios_project_root} --package {package} \
  --hmos-root    {hmos_project_root}    --bundle  {bundleName} \
  --rebuild
CASE 脚本 exit:
  0 → 出包+装机成功，脚本已打新鲜戳 → 下一轮 Phase 1.1.d 见戳秒过（同批改动只编这一次）
  3 → 构建失败（fixer 改出了编译错误——修复循环里的常态事件，不是意外）：
      自动调 $hmos-fix-build-errors（指向 {hmos_project_root}，其内部自带
      构建→修错→再构建循环，直到绿或达其内部轮次上限）：
        修好 → 复跑本脚本 --rebuild（增量编译秒级；确保装上的是修复后的包 + 打戳）→ 继续
        它也修不动 → 升级用户，ABORT（附 hvigorw 错误摘要）
      ★ 每个构建点最多自动修一次，防 build-fix 与 visual-fixer 互相打架的 ping-pong
  * → 升级用户: "装机失败，请检查设备连接" → ABORT
```

**为什么放在 fix 之后而不是只靠下一轮遍历前**（2026-08-12 用户拍板）：
1. **"跑了"≠"成功了"**——重编必须以"顺利出包"为 pass 判据，失败要当场解决（接
   hmos-fix-build-errors），不是留给下一轮再撞一次。
2. **错误归因最准**：刚跑完的 fixer 就是嫌疑人，此刻修编译错误上下文最全。
3. **每个 fix 批次恰好编译一次**：本步打戳 → Phase 1.1.d `--skip-if-fresh` 秒过，
   消掉旧设计"fix 完编一次+遍历前又编一次"的重复。O(batch) → O(1)。

---

## Step 6.9: 写 spec/visual-verify/report.md（人类可读总览）

这份是给人看的，不是给 fixer 的入口；保留页面维度表 + 关键差异 link 到 markdown 即可：

```markdown
# 视觉对比验证报告 — Round {N}

- 执行时间: YYYY-MM-DD HH:mm
- spec/fix/round-{N}/ui/ 产出：{count} 条
- 自检结果: ✅ PASS / ❌ {fail 项列表}

## 页面可达性分类
| 分类 | 页面数 | 处理方式 |
|---|---|---|
| public | X | 完整截图对比 |
| login_walled (via scenario) | Y | scenario 跑通后截图对比 |
| data_dependent (via scenario) | Z | scenario 跑通后截图对比 |

## 截图对比总览（透传 _summary.md 页面维度）
| 页面 ID | 页面名称 | 可达性 | 总体相似度 | high | medium | low | rounds | status | spec/fix 产出 |
|---|---|---|---|---|---|---|---|---|---|
| P0001 | Index | public | 92% | 0 | 1 | 2 | 2 | ✅ pass | 0 个 markdown |
| P0010 | MineSettingPage | public | 85% | 1 | 2 | 1 | 5 | 🔄 partial | 4 个 markdown |
| P0017 | OrderStatusPage | public | - | - | - | - | - | 💥 blocked | 1 个 CRASH md |

## 关键 markdown 入口
- [round-{N}/_index.md](../fix/round-{N}/_index.md)
- [round-{N}/_summary.md](../fix/round-{N}/_summary.md)
- [round-{N}/ui/](../fix/round-{N}/ui/)

## 后续动作
visual-fixer 已在 Step 6.6 跑过（如有 finding），代码改动已落盘但未涉及 git。git 操作（add / commit）由用户 / 上游调用方统筹。下一轮由本 skill Phase 6.5 的 `round_budget.py next` 按退出码自行路由（0=继续 / 10=预算用尽 / 11=收敛）；预算用尽后若还想继续，任何调用方（用户或 a2h-verify）再调一次本 skill 即可，轮次差值预算天然累计。
```
