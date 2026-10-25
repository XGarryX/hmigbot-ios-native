# `spec/fix/round-N/` 单问题文件 Schema

本文档定义 `spec/fix/` 下每个问题 markdown 文件的统一格式。**所有写入 `spec/fix/` 的 verifier**（dt-verifier、visual-verify、未来的任何 verifier）都必须遵循此 schema；**所有读取 `spec/fix/` 的消费者**（arkts-verify-fix、visual-fixer agent、a2h-verify CHECK-6）都按此 schema 解析。

---

## 一、目录布局

```
spec/fix/
├── round-0/                        ← baseline（首轮，standalone 或 CHECK-6 触发均同构）
│   ├── _index.md                   ← 本轮所有问题清单（人类速览，verifier 自动生成）
│   ├── _summary.md                 ← 本轮统计 + 页面维度表 + checks performed（verifier 自动生成）
│   ├── _delta.md                   ← 与上一轮对比（round-0 不写，round-1+ 才写）
│   ├── feat/
│   │   ├── F001_AC01_<slug>.md     ← 单元测试 RED/ERROR
│   │   ├── F010_AC03_<slug>.md
│   │   └── _systemic/
│   │       └── SYSTEMIC_<slug>.md  ← 跨 Feature 系统性问题
│   └── ui/
│       ├── P0010_UI_INTERACT_<slug>.md
│       ├── F010_UI_AC04_<slug>.md
│       ├── ALIGN_P0002_color_mismatch_titlebar-bg.md   ← 视觉对齐
│       ├── URL_P0023_query_lang.md                     ← H5 URL 断言失败
│       ├── CRASH_P0017_app_crash_on_load.md            ← 崩溃 / 不可达
│       └── _systemic/
│           └── SYSTEMIC_<slug>.md
│
├── round-1/                        ← autofix 第 1 轮回跑后
├── round-2/
└── _state.yaml                     ← 全局轻量状态（current_round 等）
```

**核心 invariant**：`round-N/` 目录里**只放本轮 verifier 跑完时仍是 RED/ERROR/DIFF 的问题**。GREEN 不写文件；文件存在 = 本轮失败。

**不变性保证**：
- 文件**只增不删** —— 每轮新建一个 round 目录，旧目录不动（git 永久保留）
- 同一问题跨轮的身份靠 **id**（文件名 = id + .md）
- 状态变化（fixed / regressed / stale）从目录序列推导，不持久化在 frontmatter

### `progress.json` 与 `round-N/` 的关系（visual-verify 专用）

**两者职责严格分离**：

| 文件 | 角色 | 写入时机 | 生命周期 |
|---|---|---|---|
| `spec/visual-verify/progress.json` | visual-verify 内部状态机（断点续跑、单页闭环 round 计数、scenario 结果） | 每页 Phase 4 结束立即写 | 每次 visual-verify run 内部维护，跨 run 复用 |
| `spec/fix/round-N/` | 对外交付物（autofix / verify-fix 消费） | visual-verify **整轮**全跑结束、且收敛或达 MAX_ROUNDS 后**一次性**生成 | 每个 verifier round 一份目录，git 永久保留 |

**关键约定**：
- visual-verify 内部的"单页闭环 round 计数"（progress.json.pages[X].rounds，最多 10 轮）**不**等于 `spec/fix/round-N/` 的全局 N。N 由**本 skill 自持推进**（`_state.yaml.current_round`，`scripts/round_budget.py` 唯一写者）；调用方（含 a2h-verify）只读 N 定位目录，不自增。
- visual-verify 一次完整 run（跑完所有 P0 页 + 全部修完或达 cap）→ 对应**一个** round-N 目录。
- 每页未收敛时，**最后一轮**的差异写入 round-N；已收敛页不写文件（符合 "文件存在=失败" invariant）。
- 崩溃 / blocked 页面写 `CRASH_*.md`（visual-verify 该页 status=blocked 时必写）。

---

## 二、文件名 = ID（确定性、跨轮稳定）

| 来源 | ID 推导规则 | 例 |
|---|---|---|
| dt-verifier 单元测试 | `<it_name>` | `F010_AC03_deleteFiles_useRecycleBin` |
| dt-verifier UI 测试（页面派生） | `<it_name>` | `P0010_UI_INTERACT_row_open_dialog` |
| dt-verifier UI 测试（feature 派生） | `<it_name>` | `F010_UI_AC04_bookmarkRow_click` |
| visual-verify 视觉对齐 | `ALIGN_P<page_id>_<diff_kind>_<context_slug>` | `ALIGN_P0002_color_mismatch_titlebar-bg` |
| visual-verify 崩溃/不可达 | `CRASH_P<page_id>_<reason_slug>` | `CRASH_P0017_app_crash_on_load` |
| visual-verify URL 断言失败 | `URL_P<page_id>_<diff_path_slug>` | `URL_P0023_query_lang` |
| systemic（任意来源） | `SYSTEMIC_<bucket_slug>` | `SYSTEMIC_db-init-context-failure` |

**铁律**：
- ID **不依赖**时间戳、轮次、外部状态
- 文件名严格等于 ID + `.md`，可 1:1 互查
- ID 唯一性必须保证；同一轮内重复 ID → verifier 报错停下

### `<context_slug>` 派生规则（visual-verify ALIGN 专用，必读）

同一页面常有多个同 `<diff_kind>` 差异（如 P0010 有 3 处 color_mismatch）；不加 `<context_slug>` 必然 ID 冲突。派生顺序按**输入来源**分流：

#### A. `differences[]` 普通项（含 suggested_fix）

1. **首选** `suggested_fix.property` — 如 `backgroundColor` → `backgroundcolor`
2. **次选** `suggested_fix.file` 的 basename + property — 如 `TitleBar.ets` + `fontColor` → `titlebar-fontcolor`
3. **再次** `description` 的**英文/数字**关键词（取前 2-3 个 token，kebab-case）；**中文 description 跳过此步直接走兜底**
4. **兜底** `idx<NN>` — 同一 (page_id, diff_kind) 内按 differences[] 数组顺序，从 `idx01` 开始

#### B. `siblings_order_checks[]`（match=false）

直接派生自 **`container`** 字段：`"HomeView Tab Row"` → `homeview-tab-row`。**不走通用规则**。

#### C. `icon_semantic_checks[]`（match=false）

直接派生自 **`context`** 字段：`"Works FAB"` → `works-fab`。**不走通用规则**。

#### D. `missing_elements[]` / `extra_elements[]`（裸字符串数组）

字符串若全为 ASCII → 取前 2-3 词 kebab-case；若含中文/非 ASCII → 直接用 `idx<NN>`（数组下标）。例：
- `"bottom upload button"` → `bottom-upload-button`
- `"底部上传按钮"` → `idx01`（在 `extra_elements[]` 中是第 1 项）

#### E. `scroll_needed=true`（整页只有一条）

**不需要** context_slug，ID 直接为 `ALIGN_P{page_id}_scroll_overflow`。

#### slug 通用约束

- kebab-case，仅 `[a-z0-9-]`
- 长度 3–30 字符
- 不含 `_`（避免和 ID 各段分隔符混淆）；`idx<NN>` 是唯一例外
- 派生后 (page_id, diff_kind, context_slug) 仍冲突 → 末尾追加 `-2` / `-3`

### `<diff_path_slug>` 派生规则（URL_MISMATCH 专用）

`compare_webview_urls.py` 的 `diff: ["path", "query.lang", "query.from"]` 是 array，**每个 diff 项拆成一个独立文件**：

| diff 原值 | slug |
|---|---|
| `path` | `path` |
| `origin` | `origin` |
| `fragment` | `fragment` |
| `query.lang` | `query_lang` |
| `query.from` | `query_from` |

例：上面的 array 拆成 `URL_P0023_path.md`、`URL_P0023_query_lang.md`、`URL_P0023_query_from.md` 三个文件，各自独立 disposition / 修复路径。

### `title:` 派生规则（visual-verify 专用）

`title` 是 `_index.md` 速览的核心，必须 deterministic：

| kind | 公式 | 例 |
|---|---|---|
| `ALIGNMENT_DIFF` (普通 differences) | `[{page_id}] {category_zh}: {description 截断 38 字}` | `[P0010] 颜色: 标题栏背景偏亮，应为深色实际为浅色` |
| `ALIGNMENT_DIFF` (siblings_order) | `[{page_id}] 顺序: {container} 与 iOS 不一致` | `[P0010] 顺序: HomeView Tab Row 与 iOS 不一致` |
| `ALIGNMENT_DIFF` (icon_semantic) | `[{page_id}] 图标: {context} 形状/方向不符` | `[P0010] 图标: Works FAB 形状/方向不符` |
| `ALIGNMENT_DIFF` (missing/extra) | `[{page_id}] 缺失: {element}` / `[{page_id}] 多余: {element}` | `[P0010] 缺失: 底部上传按钮` |
| `ALIGNMENT_DIFF` (scroll_overflow) | `[{page_id}] 滚动: 单屏页面意外需要滚动` | 同左 |
| `URL_MISMATCH` | `[{page_id}] URL: {diff 字段} 跨端不一致` | `[P0023] URL: query.lang 跨端不一致` |
| `CRASH` (app_crash) | `[{page_id}] 崩溃: {phase} 阶段` | `[P0017] 崩溃: load 阶段` |
| `CRASH` (scenario_failed) | `[{page_id}] 不可达: {scenario} 场景失败` | `[P0040] 不可达: login 场景失败` |

`category_zh` 映射表：`color`→颜色, `font`→字体, `layout`/`layout_bug`→布局, `spacing`→间距, `component`→组件, `icon`→图标, `text`→文案。

总长度硬上限 60 字符；超出时截断 description/element 部分并追加 `…`。

### `<diff_kind>` 枚举（visual-verify ALIGN 专用）

| 取值 | 含义 | 来源（multimodal output category） |
|---|---|---|
| `layout_drift` | 布局位置/尺寸/兄弟元素顺序差异 | `layout` / `siblings_order_checks.match=false` |
| `layout_bug` | ArkTS 隐形 layout 缺陷（layoutWeight 误用、ImageFit 撑高等） | `layout_bug` |
| `color_mismatch` | 颜色/对比度差异 | `color` |
| `font_mismatch` | 字体大小/粗细差异 | `font` |
| `spacing_drift` | padding / margin / 间距差异 | `spacing` |
| `component_mismatch` | 组件类型不一致（应该是 List 写成了 Grid 等） | `component` |
| `icon_mismatch` | 图标语义/资源不一致 | `icon` / `icon_semantic_checks.match=false` |
| `missing_element` | 期望出现的组件缺失 | `missing` / `missing_elements[]` |
| `extra_element` | 期望不存在的组件出现 | `extra_elements[]` |
| `text_mismatch` | 文案与 spec 不符 | `text` |
| `scroll_overflow` | `capture_mode=single` 下却需要滚动（layoutWeight 撑高的强信号） | `scroll_needed=true` |

### `<reason_slug>` 派生规则（CRASH 专用）

CRASH 来自四类根因，写法不同：

| reason_slug 取值 | 触发场景 | evidence 主路径 | fixer_layer |
|---|---|---|---|
| `app_crash_on_<phase>` | 应用进程消失 / Activity/Ability 不再前台（Step 4.1.5 检测到） | hilog/logcat 异常段路径 + `:lineno` | `ui` |
| `scenario_failed_<scenario_name>` | `arkts-scenario-runner` 跑挂导致页面进不去（Step 4.-1） | `spec/scenarios/artifacts/<id>/result.json` | `feat`（修 scenario YAML/runner） |
| `scenario_required_<scenario_name>` | 该页需要前置 scenario 但 `page_scenarios.json` 没声明，或 scenario YAML 不存在（Step 1.2.5 / Step 4.-1 探测发现） | `spec/visual-verify/page_scenarios.json` 当前状态 + 该页所属 feature 名 | `feat`（补 scenario YAML） |
| `scenario_required_undefined` | 该页 reachability 为 `data_dependent` 但完全无 scenario 声明，且需要人工流程（如真实短信/NFC/支付）不可自动化 | 同上 + 评审说明 | `feat`，但 disposition 可能为 `manual_review` |
| `nav_unreachable_<from>_<to>` | 导航链路 dumpLayout 找不到目标元素 | dumpLayout JSON 路径 | `ui` |

`<phase>` 取值：`load` / `nav` / `interact` / `screenshot`。`<scenario_name>` 取 scenario 文件名（如 `login`、`upload_image`），未指定时用 `undefined`。

**新增 v2 约束**：`status: "skip"` 在 visual-verify 已废弃。原本应 skip 的页面（如无 scenario / 无法到达）**必须**写一份 CRASH markdown 记录缺口——下游消费者不能从 "缺失文件" 推断 "已对齐"，必须从 "存在 markdown" 看到 "未测/有缺口"。

### `<bucket_slug>` 命名（SYSTEMIC 专用）

kebab-case，简洁描述根因。常见 visual-verify SYSTEMIC：
- `missing-nav-destination` — 多页未用 NavDestination 包裹
- `titlebar-missing-status-bar-padding` — 多页标题栏缺 `padding({ top: 42 })`
- `layoutweight-misuse` — 多页 `layoutWeight(1)` 用在无固定高度父容器
- `resource-density-missing` — 多张图缺密度适配版本

---

## 三、Frontmatter Schema

### 3.1 通用字段（所有 source 必填）

```yaml
---
# 标识
id: <文件名去掉 .md 后的 slug>
title: <一句话标题，人类可读，≤ 60 字>

# 分类
source: <dt-verifier | visual-verify | manual>
layer: <feat | ui>
kind: <RED | ERROR | IMPL_MISSING | UNREACHABLE | ALIGNMENT_DIFF | URL_MISMATCH | CRASH | SYSTEMIC>
severity: <P0 | P1 | P2>
fixer_layer: <feat | ui>           # 派给哪类 fixer 写盘白名单

# 修复指引
suggested_files:
  - <仓内相对路径 1>
  - <仓内相对路径 2>
  # 多模态未定位时允许写 ["unknown"]，由 fixer 自行 grep

# 关联
related: []                         # 其他问题文件路径（非 systemic 关系）
systemic_root: null                 # 若被某 SYSTEMIC_*.md 文件 affects 到，反向指 null | <path>
affects: []                         # 仅 SYSTEMIC_*.md 文件填，列被它聚合的非 systemic 文件
# 产出侧对账（B.4.5 同页 feat↔ui fold；只在 fold 发生时写，否则省略）
subsumes_ui: []                     # 仅 feat 单：feat primary 时，列被它折叠掉(已 rm)的 ui 单 id；外观验收点已并入本单 §3
subsumes_feat: []                   # 仅 ui 单：ui primary 时，列被它折叠掉的 functional_check id（UI 缺陷阻断了该功能）
subsumes_root: []                   # 仅 feat 单(事务型)：同根 fold(B.4.5 5c)——同一事务链上其它 outcome 点因同一「首个失败步」(同 failure_trace 签名)被本单吸收的 check id；本单 §5 根因指首个失败步、§3 带全链 failure_trace，其余点标"连带"不各出单
# 事务型重验参数（仅 verify_by=outcome feat 单；detection 填——它跑过 verify_outcome 知道这些；供 visual-fixer C.5 round 内紧循环重编+重验用，缺则 fixer 跳过紧循环走"待下轮验")
reverify:
  scenario: <hmos事务配方名>          # 如 login_hmos（HMOS 侧能跑的 outcome 配方）
  device_id: <hmos_target>           # 如 127.0.0.1:5555
  package: <hmos_bundle>             # 如 com.example.xxx
  product: default                   # 可选：hvigor product，缺省 default

# 证据（至少 1 条）
evidence:
  - <日志/截图/dump 路径，带行号锚点>
  # dt-verifier 例：docs/autofix-log/round-1/raw-log.txt:1245
  # visual-verify 例：
  # - spec/visual-verify/screenshots/sbs/round-1/trip_2_logged_in_vip/P0010.jpeg
  # - spec/visual-verify/screenshots/harmony/round-1/trip_2_logged_in_vip/P0010.jpeg
  # - spec/visual-verify/screenshots/ios/trip_2_logged_in_vip/P0010.png
  #
  # ★铁律：evidence 只许写 **canonical 交付位**（screenshots/{sbs,harmony,ios}/…，
  #   过程证据在 harmony/round-N/{trip}/_evidence/）。**禁止**写 `replay/<run>/shots|dumps/…`
  #   —— <run> 每跑一轮换名（v4→v5→…），而老目录仍在盘上：那种路径**打得开**却指向历史轮次的
  #   采集，fixer 据一张三代前的图改代码且无从察觉。判定包里给的就是 canonical，原样抄即可。
  #   例外只有两类，且必须在正文里点明是"历史轮次/过程档"、不得进 evidence: 清单：
  #     · 出处存档 `replay/<run>/judge_groups/gN.json`、`run.jsonl`（不摆位的过程档）
  #     · 有意的跨轮引用（如"上一轮 v4 曾成功渲染"这类反向证据）——写在正文并标明轮次

# 跨轮持久决策（verifier 单一裁判，fixer 不写；详 §五 表格）
disposition: null                   # null | partial | skipped | problematic | manual_review | fixed
disposition_reason: null            # 字符串，简述原因
disposition_set_at_round: null      # 整数，绝对轮次号；rebase 时若改 round 号需手工同步
---
```

### 3.2 visual-verify 专属字段（仅 source=visual-verify 必填，其他 source 可整段省略）

紧跟在通用字段的 `evidence:` 之后、`disposition:` 之前插入：

```yaml
# visual-verify 专属（仅 source=visual-verify 写）
page_id: P0010                      # 必填。ui 单(ALIGN_/CRASH_/URL_)：与文件名中的 P<page_id> 一致。
                                    #   feat 单(IMPL_MISSING，按功能点命名如 MineSetting_03)：填 dual-oracle
                                    #   grounding 时所在的页（可与文件名脱钩）——B.4.5 同页 feat↔ui 对账的 join 键。
capture_mode: single                # single | long | web | single_fallback；CRASH 时填捕获崩溃前的最后一次 capture_mode 或 null
similarity: 0.85                    # 0.0–1.0；CRASH / URL_MISMATCH 允许 null
multimodal_severity: high           # high | medium | low；CRASH 填 high；URL_MISMATCH 填 high
is_migration_bug: true              # 多模态原值；ALIGNMENT_DIFF 必填；URL_MISMATCH/CRASH 恒为 true
```

> dt-verifier / manual 来源**整段省略**这 5 个字段，不要写 null —— 保持 frontmatter 紧凑。

### 字段语义

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 文件名 slug，与文件名严格一致 |
| `title` | string | ≤ 60 字符，便于 _index.md 速览 |
| `source` | enum | 来源 verifier 工具名 |
| `layer` | enum | `feat` 或 `ui`；与目录路径一致（feat/ → feat；ui/ → ui；_systemic/ 继承父目录） |
| `kind` | enum | 见 §四 |
| `severity` | enum | dt-verifier 从 spec priority 继承（P0/P1/P2）；visual-verify 按 §四 映射规则从 `multimodal_severity` 转换 |
| `fixer_layer` | enum | 派单层；通常 = layer，但 systemic 可能跨层 |
| `suggested_files` | list[string] | 至少 1 条；多模态未定位时允许 `["unknown"]`（fixer 自行 grep） |
| `related` | list[string] | 关联问题（如"修这个会顺便修那个"），非 systemic 关系 |
| `systemic_root` | null \| string | 若被某 SYSTEMIC 文件 `affects` 列表包含，此处反向指向那个 SYSTEMIC 文件路径；否则 null |
| `affects` | list[string] | 仅 SYSTEMIC 文件填；列出被聚合的非 systemic 问题文件相对路径 |
| `subsumes_ui` | list[string] | 仅 feat 单、B.4.5 fold 发生时；列被 feat primary 折叠掉(已 rm)的 ui 单 id。外观验收点已并入本单 §3。下游计数应把这些 ui 视为已归并，不重复计 |
| `subsumes_feat` | list[string] | 仅 ui 单、ui primary 时；列被折叠的 functional_check id（UI 缺陷阻断了该功能）。修好本 ui 单后该功能应恢复，下轮 dual-oracle 复验 |
| `evidence` | list[string] | 至少 1 条；接受日志路径（带行号 `:lineno`）、截图路径、dump 路径、JSON 产物路径 |
| `page_id` | string | visual-verify 必填。ui 单与文件名 `P<page_id>` 一致；feat 单填 grounding 所在页（与文件名脱钩，作 B.4.5 对账 join 键）。其他 source 整段省略 |
| `capture_mode` | enum \| null | visual-verify 必填，CRASH 可为 null |
| `similarity` | float \| null | visual-verify 必填，0.0–1.0；CRASH / URL_MISMATCH 允许 null |
| `multimodal_severity` | enum | visual-verify 必填，模型原始输出 |
| `is_migration_bug` | bool | visual-verify 必填；多模态原值；severity 映射依据；autofix 可按此过滤"真 bug" vs "platform_difference" |
| `disposition` | null \| enum | autofix 决策标记，见 §五 |
| `disposition_reason` | null \| string | disposition 非 null 时必填 |
| `disposition_set_at_round` | null \| int | disposition 非 null 时必填；绝对轮次号 |
| `stubborn_origin` | null \| string | Phase 7 移入 `spec/fix/stubborn/<id>/` 时写入原 ui/ 相对路径；回流时保留供回溯 |

---

## 四、`kind` 枚举（决定下游处理方式）

| 取值 | 含义 | 主要来源 | autofix 是否处理 |
|---|---|---|---|
| `RED` | 测试运行后断言失败 | dt-verifier | ✅ 处理 |
| `ERROR` | 测试运行时报错（非断言失败，如 init 失败、timeout） | dt-verifier | ✅ 优先处理 |
| `ALIGNMENT_DIFF` | visual-verify 检测到与 iOS 截图的视觉差异 | visual-verify | ✅ 处理 |
| `URL_MISMATCH` | visual-verify H5 页面 URL（origin / path / 业务 query / fragment）跨端不一致 | visual-verify Step 4.1.4 | ✅ 处理（按 ERROR 优先级；逻辑 bug 不是视觉差） |
| `CRASH` | visual-verify 截图过程中应用崩溃 / 导航不可达 | visual-verify Step 4.1.5 | ✅ 优先处理 |
| `SYSTEMIC` | 多个失败聚类到同一根因 | 任意 | ✅ 最高优先 |
| `IMPL_MISSING` | spec 描述了能力但实装/manifest 完全缺失（R1 占位） | dt-verifier | ❌ 跳过；需人工产品决策 |
| `UNREACHABLE` | 测试体系结构性不可达（外部 Intent / Tab 子页 / Dialog-only 等 R2 占位） | dt-verifier | ❌ 跳过；不计入分母 |

### `severity` 映射规则（visual-verify 专用）

多模态返回的 `high/medium/low` 按以下规则映射成 P0/P1/P2，原值保留在 frontmatter `multimodal_severity`：

| `multimodal_severity` + 条件 | `severity` |
|---|---|
| `high` + `is_migration_bug=true` | **P0** |
| `high` + `is_migration_bug=false`（platform_difference 但用户未豁免） | P1 |
| `medium` | P1 |
| `low` | P2 |
| `URL_MISMATCH` 类（任何级别） | **P0**（业务参数错误一律 P0） |
| `CRASH` 类（任何级别） | **P0** |

dt-verifier 来源仍按现有规则从 spec priority 继承 P0/P1/P2，本映射不影响它们。

---

## 五、`disposition` 状态字段

跨轮持久决策。**写入权限严格分层**：

| 取值 | 谁能写 | 写入时机 | 含义 | 下轮处理 |
|---|---|---|---|---|
| `null` | verifier | 默认 | 正常排队等修 | 正常 carry-forward |
| `partial` | verifier (legacy) | fixer 改了未跑回归 | 等待下一轮 visual-verify 重测 | 强制 carry-forward + 重测 |
| `skipped` | verifier | scenario 不可达 / OS 能力缺失 / 客户已豁免 | 显式暂跳过 | carry-forward 但优先级降 |
| `manual_review` | verifier | 需人工介入（私仓黑盒 / SDK 缺失 / 客户决策） | 等用户拍板 | carry-forward 提醒，不自动修 |
| `fixed` | **verifier 唯一能写**（下一轮 visual-verify）| 下一轮重新截图比对 sbs similarity ≥ 0.95 且无 CRASH | 正式关闭 finding | 停止 carry-forward |
| `problematic` | verifier | 触发 GREEN→RED 回归 | 禁选 | batching 时直接过滤掉 |

**关键规则**：

1. **visual-fixer 不再写 disposition**（2026-05-24 起）—— fixer 每轮只追加 §6 attempt + 改代码，所有 disposition 状态由 verifier 单一裁判；旧 5 态保留为 verifier / carry-forward / 历史兼容值，下游消费者继续按 5 态读
2. 只有下一轮 visual-verify 重新截图、sbs similarity ≥ 0.95、page 无 CRASH 时，才能写 `disposition: fixed`
3. 升级时 visual-verify 把文件重命名为 `RESOLVED_<原名>.md` 并写 `disposition: fixed`
4. **similarity 阈值硬约束**：若 < 0.95 即便代码看着对也保留 `partial`/`null`，下轮再测
5. **fixer 必须每轮真改一次代码** + **§6 新 attempt 的"假设根因 + 改动摘要"必须与历史 attempts 全部不同**（即便挂 OG / 私仓黑盒也要换新假设试一次，"被迫乱改说不定能改对"）—— 由 reviewer 抽查保证

**rationale**：
- round-4 `RESOLVED_PCustomerServiceWebActivity` 反面教材 → fixer 不能自标 fixed
- fixer 写 disposition 永远高估自己 → 完全交 verifier 单裁判，fixer 只管"试新假设 + 改代码"
- 真相永远在 verifier 下轮 sbs

**carry forward 算法**（verifier 写 round-N/<id>.md 之前）：

```pseudocode
if exists(spec/fix/round-{N-1}/<layer>/<id>.md):
    prev = read(prev file)
    if prev.disposition != null:
        new_file.disposition              = prev.disposition
        new_file.disposition_reason       = prev.disposition_reason
        new_file.disposition_set_at_round = prev.disposition_set_at_round
```

---

## 六、正文 5 个 Section（顺序固定，标题严格一致）

> **不写"历史尝试"section**：跨轮历史靠 round 目录序列承载（git diff round-N round-N+1 + `docs/autofix-log/round-N/{batch,fixer-summary,rollback}.md` 已经覆盖），无需在每个问题文件里维护表格。

### 6.0 修复前必读（仅 `source: visual-verify` 必须，dt-verifier / 其它 source 可略）

正文第一行 = HARD-GATE 块引用指令，迫使下游 fixer agent **必须 Read 至少一张 sbs 图**才能开始修代码。机制：fixer 按顺序读 markdown，第一行就看到这条指令，会自动 Read evidence[0] 拿到原始视觉证据，避免**仅凭文字描述凭空改代码**。

模板（visual-verify markdown 第一行 = title 下方，§1 上方）：

```markdown
# {title}

> 🔴 **修复前必读 / FIXER MUST READ**：本 finding 含视觉差异，修复代码前 **必须** Read 以下 sbs 拼图验证差异描述、确认改动方向。**禁止**仅凭 §3 文字描述就改代码。
> - `spec/visual-verify/screenshots/sbs/round-{N}/{trip_id}/{page_id}.jpeg`（路径必含 round-N，按本轮 _state.yaml.current_round 填）
> - 若只是 nav/路由类（无视觉成分，§4 已有具体行号），可仅文字定位，无需读图。

## 1. Spec 引用
```

**注意**：仅在 `kind == ALIGNMENT_DIFF` 且 `category_pattern` 与视觉强相关时（如 layout_drift / color_diff / spacing_drift / icon_semantic / siblings_order / missing_element / extra_element）插入此块；nav_chain_broken_hmos / page_missing_hmos / URL_MISMATCH / CRASH 等纯结构/路由问题可跳过本块（§4 §5 已有可执行行号）。

### 6.1 五段正文模板

```markdown
# {title}

## 1. Spec 引用
> dt-verifier: 引用 spec/baseline/ 原文（≤ 5 行块引用）
> visual-verify: 引用 iOS 源端截图（视觉基线，无文档可引时） / 或 spec/baseline/ui/page_NNNN.md
> URL_MISMATCH: 引用 iOS 源端运行时抓取的 URL 字符串（视为期望值）

来源: <见下方各 source 写法>

## 2. 期望
<期望行为或视觉，自由文本；dt 写断言文本，visual 写颜色/尺寸/视觉描述，URL 写期望 url 字符串>

## 3. 实际
<实际行为或视觉；dt 写运行返回值/错误首行，visual 写截图差异描述，URL 写实际 url 字符串>

## 4. 源码缺口
- <仓内相对路径>:<行号> — <一句话描述缺口>
- <仓内相对路径>:<行号> — ...

（行号未知写 `unknown`；多模态完全未定位时允许写一行 `unknown — 多模态未定位，由 fixer 自行 grep 定位`）

## 5. 修复建议
1. <步骤 1：动词开头，具体到方法名 / 资源 key / 组件类型>
2. <步骤 2>
3. ...

## 6. 尝试过的修复方案（仅由 visual-fixer 追加，禁删历史条目）
<!-- 首次写 markdown 时本段为空。每轮 visual-fixer 在改完代码后在此段末尾追加一条新记录；
     carry-forward 会原样保留本段，所以下一轮 fixer 能看到所有失败的历史尝试，必须改变思路。 -->

### round-{N} attempt by visual-fixer
<!-- ⚠️ 子段标题格式硬约束（regex: ^### round-\d+ attempt by visual-fixer$）：
     stubborn 计数器靠这一行严格匹配，禁止改成 #### / 漏 "by visual-fixer" 后缀 /
     用别名（如 "round-{N} fix by fixer"）。违反会导致 §6 attempt 数不准、永远进不了 stubborn。-->
- **改动文件**：`<file_a>:<line_range>`, `<file_b>:<line_range>` ...
- **改动摘要**：<一句话描述本轮改了什么，比如"在 fetchWallpaperListIncremental 头部加 await waitForToken()">
- **假设根因**：<本轮 fixer 推测的根因，比如"匿名 token 时序竞争">
- **预期效果**：<本轮预期下轮 visual-verify 看到什么，比如"trip_1 HomePage 渲染 ≥10 个壁纸卡">
- **未做的事 / 已排除的可能**：<比如"未改 signature 链；未排查后端 channel 拒绝">

## 7. 实际可达路径（reach_path，由 fact-tree 自动注入，禁手工编辑）
> 来源: spec/toolkit-fact-tree.json pages[id={page_id}].screenshots.{trip_id}.reach_path

1. <step 1>
2. <step 2>
...

```

### Section 写法约束

| Section | 必填 | 长度上限 | 写法约束 |
|---|---|---|---|
| 1. Spec 引用 | ✅ | ≤ 5 行块引用 | dt：原文直引，末尾 `来源: spec/baseline/...`；visual：截图路径或 page_NNNN.md **+ 必须追加 fact-tree.pages[id].ios_source_refs 注入的 `> 来源: app/src/main/...kt/xml` 行**（让 fixer 能 grep 真源码，不准只写规则/截图）；URL：期望 url |
| 2. 期望 | ✅ | ≤ 8 行（feat 单注入验收块时不限此行数） | 自由文本，能让 fixer 不读 spec 也能理解。**feat 单（kind=IMPL_MISSING）专属**：写单前调 `inject_spec_oracle.py <page_id> "<feature_path>"`，把返回的 `spec_lines`（spec/baseline/features/F*.md `## 验收标准` 行为契约）**原样追加**到本段——这是 feat 修复"怎么算对"的真参考，与 §1 的 ios_source_refs 注入对称。**非静默铁律**：返回 `> spec_oracle: UNRESOLVED(...)` 时**也原样写**，不省略（fixer 据此手读 spec，不静默遗漏）。ui 单不注入（截图自足）。 |
| 3. 实际 | ✅ | ≤ 8 行 | dt 引日志原文首行（≤ 160 字）；visual 贴 multimodal `description` + `root_cause_hint` 原文 |
| 4. 源码缺口 | ✅ | 每行一条 | 至少 1 条；`<file>:<line>` 或 `<file>:unknown` 或 `unknown — ...` |
| 5. 修复建议 | ✅ | 步骤化 | 至少 1 步；每步动词开头 |
| 6. 尝试过的修复方案 | visual-fixer 改完代码必填 | 每轮 ≤ 10 行 | **追加式**写入，禁删除历史；新条目前用 `### round-{N} attempt by visual-fixer` 分隔；本段必须含 5 个子项（改动文件 / 改动摘要 / 假设根因 / 预期效果 / 未做的事）；**"改动文件" 子项必须 ≥ 1 个真实仓库相对路径**（如 `products/phone/.../X.ets:42`），禁写 "无 / - / N/A / 空"——reviewer 抓到即 flag empty_diff |
| 7. 实际可达路径 | visual-verify source 必填，其它 source 可空 | 步骤化 | **由 sub-agent 写 markdown 时从 fact-tree.pages[id].screenshots.{trip}.reach_path 字段读出注入**，禁手工编辑；若 fact-tree 该字段为空（Phase 2 未跑过 / page 未达成 baseline）→ 写 `unknown — Phase 2 baseline 缺失，参考 SKILL.md §4 Phase 2 跑 dispatch_phase2_batches.py + 派 sub-agent 后重生成` |

### §6 的核心规则（防"无效修复死循环"）

1. **首轮 verifier 写 markdown 时** §6 段为空（或只放 HTML 注释占位）
2. **每轮 visual-fixer 改完代码必须追加一条** `### round-{N} attempt by visual-fixer` 子段（5 个子项）
3. **下一轮 visual-fixer 接到 carry-forward 的 markdown 时**：
   - **MUST READ §6 全部历史条目**
   - **MUST NOT 重复上一轮"假设根因 / 改动摘要"完全相同的修复尝试**
   - 必须在新尝试的"未做的事 / 已排除的可能"里显式列出已排除的方向，让再下轮看得到
4. **carry-forward 步骤不动 §6**：物理复制时只改 frontmatter `disposition` 三行，body §6 原样保留
5. **§6 段从不被 fixer 删除**：即便最终 disposition=fixed 升 RESOLVED，§6 留存供回溯（哪个尝试真生效）

### visual-verify 各 kind 的 Section 写法速查

| kind | Section 1 来源行 | Section 2/3 关键内容 |
|---|---|---|
| `ALIGNMENT_DIFF` (普通 differences[]) | `来源: spec/visual-verify/screenshots/ios/{trip_id}/{page_id}.png`（跨轮共用） | 2: 多模态 `description` 中的"应该是 X"；3: `description` 中的"实际是 Y" + `root_cause_hint` |
| `ALIGNMENT_DIFF` (siblings_order_checks) | `来源: spec/visual-verify/screenshots/sbs/round-{N}/{trip_id}/{page_id}.jpeg` | 2: `ios_order` 数组；3: `hmos_order` 数组 |
| `ALIGNMENT_DIFF` (icon_semantic_checks) | `来源: spec/visual-verify/screenshots/sbs/round-{N}/{trip_id}/{page_id}.jpeg` + `ios_drawable_ref` | 2: `ios.{shape,arrow,color}`；3: `hmos.{shape,arrow,color}` |
| `ALIGNMENT_DIFF` (missing/extra) | `来源: spec/visual-verify/screenshots/sbs/round-{N}/{trip_id}/{page_id}.jpeg` | 2: "iOS 源端有/无 X"；3: "HMOS 端无/有 X"；Section 4 多半 `unknown` |
| `ALIGNMENT_DIFF` (scroll_overflow) | `来源: spec/visual-verify/screenshots/harmony/round-{N}/{trip_id}/{page_id}.jpeg`（看到滚动条/被推出屏内容） | 2: "单屏可完整展示"；3: "需滚动才可见 {元素}"；Section 5 优先建议排查 layoutWeight |
| `URL_MISMATCH` | `来源: 运行时 hilog/logcat 抓取，期望 url = <ios_url>` | 2: `ios_url`；3: `hmos_url` + diff 字段名；evidence 写 hilog 路径或 `compare_webview_urls.py` 输出 JSON |
| `CRASH` (app_crash) | `来源: 崩溃 hilog 段路径 + :lineno`；如有崩溃前截图也加进 evidence | 2: 期望页面正常加载；3: 崩溃时机（哪一步）+ hilog 异常首行；Section 5 修 ArkTS 页面 |
| `CRASH` (scenario_failed) | `来源: spec/scenarios/artifacts/<id>/result.json` + scenario YAML 路径 | 2: 期望 scenario 把 App 带到 {state}；3: scenario stderr 首行 + 失败 step；**Section 5 修 scenario YAML / runner 配置，不是 ArkTS 页面**；fixer_layer 标记需注意 |
| `CRASH` (nav_unreachable) | `来源: dumpLayout JSON 路径` + 上一步截图 | 2: 期望从 {from} 能点击到 {target}；3: dumpLayout 中未找到 {selector}；Section 5 排查导航树/被遮挡元素 |

---

## 七、SYSTEMIC 文件的特殊性

`*_systemic/SYSTEMIC_<slug>.md` 与普通问题文件结构相同，但额外要求：

1. **frontmatter 必填 `affects`**：列出被聚合的非 systemic 问题文件路径（相对 `spec/fix/` 根的路径）
2. **`kind: SYSTEMIC`**
3. **被聚合的普通问题文件 `systemic_root`** 反向指向此 SYSTEMIC 文件
4. **`fixer_layer`** 可能与所在目录的 layer 不同（如 feat/_systemic/ 下的某文件 fixer_layer=ui，因为根因在 UI 层）
5. **`affects` 列表中的 ID 在下一轮 verifier 跑测后会自动通过目录差异（round-N vs round-N+1）观测，无需在 SYSTEMIC 文件中逐条记录修复结果**

聚合阈值：visual-verify 中**同根因 ≥3 页**才聚合为 SYSTEMIC，<3 页保持各自独立 ALIGN_*.md。

---

## 八、`_index.md` 与 `_summary.md` 与 `_delta.md`

verifier 每轮额外生成 3 个汇总文件（不是问题文件，不参与 fixer 派单）：

### `_index.md`（人类速览，每轮新生成）

```markdown
# Round {N} 索引

> 生成时间：YYYY-MM-DDTHH:mm:ss+08:00

## Feature 层（{count} 条）
- [F010_AC03 deleteFiles 必须支持 useRecycleBin 分支](feat/F010_AC03_deleteFiles_useRecycleBin.md) [RED][P0]
- [SYSTEMIC db-init Context 缺失](feat/_systemic/SYSTEMIC_db-init-context-failure.md) [SYSTEMIC][P0] (affects 12)
- ...

## UI 层（{count} 条）
- [P0010 设置页 row 点击 Dialog](ui/P0010_UI_INTERACT_row_open_dialog.md) [ERROR][P0]
- [ALIGN P0002 标题栏背景偏亮](ui/ALIGN_P0002_color_mismatch_titlebar-bg.md) [ALIGNMENT_DIFF][P1]
- [URL P0023 H5 详情页 lang 参数缺失](ui/URL_P0023_query_lang.md) [URL_MISMATCH][P0]
- [CRASH P0017 订单状态页加载崩溃](ui/CRASH_P0017_app_crash_on_load.md) [CRASH][P0]
- ...
```

### `_summary.md`（人类报告，每轮新生成）

包含三段：**总计（kind 维度）** + **页面维度（visual-verify 专用）** + **checks performed（证明 verifier 跑过，不只是没找到）**。

```markdown
# Round {N} 统计

> verifier: dt-verifier + visual-verify
> 跑测时间：YYYY-MM-DDTHH:mm:ss+08:00

## 总计（按 kind）

| 维度 | RED | ERROR | ALIGN | URL | CRASH | SYSTEMIC | IMPL_MISSING | UNREACHABLE | 合计 |
|---|---|---|---|---|---|---|---|---|---|
| feat | x | x | - | - | - | x | x | - | x |
| ui   | x | x | x | x | x | x | x | x | x |

## 页面维度（visual-verify 专用，每页一行）

| page_id | 页面名称 | reachability | capture_mode | similarity | high | medium | low | rounds | status |
|---|---|---|---|---|---|---|---|---|---|
| P0001 | Index 首页 | public | single | 0.92 | 0 | 1 | 2 | 2 | ✅ pass |
| P0010 | MineSettingPage | public | long | 0.85 | 1 | 2 | 1 | 5 | 🔄 partial |
| P0017 | OrderStatusPage | public | - | - | - | - | - | - | 💥 blocked |
| P0023 | H5 详情页 | public | web | - | 1 | 0 | 0 | 1 | ❌ fail (URL) |
| P0040 | CreditsPage | login_walled | single | 0.88 | 0 | 0 | 1 | 1 | ✅ pass |

> `status` 取值：`pass` / `partial` / `skip` / `blocked` / `fail`，与 progress.json 同步。

## Checks performed（证明 verifier 跑过）

> 全 pass 项不写问题文件（符合 invariant），但需在此处证明检查跑过。

| verifier | check | 总数 | 失败 | pass 率 |
|---|---|---|---|---|
| dt-verifier | unit tests | 412 | 23 | 94.4% |
| visual-verify | pages screenshot-compared | 80 | 17 | 78.7% |
| visual-verify | siblings_order_checks | 156 | 4 | 97.4% |
| visual-verify | icon_semantic_checks | 89 | 3 | 96.6% |
| visual-verify | url consistency (web pages) | 12 | 1 | 91.7% |

## Top 10（按修复收益排序）

1. [SYSTEMIC db-init](feat/_systemic/SYSTEMIC_db-init-context-failure.md) — affects 12
2. [SYSTEMIC missing-nav-destination](ui/_systemic/SYSTEMIC_missing-nav-destination.md) — affects 8
3. ...

## 未变化项（与 round-{N-1} 比）

无变化的开放问题：{count}
```

### `_delta.md`（每轮 verifier 自动生成，round-0 不写）

完整模板见 `reconcile-rules.md §四`。

---

## 九、`_state.yaml`（项目根全局状态）

```yaml
schema_version: 2
current_round: 3
last_verifier_run_at: 2026-05-06T15:23:11Z
last_verifier_sources: [dt-verifier, visual-verify]
last_verifier_results:
  dt-verifier:
    total_checks: 412
    failed: 23
  visual-verify:
    pages_compared: 80
    pages_blocked: 2
    siblings_order_checks: 156
    icon_semantic_checks: 89
    url_consistency_checks: 12
    failed_total: 25
last_autofix_round: 3
target_green_ratio: 1.0
# max_rounds 已删除（2026-08-11）：彻查确认它是**悬空字段**——改造前唯一的「执行者」是
# e2e-pipeline 里指向 a2h-verify 的散文，而 a2h-verify 只读 current_round 定位目录、
# 从不读 max_rounds（见其 orchestration.md:58「visual-verify 自有 _state.yaml 管轮次」）。
# 其语义（全局轮数天花板）也与新的「每次调用 3 轮、多次调用自由累计」直接冲突。
# 轮数上限现由 invocation.budget 承载，见下。
# 注：ut/ui/dt-verifier 各自私有 _state.yaml 里的 max_rounds 是**另一个文件的另一个字段**，
#     它们真的在用（配 loop_status / no_progress_rounds），不受本次删除影响。

# ── invocation：本次调用的轮次预算（由 scripts/round_budget.py 独占读写，勿手改）──
# begin 时写入、end 时删除。上限判据是**差值**：current_round - started_at_round + 1 < budget，
# 所以多次调用天然累计（调用1 跑 round 0/1/2 → 调用2 从 round-3 起再 3 轮 → 累计 6）。
invocation:
  started_at_round: 3             # 进入本次调用那一刻的 current_round，冻结不变
  budget: 3                       # 本次调用允许推进的轮数（--budget 可覆盖）
  started_at: 2026-08-11T15:04:00+08:00
```

`schema_version` 字段：当本 schema 不向后兼容地变更时递增，verifier 读到不认识的版本必须停下报错。变更历史详 git log。

---

## 十、自检（verifier 写完每轮 round-N/ 后必跑）

```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/run_fix_self_check.py <N>
# exit 0 = 全 PASS / exit 1 = 列 ❌ 不合规项 / exit 2 = 环境问题
```

8 条自检规则（文件名=id / 通用必填字段 / fixer_layer 枚举 / 5 sections / SYSTEMIC affects / visual-verify 必填字段 / similarity 范围 / ID 唯一）的实现细节看脚本，本文档**不复述以防漂移**。不通过的轮次产出视为不合格，必须修正后才能交给 autofix。

---

## 十一、图遍历专属扩展

> 图遍历 + 真实点击架构引入 3 类新 finding + 1 种 placeholder。
> 设计文档：[architecture.md](architecture.md)

### 4.1 新增 finding kind

#### 4.1.1 `CRASH` reason_slug 扩展：`nav_failed`

**触发**：测一条 edge 时，**iOS 源端 click+verify 成功**，**HMOS 端失败**。

**文件名**：`CRASH_P<page_id>_nav_failed_<from_short>_to_<to_short>.md`

例：`CRASH_P0001_nav_failed_HomeActivity_to_MineFragment.md`

##### 不一致 5 类细分（借鉴 HomeTrans button-nav-aligner）

每条 nav_failed finding 必须标 `nav_mismatch_type`（精确划分 HMOS 跟 iOS 比的不一致形式）：

| nav_mismatch_type | 含义 | HMOS 端表现 |
|---|---|---|
| `missing_handler` | Harmony 缺少跳转或缺少点击处理 | 按钮点了无响应（trigger_not_found 或 click_failed） |
| `wrong_target` | Harmony 跳到了错误页面 | 点了跳走，但 verify_signal 是别的 page |
| `extra_navigation` | Harmony 比 iOS 多了不该有的跳转 | iOS 点了无反应（弹 toast 等），HMOS 却跳转到新页 |
| `missing_params` | Harmony 缺少必要参数 / 前置条件 | 跳到目标页但数据空 / 报错（如 detail page 缺 id 参数）|
| `semantic_diff` | 到达的页面语义不等价 | 同名页但内容/态不同（如同样跳"我的"，但 iOS 是"我的-账号"，HMOS 是"我的-空"）|

`visual-fixer` 拿到这 5 种 type 时按差异化策略修：
- `missing_handler` → 加 onClick + 路由调用（最常见，约 60%）
- `wrong_target` → 改 `RouterMap.XXX` 常量引用 / RouterUtils.pushPathByName 参数
- `extra_navigation` → 删除多余 onClick 或加条件守卫
- `missing_params` → 在 `pushPathByName` 时加 `params: {...}`
- `semantic_diff` → 需要更深层语义对齐，可能要改 ViewModel 数据来源（跨层 → BLOCKED，转 visual-fixer）

##### Frontmatter 必填

```yaml
---
id: CRASH_P0001_nav_failed_HomeActivity_to_MineFragment
title: "[P0001] 导航失效: HomeActivity → MineFragment（HMOS 点击无响应）"
kind: CRASH
severity: P0
reason_slug: nav_failed                   # 
source: visual-verify
schema_version: 1
page_id: P0001                            # 失败 edge 的 from 页 id
round: <N>

# 专属字段（kind=CRASH 且 reason_slug=nav_failed 时必填）
v4_edge:
  from_page: HomeActivity
  to_page: MineFragment
  trigger:
    label: "我的"
    resource_id: null
    type: tap_text
  ios_verified: true                  # ★ 关键：iOS 源端 click+verify 通过
  ios_elapsed_ms: 1842
  hmos_failed_reason: trigger_not_found | click_failed | verify_timeout
  hmos_failed_elapsed_ms: 5212
  nav_mismatch_type: missing_handler      # 5 类之一（必填，决定 visual-fixer 修法）

blocks_subtree:                           # 因这条 edge 失败被阻塞的下游 pages
  - AccountInfoActivity
  - AboutUsActivity

disposition: null
disposition_set_at_round: null
suggested_fix_owner: visual-fixer
---

# 现象 / 影响 / 建议排查 ...
```

> **边界**：若按钮**视觉上完全缺失**（HMOS 屏上看不到这个按钮），写 `ALIGNMENT_DIFF` (missing_element) 不写 nav_failed。本 kind 仅当 HMOS **看得到按钮但点了不跳**或**跳错地方**时用。这条边界跟 HomeTrans button-nav-aligner 的设计一致。

#### 4.1.2 `CRASH` reason_slug 扩展：`back_failed`

**触发**：测 edge 成功后按 back，未能回到原 from_page。

**文件名**：`CRASH_P<page_id>_back_failed_<page>_to_<expected_parent>.md`

**v4_edge 字段**：

```yaml
v4_edge:
  page: AccountInfoActivity              # back 触发的当前页
  expected_parent: MineFragment          # 应该回到的页
  actual_landed: HomeActivity            # 实际落在的页（或 null=不动）
  direction: back
  ios_verified: true                 # iOS back 正确
severity: P0 if back_critical else P1    # 只有 back 一条出路 → P0；其它出路在 → P1
```

#### 4.1.3 新 kind：`FACT_TREE_INVALID_EDGE`

**触发**：测 edge 时 **iOS 源端也失败** → fact-tree 数据错，不是 HMOS bug。

**文件名**：`FACT_TREE_INVALID_EDGE_P<from_page>_to_<to_page>.md`

```yaml
---
kind: FACT_TREE_INVALID_EDGE              # 新 kind
severity: P2                              # 不阻塞下游，是上游数据质量问题
v4_edge:
  from_page: HomeActivity
  to_page: NonExistentPage
  ios_failed_reason: trigger_not_found
  hmos_failed_reason: trigger_not_found
suggested_fix_owner: app-relationship-tree   # ★ 路由给上游 skill
---
```

#### 4.1.4a 新 kind：`FACT_TREE_MISSING_EDGE`

**触发**：sub-agent 在 page X 上黑盒扫 clickable 时，点了 fact-tree 不知道的某个 button，**落地页存在于 fact-tree 但 X→Y 这条 edge 没在 X.edges_to_test 里**。

**文件名**：`FACT_TREE_MISSING_EDGE_P<from_page>_to_<to_page>.md`

```yaml
---
kind: FACT_TREE_MISSING_EDGE                # 
severity: P2                                # 上游数据补全问题，不阻塞测试
v4_blackbox_discovery:
  from_page: HomeActivity
  to_page: ScanHistoryActivity               # fact-tree 里有这页，但 from→to edge 漏了
  trigger:
    text: "我的扫描记录"
    resource_id: btn_scan_history
    signature: "elem:abc123def456"
  ios_can_reach: true
  hmos_can_reach: true
  landed_page_signature: "...|s.....|t....."
suggested_fix_owner: app-relationship-tree   # 转给上游补 navigation_contract.trigger
---
```

#### 4.1.4b 新 kind：`FACT_TREE_MISSING_PAGE`

**触发**：同上，但**落地页根本不在 fact-tree.pages/fragments/dialogs 里**（完全没识别过）。

**文件名**：`FACT_TREE_MISSING_PAGE_P<from_page>_NEW.md`（同 from 页多次发现新 page 时加 idx）

```yaml
---
kind: FACT_TREE_MISSING_PAGE                # 
severity: P2
v4_blackbox_discovery:
  from_page: HomeActivity
  to_page: null                              # fact-tree 里没匹配 page
  trigger:
    text: "设置"
    resource_id: btn_settings
  landed_page_signature: "...|s.....|t....."
  landed_screenshot: "spec/visual-verify/blackbox_discoveries/HomeActivity_via_btn_settings.jpeg"
  landed_text_sample: "通用设置, 关于, 退出登录, ..."  # 落地页的代表文本
suggested_fix_owner: app-relationship-tree   # 转给上游补 fact-tree node
---
```

#### 4.1.5 新 kind：`SKIPPED_DATA_REQUIRED`

**触发**：到一个需要数据态的 page 但无可用数据 + 无法跑创建流程。

```yaml
---
kind: SKIPPED_DATA_REQUIRED               # 新 kind
severity: P3                              # 信息性
v4_data_state:
  required: state:document_exists
  reason: db_empty | creation_flow_failed | not_implemented
  attempted_creation: false
  attempted_creation_error: null
disposition: pending_data_seed            # 新 disposition
suggested_fix_owner: noop                 # 不是 bug
---
```

### 4.2 新增 placeholder 类型：`status: blocked`

被上游 NAV_FAILED 阻塞的下游页面**不发独立 finding**，发**占位 markdown**：

**文件名**：`BLOCKED_P<page_id>.md`（不是 ALIGN/CRASH 前缀，避免被当 finding 计入优先级）

```yaml
---
id: BLOCKED_P0024
kind: BLOCKED                             # 新 kind（placeholder）
severity: P3
status: blocked                           # ★ 关键：从 _summary 优先级里排除
blocked_by: spec/fix/round-N/ui/CRASH_P0001_nav_failed_HomeActivity_to_MineFragment.md
blocked_by_edge: "HomeActivity → MineFragment"
disposition: pending_upstream_fix         # 新 disposition
disposition_set_at_round: <N>
suggested_fix_owner: noop
---
```

### 4.3 carry-forward 规则

```
Round N+1 visual-verify Phase 3.5 (batch 切分) 时:

1. 扫 Round N 的**任何 kind**（不限 CRASH_*_nav_failed）带非空 `blocks_subtree` 的单
   → 提取 blocks_subtree（nav_failed 另取 v4_edge.from_page + to_page）
   ★**出单侧铁律**：judge 判某页「因上游 X 阻塞/不可达」时，**必须把该页写进 X 单的 `blocks_subtree`**。
     只写在正文散文里不算——阻塞关系不进承重字段，X 修好后**没有任何机制重采被解封的子树**，
     下游缺陷会一直隐身（2026-07-28 实测事故：创作链上游弹回，下游 ChoicePPTTemplatePage/PPTFilePage
     两轮 never_seen，judge 定案只写了"创作链下游阻塞"、`affects: []`，上游修好后无人重跑 →
     死循环接线错误由人工发现）。机械兜底见 `assert_run_success.py` **cond 7a/7b**。
2. 把 to_page + blocks_subtree 标 retry_priority=high，加入到对应 trip 的 BFS 序列靠前位置
   ★**解封即重采**：上一轮 `disposition: fixed` 且带 blocks_subtree 的单，其列出的页**本轮必须重采**
   （解封 ≠ 已验）。cond 7b 机械卡。
3. 主代理派 batch 时 prompt 加 "retry edges 列表"，提示 sub-agent 优先重测
4. BLOCKED_*.md placeholder 不直接 carry-forward；下轮重测时若 root cause 已修，
   直接产正常 ALIGN/CRASH finding 覆盖（旧 BLOCKED 删除）
5. FACT_TREE_INVALID_EDGE_*.md 永久保留直到 disposition=resolved
   （需 app-relationship-tree 修了 fact-tree 才消除）
```

### 4.4 _summary.md 输出范本

```markdown
# Round N visual-verify 汇总

## 严重故障 (P0)
- 🔴 CRASH nav_failed: HomeActivity→MineFragment （HMOS 点击无响应）
    └─ 阻塞 4 个下游页: AccountInfo / AboutUs / ManageRenew / RefundProgress
       本轮未测试，root cause 修复后下轮自动重测
- 🔴 CRASH back_failed: AccountInfoActivity → 应回 MineFragment 实际不动

## 视觉对齐 (P0/P1) ... (常规 ALIGN)

## fact-tree 质量问题 (P2)
- FACT_TREE_INVALID_EDGE: HomeActivity → SomeDeprecatedPage (iOS 也未跳)

## 跳过 (P3, 信息性)
- 4 个 BLOCKED placeholder（上面 nav_failed 阻塞的）
- 2 个 SKIPPED_DATA_REQUIRED（无文档数据）
```

### 4.5 visual-fixer 路由规则（扩展）

> **路由归属说明（2026-05-22）**：visual-verify 产物的修复 owner 即将迁移到 **visual-fixer (待新建 agent)**，不再由通用 visual-fixer 处理。下面两张表分别描述：
>  - 表 1: visual-fixer **依然兜底**的项（保持现状，不变更其行为）
>  - 表 2: **visual-fixer 接管**的项（/ kind 默认路由到 visual-fixer）

### 4.5.1 visual-fixer 路由（保留现状，不动）

| kind / reason_slug | fix_owner | visual-fixer 行为 |
|---|---|---|
| ALIGNMENT_DIFF | feat | 修 HMOS UI 实现（颜色/布局/元素缺失等） |
| URL_MISMATCH | feat | 修 H5 / WebView URL |
| CRASH (legacy reason_slug：app_crash / scenario_failed) | feat / manual_review | 按原 规则 |
| SKIPPED_DATA_REQUIRED | scenario-builder（数据播种，非代码修复） | 2026-07-10 ③起不再 noop：sub-agent 自愈梯已试尽（attempted_creation_error 有记录），**由主会话派** builder 按 data_hint 重建配方/fixture 后重测该页（fixer/sub-agent 无子代理派发权，见到本行别自派——标注 needs_scenario_builder 上报即可） |
| BLOCKED | noop | 跳过，placeholder 不修 |

### 4.5.2 visual-fixer 路由（/ kind）

| kind / reason_slug | fix_owner | visual-fixer 行为 |
|---|---|---|
| CRASH / nav_failed | visual-fixer | 修 HMOS button onClick handler / 路由跳转 |
| CRASH / back_failed | visual-fixer | 修 HMOS back 行为 / NavPathStack 配置 |
| FACT_TREE_INVALID_EDGE | app-relationship-tree | visual-fixer 跳过，转上游清理 fact-tree |
| FACT_TREE_MISSING_EDGE | app-relationship-tree | visual-fixer 跳过，转上游补 fact-tree.navigation_contract |
| FACT_TREE_MISSING_PAGE | app-relationship-tree | visual-fixer 跳过，转上游补 fact-tree.pages/dialogs/fragments |

### 4.6 schema 自检脚本（附原 §四之后）

三条检查（跨平台 python 一行式，参数 = round 目录如 spec/fix/round-3）：
- check-1: `reason_slug: nav_failed` 的单必含 `ios_verified: true`（否则应归 FACT_TREE_INVALID_EDGE）且有 `blocks_subtree:` 行
- check-2: `kind: BLOCKED` 占位单的 `blocked_by:` 必须指向存在的文件
- check-3: `kind: FACT_TREE_INVALID_EDGE` 的单必含 `suggested_fix_owner: app-relationship-tree`
```text
python3 $SKILLS_ROOT/arkts-visual-verify/scripts/check_fix_schema.py <ROUND_DIR>
# 逐条打印 ❌ 行；有违规 exit 1（原内联 python -c 已落成脚本，判据不变）
```
