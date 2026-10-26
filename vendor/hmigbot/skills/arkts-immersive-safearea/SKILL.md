---
name: arkts-immersive-safearea
description: 在 ArkTS / HarmonyOS 项目中同时实现"沉浸式背景延伸到全屏"和"前景内容避开状态栏/导航条/挖孔区"的标准方案。当用户提到"沉浸式"、"状态栏遮住内容"、"底部导航条挡住按钮"、"页面顶部白边"、"背景没延伸到状态栏"、"折叠屏适配"、"安全区"、"setWindowLayoutFullScreen"、"expandSafeArea"、"windowTopPadding/windowBottomPadding"，或者新建/迁移 NavDestination 页面时，务必触发此 skill。即使用户只说"页面背景没满屏"或"按钮被系统栏盖住"，也应触发——因为这两类问题 99% 都对应这套四层架构里的某一层缺失。
metadata:
  type: domain
  domain: ui
  tags:
  - domain
  - ui
  - safearea
  - immersive
  - fullscreen
  - navdestination
---
# ArkTS 沉浸式 + 安全区 双解架构

## 这个 skill 解决什么问题

ArkTS 应用经常遇到两类对立又共存的需求：

- **沉浸式**：banner、视频、深色背景需要"穿过"系统状态栏和底部导航条，铺满整个物理屏幕
- **安全区**：页面里的标题、关闭按钮、底部 CTA 按钮**不能**被系统栏盖住

直觉上的"加 padding"或"打开 setWindowLayoutFullScreen"单独都解决不了 —— 必须**两套机制配合**：window 层把整窗扯到屏幕边、容器层声明可越过安全区、页面层手动给前景补 padding。本 skill 把这套配合方法标准化。

## 核心架构：四层

任何一层缺失都会出现可观察的视觉 bug。

```
┌────────────────────────────────────────────────────────────┐
│ Layer 1：EntryAbility.onWindowStageCreate                   │
│   把整个 window 扯到屏幕边，并测量安全区数值                  │
│   ① mainWindow.setWindowLayoutFullScreen(true)              │
│   ② setWindowSystemBarProperties { 透明背景 + 浅色文字 }     │
│   ③ getWindowAvoidArea(TYPE_SYSTEM)         → topRect       │
│   ④ getWindowAvoidArea(TYPE_NAVIGATION_INDICATOR) → bottom  │
│   ⑤ AppStorageV2.connect(WindowModel) 写入 4 字段           │
│   ⑥ on('windowSizeChange') 监听折叠屏/分屏实时更新           │
└────────────────────────────────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────┐
│ Layer 2：根 Navigation（一般在 Index.ets）                   │
│   .expandSafeArea(                                          │
│      [SafeAreaType.SYSTEM, SafeAreaType.CUTOUT],            │
│      [SafeAreaEdge.START, END, TOP, BOTTOM]                 │
│   )                                                         │
│   让 Navigation 容器物理铺满屏幕，背景能"穿过"系统栏。这里只允许容器延伸，不会自动给子组件加 padding │
└────────────────────────────────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────┐
│ Layer 3：业务页面（NavDestination）                          │
│   ① Stack 把背景图/色块铺到 100% × 100%                      │
│   ② 前景内容用 windowModel 手动 padding：                    │
│      TitleBar:  .padding({ top: windowTopPadding + 6 })     │
│      底部 CTA:  .margin({ bottom: 30 + windowBottomPadding })│
│   ③ 页面里**不要**再写 expandSafeArea —— 已被 Layer 2 覆盖  │
│      （例外：router.pushUrl 跳转的独立页见场景 E）            │
└────────────────────────────────────────────────────────────┘
                             ↓
┌────────────────────────────────────────────────────────────┐
│ Layer 4（仅滚动+沉浸式背景的特殊页）：状态栏遮罩切片            │
│   首页 banner + 列表上下滚的特殊组合 → 见 references/scroll-bleed.md │
└────────────────────────────────────────────────────────────┘
```

## 核心不变量 + 责任分层 + 简化路径（必读，先于四层细节）

### 不变量：背景穿透 ≠ 前景避让（两件事，两套机制，不可互相替代）

> **沉浸式 = 背景穿透（让背景越过系统栏）；安全区 = 前景避让（让内容躲开系统栏）。
> 这是两件相反的事，各用各的机制，加哪一个都不能"顺带"解决另一个。**

- 背景穿透：`setWindowLayoutFullScreen`（Layer 1，窗口层）+ `expandSafeArea`（Layer 2，容器层）。开了它，背景铺满屏幕，**但前景也会被推到系统栏底下**。
- 前景避让：用 `windowModel.windowTopPadding / windowBottomPadding` 给前景补 padding（Layer 3）。它**不影响**背景是否穿透。
- 错误心智："我加了 expandSafeArea，内容怎么被状态栏盖住了？"——因为 expandSafeArea 是让背景**穿过**，不是让内容**避开**；穿透越彻底，越需要前景显式避让。

### 责任分层（哪一层归谁，固定，不串位）

| 角色 | 必须做 | 绝不能做 |
|---|---|---|
| **EntryAbility** | Layer 1：`setWindowLayoutFullScreen` + 测量安全区写入 `WindowModel` | — |
| **入口页根 Navigation** | Layer 2：`expandSafeArea([SYSTEM,CUTOUT],[四边])`（全工程通常仅此一处） | — |
| **全屏页（@Entry **或** NavDestination 路由子页）** | Layer 3：前景手动 inset（`windowModel` padding，或复用 `ImmersiveScaffold`） | ❌ 不要再写 `expandSafeArea`（已被 Layer 2 覆盖；重复写 → 双重穿透/错位） |
| **子组件 / overlay（@ComponentV2 非全屏页）** | 什么都不做——安全区由宿主全屏页统一负责 | ❌ 不订阅 WindowModel、❌ 不写 expandSafeArea、❌ 不自补 padding（除非宿主通过 @Param 注入偏移） |

⚠️ **NavDestination 全屏页同样要扛 Layer 3。** Navigation + pageMap 架构下全工程往往只有 1 个 `@Entry`（入口页），其余十几个全屏页都是 NavDestination——它们复用入口的 Layer 1/2，但**前景避让必须自己做**。这是最常见的漏检点。

### 验证原则：按【页面类型】判定，不抓 `@Entry` 字面串

- 判定页面是否需要 Layer 3，看 **page_type**（meta.json 权威源）/ **真装饰器 `^@Entry`** / **build() 根是否 `NavDestination(`），**不要** `grep "@Entry"` 字面串——注释里的"非 @Entry""@Entry 根"会误命中，把子组件当全屏页（假阳性）。
- 验证**必须覆盖 NavDestination 全屏页**，否则只验了 1 个入口页就 PASS，十几个真实全屏页的避让从未被闸住（假阴性）。
- 子组件显式**豁免** Layer 3；若子组件自带 `expandSafeArea` → 告警（双重 inset 风险）。
- 兜底脚本：`.agents/skills/arkts-structural-closure/scripts/check-fullscreen-immersive-safearea.sh`（v2 已按页面类型实现上述判定）。

### 简化路径：能省则省（默认安全 + 仅背景 expand）

1. **优先复用脚手架，别各页手写 padding 数学。** Base-6 提供 `ImmersiveScaffold`（`components/common/ImmersiveScaffold.ets`）——它封装 Layer 3：订阅 WindowModel、按 `insetTop/insetBottom` 开关自动补安全区，页面只管放内容：
   ```ts
   ImmersiveScaffold({ bgColor: '#F9F9F9' }) {
     Column() { /* 前景，自动避让上下系统栏 */ }
   }
   ```
   背景图要穿透系统栏时放进它的 `background` slot（铺满不 inset），前景仍在 `content`（自动 inset）。
2. **"默认安全"优先于"全屏再补回来"。** 若整页前景本就该待在安全区，让它默认 inset 即可（ImmersiveScaffold 默认 `insetTop/insetBottom=true`），**不要**为了"好看"先 expandSafeArea 全屏、再到处手算 `windowTopPadding + N` 把内容怼回安全区——那是把简单问题做复杂。
3. **只有真·edge-to-edge 的元素才单独处理。** 顶部通栏 banner、全屏视频、需要铺到挖孔的背景——把这一个元素从 content 掏出来放进 background slot（或单独 expand），其余前景继续走默认避让。手写 `windowTopPadding + N` 的偏移数学，只应出现在这类元素上，而不是每一页每个控件。

## 三个关键认知（理解 why 比记住 how 更重要）

### 1. "全屏延伸" 和 "安全区" 是两套独立机制

| 机制 | 决定什么 | 谁开 |
|---|---|---|
| `setWindowLayoutFullScreen(true)` | window 是否覆盖系统栏（系统层）| EntryAbility |
| `expandSafeArea(...)` | ArkUI 容器是否绘制到安全区（UI 层）| 根 Navigation |

**两个都打开**背景才能真正铺到屏幕边缘。只开 1 没开 2 → 系统栏物理透明但 ArkUI 容器仍被压在安全区内。只开 2 没开 1 → ArkUI 试图延伸但 window 还有 letterbox。

### 2. ArkUI 不会自动给"前景内容"加避让

`expandSafeArea` **只**解决"容器边界 = 屏幕边界"，状态栏会盖住区域里的子组件。前景必须**手动**加 padding：

```ts
.padding({ top: this.windowModel.windowTopPadding + 6 })   // TitleBar
.margin({ bottom: 30 + this.windowModel.windowBottomPadding })  // 主 CTA
```

`+6` / `+30` 是设计稿要求的额外间距。**安全区是兜底，不是设计高度，不能写死**。

### 3. 用响应式 Model 而不是快照

折叠屏展开/折叠、分屏、悬浮窗、横竖屏切换都会改变安全区。所以：

- **不要**用 `@StorageProp('statusBarHeight')` 单字段订阅，扩展性差
- **要用** `WindowModel`（`@ObservedV2` + `AppStorageV2.connect`），所有页面拿到同一实例，状态变化自动重算 padding
- EntryAbility 必须挂 `windowSizeChange` 监听同步回 WindowModel

## 场景路由（按你的 task 选 reference 文件）

| 场景 | 描述 | 看哪里 |
|---|---|---|
| **新建/迁移普通 NavDestination 页**（V2，最常见）| MainPage 子页、Tab 内容、NavPathStack 子页 | 主文件下面的"默认 V2 模板" |
| **router.pushUrl 跳转的独立 @Entry 页** | 课程详情、设置、编辑器（无 NavPathStack 父级）| [references/router-pushed-pages.md](references/router-pushed-pages.md) |
| **H5 容器壳页**（Web 组件 + jsBridge）| 会员中心、活动页 | [references/h5-container.md](references/h5-container.md) |
| **滚动列表 + 沉浸式 banner** | 首页 banner + 上下滚 | [references/scroll-bleed.md](references/scroll-bleed.md) |
| **V1（@Component）混栈 / 老代码** | 不能用 V2 装饰器的场景 | [references/v1-v2-compat.md](references/v1-v2-compat.md) |
| **Hero 顶部白边 / Image y 不为 0 / BottomBar 飘到顶** | Layer 3 layout 写法触发了 ArkUI 自动让位 | [references/layout-traps.md](references/layout-traps.md) |
| **Android Activity 迁移到 NavDestination** | 见下表"Android 映射" | 主文件下面 |

## 默认 V2 模板（场景 A：MainPage 子页 / NavPathStack 子页）

直接套这个三件套。**不要**再加 `expandSafeArea` 或 `setWindowLayoutFullScreen`（那是基座的事）。

```ts
import { WindowModel } from 'lib_common'
import { AppStorageV2 } from '@kit.ArkUI'

@Builder
export function MyPageBuilder() {
  MyPage()
}

@ComponentV2
struct MyPage {
  pathStack: NavPathStack = new NavPathStack()
  // ① 拉全局 WindowModel
  @Local windowModel: WindowModel = AppStorageV2.connect(WindowModel, () => new WindowModel())!

  build() {
    NavDestination() {
      Stack() {
        // ② 背景占满整个 NavDestination —— 沉浸式
        Image($r('app.media.bg_xxx'))
          .width('100%').height('100%').objectFit(ImageFit.Cover)

        // ③ 前景用 windowModel 补 padding
        Column() {
          // 自绘 TitleBar，避开状态栏
          Row() {
            Image($r('app.media.ic_back')).width(24).height(24)
              .onClick(() => this.pathStack.pop())
            Blank()
            Text('页面标题').fontSize(18).fontColor('#FFFFFF')
            Blank()
          }
          .width('100%').height(56)
          .padding({ top: this.windowModel.windowTopPadding + 6 })

          // ... 中间内容 ...

          // 主 CTA 避开底部导航条
          Text('立即生成')
            .width('90%').height(52)
            .margin({ bottom: 30 + this.windowModel.windowBottomPadding })
        }
        .width('100%').height('100%')
      }
    }
    .hideTitleBar(true)   // 自绘标题栏，禁用系统标题栏
    .onReady((ctx) => { this.pathStack = ctx.pathStack })
  }
}
```

## Android Activity → NavDestination 映射

| Android | ArkTS 等价 |
|---|---|
| `setDecorFitsSystemWindows(false)` | Layer 1 已统一开了 `setWindowLayoutFullScreen(true)`，**不要每页重做** |
| `WindowInsetsCompat.Type.systemBars()` | `windowModel.windowTopPadding + windowBottomPadding` |
| `view.setPadding(0, statusBar, 0, navBar)` | `padding({ top: windowTopPadding, bottom: windowBottomPadding })` |
| `android:fitsSystemWindows="true"` | 不需要，**不要写**单独的 `expandSafeArea` |

## 诊断症状 → 修复路径

| 症状 | 大概率漏的层 | 检查点 |
|---|---|---|
| 整个 App 顶部都有一条灰白边 | Layer 1 | EntryAbility 是否调了 `setWindowLayoutFullScreen(true)` |
| 状态栏文字看不见（黑底黑字）| Layer 1 | `SystemBarProperties.statusBarContentColor` 是否设浅色（`#FFFFFF`）|
| 背景顶部留白，banner 没穿过状态栏 | Layer 2 | 根 Navigation 是否有 `.expandSafeArea([SYSTEM, CUTOUT], 四向)` |
| router.pushUrl 跳转的页面顶部白边 | Layer 2 搬到本页 | 见 [router-pushed-pages.md](references/router-pushed-pages.md) |
| Hero 顶部仍有 ≈30vp 微小白边 | Layer 3 layout 陷阱 | 见 [layout-traps.md](references/layout-traps.md)（陷阱 1+2）|
| Hero Image y 坐标 ≈ 130-400vp | Layer 3 layout 陷阱 | 见 [layout-traps.md](references/layout-traps.md)（陷阱 3）|
| 标题/关闭按钮被状态栏盖住 | Layer 3 | TitleBar 是否有 `padding({ top: windowTopPadding + N })` |
| 底部按钮被导航条盖住 | Layer 3 | 底部按钮是否有 `margin({ bottom: N + windowBottomPadding })` |
| 折叠屏切换形态后 padding 没更新 | Layer 1 监听 | EntryAbility 是否挂了 `windowSizeChange` 同步 WindowModel |
| 滚动列表内容飘到状态栏 | Layer 4 | 见 [scroll-bleed.md](references/scroll-bleed.md) |
| H5 顶部空白条，状态栏区什么都不显示 | 场景 F | 见 [h5-container.md](references/h5-container.md)（native 加了多余 padding-top）|
| 改了"会员中心"完全没生效 | 入口识别错误 | 用 ArkUI Inspector 截图确认实际入口 page，不要按文件名猜 |

## 通用 Anti-pattern（场景特定的看对应 reference）

| ❌ 写法 | 为什么错 | ✅ 正确 |
|---|---|---|
| `padding({ top: 44 })` 写死状态栏高度 | 不同设备 24~50vp，刘海屏更夸张 | 用 `windowTopPadding` |
| 每页自己 `getWindowAvoidArea` 重测 | 重复开销 + 各页不同步 | 只在 EntryAbility 测一次写进 WindowModel |
| 子页面再加 `.expandSafeArea(...)` | 与根 Nav 重复，可能产生双重延伸 | 只根 Nav 写一次（router.pushUrl 跳转的独立页例外）|
| `setWindowLayoutFullScreen` 每个 Ability 都调 | 单 Ability 多页应用没必要 | 只在主 Ability `onWindowStageCreate` 调一次 |
| `windowTopPadding + 6` 里 `+6` 也来自 WindowModel | `+6` 是设计稿固定间距，不是安全区 | 设计稿数值直接写字面量 |
| 把所有 page 都假设是 NavPathStack 子页 | router.pushUrl 跳转的 @Entry 页没有父级 Nav | 见 [router-pushed-pages.md](references/router-pushed-pages.md)|

## 自检 Checklist（改完代码对照一遍）

**Layer 1 - EntryAbility**：
- [ ] 调了 `setWindowLayoutFullScreen(true)`
- [ ] `setWindowSystemBarProperties` 把 statusBar/navigationBar 设为透明（`#00000000`），statusBarContentColor 与主题对比足够
- [ ] `getWindowAvoidArea(TYPE_SYSTEM)` + `TYPE_NAVIGATION_INDICATOR` 都测了
- [ ] `AppStorageV2.connect(WindowModel, ...)` 写入 4 个字段（V1 项目额外 `AppStorage.setOrCreate('statusBarHeight'/'bottomAvoidHeight')`）
- [ ] 挂了 `windowSizeChange` 监听同步回 WindowModel

**Layer 2 - 根 Navigation**：
- [ ] `expandSafeArea([SYSTEM, CUTOUT], [START, END, TOP, BOTTOM])` 四向都开
- [ ] 类型不是 `SafeAreaType.KEYBOARD`（输入法不应被穿透）

**Layer 3 - 每个 NavDestination**：
- [ ] V2 用 `@Local windowModel = AppStorageV2.connect(WindowModel, ...)`，padding 用 `windowTopPadding`/`windowBottomPadding`
- [ ] 自绘 TitleBar 的 padding-top 用了 `<安全区> + N`；底部主按钮 margin-bottom 用了 `N + <安全区>`
- [ ] 没多此一举写 `.expandSafeArea(...)`（router.pushUrl 跳转的独立页例外）
- [ ] `.hideTitleBar(true)` 关掉系统标题栏

**特殊场景**（按需进 reference 详看）：
- [ ] router.pushUrl 跳转的独立 @Entry 页 → [router-pushed-pages.md](references/router-pushed-pages.md)
- [ ] H5 容器（Web 壳页）→ [h5-container.md](references/h5-container.md)
- [ ] Hero / Scroll / BottomBar 组合 layout 异常 → [layout-traps.md](references/layout-traps.md)
- [ ] V1 / 混栈 → [v1-v2-compat.md](references/v1-v2-compat.md)
- [ ] 滚动 + 沉浸式 banner → [scroll-bleed.md](references/scroll-bleed.md)

## 输出格式

被触发时按场景选**其中一种**输出（不要全部输出）：

- **新建普通页** → 主文件的"默认 V2 模板" + Layer 1-3 自检表
- **诊断现有 bug** → 用"诊断症状 → 修复路径"对照症状，先确认页面是 V1 还是 V2（看装饰器），给出**具体哪几行**要改 + patch
- **router.pushUrl 跳转独立页** → 读 [router-pushed-pages.md](references/router-pushed-pages.md) 给完整模板，强调本页根容器必须自己加四向 expandSafeArea
- **H5 容器壳页**（关键词：H5、WebView、jsBridge、handleClosePage、cs_*_webview_activity.xml）→ 读 [h5-container.md](references/h5-container.md) 给模板；提醒"先 Inspector 确认入口" + "TitleBar 通常应完全移除" + "三路径关闭对齐"
- **layout 陷阱**（顶部白边 / Image y 不对 / BottomBar 飘到顶）→ 读 [layout-traps.md](references/layout-traps.md) 对照陷阱 1-6
- **V1 / 混栈** → 读 [v1-v2-compat.md](references/v1-v2-compat.md) 给 V1 模板和决策树
- **滚动 + banner** → 读 [scroll-bleed.md](references/scroll-bleed.md)，简述切片图层思路

任何场景最后附 Layer 1-3 自检 Checklist。

## 相关文件

- [references/v1-v2-compat.md](references/v1-v2-compat.md) — V1/V2 双栈兼容 + V1 页面模板
- [references/router-pushed-pages.md](references/router-pushed-pages.md) — 场景 E：router.pushUrl 跳转的独立 @Entry 页
- [references/h5-container.md](references/h5-container.md) — 场景 F：H5 容器（Web 壳页）的沉浸式
- [references/layout-traps.md](references/layout-traps.md) — Layer 3 layout 陷阱大全（Hero / Scroll / BottomBar 组合异常）
- [references/scroll-bleed.md](references/scroll-bleed.md) — 滚动列表 + 沉浸式 banner 状态栏穿透解法


---

## See Also

- [arkts-truncation-fix](../arkts-truncation-fix/SKILL.md) — 文本截断 / 折叠屏布局 / 多设备响应式断点（本 skill 不覆盖这些场景）
- [arkts-video-playback](../arkts-video-playback/SKILL.md) — 视频横屏特化（letterbox 钉视频帧、防进度条遮挡），边界精确化见 video-playback §0.2
- [arkts-customer-service](../arkts-customer-service/SKILL.md) / [arkts-ad](../arkts-ad/SKILL.md) — 调用方典型场景（聊天页全屏 / 开屏广告）


## 主题状态栏色的合法落点（与 theme_brief/theme_gate 的接口，2026-08-25）

Android 主题声明了状态栏色（`android:statusBarColor` 或框架缺省）而页面走本 skill 四层架构时：
- Layer 1 仍按本契约把系统栏设**透明**——不得为了主题色改回不透明系统栏；
- 主题状态栏色由**页面顶部背景**承载：顶部安全区高度的背景色（或专用色条）取该主题色，
  视觉效果等价于 Android 的着色状态栏；
- 该色经 `$r('app.color.*')` 绑定（theme_gate 对账点）；`setWindowSystemBarProperties`
  路径只吃字符串色值，走该路径时豁免 `$r` 强制（写常量并注明来源于 resolved-theme）；
- 主题状态栏色为**透明**（#00...）时即本契约的原生形态，无需任何附加动作。
