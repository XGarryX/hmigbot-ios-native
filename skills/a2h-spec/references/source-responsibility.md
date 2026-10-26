# 原生源责任与活动目标投影

本合同用于已批准的依赖内部、测试目标或替代边界。它不改变原始 ios-facts.json、ios-obligations.json、源 unknown 和稳定 AC。

`spec/baseline/ios-responsibility.json` 可选；未提供时保留原有全部义务/AC和严格 unknown 阻断。提供错误、过期或不完整载荷时阻断，不降级回未启用模式。文件存在不等于内容及调用链闭合。

## 必需证据

- schema_version=1、source_platform=ios、当前 source_sha256 与 graph_sha256。
- product_context：原 source_build 证据、选定的 project/scheme/target/configuration/sdk/architecture 和真实可回放的 v3 条件捕获。
- review：当前文件摘要、application/dependency/test 角色及包归属、全部事实的入口/调用路由、独立复核者、未决项。review 引用固定项目文件并核对摘要，不能由工具填“已审”。
- boundaries：唯一 ID、kind、精确源路径/起止行/符号/字节摘要、原 obligation_ids、真实公开调用与 active AC、skip-list 精确标题。禁止通配整目录排除。test_target 需由原构建成员证明；头文件和资源不能由粗略成员集排除。
- replacements：原 canonical `spec/decision-ledger.md` 已批准且有授权依据的决策、精确替代边界、原 superseded AC 与当前 emits AC、历史/目标动作、语义私有与应用部分。应用历史方法另需原源 AC 行、方法区域、每项义务的 source_ac_bindings 与受审替代责任。

完整字段由 `src/hmigbot_ios/source_responsibility.py` 统一校验；不能另写简化判断器。原 traceability helper 在临时目录重新计算 all / active_target / source_history，既有 requirements-index.json 不是审批依据。

## 保留与拒绝条件

私有 unknown 可拆成明确 parts：私有部分保留 unknown、原因和事实；存续 app 部分仍为普通 known，逐项校验证据、fact_ids 和完整 typed state 值。不能将应用回调、HUD、清理或错误路径整体归入私有未知。

历史动作只允许绑定原 history AC、原源方法/真值及本次精确替代边界。目标动作至少消费本决策一个 emit，可同时消费没有 decision_ref 的普通 active app AC；后者仍必须有 coverage、计划与验收归属。混合历史与活动动作不能整体退休。

`unused_symbol` 当前没有完整可重放可达性证明协议，保持拒绝。没有词法调用、unused 标签或一句“死代码”均不足以排除动态入口义务。

历史 coverage mapping 保留、ac_ids=[] 且引用准确 responsibility_ref；产品 mapping 只能消费 active_target AC。报告分别列 all/product/historical 义务和 all/active_target/source_history AC。计数变化不增加生成、编译或行为进度。

## 候选、落盘与冻结

`spec-authoring` 可通过显式 responsibility 输入审核候选，返回候选内容与依赖摘要，不写 baseline，不授权派发。项目 owner 复核落盘后重新运行：

```text
spec-check --project <target>
source-check --project <target> --harness
```

readonly 审计须加 `source-check --harness --report-only`。事实/提取规则变化后由原 facts 工具重生成，再复审语义、责任载荷和 coverage 的新图绑定，不能手改机器事实。

plan-ir、next-batch 与 land-results 消费同一持久化投影；决策、独立审阅、skip-list、语义、页面锚点、源图、构建/条件证据及原解析器/工具规则共同冻结。任一变化必须重审/replan，不能以候选覆盖冻结输入。

工具审计、发布和项目转换按 [结果分离规则](../../a2h-run/references/tool-project-status-separation.md) 独立记账。
