# Router-only Load-Content 桥模板

> 适用场景：项目根页用 `windowStage.loadContent('pages/<RootPage>')` 加载，根页**没有 NavPathStack**，跨页跳转用 `router.pushUrl` / `router.replaceUrl`。典型形态：单 Activity Router-only 浏览器、阅读器等。
>
> 与 `direct-mount-bridge.md`（Navigation 直挂）的关系：互斥二选一。Step 2a Agent 在 §0 架构探测时根据 `windowStage.loadContent` 加载的根页是否有 `NavPathStack` 决定走哪条路径。

---

## 占位符

- `<ROOT_PAGE>` — `windowStage.loadContent('pages/<ROOT_PAGE>')` 实际加载的根页路径片段（如 `BrowserPage`），是 EntryAbility 默认加载的页面
- `<BUNDLE_NAME>` — 应用包名（从 `AppScope/app.json5` 读取）
- `<page_short>` — 见 `testable-id-catalog.md` 命名规范

### ⚠️ 路径约定（必读，不可项目内混用）

`__TARGET_PAGE__` AppStorage 字段的值有两种约定，**全项目必须统一选其一**：

| 约定 | 字段值示例 | onWindowStageCreate 用法 | onNewWant 用法 |
|------|-----------|-------------------------|----------------|
| **全路径**（推荐，与既有 EinkBro 实现对齐）| `'pages/SettingPage'` | `windowStage.loadContent(target)` 直接用 | `router.replaceUrl({ url: target })` 直接用 |
| 短名 | `'SettingPage'` | `windowStage.loadContent('pages/' + target)` 拼前缀 | `router.replaceUrl({ url: 'pages/' + target })` 拼前缀 |

混用会产生 `pages/pages/SettingPage` 双前缀错误。**测试侧 `delegator.startAbility(want)` 传 `__target_page__` 参数时，要严格按本项目约定写值**：
- 走"全路径"约定 → `parameters: { '__target_page__': 'pages/SettingPage' }`
- 走"短名"约定 → `parameters: { '__target_page__': 'SettingPage' }`

下面 §A / §B 模板**默认按全路径约定**给出。若你的项目用短名，请在 §A.2 把 `loadContent(target)` 改成 `loadContent('pages/' + target)`，并在 §B 测试 want 里去掉 `'pages/'` 前缀。

---

## A. EntryAbility 修改（Router-only 桥）

### A.1 onCreate：解析测试 want，写 AppStorage

```typescript
import AbilityConstant from '@ohos.app.ability.AbilityConstant';
import UIAbility from '@ohos.app.ability.UIAbility';
import Want from '@ohos.app.ability.Want';
import window from '@ohos.window';
import router from '@ohos.router';

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    // --- arkts-dt-verifier: parse test want ---
    const testMode: boolean = (want?.parameters?.['__test_mode__'] as boolean) ?? false;
    const targetPage: string = (want?.parameters?.['__target_page__'] as string) ?? '';
    AppStorage.setOrCreate<boolean>('__TEST_MODE__', testMode);
    AppStorage.setOrCreate<string>('__TARGET_PAGE__', targetPage);
    const targetParams = want?.parameters?.['__target_page_params__'] as Record<string, Object> | undefined;
    AppStorage.setOrCreate<Record<string, Object> | null>('__TARGET_PAGE_PARAMS__', targetParams ?? null);

    // ... 既有 onCreate 逻辑（如初始化 EventHub / 全局服务） ...
  }

  // ... onWindowStageCreate 见 A.2 ...
  // ... onNewWant 见 A.3 ...
}
```

### A.2 onWindowStageCreate：根据 `__TARGET_PAGE__` 切 loadContent 目标

```typescript
onWindowStageCreate(windowStage: window.WindowStage): void {
  // --- arkts-dt-verifier: route to test target page if specified ---
  const targetPage: string = AppStorage.get<string>('__TARGET_PAGE__') ?? '';
  const loadPath: string = (targetPage.length > 0)
    ? `pages/${targetPage}`           // 例如 'pages/SettingPage'
    : 'pages/<ROOT_PAGE>';            // 默认根页

  windowStage.loadContent(loadPath, (err) => {
    if (err.code) {
      console.error(`[direct-mount] loadContent failed for '${loadPath}': ${JSON.stringify(err)}`);
      // 回退到根页，不让进程死掉
      if (targetPage.length > 0) {
        windowStage.loadContent('pages/<ROOT_PAGE>');
      }
      return;
    }
    // 加载成功后清掉 __TARGET_PAGE__，避免热路径误用旧值
    AppStorage.setOrCreate<string>('__TARGET_PAGE__', '');
  });
}
```

### A.3 onNewWant：跨测试热路径，用 `router.replaceUrl` 切页

EntryAbility 是 singleton；首次启动后，第二条以及之后的 `delegator.startAbility(want)` 都只会触发 `onNewWant`，不再触发 `onCreate` / `onWindowStageCreate`。所以这里要主动用 router 做切换：

```typescript
onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void {
  // --- arkts-dt-verifier: hot path for cross-test page switch ---
  const targetPage: string = (want?.parameters?.['__target_page__'] as string) ?? '';
  if (targetPage.length === 0) {
    return;
  }

  // 写新参数（让 onReady 能读到）
  const targetParams = want?.parameters?.['__target_page_params__'] as Record<string, Object> | undefined;
  AppStorage.setOrCreate<Record<string, Object> | null>('__TARGET_PAGE_PARAMS__', targetParams ?? null);
  AppStorage.setOrCreate<string>('__TARGET_PAGE__', targetPage);

  // router.replaceUrl 是异步的，但不能 await（onNewWant 不允许 async 签名）
  // 直接 fire-and-forget；测试侧用 landmark 轮询兜底
  try {
    router.replaceUrl({
      url: `pages/${targetPage}`,
      params: (targetParams ?? {}) as Record<string, Object>
    }).catch((e: Error) => {
      console.error(`[direct-mount] router.replaceUrl failed for '${targetPage}': ${e.message}`);
    });
  } catch (e) {
    console.error(`[direct-mount] router.replaceUrl threw: ${(e as Error).message}`);
  }
}
```

---

## B. UI 测试骨架（Router-only 流程）

### B.1 共享 helpers（在每个 UI 测试文件顶部 import 后插入）

```typescript
const BUNDLE_NAME: string = '<BUNDLE_NAME>';
const ABILITY_NAME: string = 'EntryAbility';
const MODULE_NAME: string = 'entry';
const LANDMARK_POLL_MAX_MS: number = 8000;
const LANDMARK_POLL_STEP_MS: number = 500;

// Router-only 模式下，首次启动通过 want 参数指定目标页
// 跨测试切页通过 onNewWant 内的 router.replaceUrl
async function mountPageRouterOnly(
  driver: Driver,
  page: string,
  pageShort: string,
  params?: Record<string, Object>
): Promise<void> {
  const delegator = abilityDelegatorRegistry.getAbilityDelegator();

  const parameters: Record<string, Object> = {
    '__test_mode__': true as Object,
    '__target_page__': page as Object
  };
  if (params !== undefined) {
    parameters['__target_page_params__'] = params as Object;
  }
  const want: Want = {
    bundleName: BUNDLE_NAME,
    abilityName: ABILITY_NAME,
    moduleName: MODULE_NAME,
    parameters: parameters
  };

  await delegator.startAbility(want);
  // router.replaceUrl 是异步的，必须给足时间。1500ms 是经验下限。
  await driver.delayMs(1500);

  // 用 landmark 轮询替代固定 delay 兜底（建议优先 waitForComponent）
  let elapsed = 0;
  while (elapsed < LANDMARK_POLL_MAX_MS) {
    try {
      const comp = await driver.findComponent(ON.id(`${pageShort}_root`));
      if (comp !== null) return;
    } catch (_e) { /* not found yet */ }
    await driver.delayMs(LANDMARK_POLL_STEP_MS);
    elapsed += LANDMARK_POLL_STEP_MS;
  }
}
```

### B.2 测试文件骨架

```typescript
import { describe, it, expect, beforeAll, beforeEach } from '@ohos/hypium';
import { Driver, ON, Component } from '@ohos.UiTest';
import { abilityDelegatorRegistry } from '@kit.TestKit';
import { Want } from '@kit.AbilityKit';

// （此处插入 B.1 共享 helpers）

export default function <PageName>_UI() {
  describe('<PageName>_UI', () => {
    let driver: Driver;

    // beforeAll 仅做一次：startAbility 把目标页拉起来
    beforeAll(async () => {
      driver = await Driver.create();
      await mountPageRouterOnly(driver, '<PageName>', '<page_short>');
    });

    // beforeEach 每个 it 跑前确认 driver / landmark 仍在
    beforeEach(async () => {
      if (driver === undefined) driver = await Driver.create();
      // 如果上一条 it() 把页面跳走了，重新拉回当前测试页
      try {
        await driver.assertComponentExist(ON.id('<page_short>_root'));
      } catch (_e) {
        await mountPageRouterOnly(driver, '<PageName>', '<page_short>');
      }
    });

    it('P{编号}_UI_SMOKE_page_renders', 0, async () => {
      // 优先用 waitForComponent（API 11+）替代 assertComponentExist
      // 因 router.replaceUrl 是异步，可能 1.5s 后 landmark 仍未就绪
      try {
        // @ts-ignore — waitForComponent 可能在某些 SDK 上不存在
        await driver.waitForComponent(ON.id('<page_short>_root'), 5000);
      } catch (_e) {
        await driver.assertComponentExist(ON.id('<page_short>_root'));
      }
    });

    // ... 其它 COMP / NAV / INTERACT it() ...
  });
}
```

---

## C. 时序问题提示（重要）

### C.1 `router.replaceUrl` 是异步

`router.replaceUrl({...})` 返回 `Promise<void>`，但调用后页面真正切换到新 onReady 触发可能还要 100~800ms。在 `onNewWant` 里**不能 await**（onNewWant 是同步签名，不允许标 async），所以是 fire-and-forget。

后果：测试侧 `delegator.startAbility(want)` 一返回就立即 `findComponent` 会失败。所以 `delayMs` 必须给到至少 **1500ms**（实测下限），并且**优先用 `waitForComponent`**（API 11+ 提供，按 timeout 轮询，比固定 sleep 更稳）替代 `assertComponentExist`。

### C.2 跨测试热路径靠 onNewWant，不靠 onCreate

EntryAbility 是 singleton。第一次 startAbility 走 onCreate → onWindowStageCreate → 加载根页或目标页。**第二次** startAbility 只触发 `onNewWant` —— 这时候 `onWindowStageCreate` 不会再跑，靠 router.replaceUrl 切页。

如果 `onNewWant` 没注入切页逻辑，第二个测试文件会停在第一个文件的页面 → SMOKE landmark 失败 → 整批 ERROR。

### C.3 首次冷启动的 onCreate / onWindowStageCreate 顺序

冷启动时：

1. `onCreate(want)` 解析参数，写 AppStorage `__TARGET_PAGE__`
2. `onWindowStageCreate(windowStage)` 读 `__TARGET_PAGE__`，决定 `windowStage.loadContent` 目标

第二次（hot）：

1. `onNewWant(want)` 解析参数，写 AppStorage + 调 `router.replaceUrl`
2. 不再触发 `onWindowStageCreate`

测试侧 helper `mountPageRouterOnly` 不区分冷热路径（让 EntryAbility 自己处理）—— 同一个 helper 函数即可。

### C.4 onWindowStageCreate 加载失败的回退

`windowStage.loadContent('pages/Foo', cb)` 在路径不存在时会报错；err 回调里要降级到根页加载，不让进程死。这个分支主要给 typo / 路由未注册保底 —— 写完 manifest 之后用一个普通 SMOKE 测试就能验证。

### C.5 router.replaceUrl 在某些场景失败

```
- 目标页不在 main_pages 列表（main_pages.json 没注册）→ replaceUrl 抛 100002
- 当前栈已经在目标页 → 静默成功，但视觉上"没变化"，测试看着像挂了
- onNewWant 在 ability 销毁过程中触发 → router 实例可能为 undefined
```

第一种最常见：Router-only 项目 main_pages.json 必须显式注册所有可被 direct-mount 的 page。Step 4 编译 Agent 应该已校验了；UI 测试 Agent 不再校验，但第一次跑 SMOKE 一旦命中就立刻报。

---

## D. 自检 greps（Step 2a 写完必跑）

```bash
# D.1 EntryAbility 三处必须命中
grep -n '__TARGET_PAGE__' entry/src/main/ets/entryability/EntryAbility.ets   # ≥3 (onCreate, onWindowStageCreate, onNewWant)
grep -n 'onNewWant' entry/src/main/ets/entryability/EntryAbility.ets         # =1
grep -nE 'router\.(replaceUrl|pushUrl)' entry/src/main/ets/entryability/EntryAbility.ets  # ≥1 (onNewWant)
grep -nE 'windowStage\.loadContent\(.*targetPage' entry/src/main/ets/entryability/EntryAbility.ets  # =1

# D.2 不应有的内容（防 Step 2a 误把 Navigation 桥也注入）
grep -rn "@Monitor('directMount.targetPage')" entry/src/main/ets/pages/  # 期望 0 处（Router-only 不需要根页响应式监听）
```

任一失败 → `BLOCKERS: router-only bridge incomplete`，**终止**。

---

## E. 与 Navigation 流程的差异速查表

| 维度 | NAVIGATION_DIRECT_MOUNT | ROUTER_LOAD_CONTENT |
|------|-------------------------|---------------------|
| 切页机制 | NavPathStack.pushPath | router.replaceUrl / windowStage.loadContent |
| 桥位置 | EntryAbility + 根页 @Monitor（DirectMountModel） | 仅 EntryAbility |
| onNewWant | 写 DirectMountModel 触发根页 @Monitor | 写 AppStorage + 调 router.replaceUrl |
| 时序兜底 | 根页 mountTargetWithRetry 50ms × 20 | 测试侧 delayMs(1500) + waitForComponent |
| beforeAll vs beforeEach | beforeEach 懒挂载（每条 it 重挂） | beforeAll 挂一次 + beforeEach landmark 检查 |
| Spec 不可达 | 嵌套 Navigation / Tab 子页 / Dialog-only | main_pages 未注册 / Splash 抢占 / Tab 子页 |

---

## F. 何时切回 Navigation 流程

如果项目后续重构成 Navigation 架构（根页加 NavPathStack），Step 2a 0 节探测会自动走 `NAVIGATION_DIRECT_MOUNT`，不用改本文件。但 Router-only 桥已注入的代码必须手工卸掉，否则 EntryAbility 同时跑两套桥逻辑会冲突。
