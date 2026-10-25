<!-- when: 理解三源数据消费顺序 / 评估大型项目 Phase 策略时加载 -->
# 三源数据原则 + 大型项目支持（背景）

## 三源数据原则

三源保持原 meta.json、view.xml、真实源码/资源。结构以 view.xml 的已记录来源为准、样式看真实源码/资源、语义看经核对的 meta.json。静态合成不是运行观测，不能因字段名或 XML 文件存在而提高 confidence。

| 信息类型 | view.xml | meta.json | 原生源码/资源 |
|---|---|---|---|
| 层级/显隐 | 真实观测或明确标注 synthesized 的静态结构 | 语义和状态条件 | SwiftUI 组合、UIKit/IB 约束与运行条件 |
| bounds/单位 | 仅真实观测可填，记录 points/pixels 与截图 scale；静态合成未知 | 保留证据来源 | frame/约束和实际逐图 scale，不猜倍率 |
| 文本/样式 | 仅反映实际可采集字段 | 语义补充 | strings/xcstrings、Asset Catalog、SwiftUI environment/modifier、UIKit UIAppearance |
| 主题继承 | 不假装包含完整着色规则 | 相关来源 | 实际环境/容器/appearance 与深浅变体 |
| 图片/符号 | 仅实际观测 | 标识及依据 | 实际 Image/UIImage、SF Symbol、Asset Catalog |
| 导航与页面映射 | 已观测层级只是当次状态 | navigation_targets/click_path/came_from；activity 值为真实原生类型 | App/Scene、路由、Tab/模态、UIKit push/present/segue 真实入口 |

converter 消费顺序保持：
1. meta.json 了解页面、操作与条件；规范化槽位不是 SDK 类型。
2. view.xml 读取已核对层级，区分真实观测与静态合成，不把未知坐标当精确值。
3. 选定 Source 的 Swift/Objective-C、Storyboard/XIB、Asset Catalog 和字符串资源补样式、身份与行为。
4. 交叉核对层级、当前状态与实际源码；静态合成有误须回补，不能用词法骨架推翻真实源语义。
5. screenshot.png 如有则核对实际尺寸/scale与可见状态；无图不能声称视觉验证。

## 大型项目支持

| 项目规模 | 页面数 | Phase A 策略 | Phase B/C 策略 |
|---------|--------|-------------|---------------|
| 小 | <10 | 全量批量 | 单文件 feature-index 足够 |
| 中 | 10-30 | 全量批量 | 2-3 个 feature 组 |
| 大 | 30-100 | 批量 + 按需混合 | 按模块分组 feature |
| 超大 | 100+ | 按模块拆分子项目 | 每模块独立 feature-index |

上下文窗口管理：
- spec 文件按业务复杂度组织，不强制行数上限——保持单文件主题聚焦即可（一页一文件 / 一功能一文件 / 全局总览一文件）
- `ui-snapshots` 数据由 agent 按需读取，不预加载

原生单位口径：源码 frame/约束的 point 数值以 1 point → 1 vp 作为布局基准，视口适配按本轮规格处理；字体 point 数值按目标 fp/动态字体策略核对。不得把 points 当 pixels 后再除设备密度。仅原始图片/截图 pixels 按真实逐图 scale 或观测坐标单位换算，不使用默认倍率。目标引擎常量不改，图片守卫仍拒收无源证据的尺寸自愈。
