---
name: ios-fact-tree
description: "将已审定 git 源事实、页面和功能规格投影为下游原生关系树；不启动另一套源分析流水线。"
---

> **原生输入边界**：本文件保留 Garry 的目标平台算法、私有 wire 字段和平台对照示例。
> 源输入只来自当前 git facts/semantics/page spec；历史源设备命令和旧语言扫描不适用于 iOS，
> 不得实际调用或用它们的缺省结果表示源端通过。源扫描缺少原生适配时保持 unresolved；
> 当前范围的屏幕采集/设备控制记 not_run。目标 hdc/hvigor 的适用部分也须遵守当前授权。



先读取 [唯一源分析](../ios-source-analysis/SKILL.md) 和 [执行交界](../a2h-run/references/execution-boundary.md)。
该名称只是同一源服务的输入/输出合同适配，不拥有独立 Source、Provider、审批或状态账本。
所有源事实从 git 发布并重验的 ios-facts/ios-semantics/source-index 读取，Swift 词项从同一官方证据读取。

按 ios-ui-graph-builder 的原生四图格式投影已确认的页面、组件、包含和导航边；
同一 page_id/source anchor 保持不变，未知导航和前置态保留 unknown，不以静态图证明运行可达。
按 app-relationship-tree 的丰富/校准合同补充有依据的描述、可达链和功能检查引用。
使用 Garry 原下游 output-contract/connectivity/functional 检查实际验收；失败返回上游补证，不能填空数组绕过。
禁止按 XML/Compose 分支重新扫描 iOS，禁止生成 kt/java 影子源或调用历史 Android 源扫描分支。
图只作为已有源事实的视图；源语义或产品范围变化必须回当前 git spec/plan 受审处理。
