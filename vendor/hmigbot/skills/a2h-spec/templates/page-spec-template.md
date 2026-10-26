<!-- when: Phase B Step B2 生成分页 ui/page_NNNN.md 时加载 -->
<!-- topics: 分页 spec, android_source_anchors, 溯源, 转换决策, 状态接口, 导航关系 -->

# 分页 UI Spec 模板

必填字段：顶部 `android_source_anchors` YAML（stub-name → Kotlin/Java 源文件，文件级）、溯源、页面结构、转换决策表、状态接口表（@Local 变量供 Feature Pipeline 对接）、导航关系表、**沉浸式 + 安全区配置**（仅入口页 / Tab 页 / 含全屏背景的页面需填）。

````markdown
# page_0001: MainActivity

```yaml
android_source_anchors:                # 文件级，stub-name → Kotlin/Java 源文件路径
  SmartCourseComponent: "app/src/main/java/com/example/holder/GySmartClazzHolder.kt"
  PartFiveBubblePage:   "app/src/main/java/com/example/ui/PartFiveBubblePage.kt"
```

## 溯源
- Android Activity: de.danoeh.antennapod.activity.MainActivity
- 源码布局: app/src/main/res/layout/main.xml
- UI 快照: ui-snapshots/page_0001_MainActivity/
- 输出文件: entry/src/main/ets/pages/MainPage.ets

## 页面结构
- 根布局: DrawerLayout → SideBarContainer
- 内容区: CoordinatorLayout → Stack
- 底部导航: BottomNavigationView → Tabs (4 tabs + More popup)
- 外部播放器: ExternalPlayerFragment → ExternalPlayerBar

## 转换决策
| Android 组件 | ArkUI 组件 | 决策理由 |
|-------------|-----------|---------|
| DrawerLayout | SideBarContainer(Overlay) | 官方侧边栏容器 |
| BottomNavigationView | Tabs(BarPosition.End) | 底部 Tab 标准实现 |
| CoordinatorLayout | Stack(Alignment.Bottom) | 叠加布局 + 底部对齐 |

## 状态接口（供 Feature Pipeline 对接）
| @Local 变量 | 类型 | 数据来源 | 关联功能 |
|------------|------|---------|---------|
| isPlaying | boolean | PlaybackService | F001-playback |
| episodeTitle | string | PlaybackService.currentItem | F001-playback |
| currentTabIndex | number | 本地 UI 状态 | — |
| sideBarShow | boolean | 本地 UI 状态 | — |

## 导航关系
| 触发 | 目标页面 | 类型 |
|------|---------|------|
| Tab: Home | page_0002_HomeFragment | Tab 切换 |
| Tab: Queue | page_0003_QueueFragment | Tab 切换 |
| Tab: More | BottomNavigationMorePopup | 弹出菜单 |
| ExternalPlayerBar 点击 | AudioPlayerPage | 页面跳转 |
| 侧边栏: Settings | PreferencePage | 页面跳转 |

## 沉浸式 + 安全区

本页面 `needs_immersive_safearea = {读 meta.json 字段值}`（基于 `page_type = {读 meta.json 字段值}` 自动判定）。
- `true` → converter 按 [arkts-immersive-safearea](../arkts-immersive-safearea/SKILL.md) 四层架构实施（spec 不列 API 以避免与 skill 漂移）
- `false`（modal_overlay / dialog / sub_component）→ converter 跳过本契约
````

分页 Spec 的生成逻辑：
- **android_source_anchors（顶部 YAML 块）**：识别页面里所有 stub 引用（转换时需追溯 Android 源码理解的复杂组件，如自定义 ViewHolder、自定义 ViewGroup、运行时绑定的 Item 模板）。对每个 stub 名（用 ArkTS 端期望的组件名作 key），扫描 Android 工程中匹配的 Kotlin/Java 源文件，记录**文件级**路径（不到行号）。下游 a2h-activity-converter 遇到 stub 时**必须**读对应源文件再生成 ArkTS，缺 anchor → FAIL（见 a2h-execute §3a 占位即 FAIL 规则）。
  - 扫描策略：stub 名 ↔ `*ViewHolder.kt` / `*Component.kt` / `*View.kt` / `*Adapter.kt` / `*Page.kt` 命名约定匹配；命中多个时全部记录。
  - 自动扫描遗漏时 → 留空，由 converter 触发 FAIL 暴露 → 人工补 anchor。
- **溯源**：从 Phase A 的分析结果直接提取
- **页面结构**：读取 view.xml（或合成版）的层级树，提取主要 ViewGroup 结构，对应到 ArkUI 组件
- **转换决策**：对每个关键 Android 组件，记录选择的 ArkUI 替代方案和理由
- **状态接口**：扫描源码中的成员变量、LiveData/Flow 订阅、SharedPreferences 读取，预定义 @Local 变量
- **导航关系**：从 Phase A Step A2 的导航分析结果提取
