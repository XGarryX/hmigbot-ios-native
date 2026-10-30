# UI 测试反模式（False-GREEN 陷阱）

TDD 的生命线是"没实装就要 RED"。下面按主题分 6 类整理常见陷阱；Step 3 agent 生成时必须全部规避，修旧代码时全部清除。

---

## 1. 路由与挂载

### 症结
Navigation 宿主页自挂载不能 `pushPath(self)`（路由匹配不到，静默失败害 beforeAll landmark 挂掉）；direct-mount 桥若 Step 2 未在 EntryAbility + 根页两侧都注入，Step 3 整批测试启动即 ERROR。

**对策**：Watch handler 对宿主页名特判（消费 token 但不 push，见 `templates/direct-mount-bridge.md` 的 `<HOST_PAGE_NAME>` 分支）；`aboutToAppear` 首次读取做同样处理。Step 2 必须同时注入 A/B 两半。

### ❌ vs ✅

```typescript
// ❌ 把 Navigation-host 当普通 NavDestination push
onTargetPageChange(): void {
  this.navPathStack.pushPath({ name: this.directMountTarget })   // pushPath('MainPage') 静默失败
}

// ✅ 对宿主页特判
if (targetPage === 'MainPage') {
  AppStorage.setOrCreate('__TARGET_PAGE__', '')
  try { this.navPathStack.clear() } catch (e) {}
  return
}
this.navPathStack.pushPath({ name: targetPage })
```

---

## 2. 查找组件

### 症结
`driver.scrollSearch` **不存在**（编译期 error "Property 'scrollSearch' does not exist on type 'Driver'"）—— 只有 `Component.scrollSearch`。`driver.findComponent(ON.id(X))` 只在当前视口内搜索，Scroll/List 屏外的 toggle/row 一律返回 null。manifest 没注入的 id 写在测试里必然找不到。

**对策**：长 Scroll 页用 `findInScroll(driver, scrollId, id)` helper（先 findComponent，再 Scroll 容器 `scrollSearch`）。manifest 缺 id 的组件写 `// TODO[id-needed]` + `ON.type` 兜底，并 BLOCKERS 报 `manifest gap`。

### ❌ vs ✅

```typescript
// ❌ 期望 driver 有 scrollSearch
const t = await driver.scrollSearch(ON.id('settings_autoplay_toggle'))   // 编译错

// ✅ 用 Component.scrollSearch
const scroll = await driver.findComponent(ON.id('settings_scroll'))
const t = scroll !== null ? await scroll.scrollSearch(ON.id('settings_autoplay_toggle')) : null
```

---

## 3. 测试隔离与 Driver 生命周期

### 症结

两个独立问题常被一起踩：

1. **`beforeAll` 里 `Driver.create()` 返回 null**：hypium 的 `beforeAll` 在 `OpenHarmonyTestRunner.onRun()` 里 `delegator.startAbility(TestAbility)` 尚未 resolve 时就触发；delegator 未 ready，`@ohos.UiTest` 的 `Driver.create()` 静默返回 null（不抛异常），之后每个 it 的 beforeEach 都挂在 `driver.delayMs(...)` 报 `Cannot read property delayMs of null`。——这是"所有 it 统一 ERROR"最常见的根因之一。
2. **`beforeAll` 只挂载一次，it 间状态不重置**：nav click / Dialog / CAB / toggle 改变 driver 当前页，后续 it 在错的页面跑。多条 it 共享状态但没有独立启动 → 偶发 PASS / FAIL 取决于执行顺序。

### 对策（统一规则：只用 `beforeEach`，不用 `beforeAll`）

```typescript
let driver: Driver   // 不初始化，交给 beforeEach

beforeEach(async () => {
  // ① 懒初始化：只在第一次 beforeEach 建 Driver，整个 describe 复用
  if (driver === undefined) driver = await Driver.create()
  // ② 每个 it 前重新挂载，保证状态干净
  await mountPage(driver, '<PageName>')
  await driver.assertComponentExist(ON.id('<page_short>_root'))
})
```

判据：`grep -E "(NAV_|_opens_dialog|_cab_|_flips_checked|menu_)"` 命中即必须 `beforeEach` + remount。即使短 describe 只含只读 COMP，也建议统一用 `beforeEach` 模板，保持代码一致。

### ❌ vs ✅

```typescript
// ❌ beforeAll 里 Driver.create() —— 返回 null，整批 it 挂
beforeAll(async () => {
  driver = await Driver.create()                 // 此时 delegator 还没 ready，拿到 null
  await mountPage(driver, 'MainPage')             // driver.delayMs 抛 TypeError
})

// ❌ 只 beforeAll，第一条 it 跳到子页没回
beforeAll(async () => { await mountPage(driver, 'MainPage') })
it('A', ..., async () => { await firstDir.click() /* 进了详情，没返回 */ })
it('B', ..., async () => { /* 以为在主页，其实在详情 */ })

// ✅ 懒 create + 每次 remount
let driver: Driver
beforeEach(async () => {
  if (driver === undefined) driver = await Driver.create()
  await mountPage(driver, 'MainPage')
  await driver.assertComponentExist(ON.id('main_root'))
})
```

**注**：Driver 没有 `release()` / `destroy()` 公开 API，生命周期由 GC 管理；跨 it 复用同一实例完全安全（`startAbility` 重启 ability 不会让 Driver handle 失效，前提是 uitest daemon 在跑）。因此不需要 `afterEach` 清理。

---

## 4. 等待与时序

### 症结
beforeEach 启动 App 不等 landmark 断言就继续，或者每一跳都用 `if (comp)` 保护，链路任何一环没拉起来都不报错，后面 it 在错的页面跑（`aa test` 启动的是 DevEco TestAbility 白页，不是 EntryAbility；必须靠 `delegator.startAbility` 把真实应用拉前台）。

**对策**：`beforeEach` 末尾必须 `assertComponentExist(ON.id('<page_short>_root'))` landmark；每一跳失败就 `throw new Error(...)`，让这条 it 被标 SETUP_FAILED。`delayMs(500)` 经实测足够，早期 `1500` 是保守值可以降。

### ❌ vs ✅

```typescript
// ❌ 链路每步 if 保护，整条链静默失败
beforeEach(async () => {
  await delegator.startAbility(want)
  const overflow = await driver.findComponent(ON.text('更多'))
  if (overflow) { await overflow.click() }   // 找不到就跳过
})

// ✅ 每跳无条件断言 + 落脚 landmark
beforeEach(async () => {
  if (driver === undefined) driver = await Driver.create()
  await delegator.startAbility(want)
  await driver.delayMs(500)
  await driver.assertComponentExist(ON.id('main_root'))   // 落脚
})
```

---

## 5. 断言

### 症结
`if (comp) { click; assert }` 短路：找不到 comp 就直接 return 没任何断言 → 默认 PASS（最常见 False-GREEN 来源）。`expect(driver != null)` 空断言（`Driver.create()` 成功后永远非 null）。点击无状态对比断言。用 MainPage 的 Grid/Column 当"到不了目标页"的兜底 landmark（断言通过但测的是错的页）。Feature 派生 UI AC 只断言"某组件存在"跟页面级 COMP 重复注水。afterAll 里夹业务断言难诊断。

**对策**：正向路径**无条件** `expect(comp != null).assertTrue()`；SMOKE 断目标页特征 landmark（`ON.id('<page_short>_root')` 或 spec 独有文案/类型）；INTERACT 必须点击前后状态对比；`assertComponentExist(ON.type(X))` 的 X 必须是**该页** spec 真实存在的类型；不可达页 `beforeAll` 必须 `throw new Error('Pxxxx setup: <page> unreachable from test context')` 而不是降级到 MainPage landmark；afterAll 只清理。

### ❌ vs ✅

```typescript
// ❌ 短路 + 用错页 landmark
it('P0016_UI_COMP_Canvas_exists', 0, async () => {
  const canvas = await driver.findComponent(ON.type('Canvas'))
  if (canvas) { await driver.assertComponentExist(ON.type('Column')) }  // Column 是 MainPage 的
})

// ✅ 断目标页特征
it('P0016_UI_COMP_Canvas_exists', 0, async () => {
  await driver.assertComponentExist(ON.type('Canvas'))   // Canvas 是 EditPage 独有
})
```

---

## 6. 类型与 API

### 症结
`Driver` vs `Component` API 混用（`driver.scrollSearch` 不存在，见第 2 节）。`ON.text(...)` 字面量凭空翻译（spec 写英文 "Settings" 就直接 `ON.text('设置')`，或反之），selector 必须有可信来源：ID → manifest，文本 → manifest "字符串映射"（来自 `string.json`），类型 → spec `## 转换决策`。中文 UI 禁用英文文本匹配。

**对策**：selector 严格走优先级 `ON.id` > `ON.text(manifest 字符串)` > `ON.type(spec 真实类型)`；写完 grep 每条 `ON.text(...)` 字面量必须能在 manifest "字符串映射" 或对应 spec 中找到原文，找不到就是 agent 编的，改为 `ON.id` 或带追溯注释。

### ❌ vs ✅

```typescript
// ❌ 凭空翻译
const overflow = await driver.findComponent(ON.text('更多'))   // manifest 里没这个字面量

// ✅ 走 manifest
const overflow = await driver.findComponent(ON.id('main_overflow_btn'))
if (!overflow) throw new Error('main_overflow_btn missing')
// 菜单项：value 从 manifest 字符串映射取
const settings = await driver.findComponent(ON.text('Settings'))  // string.json:settings.value
```

---

## 7. IMPL_MISSING 占位伪 PASS（最严重 False-GREEN）

### 症结

`_IMPL_MISSING` 后缀的 it() 是 R1 规则的"占位 RED"——spec 描述了交互点但 manifest/源码没对应组件 → 测试体应该尝试 `assertComponentExist` 一个**找不到的 id** → 抛错 → RED → 暴露 spec gap。

但 Step 3 Agent 容易写错成"检查页面根容器存在"，让测试永远 PASS：源码没实装组件 → 但 root 永远在 → 测试 GREEN → 假装"功能 OK"。这是最严重的 False-GREEN，因为它把 spec gap 完全藏起来了。

### ❌ vs ✅

```typescript
// ❌ 永远 PASS — 检查的是页面根容器，不是 spec 描述的"缺失组件"
it('P0001_UI_NAV_to_SettingPage_IMPL_MISSING', 0, async () => {
  const root = await driver.findComponent(ON.id('browser_root'))
  expect(root !== null).assertTrue()    // root 永远存在
})

// ❌ 同样错 — findComponent + expect != null
it('P0007_UI_INTERACT_click_link_icon_launches_url_IMPL_MISSING', 0, async () => {
  const comp = await driver.findComponent(ON.id('highlights_link_btn'))   // 找不到 → null
  expect(comp !== null).assertTrue()    // null !== null = false → FAIL? 不！
  // 注：如果 findComponent 成功（组件存在），则这条永远 PASS；如果失败返 null，则上面 assertTrue 才 FAIL
  // 但 IMPL_MISSING 期望的是"源码没该组件" → 应该 FAIL 暴露问题，不应留 expect 弱化判断
})

// ✅ 期望 RED — assertComponentExist 找不到就抛错
it('P0001_UI_NAV_to_SettingPage_IMPL_MISSING', 0, async () => {
  // spec 写"工具栏 settings 按钮 → SettingActivity"
  // 推导期望 id：`browser_toolbar_settings_btn`
  // 当前 manifest 里没这个 id（BrowserToolbar 子组件 .id 没注入）
  // 真实装后 → 这条转 GREEN；目前必 RED 暴露 spec gap
  await driver.assertComponentExist(ON.id('browser_toolbar_settings_btn'))
})
```

### 对策（生成阶段自检铁律）

写完 `*_UI.test.ets` 文件后，主线程跑：

```bash
# 命中即必须 BLOCKER 重写
grep -B1 -A6 "_IMPL_MISSING" entry/src/ohosTest/ets/test/ui/*.test.ets | \
  grep -cE "expect\([a-zA-Z_]+ ?!== ?null\)\.assertTrue|expect\((true|false|null)\)\."
```

详细自检脚本见 `references/agent-prompts/step3-ui-test-agent.md §6.1`。

---

## 生成阶段自检清单（Step 3 Agent 必走）

写完任何 UI 测试文件之前，全文 grep 确认：

- [ ] 没有 `if (.*) {` 包裹的正向路径（只有 afterAll 恢复场景允许）
- [ ] 没有 `expect(driver != null)` 空断言
- [ ] beforeAll 结尾有 landmark `assertComponentExist(ON.id('<page_short>_root'))`
- [ ] 每个 `it()` 至少有一条 `expect(...).assert*` 或 `assertComponentExist`
- [ ] `ON.text(...)` 字面量每条可追溯到 manifest "字符串映射" 或 spec
- [ ] INTERACT 类用例有点击前后状态对比（不是仅 click）
- [ ] `afterAll` 不含业务断言
- [ ] 所有 `assertComponentExist(ON.type(X))` 的 X 必须是被测页 spec 真实存在的类型
- [ ] 一个页面的多条 it() 不应全部收敛到同一个通用类型（Grid/Column）
- [ ] 不可达页 `beforeAll` `throw new Error(...)` 而不降级到 MainPage landmark
- [ ] 设置页 INTERACT `_toggle_*` 条数 ≥ spec `## 状态接口` 去重后 `@Local boolean` 行数
- [ ] 设置页 INTERACT `_row_opens_*` / `_row_triggers_*` 条数 ≥ spec TextValueRow/OneLinerRow 行数
- [ ] 带溢出菜单的页 INTERACT `_menu_*` 条数 = spec `## 菜单项` 表行数
- [ ] 带 CAB 的页 INTERACT `_cab_*` 条数 = spec `## CAB` 表行数
- [ ] Scroll / List / NestedScrollView 页至少一条 `INTERACT_scroll_to_bottom_reveals_*`
- [ ] Navigation-host 测试用例的桥模板 `<HOST_PAGE_NAME>` 占位符已替换
- [ ] 长 Scroll 页非顶层 landmark 的 `ON.id` 查找使用 `findInScroll` helper
- [ ] describe 含 NAV_/_opens_dialog/cab_/_flips_checked/menu_ 的 it → 有 `beforeEach`
- [ ] **`_IMPL_MISSING` 后缀的 it() 测试体里必须出现 `await driver.assertComponentExist(ON.id(...))`**（§7 反模式）
- [ ] **`_IMPL_MISSING` 后缀的 it() 不允许出现 `findComponent(ON.id(<page>_root))` + `expect(... !== null).assertTrue()`**（伪 PASS 模式）
- [ ] **`_IMPL_MISSING` 后缀的 it() 不允许只 `expect(true|false|null).assertXxx()`**（空断言）

---

## 相关文档

- `templates/direct-mount-bridge.md` — Step 2 注入的桥模板（Navigation-host 特判）
- `templates/ui-test-skeleton.md` — mountPage / findInScroll helper + beforeEach 模板
- `compile-pitfalls.md` — ArkTS 严格模式 + arkXtest API 编译期陷阱
- `spec-parsing-guide.md` — 从 spec 推导 UI AC 的解析规则
