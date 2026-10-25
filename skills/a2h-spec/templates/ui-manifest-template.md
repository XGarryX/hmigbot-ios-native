<!-- when: Phase B Step B1 生成 ui-manifest.md 时加载 -->
<!-- topics: ui-manifest, 页面清单, 全局约定, 页面状态生命周期, 转换批次, 共享组件 -->

# UI Manifest 模板

保留全局约定、页面清单、状态生命周期、转换批次及共享组件字段。页面名称、令牌、批次和数量由实际源工程确定。

```markdown
# UI Manifest

## 全局约定
- 导航架构: Navigation + NavPathStack，保留源 Tab、模态、深链和返回契约
- 设计令牌: 从 SwiftUI/UIKit 样式及 Asset Catalog 读取，列实际路径、数值、单位与语义，分别说明 light/dark、字体、形状与渐变
- 命名规范: 页面 XxxPage.ets，复用组件 XxxComponent.ets
- 图标方案: 转换实际图片或选定目标符号，SF Symbols 不按位图密度猜尺寸
- 沉浸式 + 安全区: 全屏页采用 arkts-immersive-safearea 四层架构，每页按 meta.json 的 page_type / needs_immersive_safearea 决定

## 页面清单
| 序号 | iOS | ArkTS 产出 | 优先级 | confidence | 状态 |
|---|---|---|---|---|---|
| 0001 | HomeView | HomePage.ets | P0 | medium | pending |
| 0002 | DetailView | DetailPage.ets | P0 | medium | pending |

### 页面状态生命周期
pending → converted → verified
- pending: 待转换
- converted: UI 已转换，等待验证
- verified: 编译与该切片所需功能验证通过，不得仅凭文件存在设置
- skipped: 有明确本轮范围决定，附决策引用

## 转换批次
- Batch 1 (P0): 实际入口、核心 Tab 和主操作路径
- 后续批次: 按真实依赖、优先级和并行规则分组

## 共享组件
| 组件 | 用于页面 | iOS 来源 |
|---|---|---|
| ItemRow | Home, Search | App/Views/Components/ItemRow.swift |
```

从 App/Scene、UIKit 控制器、Storyboard/XIB、SwiftUI 路由、Tab 和模态识别导航；复用 View 不自动成为页面。设计令牌与资源来自当前选定源，保存深浅色和安全区语义。P0 为入口及核心路径，P1 为次级业务，P2 为辅助页面。状态、批次和字段的下游含义沿用原流程。
