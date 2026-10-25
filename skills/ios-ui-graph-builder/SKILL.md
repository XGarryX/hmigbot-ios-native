---
name: ios-ui-graph-builder
description: 从 SwiftUI/UIKit、Storyboard/XIB 与真实观测生成 iOS 页面关系图和三源元数据，保留原 schema 和后续语义补充步骤。
metadata:
  type: domain
  domain: migration
---

# Native UI Graph Builder

沿用 1.5.2 的七步分工：源码识别与导航语义由分析者完成，ID/关联校验由原脚本完成。先读 [原生输入协议](../a2h-spec/references/native-input.md) 和 `references/schema_v2.md`。通用 wire 槽位保留，正式组件身份使用 ios_id。值必须是真实 iOS 类型/语言；静态分析分组使用 analysis:semantic_region，不能冒充 SDK 类型或运行时坐标。

1. **READ schema**：读取四文件字段、ID、空值和边约束。iOS Screen.type 可为 App/Scene/UIViewController/SwiftUIView/Dialog/Sheet；language=Swift/Objective-C。`activity`/`parent_activity` 是历史关联字段，不代表 iOS 运行环境。
2. **SCAN**：用共享 Source 上下文枚举选中 Release target 的源文件、Storyboard/XIB、Asset Catalog、生命周期与真实导航定义。先辨 SwiftUI / UIKit / 混合，不按文件名数量猜页面。
3. **EXTRACT screens（语义）**：区分 App/Scene 根、可导航页面、Tab/嵌套子页、模态与普通可复用 View。读完整入口、条件和生命周期；为 Screen.json 提供真实类型、来源、主题/安全区线索，未知值按原 schema 披露。
4. **PARSE layouts（机械 + 源码补充）**：已有设备层级优先保留其来源；否则用 `scripts/synthesize_meta_json.py` 和 `scripts/synthesize_view_xml.py` 生成静态骨架。补充 SwiftUI 状态/Binding/ForEach 身份/modifier 次序、UIKit 约束/委托、IB outlet/action/segue；合成 outline 不冒充精确布局树。Component、Containment 使用原 ID/父子约定。
5. **EXTRACT navigation（语义）**：沿 NavigationStack/path、NavigationLink、sheet/fullScreenCover、Tab、push/present、segue 追踪触发、目的页、参数、返回与取消；动态路由明确未知，不发明边。
6. **MERGE and ENRICH**：汇合原四文件，保持节点 ID 唯一、层级与触发可追溯，补导航、样式、资源和交互说明。不得因脚本没检出就省略二三级页。
7. **VALIDATE**：运行原图完整性/引用校验；修复重复 ID、悬空边和缺字段。通过原生入口的只读临时字段适配复用原编译校验器，原错误、警告和退出码保留；不得在正式图补兼容身份键。每次保留原输出和正式图/视图哈希，查询结果使用 ios_id。

输出仍是 Screen.json、Component.json、Navigation_Edge.json、Containment_Edge.json；Phase A 再按这些材料生成原 snapshot。JSON、源码小片段属于内部分析证据，分页 Markdown 是独立可读的规格书。
