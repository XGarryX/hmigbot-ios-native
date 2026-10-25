# 编译陷阱速查（ArkTS 严格模式 + arkXtest API）

生成测试文件前**必读**。这里列的每一条都是实测过 210+ 个编译错误浓缩出来的，照做可以把生成→编译通过率从 "满屏红" 推到一次性通过。

---

## 1. arkXtest API 幻觉清单（最高频坑）

❌ **`driver.dumpLayout()` 不存在** — `@ohos.UiTest` / `@kit.TestKit` 导出的 `Driver` 没有这个方法。一旦写了，整条链路返回 `any`，会级联出 1 条 `dumpLayout` 错 + 若干条 `arkts-no-any-unknown` 错。

| ❌ 禁用 | ✅ 替代 |
|---------|---------|
| `const layout = await driver.dumpLayout(); expect(layout.includes('收藏')).assertTrue()` | `const c = await driver.findComponent(ON.text('收藏')); expect(c != null).assertTrue()` |
| 用 dumpLayout 判断"页面渲染完成" | `await driver.assertComponentExist(ON.type('Grid'))` 或 `await driver.delayMs(500)` 做兜底 |
| 用 dumpLayout 做"点击后菜单弹出"断言 | 直接 `findComponent(ON.text('菜单项文本'))` 断言非空 |

其他容易写错的 API：
- ❌ `driver.pressBack()` → ✅ `driver.pressBack()` 是存在的，但有些 SDK 叫 `triggerKey(KeyCode.KEY_BACK)`，以实机为准。
- ❌ `component.dumpInfo()` → ✅ `component.getText()` / `component.getId()` / `component.isChecked()`
- ❌ `driver.swipe(x1,y1,x2,y2)` 期望返回值 → ✅ `swipe` 返回 `Promise<void>`，不要赋值接收

---

## 2. ArkTS 严格模式速查

### 2.1 `arkts-no-untyped-obj-literals` — 对象字面量必须有类型

❌ 禁写：
```typescript
const medium = { id: 1, path: 'x.jpg', isVideo: false }       // 裸对象
const params = { __test_mode__: true }                          // 传给 startAbility 也不行
```

✅ 三种修法（优先级从高到低）：

**(a) 复用源码 model class（首选）**
```typescript
import { Medium } from '../../../../main/ets/models/Medium'
const medium = new Medium()
medium.id = 1
medium.path = 'x.jpg'
medium.isVideo = false
```

**(b) 测试文件内定义 interface**
```typescript
interface TestMedium { id: number; path: string; isVideo: boolean }
const medium: TestMedium = { id: 1, path: 'x.jpg', isVideo: false }
```

**(c) Record / 类型断言（仅应急）**
```typescript
const params: Record<string, boolean> = { '__test_mode__': true }
```

### 2.2 `arkts-no-any-unknown` — 禁用 any / unknown

❌ `const layout: any = ...` / `let x` (默认推断 any) / `(data as unknown as Medium)`

✅ 所有局部变量、函数参数、返回类型都显式给 → 用 `Object`（ArkTS 的 top type）或具体 interface。

### 2.3 `arkts-no-ns-as-obj` — 不能把命名空间当对象

❌ 禁写（MockKit 场景最常见）：
```typescript
import fileIo from '@ohos.file.fs'
when(mocker.mockFunc(fileIo, fileIo.copyFile)).afterReturn(...)   // fileIo 是 namespace
```

✅ 包一层 class shim，对实例 mock：
```typescript
class FileIoShim {
  async copyFile(src: string, dst: string): Promise<void> { return fileIo.copyFile(src, dst) }
  async unlink(p: string): Promise<void> { return fileIo.unlink(p) }
}
const shim = new FileIoShim()
const mockCopy = mocker.mockFunc(shim, shim.copyFile)
```

然后把生产代码里的 `fileIo.copyFile` 调用替换成注入的 shim（或让 Service 接受 shim 作为依赖）。

### 2.4 `arkts-no-func-apply-call` — 禁止 `.call()` / `.apply()`

❌ `fn.call(thisArg, a, b)`
✅ 直接 `fn(a, b)`，或把函数解出来 `const f = obj.method.bind(obj); f(a,b)`，或箭头包裹。

### 2.5 `arkts-no-obj-literals-as-types` — 不能内联 `{k: T}` 当类型

❌ `function make(): { id: number; name: string } { ... }`
✅ 先定义 `interface Result { id: number; name: string }`，再 `function make(): Result`

### 2.6 `arkts-limited-throw` — `throw` 只能抛 Error

❌ `throw err` (err 是 unknown)
✅ `throw err instanceof Error ? err : new Error(String(err))`

---

## 3. TestKit / TestRunner 导入规范

### 3.1 大小写是严格的

| ❌ 错的 | ✅ 对的 | 备注 |
|---------|---------|------|
| `import { AbilityDelegatorRegistry } from '@kit.TestKit'` | `import { abilityDelegatorRegistry } from '@kit.TestKit'` | 只导出小写；全局类型叫 `AbilityDelegatorRegistry`，不是值 |
| `AbilityDelegatorRegistry.getAbilityDelegator()` | `abilityDelegatorRegistry.getAbilityDelegator()` | 用实例名访问 |
| `import { Driver, ON } from '@ohos.UiTest'` | `import { Driver, ON } from '@kit.TestKit'` | 新 SDK 统一走 Kit 命名 |
| `import { describe, it } from '@ohos/hypium'` | ✅ 这个不变 | hypium 还是老包名 |

### 3.2 OpenHarmonyTestRunner 标准骨架

```typescript
import { abilityDelegatorRegistry, TestRunner } from '@kit.TestKit'
import { Hypium } from '@ohos/hypium'
import testsuite from '../test/List.test'
import hilog from '@ohos.hilog'

const delegator = abilityDelegatorRegistry.getAbilityDelegator()
const args = abilityDelegatorRegistry.getArguments()

export default class OpenHarmonyTestRunner implements TestRunner {
  onPrepare() { hilog.info(0x0000, 'testTag', 'OpenHarmonyTestRunner onPrepare') }
  onRun() {
    Hypium.hypiumInit(delegator, args)
    testsuite()
    Hypium.hypiumStart(delegator, args)
  }
}
```

### 3.3 MockKit 在 ArkTS 严格模式下打 `@kit.*` 命名空间会 fail（**`arkts-no-ns-as-obj`**）

最常见症状：写 `mocker.mockFunc(http, http.createHttp)` / `mocker.mockFunc(fileIo, fileIo.copyFile)` —— 编译报 `arkts-no-ns-as-obj`，把命名空间当对象传给 mockFunc 不允许。

**❌ 不要降级写法**：遇到该错误**不要**改成 `expect(typeof xxx).assertEqual('function')` / `expect(true).assertTrue()` 之类伪覆盖 —— 这是 C 级占位（参见 `step1-unit-test-agent.md §6.1` 禁止清单），命中即 BLOCKER。

**✅ 正确路径**：看 `references/test-patterns.md §ArkTS 严格模式下的 MockKit 替代方案`，三种合法模式按优先级套用：
1. 构造器注入（最佳：源码已支持依赖注入时直接注入 mock 实现）
2. Wrapper 函数（次选：包一层用户态函数代替直接调 `@kit.*`）
3. 真实 Context + AppStorage seeding（兜底：用 TestKit delegator 拿真实 Context，用 AppStorage 预置数据）

三种都不可行 → Step 1 Agent 必须返回 `BLOCKERS: mockkit_arkts_incompat`，让主线程决策（切 weak / 引入 hamock / 改源码用构造器注入），**禁止 Agent 自己降级到 C 级**。

---

## 4. ohosTest 资源骨架（module 编译前置）

`ohosTest/module.json5` 中 `TestAbility` 的 `icon` / `startWindowIcon` / `startWindowBackground` / `label` / `description` 都会走 `$media:` / `$string:` / `$color:` 引用 → **对应资源文件必须在 `ohosTest/resources/base/` 存在**，否则报 `10903329 Unknown resource name`。

### 最小资源清单

```
entry/src/ohosTest/resources/base/
├── element/
│   ├── color.json         # 至少 {"color":[{"name":"start_window_background","value":"#FFFFFF"}]}
│   └── string.json        # module_test_desc / TestAbility_desc / TestAbility_label / module_test_name
├── media/
│   └── icon.png           # 任意 png；没有就从 main/resources/base/media/ 拷一张 background.png 改名
└── profile/
    └── test_pages.json    # {"src":["TestAbility/pages/Index"]}
```

**经验**：ohosTest 目录经常在 git 清理后被整个删掉（status 标 `D`），重建时**逐项对照 module.json5 的 `$...:xxx` 引用**补资源，不要省略。

---

## 5. startAbility 参数传递

❌ 裸对象会被 `arkts-no-untyped-obj-literals` 拦：
```typescript
await driver.startAbility({
  bundleName: 'xxx',
  parameters: { '__test_mode__': true }           // parameters 类型不是 any
})
```

✅ 用 `@kit.AbilityKit` 的 `Want`（和 UI 测试 mountPage 的 import 保持统一；`@ohos.app.ability.Want` 的老路径在 API 12+ 已被 `@kit.AbilityKit` 吸收）：
```typescript
import { Want } from '@kit.AbilityKit'
const want: Want = {
  bundleName: 'com.example.gallery_arkts_v2',
  abilityName: 'EntryAbility',
  moduleName: 'entry',                       // 跨模块 startAbility 必填，缺失 → startAbility failed
  parameters: { '__test_mode__': true } as Record<string, Object>
}
await delegator.startAbility(want)
```

> **注**：`Driver.startAbility` 在某些 SDK 版本上不存在 / 签名不同，优先用 `delegator.startAbility(want)`。

---

## 6. 生成阶段自检清单（Step 1/Step 3 Agent 必走）

在写完任何测试文件之前，用这份清单快速过一遍：

- [ ] 每个对象字面量都有 interface / class 支撑（搜 `= {` 看看有无裸字面量）
- [ ] 没有 `dumpLayout` 字样（全文 grep）
- [ ] 没有 `any` / `unknown` 关键字（全文 grep）
- [ ] 没有 `namespace.method` 直接传给 MockKit（检查 `mocker.mockFunc(` 后第一个参数是否是 class 实例）
- [ ] `@kit.TestKit` 的导入用小写 `abilityDelegatorRegistry`
- [ ] `startAbility` 的 Want 对象有显式 `Want` 类型
- [ ] ohosTest 资源骨架齐全（第一次生成时）

---

## 7. 修复失败的降级策略

若生成的某个测试文件怎么修都编不过（通常是 MockKit 对复杂依赖链的限制）：

1. **不要删 `it()`**，不要降语义 —— 把这个 `it()` 挪到一个 `// @ts-expect-error` 或直接 `expect(false).assertTrue()` 是更差的选择
2. 把整份测试文件从 `List.test.ets` 的 import/调用里**注释掉**（只改 List，不改测试文件本身）
3. 在报告里列入 `skipped-compile`，**不计入分母** —— 保留"这条 AC 有测试代码但暂跑不通"的轨迹
4. 避免让编译失败阻塞其他 10 个 Feature 的结果收集

---

## 8. 相关文档

- `test-patterns.md` — 测试写法完整模板
- `spec-parsing-guide.md` — Spec → AC 分类决策
- `ac-index-format.md` — AC 索引表头/字段
- `report-format.md` — 报告模板
