---
name: arkts-animation-migrate
description: 从 SwiftUI、UIKit、Core Animation 与实际三方动画依赖识别和迁移动画，保留时间、状态、生命周期与取消语义；目标 API 和实现复用 arkts-animation-builder。
metadata:
  type: domain
  domain: ui
  tags:
  - domain
  - ui
  - animation
  - migration
  - lottie
  - transition
  - sharedelement
---

> **0.13.4 统一合同（优先于历史示例）**：先读 [执行交界合同](../a2h-run/references/execution-boundary.md)。源读取、选定构建配置、SwiftSyntax/facts、源 AC 和 indexed 计划由当前 git 上游唯一生产；从 execute 起使用本技能的 Garry 实施/收口方法。只使用宿主实际支持的派发字段，不照抄 `agent_type`。已有授权直接沿用；依赖失败输入的任务保持 blocked，不降低静态门禁。当前范围禁止屏幕读取/截图/录屏及设备远控；依赖这些观察的检查记 not_run。未经授权不运行遥测上传。工具修复、工具验证、项目转换、HAP 构建和完整迁移验收分别报告，不能用局部 100% 代表全部完成。



# arkts-animation-migrate

目标 API 与完整 ArkTS 实现统一复用 [arkts-animation-builder](../arkts-animation-builder/SKILL.md)，不复制一套目标引擎。读取 native-input，源使用同一选定 target/当前配置 Source。

## 1. 定位

沿用识别 → 选型 → 还原 → 验证。读取真实 modifier/调用、资源和可用观测，不把动画改成静态成功图。先核验目标能力/库与配置，再按原决策流程讨论替代；资源、时间和生命周期共同构成行为。

## 2. 触发与原生信号

SwiftUI withAnimation/animation(value:)/transition/matchedGeometryEffect、UIKit UIView.animate/UIViewPropertyAnimator/转场协议、Core Animation 的 CAAnimation/CASpringAnimation、UIImageView 序列帧及实际 Lottie/SVGA/PAG 等依赖均为候选。只按存在的源调用确认，不把文件后缀或图集单独当成使用证据。

## 3. 识别决策

确认实际源框架与动作 → 读取起止状态/触发/时长/单位/延迟/曲线/循环 → 读取完成/中断/取消/重入/后台 → 沿实际资源引用取证 → 按下表路由。共享元素需要真实身份、源/目的几何和容器生命周期；交互转场需要进度与取消恢复，不能只重建一个固定时长动画。

## 4. 分类与参考

| 源行为 | 目标候选 | 参考 |
|---|---|---|
| Lottie 实际播放器/SwiftUI wrapper | 已核验的目标播放器与资源 | references/lottie.md |
| SwiftUI 状态补间 / UIView 属性动画 | .animation / animateTo | references/property-and-tween.md |
| CAKeyframeAnimation / 串并行编排 | keyframe / 显式编排 | 同上 |
| UIImageView.animationImages / 实际解码序列帧 | ImageAnimator | references/frame-and-svga.md |
| SwiftUI transition / UIKit 自定义转场 | transition / 目标导航转场 | references/transitions.md |
| 实际 SVGA 依赖 | 核验目标库或经批准的格式替代 | references/frame-and-svga.md |
| matchedGeometryEffect / UIKit 共享元素式动画 | geometryTransition / 对应导航转场候选 | references/transitions.md |
| SwiftUI spring / CASpringAnimation | 经参数语义核验的目标 spring | references/property-and-tween.md |
| 页面 push/present/dismiss 交互转场 | 目标导航与模态转场 | references/transitions.md |

## 5. 资源

沿 Bundle/Asset Catalog/真实库 bundle 获取 JSON、图集、序列帧、字体和动态替换项；使用 ios-resources-convert 与原 Stage 0 资源登记。保留资源路径、scale、外观/语言与许可，不猜默认源资源目录。

## 6. 实现

目标 V2-first、状态管理和构建规则仍按原领域技能。保留源状态所有权、取消/重入、播放区间、速度、循环、音频/视觉回调和释放时机。源秒与目标毫秒需按实际 API 换算；弹簧参数不承诺跨引擎数字直接等价。

## 7. 验证与缺口

先运行原目标编译；真实截图/录屏/设备行为另行确认。静态分析不冒充观察到真实帧、时长或到态。缺平台 SDK、资源或观测时保留真实缺口和关闭条件，按原占位/产品决策处理。
