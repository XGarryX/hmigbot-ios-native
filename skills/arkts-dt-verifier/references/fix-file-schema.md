# `spec/fix/round-N/` 单问题文件 Schema

本文档定义 `spec/fix/` 下每个问题 markdown 文件的统一格式。**所有写入 `spec/fix/` 的 verifier**（dt-verifier、visual-verify、未来的任何 verifier）都必须遵循此 schema；**所有读取 `spec/fix/` 的消费者**（a2h-fixer agent、a2h-verify CHECK-7）都按此 schema 解析。

> **v2 简化（已应用）**：移除 SYSTEMIC kind 与 _systemic/ 子目录。每个失败 it() / 视觉差异都是一个独立文件，由 a2h-fixer 逐条独立诊断 + 修复。理由见 `agents/a2h-fixer.md §5`。

---

## 一、目录布局

```
spec/fix/
├── round-0/                        ← baseline（a2h-verify 首次 CHECK-7）
│   ├── _index.md                   ← 本轮所有问题清单（人类速览，verifier 自动生成）
│   ├── _summary.md                 ← 本轮统计（counts + 维度表，verifier 自动生成）
│   ├── _delta.md                   ← 与上一轮对比（round-0 不写，round-1+ 才写）
│   ├── feat/
│   │   ├── F001_AC01_<slug>.md     ← 单元测试 RED/ERROR
│   │   └── F010_AC03_<slug>.md
│   └── ui/
│       ├── P0010_UI_INTERACT_<slug>.md
│       ├── F010_UI_AC04_<slug>.md
│       └── ALIGN_P0002_<slug>.md   ← 视觉对齐问题
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

---

## 二、文件名 = ID（确定性、跨轮稳定）

| 来源 | ID 推导规则 | 例 |
|---|---|---|
| dt-verifier 单元测试 | `<it_name>` | `F010_AC03_deleteFiles_useRecycleBin` |
| dt-verifier UI 测试（页面派生） | `<it_name>` | `P0010_UI_INTERACT_row_open_dialog` |
| dt-verifier UI 测试（feature 派生） | `<it_name>` | `F010_UI_AC04_bookmarkRow_click` |
| visual-verify 视觉对齐 | `ALIGN_P<page_id>_<diff_kind>` | `ALIGN_P0002_color_drift` |

**铁律**：
- ID **不依赖**时间戳、轮次、外部状态
- 文件名严格等于 ID + `.md`，可 1:1 互查
- ID 唯一性必须保证；同一轮内重复 ID → verifier 报错停下

`<diff_kind>` 枚举（visual-verify 专用）：
- `layout_drift` — 布局位置/尺寸差异
- `color_mismatch` — 颜色/对比度差异
- `font_mismatch` — 字体大小/粗细差异
- `missing_element` — 期望出现的组件缺失
- `extra_element` — 期望不存在的组件出现
- `text_mismatch` — 文案与 spec 不符

---

## 三、Frontmatter Schema

每个文件的 YAML frontmatter **严格按以下顺序+字段**写：

```yaml
---
# 标识
id: <文件名去掉 .md 后的 slug>
title: <一句话标题，人类可读，≤ 60 字>

# 分类
source: <dt-verifier | visual-verify | manual>
layer: <feat | ui>
kind: <RED | ERROR | IMPL_MISSING | UNREACHABLE | ALIGNMENT_DIFF>
severity: <P0 | P1 | P2>
fixer_layer: <feat | ui>           # 派给哪类 fixer 写盘白名单

# 修复指引
suggested_files:
  - <仓内相对路径 1>
  - <仓内相对路径 2>

# 关联
related: []                         # 其他问题文件路径（手工标注；fixer 不依赖）

# 证据（至少 1 条）
evidence:
  - <日志/截图/dump 路径，带行号锚点；如 docs/autofix-log/round-1/raw-log.txt:1245>

# 跨轮持久决策（autofix 主线程写，verifier carry forward）
disposition: null                   # null | skipped | manual_review
disposition_reason: null            # 字符串，简述原因
disposition_set_at_round: null      # 整数，绝对轮次号
---
```

### 字段语义

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 文件名 slug，与文件名严格一致 |
| `title` | string | ≤ 60 字符，便于 _index.md 速览 |
| `source` | enum | 来源 verifier 工具名 |
| `layer` | enum | `feat` 或 `ui`；与目录路径一致 |
| `kind` | enum | 见下表 §四 |
| `severity` | enum | 从 spec priority 继承（P0/P1/P2） |
| `fixer_layer` | enum | 派单层（feat / ui），决定 fixer 写盘白名单 |
| `suggested_files` | list[string] | 至少 1 条；fixer 用此定位修改目标，但**不必盲信**（fixer 自带独立诊断） |
| `related` | list[string] | 手工标注的关联问题（如同源/同模块）；fixer 不据此聚类 |
| `evidence` | list[string] | 至少 1 条；日志路径带行号、截图路径、dump 路径等 |
| `disposition` | null \| enum | autofix 决策标记，见 §五 |
| `disposition_reason` | null \| string | disposition 非 null 时必填 |
| `disposition_set_at_round` | null \| int | disposition 非 null 时必填；绝对轮次号 |

> **v2 移除字段**：`systemic_root`、`affects`（已废除 SYSTEMIC 概念）

---

## 四、`kind` 枚举（决定下游处理方式）

| 取值 | 含义 | a2h-fixer 是否处理 |
|---|---|---|
| `RED` | 测试运行后断言失败 | ✅ 处理 |
| `ERROR` | 测试运行时报错（非断言失败，如 init 失败、timeout） | ✅ 处理 |
| `ALIGNMENT_DIFF` | visual-verify 检测到与 spec 截图的视觉差异 | ✅ 处理 |
| `IMPL_MISSING` | spec 描述了能力但实装/manifest 完全缺失（V2 deferred 占位） | ❌ 永久跳过；需人工产品决策 |
| `UNREACHABLE` | 测试体系结构性不可达（外部 Intent / Tab 子页 / Dialog-only 等） | ❌ 永久跳过；不计入分母 |

> **v2 移除枚举值**：`SYSTEMIC`（已废除聚类概念）

---

## 五、`disposition` 状态字段

跨轮持久决策。**只有 a2h-verify CHECK-7 主线程能写**；verifier 在 carry forward 时尊重它，fixer 必须读它来决定是否跳过。

| 取值 | 写入时机 | 含义 | 下轮 fixer 处理 |
|---|---|---|---|
| `null` | 默认 | 正常排队等修 | 正常评估 |
| `skipped` | 主线程发现 BLOCKER 后标 | 暂时降权 | 跳过本轮，下轮可清回 null 重试 |
| `manual_review` | 修复需要人工介入（SDK 不支持 / REGRESSED 自动标）| 永久跳过自动修 | 直接跳过 |

> **v2 移除取值**：`problematic`（旧版回滚后标，新版无回滚故无此用途）

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

> **不写"历史尝试"section**：跨轮历史靠 round 目录序列承载（git diff round-N round-N+1 + `docs/autofix-log/round-N/fixer-summary.md` 已经覆盖），无需在每个问题文件里维护表格。

```markdown
# {title}

## 1. Spec 引用
> 引用 spec/baseline/ 原文（≤ 5 行块引用）

来源: <spec/baseline/features/F00x.md §AC{n}> 或 <spec/baseline/ui/page_00xx.md §节标题>

## 2. 期望
<期望行为或视觉，自由文本；dt 写断言文本，visual 写颜色/尺寸/视觉描述>

## 3. 实际
<实际行为或视觉；dt 写运行返回值/错误首行，visual 写截图差异描述>

## 4. 源码缺口
- <仓内相对路径>:<行号> — <一句话描述缺口>
- <仓内相对路径>:<行号> — ...

（行号未知写 `unknown`；至少给到文件路径）

## 5. 修复建议
1. <步骤 1：动词开头，具体到方法名 / 资源 key / 组件类型>
2. <步骤 2>
3. ...
```

### Section 写法约束

| Section | 必填 | 长度上限 | 写法约束 |
|---|---|---|---|
| 1. Spec 引用 | ✅ | ≤ 5 行块引用 | **原文直引**，不得意译；末尾标 `来源:` 路径 |
| 2. 期望 | ✅ | ≤ 8 行 | 自由文本，能让 fixer 不读 spec 也能理解 |
| 3. 实际 | ✅ | ≤ 8 行 | dt 引日志原文首行（≤ 160 字）；visual 引截图差异关键点 |
| 4. 源码缺口 | ✅ | 每行一条 | 至少 1 条 `<file>:<line>` 定位；行号未知写 `unknown` |
| 5. 修复建议 | ✅ | 步骤化 | 至少 1 步；每步动词开头。**fixer 把它当 hypothesis，不是金科玉律**——会自行 grep 验证 |

---

## 七、`_index.md` 与 `_summary.md` 与 `_delta.md`

verifier 每轮额外生成 3 个汇总文件（不是问题文件，不参与 fixer 派单）：

### `_index.md`（人类速览，每轮新生成）

```markdown
# Round {N} 索引

> 生成时间：YYYY-MM-DDTHH:mm:ss+08:00

## Feature 层（{count} 条）
- [F010_AC03 deleteFiles 必须支持 useRecycleBin 分支](feat/F010_AC03_deleteFiles_useRecycleBin.md) [RED][P0]
- [F005_AC01 db init 失败](feat/F005_AC01_db_init.md) [ERROR][P0]
- ...

## UI 层（{count} 条）
- [P0010 设置页 row 点击 Dialog](ui/P0010_UI_INTERACT_row_open_dialog.md) [ERROR][P0]
- [ALIGN P0002 主页深色背景偏亮](ui/ALIGN_P0002_color_drift.md) [ALIGNMENT_DIFF][P1]
- ...
```

### `_summary.md`（人类报告，每轮新生成）

```markdown
# Round {N} 统计

> verifier: dt-verifier + visual-verify
> 跑测时间：YYYY-MM-DDTHH:mm:ss+08:00

## 总计

| 维度 | RED | ERROR | ALIGN | IMPL_MISSING | UNREACHABLE | 合计 |
|---|---|---|---|---|---|---|
| feat | x | x | - | x | - | x |
| ui   | x | x | x | x | x | x |

## Top 10（按 severity + suggested_files 触达广度排序）

1. [F005_AC01 db init 失败](feat/F005_AC01_db_init.md) — P0, severity=高
2. ...

## 未变化项（与 round-{N-1} 比）

无变化的开放问题：{count}
```

### `_delta.md`（每轮 verifier 自动生成，round-0 不写）

完整模板见 `reconcile-rules.md §四`。

---

## 八、`_state.yaml`（项目根全局状态）

```yaml
schema_version: 2                # v2: 移除 SYSTEMIC 与 problematic disposition
current_round: 3
last_verifier_run_at: 2026-05-06T15:23:11Z
last_verifier_sources: [dt-verifier, visual-verify]
last_autofix_round: 3
target_green_ratio: 1.0
max_rounds: 10
```

`schema_version` 字段：当本 schema 不向后兼容地变更时递增，verifier 读到不认识的版本必须停下报错。

> **v2 升级**：旧 schema_version=1 的 round 目录可能含 `_systemic/` 子目录与 `kind: SYSTEMIC` 文件，新 verifier 读到时应跳过这些文件并 warning（向前兼容）。

---

## 九、自检（verifier 写完每轮 round-N/ 后必跑）

```bash
ROUND_DIR="spec/fix/round-${N}"

# 1. 文件名 = id（去 .md）
for f in $(find $ROUND_DIR -name '*.md' -not -name '_*.md'); do
  id_in_fm=$(awk '/^id:/{print $2; exit}' $f)
  filename=$(basename $f .md)
  [[ "$id_in_fm" == "$filename" ]] || echo "❌ $f: id 与文件名不一致"
done

# 2. 必填字段齐全（注意：移除了 systemic_root / affects）
for f in $(find $ROUND_DIR -name '*.md' -not -name '_*.md'); do
  for field in id title source layer kind severity fixer_layer suggested_files evidence; do
    grep -q "^${field}:" $f || echo "❌ $f: 缺字段 $field"
  done
done

# 3. fixer_layer 取值合法
grep -hE '^fixer_layer:' $ROUND_DIR/**/*.md | grep -vE 'fixer_layer: (feat|ui)' && echo "❌ 非法 fixer_layer"

# 4. kind 取值合法（注意：移除了 SYSTEMIC）
grep -hE '^kind:' $ROUND_DIR/**/*.md | grep -vE 'kind: (RED|ERROR|IMPL_MISSING|UNREACHABLE|ALIGNMENT_DIFF)' \
  && echo "❌ 非法 kind 值（v2 已移除 SYSTEMIC）"

# 5. disposition 取值合法（注意：移除了 problematic）
awk '/^disposition:/{print $2}' $ROUND_DIR/**/*.md | sort -u | \
  grep -vE '^(null|skipped|manual_review)$' && echo "❌ 非法 disposition 值（v2 已移除 problematic）"

# 6. 5 个 section 全部存在
for f in $(find $ROUND_DIR -name '*.md' -not -name '_*.md'); do
  for sec in '## 1. Spec 引用' '## 2. 期望' '## 3. 实际' '## 4. 源码缺口' '## 5. 修复建议'; do
    grep -qF "$sec" $f || echo "❌ $f: 缺 section [$sec]"
  done
done

# 7. 不应有 _systemic/ 子目录（v2 废除）
find $ROUND_DIR -type d -name '_systemic' && echo "⚠️ 检测到 _systemic/ 子目录（v2 已废除，verifier 不应再生成）"
```

不通过的轮次产出视为不合格，必须修正后才能交给 fixer。
