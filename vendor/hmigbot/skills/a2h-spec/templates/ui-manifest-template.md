<!-- when: Phase B Step B1 生成 ui-manifest.md 时加载 -->
<!-- topics: ui-manifest, 页面清单, 全局约定, 页面状态生命周期, 转换批次, 共享组件 -->

# ui-manifest.md 模板

必填字段：全局约定（导航架构 / 设计令牌 / 命名规范 / 图标方案 / **沉浸式 + 安全区四件套**）、页面清单表（序号 / Android / ArkTS 产出 / 优先级 / confidence / 状态）、页面状态生命周期、转换批次、共享组件表。

```markdown
# UI Manifest

## 全局约定
- 导航架构: Navigation + NavPathStack（单 Navigation 容器 + NavDestination 子页面）
- 设计令牌: <按项目实际设计系统完整列出 — 不预设 token 数量、命名、分组方式；
      源在 Kotlin/Compose 时记录 .kt 文件路径与每个 token 的字面值/语义；
      源在 XML 资源时记录 colors.xml/themes.xml 关键 ref；
      如有 light/dark/gradient/typography/shape 子系统按项目结构分别列出>
- 命名规范: 页面 XxxPage.ets，组件 XxxComponent.ets
- 图标方案: SVG 资源 $r('app.media.ic_xxx')
- **沉浸式 + 安全区**：本工程全屏页统一采用 [arkts-immersive-safearea](../arkts-immersive-safearea/SKILL.md) 四层架构（API 细节由该 skill 维护，spec 不重复以避免漂移）；每页是否需要由 meta.json `needs_immersive_safearea` 字段决定

## 页面清单
| 序号 | Android | ArkTS 产出 | 优先级 | confidence | 状态 |
|------|---------|-----------|--------|-----------|------|
| 0001 | MainActivity | MainPage.ets | P0 | high | pending |
| 0002 | HomeFragment | HomePage.ets | P0 | high | pending |
| 0003 | QueueFragment | QueuePage.ets | P0 | medium | pending |
| ... |

### 页面状态生命周期
pending → converted → verified
- pending: 待转换
- converted: UI 已转换，等待验证
- verified: 编译通过 + 切片级功能验证通过
- skipped: 本轮不转换（V2 范围外）

## 转换批次
- Batch 1 (P0): 0001-0005 (App Shell + Home + 核心列表页)
- Batch 2 (P0): 0006-0010 (播放器 + 订阅 + 搜索)
- Batch 3 (P1): 0011-0016 (下载 + 统计 + 设置)
- Batch 4 (P2): 0017-0023 (次要页面)

## 共享组件
| 组件 | 用于页面 | Android 来源 |
|------|---------|-------------|
| ExternalPlayerBar | MainPage | external_player_fragment.xml |
| NavDrawer | MainPage | nav_list.xml |
| EpisodeListItem | Queue, Inbox, AllEpisodes | ... |
```

全局约定的推导逻辑：
- **导航架构**：从 AndroidManifest.xml 的 Activity 数量 + Navigation Component 使用情况推断。单 Activity + NavHost → NavPathStack，多 Activity → 评估是否合并
- **设计令牌**：从 `styles.xml` / `themes.xml` / `colors.xml` 提取主色、文字色、背景色
- **命名规范**：Activity → Page，Fragment → Page 或 Component（依据是否独立导航）
- **图标方案**：扫描 `res/drawable*` 目录，确定图标格式（SVG/PNG/VectorDrawable）
- **沉浸式 + 安全区**：本节展示全工程统一的标准方案（4 Layer）；**每页是否需要产出对应配置由 `meta.json` 的 `page_type` / `needs_immersive_safearea` 字段自动决定**（见 `android-ui-graph-builder/scripts/synthesize_meta_json.py` 的 `detect_page_type()`）—— 本段无需再做词汇判定

优先级分配规则：
- P0：Launcher Activity + 其直接 Fragment + 核心业务页面
- P1：次级功能页面（设置、搜索、下载管理等）
- P2：辅助页面（关于、许可证、同步设置等）
