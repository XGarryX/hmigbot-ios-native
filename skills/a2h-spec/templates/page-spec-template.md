<!-- when: Phase B Step B2 生成分页 ui/page_NNNN.md 时加载 -->
<!-- topics: 分页 spec, source_anchors, 溯源, 转换决策, 状态接口, 导航关系 -->

# 分页 UI Spec 模板

必填字段：文件级 source_anchors YAML、溯源、页面结构、转换决策、状态接口、导航关系、沉浸式与安全区。写成可独立理解和验收的规格，不复制页面实现充当正文。以下为通用示例，名称、路径、值和状态必须从当前源工程读取。

````markdown
# page_0001: HomeView

```yaml
source_anchors:
  HomePage: "App/Views/HomeView.swift"
  ItemRow: "App/Views/Components/ItemRow.swift"
```

## 溯源
- iOS 页面: HomeView
- 原生 UI 源: App/Views/HomeView.swift
- UI 快照: ui-snapshots/page_0001_HomeView/
- 输出文件: entry/src/main/ets/pages/HomePage.ets
- 证据: 静态源分析；无设备观测时不声明实际 bounds

## 页面结构
- 顶部: 页面标题及当前状态摘要
- 内容: 列表、加载态、空态和错误态，具体文案以源码为准
- 底部: 主操作入口，保留启用、禁用和进行中状态
- 浮层: 仅在源端确有对应条件时展示

## 转换决策
| iOS 组件 | ArkUI 组件 | 决策理由 |
|---|---|---|
| NavigationStack | Navigation + NavPathStack | 保留目的页、参数、返回和深链语义 |
| List / ForEach | List / ForEach | 保留稳定标识、滚动和列表状态 |
| sheet | 对应模态承载 | 保留显示条件、取消和关闭回调 |

## 状态接口（供 Feature Pipeline 对接）
| @Local 变量 | 类型 | 数据来源 | 关联功能 |
|---|---|---|---|
| loading | boolean | 当前功能加载状态 | F001 |
| items | ItemModel[] | 源数据列表 | F001 |
| errorMessage | string | 当前操作错误 | F001 |

## 导航关系
| 触发 | 目标页面 | 类型 |
|---|---|---|
| 点击列表项 | page_0002_DetailView | push；携带真实标识 |
| 关闭模态 | 来源页面 | dismiss；保留取消/返回语义 |

## 沉浸式 + 安全区
本页面 needs_immersive_safearea = {读取 meta.json}，page_type = {读取 meta.json}。
全屏页按 arkts-immersive-safearea 四层架构实施；模态、对话框与子组件填实际配置，由 converter 按类型处理。记录源 safeAreaInset/ignoresSafeArea 或 UIKit inset 的真实意图。
````

生成规则：

- source_anchors 是文件级对应，填写当前 target/Release 范围中的真实 Swift/Objective-C 文件；多个文件共同实现时全部列明，不要求一控件一 AC。
- 结构和转换决策来源于三源材料；缺设备观测时使用静态层级与自适应尺寸，不编造运行坐标。
- 状态接口读源状态、Binding、Observable/@Published、委托和持久化，保留行为与所有权。
- 导航写触发、前置条件、参数、目的页、返回和取消，不以代码块替代行为说明。
- 共享组件和复杂控件必须能沿锚点回到真实源文件，缺失时依原占位和门禁规则处理。
