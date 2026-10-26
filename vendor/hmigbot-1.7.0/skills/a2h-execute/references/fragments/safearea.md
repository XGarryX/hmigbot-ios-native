# safearea — 沉浸式+安全区

## 不变量：背景穿透 ≠ 前景避让
**先确认这一页真的沉浸**：`meta.needs_immersive_safearea` 由安卓真值机械判定（ImmersionBar 按**实参取值**、主题 windowFullscreen/Translucent、布局 fitsSystemWindows=false；E267）。不沉浸的页交给系统默认避让，一行 L3 都不该写。
沉浸式=背景穿透（`setWindowLayoutFullScreen`+`expandSafeArea`）；安全区=前景避让（`windowTopPadding/windowBottomPadding` 补 padding）。两套禁互替：expandSafeArea 只让背景穿过系统栏，不让内容避开；穿透越彻底，前景越须显式避让。

## 责任分层（固定，禁串位）
| 角色 | 必须做 | 禁止 |
|---|---|---|
| EntryAbility | L1：setWindowLayoutFullScreen(true)+测安全区写 WindowModel+挂 windowSizeChange；`getWindowAvoidArea().topRect/bottomRect` 与 `getWindowProperties().windowRect` 都是 **px**，写 WindowModel 前必须 `px2vp()`（写 px 当 vp 用 = 3x 屏顶出三倍空白，token2 实证） | — |
| 入口页根 Navigation | L2：expandSafeArea([SYSTEM,CUTOUT],四边)，全工程仅此一处——**只在「全部全屏页都是沉浸式」时才写在根上**（E267） | 沉浸式页只是真子集时禁写在根上：L1/L2 都是窗口级，会把非沉浸页也穿透，凭空造出安卓侧不存在的问题再逼它们补 L3 |
| 全屏页（@Entry 或 NavDestination 子页） | L3：前景手动 inset（windowModel padding） | 再写 expandSafeArea（双重穿透） |
| 子组件/overlay | 什么都不做，宿主统一负责 | 订阅 WindowModel／expandSafeArea／自补 padding |

机械检查：`static_runtime_lint.py` 的 `avoid-area-px-as-vp`（落账时自动跑并 `--fix` 原地包 `px2vp()`；未转换的 px 进尺寸参数即报）。

NavDestination 全屏页同样要扛 L3（最常漏）。判定看 page_type／真装饰器 `^@Entry`／build() 根是否 `NavDestination(`，禁 grep "@Entry" 字面串。

## 默认 V2 模板（NavPathStack 子页）
```ts
@ComponentV2
struct MyPage {
  pathStack: NavPathStack = new NavPathStack()
  @Local windowModel: WindowModel = AppStorageV2.connect(WindowModel, () => new WindowModel())!
  build() {
    NavDestination() {
      Stack() {
        Image($r('app.media.bg')).width('100%').height('100%') // 背景铺满
        Column() {
          Row() {/* TitleBar */}.padding({ top: this.windowModel.windowTopPadding + 6 })
          Text('CTA').margin({ bottom: 30 + this.windowModel.windowBottomPadding })
        }
      }
    }
    .hideTitleBar(true)
    .onReady(ctx => { this.pathStack = ctx.pathStack })
  }
}
```
禁在子页再加 expandSafeArea/setWindowLayoutFullScreen；`+6/+30` 是设计稿间距；安全区值禁写死。

## 症状 → 修复
| 症状 | 漏层／检查点 |
|---|---|
| 全 App 顶部灰白边 | L1 setWindowLayoutFullScreen(true) |
| 状态栏文字看不见 | L1 statusBarContentColor 设浅色 |
| 背景顶部留白 | L2 根 Navigation expandSafeArea 四向 |
| router.pushUrl 页顶白边 | 独立页自己 expand（L2 搬到本页） |
| 标题被状态栏盖 | L3 padding({top: windowTopPadding+N}) |
| 底按钮被导航条盖 | L3 margin({bottom: N+windowBottomPadding}) |
| 折叠屏切换 padding 不更新 | L1 windowSizeChange 监听 |
| 滚动内容飘进状态栏 | L4 状态栏遮罩切片方案 |

<!-- source: arkts-immersive-safearea/SKILL.md:L61-83,L144-198,L208-224 -->
