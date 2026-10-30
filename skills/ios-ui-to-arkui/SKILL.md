---

name: ios-ui-to-arkui
description: 按已审批 iOS 页面规格和 indexed 计划分批转换 SwiftUI/UIKit 为 ArkUI，复用 a2h-execute 的收尾、覆盖与编译协议。
metadata:
  type: domain
  domain: migration
  tags:
  - migration
  - ios
  - native-ui
  - arkui
---

When runtime UI validation is selected, preserve explicitly evidenced source accessibility identifiers on the corresponding target controls using the applicable ArkUI `.id()` capability and check uniqueness in the affected screen. Preserve source anchors and the target control selector in the optional source-to-target UI mapping. Do not add identifiers to the read-only iOS source, confuse SwiftUI structural identity with accessibility identity, or require a map for every dynamic/inaccessible node as a new global migration gate. Missing mapping becomes a scoped validation gap. The existing `scripts/ui_validation_evidence.py bind-mapping` / `pair --control-mapping` entrypoints and `docs/APP-UI-VALIDATION.md` define the current protocol.

> **0.13.4 统一合同（优先于历史示例）**：先读 [执行交界合同](../a2h-run/references/execution-boundary.md)。源读取、选定构建配置、SwiftSyntax/facts、源 AC 和 indexed 计划由当前 git 上游唯一生产；从 execute 起使用本技能的 Garry 实施/收口方法。只使用宿主实际支持的派发字段，不照抄 `agent_type`。已有授权直接沿用；依赖失败输入的任务保持 blocked，不降低静态门禁。权限按交界合同区分：禁止桌面远控；指定测试应用/模拟器的截图、控件查询和固定回放可按已确认范围执行，Preview 不证明业务运行。录屏及未指定设备不在此授权内，未执行项如实记 not_run。未经授权不运行遥测上传。工具修复、工具验证、项目转换、HAP 构建和完整迁移验收分别报告，不能用局部 100% 代表全部完成。



# iOS 页面批量转换

先读 ios-source-analysis/SKILL.md，按真实 SwiftUI/UIKit/Storyboard/XIB 页面、选定 Xcode target 和 Release 视图读取来源。该技能服务原 a2h-execute Stage 1，不另建第二套状态账本或迁移流水线。

1. 消费 spec/execution/source-ui/manifest.json、ui-snapshots、页面规格和 ui-plan.md 的 batch 归属；所有源文件经 Source 读取，不调用退休的 scan_ios_ui.ps1/deep_verify.ps1 源扫描器。原 Phase A 的语义补充和覆盖核对不能省略。
   manifest/meta 中的 runtime_observations 是单独绑定的原生截图与控件树，UI 作者必须按本页检查点实际读取；view.xml 仍是静态 outline，不能因此丢掉原图，也不能把全局 runtime_observed=false 误读为所有页面都未采集。逐页核对 runtime_observed_checkpoints，只用已采状态辅助布局，不将其推广到全部分支或源默认值。若原页面仍写本次 screenshot=null/runtime=not_run，回原页面作者消除已采范围内的矛盾，不自行改写源语义或旧历史结论。
2. 按 ui-plan 的既定 batch 执行，读取 a2h-execute/references/agent-prompts/1-converter.md 以及 a2h-ios-converter 角色；限定独占文件，不改其他 owner 产物。
3. 映射 State/Binding/Observable、ForEach identity、UIKit delegate/生命周期、容器和模态；来源结构、约束、样式、图标与动态显隐均须有真实证据。规格中未知的尺寸不能假装是观测值。
4. 页面、列表行、弹窗、菜单、子容器和路由目标逐项覆盖；支持 custom drawing/媒体/后台等接缝时按计划绑定专项技能，不能以本技能视觉骨架代替功能。临时 FWD-REF/占位只按原 execute 协议登记并在收尾清零，不擅自以 TODO 结项。
5. 按原 batch-closer 收口、覆盖与资源残量检查、真实 hvigor 编译门执行；仅原 writer 写账本，不能按文件存在写完成。

映射提示见 references/ios-to-arkui-mapping.md；复杂模式见 references/unsupported-patterns.md。目标布局尺寸、安全区、V2 装饰器、原收尾与编译要求保持不变。
