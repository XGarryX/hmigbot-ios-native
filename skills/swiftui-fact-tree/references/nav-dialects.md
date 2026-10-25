# SwiftUI / UIKit 导航方言

使用 A1 和 native-input 的同一入口口径：App/Scene、WindowGroup、NavigationStack/path、NavigationLink/value/destination、TabView selection、sheet/fullScreenCover/popover/alert、UIKit push/present/segue 与真实 URL 处理。没有标准导航容器时沿根视图的状态分支和自定义路由封装追踪，不发明路由字符串。

逐条记录调用方/触发、条件、目标、参数、宿主、返回/取消及异步状态；动态目的地未解出则 unknown。嵌套导航栈与每个 Tab 的独立栈分开，页面声明与实际可达性分开。UIKit representable/hosting bridge 追双向生命周期和状态所有权。源路径使用选定 Release Source；公共图查询走原生 query_graph.py。
