---
name: ios-view-to-arkui
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

# iOS 页面批量转换

先读 a2h-spec/references/native-input.md，按真实 SwiftUI/UIKit/Storyboard/XIB 页面、选定 Xcode target 和 Release 视图读取来源。该技能服务原 a2h-execute Stage 1，不另建第二套状态账本或迁移流水线。

1. 消费 spec/baseline/ui-manifest.json、ui-snapshots、页面规格和 ui-plan.md 的 batch 归属；所有源文件经 Source 读取，不调用退休的 scan_ios_ui.ps1/deep_verify.ps1 源扫描器。原 Phase A 的语义补充和覆盖核对不能省略。
2. 按 ui-plan 的既定 batch 执行，读取 a2h-execute/references/agent-prompts/1-converter.md 以及 a2h-ios-converter 角色；限定独占文件，不改其他 owner 产物。
3. 映射 State/Binding/Observable、ForEach identity、UIKit delegate/生命周期、容器和模态；来源结构、约束、样式、图标与动态显隐均须有真实证据。规格中未知的尺寸不能假装是观测值。
4. 页面、列表行、弹窗、菜单、子容器和路由目标逐项覆盖；支持 custom drawing/媒体/后台等接缝时按计划绑定专项技能，不能以本技能视觉骨架代替功能。临时 FWD-REF/占位只按原 execute 协议登记并在收尾清零，不擅自以 TODO 结项。
5. 按原 batch-closer 收口、覆盖与资源残量检查、真实 hvigor 编译门执行；仅原 writer 写账本，不能按文件存在写完成。

映射提示见 references/ios-to-arkui-mapping.md；复杂模式见 references/unsupported-patterns.md。目标布局尺寸、安全区、V2 装饰器、原收尾与编译要求保持不变。
