# Step 4.3 / 2.4 / 2.5 — 差异分类 + 写 markdown + 单页收尾

> **写单先产骨架（2026-07-12）**：本文件的分类/去重规则照旧，但落盘动作一律经 `render_finding_skeleton.py`（frontmatter/§0/§6/§7/carry-forward 机械生成，LLM 只填 `<<LLM:...>>` 判定段）——见 sub-agent-batch-prompt.md 写单铁律。禁手打骨架。

> 从 SKILL.md §4 Step 4.3 / 2.4 / 2.5 抽出。sub-agent 多模态返回后 Read。
>
> **写 markdown 前必读** [`fix-file-schema.md`](fix-file-schema.md)（唯一权威 schema）。本文件只列概要 + visual-verify 专属差异展开规则。

---

## Step 4.3: 差异分类

> **SKILL.md §1.1.1 强制**：分类**默认**是 bug。`design_difference` / `dynamic_content` 必须满足 §1.1.1 的三种证据之一才能采用，且需在 progress.json 写明证据出处。

### 2.3-0 合并两路差异来源（结构 oracle + 多模态，P0-B）

本步的输入差异集 = **多模态 `differences[]`** ∪ **结构 oracle `differences[]`**（Step 4.2-pre 的 `*.struct.json`，`source="structural_oracle"`，仅 missing/extra/order 三类）。合并去重规则：

- **同一 page + 同一元素文本 + 同一 category** 视为重复，**保留结构 oracle 那条**（确定性、带精确 region/顺序证据），多模态重复条丢弃。
- 结构 oracle 的 missing/extra/order 都是 `is_migration_bug=true` 硬差异，按下表正常分类写盘（order→`layout_bug`；missing→`needs_investigation`；extra→`layout_bug`）。
- 结构 oracle 条目带 `dynamic_suspect: true` 的（时钟/日期等）**不直接当 bug**，按 `dynamic_content` 处理（仍需 §1.1.1 证据，缺证据则回落 bug）。
- `position_hints` **不在本步**单独成单——它已注入多模态 prompt，由多模态在 sbs 复核后决定是否产 position 差异。

将（合并后的）差异按可修复性分类：

| 类别 | 说明 | 处理方式 |
|------|------|---------|
| `auto_fixable` | `is_migration_bug=true` 且 description 已写明属性级差异（如"字号 14 vs 16"、"padding top 0 vs 42"） | 交 visual-fixer：auto_fixable 类别 |
| `layout_bug` | 元素消失/尺寸异常/位置错乱，需先读代码确认根因再修 | 交 visual-fixer：layout_bug 类别，由 fixer 排查根因并改代码；**测量闭环/满尺寸+margin 溢出/Stack 定位三类系统性布局缺陷的判据与修法见 [`layout-troubleshooting.md`](layout-troubleshooting.md)**（同类单先按其 §5 硬规则聚 SYSTEMIC） |
| `resource_missing` | HMOS 端缺资源（图标/图片/9-patch） | 交 visual-fixer：resource_missing 类别，**禁止 fallback 简化**——由 fixer 走资源迁移/SVG 重绘/Canvas 等兜底链路 |
| `needs_investigation` | 缺失元素，需分析代码才知道怎么加 | 交 visual-fixer：needs_investigation 类别，**禁止本 skill 直接判 partial** |
| `design_difference` | **仅当**用户对话明确豁免 / OS 系统级 UI 已证明无 App API 干预 / iOS 源端本就动态随机 | 必须在 progress.json 该差异处带 `waiver_evidence`（见 SKILL.md §1.1.1） |
| `dynamic_content` | 运行时数据差异（列表内容/时间戳不同） | 必须给出 iOS 源码片段证明该字段为运行时随机值；缺证据视为 bug |

**禁止的简化路径**（每条曾在本 skill 实战中导致问题，不得重犯）：
- ❌ 资源缺失 → fallback 纯色 / 简化样式 → 判 design_difference
- ❌ 动画无法对齐 → 判 platform_difference 跳过
- ❌ 字号 ±2px 差异 → 判 "在 ±10% 容差内" 直接 PASS（容差仅适用于像素级渲染抖动，不适用于设计稿明确数值差）
- ❌ Tab 排序不一致 → 判 dynamic_content 不修

---

## Step 4.4: 把每条差异写成 spec/fix/round-N/ui/*.md

**这是本 skill 的核心交付动作**。把 Step 4.3 分类后的差异、Step 4.2 的 siblings_order_checks / icon_semantic_checks / missing_elements / extra_elements / scroll_needed、以及 Step 4.1.5 检测到的崩溃，**逐条**展开成一个 markdown 文件，落到 `spec/fix/round-N/ui/`。

> **必读**：[`fix-file-schema.md`](fix-file-schema.md) 是本步的唯一规范。下面只列概要 + visual-verify 专属注意点，所有 ID 派生 / frontmatter 字段 / Section 写法的细节以 schema 为准。

> **⚠️ 本步写的 ui 单不是最终态**：本步（在 sub-agent 时序上 = B.4）先于 dual-oracle（B.4.5）。同页若某元素**既视觉不一致（本步写 ui 单）又功能退化（B.4.5 判 feat FAIL）**，B.4.5 的"同页 feat↔ui 对账闸"会按 H 失败模式 fold 掉一端（feat primary 时**会 rm 本步刚写的 ui 单**，外观验收点并入 feat 单）。所以：① ui 单的 `context_slug`/元素描述要写清楚（B.4.5 靠它和 functional_check 模糊匹配）；② 不要假设本步写下的 ui 单一定留到 manifest——被 fold 的会标 `folded_into`。详见 [`sub-agent-batch-prompt.md`](sub-agent-batch-prompt.md) B.4.5 step 5b。

### 2.4-0 写 markdown 前的强制单次注入：fact-tree §1 + §7 双段

写每条 finding 的 markdown 前，sub-agent **必须**调一次 `inject_factree_refs.py`，输出 JSON 含两段：

```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/inject_factree_refs.py {page_id} {trip_id}
# stdout 是一段 JSON：{"spec_lines":[...], "reach_steps":[...]}
# SPEC_LINES  = .spec_lines  数组逐行拼接
# REACH_STEPS = .reach_steps 数组逐行拼接（直接读 JSON 即可，无需 jq）
```

- **§1 "Spec 引用"**：把 `SPEC_LINES` **追加**到原有 `来源:` 行后（不替换 spec/baseline 引用），让 fixer 按 visual-fixer.md L137 可 grep `.kt/.java/.xml` 全 Read
- **§7 "实际可达路径"**：把 `REACH_STEPS` 原样填入

**铁律**：禁止手工编造 spec_lines 或 reach_steps。若脚本输出含 `iOS 源参考缺失` / `unknown — Phase 2 baseline 缺失` 兜底文案，**原样填入**——这是 fixer 触发兜底逻辑的信号，不要美化抹掉。

**用途**：
- §1 让 visual-fixer 拿到真 iOS 源路径 → 修代码前 Read .kt/.xml 求证（不再凭规则/截图猜）
- §7 让 visual-fixer / verifier / Phase 7 mini-round 用同一 reach_path 复现，避免"换路径走通了误判 fixed"

### 2.4-a 差异展开规则（一差异 = 一文件）

| 输入 | 展开规则 | 文件名（id）模板 | kind |
|---|---|---|---|
| `differences[i]`（普通项） | 1 项 → 1 文件 | `ALIGN_P{page_id}_{diff_kind}_{context_slug}` | `ALIGNMENT_DIFF` |
| `siblings_order_checks[i]` (`match=false`) | 1 项 → 1 文件 | `ALIGN_P{page_id}_layout_drift_{container_slug}` | `ALIGNMENT_DIFF` |
| `icon_semantic_checks[i]` (`match=false`) | 1 项 → 1 文件 | `ALIGN_P{page_id}_icon_mismatch_{context_slug}` | `ALIGNMENT_DIFF` |
| `missing_elements[i]` | 1 项 → 1 文件 | `ALIGN_P{page_id}_missing_element_{slug}` | `ALIGNMENT_DIFF` |
| `extra_elements[i]` | 1 项 → 1 文件 | `ALIGN_P{page_id}_extra_element_{slug}` | `ALIGNMENT_DIFF` |
| `scroll_needed=true` (single 模式下) | 整页 1 文件 | `ALIGN_P{page_id}_scroll_overflow` | `ALIGNMENT_DIFF` |
| `compare_webview_urls.py` 的 `diff[]` 每项 | 1 项 → 1 文件 | `URL_P{page_id}_{diff_path_slug}` | `URL_MISMATCH` |
| Step 4.1.5 崩溃 | 1 文件 | `CRASH_P{page_id}_app_crash_on_{phase}` | `CRASH` |
| Step 4.-1 scenario 跑挂 | 1 文件 | `CRASH_P{page_id}_scenario_failed_{scenario}` | `CRASH` |
| Step 4.0 导航不到 | 1 文件 | `CRASH_P{page_id}_nav_unreachable_{from}_{to}` | `CRASH` |

> ID 派生与 slug 兜底（`idx<NN>`、kebab-case 约束、长度 3–30、冲突追加 `-2/-3`）严格按 schema §二。

### 2.4-b frontmatter 必填字段

每个 markdown 顶部 yaml frontmatter，本 skill 写：

```yaml
---
id: <文件名去 .md>
title: <按 schema §二 title 派生规则，≤60 字>
source: visual-verify
layer: ui
kind: ALIGNMENT_DIFF | URL_MISMATCH | CRASH    # 严格按 2.4-a
severity: P0 | P1 | P2                          # 按 schema §四 severity 映射规则从 multimodal_severity 转换
fixer_layer: ui                                 # CRASH(scenario_failed) 时可能为 feat，详见 schema §六
suggested_files:
  - <ets 路径，多模态能定位则填，不能则填 "unknown">
related: []
systemic_root: null                             # Phase 6 做 systemic 聚合时回填
affects: []                                     # 仅 SYSTEMIC_*.md 才填
evidence:
  - <sbs 截图路径 / harmony 截图 json / hilog 段路径 / scenario result.json>

# visual-verify 专属 5 字段
page_id: P0010
capture_mode: single | long | web | single_fallback
similarity: 0.85                                # CRASH/URL_MISMATCH 允许 null
multimodal_severity: high | medium | low
is_migration_bug: true | false                  # 多模态原值

# carry forward（schema §五）
disposition: <从 round-(N-1) carry forward；新条目为 null>
disposition_reason: <同上>
disposition_set_at_round: <同上，整数绝对轮次号>
---
```

**carry forward 算法**（写每个文件之前必跑）：

```pseudocode
prev_path = "spec/fix/round-{N-1}/ui/{id}.md"
if exists(prev_path):
    prev_fm = parse_frontmatter(prev_path)
    if prev_fm.disposition is not null:
        new_fm.disposition              = prev_fm.disposition
        new_fm.disposition_reason       = prev_fm.disposition_reason
        new_fm.disposition_set_at_round = prev_fm.disposition_set_at_round
```

### 2.4-c 正文 5 个 Section（标题、顺序严格一致）

```markdown
# {title}

## 1. Spec 引用
来源: <按 schema §六 visual-verify 各 kind 的来源行规则>

## 2. 期望
<iOS 源端的视觉/url/期望加载状态，自由文本>

## 3. 实际
<HMOS 端实测；ALIGNMENT_DIFF 直接贴多模态 description + root_cause_hint 原文；
 URL_MISMATCH 贴 hmos_url + diff 字段名；
 CRASH 贴 hilog 异常首行 + 崩溃时机>

## 4. 源码缺口
- <ets 路径>:<行号> — <一句话描述>
- ...

（行号未知写 `unknown`；多模态完全未定位允许写一行 `unknown — 多模态未定位，由 fixer 自行 grep 定位`）

## 5. 修复建议
1. <动词开头的步骤，写到方法名 / 资源 key / 组件类型粒度>
2. ...
```

**写法约束（不可违反）**：
- Section 1–5 标题完全一致（`## 1. Spec 引用` 等），不许改字
- 每个 section 都必填，不许整段省略
- Section 4 至少 1 行
- Section 5 至少 1 步
- ALIGNMENT_DIFF 的 Section 3 **必须**贴多模态 `description` + `root_cause_hint` 原文，**不允许**本 skill 自己改写——这是 fixer 复核根因的依据

### 2.4-d 写盘策略（防止半成品）

每条差异处理流程：
```
1. 派生 id（按 §二 规则；冲突追加 -2/-3）
2. 检查 prev round 同 id 文件 → carry forward disposition
3. 写完整 frontmatter + 5 个 section 到 spec/fix/round-N/ui/{id}.md
4. 写完后立即追加到 progress.json.pages[X].fix_files[]，便于 Phase 6 汇总
```

**禁止行为**：
- ❌ 把多条差异合并到一个文件（schema 要求一差异一文件，便于 fixer 派单）
- ❌ 跳过 Section（"这个差异不需要建议" → 错，至少写一句"由 fixer 排查"）
- ❌ 在文件里写"已尝试修复路径" / "fixer 历史调用"——schema 明确禁止历史段（跨轮历史靠 round 目录序列承载）
- ❌ 直接 Edit/Write 任何 `.ets` 文件
- ❌ 自己在主上下文里凭经验改代码

---

## Step 4.5: 单页结束、写 progress.json、进入下一页

**单 round 内**不做"重截图收敛循环"——每页只跑一次（capture → multimodal → 写 markdown）。
"是否收敛"是**跨 round** 的判断，由 Phase 6.5 的 `round_budget.py next` 按退出码机械裁定
（0=继续 / 11=CONVERGED / 10=本次预算用尽），不在本 Phase、也不再交 a2h-verify。

```
本页结束动作：
  1. 累计本页 fix_files 数量 + status 写 progress.json.pages[X]：
       status: "pass"      = 多模态返回 0 条 high 且无 CRASH/URL_MISMATCH（本轮该页无 markdown 产出）
               "partial"   = 有 medium/low diff 但无 high（本轮有 markdown，severity 不到 P0）
               "fail"      = 有 high diff 或 URL_MISMATCH（本轮有 P0 markdown）
               "blocked"   = CRASH 各类（app_crash / scenario_failed / scenario_required_* / nav_unreachable）
                             —— 所有无法实际截图的页面都视为 blocked，
                                写对应 CRASH markdown 记录缺口，确保 "测过/有产出" 这条铁律
       rounds += 1（这是该页跨全局轮的累计计数，供调用方与 _summary.md 消费）
  2. 立即落盘 progress.json（断点续跑）
  3. 移到下一页
```

> **标 `noop` / `pending_upstream_fix` 前必跑 wiring-gap 判据（硬约束）**：
> 页面判 blocked 且根因形如「XX 未配置 / 未就绪 / 暂不可用 / 等后端 / provider 不可用」时，
> **必须先跑 [`wiring-gap-detection.md`](wiring-gap-detection.md) §2 三步判据**数一遍装配入口调用点：
> 调用点 = 0 → 这是**实现缺口**（`kind=IMPL_MISSING` / `severity=P0` / `is_migration_bug=true` /
> `suggested_fix_owner=fixer`），**不得**标 `noop`；调用点存在但运行期条件不满足才是真上游阻塞，
> 且 `not_migration_evidence` 必须写明调用点行号。没跑判据就标 noop = 假阴性事故。

> **不存在 status="skip"**——所有页面要么进入 Step 4.1 实际截图（→ pass / partial / fail），要么因 CRASH 无法截图（→ blocked + 一份 CRASH markdown）。**不存在"队列里有这页但没产出"的状态**。

**SKILL.md §1.1.1 防绕规则（仍然适用 Step 4.3 分类阶段）**：
- ❌ 禁止自动给差异打 `category="design_difference"` / `dynamic_content`，除非 §1.1.1 三条证据满足
- ❌ 禁止把 `severity` 从 high 自动降为 medium/low（severity 只能透传多模态返回）
- ✅ 用户在对话里明确豁免 → 在该差异的 markdown frontmatter 里把 `disposition` 设为 `manual_review`、`disposition_reason` 引用户原话、`disposition_set_at_round` 填 N

> **关于"反退化 / 修复路径质上不同"**：原本是本 skill 对 in-loop fixer 的把关，现在改成由 visual-fixer 自己跨轮维护（fixer 在 `docs/autofix-log/round-N/` 写它的尝试历史）。本 skill 不再承担此职责。

**每页结束时立即写入 `progress.json`**（无论 pass/partial/fail/blocked）：

```json
"MineSettingPage": {
  "status": "pass",
  "reachability": "public",
  "last_updated": "2026-05-11T07:00:00Z",
  "capture_mode": "single",
  "similarity": 0.91,
  "rounds": 2,                                    // 该页跨全局轮的累计计数（全局轮次由本 skill 自持）
  "high": 0, "medium": 1, "low": 2,
  "fix_files": [                                  // 本轮 Step 4.4 写出的 markdown 相对路径
    "spec/fix/round-2/ui/ALIGN_P0010_spacing_drift_titlebar-padding.md"
  ],
  "navigation_path": "Home → Mine tab → Settings icon",
  "scenario_chain": "login,upload_image"          // 本页用过的 scenario 链（记录用）
}
```

`status` 取值（本 skill 自身判定，业务"是否对齐"的再解释由调用方——用户或 a2h-verify——看 markdown + VERDICT 决定）：

| 值 | 含义 |
|----|------|
| `pass` | 多模态返回 0 条 high 且无 CRASH/URL_MISMATCH（本轮该页无 markdown 产出） |
| `partial` | 有 medium/low 差异但无 high（本轮有 markdown，severity 不到 P0） |
| `fail` | 有 high diff 或 URL_MISMATCH（本轮有 P0 markdown） |
| `blocked` | CRASH（app_crash / scenario_failed / nav_unreachable）→ 写 CRASH_*.md |
