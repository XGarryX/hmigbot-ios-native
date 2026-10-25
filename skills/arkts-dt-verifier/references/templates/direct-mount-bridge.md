# Direct-Mount Bridge 模板

> **何时读这份**：根页 `grep ': NavPathStack'` 命中 1 处（Navigation 架构）。
>
> **何时不读这份，改读 `router-load-content.md`**：根页无 `NavPathStack`（Router-only 架构，单 Activity + `router.pushUrl/replaceUrl`）。Router-only 项目不能 direct-mount push 到目标页 —— 没有 NavPathStack 可以 push。等价方案是 `router-load-content.md`：让 EntryAbility 的 `onWindowStageCreate` 根据 `__target_page__` 直接 `windowStage.loadContent` 落到目标页。
>
> Step 2a Agent 在 §0 节自动探测，这两个模板**互斥二选一**，不要同时注入。

UI 测试（Step 3）默认走 **direct-mount** 直接挂载目标页，绕开点击链和 stub-handler。

> **ArkTS V2**：a2h pipeline 锁 V2，被测根页是 `@ComponentV2`，**不能注入 V1 的 `@StorageLink` / `@Watch` 装饰器**（在 `@ComponentV2` 中编译报错）。本桥使用 V2 状态管理：`@ObservedV2` 共享模型 + `AppStorageV2.connect` + `@Monitor`。

**机制**：测试 `startAbility` 时传 `__target_page__` + `__target_page_params__` → EntryAbility 写入 `DirectMountModel`（`AppStorageV2` 共享实例）→ 根页（Navigation 宿主）通过 `@Monitor` 响应式监听并 `pushPath`。

**Step 2 必须注入三处**：①共享模型 `DirectMountModel.ets`、②EntryAbility、③根页，缺任一 Step 3 全部失败。

**占位符**：
- `<HOST_PAGE_NAME>` — 根页 NavDestination `name` 约定（通常就是根组件类名，如 `'MainPage'`）
- `<NAV_STACK_FIELD>` — 根页的 `NavPathStack` 字段名（step2 用 `grep ': NavPathStack'` 探测；常见 `navPathStack` / `pathStack` / `pageStack`）。**不要硬编码 `navPathStack`**。

---

## 0. 共享模型 — DirectMountModel.ets

新建 `entry/src/main/ets/common/DirectMountModel.ets`（`common/` 目录不存在则创建）。EntryAbility 与根页都 import 它，保证 connect 到同一实例：

```typescript
// --- arkts-dt-verifier: direct-mount shared model (ArkTS V2) ---
import { AppStorageV2 } from '@kit.ArkUI';

@ObservedV2
export class DirectMountModel {
  @Trace targetPage: string = '';
  @Trace targetParams: Record<string, Object> | null = null;
}

// 全局单例 —— EntryAbility 与根页 connect 同一实例，任意一方改 @Trace 字段都会通知另一方
export function getDirectMountModel(): DirectMountModel {
  return AppStorageV2.connect(DirectMountModel, '__DIRECT_MOUNT__', () => new DirectMountModel())!;
}
```

---

## A. EntryAbility — 读 want 写 DirectMountModel

EntryAbility 顶部追加 import（路径按实际目录层级调整）：

```typescript
import { getDirectMountModel } from '../common/DirectMountModel';
```

在 `onCreate(want, launchParam)` 中，紧接 `__test_mode__` 处理之后追加：

```typescript
// --- arkts-dt-verifier: direct-mount target page for UI test ---
const dmModel = getDirectMountModel();
const targetPage: string = (want?.parameters?.['__target_page__'] as string) ?? '';
if (targetPage.length > 0) {
  const targetParams = want?.parameters?.['__target_page_params__'] as Record<string, Object> | undefined;
  // 先写 params 再写 targetPage，保证根页 @Monitor 触发时 params 已就绪
  dmModel.targetParams = targetParams ?? null;
  dmModel.targetPage = targetPage;
} else {
  dmModel.targetPage = '';
  dmModel.targetParams = null;
}
```

**必须**同时添加 `onNewWant` —— 一轮测试会多次 `startAbility` 切页，第二次之后 `onCreate` 不再触发：

```typescript
onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void {
  const targetPage: string = (want?.parameters?.['__target_page__'] as string) ?? '';
  if (targetPage.length > 0) {
    const dmModel = getDirectMountModel();
    const targetParams = want?.parameters?.['__target_page_params__'] as Record<string, Object> | undefined;
    // 先写 params 再写 targetPage，保证根页 @Monitor 触发时 params 已就绪
    dmModel.targetParams = targetParams ?? null;
    dmModel.targetPage = targetPage;
  }
}
```

---

## B. 根页（Navigation 宿主）—— 响应式监听并 push

找到项目的 Navigation 根组件页（通常是 `MainPage.ets` / `Index.ets`，即持有 `NavPathStack` 的那个页面）。根页必为 `@ComponentV2`。

根页顶部追加 import：

```typescript
import { DirectMountModel, getDirectMountModel } from '../common/DirectMountModel';
```

加入字段 + `@Monitor` 方法（`@Monitor` 监听 `@Local` 持有对象的 `@Trace` 属性路径）：

```typescript
// --- arkts-dt-verifier: reactive direct-mount (ArkTS V2) ---
@Local directMount: DirectMountModel = getDirectMountModel()

@Monitor('directMount.targetPage')
onTargetPageChange(): void {
  const targetPage: string = this.directMount.targetPage
  if (targetPage.length === 0) {
    return
  }
  // Navigation-host 自身（本页就是 Navigation 宿主，非 NavDestination）
  // 不能 pushPath 自己，否则路由匹配不到会静默失败，害 beforeAll landmark 挂掉。
  // <HOST_PAGE_NAME> 替换为本根页的 NavDestination 'name' 约定（通常就是类名，如 'MainPage'）。
  if (targetPage === '<HOST_PAGE_NAME>') {
    this.directMount.targetPage = ''
    this.directMount.targetParams = null
    try { this.<NAV_STACK_FIELD>.clear() } catch (e) {}
    return
  }
  const targetParams: Record<string, Object> | null = this.directMount.targetParams
  // 清掉，做成一次性
  this.directMount.targetPage = ''
  this.directMount.targetParams = null
  this.mountTargetWithRetry(targetPage, targetParams)
}
```

再在根页 `aboutToAppear` 里加首次挂载分支（`@Monitor` 对初始值不触发）：

```typescript
aboutToAppear(): void {
  // ... 既有逻辑 ...
  const targetPage: string = this.directMount.targetPage
  if (targetPage === '<HOST_PAGE_NAME>') {
    // Navigation-host 自挂载：只消费 token，不 pushPath。
    this.directMount.targetPage = ''
    this.directMount.targetParams = null
  }
  if (targetPage.length > 0 && targetPage !== '<HOST_PAGE_NAME>') {
    const targetParams: Record<string, Object> | null = this.directMount.targetParams
    this.directMount.targetPage = ''
    this.directMount.targetParams = null
    this.mountTargetWithRetry(targetPage, targetParams)
  }
}
```

再加一个共享方法（放在根组件内）—— 用重试代替固定 50ms 等待，最多轮询 ~1s 等待 Navigation 挂载完成：

```typescript
// 把 <NAV_STACK_FIELD> 换成 1a 探测到的字段名
private mountTargetWithRetry(
  targetPage: string,
  targetParams: Record<string, Object> | null,
  attempt: number = 0
): void {
  const MAX_ATTEMPTS = 20   // 20 × 50ms = 1s 总上限
  const stack = this.<NAV_STACK_FIELD>
  if (stack === undefined || stack === null) {
    if (attempt < MAX_ATTEMPTS) {
      setTimeout(() => this.mountTargetWithRetry(targetPage, targetParams, attempt + 1), 50)
    } else {
      console.error(`[direct-mount] NavPathStack not ready after ${MAX_ATTEMPTS} retries`)
    }
    return
  }
  try { stack.clear() } catch (e) { /* older SDK */ }
  const sizeBefore: number = stack.size()
  if (targetParams !== null) {
    stack.pushPath({ name: targetPage, param: targetParams })
  } else {
    stack.pushPath({ name: targetPage })
  }
  // pushPath 对未注册 name 是静默失败 —— 靠 size 变化归因
  setTimeout(() => {
    if (stack.size() === sizeBefore) {
      console.error(`[direct-mount] pushPath('${targetPage}') failed silently — route not registered?`)
    }
  }, 100)
}
```

---

## Navigation-host 自挂载的特殊处理

当测试 target 就是 Navigation 宿主本身（如 `'MainPage'`），`pushPath('MainPage')` 会因路由没注册而静默失败。上面 `<HOST_PAGE_NAME>` 的两个分支（`@Monitor` 和 `aboutToAppear`）专门消费 token 但不 push，保证 landmark `main_root` 能正常通过。

---

## 自检 greps

- `grep -n 'getDirectMountModel\|@ObservedV2' entry/src/main/ets/common/DirectMountModel.ets` → 模型类已创建（≥ 2 处）
- `grep -n 'getDirectMountModel' entry/src/main/ets/entryability/EntryAbility.ets` → 至少 2 处（onCreate + onNewWant）
- `grep -rn "@Monitor('directMount.targetPage')" entry/src/main/ets/pages/` → 至少 1 处
- `grep -n 'onNewWant' entry/src/main/ets/entryability/EntryAbility.ets` → 1 处

任一缺失 → `BLOCKERS: direct-mount bridge incomplete`。

**前置**：根页必须有 `xxx: NavPathStack` 字段（字段名由 step2 1a 探测，存入 `<NAV_STACK_FIELD>`）。若没有（纯 Router 栈新项目）→ `BLOCKERS: root page has no NavPathStack — direct-mount needs Navigation`，不强行改造。

**多 Navigation 警告**：若 `grep ': NavPathStack'` 命中多个文件（根页下嵌套 Tab 各自一个 Navigation，或独立子 Navigation），本桥只作用于**根 Navigation**；嵌套 Navigation 的子页无法被 direct-mount 直达，必须在 Step 3 标 `unreachable`（见 step3-ui-test-agent.md 不可达页分类）。
