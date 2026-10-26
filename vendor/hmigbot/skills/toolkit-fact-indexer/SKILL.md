---
name: toolkit-fact-indexer
description: 纯确定性地把 harmony-migration-toolkit 产物加工成一份扁平的「Android 端事实树」`spec/toolkit-fact-tree.json`。tree 含 pages / fragments / dialogs / components 的列表 + 组件父子关系 + 页面间流转 + 行为锚点。**业务 purpose / description 不在本 skill 范围内**——由下游 `app-relationship-tree` 跑 LLM 读源码补。本 skill 零 LLM、~20s 跑完。`a2h-spec` 直接消费此 tree（用 navigation + components 结构事实），`app-relationship-tree` 作为主输入再补语义。当用户说"用 toolkit 产物生成事实索引"、"基于 harmony-migration-toolkit 产关系索引"、"fact-index"、"toolkit-fact-tree"、"toolkit 转关系树"时触发。
metadata:
  tags:
  - analysis
  - fact-tree
  - toolkit
  - deterministic
  references:
  - references/fact-tree-schema.md
---

> **Codex subagent dispatch convention.** This skill dispatches subagents. In Codex, spawn them with the `spawn_agent` tool and pass `agent_type` = the role name **exactly as written in this skill** — the roles registered under `.codex/agents/*.toml` use the same hyphenated names, so no translation step is involved: `a2h-activity-converter`, `a2h-android-analyzer`, `a2h-closer`, `a2h-fixer`, `a2h-migration-worker`, `ad-profile-builder`, `compose-fact-analyzer`, `hmos-builder`, `scenario-builder`, `visual-fixer`, `visual-fixer-reviewer`. The built-in `general-purpose` agent_type is unchanged. (Claude's `subagent_type` field is written `agent_type` for Codex; `Agent(...)` dispatch calls are `spawn_agent(...)`; there is no `Task` tool in Codex.)
>
> **Join 协议（收口五条款）。** Codex 子代理完成后**不会**唤醒主会话——结果必须由派发方主动收口，违者=静默卡死（实测事故）。
> ① **循环 wait**：每个 `spawn_agent` 句柄用循环调用 `wait_agent` 收口；单次超时只代表"还在跑"，继续再调；**禁止以"等待子代理"为由结束回合**。醒后必调 `list_agents` 确认是谁完成——**完成的唯一合法信号 = `agent_status` 为 `{"completed": …}`，绝不是产物文件的存在/条数**（文件会中途落盘，读半截=实测事故）；completed 态会在数轮后从 list 中消失，所以每次醒来都要及时查。正文所有"等待完成 / join / 到点即收"表述一律指此循环。
> ② **死句柄与验收**：连续 3 次超时后调 `list_agents` 核对，可配 `wait_for_artifact.py` 探产物活性；已 completed 且 summary 可读 → 直接消费；句柄消失且从未观测到 completed → 按断点重派（带原 prompt + 已落盘产物，上限 2 次），禁止继续等待。**completed ≠ 验收通过**：join 点跑 `python3 .agents/skills/a2h-join/scripts/join_gate.py --project .` 验产物完整性，FAIL 视同未取回、按本条重派。
> ③ **收口锚点**：本 skill 最终完成报告前必须收口全部句柄（join_gate exit 0）；正文写明的显式 join 点优先按正文执行。发用户门（Gate）时允许句柄跨 Gate 存活，但 Gate 摘要必须列明未收口句柄清单 + 各自的指定 join 点。
> ④ **放行 ≠ 遗弃**：正文"非阻塞放行/到点即收/降级继续"只推迟收口时机，不豁免收口义务。
> ⑤ **fire-and-forget**：仅正文显式声明"结果丢弃/不 gate"的派发（如 a2h-execute 的 env-prewarm）免收口；审计只认 join_gate 内静态 allowlist，正文声明只是文档层。
> **派发纪律**：`task_name` 必须唯一（带 page-id/slice-id/round-N 后缀）；并行派发前把预期产物清单写 `spec/a2h/_work/expected_<join点>.json`（join_gate 对账用，契约只认派发方、不认子代理自报）；**谁派谁收**——sub-agent 内部需要"等齐 N 片再合并"时禁止嵌套外派后自行退出，要么同步自做、要么把分片清单回报主会话代派（sub-agent 一停止，收口能力即丢）。**契约产物必须出自承担任务的子代理**：重派上限后仍产不出 → 如实报缺并停在未完成态；禁止派发方代写占位产物让 gate 转绿（声明过也不行——绿账必须对应真产物）。

> **路径约定**：下文 `$SKILLS_ROOT` = 本套 skills 的安装根目录。执行任何脚本前先设一次：`SKILLS_ROOT="$(cd "$(dirname 本SKILL.md)/.." && pwd)"`（用户级安装=`~/.agents/skills`；项目级=`<project>/.agents/skills` 或 `<project>/skills`）。

# toolkit-fact-indexer — toolkit-fact-tree 生成器（纯确定性）

> **⚠️ 状态：Phase 1 修补（v1.3 — 2026-06）+ vendored toolkit 升级（2026-07-13）**
>
> **2026-07-13**：vendored `scripts/harmony-migration-toolkit/` 整体替换为 behaviour-modified 最新版，
> 核心新增**字符串路由解析 pass**（`bundled_spec_tools/extractors/router_table_extractor.py` +
> `docs/ROUTER_PASS_DESIGN.md`）：@Route/@RouterUri 注解建路由表 + 常量拼接求值 + TheRouter/ARouter
> build 调用点连边 + wrapper 名称启发式。Fitness 实测：nav 边 50→141（activity 型 12→102，89 条
> router:therouter，抽查与设备账本一致）、draft 原生真链(reach≥3) 16%→30%、isolated 128→105。
> 已知残留：launcher 检测对 Fitness 仍返回 None；tab/host_default fragment 边仍弱（unreached 集中在
> tab 内容 fragment）——由下游 ART/device_verified 边兜底。旧版及 v1 备份已删除不留档。
>
> 当前版本针对 popup/dialog 漏识问题做了最小化修补：
> 1. **修上游 launcher 检测 bug**：`harmony-migration-toolkit/stages/_util.py:parse_manifest_launcher` 与 `bundled_spec_tools/extractors/android_project.py:launcher_activity_class` 用 `xml.etree.ElementTree` 替代 regex，正确识别 `<activity-alias>` + `targetActivity` 注册的 launcher（旧版在多图标 alias 项目里会错挂到第一个 `<activity>` tag）
> 2. **放宽归类规则**：`discover_fragments_from_specs` 现在也会 promote `dialog_*/popup_*/pop_*/_xpopup_*/bottom_sheet_*` 命名的 spec 文件；当 `screen_type=unknown` 但 layout 名是 popup 形态时，自动升格成 `screen_kind=dialog` 归入 `dialogs[]`
> 3. **records 增加 `source` 字段**：可取 `toolkit_screen` / `spec_promoted` / `spec_promoted_popup_layout`，便于下游区分"真 Dialog 子类"与"只有 layout 的浮层"
>
> **预期效果（jq50w 实测）**：`fact-tree.dialogs` 从 46 涨到 ~120，与项目真实 118 个业务弹窗对齐；launcher 从空字符串变为 `SplashActivity`。
>
> **长期路径（Phase 2 待立项）**：harmony-migration-toolkit 是自家项目，fact-indexer 这层适配的存在意义已削弱。后续可能淘汰本 skill，让 toolkit 直接产对外稳定契约。本次修补**明确标记为技术债**，不要在此基础上继续加重型翻译逻辑。

## 1. 定位（v1.1 重定位 — 2026-05）

本 skill 是 [harmony-migration-toolkit](https://github.com/Junkang123456/harmony-migration-toolkit) 的**结构化适配器**——把 12 个 toolkit JSON 加工成一份扁平的 Android 端事实树 `spec/toolkit-fact-tree.json`。

**关键边界（v1.1 收紧）**：

| 责任 | 本 skill | app-relationship-tree | 备注 |
|---|---|---|---|
| 结构性事实抽取（pages / fragments / dialogs / components / nav / parent_id / flow_graph） | ✅ 必做 | — | toolkit 产物的扁平化 |
| Fragment 兜底（toolkit 漏识的 13 个 Fragment）| ✅ 必做 | — | grep `<android_root>` 补 class |
| 6 enhancer（source_findings / static_xml fallback / gap_items / nav_candidates / impl 节点 / dynamic_gap）| ✅ 必做 | — | toolkit 产物再加工 |
| 自检结构性事实（id 唯一、parent_id 闭合、flow_graph 一致、stats 一致）| ✅ 严格自检 | — | 不通过即 skill fail |
| **LLM 补 description / purpose** | **❌ 不做** | ✅ 主责 | tree skill 一次性读源码 + spec 补 |
| 读 page_spec / android-source / graph-builder 多源 supplements | ❌ 不做 | ✅ 主责 | tree skill 的 Phase 4.5 |

**输出 tree 的 description / purpose 字段全部为 null** —— 这是设计选择，不是缺陷。下游 `app-relationship-tree` 会一次性 LLM 读源码同时补 description + supplements，**避免读两遍源码**。

```
toolkit bundle
    │
    ├─ agent_bundle.v1.json
    ├─ intermediate/0_android_facts/navigation_graph.json     (干净 nav 边)
    ├─ intermediate/0_android_facts/specs/*.json              (每屏 ui_elements)
    ├─ intermediate/0_android_facts/ui_paths.json             (修复后 156 条 path)
    ├─ intermediate/0_android_facts/source_findings.json      (event_reg / id_dispatcher / visibility_ctrl)
    ├─ intermediate/0_android_facts/static_xml.json           (XML fallback 元素清单)
    ├─ intermediate/0_android_facts/navigation_candidates.json(未解析 startActivity hint)
    ├─ intermediate/0_android_facts/ground_truth.json         (dynamic_gap)
    ├─ intermediate/1_android_facts/android_facts.v1.json     (app + manifest)
    ├─ intermediate/2_framework_map/framework_map.v1.json     (gap_items)
    ├─ intermediate/3_harmony_arch/harmony_arch.v1.json       (Harmony route placeholder)
    └─ intermediate/5_feature_tree/feature_tree.v1.json       (screens + feature + implementation 节点)
                  │
                  ▼
       ┌─────────────────────────┐
       │  toolkit-fact-indexer   │
       │  Phase 1: 脚本读 12 src │  → spec/.cache/fact-tree/draft.json
       │  Phase 2: 自检 + 落盘   │  → spec/toolkit-fact-tree.json
       └─────────────────────────┘
                  (~20s, 零 LLM)
```

---

## 2. 输出 tree 包含什么

| 维度 | tree 中的体现 |
|---|---|
| **所有 pages / fragments / dialogs** | 顶层 `pages[]` + `fragments[]` + `dialogs[]`，含 Fragment 兜底（toolkit 漏识的） |
| **组件清单（每个 page 内）** | `pages[i].components[]` flat list，每条含 type / text / hint / parent_id / behaviors / triggers / source_anchor |
| **组件触发形式** | `components[i].triggers[]` 聚合（如 `["click","long_press"]`，来自 behaviors 的 event/method）+ `components[i].navigation.trigger` 跳转触发 |
| **组件详细属性** | `components[i].text` / `.hint`（EditText placeholder）/ `.image_resource` / `.content_desc` / `.on_click_attr`（XML 静态 onClick）/ `.visibility` / `.visible_when`（动态可见条件）/ `.is_interactive` |
| **组件父子关系** | `components[i].parent_id` 指向同 page 内的父组件 id；null 表示页面根 |
| **页面父子关系** | `pages[i].contains[]`（嵌的 Fragment）+ `pages[i].shows_dialogs[]`（触发的 Dialog） |
| **流转逻辑（页面间）** | `pages[i].navigation.{inbound,outbound}[]` + 顶层聚合 `flow_graph.{nodes,edges}` |
| **流转逻辑（组件→页面）** | `components[i].navigation.{to_page, trigger, params, is_dynamic}` |
| **reach_paths（从入口到达本页的链路）** | `pages[i].reach_paths[]`——**直接引用 toolkit `ui_paths.json` + `ui_paths_enumerated.json`**，不自己 BFS |
| **未解析跳转 hint** | `pages[i].navigation.unresolved_hints[]`（toolkit 解不出的 startActivity 候选） |
| **行为锚点（toolkit 已挖好的 file:line）** | `components[i].behaviors[]` + `_record_behaviors[]`（lifecycle 级） |
| **不确定标记** | `uncertain: true`（Fragment 兜底失败 / gap_items / dynamic_gap） |
| **人工备注**（toolkit 解不出 / 易踩坑的 trigger 等） | `pages[i].notes` + `components[i].notes` —— **fact-indexer 不写**，留 null 占位给用户/下游 LLM 填 |
| **业务 description / purpose** | ⏭️ **全 null**（由 tree skill 补） |

---

## 3. 前置条件

### 3.1 硬性环境依赖

| 条件 | 验证命令 | 失败提示 |
|------|---------|---------|
| Python 3.10+ | `python3 --version` | "请安装 Python 3.10+" |
| jq 可用（自检脚本依赖） | `which jq` | "请安装 jq（macOS: `brew install jq`）" |

### 3.2 toolkit 产物探测（缺失则自动跑 pipeline）

**探测顺序**（v1.2 起 toolkit 已 vendored 进 `scripts/harmony-migration-toolkit/`，缺失即可自动调起）：
1. 用户显式传入 `{toolkit_out}` → 直接用
2. 默认路径 `{project_root}/intermediate/` + `agent_bundle.v1.json` 都在 → 直接用
3. 缺 → **自动调** `scripts/run_full_pipeline.sh`，串起 Stage A (toolkit pipeline) + Stage B (fact-tree 生成)，把产物落到 `{project_root}/`：

```bash
bash $SKILLS_ROOT/toolkit-fact-indexer/scripts/run_full_pipeline.sh \
    --android-root <ANDROID_ROOT> \
    --toolkit-out  {project_root} \
    --project-root {project_root}
```

helper 自动：
- 装 toolkit Python 依赖（jsonschema / PyYAML / pytest，幂等，已装跳过；PEP 668 环境退到 `--user`）
- 跑 `harmony-migration-toolkit/pipeline.py --android-root --out` 产 intermediate/ + agent_bundle
- 跑 `toolkit_to_fact_tree_draft.py` 产 spec/.cache/fact-tree/{draft,source-index}.json
- 复制 draft.json → spec/toolkit-fact-tree.json
- 通过 `--force-toolkit` 可强制重跑 Stage A（如 toolkit 产物想刷新）

### 3.3 退出契约

| 退出状态 | 含义 | 调用方应对 |
|---|---|---|
| `success` | `spec/toolkit-fact-tree.json` 已生成且通过结构性自检（7 项） | **必须紧接着调 `$app-relationship-tree`**（见下方铁律） |
| `skipped` | 用户选 C / toolkit 产物不可得 | tree skill 走降级路径，**不打 ⚠️** |
| `error` | 环境依赖缺失 / toolkit 产物损坏 / 脚本崩溃 / 自检结构性项失败 | 报错 |

#### 3.3.1 退出后铁律（双保险固化链路，**违反算事故**）

**本 skill 跑成功（`success`）后，主代理必须紧接着调 `$app-relationship-tree`，无任何例外**。

理由：
- 本 skill 只产**结构事实层**（pages / fragments / dialogs / nav 边），所有 `purpose=null` / `reach_paths=[]` / `inbound_triggers=[]` / `navigation_contract=null` 是预期空白
- 这些空白由 app-relationship-tree 的 5 个 phase 补全
- 缺了语义补全，下游 visual-verify / a2h-spec 拿到的是**半成品 tree**——典型现象：visual-verify 深层页全够不着、只能截 launcher 周边
- 即使调用方（如 visual-verify）已经在它自己的 Step 1.0 写死了"toolkit-fact-indexer → app-relationship-tree"链路，**本 skill 也必须自己重申这条铁律**，形成双保险：上游已声明 + 下游已强制，双方都跳过的概率才足够低

**唯一豁免**：调用方在 prompt 中显式声明 `"只补结构事实，跳过语义补全"`（如 toolkit 端调试 / 修脚本验证）——这种主代理可以不接续调 app-relationship-tree，但必须在响应里**显式说明跳过的理由**。

**禁止行为**：
- ❌ 主代理跑完本 skill 后输出"完成"然后停下不调 app-relationship-tree（最常见的跳过模式）
- ❌ 主代理合理化"上次跑过 app-relationship-tree 应该没问题"（必须按 fact-tree 当前内容判断，不是按记忆）
- ❌ 用 subprocess 调 `app-relationship-tree/scripts/*.py` 绕过 `Skill()` 工具——会丢 app-relationship-tree 自己的 5 phase 编排 + LLM sub-agent 派发

**正确收尾示例**：

```
[本 skill 跑完，输出结构事实层 fact-tree]
=== toolkit-fact-tree.json 生成完成（结构事实层）===
pages=38 fragments=11 dialogs=66 ...

⏭️  按退出契约 §3.3.1 铁律，紧接着调起 app-relationship-tree 补语义层：

[主代理立即调用 $app-relationship-tree，无需等用户确认]
```

### 3.4 Stage A 产物质量门（max 5 iteration，自愈循环）

`run_full_pipeline.sh` 的 Stage A（toolkit pipeline）历史上有**确定性失败模式**——例如相对路径在 subprocess cwd 变化后失效，导致 `launcher_class=""` → Step 6 短路 → `ui_paths.json / ui_dag.json / ui_paths_coverage_report.json` 等 5 个文件写空，但 pipeline 退出码 0 静默通过。下游 visual-verify / app-relationship-tree 拿到这些空产物时才发现深层页全够不着。

**质量门强制要求**：Stage A 跑完后（或检测到已有 intermediate/ 时也要跑一次），进 Phase 1 之前必须通过质量门。

**循环结构（主代理执行，不接管用户）**：

```
for iter in 1..5:
    # 检查阶段（sub-agent，只读）
    spawn sub-agent (通用子代理):
        prompt = references/stage-a-quality-checklist.md 的全文 + 当前 project_root
        要求返回结构化 JSON 报告（schema 见 checklist 文档）

    if report.verdict == "PASS":
        break  # 进 Phase 1

    # 修复阶段（主代理，不交人）
    主代理读 report.failed_files + report.root_cause_hint
    主代理自行：
        - 读相关源码（AndroidManifest.xml / build.gradle / pipeline.py / main.py / 涉及 extractor）
        - 判定根因（路径错 / 字段为空 / 模块短路 / 异常被吞 ...）
        - 应用定向修复（patch 配置 / patch toolkit 脚本 / 手工重跑特定 step / 改 invoking shell ...）
        - **禁止**简单的 `重跑整个 run_full_pipeline.sh` 当修复——若根因没变，下次还塌
        - **禁止**写空文件 / 占位文件来"满足"检查

    continue  # 下一轮 sub-agent 复检

# 5 轮全 FAIL
else:
    将 sub-agent 最后一轮报告写入 spec/toolkit-stage-a-quality-issues.md
    主代理在 SKILL 主流程的 stdout 打 ⚠️ 横幅
    **继续往下走 Phase 1（skip，不阻塞）** —— 但 a2h-spec / visual-verify 等下游 skill
    读到该文件存在时必须主动降级提示用户"toolkit 产物部分残缺"。
```

**红线**：
- 5 轮硬上限，不允许扩到 6
- sub-agent 全程只读，不允许跑修复 / 重跑命令
- 主代理修复阶段不允许交互式问用户；它就是 fix 不动也要在 5 轮内自己产 5 个尝试结论
- 5 轮全 FAIL 不阻塞主流程；产物残缺的代价由下游 skill 承担

**已知失败模式速查**（主代理首轮可直接对照）：

| 症状 | 根因 | 修复 |
|---|---|---|
| `ui_paths.json = []` + `ui_dag.json` screen_class="" | main.py 拿到的 `android_root` 是无效相对路径（pushd 后 cwd 变了） | 改 `run_full_pipeline.sh` pushd 前先 `ANDROID_ROOT="$(cd "$ANDROID_ROOT" && pwd)"`；或不打 patch 而直接用绝对路径手工重跑 main.py Step 6 |
| `manifest.package=None` + AGP 7+ 项目 | toolkit `read_gradle_app_config` 不识别 `namespace packageName`（变量引用）| 在 manifest.json 手工写回 package；或加 patch 让 regex 支持变量解析 |
| `launcher_activity_qualified` 错挂到第一个自闭合 activity | `parse_manifest_launcher` regex 跨 activity 边界 | 用 ET.parse 重写 launcher 检测；或 manifest.json 手工改 |
| 大量自循环边（`from==to`）占活动边 70%+ | toolkit 静态分析解不出 `openActivity(X::class.java)` helper 参数 | 不在 toolkit 修复范围，记录到 quality-issues.md 让下游 app-relationship-tree 兜底 |

---

## 4. 输入 / 输出

| 输入 | 路径 | 必选 |
|------|------|------|
| toolkit 输出目录 | `{toolkit_out}/`（含 `agent_bundle.v1.json` + `intermediate/...`） | ✅ |
| Android 源码根 | `{android_root}/`（Fragment grep + layout XML 解析）| 🟡 脚本会从 toolkit `source.android_root` 反查 |

| 输出 | 谁产 | 用途 |
|------|------|------|
| `spec/.cache/fact-tree/draft.json` | 脚本（Phase 1） | 完整结构骨架，`purpose` 全 `null` |
| `spec/.cache/fact-tree/source-index.json` | 脚本（Phase 1） | 每个 component 的源锚点（file + line），给 tree skill LLM 增量读用 |
| **`spec/toolkit-fact-tree.json`** | 脚本（Phase 2） | **最终对外产物**（与 draft.json 内容相同；分两个文件方便断点） |

完整字段定义见 [`references/fact-tree-schema.md`](references/fact-tree-schema.md)。

---

## 5. 执行流程（2 个 phase + 1 个质量门）

> **顺序**：3.2 跑 toolkit → 3.4 质量门（5 轮自愈）→ Phase 1 产骨架 → Phase 2 落盘。质量门即使全 FAIL 也不阻塞 Phase 1，但会让下游 skill 提示降级。


### Phase 1: 脚本产骨架（~20s）

```bash
python3 $SKILLS_ROOT/toolkit-fact-indexer/scripts/toolkit_to_fact_tree_draft.py \
  --toolkit-out  {toolkit_out} \
  --android-root {android_root} \
  --out          spec/.cache/fact-tree
```

脚本干 6 件事：

1. **读 toolkit**：bundle / android_facts / feature_tree / navigation_graph / ui_paths / specs/
2. **Fragment 兜底**：扫 `specs/fragment_*.json` + `page_*.json` + `widget_*.json` 中 feature_tree 没有的；grep `<android_root>` 找 class
3. **per-page 组件清单**：从 `specs/*.json` 的 `ui_elements[]` 提 flat list；layout XML 在磁盘则解析得 `parent_id`
4. **navigation 双向**：从 `navigation_graph.json` 建 `pages[i].navigation.{inbound,outbound}` + `components[i].navigation`
5. **顶层 flow_graph + features**：聚合所有 nav 边；从 `feature_tree.nodes[kind=feature]` 取 17 个聚类
6. **6 enhancer**：source_findings / static_xml fallback / gap_items / nav_candidates / impl 节点 / dynamic_gap

输出 `draft.json` + `source-index.json`，所有 `purpose` / `description` 字段为 `null`（**这是预期的**）。

主代理在 Phase 1 不做任何业务判断，只检查脚本退出码 + stdout 摘要。失败直接终止。

### Phase 2: 自检 + 落盘最终产物

1. `cp spec/.cache/fact-tree/draft.json spec/toolkit-fact-tree.json`
2. 跑 `references/fact-tree-schema.md` §十一 的**结构性自检脚本（7 项）**：
   - schema_version=1
   - 顶层 8 字段齐
   - id 唯一（pages + fragments + dialogs）
   - navigation.to_page 可达（或 `is_dynamic: true`）
   - parent_id 闭合（指向同 page 内存在的 id 或 null）
   - flow_graph.edges 数 == 所有 outbound 之和
   - stats 与实际数量一致
3. 任一 ❌ → 修复后重跑；连续 3 次失败 → 升级用户报错
4. 输出摘要：

```
=== toolkit-fact-tree.json 生成完成（结构事实层）===
来源: harmony-migration-toolkit ({toolkit_out})
pages={N} fragments={M} dialogs={K} components={C} nav_edges={E} features={F}
parent_id 设了: {P}/{C}   fragments_promoted: {Fp}   uncertain: {U}
behaviors 锚点: {B}（含 enhancer 补的 source_findings 锚点）
unresolved nav hints: {NH}

⏭️  按 §3.3.1 退出契约铁律，主代理必须立即调起 $app-relationship-tree
    补语义层（purpose / reach_path / inbound_triggers / navigation_contract /
    preconditions / dependency_graph），不允许停在这里。
```

5. **接续 app-relationship-tree（§3.3.1 铁律）**：Phase 2 完成 ≠ 任务完成。主代理输出上述摘要后，**必须**在同一响应内继续 `$app-relationship-tree` 调用——不要等用户确认、不要询问"是否继续"、不要写成"建议下一步"。本 skill 只产半成品，语义层缺失会让下游 visual-verify 深层页全够不着。详见 [§3.3.1 退出后铁律](#331-退出后铁律双保险固化链路违反算事故)。

> **去掉的 Phase**：旧版有"Phase 2 LLM 补 purpose"。v1.1 起删除——LLM 工作全部移到 app-relationship-tree 一处做。

---

## 6. 与下游 skill 的协议

### 6.1 给 a2h-spec 用（Phase 0.5）

a2h-spec 检测 `spec/toolkit-fact-tree.json` 是否存在。如有：

- `## navigation` 段 → 直接抄 `pages[*].navigation.inbound/outbound`（结构事实，无需 LLM）
- `## conversion decisions` 表 → 用 `components[*]` 的 `type` + `text` + `id` + `behaviors` 生成 ArkTS 组件映射初稿（type 是事实，description 是 null，a2h-spec 自己 LLM 写自己的 spec 描述）
- `## page structure` 描述 → 用 `contains` + `shows_dialogs` + `components[]` 的 parent_id 关系串自然语言
- 节省重复扫 Android 源码的时间，特别是动态导航（`is_dynamic: true` + `unresolved_hints`）

**a2h-spec 不期望 fact-tree 含 description**——它自己生成 spec 描述。

### 6.2 给 app-relationship-tree 用（Phase 4D + 4.5）

**Phase 4D 字段映射全部兼容**（schema_version=1 不变，结构 1:1）：
- `fact.pages[i].id` → `tree.pages[i].name`
- `fact.pages[i].purpose` → `tree.pages[i].description`（这时是 null，由 tree skill 的 Phase 4.5.B LLM 补）
- `fact.pages[i].components[]` ← flat list，每条含 `id / type / parent_id / behaviors / navigation`
- `fact.flow_graph` ← 顶层保留供 4D Step 4D.4 找强连通子图聚类

**Phase 4.5.B (新 — tree skill 的活)**：
对每个 description=null 的 record / sub_component，tree skill 用 `source-index.json` 拿锚点读源码片段，LLM 推断中文 description，同时一次性扩展可能漏识的 sub_components。

---

## 7. 自检与质量门控（严格不放宽）

退出前必须确认（结构事实层 8 项）：

| 项 | 验证方式 | 严重度 |
|---|---|---|
| JSON 合法 | `jq empty < spec/toolkit-fact-tree.json` | HARD |
| schema_version == 1 | schema §11.1 | HARD |
| 顶层 8 字段齐（source / app / features / pages / fragments / dialogs / flow_graph / stats）| schema §11.2 | HARD |
| pages/fragments/dialogs id 唯一 | schema §11.3 | HARD |
| 所有 navigation.to_page 可达（或 is_dynamic=true）| schema §11.4 | HARD |
| 所有 component.parent_id 闭合 | schema §11.5 | HARD |
| `flow_graph.edges` 与所有 outbound 总数一致 | schema §11.6 | HARD |
| `stats` 字段与实际数量一致 | schema §11.7 | HARD |
| 所有 record.reach_paths 是 list（可为空数组 `[]`，但不可 null）| schema §11.8 | HARD |

> **不再检查的项**（已移交 app-relationship-tree）：
> - ~~所有 component.purpose 不能 null~~ → tree skill 的 Phase 4.5.B 自检管
> - ~~所有 page/fragment/dialog purpose 不能 null~~ → 同上

任一 HARD 项不通过 → fact-indexer 失败，向用户报错。**结构性事实不允许残缺。**

---

## 8. 使用示例

```
用户: 帮我把 toolkit 的产物加工成 fact-tree
用户: 基于 harmony-migration-toolkit 生成事实索引
用户: 用 toolkit 跑一份 toolkit-fact-tree 出来
用户: 我已经跑过 toolkit 了，能不能加工成结构化的页面索引
用户: 给我个初版 tree（事实层）
```

---

## 9. 局限性

| 局限 | 说明 |
|------|------|
| 依赖 toolkit 精度 | toolkit 漏识别的动态 navigation / 反射调用 → tree 同样漏。`uncertain: true` 标记会传染 |
| **description 全 null 是预期**（v1.1） | 业务 purpose 由下游 app-relationship-tree 补；本 skill 不读源码做 LLM |
| `parent_id` 仅当 layout XML 在磁盘时给出 | Compose / 程序化 View 对应页面 `parent_id` 为 null |
| `items[]` 字段 | RecyclerView / Adapter 子项需扫源码 adapter；当前为 null 占位 |
| Android 端事实，不含 ArkTS | tree 是 Android 视角；HMOS 端 rename / 重命名是 app-relationship-tree 的 supplement 阶段 |
| AlertDialog.Builder / PopupWindow / BottomSheet / Toast | toolkit 不识别，tree 也不补 |
| Compose 页面 | toolkit `ui_fidelity: high_xml`，Compose 不在 |

---

## 10. 历史变更

| 版本 | 时间 | 主要变化 |
|---|---|---|
| **v1.1**（current） | 2026-05 | **删除 Phase 2 LLM 补 purpose**；自检从 9 项缩为结构性 7 项；LLM 补 description 移交 app-relationship-tree 一次性做 |
| ~~v1.0~~ | 2026-05 短暂 | 产物正名为 `toolkit-fact-tree.json`；schema 1:1 兼容 app-relationship-tree 4D；含 LLM Phase 2 |
| ~~v3 fact-index~~ | 2026-05 短暂 | 误把 components 改为递归 component_tree、删了 flow_graph，3 处契约不符 |
| ~~v2 fact-index~~ | 2026-05 短暂 | 引入 reach_path 二次 BFS，与 toolkit ui_paths.json 重复 |
| ~~v1 fact-index~~ | 2026-04 | 最初版本 |

---

## 11. 完整链路

```
用户: "用 toolkit 产物生成事实树"
  │
  ▼
toolkit-fact-indexer（纯确定性 ~20s）
  │
  ├─ Phase 1: python3 toolkit_to_fact_tree_draft.py
  │      → spec/.cache/fact-tree/draft.json (purpose 全 null，结构完整)
  │      → spec/.cache/fact-tree/source-index.json
  │
  └─ Phase 2: cp draft.json → spec/toolkit-fact-tree.json
             跑结构性自检 7 项
             输出摘要（无 LLM 字段）

下游消费（不在本 skill 内）：
  - a2h-spec Phase 0.5 探测 spec/toolkit-fact-tree.json
        用 navigation / components 结构事实写 spec
        自己 LLM 生成 spec 描述（不依赖 fact-tree.purpose）
  - app-relationship-tree Phase 4D + 4.5
        primary = fact-tree
        Phase 4.5.B 一次性 LLM 读源码补 description + supplements
        输出 spec/app-relationship-tree.json（含 description）
```
