<!-- when: 理解三源数据消费顺序 / 评估大型项目 Phase 策略时加载 -->
<!-- topics: 三源数据原则, view.xml, meta.json, 源码 layout, 大型项目支持, 上下文窗口管理 -->

# 三源数据原则 + 大型项目支持（背景）

## 三源数据原则

a2h-spec Phase A 准备的三源数据是整个 v2 架构的基础。核心原则：

**结构以 view.xml 为准，样式以源码为准，语义以 meta.json 为准。**

| 信息类型 | view.xml | meta.json | 源码 layout XML |
|---------|----------|-----------|----------------|
| 视图层级结构 | **主**（运行时真实层级） | — | 辅（静态定义） |
| bounds 坐标/尺寸 | **主**（精确像素） | — | — |
| 可见性状态 | **主**（运行时真实） | — | 辅（默认值） |
| 文本内容 | 有（运行时值） | 有（语义补充） | 有（默认值/resource ref） |
| 颜色/字体/样式 | **无** | — | **主**（完整样式定义） |
| 主题/Style 继承 | **无** | — | **主**（themes.xml + styles.xml） |
| Drawable/图标引用 | **无** | 部分（icon 字段） | **主**（`@drawable/ic_home`） |
| 资源名 | **无** | — | **主**（`@string/home_label`） |
| 导航目标 | **无** | **主**（navigation_targets） | — |
| 点击路径/页面关系 | **无** | **主**（click_path, came_from） | — |
| Activity/Fragment 映射 | **无** | **主**（activity 字段） | — |

a2h-activity-converter 消费顺序：
1. 读 meta.json → 理解"这个页面是什么、能做什么"
2. 读 view.xml → 构建精确的视图层级树
3. 读源码 layout XML + styles.xml + themes.xml → 补充样式、颜色、资源引用
4. 交叉验证：view.xml 层级 vs 源码 layout 层级，以 view.xml 为准，源码补充样式
5. 读 screenshot.png（如有）→ 最终视觉校验

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
