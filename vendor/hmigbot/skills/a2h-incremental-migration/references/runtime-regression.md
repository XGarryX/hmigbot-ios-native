# §S3.6 运行时回归（references 详细版）

主 SKILL.md §S3.6 的详细执行手册。**evolver verify 通过后必跑**，不可绕过。

## 1. 为什么必跑（核心立场）

evolver Verify 阶段三层验证各自只看一个截面：
- Step 10 编译只看**语法**
- Step 11a dt-verifier 只看**断言**
- Step 11b 视觉验证只看**UI 截面**

下游真实业务流是否还能跑通必须由本 skill 在 evolver 收尾后再跑一道运行时回归。

**真实漏检反例（不得重犯）**：
- ❌ "subject tab 截图 ✅ + doc tab 截图 ✅ + 编译 ✅ → F001 PPT 创建主流程不退化" — 错。截图只验 tab 头 UI，没验"输入主题 → 立即生成 → AntiCheat → FreeCount → navigate → outline 页"完整链路
- ❌ "TemplateService.buildCategoryMap 改 async 编译过 → F002 不退化" — 错。await 链路漏一处会运行时崩溃，编译不暴露

## 2. 必跑三类回归

对**每条 evolver 已 done 的 spec**，在收尾前必须跑下面三类，证据落到 `spec/incremental-migration-{date}/runtime-regression-log.md`。

### A. feature_acs 主链路烟雾

**来源**：spec 的 `## 回归范围 → feature_acs`

**步骤**：
1. 读 baseline `spec/baseline/features/F00X.md` 找该 AC 的"用户操作步骤"
2. 真机操作走完整链路：
   - HMOS：`hdc shell uitest` + `dumpLayout` + `uiInput click` 逐步驱动
   - 关键节点截图：`spec/visual-verify/screenshots/regression/F00X-AC{n}_{step}.jpeg`
   - 终态截图与 baseline 期望对照
3. 崩溃 / 行为异常 / 路径中断 → 标 `failed`，回 §S3 修该 spec
4. **禁止**仅用"代码 grep 看起来 OK"作为 PASS；**必须**有命令 stdout 或截图

**执行模板**（写入 runtime-regression-log.md）：
```
[YYYY-MM-DD HH:MM] F001-AC1 输入主题创建 PPT 主流程
  step 1: hdc click 主题输入框 (cx, cy) → 发送文本 "工作总结"
          stdout: "No Error"
          screenshot: regression/F001-AC1_input.jpeg
  step 2: hdc click 立即生成按钮
          aa dump → 当前 ability: CreateOutlinePage ✅（路径到达）
          screenshot: regression/F001-AC1_outline.jpeg
  ...
  result: PASS | FAILED({reason})
```

### B. page_acs UI 交互回归

**来源**：spec 的 `## 回归范围 → page_acs`

对每条 page_ac（如 `page_0009 UI-INTERACT_picker_flow`）：
- 真机点到该交互入口
- 截图前后两态
- multimodal 对比"行为是否如预期"——不仅看 UI，要看副作用（toast / nav / 数据更新）

### C. shared_files 被改函数的 happy path

**来源**：spec 的 `## 回归范围 → shared_files / shared_symbols`

对每个被本次改动**修改过的方法**（不只是新增），找至少一个真实调用方驱动 happy path：

- 例：`TemplateService.buildCategoryMap` 改 async → 真跑 `RecommendView.aboutToAppear` 或 `ChoiceTemplatePage.loadTemplates`，看 categoryList 填充
- 例：`UserTemplateStore.addPath` 改 emit → 真跑"上传 → 切到 RecommendView" 看分类刷新

## 3. visual-verify 完整覆盖

调 arkts-visual-verify 时，`affected_visual_pages` 中**每一个 state_label 都必须有结论**（PASS / FAILED / user_waived）。

**禁止**：
- ❌ 仅以"该状态需要 picker 交互" / "需要前置数据" 为由跳过任何 state_label
- ❌ 推给"人工验证保留"而不调 arkts-scenario-runner 创建对应 scenario
- ❌ 仅跑了子集就升级 spec status 到 done

**必须**：
- ✅ 未声明 scenario 的状态 → 先调 arkts-scenario-runner 写 scenario，再回来跑 visual-verify
- ✅ 所有 state_label 都有结论 + 截图存档；缺任一 → spec status 留 `verifying(visual-pending)`

## 4. 升级 done 的硬条件（同时满足）

| 条件 | 证据 |
|------|------|
| 编译 PASS | hmos-fix-build-errors stdout |
| 静态 grep AC 全部命中 | grep 命令 + stdout |
| feature_acs 全部 PASS | runtime-regression-log.md 每条 AC 步骤 + 截图 |
| page_acs 全部 PASS | 同上 |
| shared_files 改动 happy path 全部跑过 | 同上 |
| affected_visual_pages 全部有结论 | visual-verify 报告 + 截图 |

任一缺失 → 维持 `verifying(*-pending)`，**禁止**升级 done。

## 5. §S4 完成摘要必须暴露的字段

完成摘要"整体状态"段必须新增以下字段（缺即偷懒）：

```yaml
runtime_regression_log: spec/incremental-migration-{date}/runtime-regression-log.md
feature_acs_runtime_pass / fail / pending: <数量>
page_acs_runtime_pass / fail / pending: <数量>
shared_files_runtime_pass / fail / pending: <数量>
visual_verify_state_labels_pass / fail / waived: <数量>
```

**任一 fail/pending 非 0** → 摘要顶部 ⚠️ 醒目标记，不许藏尾部。
