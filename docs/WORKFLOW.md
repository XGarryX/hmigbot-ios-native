当前默认交界见 [执行交界合同](../skills/a2h-run/references/execution-boundary.md)：init/spec/plan 由 git 主导，从 execute 起使用 Garry indexed 阶段与七项验证。文中旧 v2 四拍/四项描述仅适用于原冻结合同兼容。

# 原 a2h 流水线中的原生 iOS 路径

入口为 [a2h-run](../skills/a2h-run/SKILL.md)。初始化使用 source_platform=ios 与真实源、目标目录。
完整细分步骤、各步 skill/MCP、产物和阶段交接见 [README 流水线](../README.md#迁移流水线细分步骤与阶段交接)。
0.7.0 在 spec 中按固定清单加载外部 iOS 专业资料、保存审阅，并可采集真实源 MCP 证据；
`source-check --harness` 验收记录合同，plan-ir 冻结资料/审阅/工具证据。实际接入见
[外部能力规程](../skills/ios-source-analysis/references/external-expertise.md)。

1. **spec**：ios-source-analysis 编排工程、UI、功能、API 四个源技能；形成源证据、分页/功能规格、原生语义和决策。
2. **plan**：保留 P0 归属、P1 UI/Base/Slice、P2 汇总；indexed-v1、wires、integration_points、覆盖矩阵与稳定 AC 不变。
3. **execute**：资源前置 → UI 批次 → Base → Feature Slice → 组接线与最终结构闭包 → 编译；使用原 ArkTS 领域技能和唯一写入协议。
4. **verify**：静态/身份、已选范围视觉与 UT；源 oracle 从 iOS 源码/独立测试/真实运行提取，保留原设计、生成、执行、修复步骤。
5. **retrospect**：根据实际完成、失败和差异复盘，规则变更有证据和范围。原运行时阶段记录只作为恢复线索。

0.13.5 的子任务收口按 [Join 规则](../skills/a2h-join/SKILL.md) 读取本轮可信宿主状态/原生终答，再验当前轮次产物。Execute 的 UI Batch 与 Slice Group 按 [资源增量协议](../skills/a2h-execute/references/resource-deltas.md) 在派发前登记完整任务；worker 提交增量，唯一 closer 统一合并，原 writeback 入口核验当前合并收据和计划归属。旧冻结合同变化按受审 replan 恢复。

共同控制面为 spec/.a2h/open-findings.json；各检查只改自己的分区。
requirements-index → plan-coverage → impl-claims → verification 保留独立真值与验收强度。
没有设备时保留 DEFERRED；源版本变化重开受影响事项，不只更新指纹。

源锚点字段为 source_anchors / source_anchors_ref。原生事实伴随文件 ios-semantics.json 不代替 Markdown 规格。
源码已分析、规格已生成、目标已编译、功能已验证分别记录；当前用户范围和授权优先。

参见 [spec 规程](../skills/a2h-spec/SKILL.md)、[原生事实契约](../skills/ios-source-analysis/references/native-facts.md)、
[plan 输入](../skills/a2h-plan/references/ios-source-protocol.md)、[execute 输入](../skills/a2h-execute/references/ios-source-protocol.md)、
[verify 输入](../skills/a2h-verify/references/ios-source-protocol.md)。
