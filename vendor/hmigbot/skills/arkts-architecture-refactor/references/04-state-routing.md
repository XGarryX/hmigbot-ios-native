# 状态管理 + 路由（R6.1 / R6.2）

> 章节编号说明：本节按 customer-checklist.md / rule-checklist.md 的统一编号——R6.1（状态管理，含 a/b/b'/c）+ R6.2（路由）。

## R6.1a V2 状态管理（**MUST**——场景分流）

**禁用**：`@State / @Prop / @Link / @Provide / @Consume / @Observed / @ObjectLink / @StorageLink / @StorageProp / @Builder（v1 语义） / @Component`

**改用**：`@ComponentV2 / @Local / @Param / @Once / @Event / @ObservedV2 / @Trace / @Computed / @Monitor / AppStorageV2 / PersistenceV2`

### 反例 → 正例

```ts
// 反例 (v1)
@Component
struct HomePage {
  @State count: number = 0
  @Provide('user') user: User = new User()
  build() { Text(`${this.count}`) }
}

// 正例 (v2)
@ComponentV2
struct HomePage {
  @Local count: number = 0
  @Local user: User = new User()
  build() { Text(`${this.count}`) }
}
```

> **不能 v1/v2 混用**：同一文件出现 `@State` + `@Local` 会编译报错；同组件树里的父子也不要一边 v1 一边 v2。

## R6.1b Repeat 替代 LazyForEach（**MUST**——客户已升级严格度）

> **客户校准**（2026-04）：R6.1b 从 SHOULD 升为 **MUST**。**列表必须用 Repeat**——审计命中 LazyForEach → P1 必改。仅在 Repeat 不支持的极个别场景（如某些 SDK 内置组件强制 LazyForEach）才豁免，需在报告里记录豁免理由。

```ts
// 反例
LazyForEach(this.dataSource, (item: Item) => {
  ListItem() { Text(item.name) }
}, (item: Item) => item.id)

// 正例（@Builder 必须接整个 RepeatItem，否则刷新失效）
Repeat<Item>(this.list)
  .each((ri: RepeatItem<Item>) => {
    ListItem() { this.itemBuilder(ri) }   // 传整个 ri，不要解构
  })
  .key((item: Item) => item.id)

@Builder
itemBuilder(ri: RepeatItem<Item>) {
  Text(ri.item.name)
}
```

> **坑**：如果只把 `ri.item` 传给 @Builder，state 改动不会触发刷新——这是规则文里特别强调的。

### R6.1b''' Repeat 不应配合 LazyDataSource / virtualScroll 不传参（**MUST**——客户 2026-05 校准）

> **客户反馈**：见到工程里大量出现 `Repeat<T>(this.dataSource.getDataList()).virtualScroll({ totalCount: ... })`——这是 LazyForEach 时代的写法残留。Repeat 自身已经做了懒加载窗口，**数据源直接传 `T[]` 即可，且 `.virtualScroll()` 后面不需要传参**（无 totalCount/reusable/onLazyLoading）。

**判定**：
- ❌ `Repeat<T>(this.lazyDataSource.getDataList())` — `getDataList()` 是 LazyDataSource 残留 API
- ❌ `Repeat<T>(this.lazyDataSource)` — Repeat 不接受 IDataSource
- ❌ `Repeat<T>(this.list).each(...).virtualScroll({ totalCount: this.list.length })` — 多余参数
- ✅ `Repeat<T>(this.list).each(...).virtualScroll()` — list 是普通 `T[]`，virtualScroll 空参

```ts
// 反例：LazyForEach 时代写法 — Repeat + LazyDataSource + virtualScroll 传参
Repeat<Item>(this.dataSource.getDataList())
  .each((ri: RepeatItem<Item>) => { ... })
  .virtualScroll({ totalCount: this.dataSource.totalCount() })

// 正例：Repeat 标准写法
@Trace list: Item[] = [];   // 直接 Array，不再 LazyDataSource

Repeat<Item>(this.list)
  .each((ri: RepeatItem<Item>) => { ... })
  .key((item: Item) => item.id)
  .virtualScroll()           // 空参
```

**配套清理**：
- 删除 `private dataSource: LazyDataSource<T> = new LazyDataSource<T>()` 字段
- 删除 `dataSource.setData(arr)` / `dataSource.reloadData()` / `dataSource.getDataList()` 等调用，改为直接赋值 `this.list = arr`
- 如果该文件除了 Repeat 还有 ForEach 用了同一 LazyDataSource，**那两个 ForEach 也要一起改**——LazyDataSource 在 Repeat 时代是无意义包装

audit 命中即 P1。grep 触发器：
```bash
grep -rnE 'Repeat<[^>]+>\([^)]*\.getDataList\(\)' --include='*.ets' <root>     # ❌ Repeat 接 LazyDataSource
grep -rnE 'Repeat<[^>]+>\([^)]*\)\s*$' --include='*.ets' <root>                 # 起手式
grep -rnE '\.virtualScroll\(\s*\{' --include='*.ets' <root>                     # virtualScroll 传参
grep -rn 'LazyDataSource' --include='*.ets' <root>                              # LazyDataSource 残留
```

## R6.1c ViewModel 链顶层继承 BaseViewModel（SHOULD）

规范原文："**对于复杂页面**...请将 ViewModel **继承自** BaseViewModel"。

**重要**：只约束**链顶层**——`class ChildVM extends ParentVM` 中如果 `ParentVM` 已继承 BaseViewModel，则 ChildVM 视为合规。中间继承层不需重复继承。

```ts
// ✅ 合规链：A -> B -> BaseViewModel
class B extends BaseViewModel {}
class A extends B {}        // ChildVM，无需自己直接继承 BaseViewModel

// ❌ 顶层未继承
class StandaloneVM {        // 链顶层，未继承任何东西，违反 R6.3
  // ...
}
```

audit 时只标"无 extends 子句的 *ViewModel 类"为待改项，**不要**把链中间层（extends ParentVM）也标违规。

### R6.1c 范例（写新 VM 时的标准形态）

```ts
import { BaseViewModel } from 'lib_common';

@ObservedV2
export class HomeViewModel extends BaseViewModel {
  @Trace list: Item[] = [];

  // BaseViewModel 已暴露 breakpoint / windowTopPadding / windowBottomPadding
  loadData() {
    this.list = [/* ... */];
  }
}
```

并且**复杂页面的状态全部放进 ViewModel**，组件只负责描述布局：

```ts
@ComponentV2
struct HomePage {
  @Local vm: HomeViewModel = new HomeViewModel();
  build() {
    Column() {
      Text(`列表共 ${this.vm.list.length} 项`)
      // ...
    }
    .padding({ left: this.vm.breakpoint.pagePadding })
  }
  aboutToAppear() { this.vm.loadData(); }
}
```

### R6.1c-2 ViewModel 默认**不写单例**（**MUST**——客户 2026-05 校准）

> **客户反馈**：见到工程里 `HomeViewModel / StarBurstViewModel / SettingsViewModel / NetworkViewModel ...` 这类 page-scope ViewModel 普遍写了 `private static instance` + `getInstance()` + `clearInstance()` 三件套。这是 **Java/Kotlin 单例反射**，不符合 ArkTS V2 状态管理模型，且会导致：
>   - 同一页面多次进入复用旧状态（残留搜索词、滚动位置、过期数据）
>   - @Trace 字段跨页面相互污染
>   - clearInstance 时机模糊，往往忘记调用 → 内存泄漏

**判定原则**：

| ViewModel 类型 | 是否允许单例 | 例 |
|---|---|---|
| **Page-scope**（绑定单页生命周期） | ❌ MUST 删 | `HomePageVM` / `LoginPageVM` / `SettingsPageVM` |
| **Tab/Fragment-scope**（绑定 Tab 内某 Fragment） | ❌ MUST 删 | `MineFragmentVM` / `HomeFragmentVM` |
| **跨页全局共享** | ✅ 允许 | `IonBusiness` / `MembershipRefresher` / `UseCountManager` (业务无 page 绑定的 manager) |
| **AppStorageV2 connect 模型**（通过 `AppStorageV2.connect(ViewModel, () => new ViewModel())` 共享） | ✅ 推荐 | 替代 getInstance 的鸿蒙原生方式 |

**ViewModel 命名 + 行为约束**：
- `*PageViewModel` / `*FragmentViewModel` / `*PageVM` / `*FragmentVM` —— **禁止**单例
- `*Manager` / `*Service` / `*Refresher` / `*Repository` —— 单例可接受（属于 Service 层 / 全局态）

**page 持有 vm 的标准写法**：

```ts
// ✅ 正例 — page 内每次 new
@ComponentV2
struct HomePage {
  @Local vm: HomePageViewModel = new HomePageViewModel();
  // 页面销毁时 vm 自动随之释放
}

// ❌ 反例 — 单例三件套
@ObservedV2
export class HomePageViewModel extends BaseViewModel {
  private static instance: HomePageViewModel | null = null;
  static getInstance(): HomePageViewModel {
    if (!HomePageViewModel.instance) {
      HomePageViewModel.instance = new HomePageViewModel();
    }
    return HomePageViewModel.instance;
  }
  static clearInstance(): void { HomePageViewModel.instance = null; }
  ...
}
```

**整改方法**：
1. 删除 `private static instance` + `getInstance()` + `clearInstance()` 三件套
2. 调用方（page）从 `XxxViewModel.getInstance()` → `new XxxViewModel()`（用 @Local 持有）
3. 如果该 VM 确实需要跨页共享，**改用 `AppStorageV2.connect(VM, () => new VM())`** —— 鸿蒙原生跨页面共享方式

audit 触发器：
```bash
# 命中所有自定义单例三件套 ViewModel
grep -rnE 'private\s+static\s+instance.*ViewModel' --include='*.ets' <root>
grep -rnE 'static\s+getInstance\(\)\s*:\s*\w+ViewModel' --include='*.ets' <root>
# 排除合法单例（Manager/Service/Refresher/Repository）
```

## R6.2 路由：Navigation + RouterUtils（私仓）

工程整体路由用 `Navigation` 容器，所有 push/pop 走 `lib_common` 的 `RouterUtils`：

```ts
import { RouterUtils } from 'lib_common';

// push
RouterUtils.push('PageDetail', { id: 123 });

// 带返回值
const result = await RouterUtils.pushForResult('PageEditor', { draft });

// 返回
RouterUtils.back();
```

**禁止**：`@kit.ArkUI` 的旧 `router.pushUrl` / `router.replaceUrl` / `router.back`。

入口在 `products/phone/.../EntryAbility.ets` 启动时初始化 NavPathStack，并把页面 @Builder 注册到一个集中表（详细做法见 `arkts-navigation-builder` skill 的产物）。

---

## R6.2-CRITICAL：壳工程 PageMap @Builder 必须包 NavDestination ⚠️

> **本节是致命陷阱专区**——**编译期不会报错、运行时所有页面变白屏**。任何忘记此条的重构都会导致用户首次启动 App 看到全黑/全白页面，且无任何错误日志。

### 致命反模式 ❌

```ts
// products/phone/src/main/ets/pages/Index.ets
@Entry @ComponentV2
struct Index {
  pageStack: NavPathStack = RouterUtils.createStack(StackEnum.Main, true);
  aboutToAppear(): void { this.pageStack.pushPathByName('SplashPage', null); }
  build() {
    Navigation(this.pageStack).navDestination(this.PageMap)
  }

  @Builder
  PageMap(name: string) {
    if (name === 'SplashPage') {
      SplashPage()         // ❌ 没有 NavDestination 包裹
    } else if (name === 'LoginPage') {
      LoginPage()          // ❌ 同上
    }
  }
}
```

**症状**：编译完美通过，安装运行后**所有 NavPathStack 推入的页面都不显示**（首屏空白，点击 Tab 跳转后还是空白）。框架不会报错，因为 `.navDestination(builder)` 只是默默忽略了非 NavDestination 子组件。

### 正确写法 ✅

```ts
@Builder
PageMap(name: string) {
  NavDestination() {                    // ← 必须！每条路由必须用 NavDestination 包一层
    if (name === 'SplashPage') {
      SplashPage()
    } else if (name === 'LoginPage') {
      LoginPage()
    } else if (name === 'MainPage') {
      MainPage()
    }
    // ... 其他 page
  }
  .hideTitleBar(true)                   // 不要默认 toolbar
  .hideToolBar(true)
  .mode(NavDestinationMode.STANDARD)
}
```

### 三条等价的实现选择

任选一种，但必须**有且仅有一种**生效：

| 实现 | 包装位置 | 适用 |
|---|---|---|
| **A. PageMap 内统一包**（推荐） | `@Builder PageMap(name) { NavDestination() { ...if-else... } }` | 多 page 共享 chrome 配置 |
| **B. 每个 page 自己包** | page 的 `build()` 顶层是 `NavDestination() { ...原 Column/Stack... }` | 各 page 需要自定义 chrome |
| **C. 注册式 RouterMap** | 使用 `lib_common` 的 `RouterMap` 注解，由 lib 内部包装 | 与 lib_common 1.1.5+ 配套 |

**禁止**：`PageMap` 直接调 page struct 而页面 `build()` 顶层又是 Column/Stack——这就是反模式。

**双重反模式**（2026-04 RR2）：Index.ets 已经写成 `Navigation(RouterUtils.getStack()) { }`（空 body，不挂 `.navDestination`），工程内**还**存在一份手写 `pages/PageMap.ets`。这种情况下 PageMap 是**死代码**——`RouterUtils` 的 stack 已经通过各 page 的 `@RouterMap` 注解（lib_common 自带）完成注册。修复方式是**删除整个 PageMap.ets**，由各 page 用 `@RouterMap({ name: ... })` 自注册（即上表方案 C），而不是补上 `.navDestination(this.PageMap)`。

### 静态校验（Phase 3 Step 4 完成后必跑）

```bash
# 拦截最常见的 NavDestination 缺失错误
INDEX=products/phone/src/main/ets/pages/Index.ets
test -f "$INDEX" || { echo "✗ 缺 phone Index.ets"; exit 1; }
grep -A 60 '@Builder.*PageMap\|@Builder\s*$' "$INDEX" | grep -q 'NavDestination(' \
  || { echo "❌ FATAL: PageMap 未用 NavDestination 包裹 → 运行时所有页面会空白"; exit 1; }

# 每个 page 的 build() 没用 NavDestination 也是允许的（走方案 A）
# 但若选方案 B，必须在 page 的 build() 顶层有 NavDestination
```

把这个 grep 加到 Phase 4 ③ 静态合规扫的必跑清单。

### 关联 BEHAVIOR_RISK

NavDestination 包装影响**生命周期回调时机**：
- 原 `@Entry @ComponentV2` 顶层 page：`aboutToAppear` 在 page 加载时调用
- 现在作为 NavDestination 子页：`aboutToAppear` 仍在 push 时调用，但 `onPageShow / onPageHide` 改由 NavDestination 的 `onShown / onHidden` 替代
- 旧代码若用 `onPageShow` 不会编译报错但**永远不触发** → 必须迁到 `NavDestination().onShown(...)` 或在 page 内手动监听

把"page 内 onPageShow / onPageHide 调用"列为 Phase 3 BEHAVIOR_RISK 强制项。


---

## v1 → v2 全量迁移：codemod 安全规则（实战补充）

> 这一节的规则来自 AIPPT_ArkTS_rebuild 项目（22 page / 47 @StorageProp / 178 @State 全栈迁移）。完整 5 步 playbook 见 [`v2-migration-playbook.md`](./v2-migration-playbook.md)。

### C1. 单文件多 @Component 必须**同步**转 v2

**坑**：codemod 用 `count=1` 替了第一个 `@Component → @ComponentV2`，但 `@State → @Local` 全替——文件其他 v1 struct 用了 v2 装饰器，编译报错 `@Local 只能在 @ComponentV2 中使用`。

**根因**：MainPage.ets 这种文件常含 5+ inner @Component（HomeView/RecommendView/WorksView/MineView/MainPage）+ 2 @CustomDialog。

**强制规则**：
- `@Component → @ComponentV2`：**全文件全替**，禁止 `count=1`
- `@CustomDialog`、`@Builder`：保持原样不动
- `@State / @Prop / @StorageProp`：跟随 `@Component → @ComponentV2`，全文件一致替换

### C2. v1 parent → v2 child 边界的 callback 字段必须 `@Event`

**症状**：v2 child 收 v1 parent 传的函数字段（`onClick: () => void = () => {}`）→ 编译报 `10905324 regular property cannot be initialized here`。

**实测影响**：AIPPT 项目 6 个错来自 SettingBarComponent / TemplateCardItem / OutlineContentItem / OutlineChapterItem。

**修复**：
```diff
  @ComponentV2
  struct ChildV2 {
    @Param x: T = ...
-   onClick: () => void = () => {}
+   @Event onClick: () => void = () => {}
  }
```

codemod 识别到 v2 struct 内有"函数类型字段且无装饰器"时自动加 `@Event`。

### C3. business_common 内部禁用 self-import

**坑**：business_common 内部文件（如 UserData.ets）写 `import { GlobalState } from 'business_common'` → ohpm install 报 `indirect dependency cannot be same as module name`。

**规则**：同模块内部 import 用相对路径 `from './X'`，禁止用模块名 `from 'business_common'`。

### C4. @Monitor handler 不需要 IMonitor 参数

**实测**：现有 `(): void` 签名的 v1 @Watch handler **直接加** `@Monitor` 装饰器即可编译过：

```ts
@Monitor('login.loginStateVersion')
onLoginStateChanged(): void { /* unchanged */ }
```

**规则**：codemod 不要给 handler 强加 `(monitor: IMonitor)` 参数。

### C5. @StorageProp + @Watch 组合的迁移

```diff
- @StorageProp('loginStateVersion') @Watch('onLoginStateChanged') loginStateVersion: number = 0;
+ // 删除整行；改用 GlobalState.login + @Monitor 装饰 handler

  // handler 加路径化 @Monitor
+ @Monitor('login.loginStateVersion')
  onLoginStateChanged(): void { /* unchanged */ }
```

### C6. RouterUtils 不返回 Promise

`router.pushUrl({...})` 返回 `Promise<void>`，可链 `.catch`；`RouterUtils.pushPathByName(...)` 返回 `void`。

**症状**：`router-replace` 后会留下 `RouterUtils.pushPathByName(...).catch(...)` → 编译报 `Property 'catch' does not exist on type 'void'`。

**规则**：`router-replace` 后**强制串联** `remove-router-catch` codemod。或合并成单步处理。

### C7. ArkTS 严格模式禁止 untyped object literal 当 router 参数

```ts
RouterUtils.pushPathByName('X', { a: 1, b: 'foo' })  // ❌ ArkTS 严格模式
```

**修复**：用 typed interface（`add-page-params-cast` codemod 处理）：
```ts
interface __XParams { a: number; b: string }
const __p: __XParams = { a: 1, b: 'foo' };
RouterUtils.pushPathByName('X', __p)
```
