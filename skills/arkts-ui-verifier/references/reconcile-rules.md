# Reconciliation 算法（跨轮状态推导）

`arkts-ui-verifier` 的 execute 步骤每轮跑完后，通过比较 `spec/fix/round-{N-1}/ui/` 与本轮 runtime 结果，写出 `spec/fix/round-N/ui/` + `_ui_delta.md`，并保证状态语义正确。

**角色**：ui-verifier execute 步骤的"权威算法"。**依赖**：`fix-file-schema.md`（文件结构）。

## 一、核心命名约定

- 一个**问题** = 一个 ID（确定性，跨轮稳定）
- 一个**文件** = `spec/fix/round-N/ui/<id>.md`
- **文件存在** = 该轮该问题处于 RED / ERROR 之一（含双重断言任一层失败）
- **文件不存在** ∧ **测试套件仍含此 it()** = 该轮 GREEN（两层都通过）
- **文件不存在** ∧ **测试套件不含此 it()** = stale（spec/测试已删此条）

## 二、状态推导表（不依赖 frontmatter）

某 ID 在 round-N 的状态 = `round-(N-1)` 与本轮 runtime 的存在性组合：

| round-(N-1) 文件 | round-N runtime | 推导状态 | round-N/ 是否写文件 | 备注 |
|---|---|---|---|---|
| 不存在 | GREEN | `still_green` | 否 | 不关心 |
| 不存在 | RED / ERROR | `newly_open` | ✅ 新建 | created_round 隐含 = N |
| 存在 | GREEN | `fixed` | 否 | round-N/ 缺该文件 = fixed 信号 |
| 存在 | RED / ERROR | `still_failing` | ✅ carry forward 写 | disposition 必须 carry |
| 存在 | 不在 runtime 中 | `stale` 候选 | 否 | 进一步在 `_delta.md` 区分 |

**回归（regression）检测**：扫历史轮看模式

```
∃ K ≤ N-2: round-K ∋ id ∧ round-(K+1) ∌ id ∧ ... ∧ round-(N-1) ∌ id ∧ round-N ∋ id
```

即：上次 fixed 之后又再次出现 → 这是回归。`_ui_delta.md` 把这种 ID 标 `regressed`。

> **不回滚**：fix-loop 主线程拿到 REGRESSED 列表后，给每个 ID 自动写 `disposition: manual_review` 让下轮 fixer 跳过（防来回反复），但**不 git reset**。本轮其它 RESOLVED 的进展保留。原因：回滚的损失大于收益；fixer 应通过反向 impact 自检 + 保留向后兼容来主动防回归。

## 三、carry forward 算法（写 round-N/ui/<id>.md 之前）

```pseudocode
def write_problem_file(round_N: int, id: str, current_run_data: dict):
    new_file_path  = f"spec/fix/round-{round_N}/ui/{id}.md"
    prev_file_path = f"spec/fix/round-{round_N - 1}/ui/{id}.md"

    # 1. 准备新 frontmatter（默认值 + 当轮数据）
    fm = {
        "id":               id,
        "title":            current_run_data["title"],
        "source":           "arkts-ui-verifier",
        "layer":            "ui",
        "kind":             current_run_data["kind"],         # RED | ERROR | IMPL_MISSING | UNREACHABLE
        "severity":         current_run_data["severity"],
        "suggested_files":  current_run_data["suggested_files"],
        "related":          [],
        "evidence":         current_run_data["evidence"],
        "disposition":              None,
        "disposition_reason":       None,
        "disposition_set_at_round": None,
    }

    # 2. carry forward disposition + related（即使本轮重算）
    if exists(prev_file_path):
        prev_fm = parse_frontmatter(prev_file_path)
        if prev_fm.get("disposition") is not None:
            fm["disposition"]              = prev_fm["disposition"]
            fm["disposition_reason"]       = prev_fm["disposition_reason"]
            fm["disposition_set_at_round"] = prev_fm["disposition_set_at_round"]
        if prev_fm.get("related"):
            fm["related"] = prev_fm["related"]

    # 3. 拼正文（5 sections，无历史尝试）
    body = render_sections(current_run_data)

    write_file(new_file_path, frontmatter_to_yaml(fm) + body)
```

### 关键不变式

1. **disposition 永不丢失**：除非 fix-loop 主线程显式清空（设为 null），否则一直 carry forward
2. **suggested_files 每轮重算**：本轮 verifier 的最新分析为权威（spec 改 / 源码改 → 缺口位置可能变）
3. **kind / severity 每轮重算**：本轮 runtime 是权威（如 ERROR 修成 RED 也要更新）
4. **不维护历史尝试表**：跨轮历史靠 round 目录序列 + `fixer-summary-ui.md` 承载
5. **双重断言失败合并为一个文件**：意图层 / 状态层任一失败都视为该 it() 失败，写一份文件，「期望」「实际」两 section 同时记两层（见 `fix-file-template.md §示例`）

## 四、`_ui_delta.md` 生成算法

每轮（round-1 起）verifier 写完 `round-N/ui/` 所有 .md 后，立即生成 `round-N/_ui_delta.md`。

```pseudocode
def gen_delta(round_N: int):
    prev_dir = f"spec/fix/round-{round_N - 1}/ui"
    curr_dir = f"spec/fix/round-{round_N}/ui"

    prev_ids = scan_problem_files(prev_dir)
    curr_ids = scan_problem_files(curr_dir)

    resolved      = prev_ids - curr_ids
    newly_open    = curr_ids - prev_ids
    still_failing = prev_ids ∩ curr_ids

    # newly_open 区分"全新"vs"回归"
    truly_new, regressed = [], []
    for id in newly_open:
        if appears_in_any_round(id, range(0, round_N - 1)):
            regressed.append(id)   # 历史上 fixed 过又出现
        else:
            truly_new.append(id)

    # resolved 区分"真 fixed"vs"stale"
    fixed, stale = [], []
    test_names_now = parse_current_test_suite_it_names()
    for id in resolved:
        if id not in test_names_now:
            stale.append(id)   # spec 改 / 测试删 → it() 不再存在
        else:
            fixed.append(id)

    write_delta_md(round_N, fixed, stale, regressed, truly_new, still_failing)
```

### `_ui_delta.md` 模板

```markdown
# Round {N} ui delta（vs round-{N-1}）

> 生成时间：YYYY-MM-DDTHH:mm:ss+08:00
> verifier source: arkts-ui-verifier
> 设备：<device_id> bundle: <bundle>
> aa test 原始汇总: `Tests run: N, Failure: F, Error: E, Pass: P, Ignore: I`

## ✅ Resolved（fixed，{count}）

上轮失败、本轮 GREEN（意图层 + 状态层都过）：

- P0007_UI_NAV_drawer_swipe
- F010_UI_AC04_bookmarkRow_click
- ...

## 🆕 Newly opened（首次出现，{count}）

历史上没出现过的新 RED/ERROR：

- P0008_UI_INTERACT_share_btn     ← 之前 SKIP 过 / 设备问题没跑到
- ...

## 🚨 Regressed（回归，{count}）⚠️ 自动 mark manual_review，不回滚

历史轮次中 fixed 过、本轮再次失败：

- P0010_UI_INTERACT_row_open_dialog   ← 在 round-2 fixed，本轮 round-{N} 再次失败
  上次 fixed 时 commit: <sha>（见 fixer-summary-ui.md）
  本轮自动标 disposition: manual_review（需人工排查 fix 的副作用 / 是否动了 AppStorage key）

## 🪦 Stale（{count}）

文件不再出现且测试已不在当前套件（spec/测试架构变了）：

- P0099_UI_legacy_xxx   ← 页面 Spec 被删

## 🔁 Still failing（仍未修复，{count}）

- 折叠列出 ID（点击 round-{N}/ui/<id>.md 查看详情）

## 计数变化

| 维度 | round-{N-1} | round-{N} | Δ |
|---|---|---|---|
| ui 失败数 | x | x | ±x |
| disposition=manual_review | x | x | ±x |
| disposition=skipped | x | x | ±x |
```

## 五、edge case 处理表

| 情形 | 处理 |
|---|---|
| **同一轮 verifier 跑两次**（设备闪退重跑） | 第二次完全覆盖第一次的 round-N/ui/；不改 round 号 |
| **用户手动改了 round-N/ui/<id>.md** | 下轮 verifier carry forward 时尊重用户改动（仅限 disposition / related 字段） |
| **verifier SKIP 了某 it()**（编译失败 / timeout / daemon 死） | 该 it() 不计入本轮 runtime；若上轮该文件存在 → carry forward 全文件，§3 实际写"本轮 SKIPPED_<原因>" |
| **spec 改名了**（P0010_UI_INTERACT_x → _y） | 老 ID 文件本轮 stale；新 ID 创建新文件 |
| **测试套件结构变** | 不影响 reconcile，照常按 ID 比对 |
| **round-(N-1)/ 不存在**（首次跑） | 跳过 carry forward 步骤，直接按 newly_open 写所有失败 |
| **意图层过 + 状态层挂**（onClick 修了但忘记 AppStorage.setOrCreate） | 仍判 RED，写一份文件，「实际」标"意图层 GREEN / 状态层 FAIL"明示 |

## 六、`_state.yaml` 维护

每轮 verifier 完成后，主线程更新 `_state.yaml`：

```yaml
schema_version: 1
current_round: <N>
last_verifier_run_at: <ISO 时间戳>
last_verifier_source: arkts-ui-verifier
loop_status: running | paused | passed | failed | stalled
max_rounds: 10
no_progress_rounds: 2
```

更新规则：
- verifier 首跑（baseline）→ 写 `current_round: 0`
- fix-loop 调度 verifier 重跑 → `current_round = N+1`
- verifier 不要自己推断 round 号；主线程显式传 `ROUND` 参数

> 若同项目并行跑 `arkts-ut-verifier`，`last_verifier_source` 字段会被各 skill 互相覆盖（最后写者胜出）；不影响 round 推进。

## 七、自检（verifier 完成 reconcile 后必跑）

```bash
N=<本轮号>
ROUND_DIR="spec/fix/round-$N"
PREV_DIR="spec/fix/round-$((N-1))"

# 1. round 目录已建
test -d $ROUND_DIR/ui || mkdir -p $ROUND_DIR/ui

# 2. 汇总文件齐全
for f in _ui_index.md _ui_summary.md; do
  test -f $ROUND_DIR/$f || echo "❌ 缺 $ROUND_DIR/$f"
done
# round-0 不写 _delta，round-1+ 必写
[[ $N -ge 1 ]] && { test -f $ROUND_DIR/_ui_delta.md || echo "❌ round-$N 缺 _ui_delta.md"; }

# 3. carry forward 检查：上轮所有有 disposition 的文件，本轮如果还失败必须 carry
if [[ -d $PREV_DIR/ui ]]; then
  for f in $(find $PREV_DIR/ui -name '*.md' -not -name '_*.md'); do
    id=$(basename $f .md)
    new_f=$ROUND_DIR/ui/$id.md
    if [[ -f $new_f ]]; then
      prev_disp=$(awk '/^disposition:/{print $2; exit}' $f)
      new_disp=$(awk '/^disposition:/{print $2; exit}' $new_f)
      if [[ "$prev_disp" != "null" && "$prev_disp" != "$new_disp" ]]; then
        echo "❌ $new_f: disposition 未 carry forward (prev=$prev_disp, new=$new_disp)"
      fi
    fi
  done
fi

# 4. _state.yaml 已更新到本轮
state_round=$(awk '/^current_round:/{print $2; exit}' spec/fix/_state.yaml)
[[ "$state_round" == "$N" ]] || echo "❌ _state.yaml current_round 未更新到 $N"
```
