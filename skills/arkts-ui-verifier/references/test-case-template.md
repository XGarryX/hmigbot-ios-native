# UI 测试用例模版（UI Code）

第三步「测试用例生成」按设计文档落地。三类工件：

1. **`.id()` 注入**到 `entry/src/main/ets/{pages,components}/` 源码
2. **测试数据 + 桥**：`entry/src/main/ets/test/TestDataSetup.ets` + EntryAbility / 根页桥
3. **UI 测试代码**：`entry/src/ohosTest/ets/test/ui/P{编号}_{PageName}_UI.test.ets`

---

## 1. 文件骨架

```typescript
import { describe, it, expect, beforeEach } from '@ohos/hypium'
import { Driver, ON, Component } from '@ohos.UiTest'
import { abilityDelegatorRegistry } from '@kit.TestKit'
import { UIAbility, Want } from '@kit.AbilityKit'

// （顶部：共享 helpers，见 §6）

export default function <PageName>_UI() {
  describe('<PageName>_UI', () => {
    let driver: Driver

    beforeEach(async () => {
      if (driver === undefined) driver = await Driver.create()   // 懒 create
      await mountPage(driver, '<PageName>')
      await driver.assertComponentExist(ON.id('<page_short>_root'))
    })

    // it() 块...
  })
}
```

注册到 `entry/src/ohosTest/ets/test/List.test.ets`（由 register 模式重建）。

命名：`P{编号}_UI_{SMOKE|COMP|NAV|INTERACT}_xxx` 或 `F{编号}_UI_AC{序号}_xxx`。

---

## 2. UiTest API（能用什么、不能用什么）

| 用 | 不能用 / 注意 |
|---|---|
| `driver.findComponent(ON.id/text/type)` 返回单个 | `driver.scrollSearch` **不存在**（编译错），只有 `Component.scrollSearch` |
| `driver.findComponents(...)` 返回数组 | `driver.dumpLayout` **不存在**（不要写） |
| `driver.assertComponentExist(ON.x)` | `driver.pressBack` 部分 SDK 用 `triggerKey(KeyCode.KEY_BACK)` |
| `driver.delayMs(ms)` 等待 | `driver.swipe` 返回 `Promise<void>`，不要赋值 |
| `comp.click()` / `longClick()` / `inputText()` / `getText()` / `getId()` / `isChecked()` / `isEnabled()` / `scrollSearch()` | `component.dumpInfo` **不存在** |

---

## 3. Selector 优先级（强制）

1. **`ON.id('<page_short>_<purpose>_<kind>')`** ← manifest 默认
2. **`ON.text('<value>')`** ← LazyForEach 动态项 / bindMenu 菜单项；value **必须**来自 manifest「字符串映射」（`string.json`），禁止凭空翻译
3. **`ON.type('Toggle' / 'Swiper' / ...)`** ← spec `## 转换决策` 真实类型兜底
4. **关系选择器 `On.isBefore(on)` / `isAfter(on)` / `within(on)`**（since 9/10）—— 当目标控件本身没法直接拿到 id（@Builder 复用、ForEach 子项、NavigationMenuItem），但**附近有可定位锚点**（label 文本 / 父容器 id）时，用：`ON.type('Toggle').isAfter(ON.text('<label 字面量>'))` 把"按 label 找邻近 Toggle"一次解决，**无需改源码加 idSuffix**。对 SettingsPage 类页（5+ 个 @Builder 复用上百个调用点）尤其关键。
5. **禁用**：凭空翻译的中英文字面量；写完全文 grep `ON.text(...)` 字面量必须可追溯到 manifest

---

## 4. `.id()` 注入规则（命名 + 9 类组件）

**格式**：`<page_short>_<purpose>_<kind>`，全小写 snake_case，≤32 字符，页面内唯一。

- `page_short`：`page_NNNN_<Xxx>.md` → `<Xxx>` 去 `Activity/Fragment/Page` 后缀 + snake_case（`MainActivity` → `main`，`WidgetConfigureActivity` → `widget_config`）
- `purpose`：英文小词（`overflow` / `search` / `autoplay`）
- `kind`：见下表

**注入位置**：链式调用紧接第一行（`.width()` 之前）。

| 规则 | 组件形态 | kind | 命名例 |
|------|---------|------|--------|
| A1 | 顶部 ActionBar 图标按钮（Image + onClick）| `btn` | `main_overflow_btn`（资源名 `more` → `overflow`；`search` / `back` / `save` / `delete` / `edit` / `settings` / `add` / `filter` / `sort` / `refresh` / `play` / `pause` 各对应关键词） |
| A2 | 顶部标题文本 | `text` | `main_toolbar_title` |
| A3 | 顶层数据容器 | `grid` / `list` / `swiper` / `refresh` / `tabs` / `waterflow` | `main_directory_grid` |
| A4 | 设置行 + 其内 Toggle | `row` / `toggle` | `settings_autoplay_videos_row` / `settings_autoplay_videos_toggle`（`<setting>` 取 `$r('app.string.xxx')` 的 `xxx`） |
| A5 | FAB / 主操作按钮 | `fab` / `btn` | `edit_save_btn` |
| A6 | 输入框（TextInput / Search） | `input` | `search_query_input` |
| A7 | Dialog 内按钮 + Dialog 根 | `_confirm_btn` / `_cancel_btn` / `dialog` | `delete_confirm_dialog` |
| A8 | 页面根容器（Navigation / Column / Stack 最外层）| `root` | `main_root` |
| A9 | bindMenu / bindContextMenu / bindSheet 触发器 | 同 A1 | (弹出菜单项**不加** id，靠 `ON.text` 定位) |

**不加 id**：LazyForEach/ForEach 动态子项（重复 id 冲突，用 `findComponents(ON.type)[idx]`）；装饰容器；纯显示 Image/Text。

**灰色地带（标 `[NEEDS_REVIEW]`，不直接加）**：@Builder 内 ≥5 同形态 Image；嵌套容器哪层是真列表不清；同名重复（用 `_primary` / `_secondary` 区分）。

**跨页面复用子组件**（components/ 被 ≥2 个 page import）：优先改 `idPrefix: string` prop，父页传 `'settings'` / `'data_list'`，子组件内 `.id(this.idPrefix + '_xxx')`；不想改源码 → 用 `<component_short>` 自前缀。

**Settings 类页下限**：`<page>_<key>_toggle` 行数 ≥ 去重后 `@State boolean` 行数；`<page>_<key>_row` 行数 ≥ 去重后布尔行数 + TextValueRow/OneLinerRow 行数。

**Manifest**：写到 `entry/src/main/ets/test/testable-id-manifest.md`，含 `Page → page_short 映射` + 每页 ID 表（ID / 行号 / 组件 / 规则）+ 字符串映射（key / base / zh_CN / en_US / 设备实际） + NEEDS_REVIEW 表。

---

## 5. 测试数据 setup

**EntryAbility `onCreate`** 检测测试模式（已存在跳过）：

```typescript
const isTestMode: boolean = (want?.parameters?.['__test_mode__'] as boolean) ?? false
AppStorage.setOrCreate<boolean>('__TEST_MODE__', isTestMode)
if (isTestMode) {
  const { TestDataSetup } = await import('../test/TestDataSetup')
  await TestDataSetup.injectMockData()
}
```

**`entry/src/main/ets/test/TestDataSetup.ets`**：

```typescript
export class TestDataSetup {
  static async injectMockData(): Promise<void> {
    AppStorage.setOrCreate('__MOCK_DIRECTORIES__', [
      { path: 'DCIM/Camera', name: 'Camera' },
      { path: 'Pictures/Test', name: 'Test' },
    ])
    // 数量小（≤10）+ 覆盖边界（收藏/未收藏/已删除/超期）+ 文件名带 test_ 前缀
  }
}
```

**Service 旁路**（不改生产逻辑，只在测试模式下旁路）：

```typescript
if (AppStorage.get<boolean>('__TEST_MODE__')) {
  const mock = AppStorage.get<XxxModel[]>('__MOCK_XXX__')
  if (mock !== undefined) return mock
}
```

---

## 6. Mount Bridge（Navigation vs Router 二选一）

**架构探测**：根页 `entry/src/main/ets/pages/<RootPage>.ets` `grep ': NavPathStack'` 命中 → `NAVIGATION_DIRECT_MOUNT`；否则 → `ROUTER_LOAD_CONTENT`。两套桥**互斥**，不要同时注入。

### 6.1 共享：EntryAbility 读 want 写 AppStorage（两套桥都用）

```typescript
// onCreate(want, launchParam) 内追加；onNewWant(want, launchParam) 同样追加（singleton 切页）
const targetPage: string = (want?.parameters?.['__target_page__'] as string) ?? ''
if (targetPage.length > 0) {
  const targetParams = want?.parameters?.['__target_page_params__'] as Record<string, Object> | undefined
  AppStorage.setOrCreate<Record<string, Object> | null>('__TARGET_PAGE_PARAMS__', targetParams ?? null)
  AppStorage.setOrCreate<string>('__TARGET_PAGE__', targetPage)
}
```

### 6.2 NAVIGATION_DIRECT_MOUNT（根页有 `NavPathStack`）

**EntryAbility 写 AppStorage 即可；根页**（持有 `<NAV_STACK_FIELD>: NavPathStack` 的页面）加：

```typescript
@StorageLink('__TARGET_PAGE__') @Watch('onTargetPageChange') directMountTarget: string = ''

onTargetPageChange(): void {
  const target: string = this.directMountTarget
  if (target.length === 0) return
  // 宿主页自挂载特判：pushPath 自己会静默失败，只消费 token
  if (target === '<HOST_PAGE_NAME>') {
    AppStorage.setOrCreate<string>('__TARGET_PAGE__', '')
    try { this.<NAV_STACK_FIELD>.clear() } catch (e) {}
    return
  }
  const params = AppStorage.get<Record<string, Object> | null>('__TARGET_PAGE_PARAMS__') ?? null
  AppStorage.setOrCreate<string>('__TARGET_PAGE__', '')
  this.mountTargetWithRetry(target, params)
}

// aboutToAppear 末尾加首次挂载分支（@Watch 对初始值不触发）—— 同样含 HOST_PAGE 特判
private mountTargetWithRetry(target: string, params: Record<string, Object> | null, attempt: number = 0): void {
  const MAX = 20  // 20 × 50ms = 1s
  const stack = this.<NAV_STACK_FIELD>
  if (stack === undefined || stack === null) {
    if (attempt < MAX) setTimeout(() => this.mountTargetWithRetry(target, params, attempt + 1), 50)
    return
  }
  try { stack.clear() } catch (e) {}
  if (params !== null) stack.pushPath({ name: target, param: params })
  else stack.pushPath({ name: target })
}
```

> 嵌套 Navigation 的子页不可被 direct-mount 直达 → 标 `unreachable`。

### 6.3 ROUTER_LOAD_CONTENT（根页无 `NavPathStack`）

仅改 EntryAbility，不动根页：

```typescript
// onCreate 写 AppStorage（同 6.1）

onWindowStageCreate(windowStage: window.WindowStage): void {
  const target: string = AppStorage.get<string>('__TARGET_PAGE__') ?? ''
  const loadPath: string = target.length > 0 ? `pages/${target}` : 'pages/<ROOT_PAGE>'
  windowStage.loadContent(loadPath, (err) => {
    if (err.code && target.length > 0) windowStage.loadContent('pages/<ROOT_PAGE>')  // 回退
    AppStorage.setOrCreate<string>('__TARGET_PAGE__', '')
  })
}

onNewWant(want: Want, launchParam: AbilityConstant.LaunchParam): void {
  const target: string = (want?.parameters?.['__target_page__'] as string) ?? ''
  if (target.length === 0) return
  AppStorage.setOrCreate<string>('__TARGET_PAGE__', target)
  // fire-and-forget；onNewWant 不能 async
  router.replaceUrl({ url: `pages/${target}` }).catch((e: Error) => console.error(e.message))
}
```

> `__TARGET_PAGE__` 值约定：**全路径**（`'pages/SettingPage'`）或**短名**（`'SettingPage'`），项目内统一，否则 `pages/pages/...` 双前缀错。本模板按短名 + 桥拼前缀。

---

## 7. UI 测试 helpers（共享，每个测试文件复用）

```typescript
const BUNDLE_NAME: string = '<BUNDLE_NAME>'
const ABILITY_NAME: string = 'EntryAbility'
const MODULE_NAME: string = 'entry'   // 主 HAP；ohosTest 是 'entry_test'
let entryAbilityReady: boolean = false   // 文件级；冷热路径标志

async function mountPage(driver: Driver, page: string, params?: Record<string, Object>): Promise<void> {
  const delegator = abilityDelegatorRegistry.getAbilityDelegator()
  const parameters: Record<string, Object> = { '__test_mode__': true as Object, '__target_page__': page as Object }
  if (params !== undefined) parameters['__target_page_params__'] = params as Object
  const want: Want = { bundleName: BUNDLE_NAME, abilityName: ABILITY_NAME, moduleName: MODULE_NAME, parameters }

  if (!entryAbilityReady) {
    // 冷热路径双保险：Promise.race（v10 实测，热路径 monitor 不 fire 会超时）
    const monitor: abilityDelegatorRegistry.AbilityMonitor = { abilityName: ABILITY_NAME }
    delegator.addAbilityMonitor(monitor)
    await delegator.startAbility(want)
    try {
      const waitP: Promise<UIAbility> = delegator.waitAbilityMonitor(monitor)
      const timeoutP: Promise<UIAbility> = new Promise<UIAbility>((_r, rej) =>
        { setTimeout(() => rej(new Error('monitor-timeout')), 3000) })
      const ability: UIAbility = await Promise.race<UIAbility>([waitP, timeoutP])
      await delegator.doAbilityForeground(ability)
    } catch (_e) { /* 热路径 fallthrough：startAbility 已触发 onNewWant，桥重新挂目标页 */ }
    delegator.removeAbilityMonitor(monitor)
    entryAbilityReady = true
  } else {
    await delegator.startAbility(want)   // 同一文件后续 it：仅触发 onNewWant
  }

  // landmark 轮询代替固定 sleep（冷启动可能 1-3s）
  await driver.delayMs(500)
  let elapsed = 0
  while (elapsed < 8000) {
    try {
      const comp = await driver.findComponent(ON.id('<page_short>_root'))
      if (comp !== null) return
    } catch (_e) {}
    await driver.delayMs(500)
    elapsed += 500
  }
}

// 长 Scroll 页找屏外控件 —— **禁用 Component.scrollSearch**（实测在 50+ 行 Scroll
// 上 O(N²) 退化 + 累积内存压力，第 10 个 toggle 用例必卡死 daemon；force-cancel 又触发
// "uitest-api dose not allow calling concurrently"）。改用有限次 driver.swipe 手动滚找：
async function findInScroll(driver: Driver, _scrollId: string, id: string): Promise<Component | null> {
  const direct = await driver.findComponent(ON.id(id))
  if (direct !== null) return direct
  let size: Point | null = null
  try { size = await driver.getDisplaySize() } catch (_e) {}
  const w = (size !== null && size.x > 0) ? size.x : 1080
  const h = (size !== null && size.y > 0) ? size.y : 2340
  const cx = Math.floor(w / 2), y1 = Math.floor(h * 0.75), y2 = Math.floor(h * 0.25)
  for (let i = 0; i < 4; i++) {   // 上限 4 次：覆盖 ~3 屏长度；多了徒增噪声
    try { await driver.swipe(cx, y1, cx, y2, 1200) } catch (_e) {}
    await driver.delayMs(250)
    const hit = await driver.findComponent(ON.id(id))
    if (hit !== null) return hit
  }
  return null
}

// 状态层断言取 persistence key：查 manifest `## ID → State Key 映射` 段，禁 strip 推导
// （P0010 教训：strip 出 snake `show_hidden_items`，SettingsKeys 真值是 camel `showHiddenItems` → 37 用例 RED）
// 实现：把 manifest 映射在测试文件顶部以常量字典登记，运行时查表
const STATE_KEY_MAP: Record<string, string> = {
  // 由 step3-generate 从 manifest §map 抄入；none 标记跳过状态层
  // 'settings_show_hidden_items_toggle': 'showHiddenItems',
}
function lookupStateKey(uiId: string): string | null {
  return STATE_KEY_MAP[uiId] ?? null   // null = 仅意图层 / _IMPL_MISSING
}
```

**关键铁律**（每条都有实测失败证据）：

1. **`Driver.create()` 必须在 `beforeEach` 懒 create**，禁 `beforeAll`：beforeAll 时 delegator 未 ready，create 返回 null（不抛），后续全 `Cannot read property delayMs of null`。
2. **跨模块 startAbility 必须 `moduleName: 'entry'`**：缺失 → 整批 `startAbility failed., error in beforeEach`。
3. **冷热路径 `Promise.race` 双保险**：第二个测试文件起 EntryAbility 已 singleton 在前台 → `startAbility` 只触发 `onNewWant`，monitor 永不 fire，3s 超时兜底进热路径。
4. **landmark 轮询，禁固定 delayMs(500)**：冷启动可能 1-3s。
5. **delegator 从 `@kit.TestKit` import**，不是 `@ohos.app.ability.abilityDelegatorRegistry`。
6. **bypass 读 mock 用 `Record<string, Object>` 取字段、mountTarget 同名 target 要幂等（栈顶相同直接 return）**：cast 成 class 类型再调 `m.isVideo()` 等方法在 plain mock 上是 TypeError；反复 destroy/create 同一 NavDestination 会触发 `libark_jsruntime + libuitest` native race → 整批 `App died`。

---

## 8. 每页 AC 类型 → 断言形态

| AC 类型 | 断言 |
|---------|------|
| SMOKE | `assertComponentExist(ON.id('<page_short>_root'))` |
| COMP | `assertComponentExist(ON.id(...) / .type(...))` — type 必须是该页 spec 真实存在的类型 |
| NAV 入/出 | 点入口 → 落地页 landmark `ON.id('<target_short>_root')` |
| INTERACT_toggle | `isChecked()` 前后取反 |
| INTERACT_opens_dialog | 点击后 `ON.type('Dialog')` 或 `ON.id('xxx_dialog')` 存在 |
| INTERACT_menu | 点触发器 → `ON.text(manifest 字符串)` 存在 |
| INTERACT_swiper | `getPageSig()` 前后不等 |
| INTERACT_search | `getText()` 等于输入值 |
| INTERACT_scroll_to_bottom | `driver.swipe` + 最后一节的 row id 存在 |

**示例 it 块**：

```typescript
// COMP：直接存在性
it('P0002_UI_COMP_Grid_exists', 0, async () => {
  await driver.assertComponentExist(ON.id('main_directory_grid'))
})

// NAV：点入口 → 落地页 landmark
it('P0002_UI_NAV_to_MediaPage', 0, async () => {
  const item = await driver.findComponent(ON.type('GridItem'))
  expect(item !== null).assertTrue()
  if (item !== null) { await item.click(); await driver.delayMs(500) }
  await driver.assertComponentExist(ON.id('media_root'))
})

// INTERACT_toggle（长 Scroll 页用 findInScroll）
it('P0010_UI_INTERACT_show_hidden_items_toggle_flips_checked', 0, async () => {
  const t = await findInScroll(driver, 'settings_scroll', 'settings_show_hidden_items_toggle')
  expect(t !== null).assertTrue()
  if (t !== null) {
    const before = await t.isChecked(); await t.click(); await driver.delayMs(200)
    expect(await t.isChecked()).assertEqual(!before)
  }
})

// 不可达页（FormExtension / 必须真实 ContentResolver）
beforeAll(async () => {
  throw new Error('P00xx setup: <page> unreachable from test context')   // 不降级到 MainPage landmark
})
```

---

## 9. 反模式禁止清单（False-GREEN 速查）

| ❌ | ✅ |
|---|---|
| `if (comp) { click; assert }` 短路（找不到默认 PASS）| 正向路径无条件 `expect(comp != null).assertTrue()` + 必 click 后断言 |
| `expect(driver != null).assertTrue()` 空断言 | 断目标页特征 landmark |
| 点击无前后状态对比 | INTERACT 必须 `before / after` 对比（`isChecked` / `getText` / 控件存在变化） |
| `assertComponentExist(ON.type('Column'))` 用错页 landmark | landmark 必须该页 spec 真实存在的类型 / id |
| `ON.text('设置')` 凭空翻译 | `ON.text` 字面量可追溯到 manifest 字符串映射 |
| `_IMPL_MISSING` 用例查 `<page>_root` 然后 `expect !== null`（root 永远存在 → 伪 PASS）| `_IMPL_MISSING` 用 `assertComponentExist(ON.id('<期望但不存在的 id>'))` 让它必 RED 暴露 spec gap |
| `driver.scrollSearch(...)` (不存在) / 直接 `Component.scrollSearch`（O(N²) 退化 + 卡死 daemon）| `findInScroll` helper（有限次 `driver.swipe` 手动滚 ≤4 次） |
| `withTimeout(scrollToTop, ...)` 类用 setTimeout 包裹 uitest API | uitest API 无 cancel：超时 resolve 后下次调用必抛 `dose not allow calling concurrently`；只能改用即发即返的 `driver.swipe` |
| 每个 it() beforeEach 都 `resetScrollToTop`（造成屏幕反复颠簸）| 让 scroll 位置自然继承，下个 it 找邻近 toggle 就近滚 |
| `stateKey = uiId.replace('settings_','').replace('_toggle','')` 推导 persistence key | `lookupStateKey(uiId)` 查 manifest `## ID → State Key 映射`；snake↔camel 必显式映射 |
| 一个页面多条 it 全用同一通用类型（Grid/Column）| 不同 it 用不同 id / type；同类型集中是设计退化信号 |
| `afterAll` 含业务断言 | `afterAll` 只清理 |
| `beforeAll(async () => { driver = await Driver.create() })` | `beforeEach` 懒 create |

**枚举铁律**（设计要求 + 生成必跑）：菜单项 / CAB 动作 / 设置项 / `@State boolean` Toggle 各**每项一条 it()**，禁合并；Scroll 页额外 1 条 `scroll_to_bottom_reveals_*`。

---

## 10. ArkTS 严格模式 + UI 编译要点

| 规则 | ❌ | ✅ |
|------|---|---|
| `arkts-no-untyped-obj-literals` | `const m = { id: 1 }` 裸对象 / `parameters: { ... }` | 复用源码类 `new Xxx()` + 字段赋值；或定义 `interface`；`Want.parameters: Record<string, Object>` |
| `arkts-no-any-unknown` | `let x` / `: any` / `as unknown` | 显式类型；ArkTS top type 是 `Object` |
| `arkts-no-ns-as-obj` | `mocker.mockFunc(http, http.request)` 传 namespace | 包 class shim 后 mock 实例（仅 ut 相关；UI 默认走 mock 数据） |
| `arkts-no-nested-funcs` | it() 内 `function buildMockX(...) {}` | 提到 describe 之外作 module-scope helper |
| `arkts-limited-throw` | `throw err` (err 是 unknown) | `throw err instanceof Error ? err : new Error(String(err))` |
| TestKit 大小写 | `AbilityDelegatorRegistry.xxx` | 小写实例 `abilityDelegatorRegistry.getAbilityDelegator()`；UiTest 从 `@ohos.UiTest` import |
| `startAbility` Want | `await driver.startAbility({...})` 裸对象 | `import { Want } from '@kit.AbilityKit'`；`Want` 类型必填 `moduleName: 'entry'` |

---

## 11. 设备前置（跑测前必做，否则整批 ERROR）

```bash
# (1) 系统 ArkUI 测试模式 — 改完需重启设备
$HDC -t $DEVICE shell param set persist.ace.testmode.enabled 1 && $HDC -t $DEVICE shell reboot

# (2) auto-sign：DevEco → Project Structure → Signing Configs → 勾 Automatically generate signature

# (3) uitest daemon —— 跑测时必须与 aa test 在同一条 hdc shell 链式执行（token=0 固定）
$HDC -t $DEVICE shell "uitest start-daemon 0; aa test -b $BUNDLE -m entry_test \
  -s unittest OpenHarmonyTestRunner -s timeout 600000" > /tmp/ui-run.log 2>&1
```

**四个常见根因**（症状都是"所有 UI ERROR / 拿不到窗口 / Cannot read property xxx of null"）：

| 根因 | 特征日志 | 修法 |
|------|---------|------|
| daemon 没起 / 被杀 | `Wait for ApiCaller publish by server timeout` + `ipc connection is dead (17000006)` | 链式命令；token=0 |
| 没开 auto-sign | `NapiDefineClass occur exception, className:Driver` | DevEco 勾自动签名，重编重装 |
| `Driver.create()` 在 beforeAll | beforeAll 阶段 `Cannot get AbilityDelegator` | 改 `beforeEach` 懒 create |
| testmode 没开 | `Get windows failed` / `GetRootByWindow failed` | `param set persist.ace.testmode.enabled 1` 后重启设备 |
