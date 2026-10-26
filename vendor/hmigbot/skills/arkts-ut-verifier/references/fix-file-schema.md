# `spec/verify/ut/round-N/ut/` 单问题文件 Schema

`spec/verify/ut/round-N/ut/` 下每个问题 markdown 的统一格式。`arkts-ut-test-executor` 按此 schema 写文件；`arkts-ut-fixer` 按此 schema 读文件。

## 一、目录布局

```
spec/verify/ut/
├── _state.yaml                    ← 全局状态（current_round / loop_status / max_rounds 等）
├── round-0/                       ← baseline = execute 首跑
│   ├── _ut_index.md               ← 本轮失败速览（人类，verifier 自动）
│   ├── _ut_summary.md             ← 本轮统计 + 维度表（verifier 自动）
│   ├── (round-0 不写 _delta)
│   └── ut/
│       └── F010_AC03_<slug>.md
├── round-1/                       ← fix loop 第 1 轮回跑
│   ├── 同上
│   ├── _ut_delta.md               ← 与 round-{N-1} 对比（round-1+ 才写）
│   ├── fixers/<WORK_ITEM_ID>.md    ← 每个 arkts-ut-fixer 独占的修复摘要
│   └── fixer-summary-ut.md        ← 主线程等待全部工作项完成后的统一汇总
└── round-2/ …
```

> `arkts-ui-verifier` 在自己的 `spec/verify/ui/` 下维护同构目录树，`arkts-visual-verify` 的差异文件在 `spec/fix/`；三个 verifier 目录完全独立，互不读写、无共享状态。

修复并发的文件所有权与汇总规则见 `references/fixer-dispatch.md`；fixer 不写全局摘要、不操作共享暂存区，也不修改问题文件的处置字段。

**核心不变性**：

- 文件存在 ⇔ 本轮该问题为 `RED/ERROR/IMPL_MISSING/UNREACHABLE`；方法 UT 的原始 GREEN 不会消除仍存在的接线问题，缺结果/缺依据且无法定 kind 的项另列未验证清单
- 旧 round 问题文件保留，不能删除文件或改写原始运行证据制造已解决。主线程可按当前源码和 Android 证据复核上一轮供派单文件，修正已失效的 kind/disposition 及分类依据后重派；fixer 不直接改问题文件，跨轮状态仍按稳定 ID 与本轮独立验证推导
- 同一问题跨轮的身份靠 **id**（文件名 = id + `.md`，1:1 互查）

## 二、文件名 = ID（确定性，跨轮稳定）

ID 推导：直接用 `<it_name>`（例：`F010_AC03_deleteFiles_useRecycleBin`）。

**铁律**：ID 不依赖时间戳/轮次/外部状态；文件名严格等于 ID + `.md`；同一轮内 ID 重复 → verifier 报错停下。

## 三、Frontmatter Schema

```yaml
---
# 标识
id: <文件名去掉 .md 后的 slug>
title: <一句话标题，≤ 60 字>

# 分类
source: arkts-ut-verifier
layer: ut
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
  - <日志/dump 路径，带行号锚点；如 /tmp/ut-run.log:1245>

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
| `title` | string | ≤ 60 字，便于 _ut_index.md 速览 |
| `source` | const | 固定 `arkts-ut-verifier` |
| `layer` | const | 固定 `ut` |
| `kind` | enum | 见 §四 |
| `severity` | enum | 从 spec priority 继承（P0/P1/P2） |
| `suggested_files` | list[string] | ≥ 1 条；fixer 用来定位，但不必盲信（fixer 自做诊断） |
| `related` | list[string] | 手工标注；fixer 不据此聚类 |
| `evidence` | list[string] | ≥ 1 条；日志/dump 或源码路径带行号。生产接线缺口须列真实调用位置与 Android 行为依据，方法 UT 已通过时保留原始日志，不伪造运行失败 |
| `disposition` | null \| enum | fix-loop 跨轮决策，见 §五 |
| `disposition_reason` | null \| string | disposition 非 null 时必填 |
| `disposition_set_at_round` | null \| int | disposition 非 null 时必填 |

## 四、`kind` 枚举（决定下游处理方式）

| 取值 | 含义 | `arkts-ut-fixer` 处理 |
|---|---|---|
| `RED` | 测试运行后断言失败 | ✅ 处理 |
| `ERROR` | 测试运行时报错（init 失败 / timeout / 编译跳过等） | 先区分根因；业务缺陷修生产代码，测试缺陷由获授权的 fixer 或测试阶段修测试，禁止生产兜底凑绿 |
| `IMPL_MISSING` | 范围内 Android 行为及批准差异已有证据，当前 ArkTS 缺少等价功能入口或必要生产接线 | ✅ fixer 按 Android 行为补齐能力、实际调用与结果消费，按需新增/更新测试；不能仅因缺 Spec 建议类名新增实现，见 `fixer-test-policy.md` 和 `fixer-wiring-policy.md` |
| `UNREACHABLE` | 本验证范围内无可执行入口/可观测结果，已排除前置条件和测试接线问题 | ❌ 不进入本轮自动修复；不计入分母，保留原因和未验证范围 |

## 五、`disposition` 跨轮决策

跨轮决策由 **fix-loop 主线程**写。测试质量、接线或旧分类问题默认保持开放，由对应 fixer/测试阶段修复；只有缺少行为依据、未裁决冲突或不可用外部前置时才写具体人工原因。fixer 只返回建议，不直接修改 disposition。因旧禁测规则而标人工的条目，主线程核实后清回 null 再派发。

mock 配置、Hypium 版本、测试 Context/fixture 或未命中桩导致的错误不等于业务未实现。共享基础设施交 executor，Feature 独占测试交获授权的 fixer/生成者；保持 `ERROR` 与测试侧修复建议，不因职责划分自动转人工。禁止扩大 mock 绕过焦点或新增生产 fallback。

| 取值 | 写入时机 | 含义 | 下轮 fixer 处理 |
|---|---|---|---|
| `null` | 默认 | 正常排队等修 | 正常评估 |
| `skipped` | 主线程发现 BLOCKER 后标 | 暂时降权 | 跳过本轮；下轮可清回 null 重试 |
| `manual_review` | 有证据的行为依据缺失、未裁决冲突或外部前置不可用 | 暂停该项自动修复，主线程核实原因解除后可清回 null | 清回前跳过，不代表通过 |

### carry forward 算法（verifier 写 round-N/ut/<id>.md 之前）

```pseudocode
prev_path = "spec/verify/ut/round-{N-1}/ut/{id}.md"
if exists(prev_path):
    prev = read(prev_path)
    if prev.disposition != null:
        new_file.disposition              = prev.disposition
        new_file.disposition_reason       = prev.disposition_reason
        new_file.disposition_set_at_round = prev.disposition_set_at_round
```

## 六、正文 5 个 Section（顺序固定，标题严格一致）

> **不写"历史尝试" section**：跨轮历史靠 round 目录序列承载（git diff + `fixer-summary.md` 已覆盖）。

```markdown
# {title}

## 1. Spec 引用
> 引用 spec/baseline/ 原文（≤ 5 行块引用）

来源: <spec/baseline/features/F00x.md §AC{n}> 或 <spec/baseline/ui/page_00xx.md §节标题>

## 2. 期望
<期望断言文本，如 `expect(x).assertEqual(y)`>

## 3. 实际
<运行返回值 / 错误首行>

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
| 2. 期望 | ✅ | ≤ 8 行 | 描述行为并附 Android 路径/符号/行号或已核验 oracle、批准差异引用；fixer 必须回读证据，不以描述代替源码 |
| 3. 实际 | ✅ | ≤ 8 行 | 已执行项引日志原文首行（≤ 160 字）；方法 GREEN 但必要接线仍缺时同时列源码缺口。未生成/未执行项写“未执行”并引用 generation 与当前源码/环境复核证据，不伪造失败日志 |
| 4. 源码缺口 | ✅ | 每行一条 | ≥ 1 条 `<file>:<line>`；行号未知写 `unknown` |
| 5. 修复建议 | ✅ | 步骤化 | ≥ 1 步；每步动词开头。**fixer 当 hypothesis，会自行 grep 验证**，不当金科玉律 |

## 七、`_ut_index.md` / `_ut_summary.md` / `_ut_delta.md`

verifier 每轮额外生成 3 个汇总文件（不参与 fixer 派单）：

### `_ut_index.md`（人类速览）

```markdown
# Round {N} ut 索引

> 生成时间：YYYY-MM-DDTHH:mm:ss+08:00

## ut 层（{count} 条）
- [F010_AC03 deleteFiles 必须支持 useRecycleBin](ut/F010_AC03_deleteFiles_useRecycleBin.md) [RED][P0]
- [F005_AC01 db init 失败](ut/F005_AC01_db_init.md) [ERROR][P0]
- ...
```

### `_ut_summary.md`（人类报告）

```markdown
# Round {N} ut 统计

> verifier: arkts-ut-verifier
> 跑测时间：YYYY-MM-DDTHH:mm:ss+08:00

## 总计

| 维度 | RED | ERROR | IMPL_MISSING | UNREACHABLE | 合计 |
|---|---|---|---|---|---|
| ut | x | x | x | x | x |

## Top 10（按 severity + suggested_files 触达广度排序）

1. [F005_AC01 db init 失败](ut/F005_AC01_db_init.md) — P0
2. ...

## 未变化项（与 round-{N-1} 比）

无变化的开放问题：{count}
```

### `_ut_delta.md`（round-1+ 每轮自动；round-0 不写）

完整模板见 `reconcile-rules.md §四`。

## 八、`_state.yaml`

```yaml
schema_version: 1
current_round: 3
last_verifier_run_at: 2026-05-24T15:23:11Z
last_verifier_source: arkts-ut-verifier
loop_status: running | paused | passed | converged | failed | stalled
max_rounds: 10
no_progress_rounds: 2
```

> `_state.yaml` 位于本 skill 私有的 `spec/verify/ut/` 根下，不与其它 verifier 共享——不存在并发覆盖问题。

`schema_version`：本 schema 不向后兼容地变更时递增；verifier 读到不认识的版本必须停下报错。

## 九、自检（verifier 写完每轮 round-N/ 后必跑）

```bash
ROUND_DIR="spec/verify/ut/round-${N}"

# 1. 文件名 = id（去 .md）
for f in $(find $ROUND_DIR/ut -name '*.md' -not -name '_*.md'); do
  id_in_fm=$(awk '/^id:/{print $2; exit}' $f)
  filename=$(basename $f .md)
  [[ "$id_in_fm" == "$filename" ]] || echo "❌ $f: id 与文件名不一致"
done

# 2. 必填字段齐全
for f in $(find $ROUND_DIR/ut -name '*.md' -not -name '_*.md'); do
  for field in id title source layer kind severity suggested_files evidence; do
    grep -q "^${field}:" $f || echo "❌ $f: 缺字段 $field"
  done
done

# 3. layer 固定 ut
grep -hE '^layer:' $ROUND_DIR/ut/*.md | grep -v 'layer: ut' && echo "❌ ut/ 下 layer 非 ut"

# 4. source 固定 arkts-ut-verifier
grep -hE '^source:' $ROUND_DIR/ut/*.md | grep -v 'source: arkts-ut-verifier' && echo "❌ source 非 arkts-ut-verifier"

# 5. kind 取值合法
grep -hE '^kind:' $ROUND_DIR/ut/*.md | grep -vE 'kind: (RED|ERROR|IMPL_MISSING|UNREACHABLE)' \
  && echo "❌ 非法 kind"

# 6. disposition 取值合法
awk '/^disposition:/{print $2}' $ROUND_DIR/ut/*.md | sort -u | \
  grep -vE '^(null|skipped|manual_review)$' && echo "❌ 非法 disposition"

# 7. 5 个 section 全部存在
for f in $(find $ROUND_DIR/ut -name '*.md' -not -name '_*.md'); do
  for sec in '## 1. Spec 引用' '## 2. 期望' '## 3. 实际' '## 4. 源码缺口' '## 5. 修复建议'; do
    grep -qF "$sec" $f || echo "❌ $f: 缺 section [$sec]"
  done
done
```

不通过的轮次产出视为不合格，必须修正后才能交给 fixer。按 executor §6.5 在同一轮自动修复自身产物并重验这 7 项及 reconcile 的 4 项，最多 2 次修复重验；保持原始运行证据、失败项、有效处置及轮号。涉及他人所有权或 disposition 时先交主线程协调。未知 schema、真实外部阻塞、需用户决策或重验仍失败才返回具体 BLOCKERS，不直接要求用户修复 executor 自己的格式/汇总错误。
