# Navigation 系统路由表（route_map）+ pushDestinationByName

> HarmonyOS 官方**推荐**的动态路由机制，也是**跨模块（HAP/HSP/HAR）导航的唯一标准方式**——比静态 import `@Builder` pageMap 解耦。经 harmony-docs 核验（快照 2026-05-24）。
> 静态 import + 手写 pageMap 仅适合单模块小工程；多模块/可下载 feature/动态页面**必须用系统路由表**。

## 三步配置

### 1. module.json5 注册路由表

```json
{ "module": { "routerMap": "$profile:route_map" } }
```

### 2. `src/main/resources/base/profile/route_map.json`

```json
{
  "routerMap": [
    {
      "name": "PageOne",
      "pageSourceFile": "src/main/ets/pages/PageOne.ets",
      "buildFunction": "PageOneBuilder",
      "data": { "description": "示例页" }
    },
    { "name": "PageTwo", "pageSourceFile": "src/main/ets/pages/PageTwo.ets", "buildFunction": "PageTwoBuilder" }
  ]
}
```

### 3. 页面文件导出 `@Builder`（名字必须等于 `buildFunction`）

```typescript
// src/main/ets/pages/PageOne.ets
@Builder
export function PageOneBuilder() {
  PageOne()
}

@ComponentV2
struct PageOne {
  build() {
    NavDestination() {
      // ...页面内容
    }
  }
}
```

配好后**无需 import、无需手写 `@Builder` pageMap**，直接按 `name` 跳转。

## 跳转：优先 `pushDestinationByName`（防白屏）

```typescript
// ❌ pushPathByName 同步；路由名错 / 页面加载失败时静默白屏，无法捕获
this.pageStack.pushPathByName('PageOne', param)

// ✅ pushDestinationByName 返回 Promise，可 catch → 兜底/重定向错误页
this.pageStack.pushDestinationByName('PageOne', param)
  .catch((e: BusinessError) => {
    // 路由不存在 / 加载失败 → 跳错误页或提示
  })
```

签名：`pushDestinationByName(name: string, param: Object, animated?: boolean): Promise<void>`（API 11+；另有带 `onPop: Callback<PopInfo>` 的重载用于接收返回值）。

## 跨模块（HAP / HSP / HAR）

每个 feature / HSP / HAR 模块各自：① 在自己的 module.json5 配 `"routerMap": "$profile:route_map"`；② 自带 `route_map.json` 注册本模块页面。entry 模块**不需 import** 其他模块的页面文件，按 `name` 跳转即可——这是解耦多模块导航的关键，也是静态 pageMap 做不到的。

## 白屏排查清单

- [ ] 跳转用 `pushDestinationByName`（可 catch），不用 `pushPathByName`
- [ ] `route_map.json` 在 `src/main/resources/base/profile/`，module.json5 已配 `"routerMap": "$profile:route_map"`
- [ ] `buildFunction` 名与页面里 `export function XxxBuilder()` **完全一致**，且 `@Builder` 已 `export`
- [ ] 承载跨模块页面的模块 `type` 为 `har` / `shared`(HSP)（不要放进不被依赖的模块）
- [ ] 子页用的是父级传下来的**同一个** `NavPathStack`，不是 `new NavPathStack()`
- [ ] Previewer 不支持系统路由表，需真机/模拟器验证
