# 参考基线（Ground Truth）

**两个参考工程都视为 100% 合规：**

- `~/Desktop/HUAWEI/wfhc/features/AI`
- `~/Desktop/HUAWEI/wfhc/features/Scan`

任何在**任一**参考工程里出现的写法都不应被 audit 标违规——audit 的边界由两个工程的**并集**定义，不由规范文字字面定义。两工程的**差异**正是规则容忍度的边界提示。

## 两工程的关键差异（揭示规则容忍度）

| 项 | AI 工程 | Scan 工程 | 校准结论 |
|---|---|---|---|
| 根 `oh-package.json5` overrides | **有** | **无** | overrides **MAY**（不是必填，是 best practice） |
| `lib_common` 版本 | 1.1.5 | 1.1.8 | 版本号**按工程当时稳定版**，模板不硬编码 |
| `lib_network` 版本 | 1.0.9 | 1.1.5 | 同上 |
| `lib_widget` 版本 | 1.0.2 | 1.0.8 | 同上 |
| business 模块数 | 7 个（含 video / interaction） | 5 个（基础业务） | business 数量按业务实际范围，不强求 |
| `guidecommponent/Guide*.ets` | 无 | 有，v1 装饰器 | ⚠️ **客户校准为 MUST 全局 v2**：Scan 的 GuideCheckMark v1 残留视为遗留，不再豁免 |
| Feature 级非主页面 VM 未继承 BaseVM | QqShare/WxShareVM | + PreviewVM / UseCountVM | **辅助型 feature VM 不继承也合规** |
| AbortController 实际使用 | 全工程未用 | CropVM / FileOrCardScanVM 用了 | AbortController **真的是可选模式**——可不用，可主动用 |
| png 资源数 | 110 | 172 | png 容忍度高，**MAY**（不是 SHOULD warning） |
| gif | 1 | 2 | 同上 |
| `axios` 单点调用 | ReadCoverCreate | ReadCoverCreate（同样位置） | 特殊场景豁免，**MAY** |
| `import { AbortController/GenericAbortSignal } from '@ohos/axios'` | 无 | 4 处类型导入 | axios 作为类型来源容许（不是 HTTP 调用） |

## 关键校准点

## 关键校准点

下面列出 AI 工程对每条规则的**实际做法**——这才是 audit 的判定基准。规范文字给的是方向和示例，AI 工程给的是落地边界。

### 工程结构（R1）

| 项 | AI 做法 |
|---|---|
| 三段式 products/features/components | 全部齐备 |
| business 命名 | `business_<name>`（home / mine / login / setting / interaction / video / common） |
| module 命名 | `module_<name>`（advertisement / share / swipeplayer / text_reader / transition / setfontsize） |
| AppScope | 项目根级目录（鸿蒙工程标配） |

### 私仓依赖（R2）

| 项 | AI 做法 |
|---|---|
| `.ohpmrc` | 三个 registry：openharmony.cn + bytedance + dadoubk |
| 引入的 lib_* | lib_common 1.1.5 / lib_widget 1.0.2 / lib_network 1.0.9 / lib_payment 1.0.6 / lib_starburst 1.0.1 / lib_umeng 1.0.0 |
| **未引入** | lib_hmiap（说明该项目未启用鸿蒙联运） |
| overrides | 上述 6 个 lib_* 都锁版本 |

### 代码分层（R3）

AI 各 business / module 实际目录命名**多种多样**：

```
business_common: apis / bean / components / constants / db / tool / type / util
business_home:   components / db / model / pages / tool / util / viewmodels
business_login:  components / constants / pages / utils / viewmodels
business_mine:   components / constants / dialog / model / pages / services / types / viewmodels
business_setting: components / pages / types / viewmodels
business_video:  api / components / constants / model / pages / util / viewmodels / vm / workers
business_interaction: common / components / pages / viewmodels
module_share:    buider / componentscreenshot / constants / model / utils / viewmodel / views
module_swipeplayer: components / constants / controller / datasource / models / type / utils / viewmodel / views
module_text_reader: utils / views
module_transition: constants / customtransition / sessions / utils
```

**结论**：
- `viewmodels`（复数）/`utils`（复数）是常态
- `services / types / dialog / model / api / vm / db / tool / workers / views / controller` 等都允许
- audit **不要**按"viewmodel/util/bean 单数"作为判违规依据

### 静态资源（R4）

- AI 工程仍存在 110 个 `.png`（多在 module_swipeplayer/screenshots、AppScope/resources/base/media 等）和 1 个 `.gif`
- 说明 webp/svg 是**优先选择**，存量 png/gif **不强制清理**
- 可以归到"资源体积优化"类的低优先级建议

### 颜色（R5.1）

| color.json 文件 | AI 实际内容 |
|---|---|
| `business_common` | 仅 2 个 token：`cancel_btn_bg`, `common_page_bg` |
| `products/phone` (base) | 19 个自定义命名：`app_theme / app_text_color / btn_*_Color / page_color / theme_color / main_bg_color / cancel_btn_bg / common_page_bg / widget_title_bg ...` |
| `business_mine` | `main_bg_color / my_instant_reply_bg / video_bg / video_duration_bg` |
| 各 module | 各自的业务色（slide_*_color 等） |

**结论**：
- "通用色 19 个 token" 是规范**推荐的同名清单**（便于跨平台迁移），**不是必须包含的硬清单**
- 项目用 `app_theme / text_color / btn_*_Color` 等自有命名是允许的
- audit **不要**把"products/phone 用了 app_theme"标违规
- 也**不要**强制 business_common 包含规范列出的所有 19 个 token

### 状态管理（R6.1）

#### v1 装饰器允许的场景（AI 全部 v1 残留场景）

```
products/phone/.../widget/pages/WidgetCard.ets         # Widget 卡片框架
features/business_common/.../components/DialogBuilder.ets    # Dialog Builder 模式
features/business_home/.../components/HistoryDialog.ets      # Dialog
features/business_home/.../components/NewChatBuilder.ets     # Builder 模式
features/business_mine/.../components/DigitalScrollDetail.ets # 特殊数字滚动组件
components/module_setfontsize/.../components/ButtonGroup.ets # 字号设置按钮组
components/module_swipeplayer/.../views/LandscapeVideo.ets   # 横屏视频特殊组件
components/module_text_reader/.../views/ReadNewsComponent.ets # 阅读组件
```

**规律**（综合 AI + Scan）：v1 残留**历史上**集中在
1. **Widget 卡片**（`widget/` 目录下，HarmonyOS Widget 框架要求）
2. **Dialog 类组件**（`*Dialog.ets / DialogBuilder.ets`）
3. **Builder 模式组件**（`*Builder.ets`）
4. **特殊渲染组件**（数字滚动、视频横屏、阅读文本、字号设置按钮组等）
5. **引导组件**（`guidecommponent/` 目录或 `Guide*.ets` —— Scan 工程的 GuideCheckMark）

> ⚠️ **客户校准（2026-04）**：上述 5 类场景**不再豁免**。客户要求**全局统一 v2 装饰器，无场景例外**——audit 命中任何 v1 装饰器（含上述 5 类）一律 P1 改造。AI / Scan baseline 中残留的 v1 实例视为**遗留待整改**，不作为合规判定依据。

旧豁免逻辑（已废弃）：~~audit 不要把这些场景的 v1 装饰器标违规~~ → 现在所有 v1 都报。

#### LazyForEach（R6.1b）

AI 仍有 3 处 LazyForEach（library work list / dialogue page / video swipe player）——SHOULD 级，不强改。

#### ViewModel 继承（R6.1c）

未继承 BaseViewModel 的 VM 列表（AI + Scan 综合）：

| 工程 | VM | 类型判定 |
|---|---|---|
| AI / Scan | `QqShareViewModel / WxShareViewModel` (module_share) | 简单工具 VM |
| Scan | `PreviewViewModel` (business_home) | feature 级辅助 VM |
| Scan | `UseCountViewModel` (business_common/model) | 计数 / 工具 VM |

**结论**：BaseViewModel 继承的真实约束是**主页面状态容器**——`*PageVM / *PageViewModel` 这种驱动整个复杂页面的 VM。Feature 级辅助 VM、计数 VM、Share 工具 VM 都允许不继承。

**audit 判定**：仅当 VM 命名以 `*PageVM / *PageViewModel` 结尾且未继承 BaseViewModel 时，才提示 P2 warning。其他 *VM / *ViewModel 都视为辅助型，不报。

### 网络（R6.3）

#### HTTP 客户端（R6.3a）

AI 中**有一处** `@ohos/axios` 直调（`module_text_reader/utils/ReadCoverCreate.ets`）——说明**特殊场景容许**绕开 RequestUtil/ExternalReqUtil。可能是文件下载、特殊 header、特殊 content-type 等场景。

audit 应**列为提示**而非违规。

#### interface vs class（R6.3b）

AI 中所有 DTO 类**全部 `extends BaseBean`** 模式：

```ts
export class WorksBean extends BaseBean {...}
export class BarrageBean extends BaseBean {...}
```

`BaseBean` 来自 lib_common，提供反序列化基础能力。这是项目的**标准做法**。

**结论**：
- `extends BaseBean / HSData / 项目基类` 模式**是规范允许的合理写法**
- 只有**裸 class**（无 extends 无方法）才考虑改 interface
- `implements VideoPlayerData` 等 UI 契约约束的也保留 class

#### AbortController（R6.3c / R6.3d / R6.3e）

| 工程 | 实际做法 |
|---|---|
| AI | 全工程**未使用** AbortController |
| Scan | `CropViewModel / FileOrCardScanViewModel` 主动使用 AbortController + signal |

**结论**：AbortController 是规范给的**可选模式**——"如需取消支持时这样做"。两种做法都合规：
- 不用（AI 模式）：完全合规
- 主动用（Scan 模式）：实现了规范的取消能力

audit **不要**把"未使用 AbortController"标违规。仅当工程**已经部分使用了** AbortController 但其他相同业务场景**漏传**时，才提示一致性问题。

### 持久化（R6.4）

AI 中：
- ✓ 简单 KV 走 PreferenceUtil（无 `@ohos.data.preferences` 直调）
- WorksDao 用了 `@ohos.data.relationalStore` 直接 import——这是**项目内部实现关系数据库**的合理场景

**结论**：
- KV 持久化 grep `@ohos.data.preferences` 直调（绕开 PreferenceUtil）→ MUST 改
- 关系数据库 grep `@ohos.data.relationalStore`：如果是封装实现（DAO 层）→ 容许；如果是业务直调（页面/VM 直接拼 SQL）→ 建议改 dataorm（**仍只是 SHOULD**）

### 布局（R6.5）

未在 AI 工程做完整布局检查；按规范严格度处理（多数 SHOULD）。

### build-profile（R6.6）

AI 工程的 `build-profile.json5` **未配置** `buildProfileFields`。

**结论**：`buildProfileFields` **不是必填**——只在工程实际有 三方 key（appName/appBaseType/ChanelId/WXAppId 等）需要管理时才配置。如果项目没有这类 key，不算违规。

---

## audit 边界总结

**真正的 MUST（违反就一定要改）**：
1. 工程**完全没有**三段式骨架（P0）
2. `.ohpmrc` 缺 dadoubk（P0）
3. 没有引入 `lib_common`（P0）
4. 用了网络但没引 `lib_network`（P1）
5. 大面积 v1 状态管理（不是少数特殊场景，是**业务主体**用 v1）
6. 大面积旧 router API（router.pushUrl 等）
7. List/Scroll 内嵌 RelativeContainer（会导致无法滑动 → P0 bug）

**SHOULD（建议改，列 warning，用户决定）**：
- LazyForEach
- 部分 PNG 资源
- 颜色命名跨平台对齐
- 嵌套深度
- 字体 Bold 数值化
- 复杂数据库改 dataorm
- 单 ViewModel 多状态字段但未继承 BaseViewModel

**MAY / 不视为违规（即使命中也别报）**：
- v1 在 widget / dialog / builder / 特殊渲染组件
- axios 在特殊场景（文件下载、特殊 header）
- 自定义颜色命名（business 自有色 + products 主题色）
- 简单工具类 VM 未继承 BaseViewModel
- API 层签名未含 signal（AbortController 是可选）
- 任何 DTO `extends BaseBean / HSData / 项目基类`
- 缺 buildProfileFields（除非用户明确有三方 key）
- LazyForEach 命中点（除非用户说要改 Repeat）
