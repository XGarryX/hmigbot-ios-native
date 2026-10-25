# `spec/fix/round-N/ui/` 单问题文件 Schema

`spec/fix/round-N/ui/` 下每个问题 markdown 的统一格式。**arkts-ui-verifier 的 execute 阶段**按此 schema 写文件；**spec-fixer-ui agent** 按此 schema 读文件。

## 一、目录布局

```
spec/fix/
├── _state.yaml                    ← 全局状态（current_round / loop_status / max_rounds 等）
├── round-0/                       ← baseline = execute 首跑
│   ├── _ui_index.md               ← 本轮失败速览（人类，verifier 自动）
│   ├── _ui_summary.md             ← 本轮统计 + 维度表（verifier 自动）
│   ├── (round-0 不写 _delta)
│   └── ui/
│       ├── P0010_UI_INTERACT_<slug>.md      ← 页面派生 UI 测试
│       └── F010_UI_AC04_<slug>.md           ← feature 派生 UI 测试
├── round-1/                       ← fix loop 第 1 轮回跑
│   ├── 同上
│   ├── _ui_delta.md               ← 与 round-{N-1} 对比（round-1+ 才写）
│   └── fixer-summary-ui.md        ← 本轮 fixer 的 EDITED / SKIPPED
└── round-2/ …
```

> 若同项目并行跑 `arkts-ut-verifier`，它会在 `round-N/` 下并列写 `ut/` 子目录 + `_ut_*` 汇总；本 schema 不涉及，两 skill 互不踩。

**核心不变性**：

- 文件存在 ⇔ 本轮该问题为 `RED/ERROR/IMPL_MISSING`（GREEN 不写文件）
- 文件**只增不删**：旧 round 目录保留不动，跨轮状态从目录序列推导
- 同一问题跨轮的身份靠 **id**（文件名 = id + `.md`，1:1 互查）

## 二、文件名 = ID（确定性，跨轮稳定）

| 来源 | ID 推导 | 例 |
|---|---|---|
| 页面派生 UI 测试 | `<it_name>` | `P0010_UI_INTERACT_row_open_dialog` |
| feature 派生 UI 测试 | `<it_name>` | `F010_UI_AC04_bookmarkRow_click` |

**铁律**：ID 不依赖时间戳/轮次/外部状态；文件名严格等于 ID + `.md`；同一轮内 ID 重复 → verifier 报错停下。

## 三、Frontmatter Schema

```yaml
---
# 标识
id: <文件名去掉 .md 后的 slug>
title: <一句话标题，≤ 60 字>

# 分类
source: arkts-ui-verifier
layer: ui
kind: <RED | ERROR | IMPL_MISSING | UNREACHABLE>
severity: <P0 | P1 | P2>

# 修复指引
suggested_files:
  - <仓内相对路径 1>
  - <仓内相对路径 2>

# 关联（手工标注；fixer 不依赖）
related: []

# 证据（至少 1 条）
evidence:
  - <日志/dump 路径，带行号锚点；如 /tmp/ui-run.log:3422>

# 跨轮持久决策（fix-loop 主线程写，verifier carry forward 保留）
disposition: null                   # null | skipped | manual_review
disposition_reason: null
disposition_set_at_round: null      # 整数，绝对轮次号
---
```

### 字段语义

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string | 文件名 slug，与文件名严格一致 |
| `title` | string | ≤ 60 字，便于 _ui_index.md 速览 |
| `source` | const | 固定 `arkts-ui-verifier` |
| `layer` | const | 固定 `ui` |
| `kind` | enum | 见 §四 |
| `severity` | enum | 从 spec priority 继承（P0/P1/P2） |
| `suggested_files` | list[string] | ≥ 1 条；fixer 用来定位，但不必盲信（fixer 自做诊断） |
| `related` | list[string] | 手工标注；fixer 不据此聚类 |
| `evidence` | list[string] | ≥ 1 条；日志/dump 路径带行号 |
| `disposition` | null \| enum | fix-loop 跨轮决策，见 §五 |
| `disposition_reason` | null \| string | disposition 非 null 时必填 |
| `disposition_set_at_round` | null \| int | disposition 非 null 时必填 |

## 四、`kind` 枚举（决定下游处理方式）

| 取值 | 含义 | spec-fixer-ui 处理 |
|---|---|---|
| `RED` | UI 测试运行后断言失败（意图层或状态层任一失败） | ✅ 处理 |
| `ERROR` | UI 测试运行时报错（landmark 缺失 / Driver init / timeout / 编译跳过等） | ✅ 处理 |
| `IMPL_MISSING` | spec 描述了组件/页面但实装完全缺失 | ❌ 永久跳过；需人工产品决策 |
| `UNREACHABLE` | UI 测试结构性不可达（外部 Intent / Tab 子页 / Dialog-only / FormExtension 等） | ❌ 永久跳过；不计入分母 |

## 五、`disposition` 跨轮决策

只有 **fix-loop 主线程**能写；verifier carry forward 时尊重，fixer 必须读它决定是否跳过。

| 取值 | 写入时机 | 含义 | 下轮 fixer 处理 |
|---|---|---|---|
| `null` | 默认 | 正常排队等修 | 正常评估 |
| `skipped` | 主线程发现 BLOCKER 后标 | 暂时降权 | 跳过本轮；下轮可清回 null 重试 |
| `manual_review` | 修复需人工（SDK 不支持 / REGRESSED 自动标）| 永久跳过自动修 | 直接跳过 |

### carry forward 算法（verifier 写 round-N/ui/<id>.md 之前）

```pseudocode
prev_path = "spec/fix/round-{N-1}/ui/{id}.md"
if exists(prev_path):
    prev = read(prev_path)
    if prev.disposition != null:
        new_file.disposition              = prev.disposition
        new_file.disposition_reason       = prev.disposition_reason
        new_file.disposition_set_at_round = prev.disposition_set_at_round
```

## 六、正文 5 个 Section（顺序固定，标题严格一致）

> **不写"历史尝试" section**：跨轮历史靠 round 目录序列承载（git diff + `fixer-summary-ui.md` 已覆盖）。

```markdown
# {title}

## 1. Spec 引用
> 引用 spec/baseline/ 原文（≤ 5 行块引用）

来源: <spec/baseline/ui/page_00xx.md §节标题> 或 <spec/baseline/features/F00x.md §AC{n}>

## 2. 期望
- **意图层**：定位控件 + 断言特征 (`assertComponentExist(ON.id(...))` / `getText()==...` / `isChecked()==...`)
- **状态层**：`AppStorage.get<T>('key')==value` 或 `@State` 绑定值

## 3. 实际
- 意图层：定位失败 / 控件特征实际值
- 状态层：`AppStorage.get('key')` 实测值（含 `undefined` 表示 key 都没建）

## 4. 源码缺口
- <仓内相对路径>:<行号> — <一句话描述缺口>
- <仓内相对路径>:<行号> — ...

（行号未知写 `unknown`；至少给到文件路径）

## 5. 修复建议
1. <步骤 1：动词开头，具体到方法名 / 资源 key / 组件类型 / AppStorage key>
2. <步骤 2>
3. ...
```

### Section 写法约束

| Section | 必填 | 长度上限 | 写法约束 |
|---|---|---|---|
| 1. Spec 引用 | ✅ | ≤ 5 行块引用 | **原文直引**，不得意译；末尾标 `来源:` 路径 |
| 2. 期望 | ✅ | ≤ 8 行 | **意图层 + 状态层两行**（双重断言，与 test-design-template 标准 3 一致）；纯渲染无对应状态键 → 备注"仅意图层 + 原因" |
| 3. 实际 | ✅ | ≤ 8 行 | 意图层引日志原文首行（≤ 160 字）+ 状态层 AppStorage 实测值 |
| 4. 源码缺口 | ✅ | 每行一条 | ≥ 1 条 `<file>:<line>`；行号未知写 `unknown`；含缺 onClick / AppStorage 状态键 / `.id()` 锚点等 |
| 5. 修复建议 | ✅ | 步骤化 | ≥ 1 步；每步动词开头。**fixer 当 hypothesis，会自行 grep 验证**，不当金科玉律 |

## 七、`_ui_index.md` / `_ui_summary.md` / `_ui_delta.md`

verifier 每轮额外生成 3 个汇总文件（不参与 fixer 派单）：

### `_ui_index.md`（人类速览）

```markdown
# Round {N} ui 索引

> 生成时间：YYYY-MM-DDTHH:mm:ss+08:00

## ui 层（{count} 条）
- [P0010 设置页 row 点击 Dialog](ui/P0010_UI_INTERACT_row_open_dialog.md) [ERROR][P0]
- [F010_UI_AC04 收藏行点击](ui/F010_UI_AC04_bookmarkRow_click.md) [RED][P0]
- ...
```

### `_ui_summary.md`（人类报告）

```markdown
# Round {N} ui 统计

> verifier: arkts-ui-verifier
> 跑测时间：YYYY-MM-DDTHH:mm:ss+08:00

## 总计

| 维度 | RED | ERROR | IMPL_MISSING | UNREACHABLE | 合计 |
|---|---|---|---|---|---|
| ui | x | x | x | x | x |

## 双重断言失败分布

| 类型 | 计数 |
|---|---|
| 仅意图层失败 | x |
| 仅状态层失败 | x |
| 两层都失败   | x |

## Top 10（按 severity + suggested_files 触达广度排序）

1. [P0010 设置页 row 点击 Dialog](ui/P0010_UI_INTERACT_row_open_dialog.md) — P0
2. ...

## 未变化项（与 round-{N-1} 比）

无变化的开放问题：{count}
```

### `_ui_delta.md`（round-1+ 每轮自动；round-0 不写）

完整模板见 `reconcile-rules.md §四`。

## 八、`_state.yaml`

```yaml
schema_version: 1
current_round: 3
last_verifier_run_at: 2026-05-24T15:23:11Z
last_verifier_source: arkts-ui-verifier
loop_status: running | paused | passed | failed | stalled
max_rounds: 10
no_progress_rounds: 2
```

`schema_version`：本 schema 不向后兼容地变更时递增；verifier 读到不认识的版本必须停下报错。

> 若同项目并行跑 `arkts-ut-verifier`，`last_verifier_source` 字段会被各 skill 互相覆盖（最后写者胜出）；不影响 round 推进。

## 九、自检（verifier 写完每轮 round-N/ 后必跑）

```bash
ROUND_DIR="spec/fix/round-${N}"

# 1. 文件名 = id（去 .md）
for f in $(find $ROUND_DIR/ui -name '*.md' -not -name '_*.md'); do
  id_in_fm=$(awk '/^id:/{print $2; exit}' $f)
  filename=$(basename $f .md)
  [[ "$id_in_fm" == "$filename" ]] || echo "❌ $f: id 与文件名不一致"
done

# 2. 必填字段齐全
for f in $(find $ROUND_DIR/ui -name '*.md' -not -name '_*.md'); do
  for field in id title source layer kind severity suggested_files evidence; do
    grep -q "^${field}:" $f || echo "❌ $f: 缺字段 $field"
  done
done

# 3. layer 固定 ui
grep -hE '^layer:' $ROUND_DIR/ui/*.md | grep -v 'layer: ui' && echo "❌ ui/ 下 layer 非 ui"

# 4. source 固定 arkts-ui-verifier
grep -hE '^source:' $ROUND_DIR/ui/*.md | grep -v 'source: arkts-ui-verifier' && echo "❌ source 非 arkts-ui-verifier"

# 5. kind 取值合法
grep -hE '^kind:' $ROUND_DIR/ui/*.md | grep -vE 'kind: (RED|ERROR|IMPL_MISSING|UNREACHABLE)' \
  && echo "❌ 非法 kind"

# 6. disposition 取值合法
awk '/^disposition:/{print $2}' $ROUND_DIR/ui/*.md | sort -u | \
  grep -vE '^(null|skipped|manual_review)$' && echo "❌ 非法 disposition"

# 7. 5 个 section 全部存在
for f in $(find $ROUND_DIR/ui -name '*.md' -not -name '_*.md'); do
  for sec in '## 1. Spec 引用' '## 2. 期望' '## 3. 实际' '## 4. 源码缺口' '## 5. 修复建议'; do
    grep -qF "$sec" $f || echo "❌ $f: 缺 section [$sec]"
  done
done
```

不通过的轮次产出视为不合格，必须修正后才能交给 fixer。
