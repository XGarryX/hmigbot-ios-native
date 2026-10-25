# Reconciliation 算法（跨轮状态推导）

本文档定义 verifier 每轮跑完后，如何通过比较 `spec/fix/round-{N-1}/` 与本轮 runtime 结果，写出 `spec/fix/round-N/` + `_delta.md`，并保证状态语义正确。

> **角色**：dt-verifier Step 5、visual-verify 写报告步骤共同遵循的"权威算法"。
> **依赖**：`fix-file-schema.md`（文件结构）

> **v2 简化（已应用）**：移除 SYSTEMIC kind / _systemic/ 子目录，移除 `disposition: problematic`，移除 REGRESSED 触发回滚的语义（REGRESSED 现在仅作为统计字段，由 a2h-verify 主线程自动 mark `disposition: manual_review` 防止下轮 fixer 来回反复，但**不 git reset**）。

---

## 一、核心命名约定（再强调）

- 一个**问题** = 一个 ID（确定性，跨轮稳定）
- 一个**文件** = `spec/fix/round-N/<layer>/<id>.md`
- **文件存在** = 该轮该问题处于 RED/ERROR/ALIGNMENT_DIFF 之一
- **文件不存在** ∧ **AC 索引仍含此 it()** = 该轮 GREEN
- **文件不存在** ∧ **AC 索引不含此 it()** = stale（spec/测试已删此条）

---

## 二、状态推导表（不依赖 frontmatter）

某 ID 在 round-N 的状态 = `round-(N-1)` 与本轮 runtime 的存在性组合：

| round-(N-1) 文件 | round-N runtime | 推导状态 | round-N/ 是否写文件 | 备注 |
|---|---|---|---|---|
| 不存在 | GREEN | `still_green` | 否 | 不关心 |
| 不存在 | RED/ERROR/DIFF | `newly_open` | ✅ 新建 | created_round 隐含 = N |
| 存在 | GREEN | `fixed` | 否（不写） | round-N/ 缺该文件 = fixed 信号 |
| 存在 | RED/ERROR/DIFF | `still_failing` | ✅ carry forward 写 | disposition 必须 carry |
| 存在 | 不在 runtime 中 | `stale` 候选 | 否（不写） | dt-verifier Step 5 进一步区分 |

**回归（regression）检测**：扫三轮看模式

```
∃ K ≤ N-2: round-K ∋ id ∧ round-(K+1) ∌ id ∧ ... ∧ round-(N-1) ∌ id ∧ round-N ∋ id
```

即：上次 fixed 之后又再次出现 → 这是回归。`_delta.md` 必须把这种 ID 标注为 `regressed`。

> **v2 处理**：旧版 REGRESSED ≥ 1 触发 `git reset --hard` 全轮回滚。新版**不回滚**：a2h-verify CHECK-7 §3d.4 Step E 仅给 REGRESSED 项自动写 `disposition: manual_review`，让下一轮 fixer 跳过。原因见 a2h-fixer.md §5：1:26 比例的回滚损失太大；fixer 应通过反向 impact 自检 + 保留向后兼容来主动防回归。

简化判定：**只需看 `round-(N-1) ∌ id ∧ round-N ∋ id` 模式，其中 ∃ K < N-1: round-K ∋ id`**（曾经存在但上轮不存在 → 本轮又出现 = 回归）。

---

## 三、carry forward 算法（写 round-N/<id>.md 之前）

每轮新建 `round-N/` 后，对每个本轮失败的 ID：

```pseudocode
def write_problem_file(round_N: int, layer: str, id: str, current_run_data: dict):
    new_file_path = f"spec/fix/round-{round_N}/{layer}/{id}.md"
    prev_file_path = f"spec/fix/round-{round_N - 1}/{layer}/{id}.md"

    # 1. 准备新 frontmatter（默认值 + 当轮数据）
    # v2 移除：systemic_root / affects 字段
    fm = {
        "id": id,
        "title": current_run_data["title"],
        "source": current_run_data["source"],
        "layer": layer,
        "kind": current_run_data["kind"],
        "severity": current_run_data["severity"],
        "fixer_layer": current_run_data["fixer_layer"],
        "suggested_files": current_run_data["suggested_files"],
        "related": [],
        "evidence": current_run_data["evidence"],

        # disposition 默认 null，下面 carry forward 覆盖
        "disposition": None,
        "disposition_reason": None,
        "disposition_set_at_round": None,
    }

    # 2. carry forward disposition
    if exists(prev_file_path):
        prev_fm = parse_frontmatter(prev_file_path)
        if prev_fm.get("disposition") is not None:
            fm["disposition"] = prev_fm["disposition"]
            fm["disposition_reason"] = prev_fm["disposition_reason"]
            fm["disposition_set_at_round"] = prev_fm["disposition_set_at_round"]

    # 3. carry forward related（手工添加的关联不应被冲掉）
    if exists(prev_file_path):
        prev_fm = parse_frontmatter(prev_file_path)
        if prev_fm.get("related"):
            fm["related"] = prev_fm["related"]

    # 4. 拼正文（5 sections，无历史尝试）
    body = render_sections(current_run_data)

    write_file(new_file_path, frontmatter_to_yaml(fm) + body)
```

### 关键不变式

1. **disposition 永不丢失**：除非 CHECK-7 主线程显式清空（设为 null），否则一直 carry forward
2. **suggested_files 每轮重算**：即使 prev 文件存在，suggested_files 也用本轮 verifier 的最新分析（spec 改了 / 源码改了 → 缺口位置可能变）
3. **kind / severity 每轮重算**：本轮 runtime 是权威，例如 ERROR 修成 RED 也要更新
4. **不维护历史尝试表**：跨轮历史靠 round 目录序列承载（git diff round-N round-N+1 + `docs/autofix-log/round-N/{batch,fixer-summary,rollback}.md`）

---

## 四、`_delta.md` 生成算法

每轮（round-1 起）verifier 写完 `round-N/` 所有 .md 后，立即生成 `round-N/_delta.md`。

### 算法

```pseudocode
def gen_delta(round_N: int):
    prev_dir = f"spec/fix/round-{round_N - 1}"
    curr_dir = f"spec/fix/round-{round_N}"

    prev_ids = scan_problem_files(prev_dir)         # 扫 .md 文件名（去 .md）
    curr_ids = scan_problem_files(curr_dir)

    resolved      = prev_ids - curr_ids             # 上轮失败、本轮 GREEN
    newly_open    = curr_ids - prev_ids
    still_failing = prev_ids ∩ curr_ids

    # 进一步区分 newly_open 中的"全新"vs"回归"
    truly_new = []
    regressed = []
    for id in newly_open:
        if appears_in_any_round(id, range(0, round_N - 1)):
            regressed.append(id)   # 历史上 fixed 过又出现
        else:
            truly_new.append(id)

    # 进一步区分 resolved 中的"真 fixed"vs"stale"
    fixed = []
    stale = []
    ac_index_now = parse_ac_index_test_names()      # 当前测试套件中的 it() 名集合
    for id in resolved:
        # AC 索引中 it() 已不存在 → 测试被删了（spec 改 / 测试架构改）
        if id not in ac_index_now and not id.startswith("ALIGN_"):
            stale.append(id)
        # ALIGN_* ID 来源是 visual-verify 的差异类型，不在 AC 索引里
        # 判定 stale：visual-verify 这一轮根本没跑该页（设备未连），文件不出现 ≠ fixed
        elif id.startswith("ALIGN_") and not visual_verify_ran_this_round(extract_page_id(id)):
            stale.append(id)
        else:
            fixed.append(id)

    write_delta_md(round_N, fixed, stale, regressed, truly_new, still_failing)
```

### `_delta.md` 模板

```markdown
# Round {N} delta（vs round-{N-1}）

> 生成时间：YYYY-MM-DDTHH:mm:ss+08:00
> verifier sources: dt-verifier, visual-verify
> 设备：<device_id> bundle: <bundle>
> aa test 原始汇总: `Tests run: N, Failures: F, Errors: E, Skipped: S`

## ✅ Resolved（fixed，{count}）

上轮失败、本轮 GREEN/passed：

- feat/F010_AC04_deleteFiles_emptyArray
- ui/ALIGN_P0010_layout_drift
- ui/P0007_UI_NAV_drawer_swipe
- ...

## 🆕 Newly opened（首次出现，{count}）

历史上没出现过的新 RED/ERROR/DIFF：

- feat/F022_AC01_savedPage_resume    ← spec 改了引入新测试
- ui/P0008_UI_INTERACT_share_btn     ← 之前 SKIP 过 / 设备问题没跑到
- ...

## 🚨 Regressed（回归，{count}）⚠️ 自动 mark manual_review，不回滚

历史轮次中 fixed 过、本轮再次失败：

- feat/F005_AC01_db_init   ← 在 round-2 fixed，本轮 round-{N} 再次失败
  上次 fixed 时 commit: <sha>（详见 docs/autofix-log/round-2/fixer-summary.md）
  本轮自动标 disposition: manual_review（需人工排查 fix 的副作用）
- ...

> **v2 处理**：a2h-verify CHECK-7 §3d.4 Step E 拿到 REGRESSED 列表后，自动给每个 ID 写 `disposition: manual_review`，让下一轮 fixer 跳过该 ID。**不 git reset**，本轮其它 RESOLVED 的进展保留。

## 🪦 Stale（{count}）

文件不再出现且测试已不在 AC 索引（spec/测试架构变了）：

- feat/F099_AC07_legacy_xxx   ← spec 删除了 AC07
- ...

## 🔁 Still failing（仍未修复，{count}）

- 折叠列出 ID（点击 round-{N}/<layer>/<id>.md 查看详情）

## 计数变化

| 维度 | round-{N-1} | round-{N} | Δ |
|---|---|---|---|
| feat 失败数 | x | x | ±x |
| ui 失败数 | x | x | ±x |
| 总失败数 | x | x | ±x |
| disposition=manual_review | x | x | ±x |
| disposition=skipped | x | x | ±x |
```

> **v2 移除字段**：`disposition=problematic`（已废除）。本次轮 REGRESSED 自动转为 `manual_review`，故只统计 `manual_review` + `skipped`。

---

## 五、edge case 处理表

| 情形 | 处理 |
|---|---|
| **同一轮 verifier 跑两次**（设备闪退重跑） | 第二次完全覆盖第一次的 round-N/；不改 round 号 |
| **用户手动改了 round-N/<id>.md** | 下轮 verifier carry forward 时尊重用户改动（仅限 disposition / related 字段） |
| **visual-verify 这一轮没跑**（设备未连） | round-N/ 不删除上轮所有 ALIGN_*.md；它们 carry forward 全部 frontmatter，§3 实际写"本轮未跑视觉验证" |
| **dt-verifier SKIP 了某 it()**（编译失败 / timeout） | 该 it() 不计入本轮 runtime；若上轮该文件存在 → carry forward 全文件，§3 实际写"本轮 SKIPPED_<原因>" |
| **spec 改名了**（F010_AC03 → F010_AC03b） | 老 ID 文件本轮 stale；新 ID 创建新文件 |
| **AC 索引行数变了**（测试套件结构变） | 不影响 reconcile，照常按 ID 比对 |
| **round-(N-1)/ 不存在**（首次跑） | 跳过 carry forward 步骤，直接按 newly_open 写所有失败 |

---

## 六、`_state.yaml` 维护

每轮 verifier 完成后，主线程更新 `_state.yaml`：

```yaml
schema_version: 1
current_round: <N>
last_verifier_run_at: <ISO 时间戳>
last_verifier_sources: [<dt-verifier | visual-verify>]
last_autofix_round: <最近一次 autofix round；与 verifier round 同步>
target_green_ratio: 1.0
max_rounds: 10
```

更新规则：
- verifier 单跑（baseline 或独立调用）→ 更新 `current_round` + `last_verifier_*` 字段
- autofix 调度 verifier 重跑 → 同时更新 `last_autofix_round = current_round`

`current_round` 的来源：
- 首次：默认 0（baseline）
- autofix 调用 verifier 时显式传 `ROUND` 参数
- verifier 不要自己推断 round 号（除非主线程没传）

---

## 七、自检（verifier 完成 reconcile 后必跑）

```bash
N=<本轮号>
ROUND_DIR="spec/fix/round-$N"
PREV_DIR="spec/fix/round-$((N-1))"

# 1. round 目录已建
test -d $ROUND_DIR || { echo "❌ round-$N 目录未建"; exit 1; }

# 2. 三个汇总文件齐全
for f in _index.md _summary.md; do
  test -f $ROUND_DIR/$f || echo "❌ 缺 $ROUND_DIR/$f"
done
# round-0 不写 _delta.md，round-1+ 必写
[[ $N -ge 1 ]] && { test -f $ROUND_DIR/_delta.md || echo "❌ round-$N 缺 _delta.md"; }

# 3. carry forward 检查：上轮所有有 disposition 的文件，本轮如果还失败必须 carry
if [[ -d $PREV_DIR ]]; then
  for f in $(find $PREV_DIR -name '*.md' -not -name '_*.md'); do
    id=$(basename $f .md)
    layer_dir=$(dirname $f | sed "s|$PREV_DIR/||")
    new_f=$ROUND_DIR/$layer_dir/$id.md
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
