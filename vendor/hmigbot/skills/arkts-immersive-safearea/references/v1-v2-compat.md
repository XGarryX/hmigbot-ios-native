# V1 / V2 双栈兼容（@StorageProp vs WindowModel）

> **触发场景**：项目里 V2（`@ComponentV2 + @Local + AppStorageV2`）和 V1（`@Component + @State + @StorageProp`）共存，或当前要修改的 page 用了 V1 装饰器。

## 总原则

- **基座一份就够**：EntryAbility / 根 Navigation 同时支撑两套，**不用**每页改基座。
- **页面层订阅方式按装饰器选**：V2 用 `WindowModel`，V1 用 `@StorageProp` 单字段。
- **同一 struct 内不混用装饰器**：编译会报错或运行时不刷新。

---

## 基座侧：双写两个入口（已对齐项目现状）

EntryAbility 在 `onWindowStageCreate` 里**同时**写两份，缺一不可：

```ts
// V1 入口：单字段写到 AppStorage（V1 的 @StorageProp 直接读）
AppStorage.setOrCreate('statusBarHeight', statusBarHeight)
AppStorage.setOrCreate('bottomAvoidHeight', bottomAvoidHeight)

// V2 入口：写到 WindowModel（V2 的 AppStorageV2.connect 订阅整个对象）
const windowModel = AppStorageV2.connect(WindowModel, () => new WindowModel())!
windowModel.windowTopPadding = statusBarHeight
windowModel.windowBottomPadding = bottomAvoidHeight
windowModel.windowWidth = px2vp(rect.width)
windowModel.windowHeight = px2vp(rect.height)
```

**字段命名差异（容易踩坑）**：
- V1 用 `statusBarHeight` / `bottomAvoidHeight`（与历史项目保持一致）
- V2 用 `windowTopPadding` / `windowBottomPadding`（语义更通用）
- 数值是相同的（都来自同一次 `getWindowAvoidArea`），只是键名不同

---

## V1 页面模板

```ts
@Builder
export function MyPageBuilder() {
  MyPage()
}

@Component
struct MyPage {
  pathStack: NavPathStack = new NavPathStack()
  // 单字段订阅，类型必须是 number，提供合理默认值（避免首次渲染 NaN）
  @StorageProp('statusBarHeight') statusBarHeight: number = 36
  @StorageProp('bottomAvoidHeight') bottomAvoidHeight: number = 28

  build() {
    NavDestination() {
      Stack() {
        Image($r('app.media.bg_xxx'))
          .width('100%').height('100%').objectFit(ImageFit.Cover)

        Column() {
          Row() {
            Image($r('app.media.ic_back')).width(24).height(24)
              .onClick(() => this.pathStack.pop())
            Blank()
            Text('页面标题').fontSize(18).fontColor('#FFFFFF')
            Blank()
          }
          .width('100%').height(56)
          .padding({ top: this.statusBarHeight + 6 })   // ← 用 V1 字段

          Text('立即生成')
            .width('90%').height(52)
            .margin({ bottom: 30 + this.bottomAvoidHeight })   // ← 用 V1 字段
        }
        .width('100%').height('100%')
      }
    }
    .hideTitleBar(true)
    .onReady((ctx) => { this.pathStack = ctx.pathStack })
  }
}
```

---

## V1 必须知道的 5 件事

1. **不能与 V2 装饰器混用**：同一个 struct 里不能既有 `@StorageProp` 又有 `@Local`；同样 `@Component` 不能用 `@Param`。混用会编译报错。如果父组件是 V2、子组件是 V1（或反过来），传值通过 props 显式传，不要跨版本共享状态。

2. **默认值必须给**：`@StorageProp` 在 EntryAbility 还没写入前会取默认值；不给默认值首次渲染会 NaN/undefined，padding 计算后变成 0 → 页面跳一下。常用默认 `statusBarHeight: 36` / `bottomAvoidHeight: 28`（多数设备的合理估计）。

3. **`@StorageProp` 是只读单向同步**：AppStorage 改 → 组件刷新；组件改本地副本不会回写。要双向用 `@StorageLink`，但安全区数值无须双向。

4. **折叠屏 size change 不触发 V1 字段更新**：项目当前 `windowSizeChange` 监听只写回 V2 WindowModel 的 width/height，**不**重新调 `getWindowAvoidArea` 也**不**回写 V1 的 statusBarHeight/bottomAvoidHeight。如果 V1 页要响应折叠屏切形态，需要在监听里**额外**加 `AppStorage.setOrCreate('statusBarHeight', ...)`。但实际多数设备折叠前后 statusBar 高度不变，业务可不处理。

5. **V1 不能 `connect(WindowModel)`**：`AppStorageV2.connect` 返回的对象内部用 `@ObservedV2` + `@Trace` 实现响应式，V1 组件无法监听其字段变化（即便能拿到引用，UI 也不会刷新）。V1 必须走 `@StorageProp` 单字段路径。

---

## V1 / V2 选择决策树

```
新页 / 新模块？             → V2（@ComponentV2）
迁移自 Android 的页？        → V2（统一新写法）
父组件是 V2？               → 子组件也用 V2
依赖某个还没升级 V2 的子组件？ → 父用 V1，等子组件升级后整体迁
混合栈实在不可避免？         → 父子界面间通过 props 显式传 statusBarHeight，不要混用装饰器
```

---

## 常见错误与对策

| ❌ 写法 | 为什么错 | ✅ 正确 |
|---|---|---|
| V2 组件里写 `@StorageProp` / V1 组件里写 `@Local` | 装饰器混用，编译报错或运行时不刷新 | 同一 struct 内不混用 |
| V1 里 `@StorageProp` 不给默认值 | 首帧 undefined，padding=NaN，UI 跳变 | 写默认值 `: number = 36`（top）/ `: number = 28`（bottom） |
| ~~一律用 `@StorageProp('statusBarHeight')`~~ | 单字段订阅，扩展时要改所有页面 | V2 页用 `WindowModel`；只有 V1 才用 `@StorageProp` |
