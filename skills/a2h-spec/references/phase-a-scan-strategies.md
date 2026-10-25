<!-- when: Phase A 语义富化 meta.json 时加载 -->
# Phase A 原生 UI 扩展分析

对选定 target/Release 的每个真实页面补充以下语义。脚本只生成骨架，不承诺自动提取完整层级、导航或数值边界。

- 动态菜单：SwiftUI Menu/Toolbar/Tab、UIKit UIMenu/UIAction 与配置数据，追选中状态、显隐、溢出和点击作用。
- 模态与底部面板：sheet/fullScreenCover/alert/confirmationDialog、presentationDetents 与 UIKit presentation controller；记录绑定的呈现条件、交互关闭、返回/取消、safe area 和状态恢复。
- 列表：List/ForEach/LazyVStack、UITableView/UICollectionView 的 cell/section/diffable data source，保留稳定 identity、复用、刷新/分页和行事件；不能每个可复用 View 都注册为页面。
- 子视图与路由：NavigationStack/path/navigationDestination、Tab、导航控制器/容器、Storyboard segue、deep link；追参数、返回结果与真实路由标识，不能从类型名编造可达路径。
- 状态与生命周期：State/Binding/Observable、Combine、task/onAppear/onDisappear、UIKit delegate，记录所有权、异步取消、重新进入、前后台及权限状态。

meta.json 保持原接口：activity=真实原生页面类型；layout_sources=Swift/ObjC/Storyboard/XIB；style_sources=Asset/appearance/environment 来源；navigation_targets=真实目的地/条件；clickable_elements=真实控件或动作标识、可见文案和可访问标签。没有观测的 bounds 为未知，synthesized=true，不能填设备坐标。

dynamic_menus/bottom_sheet_config/recycler_item_layouts/fragment_tags 等保留字段按真实菜单/模态/列表/路由语义填写并注明来源；无对应项为空，不虚构源构造。关联节点和实际页面 ID 继续走原 manifest/page/snapshot 契约。
