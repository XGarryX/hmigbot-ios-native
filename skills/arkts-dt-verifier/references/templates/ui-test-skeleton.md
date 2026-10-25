# UI 测试文件骨架模板

**文件位置**：`entry/src/ohosTest/ets/test/ui/P{编号}_{PageName}_UI.test.ets`

**命名**：每个 `page_000x.md` 对应一个文件。`it()` 名：
- 页面派生：`P{编号}_UI_{SMOKE|COMP|NAV|INTERACT}_xxx`
- Feature 派生：`F{编号}_UI_AC{序号}_xxx`

**占位符**：
- `<BUNDLE_NAME>` / `<ABILITY_NAME>` — 从输入参数填入
- `<PageName>` — NavDestination name（MainPage 的 PageMapBuilder 注册名）
- `<page_short>` — 见 `testable-id-catalog.md` 命名规范

---

## ⚠️ 关键写法规则（实测验证，勿擅改）

以下每一条都有实测失败证据支撑。详见 `references/ui-test-antipatterns.md`。

1. **必须用 `beforeEach`，不能用 `beforeAll` 做 `Driver.create()`**
   - 反例：`beforeAll(() => { driver = await Driver.create() })` —— 在 hypium `beforeAll` 执行时，`OpenHarmonyTestRunner.onRun` 里 `delegator.startAbility(TestAbility)` 还没 resolve，delegator 未 ready，`Driver.create()` 静默返回 **null**（不抛异常），后续 `driver.delayMs/findComponent` 全部 `Cannot read property xxx of null`。
   - 正例：`beforeEach` 里 lazy create（见骨架）。
2. **Driver 懒初始化 + 跨 it 复用**
   - `if (driver === undefined) driver = await Driver.create()` —— 只在第一次 beforeEach 建 Driver，之后整个 describe 共享。每个 `it` 都 create 一次虽然也能过，但每次 IPC 握手 ~300ms，数量多会慢。
   - Driver 没有 `release()` API，靠 GC 回收。一个 describe 全程 1 个 Driver 实例，不用 afterEach 清理。
3. **跨模块 startAbility 必须显式指定 `moduleName: 'entry'`**（2026-04-16 实测根因，v8 有、v9 丢了）
   - ohosTest module 名是 `entry_test`，主 HAP module 名是 `entry`。ohosTest 测试从 TestAbility 侧发起 `delegator.startAbility` 到 EntryAbility 时，AMS 需要 `moduleName` 才能定位 EntryAbility 所在 HAP。
   - 缺 `moduleName` 的症状是**整批 UI 测试** `startAbility failed., error in beforeEach function`，hilog 不给具体错误码，很容易误诊断成"权限/签名/skills 冲突"，实际就是少一行字段。
   - 正例：`{ bundleName, abilityName: 'EntryAbility', moduleName: 'entry', parameters: {...} }`。
4. **首次冷启动必须用 AbilityMonitor + doAbilityForeground 握手，冷/热路径必须用 `Promise.race + try-catch` 双保险**
   - `delegator.startAbility(want)` 是 fire-and-forget 语义，返回时 Ability 可能还在 create/backgroud 状态。直接 `findComponent` 会因为 window 还没前台化而拿不到组件。
   - ⚠️ **v10 实测坑（2026-04-16）**：`entryAbilityReady` 标志位是**文件级**的（每个 `.test.ets` 顶部有自己的 `let entryAbilityReady = false`）。第一个 UI 测试文件（比如 P0002_MainPage_UI）冷启动成功，`entryAbilityReady=true`。但切到第二个文件（P0003_MediaPage_UI）时，该文件的 `entryAbilityReady` 仍是 `false` → 走冷路径 → `addAbilityMonitor(EntryAbility)` + `startAbility` + `waitAbilityMonitor`。此时 EntryAbility 是 singleton 已经在前台，`startAbility` 只触发 `onNewWant`，**不触发 onCreate → monitor 永远不 fire → `waitAbilityMonitor` 超时（5s 左右）报错 `Calling WaitAbilityMonitor failed.`，该文件**整批 `it()` 全 ERROR**。
   - 症状是：P0002 测试 OK，P0003+ 所有页 ERROR，stream=`Calling WaitAbilityMonitor failed., error in beforeEach function`。命中这个就是本坑。
   - 正确流程（**`Promise.race` 超时 + `try-catch` fallthrough**，v10 开始强制）：
     ```typescript
     if (!entryAbilityReady) {
       const monitor: abilityDelegatorRegistry.AbilityMonitor = { abilityName: ABILITY_NAME }
       delegator.addAbilityMonitor(monitor)
       await delegator.startAbility(want)
       try {
         // 冷路径：Ability 第一次 create，waitAbilityMonitor 会 fire
         // 热路径（Ability 已在前台）：monitor 永不 fire，用 3s timeout 兜底
         const waitPromise: Promise<UIAbility> = delegator.waitAbilityMonitor(monitor)
         const timeoutPromise: Promise<UIAbility> = new Promise<UIAbility>((_r, rej) =>
           { setTimeout(() => rej(new Error('monitor-timeout')), 3000) })
         const ability: UIAbility = await Promise.race<UIAbility>([waitPromise, timeoutPromise])
         await delegator.doAbilityForeground(ability)
       } catch (_e) {
         // 热路径 —— EntryAbility 已从前一个测试文件活着；startAbility 上面已触发 onNewWant，桥会重新挂目标页
       }
       delegator.removeAbilityMonitor(monitor)
       entryAbilityReady = true
     } else {
       await delegator.startAbility(want)  // 同一文件内后续 it()：EntryAbility 已 ready，仅触发 onNewWant
     }
     ```
   - 为什么不直接把 `entryAbilityReady` 做成跨文件共享（比如 AppStorage）：Hypium 测试进程可能为每个 describe 重建 JS context，AppStorage/全局 let 都不保证跨文件持久；Promise.race 方案更稳。
5. **delegator 从 `@kit.TestKit` import，不是 `@ohos.app.ability.abilityDelegatorRegistry`**
   - 两者方法签名相似，但 `@kit.TestKit` 的 delegator 是 arkXtest 官方推荐入口，行为在 ohosTest 测试场景下经验证稳定。
6. **landmark 轮询，不要靠固定 `delayMs`**
   - 冷启动 + 首屏挂载 + NavPathStack.pushPath 到目标页可能要 1–3s，固定 `delayMs(500)` 会 flaky。
   - 骨架 mountPage 在 startAbility 后轮询 `ON.id('<page_short>_root')` 直到出现或超时（默认 8s × 500ms）。超时就让测试 ERROR，beforeEach 显式暴露挂载失败。
7. **手工启动 uitest daemon 是必须的**
   - 跑测前：`hdc shell uitest start-daemon 0`（token 必须是 `0`）。
   - daemon 不是"delegator 会自动拉起"（之前的误判），**不起 daemon 整批 UI 会 ERROR**，错误签名是 `Wait for ApiCaller publish by server timeout` + `ipc connection is dead (17000006)`。
8. **签名必须 auto-generate**
   - 否则 hilog 里会出现 `NapiDefineClass occur exception, className:Driver`，Driver 类根本 define 不出来，`Driver.create()` 永远返回 null。DevEco Studio → File → Project Structure → Signing Configs → 勾 **Automatically generate signature**。

---

## 共享 helpers（放在测试文件顶部 import 之后，每个 UI 测试文件复用）

```typescript
const BUNDLE_NAME: string = '<BUNDLE_NAME>'
const ABILITY_NAME: string = 'EntryAbility'
const MODULE_NAME: string = 'entry'   // 主 HAP 模块名；ohosTest 模块是 'entry_test'
const LANDMARK_POLL_MAX_MS: number = 8000
const LANDMARK_POLL_STEP_MS: number = 500

// 冷热路径标志：首次冷启动走 monitor 流程；后续调用仅 startAbility（触发 onNewWant）。
let entryAbilityReady: boolean = false

// --- 标准 direct-mount helper ---
// 关键点（每一行都有实测失败证据）：
//   * moduleName='entry' 必填（缺失 → startAbility failed.）
//   * 首次冷启动用 addAbilityMonitor+waitAbilityMonitor+doAbilityForeground 握手
//   * 后续调用直接 startAbility（EntryAbility singleton → onNewWant → 桥重新触发）
//   * 用轮询目标页 landmark 代替固定 delayMs，冷启动/重页面可能 1–3s
async function mountPage(
  driver: Driver,
  page: string,
  params?: Record<string, Object>
): Promise<void> {
  const delegator = abilityDelegatorRegistry.getAbilityDelegator()

  const parameters: Record<string, Object> = {
    '__test_mode__': true as Object,
    '__target_page__': page as Object
  }
  if (params !== undefined) {
    parameters['__target_page_params__'] = params as Object
  }
  const want: Want = {
    bundleName: BUNDLE_NAME,
    abilityName: ABILITY_NAME,
    moduleName: MODULE_NAME,
    parameters: parameters
  }

  if (!entryAbilityReady) {
    const monitor: abilityDelegatorRegistry.AbilityMonitor = { abilityName: ABILITY_NAME }
    delegator.addAbilityMonitor(monitor)
    await delegator.startAbility(want)
    try {
      // 冷路径走 waitAbilityMonitor；若 Ability 已在前台（跨文件后续），用 3s 超时兜底
      const waitPromise: Promise<UIAbility> = delegator.waitAbilityMonitor(monitor)
      const timeoutPromise: Promise<UIAbility> = new Promise<UIAbility>((_r, rej) =>
        { setTimeout(() => rej(new Error('monitor-timeout')), 3000) })
      const ability: UIAbility = await Promise.race<UIAbility>([waitPromise, timeoutPromise])
      await delegator.doAbilityForeground(ability)
    } catch (_e) {
      // 热路径：EntryAbility 已活着（上一个测试文件残留），startAbility 已触发 onNewWant
    }
    delegator.removeAbilityMonitor(monitor)
    entryAbilityReady = true
  } else {
    await delegator.startAbility(want)
  }

  await driver.delayMs(LANDMARK_POLL_STEP_MS)
  let elapsed = 0
  while (elapsed < LANDMARK_POLL_MAX_MS) {
    try {
      const comp = await driver.findComponent(ON.id('<page_short>_root'))
      if (comp !== null) return
    } catch (_e) { /* not found yet */ }
    await driver.delayMs(LANDMARK_POLL_STEP_MS)
    elapsed += LANDMARK_POLL_STEP_MS
  }
}

// --- 长 Scroll 页找屏外控件 ---
// driver.scrollSearch 不存在（编译期 error），只有 Component.scrollSearch。
// 仅在页面根为 Scroll/List 且子项超出首屏时需要；短页面可省。
async function findInScroll(
  driver: Driver,
  scrollId: string,
  id: string
): Promise<Component | null> {
  const direct = await driver.findComponent(ON.id(id))
  if (direct !== null) return direct
  try {
    const scroll = await driver.findComponent(ON.id(scrollId))
    if (scroll !== null) return await scroll.scrollSearch(ON.id(id))
  } catch (_e) {}
  return null
}
```

---

## 完整骨架

```typescript
import { describe, it, expect, beforeEach } from '@ohos/hypium'
import { Driver, ON, Component } from '@ohos.UiTest'
import { abilityDelegatorRegistry } from '@kit.TestKit'
import { UIAbility, Want } from '@kit.AbilityKit'

// （此处插入上方"共享 helpers" 区块：常量 + entryAbilityReady + mountPage + findInScroll）

export default function <PageName>_UI() {
  describe('<PageName>_UI', () => {
    let driver: Driver

    // ⚠️ 不要用 beforeAll：delegator 未 ready，Driver.create() 会返回 null
    beforeEach(async () => {
      if (driver === undefined) driver = await Driver.create()   // 懒初始化 + 跨 it 复用
      await mountPage(driver, '<PageName>')
      // 目标页若 onReady 读 params：
      //   await mountPage(driver, 'MediaPage', { 'path': TEST_DIR_CAMERA as Object })
      // Landmark：确认直挂成功；失败则整个 describe ERROR
      await driver.assertComponentExist(ON.id('<page_short>_root'))
    })

    // ========== 示例 it 块 ==========

    // COMP：存在性
    it('P0002_UI_COMP_Grid_exists', 0, async () => {
      await driver.assertComponentExist(ON.id('main_directory_grid'))
    })

    // NAV：点本页入口 → 落地页 landmark
    it('P0002_UI_NAV_to_MediaPage', 0, async () => {
      const firstDir = await driver.findComponent(ON.type('GridItem'))
      expect(firstDir !== null).assertTrue()
      if (firstDir !== null) {
        await firstDir.click()
        await driver.delayMs(500)
      }
      await driver.assertComponentExist(ON.id('media_root'))
    })

    // INTERACT：Dialog 弹出
    it('P0010_UI_INTERACT_click_sort_row_opens_dialog', 0, async () => {
      const row = await driver.findComponent(ON.id('settings_sort_row'))
      expect(row !== null).assertTrue()
      if (row !== null) { await row.click(); await driver.delayMs(300) }
      await driver.assertComponentExist(ON.type('Dialog'))
    })

    // INTERACT：Toggle 翻转（长 Scroll 页用 findInScroll）
    it('P0010_UI_INTERACT_show_hidden_items_toggle_flips_checked', 0, async () => {
      const toggle = await findInScroll(driver, 'settings_scroll', 'settings_show_hidden_items_toggle')
      expect(toggle !== null).assertTrue()
      if (toggle !== null) {
        const before = await toggle.isChecked()
        await toggle.click()
        await driver.delayMs(200)
        const after = await toggle.isChecked()
        expect(after).assertEqual(!before)
      }
    })

    // INTERACT：LazyForEach 子项点击（动态项不能加 .id()，用 ON.type+index 兜底）
    it('P0007_UI_INTERACT_click_first_article_navigates_to_detail', 0, async () => {
      // 前置：TestDataSetup 注入 mock article ≥ 1 条（已 mock 好）
      // 容器有稳定 id（highlights_articles_list），子项类型唯一（ListItem）
      const items = await driver.findComponents(ON.type('ListItem'))
      expect(items.length).assertLargerOrEqual(1)
      await items[0].click()
      await driver.delayMs(500)
      await driver.assertComponentExist(ON.id('highlights_detail_root'))
    })

    // INTERACT：LazyForEach 子项长按（触发 CAB / 删除确认）
    it('P0007_UI_INTERACT_long_press_first_article_opens_cab', 0, async () => {
      const items = await driver.findComponents(ON.type('ListItem'))
      expect(items.length).assertLargerOrEqual(1)
      await items[0].longClick()
      await driver.delayMs(300)
      await driver.assertComponentExist(ON.id('highlights_cab_delete_btn'))   // CAB landmark
    })
  })
}
```

---

## 何时用 `findInScroll`

判据：页面根为 `Scroll` / `List` 且子项超出首屏（典型：SettingsPage）。

对**非顶层 landmark**（root / scroll / toolbar / back_btn / toolbar_title 这些总在首屏的元素以外）的 `ON.id(...)` 查找统一走 `findInScroll`。

原因：`driver.findComponent(ON.id(X))` 只返回当前视口内的组件；Scroll/List 里屏外的 toggle/row 一律返回 null。
