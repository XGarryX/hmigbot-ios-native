# 迁移模式参考（含 V1 历史 — Legacy）

> ⚠️ **本项目锁 ArkTS V2**。本文档主要覆盖**两类迁移**：
>
> 1. **API 11- → API 12（V1 升 V1，与 V2 无关）**：`@ohos.*` → `@kit.*` 导入迁移、`router` → `Navigation` 路由迁移、V1 `@Prop` 必须初始化、V1 `@Link` 去 `$` 前缀。下文 §1 / §2 / §3 / §4 / §5 章节代码示例使用 V1 装饰器（`@Component / @State / @Prop / @Link`）作为参考。
> 2. **V1 → V2 装饰器迁移**：参阅本目录 [`v2-migration-patterns.md`](./v2-migration-patterns.md)（13 类映射 + `@Link / @StorageLink` 等结构性改写）。
>
> 推荐升级路径：先按本文档将老项目升至 API 12 V1 基线 → 再按 [`v2-migration-patterns.md`](./v2-migration-patterns.md) 升至 V2。已是 API 12+ V1 项目可直接走 V2 迁移。
>
> **新代码请直接使用 V2 装饰器**：`@ComponentV2 / @Local / @Param / @Param+@Once / @Param+@Event / @Provider / @Consumer / @ObservedV2 / @Trace / @Monitor / @Computed`。

---

## 1. @ohos.* → @kit.* 导入迁移

### 迁移步骤

1. 找到所有 `import ... from '@ohos.*'` 语句
2. 查找对应的 `@kit.*` 模块（参见 SKILL.md 映射表）
3. 替换导入路径
4. 注意：部分 `@ohos.*` 模块在 `@kit.*` 中合并为一个 Kit

### 代码对照

```typescript
// ============ 迁移前 ============

import router from '@ohos.router'
import { http } from '@ohos.net.http'
import { connection } from '@ohos.net.connection'
import dataPreferences from '@ohos.data.preferences'
import { AbilityConstant, UIAbility, Want } from '@ohos.app.ability.UIAbility'
import { common } from '@ohos.app.ability.common'
import { hilog } from '@ohos.hilog'
import { window } from '@ohos.window'
import { image } from '@ohos.multimedia.image'
import { fileIo } from '@ohos.file.fs'

// ============ 迁移后 ============

// router 废弃，不再导入，改用 Navigation
import { http, connection } from '@kit.NetworkKit'          // 网络模块合并
import { preferences } from '@kit.ArkData'                  // 数据存储
import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit'  // Ability 合并
import { common } from '@kit.AbilityKit'
import { hilog } from '@kit.PerformanceAnalysisKit'
import { window } from '@kit.ArkUI'
import { image } from '@kit.ImageKit'
import { fileIo } from '@kit.CoreFileKit'
```

### 批量迁移技巧

在 DevEco Studio 中，使用全局搜索替换：

| 搜索 | 替换 |
|---|---|
| `from '@ohos.net.http'` | `from '@kit.NetworkKit'` |
| `from '@ohos.net.connection'` | `from '@kit.NetworkKit'` |
| `from '@ohos.data.preferences'` | `from '@kit.ArkData'` |
| `from '@ohos.hilog'` | `from '@kit.PerformanceAnalysisKit'` |
| `from '@ohos.window'` | `from '@kit.ArkUI'` |

**注意**：`@ohos.router` 不是简单替换，需要重构导航逻辑，见下文。

---

## 2. router → Navigation 迁移

### 迁移步骤

1. **删除** `import router from '@ohos.router'`
2. **在入口页面**创建 `NavPathStack` 并用 `@Provide` 注入
3. **创建路由映射** `@Builder pageMap()`
4. **将入口页面包裹在** `Navigation` 容器中
5. **将子页面改造为** `NavDestination` 组件
6. **替换跳转代码**
7. **替换参数接收代码**
8. **更新** `main_pages.json`（只保留入口页面）

### 完整迁移对照

#### 迁移前（router 方案）

```typescript
// === pages/Index.ets（入口页面）===
import router from '@ohos.router'

@Entry
@Component
struct IndexPage {
  build() {
    Column() {
      Button('进入详情')
        .onClick(() => {
          router.pushUrl({
            url: 'pages/DetailPage',
            params: { id: '123', title: '文章标题' }
          })
        })
    }
  }
}

// === pages/DetailPage.ets（详情页）===
import router from '@ohos.router'

@Entry
@Component
struct DetailPage {
  @State id: string = ''
  @State title: string = ''

  aboutToAppear(): void {
    let params = router.getParams() as Record<string, string>
    this.id = params?.id ?? ''
    this.title = params?.title ?? ''
  }

  build() {
    Column() {
      Text(this.title)
      Button('返回')
        .onClick(() => {
          router.back()
        })
    }
  }
}

// === main_pages.json ===
{ "src": ["pages/Index", "pages/DetailPage"] }
```

#### 迁移后（Navigation 方案）

```typescript
// === pages/Index.ets（入口页面）===
@Entry
@Component
struct IndexPage {
  @Provide('navPathStack') navPathStack: NavPathStack = new NavPathStack()

  @Builder
  pageMap(name: string, param?: object) {
    if (name === 'DetailPage') {
      DetailPage()
    }
  }

  build() {
    Navigation(this.navPathStack) {
      Column() {
        Button('进入详情')
          .onClick(() => {
            this.navPathStack.pushPathByName('DetailPage', {
              id: '123',
              title: '文章标题'
            } as Record<string, string>)
          })
      }
    }
    .navDestination(this.pageMap)
    .title('首页')
    .mode(NavigationMode.Stack)
  }
}

// === pages/DetailPage.ets（详情页，不再是 @Entry）===
@Component
struct DetailPage {
  @Consume('navPathStack') navPathStack: NavPathStack
  @State id: string = ''
  @State title: string = ''

  build() {
    NavDestination() {
      Column() {
        Text(this.title)
        Button('返回')
          .onClick(() => {
            this.navPathStack.pop()
          })
      }
    }
    .title('详情')
    .onReady((context: NavDestinationContext) => {
      let param = context.pathInfo.param as Record<string, string>
      this.id = param?.id ?? ''
      this.title = param?.title ?? ''
    })
  }
}

// === main_pages.json ===
{ "src": ["pages/Index"] }  // 只注册入口页面
```

### 关键差异总结

| 方面 | 迁移前 | 迁移后 |
|---|---|---|
| 子页面 | `@Entry @Component` | `@Component`（无 @Entry） |
| 跳转 | `router.pushUrl({ url, params })` | `navPathStack.pushPathByName(name, params)` |
| 返回 | `router.back()` | `navPathStack.pop()` |
| 接收参数 | `router.getParams()` in `aboutToAppear` | `context.pathInfo.param` in `onReady` |
| 页面注册 | 所有页面都在 main_pages.json | 只注册入口页面 |
| 路由映射 | URL 路径 | `@Builder pageMap` 映射 |

---

## 3. @Prop 初始化迁移（V1 legacy；V2 等价见 v2-migration-patterns.md §3.2）

### 迁移步骤

1. 搜索所有 `@Prop` 声明
2. 检查是否有默认值
3. 没有的话，根据类型添加合适的默认值

### 代码对照

```typescript
// 迁移前
@Prop title: string
@Prop count: number
@Prop isActive: boolean
@Prop items: string[]
@Prop user: UserModel

// 迁移后
@Prop title: string = ''
@Prop count: number = 0
@Prop isActive: boolean = false
@Prop items: string[] = []
@Prop user: UserModel = new UserModel()
```

---

## 4. @Link 传参迁移（V1 legacy — 仅去除 `$` 前缀；V2 已无 `@Link`，等价见 v2-migration-patterns.md §3.1）

### 代码对照

```typescript
// 迁移前（$ 前缀语法）
@Entry
@Component
struct Parent {
  @State isEnabled: boolean = false

  build() {
    ChildComp({ isEnabled: $isEnabled })  // $ 前缀
  }
}

// 迁移后（直接传值）
@Entry
@Component
struct Parent {
  @State isEnabled: boolean = false

  build() {
    ChildComp({ isEnabled: this.isEnabled })  // 直接传值
  }
}
```

**注意**：`$` 前缀语法在 API 12 仍然可以工作，但不推荐。新项目应使用直接传值方式。

---

## 5. Preferences 导入迁移

### 代码对照

```typescript
// 迁移前
import dataPreferences from '@ohos.data.preferences'

async function getPrefs(context: Context): Promise<dataPreferences.Preferences> {
  return await dataPreferences.getPreferences(context, 'myStore')
}

// 迁移后
import { preferences } from '@kit.ArkData'

async function getPrefs(context: Context): Promise<preferences.Preferences> {
  return await preferences.getPreferences(context, 'myStore')
}
```

API 使用方式基本不变，只是导入路径和模块名变化。

---

## 6. 迁移检查清单（API 11- → API 12 V1 基线）

完成迁移后，逐项检查：

- [ ] 所有 `@ohos.*` 导入已替换为 `@kit.*`
- [ ] 不再引用 `@ohos.router`
- [ ] 使用 `Navigation` + `NavPathStack` 进行页面导航
- [ ] 子页面使用 `NavDestination` 而非 `@Entry`
- [ ] `main_pages.json` 中移除了不再是 `@Entry` 的页面
- [ ] 所有 `@Prop` 变量有默认值（V1 API 12+ 强制，与 V2 `@Param` 强制一致）
- [ ] `@Link` 传参不使用 `$` 前缀（V2 已无 `@Link`，本条仅适用于仍 V1 的项目）
- [ ] 编译通过，无 deprecation 警告
- [ ] 页面跳转和参数传递正常工作

---

## 7. 升 V2 后的额外检查（V1 → V2）

完成 V1 升 API 12 后，本项目要求继续升级到 V2，参阅 [`v2-migration-patterns.md`](./v2-migration-patterns.md) §4 完整 Checklist：

- [ ] 所有 `@Component` → `@ComponentV2`
- [ ] 所有 `@State` → `@Local`
- [ ] 所有 `@Prop` → `@Param`（默认加 `@Once`）/ `@Prop`（可改场景去 `@Once`）
- [ ] 所有 `@Link` → `@Param + @Event` 回调（结构性改写）
- [ ] 所有 `@Provide / @Consume` → `@Provider() / @Consumer()`（带括号 + `@Consumer` 给默认值）
- [ ] 所有 `@Observed` → `@ObservedV2`，属性加 `@Trace`
- [ ] 所有 `@ObjectLink` 改为 `@Param`，并删除 `@ObjectLink`
- [ ] 所有 `@StorageLink / @StorageProp` → `AppStorageV2.connect`（先抽 `@ObservedV2` 类）
- [ ] 所有 `PersistentStorage.persistProp` → `PersistenceV2.globalConnect`
- [ ] 所有 `@Watch` → `@Monitor`（方法装饰器 + `IMonitor` 签名）
