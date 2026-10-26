---
name: arkts-feature-coverage-auditor
description: Android→ArkTS 迁移 Feature 覆盖率审计。四层对账（源码 domain × ref/spec §5 能力 × api-inventory feature 候选 × ui-manifest 页面），强制识别 a2h-spec Phase C 阶段漏掉的业务域 feature（如笔记图层 layer / 大纲 outline / 文档标签 tag / 定时器 clock / 书签 bookmark / 多窗口 multi_window 等被 LLM 误并入其它 feature 或完全忽略的独立能力）。基于源码包路径扫描 + ref/spec §5 节标题反查 + api-inventory feature_candidates 比对 + page→feature 反向映射，对 spec/baseline/features/ 做枚举对账。当用户说"feature 覆盖率"、"漏功能"、"补 feature"、"feature 是不是齐了"、"看看 spec 功能全不全"、"这个 domain 是不是没成 feature"时触发。即使用户只说"对一下功能"或"feature-index 全不全",也应触发。
metadata:
  type: domain
  domain: migration
  tags:
  - domain
  - migration
  - audit
  - feature
  - coverage
---
# arkts-feature-coverage-auditor

## 1. 定位

Pipeline 中段的**强制审计步**，在 `a2h-spec` Phase C **Step C4.6b** 触发——紧跟 ui-coverage-auditor (Step C4.6) 之后、Step C4.7 Addenda 元数据收口之前；本 skill 不通过则**阻断 Step C5 人工审批 → a2h-plan**。在 `a2h-verify` 阶段也再跑一次做回归。

回答一个问题：**Android 项目里所有源码 domain / ref/spec 能力 / api-inventory 候选 / page 都被 spec/baseline/features/ 覆盖了吗？**

```
a2h-spec Phase C
  ├─ Step C4   生成 features/F*.md
  ├─ Step C4.5 ref 交叉验证
  ├─ Step C4.6  arkts-ui-coverage-auditor       ← UI 侧
  ├─ Step C4.6b arkts-feature-coverage-auditor（本 skill）★
  │              ↓
  │     [缺口报告] → 回 Step C2/C4 增量补 feature → 重跑本 skill（最多 2 轮）
  │              ↓
  │       第 3 轮仍 FAIL → 转 warning + 人工 override，写入 SESSION-HANDOFF.md
  ├─ Step C4.7 Addenda
  └─ Step C5   人工审批（HARD-GATE） → a2h-plan

a2h-execute → a2h-verify → arkts-feature-coverage-auditor（回归）→ a2h-retrospect
```

**为什么必须前置**：踩坑实证 —— 自由笔记 (project1) 现有 35 个 feature，但源码里**至少 7 个 domain 完全没成独立 feature**：
- `note_components/clock/` 8 文件（定时学习/番茄钟）→ 仅当成 setting 项被吞进 F022
- `note_components/layer/` 15 文件（笔记图层系统）→ 被误并入 F003 handwriting-canvas
- `note_components/outline/` 7 文件（大纲/目录）→ 被错归 F005 rich-text-editor
- `note_components/tag/` 12 文件（文档标签系统）→ 被错归 F006 folder-manager
- `note_components/bookmark/` 3 文件（PDF/笔记书签）→ 完全没人收
- `note_components/multi_window/` 6 文件（分屏多窗口）→ 仅 1 处提及
- `note_components/notesfilter/` 4 文件 → 仅 2 处零碎提及
- 加 ref/spec §5.22 跨端互通 + §5.23 调试与诊断 = 2 条 ref 契约能力没 feature

漏的根因：**Phase C 完全是 LLM 判断**，输入只有 3 个（ref/spec §5 + ui-manifest + api-inventory.json），**没有「源码 domain 子目录扫描」这第 4 个输入**。本 skill 在 spec 阶段就把缺口暴露出来，避免一路漏到 verify 才发现"业务能力没实现"。

---

## 2. 输入

| 来源 | 用途 |
|---|---|
| `$ANDROID_SRC/<module>/src/main/java\|kotlin/**/` | 源码包路径子目录枚举（L1 域覆盖） |
| `spec/ref/*_spec.md` §5 节标题 | ref 契约能力清单（L2 能力覆盖） |
| `spec/baseline/api-inventory/api-inventory.json` | `coverage.feature_candidates[]`（L3 候选覆盖） |
| `spec/baseline/ui-manifest.md` | 全 page 清单（L4 page→feature 反向映射） |
| `spec/baseline/feature-index.md` | 当前已生成 feature 总览（被审计对象） |
| `spec/baseline/features/F*.md` | 每个 feature 的主 spec（提取 android_source_anchors + 涉及页面） |
| `spec/toolkit-fact-tree.json`（可选） | reach_paths 字段做"建议合并"提示 |

如果 ref/spec 或 api-inventory 不存在，对应层降级为软审（warning 不阻断）。

### 启动校验 — Phase C 产物完整性检查

读取 `spec/baseline/feature-index.md` 后，检查：

| 检查项 | 判定 | 行动 |
|---|---|---|
| `feature-index.md` 不存在 | 🔴 PHASE_C_INCOMPLETE | 直接退出，建议先跑 a2h-spec Phase C |
| `features/F*.md` 数 < `feature-index.md` 列出的 ID 数 | 🟡 INCOMPLETE | 警告但继续，缺失项标 `missing_main_spec` |
| 所有 feature 都齐全 | ✅ PASS | 进入对账阶段 |

---

## 3. 输出

### 3.1 主报告 `spec/feature-coverage-report.md`

```markdown
# Feature 覆盖率审计

- 扫描时间：<ISO date>
- Android 源码模块数：<N>
- 源码 domain 子目录数（≥3 文件）：<D>
- spec/baseline/features/F*.md 数量：<M>
- ref/spec §5 能力数：<R>
- api-inventory feature_candidates 数：<A>
- ui-manifest 页面数：<P>

## 四层对账总览

| 维度 | 全量 | 已覆盖 | 缺失 | 覆盖率 | 阈值 | 状态 |
|---|---|---|---|---|---|---|
| L1 源码 domain | 28 | 21 | 7 | 75% | ≥85% | ❌ |
| L2 ref/spec §5 能力 | 23 | 21 | 2 | 91% | 100% | ❌ |
| L3 api-inventory 候选 | 13 | 13 | 0 | 100% | 100% | ✅ |
| L4 page→feature 反向 | 142 | 128 | 14 | 90% | ≥90% | ✅ |
| **总计** | **206** | **183** | **23** | **89%** | — | **❌ FAIL** |

## L1 缺失：源码 domain 没成 feature

| domain dir | 文件数 | 业务层信号 | 候选类型 | spec 中提及次数 | 建议 |
|---|---|---|---|---|---|
| `note_components/clock/` | 8 | ✓ ViewModel/Manager | 强候选 | 1 处 | 立即独立 feature F036-clock |
| `note_components/layer/` | 15 | ✓ ViewModel/Manager | 强候选 | 7 处 | 立即独立 feature F037-layer |
| `note_components/outline/` | 7 | ✓ ViewDelegate | 强候选 | 1 处 | 立即独立 feature F038-outline |
| `note_components/tag/` | 12 | ✓ ItemVO/DragHelper | 强候选 | 7 处 | 立即独立 feature F039-tag |
| `note_components/bookmark/` | 3 | — | 弱候选 | 0 | 可合并入 F018 pdf-reading-transfer |
| `note_components/multi_window/` | 6 | ✓ DisplayStateManager | 强候选 | 1 处 | 立即独立 feature F040-multi-window |
| `note_components/notesfilter/` | 4 | — | 中候选 | 2 处 | 合并入 F013 search 或独立 |

## L2 缺失：ref/spec §5 能力没 feature

| ref §x.y 节标题 | 当前归属 | 建议 |
|---|---|---|
| §5.22 跨端互通（iOS Continuity） | 无 | 立即独立 feature F041-cross-device |
| §5.23 调试与诊断 | 无 | 立即独立 feature F042-debug-diagnostic |

## L4 缺失：page 没归属 feature

| page_id | Activity/Fragment 名 | 涉及功能推断 | 建议归属 |
|---|---|---|---|
| page_0125_FDInkBeautifyPreviewWindow | InkBeautify 预览 | F019 ink-beautify 漏列 | 加入 F019 |
| ... | ... | ... | ... |

## 增量任务派发

见 `spec/feature-coverage-tasks.md`
```

### 3.2 增量任务清单 `spec/feature-coverage-tasks.md`

直接喂给 `a2h-spec`（增量模式）和 `a2h-plan`：

```markdown
## a2h-spec 增量任务

- [ ] 新建 features/F036-clock.md（来源：源码 note_components/clock/，8 文件 + 4 popup）
- [ ] 新建 features/F037-layer.md（来源：源码 note_components/layer/，15 文件）
- [ ] 新建 features/F038-outline.md（来源：源码 note_components/outline/）
- [ ] 新建 features/F041-cross-device.md（来源：ref/spec §5.22）
- [ ] 把 page_0125 加入 F019-ink-beautify 涉及页面
...

## a2h-plan 增量任务

- [ ] feature-plan.md 加 F036-F042 的 Base / Slice 步骤
- [ ] 重算依赖图 + 拓扑顺序
```

### 3.3 通过/失败信号

```text
阈值（按项目体量分档）:

  ≤30 features (小项目)：
    L1 源码 domain 覆盖率   ≥ 95%
    L2 ref/spec §5 覆盖率   = 100%
    L3 api 候选覆盖率       = 100%
    L4 page→feature 覆盖率  ≥ 95%

  >30 features (大项目)：
    L1 源码 domain 覆盖率   ≥ 85%
    L2 ref/spec §5 覆盖率   = 100% (ref 是契约，不分档)
    L3 api 候选覆盖率       = 100% (api 是契约，不分档)
    L4 page→feature 覆盖率  ≥ 90% (允许 page 出现在主+≤2 引用 feature)

失败时：
  - 首次失败 → 生成 feature-coverage-tasks.md，派发增量补 + 重跑（最多 2 轮）
  - 连续 3 轮仍失败 → 转 warning + 人工 override（写入 SESSION-HANDOFF.md）
  - 阻断 a2h-plan 直到通过或人工 override
```

---

## 4. 核心算法

### 4.1 L1 源码 domain 扫描

```pseudocode
1. ANDROID_SRC 下枚举模块：app, note_components, wsc_common, lib_*, ...
2. 对每个模块的 src/main/{java,kotlin}/<package_path>/ 子目录：
   - 子目录文件数 ≥ 3 → 候选 domain
   - 子目录名 ∈ 黑名单 → 排除：
     utils, util, common, base, di, ext, internal, widget,
     view, helper, kit, lib, core, infra, infrastructure
3. 业务层信号检测（强弱区分）：
   - 强信号：该 dir 下存在 *Presenter.kt / *ViewModel.kt / *Manager.kt / *Repository.kt
   - 中信号：存在 *Fragment.kt / *Activity.kt（UI 层但有独立 feature 可能）
   - 弱信号：仅有 *Util.kt / *Helper.kt / *Constants.kt → 大概率不构成 feature
4. 对每个候选：
   - 在 spec/baseline/features/F*.md 全文搜该 domain 名 + 该 dir 下任一类名
   - 命中 ≥1 feature 主 spec → 视为已覆盖
   - 命中 = 0 → 进缺失清单
   - 命中 = 1~2 次但内容仅"顺带提及" → 标记 `weak_coverage`
5. 关联强度判断（"建议合并"信号）：
   - 读 spec/toolkit-fact-tree.json（若存在），看该 domain 类的 reach_paths 是否大量穿越某现有 F0NN 的 page
   - 强穿越 → 建议合并到 F0NN
   - 无穿越 → 建议独立
```

### 4.2 L2 ref/spec §5 能力扫描

```pseudocode
1. 读 spec/ref/*_spec.md（typically notepad_spec.md），抽 §5.x 节标题
2. 对每条 §5.x：
   - 提取节标题关键词（"启动与首屏" / "云同步与备份" / 跨端互通"）
   - 在 feature-index.md 表格的"功能"列模糊匹配
   - 在 features/F*.md 主 spec 内容里模糊匹配
3. 命中 → 已覆盖；零命中 → 进缺失清单
4. ref 是契约，阈值 100%（不分项目体量）
```

### 4.3 L3 api-inventory 候选扫描

```pseudocode
1. 读 spec/baseline/api-inventory/api-inventory.json 的 coverage.feature_candidates[]
2. 对每个候选（如 suggested_id="F-pay"）：
   - 在 feature-index.md / features/F*.md 搜 suggested_id 字符串
   - 或在 features/F*.md 的 "## API 接口" 章节搜 path_prefixes 引用
3. 命中 → 已覆盖；零命中 → 进缺失清单
4. api 是契约，阈值 100%
5. api-inventory.json 不存在 → 软降级（warning 不阻断）
```

### 4.4 L4 page→feature 反向覆盖

```pseudocode
1. 读 spec/baseline/ui-manifest.md 抽全 page_id 集合
2. 对每个 page_id：
   - 在 feature-index.md 表格的"涉及页面"列搜
   - 在 features/F*.md 的"涉及 page"章节搜
3. 命中 ≥1 feature → 已覆盖
4. 命中 0 feature → 孤页（进缺失清单，建议归属）
5. 命中 ≥3 feature → 警告"page 被多 feature 共享，可能拆分过细"
```

### 4.5 L5 类→AC 完整性（可选，complex feature 强制 / simple 抽 30%）

```pseudocode
本层依赖 LLM 抽样，确定性脚本只产候选清单，由调用方派 sub-agent 走：

1. 对每个 features/F*.md：
   - 提取 android_source_anchors 中的类清单
   - 若 complexity=complex → 全量抽样核心方法名
   - 若 complexity=simple → 抽 30% 类
2. 对抽样到的方法名，在该 feature 的 "## 验收标准" 章节搜：
   - 方法名直接出现 → 已覆盖
   - 方法名语义对应（如 createNote() ↔ AC: "用户能创建笔记"）→ LLM 判定
3. 输出 sample_coverage 字段（百分比）
4. 默认不阻断 HARD-GATE，仅作为质量提示
```

---

## 5. 与 pipeline 的集成

### 触发时机

| 时机 | 行为 |
|---|---|
| `a2h-spec Phase C` 完成后 | 必跑；不通过则阻断 `a2h-plan` |
| `a2h-execute` 完成后 | 必跑；不通过则阻断 `a2h-verify` |
| 用户主动说「漏 feature/feature 覆盖率/feature 全不全」 | 立即跑增量审计 |
| `a2h-retrospect` 阶段 | 跑最终回归，作为本轮迁移的 KPI 写入回顾报告 |
| `spec-evolver` 增量演进 | **v1.0：跑全量**（`--incremental` 仍是 stub，传入会报错退出）。v1.1 计划实现"只审 git diff 新增 source dir + 新增 features/F*.md"。 |

### 修复回环（最多 2 轮）

```
本 skill 不通过
  ↓
生成 feature-coverage-tasks.md
  ↓
派发给 a2h-spec（增量模式）/ a2h-plan
  ↓
重跑本 skill
  ↓
仍不通过且已 2 轮 → 转 warning + 人工 override + 写入 SESSION-HANDOFF.md
```

### 与 ui-coverage-auditor 的独立关系

本 skill 与 `arkts-ui-coverage-auditor` 独立运行、各管一摊：

| | ui-coverage-auditor | feature-coverage-auditor |
|---|---|---|
| 审计对象 | page_*.md / .ets / main_pages.json | feature-index.md / features/F*.md |
| 数据源 | android-ui-graph (Screen.json) | 源码包路径 + ref/spec + api-inventory + ui-manifest |
| 触发关键词 | "漏页" / "UI 覆盖率" / "二三层 UI" | "漏 feature" / "feature 覆盖率" / "漏功能" |
| HARD-GATE | 阻断 a2h-plan | 阻断 a2h-plan |

两者都 PASS 才能进 a2h-plan。报告模板格式约定相同（frontmatter 字段一致），方便 a2h-plan 统一消费。

---

## 6. 边界

**做**：

- 4-5 层 feature 覆盖率统计 + 缺口清单 + 增量任务派发
- 黑名单 dir + 业务层信号判断 + reach_paths 关联强度提示

**不做**：

- 不生成 feature 主 spec 内容（这是 `a2h-spec` 增量模式的事）
- 不判断 feature 间依赖关系是否合理（那是 `a2h-plan` 的事）
- 不写 ArkTS 代码（这是 `a2h-execute` 的事）
- 不审计 page 内部 UI 元素（那是 `arkts-ui-coverage-auditor` 的事）

---

## 7. Failure Modes

| 现象 | 处理 |
|---|---|
| spec/baseline/features/ 不存在 | PHASE_C_INCOMPLETE，建议先跑 a2h-spec Phase C |
| ref/spec 不存在 | L2 软降级（warning 不阻断） |
| api-inventory.json 不存在或 `_mode != "candidate"` | L3 软降级 |
| 源码模块路径无法识别（非标准 Gradle 结构） | 用 `find . -name "src/main/java"` + `src/main/kotlin` fallback |
| 黑名单 dir 包含真实业务（项目特殊命名） | 报告中允许 `--whitelist <dir>` 命令行 override |
| 业务层信号判断错（Manager 类是工具类不是业务） | 信号是软提示，最终判断看 spec 是否提及；不直接判失败 |
| 连续 3 轮 HARD-GATE 失败 | 转 warning + 人工 override；写入 SESSION-HANDOFF.md 留痕 |
| 项目体量分档判断失误 | 默认按 features 数 ≤30/>30 分档；用户可 `--tier strict/lenient` 强制覆盖 |
