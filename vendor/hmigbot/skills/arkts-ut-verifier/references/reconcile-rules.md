# Reconciliation 算法（跨轮状态推导）

`arkts-ut-verifier` 的 execute 步骤每轮跑完后，通过比较 `spec/verify/ut/round-{N-1}/ut/` 与本轮 runtime 结果，写出 `spec/verify/ut/round-N/ut/` + `_ut_delta.md`，并保证状态语义正确。

**角色**：ut-verifier execute 步骤的"权威算法"。**依赖**：`fix-file-schema.md`（文件结构）。

## 一、核心命名约定

- 一个**问题** = 一个 ID（确定性，跨轮稳定）
- 一个**文件** = `spec/verify/ut/round-N/ut/<id>.md`
- **文件存在** = 该轮该问题处于 RED / ERROR / IMPL_MISSING / UNREACHABLE 之一
- **文件不存在** ∧ **该 it() 有真实 GREEN 结果、通过独立质量门且本条行为所需生产接线无缺口** = 该轮验证通过；其余缺结果/缺依据进入未验证清单，已确认接线缺口保留实现问题
- **文件不存在** ∧ **测试套件不含此 it()** = stale（spec/测试已删此条）

## 二、状态推导表（不依赖 frontmatter）

某 ID 在 round-N 的状态由 `round-(N-1)` 问题文件与本轮验证结论共同决定；本轮结论合并实际日志、独立测试质量检查和必要生产接线复核，不直接套用方法 UT 的原始 GREEN：

| round-(N-1) 文件 | round-N 验证结论 | 推导状态 | round-N/ 是否写文件 | 备注 |
|---|---|---|---|---|
| 不存在 | GREEN 且必要接线无缺口 | `still_green` | 否 | 无开放问题 |
| 不存在 | RED / ERROR / IMPL_MISSING / UNREACHABLE | `newly_open` | ✅ 新建 | 原始 GREEN 但必要接线缺失也保留实现问题 |
| 存在 | GREEN 且必要接线无缺口 | `fixed` | 否 | 还须核对稳定 ID 与原验证义务 |
| 存在 | RED / ERROR / IMPL_MISSING / UNREACHABLE | `still_failing` | ✅ carry forward 写 | disposition 必须 carry；kind 按当前证据重算 |
| 存在 | 未执行且无足够结论 | 未验证 / `stale` 候选 | 按当前证据 | 测试仍在设计中则保留缺口，仅删除/移出范围才进一步核对 stale |

**回归（regression）检测**：扫历史轮看模式

```
∃ K ≤ N-2: round-K ∋ id ∧ round-(K+1) ∌ id ∧ ... ∧ round-(N-1) ∌ id ∧ round-N ∋ id
```

即：上次 fixed 之后又再次出现 → 这是回归。`_ut_delta.md` 把这种 ID 标 `regressed`。

> **回归需诊断**：主线程区分实际源码回归与测试质量门重分类，保留其它已验证修复，不 git reset。可修生产/测试问题继续派发，不仅因 REGRESSED 自动转人工；行为证据缺失或需裁决时才记录具体处置依据。

> **测试更新后的对账**：先验收 `TEST_UPDATES` 的 Android 依据、原行为断言与设计/generation/注册一致性，再使用本轮实际执行结果。旧 `no_entry` 已出现入口时不得照抄缺失结论；补测试后使用同一稳定 ID 的真实结果。删除/改名测试或弱化断言不能算 `fixed`，须退回补齐原验证义务；仅有新入口、尚未实跑也不能算解决。旧人工处置仅因禁测、fixture 或待刷新时，由主线程复核并清回 null，executor 不自行覆盖仍有效决策。

> **生产接线对账**：按 `fixer-wiring-policy.md` 独立回查 `WIRING_EVIDENCE` 与实际调用链。本条行为所需接线尚缺时，即使方法 UT 为 GREEN，也保留对应实现问题与 `partial`，不能算 `RESOLVED` 或完整实现。旧 `UNREACHABLE` 因新增入口失效时由主线程按当前证据重分类，再对同一稳定 ID 对账，不能凭改分类或文件消失当成已解决。

## 三、carry forward 算法（写 round-N/ut/<id>.md 之前）

```pseudocode
def write_problem_file(round_N: int, id: str, current_run_data: dict):
    new_file_path  = f"spec/verify/ut/round-{round_N}/ut/{id}.md"
    prev_file_path = f"spec/verify/ut/round-{round_N - 1}/ut/{id}.md"

    # 1. 准备新 frontmatter（默认值 + 当轮数据）
    fm = {
        "id":               id,
        "title":            current_run_data["title"],
        "source":           "arkts-ut-verifier",
        "layer":            "ut",
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

1. **disposition 不静默丢失**：主线程先复核已失效的禁测/待刷新原因，必要时显式清为 null；executor 只继承复核后的有效处置，不能将旧职责限制当永久人工原因
2. **suggested_files 每轮重算**：本轮 verifier 的最新分析为权威（spec 改 / 源码改 → 缺口位置可能变）
3. **kind / severity 每轮重算**：依据本轮实际运行与独立复核证据（如 ERROR 修成 RED，或方法 GREEN 但必要接线仍缺，也要准确分类）
4. **不维护历史尝试表**：跨轮历史靠 round 目录序列 + `fixer-summary.md` 承载

## 四、`_ut_delta.md` 生成算法

每轮（round-1 起）verifier 写完 `round-N/ut/` 所有 .md 后，立即生成 `round-N/_ut_delta.md`。

```pseudocode
def gen_delta(round_N: int):
    prev_dir = f"spec/verify/ut/round-{round_N - 1}/ut"
    curr_dir = f"spec/verify/ut/round-{round_N}/ut"

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
    validated_green = 本轮有真实 GREEN 日志、通过独立测试质量门且本条行为必要生产接线无缺口的ID
    for id in resolved:
        if id not in test_names_now:
            stale.append(id)   # 缺测试需说明，原行为义务未完成则退回补测，不算修复
        elif id not in validated_green:
            返回未执行、质量不合格或必要接线缺失问题，保持开放并修正本轮报告
        else:
            fixed.append(id)

    write_delta_md(round_N, fixed, stale, regressed, truly_new, still_failing)
```

### `_ut_delta.md` 模板

```markdown
# Round {N} ut delta（vs round-{N-1}）

> 生成时间：YYYY-MM-DDTHH:mm:ss+08:00
> verifier source: arkts-ut-verifier
> 设备：<device_id> bundle: <bundle>
> aa test 原始汇总: `Tests run: N, Failure: F, Error: E, Pass: P, Ignore: I`

## ✅ Resolved（fixed，{count}）

上轮失败、本轮 GREEN：

- F010_AC04_deleteFiles_emptyArray
- F005_AC02_init_with_seed_data
- ...

## 🆕 Newly opened（首次出现，{count}）

历史上没出现过的新 RED/ERROR：

- F022_AC01_savedPage_resume    ← spec 改了引入新测试
- ...

## 🚨 Regressed（回归，{count}）

历史轮次中 fixed 过、本轮再次失败：

- F005_AC01_db_init   ← 在 round-2 fixed，本轮 round-{N} 再次失败
  上次 fixed 时 commit: <sha>（见 fixer-summary.md）
  按本轮证据区分生产回归/测试质量问题；可修项保持开放，需裁决项注明依据

## 🪦 Stale（{count}）

文件不再出现且测试已不在当前套件（spec/测试架构变了）：

- F099_AC07_legacy_xxx   ← spec 删除了 AC07

## 🔁 Still failing（仍未修复，{count}）

- 折叠列出 ID（点击 round-{N}/ut/<id>.md 查看详情）

## 计数变化

| 维度 | round-{N-1} | round-{N} | Δ |
|---|---|---|---|
| ut 失败数 | x | x | ±x |
| disposition=manual_review | x | x | ±x |
| disposition=skipped | x | x | ±x |
```

## 五、edge case 处理表

| 情形 | 处理 |
|---|---|
| **同一轮 verifier 跑两次**（设备闪退重跑） | 第二次完全覆盖第一次的 round-N/ut/；不改 round 号 |
| **用户手动改了 round-N/<id>.md** | 下轮 verifier carry forward 时尊重用户改动（仅限 disposition / related 字段） |
| **verifier SKIP 了某 it()**（编译失败 / timeout） | 该 it() 不计入本轮 runtime；若上轮该文件存在 → carry forward 全文件，§3 实际写"本轮 SKIPPED_<原因>" |
| **spec 改名了**（F010_AC03 → F010_AC03b） | 老 ID 文件本轮 stale；新 ID 创建新文件 |
| **测试套件结构变** | 不影响 reconcile，照常按 ID 比对 |
| **round-(N-1)/ 不存在**（首次跑） | 跳过 carry forward 步骤，直接按 newly_open 写所有失败 |

## 六、`_state.yaml` 维护

每轮 verifier 完成后，主线程更新 `_state.yaml`：

```yaml
schema_version: 1
current_round: <N>
last_verifier_run_at: <ISO 时间戳>
last_verifier_source: arkts-ut-verifier
loop_status: running | paused | passed | converged | failed | stalled
max_rounds: 10
no_progress_rounds: 2
```

更新规则：
- verifier 首跑（baseline）→ 写 `current_round: 0`
- fix-loop 调度 verifier 重跑 → `current_round = N+1`
- verifier 不要自己推断 round 号；主线程显式传 `ROUND` 参数
- `passed` 仅用于实际全范围通过；有真实缺证据/不可达等未验证残留但内部工作已完成时为 `converged`，仍有待补测/质量退回时保持 `running` 或按明确失败退出。

> `_state.yaml` 位于本 skill 私有的 `spec/verify/ut/` 根下，不与其它 verifier 共享——不存在并发覆盖问题。

## 七、自检（verifier 完成 reconcile 后必跑）

失败处理统一遵循 executor §6.5 与 `fix-file-schema.md §九`：自身产物错误在本轮自动修复并重验，最多 2 次；不得改变原始证据、失败事实或擅清 disposition。主线程已批准变更的处置须附批准证据，核对该证据后更新 carry-forward 检查依据，不能把有效处置改回旧值来消除告警。

```bash
N=<本轮号>
ROUND_DIR="spec/verify/ut/round-$N"
PREV_DIR="spec/verify/ut/round-$((N-1))"

# 1. round 目录已建
test -d $ROUND_DIR/ut || mkdir -p $ROUND_DIR/ut

# 2. 汇总文件齐全
for f in _ut_index.md _ut_summary.md; do
  test -f $ROUND_DIR/$f || echo "❌ 缺 $ROUND_DIR/$f"
done
# round-0 不写 _delta，round-1+ 必写
[[ $N -ge 1 ]] && { test -f $ROUND_DIR/_ut_delta.md || echo "❌ round-$N 缺 _ut_delta.md"; }

# 3. carry forward 检查：上轮所有有 disposition 的文件，本轮如果还失败必须 carry
if [[ -d $PREV_DIR/ut ]]; then
  for f in $(find $PREV_DIR/ut -name '*.md' -not -name '_*.md'); do
    id=$(basename $f .md)
    new_f=$ROUND_DIR/ut/$id.md
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
state_round=$(awk '/^current_round:/{print $2; exit}' spec/verify/ut/_state.yaml)
[[ "$state_round" == "$N" ]] || echo "❌ _state.yaml current_round 未更新到 $N"
```
