# 原生转场与共享元素迁移

## 1. 进入/离开转场

读取 SwiftUI transition + withAnimation、UIKit UIViewControllerAnimatedTransitioning/transitionCoordinator、实际 animator 与 containerView；记录触发、几何、时间、曲线、遮挡、完成与取消。目标复用 arkts-animation-builder 的 transition/显式动画及导航技能，不凭相似名字宣称直接等价。

## 2. 同页共享元素

matchedGeometryEffect 必须记录 namespace、id、isSource、properties、anchor 及两个视图是否同时存在。目标 geometryTransition 是候选，需核验实际布局与重入，不将 source 的 identity 原样当目标运行时 ID。

## 3. 跨页/模态共享元素

源导航/展示与对象生命周期共同决定源/目的快照和返回路径。选择目标 Navigation 自定义转场或经核验的共享转场能力，保留路由参数、返回结果、源滚动位置与可见性；不要为动画新增隐藏入口或破坏页面结构。

## 4. 交互转场

UIPercentDrivenInteractiveTransition 或手势驱动 progress 必须保留开始/更新/完成/取消阈值与恢复。取消不是完成；不能用固定时间动画加空回调代替真实恢复。并发转场与重复触发沿源 guard 处理。

## 5. 页面生命周期与验证

保留 push/pop/present/dismiss、interactive dismiss、回调时机与释放。目标 onReady/appear/disappear 及导航回调不与源生命周期逐名等同；按实际行为接线。目标 API/版本按随包 SDK 资料核验，原编译门保留；视觉和行为需真实执行才可称通过。
