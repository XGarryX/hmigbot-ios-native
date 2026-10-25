# 滚动列表 + 沉浸式 banner 的状态栏穿透问题

## 触发场景

- 页面顶部是 banner 图，要"穿过"系统状态栏（沉浸式）
- 页面整体可上下滚动（List / Scroll / WaterFlow / Swiper-of-WaterFlow）
- 用户向下滚动后，列表里的 item（图片/文字）滚到顶端，**透过透明状态栏被看到**，与状态栏的时间/电量图标叠加，视觉混乱

普通页面靠"基座 expandSafeArea + 页内 padding"就够了；这类滚动 + 沉浸式背景的特殊组合需要额外做一层遮罩。

## 直接的几种思路对比

| 方案 | 缺点 |
|---|---|
| 给整个 List 加 `padding({ top: windowTopPadding })` | banner 不再穿过状态栏，**沉浸式破功** |
| 在状态栏区铺一层纯黑 `Column().backgroundColor('#000000')` | 遮挡了 banner 顶部的视觉，沉浸式破功 |
| 用 `clip(true)` 限制 List 高度从 windowTopPadding 起 | 同上：背景缩进 |
| **✅ 在状态栏区铺一层与 banner 同源的 Image 切片** | 视觉上看像是 banner 自然延伸到状态栏，又物理上挡住穿透 |

## 实现方法

把整页用 `Stack({ alignContent: Alignment.TopStart })` 包起来。底层是滚动列表，顶层是固定不滚的 banner-image 切片。

```ts
import { WindowModel } from 'lib_common'
import { AppStorageV2 } from '@kit.ArkUI'

@ComponentV2
struct HomeFragmentComponent {
  @Local windowModel: WindowModel = AppStorageV2.connect(WindowModel, () => new WindowModel())!
  @Local bannerImageRes: Resource = $r('app.media.bg_home_banner')
  @Local bannerAspect: number = 1080 / 768

  build() {
    Stack({ alignContent: Alignment.TopStart }) {

      // ─── 底层：完整 banner + 上下滚动列表 ──────────
      List() {
        ListItem() {
          Image(this.bannerImageRes)        // banner 自身：占整宽 + aspect
            .width('100%')
            .aspectRatio(this.bannerAspect)
            .objectFit(ImageFit.Cover)
        }
        ListItemGroup({ header: this.GroupTabsHeader }) {
          // ... 后续滚动内容 ...
        }
      }
      .width('100%').height('100%')
      .backgroundColor('#000000')           // 列表底色与 banner 暗部色一致

      // ─── 顶层：状态栏区遮罩切片（关键）──────────────
      // 高度恰为系统状态栏高度，宽度全屏，固定不参与滚动
      // 用 banner 图按 aspect 渲染 + clip 把下面截断 → 视觉上像 banner 顶部继续延伸
      Stack({ alignContent: Alignment.TopStart }) {
        Image(this.bannerImageRes)
          .width('100%')
          .aspectRatio(this.bannerAspect)
          .objectFit(ImageFit.Cover)
      }
      .width('100%')
      .height(this.windowModel.windowTopPadding)  // ← 关键：高度 = 安全区
      .clip(true)
      .backgroundColor('#000000')           // 兜底色，图加载前不露白
    }
    .width('100%').height('100%')
    .backgroundColor('#000000')
  }
}
```

## 几个细节

### 为什么用 `aspectRatio` 而不是 `height: '100%'`

切片容器高度只有 `windowTopPadding`（24~50vp），如果 Image 也撑满容器高，banner 会被压成一条窄缝。让 Image 用原图 aspectRatio 渲染（比容器**高**很多），再 `clip(true)` 把超出部分裁掉 → 实际显示的是 banner **顶部那一条**。

### 为什么外层还要再套一个 Stack

只是为了 `clip(true)` 生效更稳定 —— 让外层 Stack 限制高度并 clip，里层 Image 走自己的 aspectRatio。一层 Stack 也能用，但有些版本下 clip 边界容易出 1px 抖动。

### `aspectRatio` 数值怎么定

不是 `windowWidth / windowTopPadding`（那样会拉伸变形），而是**原 banner 图的固有宽高比**（图片像素 width / height）。这样图无论怎么裁，都不变形。

### 切换 banner 时这层切片要不要跟着换

需要。把 `bannerImageRes` 抽成 `@Local` 状态，主 banner 切换时这层切片跟着变。本项目 [HomeFragmentComponent.ets](../../features/business_home/src/main/ets/components/HomeFragmentComponent.ets) 里就是这么做的。

### 是否影响点击事件

这层切片**完全覆盖**状态栏区域。如果状态栏区域下面的 List 内容是可点击的（一般不会，那里是 banner 顶部），需要给切片 Stack 加 `.hitTestBehavior(HitTestMode.Transparent)` 让事件穿透。本项目当前默认状态栏区不接受点击，所以没加。

## 不适用的场景

不要无脑套这套方案：

- 顶部没有沉浸式 banner，只是普通深色背景 → 直接给页面根 Stack 设深色背景就行，不需要切片
- banner 不滚动（位置固定在顶部，列表在 banner 下面） → 不会发生穿透，不需要切片
- 顶部就是想要看到状态栏文字叠加在 banner 上 → 这是"真沉浸式"，不要切片

## 相关代码引用

实测代码：[features/business_home/src/main/ets/components/HomeFragmentComponent.ets](../../features/business_home/src/main/ets/components/HomeFragmentComponent.ets) 末尾的 build() 方法。
