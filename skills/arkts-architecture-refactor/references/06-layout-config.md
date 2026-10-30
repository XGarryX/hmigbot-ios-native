# 布局 + build-profile 配置（R6.5/R6.6）

> ⚠️ **客户校准**（2026-04）：本节多条规则严格度上调。
> - **R6.5a（沉浸式安全距）从 SHOULD 升 MUST** —— 鸿蒙工程**必须**预留顶/底安全距
> - **R6.5b-1（List/Grid 列数动态化）升 MUST** —— List 的 `lanes` / Grid 的 `columnsTemplate` **必须**通过 `BreakpointModel`（私仓）动态获取
> - **R6.5b-2（普通容器多端适配）保持 SHOULD** —— 优先 GridRow/GridCol，phone-only 项目可豁免
> - **R6.6（buildProfileFields）升 MUST** —— 壳工程**必须**配置 app 基础信息（appName/appBaseType/ChanelId 必填）
> - 仅 R6.5c（嵌套深）/ R6.5e（build() 长度）保持 SHOULD
> - R6.5d（List/Scroll 内 RelativeContainer 导致无法滑动）保持 MUST



## 范围说明：R5.3 页面间距（**仅页面级**）

规范原文："**页面左右间距**...统一采用 BreakpointModel.pagePadding"——只指**页面最外层容器**的左右 padding，**不包括组件内部 padding、卡片内 padding、Item padding 等**。audit 时不要把所有 `padding({left:N})` 命中都标违规。

```ts
// ✅ 页面外层用 pagePadding——是 R5.3 的目标
@ComponentV2
struct HomePage {
  build() {
    Column() { /* ... */ }
      .padding({ left: this.vm.breakpoint.pagePadding,
                 right: this.vm.breakpoint.pagePadding })
  }
}

// ✅ 卡片内部 padding 写死 16 是合理的，不算违规
@ComponentV2
struct GoodsCard {
  build() {
    Column() {
      Image($r('app.media.cover')).padding(8)   // 组件内距，不属"页面间距"
      Text(this.title).padding({ top: 4 })
    }.padding(16)                                // 卡片自身 padding
  }
}
```

## R6.5a 沉浸式安全距（**MUST**——客户已升级严格度）

> **客户校准**（2026-04）：从 SHOULD 升为 MUST。鸿蒙的实现**必须**预留**顶部 + 底部**安全距离——使用 `WindowModel`（私仓 lib_common）的 `windowTopPadding` / `windowBottomPadding`。**禁止**写死 `padding({top: 36})` / `padding({bottom: 24})` 这种固定值。


```ts
@ComponentV2
struct HomePage {
  @Local vm: HomeViewModel = new HomeViewModel();
  build() {
    Column() {
      // 头部
    }
    .padding({
      top: this.vm.windowTopPadding,
      bottom: this.vm.windowBottomPadding,
    })
  }
}
```

`BaseViewModel` 已经从 `AppStorageV2.connect(WindowModel)` 取好这两个值，组件直接用。**禁止**写死 `padding({ top: 36 })` 这种顶部高度。

## R6.5b 折叠屏 / 小窗：动态布局（**MUST**——客户已升级 List/Grid 子项）

> **客户校准**（2026-04）：所有布局应使用动态布局以适配折叠屏 / 小窗；**特别地**：
> - **R6.5b-1（List 的 `lanes` / Grid 的 `columnsTemplate`）→ MUST**：必须通过 `BreakpointModel`（私仓 lib_common）动态获取，**禁止**写死如 `lanes(2)` / `columnsTemplate('1fr 1fr')`
> - **R6.5b-2（普通容器布局）→ SHOULD**：优先 GridRow + GridCol + BreakpointModel（私仓）；仅 phone-only 项目可豁免

### List / Grid 必须动态列数（MUST 样例）

```ts
import { BreakpointModel } from 'lib_common';   // 私仓
import { AppStorageV2 } from '@kit.ArkUI';

@ComponentV2
struct GoodsList {
  @Local breakpoint: BreakpointModel = AppStorageV2.connect(BreakpointModel)!;

  build() {
    // ✅ 正例：lanes 由 breakpoint 动态算
    List() { /* ... */ }.lanes(this.breakpoint.gridColumns)
    // 或 BaseViewModel 已暴露：.lanes(this.vm.breakpoint.gridColumns)

    // ❌ 反例：写死 lanes(2)、columnsTemplate('1fr 1fr')
  }
}
```

### 普通容器：GridRow + GridCol（SHOULD）

```ts
import { BreakpointModel } from 'lib_common';

@ComponentV2
struct GoodsList {
  @Local vm: GoodsViewModel = new GoodsViewModel();
  build() {
    GridRow({
      columns: { sm: 4, md: 8, lg: 12 },
    }) {
      ForEach(this.vm.goods, (g: Goods) => {
        GridCol({ span: { sm: 2, md: 4, lg: 4 } }) {
          GoodsCard({ data: g })
        }
      })
    }
  }
}

// 或在 List/Grid 里动态取列数
List() { /* ... */ }.lanes(this.vm.breakpoint.gridColumns)
```

## R6.5c 减少嵌套，用 RelativeContainer（SHOULD）

```
Stack > Column > Row > Stack > Column > ... （超 4 层）
```

考虑用 `RelativeContainer` 摊平：

```ts
RelativeContainer() {
  Image($r('app.media.cover'))
    .alignRules({ top: { anchor: '__container__', align: VerticalAlign.Top } })
    .id('cover')

  Text(this.title)
    .alignRules({ top: { anchor: 'cover', align: VerticalAlign.Bottom } })
    .id('title')
}
```

## R6.5d List/Scroll 子节点禁用 RelativeContainer（**MUST**——会导致无法滑动）

`RelativeContainer` 没有内在尺寸——子项放进 `List`/`Scroll` 里会撑满高度，导致整个列表无法滚动。

修法：把 RelativeContainer 内的子项重新组合成 Column/Row，或外层加固定高度。

## R6.6 build-profile 三方 key 配置（**MUST**——客户已升级严格度）

> **客户校准**（2026-04）：从 MAY 升 MUST。壳工程 `build-profile.json5` **必须**配置 `buildProfileFields`。即使工程没有 WX/umeng 等三方 key，**`appName / appBaseType / ChanelId` 三个基础字段也必须填**（运营基础信息）。三方 key 按工程实际有的再加。

`build-profile.json5` 在 modules → 壳工程模块（products/phone）的 `targets[].config.buildOption.arkOptions.buildProfileFields` 节点：

```json5
{
  "name": "default",
  "runtimeOS": "HarmonyOS",
  "config": {
    "buildOption": {
      "arkOptions": {
        "buildProfileFields": {
          "appName": "我的应用",
          "appBaseType": "ai",
          "ChanelId": "10001",
          "WXAppId": "wxxxxxxxxxxxxxxxx",
          "WXAppSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
          "umengId": "xxxxxxxxxxxxxxxxxxxxxxxx"
        }
      }
    },
    "deviceType": ["phone", "tablet"]
  }
}
```

模板见 `assets/build-profile-target.template.json5`。三方 key 不要硬编码到 .ets 源码里——通过 `BuildProfile.<key>` 读取，便于多渠道分包。
