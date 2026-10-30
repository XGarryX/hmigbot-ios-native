# v1 → v2 状态管理全栈迁移 playbook

> 实战经验沉淀：当 R6.1a（业务页面 v2）是 P0、且工程同时有 `@StorageProp/@StorageLink` 跨页共享状态时，按本 playbook 推。
> 来源：AIPPT_ArkTS_rebuild 项目（22 page / 47 @StorageProp / 178 @State 全栈迁移，4 batch / 4 commit 完成）。

## 0. 核心洞察

**`AppStorage` 与 `AppStorageV2` 是分离存储，互不互通**。
- `AppStorage.setOrCreate(key, v)` 写入的值，`AppStorageV2.connect(Type)` 读不到
- 反向同理

**推论**：
- ❌ 不能"先迁一部分页面试试" — 跨页状态会断（登录态丢失、VIP 状态不同步）
- ❌ 不能"全 22 页一把切" — 单 component 不准混 v1/v2 装饰器，编译爆炸面太大

**解法**：**dual-write 桥接 + 渐进迁页**（5 步）。

---

## 1. 五步 playbook

### Step 1 · 建 v2 模型（business_common）

收编所有跨页 @StorageProp key 成 @ObservedV2 类。每业务域一个类，每 key 一个 @Trace 字段。

```ts
// features/business_common/src/main/ets/models/GlobalStateModels.ets
import { AppStorageV2 } from '@kit.ArkUI';

@ObservedV2
export class SafeAreaModel {
  @Trace statusBarHeight: number = 36;
  @Trace bottomAvoidHeight: number = 28;
}

@ObservedV2
export class LoginStateModel {
  @Trace loginStateVersion: number = 0;
}

@ObservedV2
export class VipStateModel {
  @Trace isVipState: boolean = false;
}

export class GlobalState {
  static readonly safeArea: SafeAreaModel =
    AppStorageV2.connect(SafeAreaModel, () => new SafeAreaModel())!;
  static readonly login: LoginStateModel =
    AppStorageV2.connect(LoginStateModel, () => new LoginStateModel())!;
  static readonly vip: VipStateModel =
    AppStorageV2.connect(VipStateModel, () => new VipStateModel())!;
}
```

把模型加到 `business_common/Index.ets` 导出。Consumer 用 `import { GlobalState } from 'business_common'`。

> 模板：`assets/global-state-models.template.ets`

### Step 2 · setter dual-write（保 v1 兼容）

每个 `AppStorage.setOrCreate(key, v)` 旁追加一行 v2 写。**保留**旧的 AppStorage 写。

```diff
  AppStorage.setOrCreate<boolean>('isVipState', UserData.isVip());
+ GlobalState.vip.isVipState = UserData.isVip(); // dual-write to AppStorageV2
```

这样 v1 @StorageProp 读还能工作，v2 AppStorageV2.connect 读也能工作。**两边并存**。

> ⚠️ 在 business_common 内部的文件（如 UserData.ets）写 setter，import 要走 `from './GlobalStateModels'` —— **不能** `from 'business_common'`（自循环：ohpm install 报 `indirect dependency cannot be same as module name`）。

### Step 3 · 单 page 试点

挑最简单的 page（只 @State + @StorageProp，无 @Provide / @Watch / @ObjectLink）做转换试点：

```diff
- @Component
- export struct AboutUsPage {
-   @StorageProp('statusBarHeight') statusBarHeight: number = 36
-   @StorageProp('bottomAvoidHeight') bottomAvoidHeight: number = 28
-   @State versionName: string = 'V1.0.4'
+ @ComponentV2
+ export struct AboutUsPage {
+   safeArea: SafeAreaModel = AppStorageV2.connect(SafeAreaModel, () => new SafeAreaModel())!
+   @Local versionName: string = 'V1.0.4'
```

并把 `this.statusBarHeight` 全部改 `this.safeArea.statusBarHeight`。

**编译 + 装包 + 截图对比 baseline**。通过才能进 Step 4 批量。

### Step 4 · 批量转剩余 page（codemod）

跑下面 Python 脚本（或类似 codemod）批量。**关键约束**：

1. **`@Component → @ComponentV2`** — 同一文件**所有** @Component 一起转（避免单文件混 v1/v2，详见 §3.A）
2. **`@State → @Local`** — 全替
3. **`@Prop → @Param`** — 全替
4. **`@StorageProp(key)` 删行 + 注入 model 字段**
5. **`this.<localVar>` → `this.<modelField>.<key>`** 全文替
6. **import 加 `AppStorageV2`** from `@kit.ArkUI` + 模型名 from `business_common`
7. **callback 字段加 `@Event`** — v1 parent 传函数给 v2 child 时强制（详见 §3.B）

### Step 5 · 处理 @Watch / @Prop+@Watch 组合

```diff
- @StorageProp('loginStateVersion') @Watch('onLoginStateChanged') loginStateVersion: number = 0;
+ // (drop the line; loginState model field already injected from Step 4)

- @Prop @Watch('onPageShowVersionChanged') pageShowVersion: number = 0;
+ @Param pageShowVersion: number = 0;

  // handler 加 @Monitor 装饰器
+ @Monitor('loginState.loginStateVersion')
  onLoginStateChanged(): void {
    // 原 handler 体不变 —— @Monitor handler 不要求 IMonitor 参数
  }

+ @Monitor('pageShowVersion')
  onPageShowVersionChanged(): void { /* unchanged */ }
```

**@Monitor path 写法**：跨字段时用 `'modelField.modelKey'`（点路径）。

### Step 6（可选）· 清理旧 AppStorage 写

所有 page 都迁完 v2 后，可以删除 Step 2 留下的 `AppStorage.setOrCreate` 旧写。但**不强制** —— 双写不影响功能，删除是洁癖项。建议下次 refactor 时再做，避免本轮风险。

---

## 2. 编译期 sharp edges

### 2.1 多 struct 单文件混合 v1/v2

**症状**：codemod 用 `count=1` 只替第一个 `@Component → @ComponentV2`，但 `@State → @Local` 全替 → v1 struct 用了 v2 装饰器 → `error: @Local 只能在 @ComponentV2 中使用`。

**根因**：MainPage.ets 这种文件常含 5+ 个 inner @Component（HomeView/RecommendView/WorksView/MineView/MainPage 自身）。

**修复**：codemod 的 `@Component → @ComponentV2` 必须**全文件替换**，不能 `count=1`。同一文件所有 struct 一起进 v2。@CustomDialog 和 @Builder 不动。

### 2.2 `.catch()` chain on RouterUtils（高频踩坑）

`router.pushUrl({...})` 返回 `Promise<void>`，可链 `.catch((err)=>{...})`。
`RouterUtils.pushPathByName(...)` 返回 `void`。

`router-replace` codemod 直接转完后会留下：

```ts
RouterUtils.pushPathByName('XPage', params).catch((err: Error) => { Logger.error(err) })
```

→ 编译报 `Property 'catch' does not exist on type 'void'`。

**实测影响**：AIPPT 项目 64 个编译错里 39 处是这个。

**修复**：`router-replace` 之后**强制**跑 `remove-router-catch`，或合并成一步（已合并到 codemod 流程，详见 `assets/refactor-codemods.py`）。

### 2.3 inline `import('path').Type` 类型引用

`router-replace` 不识别这种语法：
```ts
payData: import('../services/VipService').PayOrderData
```

**修复**：手动改为标准命名 import + 普通类型引用。codemod 不处理。

### 2.4 ArkTS 严格模式拒绝 untyped object literal 当 router 参数

```ts
RouterUtils.pushPathByName('X', { a: 1, b: 'foo' })  // ❌
```

**修复**：用 typed interface：
```ts
interface __XParams { a: number; b: string }
const __p: __XParams = { a: 1, b: 'foo' };
RouterUtils.pushPathByName('X', __p)
```

codemod `add-page-params-cast` 处理这个，建议默认串到 `router-replace` 之后。

### 2.5 跨模块 self-reference

business_common 内部文件不能 `import { X } from 'business_common'` —— ohpm install 报 `indirect dependency cannot be same as module name`。

**修复**：同模块内用相对路径 `from './X'`。

### 2.6 v1→v2 边界的 callback 字段必须 `@Event`

```ts
// v1 parent
ChildV2({ onClick: () => { ... } })

// v2 child
@ComponentV2
struct ChildV2 {
  @Param x: T = ...
  onClick: () => void = () => {}  // ❌ 报 10905324 regular property cannot be initialized here
}
```

**修复**：函数字段加 `@Event`：
```ts
  @Event onClick: () => void = () => {}
```

### 2.7 @Monitor handler 不需要 IMonitor 参数

实测：现有 `(): void` 签名的 v1 @Watch handler 加 `@Monitor` 装饰器后**直接编译过**。**不要**强加 `(monitor: IMonitor)` 参数（会造成不必要的 diff）。

---

## 3. Phase 4 ⑤ 冒烟深度要求

旧的"首屏非空 → PASS"判定**不足以**验证 v2 全栈迁移。**必跑深度路径**：

| 路径 | 验证什么 |
|---|---|
| App 启动 → 首页渲染 | 基础启动 |
| 至少 1 个 RouterUtils 跳转（pushPathByName/replacePathByName）| NavPathStack 工作 |
| 至少 1 个 v2 child 在 v1 host 渲染（或反向）| 混合组件树工作 |
| AppStorageV2 跨页读写：触发 setter（如登录态变化）+ 另一 page 读 | dual-write 链路 |
| @Monitor 触发：改 model 字段 + 验证 handler 调用 | reactive 工作 |

无登录账号时可用 `hdc shell uinput` 模拟点击 + `uitest dumpLayout` 文本断言。

---

## 4. 工程规模 / 节奏估算

| 工程规模 | 建议节奏 |
|---|---|
| ≤ 5 page | Step 1-5 一把过，单 commit |
| 6-15 page | Step 1-2 一 commit + Step 3 单页一 commit + Step 4 批量一 commit + Step 5 一 commit（共 4 commit）|
| 16+ page（含多 inner struct）| Step 1-2 一 commit + Step 3 单页 + Step 4 分"简单批"+"复杂批"+"MainPage 单独" + Step 5（共 5-6 commit）|

每 commit 必跑：编译 → 装包 → 多步骤冒烟。失败 → `git revert` 当前 commit，分析修补再重 push。

---

## 5. 实战参考：AIPPT_ArkTS_rebuild

```
batch 5  GlobalStateModels + 11 setter dual-write
batch 6  AboutUsPage 单页试点
batch 7  19 page 批量（除 MainPage）+ 50 错跨 3 轮编译修
batch 8  MainPage（5 inner struct + @Watch → @Monitor）+ 2 轮编译修
```

每 batch 后冒烟 PASS 才进下一 batch。整体 4 batch 完成 22 page v2 全栈迁移。

---

## 6. 相关资产 / 文档

- 模板：`assets/global-state-models.template.ets`
- codemod：`assets/refactor-codemods.py`（vm-extends / strip-entry / router-replace / remove-router-catch / add-page-params-cast / imports-fix）
- 状态规则：`references/04-state-routing.md`
- audit pattern：`references/audit-patterns.md`
