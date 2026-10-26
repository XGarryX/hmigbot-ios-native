# spec-evolver 完整工作流程（Step 1-12 + 强制执行检查清单 + Verify 门控）

> 从 arkts-spec-evolver/SKILL.md 下沉。SKILL.md 通过 MUST-read 指针引用本文件。

## 完整工作流程（对齐 Pipeline 五步流水线）

```
                Pipeline 流程对照
                ━━━━━━━━━━━━━━━━━━
用户输入        Pipeline             spec-evolver
变更需求        ↓                    ↓
    │           a2h-spec        →    Step 1-5: create 增量 spec
    │           ↓                    ↓
    │           a2h-plan        →    Step 6-7: plan 实现计划
    │           ↓                    ↓
    │           a2h-execute     →    Step 8-9: execute 代码变更
    │           ↓                    ↓
    │           a2h-verify      →    Step 10-11-12: 静态 + 视觉验证
    ▼           ↓                    ↓
完成            a2h-retrospect       done（视觉通过）/ verifying(visual-pending)
```

### Create 阶段（Step 1-5）

**Step 1: 读取上下文**
- 读 `spec/spec-index.md`（baseline + 已有增量）
- 读 baseline 中受影响的层（按需）
- 读已有增量（避免重复创建）

**Step 2: 分类 + 编号**
- 自动判断 `type`: feature / bugfix / optimization
- 从 spec-index.md "当前状态摘要" 读取下一编号，分配: F-xxx / BF-xxx / OPT-xxx
- 分析 `affects`: 哪些 baseline 层/section

**Step 3: 生成增量 spec**
- 按模板（`templates/increment-spec-template.md`）写入对应目录
  - feature → `spec/features/YYYY-MM-DD-Fxxx-description.md`
  - bugfix → `spec/bugfixes/YYYY-MM-DD-BFxxx-description.md`
  - optimization → `spec/optimizations/YYYY-MM-DD-OPTxxx-description.md`
- **status: pending**
- bugfix 类型额外包含 "复现步骤" 和 "根因分析" 两节

**Step 3.5: 派生回归范围（★ 必跑，不可跳过）**

<HARD-GATE>
增量 spec 的 `## 回归范围` 栏目必须在 create 阶段完成填充。该栏目是 Step 11 回归验证的前置数据，缺失 = verify 阶段无法执行 = 流程断裂。绝对禁止留空占位符或跳过此步骤。
</HARD-GATE>

从 `affects` 字段 + 实际代码分析，派生回归范围：

**3.5.1 识别 shared_files / shared_symbols**
```bash
# 列出本次改动将触碰的文件（从 spec 的"实现指引"/"变更描述"中提取）
H_TARGETS=("entry/src/main/ets/pages/XxxPage.ets" "entry/src/main/ets/viewmodels/XxxViewModel.ets")

# 对每个目标文件，grep 它在 baseline spec 中被哪些功能引用
for f in "${H_TARGETS[@]}"; do
  grep -rn "$(basename $f)" spec/baseline/ 2>/dev/null
done
```
将命中的文件和符号（struct / method / 状态变量：V2 `@Local`/`@Param`/`@Event` 或 V1 `@State`/`@Prop`/`@Link`）记入 `### shared_files / shared_symbols`。

**3.5.2 派生 feature_acs**
- 从 Step 3.5.1 命中的 baseline spec 中提取所有验收标准（AC）
- 这些 AC 代表"本次改动可能影响的已有功能"
- 如果 baseline 没有结构化 AC 编号，按 "F{功能编号}-AC{序号}" 格式编号
- 记入 `### feature_acs`

**3.5.3 派生 page_acs**
- 从 `affects` 中的 `ui: page_xxxx` 提取受影响的页面
- 为每个页面生成两类 AC：
  - `P{页面编号}-UI-SMOKE`：页面可正常打开、核心元素可见
  - `P{页面编号}-UI-INTERACT_{交互名}`：页面核心交互功能正常（Tab 切换、列表滚动、按钮点击等）
- 记入 `### page_acs`

**3.5.4 派生 affected_visual_pages**
- 仅当 `affects` 含 `ui:` 时必填
- 列出本次改动触碰的页面的所有关键状态（空状态、有数据状态、管理模式等）
- 每条包含：page_id、state_label、hmos_entry_path、android_reference、android_entry_path
- 记入 `### affected_visual_pages`

**3.5.5 填写 rationale**
- 简要说明为什么这些 AC 会受影响（改了哪个共享文件/方法/状态）

**3.5.6 explosion 判定**
- total = len(feature_acs) + len(page_acs)
- total > 10 → explosion=true，需用户 opt_out 审批
- total ≤ 10 → explosion=false，全量回归

**纯新增功能的特殊处理**：
- 如果本次变更完全不触碰任何已有文件（仅新建文件），shared_files 为空
- 此时 feature_acs 和 page_acs 可为空，但必须显式标注 "纯新增功能，不触碰已有代码，无回归项"
- affected_visual_pages 仍需填写（新增功能的视觉验证）

**Step 4: 更新 spec-index.md**
- 在对应类型表（Features / Bugfixes / Optimizations）中新增一行
- 更新 "当前状态摘要" 中的计数和下一编号

**Step 5: 用户确认 spec（★ Gate 1）**
- 输出: "增量 spec 已生成，请审阅。"
- 等待用户确认后才进入 Plan 阶段
- 如果是全流程模式（create+plan+execute+verify），用户确认后自动进入 Plan 阶段

<HARD-GATE>
无论何种模式，Step 5 必须等待用户明确确认。绝对禁止自动跳过此步骤。
</HARD-GATE>

### Plan 阶段（Step 6-7）

**Step 6: 生成实现计划**
- 分析增量 spec 的 `affects` 和 "实现指引"
- 生成 plan 文件: `spec/<type>/plans/YYYY-MM-DD-<id>-plan.md`
- plan 内容包含:
  - 影响的文件清单（创建/修改/测试）
  - 按依赖顺序拆解的 task 列表
  - 每个 task 的具体步骤
  - 调用哪些下游 skill
- 简单 bugfix 可生成简化 plan（单 task，见"简化流程"）
- 更新增量 spec 的 "实现计划" 区域，记录 plan 文件路径和 task 数量

**Step 7: 用户确认 plan（★ Gate 2）**
- 输出: "实现计划已生成，请审阅。"
- 等待用户确认后才进入 Execute 阶段

<HARD-GATE>
无论何种模式，Step 7 必须等待用户明确确认。绝对禁止自动跳过此步骤。
</HARD-GATE>

### Execute 阶段（Step 8-9）

<HARD-GATE>
Execute 前置检查：
1. 读取增量 spec 文件的 status 字段
2. status 必须为 planned
3. status 为 pending → 拒绝执行，提示 "spec 尚未确认，请先审阅并确认"
4. spec 文件不存在 → 拒绝执行，提示 "请先通过 create 模式生成 spec"
不存在已审批 spec 的情况下，绝对禁止生成任何实现代码。
</HARD-GATE>

**Step 8: 执行代码变更**
- spec status: **planned → in_progress**
- 按 plan 的 task 列表逐个执行:
  - 每个 task 调用对应下游 skill（见"Skill 调度顺序"）
  - feature → component-builder / data-layer / ...
  - bugfix → knowledge-verifier 诊断 → 对应 skill
  - optimization → ui-alignment / component-builder
- 每个 task 完成后标记 plan 中的 checkbox

**Step 9: 回填执行记录**
- 在增量 spec 的 "执行记录" 中填充:
  - 执行时间
  - 触发 skill
  - 修改文件列表
  - commit hash
- plan 文件中所有 task 标记完成

**Step 9.5: 实际改动回归范围重扫（★ 必跑，不可跳过）**

<HARD-GATE>
execute 阶段完成后、进入 verify 前，必须基于实际代码改动重新扫描回归范围。此步骤产出清单 B，与 Step 3.5 产出的清单 A 取并集，作为最终回归清单。

原因：Step 3.5 是"预测"——基于 spec affects 推断可能影响的范围；但实际写代码时可能多改了文件、多碰了共享方法、引入了 spec 未预见的依赖。仅靠预测清单做回归会漏掉这些意外触碰。
</HARD-GATE>

**9.5.1 扫描实际改动文件**
```bash
# 获取本次 execute 阶段实际修改/新增的文件列表
git diff --name-only HEAD~1..HEAD -- "*.ets" "*.json"
# 如有多个 commit，调整范围到 execute 开始前的 commit
```
产出 `actual_changed_files` 列表。

**9.5.2 从实际改动派生清单 B**

对 `actual_changed_files` 中每个文件：

1. **反查 baseline spec 引用**：
   ```bash
   grep -rn "$(basename $f)" spec/baseline/ 2>/dev/null
   ```
   命中的 baseline 功能 → 提取其 AC → 加入清单 B 的 `feature_acs_B`

2. **反查共享符号**：对实际修改的 struct / method / 状态变量（V2 `@Local`/`@Param`/`@Event` 或 V1 `@State`/`@Prop`/`@Link`），grep baseline spec 和其他页面代码，找出哪些功能依赖这些符号
   ```bash
   # 例：修改了 WorksViewModel.loadWorksList()
   grep -rn "loadWorksList\|WorksViewModel" spec/baseline/ entry/src/main/ets/pages/ 2>/dev/null
   ```
   命中的额外文件/功能 → 加入清单 B 的 `feature_acs_B` / `page_acs_B`

3. **页面级 AC 派生**：对实际改动的页面文件，生成 `P{页面}-UI-SMOKE` / `P{页面}-UI-INTERACT_*` AC → 加入清单 B 的 `page_acs_B`

4. **视觉页面派生**：对实际改动的 UI 文件，提取受影响的页面状态 → 加入清单 B 的 `affected_visual_pages_B`

**9.5.3 合并清单 A ∪ B → 最终回归清单**

```
final_feature_acs     = feature_acs_A     ∪ feature_acs_B     （去重）
final_page_acs        = page_acs_A        ∪ page_acs_B        （去重）
final_shared_files    = shared_files_A    ∪ actual_changed_files（去重）
final_visual_pages    = visual_pages_A    ∪ visual_pages_B    （按 page_id + state_label 去重）
```

**9.5.4 回写增量 spec**

将合并后的最终清单回写到增量 spec 的 `## 回归范围`，并标注来源：
```markdown
### feature_acs（最终 = 清单 A ∪ 清单 B）
- F006-AC1：作品列表正常加载（来源：清单 A — spec affects 预测）
- F006-AC3：管理模式全选/删除正常（来源：清单 B — 实际改动 WorksViewModel.ets）

### 合并记录
- 清单 A（Step 3.5 预测）：feature_acs={N}, page_acs={M}
- 清单 B（Step 9.5 实扫）：feature_acs={P}, page_acs={Q}
- 新增项（B - A）：{列出清单 B 中有但清单 A 中没有的条目}
- 最终：feature_acs={X}, page_acs={Y}, total={X+Y}
```

如果清单 B 比清单 A 多出条目，说明 Step 3.5 的预测有遗漏，这些遗漏应该在验证记录中标注，为后续改进回归预测提供反馈。

### Verify 阶段（Step 10-11-12）

**Step 10: 静态验证**
- spec status: **in_progress → verifying**
- 编译验证: hmos-fix-build-errors 自动编译修复（最多 20 轮，替代手动 hvigor build）
- 验收验证: 按增量 spec 的 "验收标准" 逐项检查（grep / 代码结构）
- 验证结果记录到增量 spec 的 "验证记录" 区域

**Step 10.5: 回归范围完整性检查（★ 必跑，Step 11 前置门禁）**

<HARD-GATE>
Step 10 通过后、进入 Step 11 前，必须检查增量 spec `## 回归范围` 栏目的完整性：

1. `## 回归范围` 栏目是否存在？
2. 是否已完成 Step 9.5 的 A ∪ B 合并（检查"合并记录"子节是否存在）？
3. `feature_acs` 最终列表是否已填充（或显式标注"纯新增，无回归项"）？
4. `page_acs` 最终列表是否已填充（或显式标注"纯新增，无回归项"）？
5. `affected_visual_pages` 最终列表是否已填充（当 affects 含 ui: 时必填）？
6. `shared_files / shared_symbols` 最终列表是否已填充？

任一项缺失 → **立即停止 verify**：
- 缺清单 A → 回到 create 阶段执行 Step 3.5
- 缺清单 B 或合并记录 → 回到 Step 9.5 执行实际改动重扫
- 然后重新进入 verify

绝对禁止以"grep 静态检查通过"替代回归范围派生和验证。grep 验收标准只能验证新增功能本身是否实现，不能验证已有功能是否被破坏。
</HARD-GATE>

**Step 10.6: 回归执行方式选择（★ 必问，不可跳过）**

<HARD-GATE>
Step 10.5 通过后、执行 Step 11 前，必须向用户展示最终回归清单并询问回归方式。绝对禁止未经询问直接执行自动化回归。
</HARD-GATE>

向用户展示以下内容并等待选择：

```
回归范围（最终清单 A ∪ B）：
  feature_acs: {列出所有条目}
  page_acs: {列出所有条目}
  affected_visual_pages: {列出所有条目}

请选择回归方式：
  (a) 自动回归 — 由我在模拟器/真机上逐项验证，输出回归报告
  (b) 人工回归 — 我输出回归清单文档，由你自行验证后反馈结果
```

用户选择 (a)：进入 Step 11，按流程执行自动化回归 + 视觉验证。
用户选择 (b)：
- 将最终回归清单输出为结构化文档（含每条 AC 的验证步骤、预期结果、操作路径）
- spec status 标为 `verifying(manual-regression)`
- 等待用户反馈回归结果后，根据结果更新 spec status：
  - 用户确认全部通过 → 进入 Step 11b 视觉验证（如需要）或直接 Step 12
  - 用户报告有退化 → 进入回退处理流程

**Step 11: 自动化回归 + 视觉验证（消费 spec 的 ## 回归范围 栏目）**

<HARD-GATE>
**前置数据**：增量 spec 必须含 `## 回归范围` 栏目（由 a2h-incremental-migration §M3.2.5 派生，或 evolver create 阶段从 affects 派生）。该栏目缺失或字段不齐（feature_acs / page_acs / explosion 三字段必须存在）→ skill 失败，回到 create 阶段补齐再执行。

**11 拆为两个子步骤，按改动类型决定哪些必跑**：

| 改动类型 | Step 11a (dt-verifier) | Step 11b (visual-verify) |
|---------|------------------------|--------------------------|
| 纯新增功能（regression_scope.feature_acs + page_acs 都为空） | 跳过 | 仅做新增功能视觉对齐 |
| 改造已有页面/组件（feature_acs 或 page_acs 非空） | **必跑** | **必跑**（含 baseline_screenshots diff） |
| 仅改 feature-base / 纯数据层 | 必跑（feature_acs） | 跳过 |
| explosion=true 且已 opt_out | 必跑（仅手挑 AC） | 按 affects 决定 |

读增量 spec frontmatter `affects` 字段 + `## 回归范围` 字段：
- 包含 `ui:` 或 `ui-manifest` → 11b **必须**调 `arkts-visual-verify`
- `feature_acs` 或 `page_acs` 非空 → 11a **必须**调 `arkts-dt-verifier`
- 两者均不命中 → 在验证记录标注 "无 UI 改动 + 纯新增，免回归 + 免视觉"

禁止以 "grep 已通过" 为由直接跳到 Step 12。

### 强制执行检查清单（每次 affects 含 ui 时必须在对话里逐条过一遍）

**在把 spec status 改为 `done` 或 `verifying(visual-pending)` 之前，本 skill MUST 在对话里显式打印以下三项中的至少一项作为证据：**

| 证据项 | 形式 | 说明 |
|---|---|---|
| (A) 视觉验证通过 | arkts-visual-verify 的返回报告 + 截图路径 | 设备齐全且 UI 对比通过 |
| (B) 视觉验证失败但已达 max_rounds | arkts-visual-verify 的终态报告 | 进回退处理（Step 12），**不得**升级 done |
| (C) 无可用设备 | `hdc list targets`（或 `adb devices`）**命令原文 + 实际 stdout**（空设备列表需可见） | 回退 `verifying(visual-pending)`，**不得**升级 done |

**硬性要求**：
- 缺上述三项任一 → 视为跳过 Step 11 → skill 失败
- 仅凭"跑过了"的陈述不作数；必须有**可见的命令输出 / 子 skill 返回块**在对话里
- `hdc list targets` / `adb devices` 命令本身必须在 execute 阶段结束后、设置 status 前**单独执行一次**，不能复用前面步骤的输出（设备状态随时变化）

**状态升级守则**：
- status: `verifying` → `done` 只在 (A) 成立时允许
- status: `verifying` → `verifying(visual-pending)` 只在 (C) 成立时允许
- status: `verifying` → `failed` 只在 (B) 成立且进入回退处理时允许
</HARD-GATE>

**Step 11a：自动化回归（消费 regression_scope.feature_acs + page_acs）**

仅当 `## 回归范围` 的 `feature_acs` 或 `page_acs` 非空时执行。

**11a.1 前置：baseline AC 索引存在性**

```bash
test -f entry/src/ohosTest/ets/test/tdd-ac-index.md
```

不存在 → 提示用户先跑一次 `arkts-dt-verifier` 给 baseline 落 AC 索引（**仅首次需要**），否则无法做 GREEN 退化判断。停在 verifying，不升级。

**11a.2 调用 arkts-dt-verifier（filtered run）**

```
调用 Skill: arkts-dt-verifier
模式: filtered-rerun
输入:
  filter_acs: {regression_scope.feature_acs + regression_scope.page_acs}
  baseline_index: entry/src/ohosTest/ets/test/tdd-ac-index.md
  expected: GREEN  # 所有过滤 AC 必须保持 GREEN
```

dt-verifier 跑完后返回每条 AC 的 GREEN/RED/ERROR 状态。

**11a.3 采样兜底（每次必跑，零人工抓漏报）**

filtered AC 跑完后，必须**额外跑一组采样 AC**作为兜底——前面 grep + LLM 派生再准也可能漏，采样跑能抓到漏报：

```
all_baseline_acs = 读 entry/src/ohosTest/ets/test/tdd-ac-index.md 全部 AC
filtered_acs = regression_scope.feature_acs + page_acs
candidate_pool = all_baseline_acs - filtered_acs

sample_size = min(len(filtered_acs), 30)   # 数量上限：不超过 filtered 的 1 倍，硬上限 30 条
sample_acs = random.sample(candidate_pool, sample_size)

跑 dt-verifier(filtered_acs ∪ sample_acs)，全部期望 GREEN
```

成本：每次 spec verify 多跑 ≤30 条 AC（最多 2x 当前回归量）。换"零人工兜底"完全值得。

**11a.4 退化判定 + 漏报自动反哺**

```
IF filtered_acs 中任一 AC 退化（GREEN→RED/ERROR）:
  → 真实回归被 dt-verifier 抓到
  → 回写 spec `## 验证记录 → Step 11a` 退化条目
  → 进入 Step 12 回退处理（按 A/B/C 子类分类）
  → 不得升级 done

IF sample_acs 中任一 AC 退化:
  → **派生漏报**（grep + LLM 都没识别出来的真实回归）
  → 自动执行 4 步反哺：
     1. 把退化的 sample AC 加进当前 spec 的 regression_scope.feature_acs / page_acs
     2. 当作 filtered AC 走子类 A/B/C 分类，按对应路径处理（修代码 / 重审 spec / 重生成测试）
     3. 把"漏报模式"自动追加写入 spec/features/regression-miss-patterns.md：
        ```markdown
        ### 模式 #N（来源 {spec_id}，发现于 {YYYY-MM-DD}）
        - 改动特征：{H_TARGETS 文件 / struct / method 列表}
        - 漏报 AC：{sample 中飘红的 AC ID + 描述}
        - 漏报根因：{LLM 自动分析：方法间接调用 / 事件订阅 / 状态共享 / 业务语言不匹配 / 命名漂移 / ...}
        - 调用链 / 依赖路径：{LLM 从代码中追的链路}
        - 后续派生提示：改 {特征} 时，连带把 {AC 域} 纳入回归
        ```
     4. 重跑 11a.2 + 11a.3（含新加入的 AC），直到 sample_acs 全 GREEN
        - 重跑次数硬上限：3 次。3 次仍有 sample 退化 → spec status 标 failed，
          说明改动影响面比预期大很多，需用户审视改动范围

IF preexisting RED（baseline 上即飘红）:
  → 不计入退化，但在报告中标注 "preexisting RED, not regression"
```

**11a.5 漏报模式知识库的双向闭环**

- **写入端**（本节 11a.4）：每次 sample 抓到漏报时自动追加
- **读取端**（a2h-incremental-migration §M3.2.5.4.5）：每次新 spec 派生时 LLM 必读该文件作为上下文
- **结果**：第一次跑可能漏 5 个，第二次漏 3 个，第十次漏 0 个——机制在使用中越用越准，零人工调优

> 类比：自动驾驶系统的 corner case 学习机制，遇到一次特殊场景就把它收录，下次遇到不再翻车。

**11a.4 explosion=true 时的特殊路径**

- 仅回归 spec 里 `feature_acs` 实际列出的"手挑关键 AC"
- 全量派生结果（spec 中 `全量派生结果` 节）仅审计用，不传给 dt-verifier
- 在验证记录里显式标注 "explosion=true，非全量回归，已 opt_out"

---

**Step 11b：视觉验证（新增功能对齐 + baseline_screenshots diff）**

仅当 `affects` 含 `ui:` 时执行。Step 11a 通过（或不需跑）后才进入。

**11b.1 设备探测（最先执行，不得跳过）**

<HARD-GATE>
进入 Step 11b 的第一个动作必须是设备探测。在探测完成前，禁止执行任何截图、对比、或视觉判定操作。
</HARD-GATE>

必须执行并在对话里显示：

```bash
# HMOS 端
hdc list targets
# Android 端（如 spec 涉及对比）
adb devices
```

- 两个命令**都必须跑**，stdout 以 code fence 贴回对话
- `hdc not found` / `adb not found` 也要显式展示 → 视同无设备
- 有至少一端设备可用 → 继续 11b.2
- 两端都无设备 → 回填 `verifying(visual-pending)`，**不**升级 `done`，在"验证记录"里贴上两条命令的实际输出作为证据，**终止 Step 11b**

**禁止**：
- 假设"上次跑过了"而不重新探测
- 以"设备应该在"等推测跳过探测
- 把 `verifying(visual-pending)` 升级为 `done` 而没有 (A) 证据

**11b.2 Scope 锁定（避免全量噪声）**

不做全量页面回归，只扫本次改动触及的页面：

1. 从 `affects.ui` 取页面 id（如 `page_0009`）
2. 映射到 HMOS `.ets` 文件（查 `spec/baseline/ui-manifest.md`）
3. 若改的是子 struct / Tab 子视图，scope 锁到 "父 Page + sub_component + 进入路径"

**11b.3 调用 arkts-visual-verify（★ 必须通过 Skill 工具调用，禁止手动替代）**

<HARD-GATE>
视觉验证**必须**通过调用 `arkts-visual-verify` skill 执行。绝对禁止以下替代行为：
- ❌ 自己截图 + 肉眼看一下就判定通过
- ❌ 只截 HMOS 端不截 Android 端就判定无差异
- ❌ 只看一个状态就判定整个页面通过（必须覆盖 affected_visual_pages 的所有状态）
- ❌ 用"截图看起来正常"替代 skill 的结构化对比报告

原因：手动截图对比缺乏结构化记录、容易遗漏状态、无法追溯判定依据。arkts-visual-verify 提供：
1. 自动化的跨端截图采集（HMOS + Android）
2. 多模态对比 + 叠加语义判定
3. 自动修复循环（截图→对比→修代码→重启，最多 max_rounds 轮）
4. 结构化报告（每条状态的判定结果 + 截图路径 + diff 描述）
</HARD-GATE>

调用参数（从 spec 的 `## 回归范围 → affected_visual_pages` 和 `## 验收标准` 中提取）：

```
调用 Skill: arkts-visual-verify
模式: targeted-single-page
输入:
  project: {hmos_project}
  scope:                                       # 从 spec 的 affected_visual_pages 逐条映射
    - spec_id: F-xxx
      page_id: page_0009
      hmos_entry: entry/src/main/ets/pages/MainPage.ets
      sub_component: ItemsView                 # 可选，子 struct 精确定位
      entry_path: 冷启 → 底 Tab "我的作品" → 切 "我创建的"
      android_reference: {android_dir}/app/src/main/res/layout/fragment_work.xml
      acceptance_visual:                       # 从 spec "验收标准" 中挑视觉可判项
        - "右下 FAB 可见，圆角 + 渐变"
        - "管理模式下 FAB 消失"
        - "本地上传项时间格式为 yyyy.MM.dd 本地上传"
  retry_policy:
    max_rounds: 3                              # 截图→对比→自动修复→重启，最多 3 轮
    on_unrecoverable: keep_verifying           # 无法自动修复时保留 verifying，不升级 done
```

**scope 构建规则**：
- `affected_visual_pages` 中的每条状态都必须出现在 scope 里，不可省略
- `acceptance_visual` 从 spec `## 验收标准` 中提取所有视觉可判项
- 如果 `affected_visual_pages` 为空但 affects 含 `ui:`，说明 Step 3.5/9.5 派生不完整 → 回退补齐

**11b.4 跨端对照判定（由 arkts-visual-verify 执行，此处定义判定规则）**

视觉真值是同期 Android 应用，**不做** "HMOS 改前 baseline 截图"——一来 HMOS 改造已有页面会误判（新增元素被当作回归），二来要求在改代码前截图增加流程负担。

arkts-visual-verify 对 `affected_visual_pages` 每条状态执行：

```
1. HMOS 走 hmos_entry_path → 截图（after）
2. Android 走 android_entry_path → 截图（reference）
3. 多模态对比，按"叠加语义"判定：
   - reference（Android）有的 UI 元素，HMOS 必须存在 + 位置/样式不变（允许像素级微差）
   - HMOS 新增元素允许（属于本次新增功能或 HMOS 设计决策）
   - 已有元素消失 / 位移 / 变形 → 失败
```

**关键判定原则**：
- 视觉对照的目的是"已有功能没坏"，**不是**追求两端像素一致。HMOS 在保留已有元素的前提下做样式适配（如 NavDestination 标题栏样式）允许。
- 当 HMOS 新增元素与 Android 引用图差异巨大（如新增大块区域），多模态可能误判为"位移变形"。此时使用 spec 中 `## 验收标准` 的视觉条目作为补充判定依据：明确属于本次新增的不计入失败。
- 任意一条状态出现"已有元素消失/位移/变形"且无法被验收标准合理解释 → 进 Step 12 回退处理；不得升级 done。

**Android 端不可达时的降级**：
- Android 模拟器未连 / 同状态未实现 → 该条标 `unreachable_reference`，仅做新增功能视觉对齐（11b.2-11b.3），不做对照
- 全部状态都不可达 → spec status 标 `verifying(visual-pending)`，等 Android 端就绪再补

**11b.5 结果回写**

arkts-visual-verify 返回结构化报告后，追加到增量 spec 的 `## 验证记录`：

```markdown
### Step 11a 自动化回归
- dt-verifier filter_acs: F006-AC1, F006-AC3, P0009-UI-SMOKE, P0009-UI-INTERACT_tab
- 结果: 4/4 GREEN（无退化）
- 报告: docs/dt-verification-report.md

### Step 11b 视觉验证
- 新增功能视觉（targeted page_0009 / ItemsView）:
    - 轮数: 2
    - 修复: 第 1 轮 FAB margin-bottom 调整
    - 结果: ✅ 通过（N/N 视觉项命中）
    - 截图留档: spec/features/visual-proofs/F-xxx-after.jpeg
- baseline_screenshots diff:
    - works-my-create-list.jpeg: ✅ 仅本次改动相关差异
    - works-my-collect-tab.jpeg: ✅ 无差异
    - works-manage-mode.jpeg: ✅ 仅本次改动相关差异（checkbox 包裹条件）
```

**Step 12: 完成或回退**

判定矩阵（必须三类验证全部通过才升级 done）：

| Step 10 静态 | Step 11a 自动化回归 | Step 11b 视觉验证 | spec status |
|--------------|---------------------|-------------------|-------------|
| ✅ | ✅（或 N/A） | ✅（或 N/A） | **done** |
| ✅ | ✅，但有 AC 标 manual_verify（子类 C 10 次后） | ✅（或 N/A） | **done(manual-pending)** |
| ✅ | ✅（或 N/A） | 无设备记为"待补" | **verifying(visual-pending)** |
| ✅ | 无设备记为"待补" | 任意 | **verifying(regression-pending)** |
| ✅ | 退化（GREEN→RED） | 任意 | **failed** → 回退处理 |
| ✅ | ✅ | baseline diff 出现"无关差异" | **failed** → 回退处理 |
| ❌ 编译失败 | — | — | **failed** → 回退处理 |

- "待补" 状态在 spec-index.md 同步标注，**不得**升级 done
- 任一 ❌ → 进入回退处理（见下方"回退处理"），spec status: **verifying → failed → pending**
- 退化条目 / 无关差异条目必须在 `## 验证记录` 中显式列出，作为回退依据

---
