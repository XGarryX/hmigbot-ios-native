# 原生语义阅读规程

语言与 UI 框架分开建模：Swift/Objective-C/Objective-C++/C/C++ 是语言；
SwiftUI/UIKit/Interface Builder/引擎承载是界面实现形态。单工程可同时包含多种。

## SwiftUI

先保存 body 组合和 modifier 的顺序，再解释状态与副作用。StateObject 的创建归属、
ObservedObject 的借用、Observable/Bindable 的引用及 Binding 的 get/set 都不能仅按
外观映射装饰器。保存 structural/explicit identity、ForEach ID 和身份变化后的状态重建。
task(id:) 重启与取消、onAppear 可重复进入、Environment 的覆盖范围需要单独写证据。
NavigationPath 值和 destination 分派是数据驱动导航，不能只保留目的页面名。

## UIKit / IB / 桥接

控制器生命周期不等于视图创建次数；present、容器嵌入、交互取消均会改变回调链。
IBOutlet/IBAction 只是连接入口，要继续追实际 handler；Auto Layout 优先级和激活条件
不能压成固定尺寸。diffable data source 标识、cell reuse、delegate weak 引用影响状态。
SwiftUI/UIKit 桥接保存 Coordinator、make/update/dismantle 及上下游状态反馈。

## 业务与语言

Swift 的值复制、Optional、关联值枚举、异步错误与取消、actor 隔离；Objective-C 的
nil messaging、nullability、block capture、ARC、KVO、selector 动态分派；桥接的
数值范围、字符串编码、指针/句柄/缓冲区生命周期，都由调用链中的影响决定是否迁移。
网络/数据库/存储/平台能力分析要保留失败、重试、权限拒绝、应用重启后的行为。

## 证据强度

源码位置能支持静态行为解释；AST 支持语法结构；符号服务支持解析后的引用关系；
构建支持选定配置可编译；运行记录支持已观察场景。不能互相升级或补造不存在的测试。
未能解释的动态分派/宏/闭源模块进入未知清单，仍继续独立部分分析。
