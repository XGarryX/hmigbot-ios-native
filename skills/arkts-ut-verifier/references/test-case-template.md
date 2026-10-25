# 测试用例模版（UT Code）

第二步「测试用例生成」的代码模版。输入是第一步的设计文档（`spec/test/ut-design/F*.md`），
输出是 arkxtest（`@ohos/hypium`）单元测试代码，写到
`entry/src/ohosTest/ets/test/spec/F{编号}_{英文名}.test.ets` 并注册到 `List.test.ets`。

**一行设计 = 一个 `it()`**。设计表里有几行，文件里就有几个 `it()`，命名沿用设计的「用例ID」。

> **API 拿不准时**：写桩 / 断言若不确定某个 hypium API 的用法或语义，查 `references/api/hypium.md`（@ohos/hypium 官方单测 API 原文）。

---

## 1. 文件骨架

```typescript
import { describe, it, expect } from '@ohos/hypium'
// 需要隔离依赖时再按需引入：MockKit, when, ArgumentMatchers
// import { describe, it, expect, MockKit, when, ArgumentMatchers } from '@ohos/hypium'
import { Xxx } from '../../../../main/ets/models/Xxx'   // 复用源码类型，不要裸对象字面量

export default function F00X_FeatureName() {
  describe('F00X_FeatureName', () => {
    it('F00X_AC01_description', 0, () => {
      // 1) 构造输入  2) 调被测方法  3) expect 断言
    })
  })
}
```

注册到 `entry/src/ohosTest/ets/test/spec/../List.test.ets`：

```typescript
import F00X_FeatureName from './spec/F00X_FeatureName.test'
export default function testsuite() {
  F00X_FeatureName()
  // …其它 Feature
}
```

> 命名：describe 与文件同名 `F00X_FeatureName`；it 名 = 设计表的用例ID `F{编号}_AC{序号}_{行为}`。

---

## 2. 隔离写法（按设计表「依赖与隔离」列挑）

### 2.1 纯函数

```typescript
it('F006_AC01_filter_by_filename', 0, () => {
  const result = SearchService.filterMedia(
    [{ filename: 'a.jpg' }, { filename: 'b.png' }] as MediaItem[], 'a')
  expect(result.length).assertEqual(1)
  expect(result[0].filename).assertEqual('a.jpg')
})
```

### 2.2 构造器注入（首选隔离方式）

源码侧让被测类通过构造器接收依赖接口，测试传 fake 实现并断言真实调用参数：

```typescript
class FakeHttpClient implements HttpClient {
  public lastUrl: string = ''
  async request(url: string, opts: HttpOptions): Promise<HttpResponse> {
    this.lastUrl = url
    return { responseCode: 200, result: '{"data":"你好"}' }
  }
}

it('F004_AC02_translate_calls_api', 0, async () => {
  const fake = new FakeHttpClient()
  const svc = new TranslateService(fake)       // 注入 fake
  const result = await svc.translate('hello', 'zh')
  expect(fake.lastUrl.includes('translate.googleapis.com')).assertTrue()  // 真断言：调用参数
  expect(result).assertEqual('你好')                                       // 真断言：返回值
})
```

### 2.3 Wrapper 函数（源码无法改构造器时）

源码固化用 `@kit.*`（如 `http` / `fileIo`），ArkTS 严格模式不允许 mock 命名空间 → 包一层用户态
class shim，对实例 mock：

```typescript
class HttpShim {
  async request(url: string, opts: HttpOptions): Promise<HttpResponse> {
    return http.createHttp().request(url, opts)
  }
}
const mocker = new MockKit()
const shim = new HttpShim()
const mockReq = mocker.mockFunc(shim, shim.request)
when(mockReq)(ArgumentMatchers.any, ArgumentMatchers.any)
  .afterReturn(Promise.resolve({ responseCode: 200, result: '{}' }))
// …让被测代码调 shim.request；teardown 在 afterEach 用 mocker.clear(shim)（见 §5，禁止 clearAll）
```

### 2.4 真实 Context + AppStorage（兜底）

依赖 RDB / Preferences / Context 且无注入点时，必须拿**真实 `UIAbilityContext`**——由第三步的 TestAbility
在 `onCreate` 注入到 `globalThis['__app_test_context__']`。**直接用 `delegator.getAppContext()` 会爆**：
它返回的是 `ApplicationContext`，`@ohos.data.preferences` / RDB 会判 `Parameter error. The context is invalid.`（401）→ `beforeAll` 抛错 → 整套 `it()` 被框架标 ERROR（不是 FAILURE）。

先放一个小 helper（测试目录下，被本节用例和 §5 的 `beforeAll` 共同复用）：

```typescript
// entry/src/ohosTest/ets/test/TestContextHolder.ets
import { common } from '@kit.AbilityKit'
import { abilityDelegatorRegistry } from '@kit.TestKit'

export class TestContextHolder {
  static async resolve(timeoutMs: number = 5000): Promise<common.Context> {
    const deadline: number = Date.now() + timeoutMs
    while (Date.now() < deadline) {
      const ctx = Reflect.get(globalThis, '__app_test_context__') as common.UIAbilityContext | undefined
      if (ctx) return ctx
      await new Promise<void>((r) => setTimeout(r, 50))
    }
    // 兜底：TestAbility 还没起来 → 回落到应用级 Context（preferences/RDB 会拒，让用例尽早 ERROR 暴露问题）
    return abilityDelegatorRegistry.getAbilityDelegator().getAppContext()
  }
}
```

用例里：

```typescript
import { TestContextHolder } from '../TestContextHolder'

it('F021_AC01_incognito_blocks_history', 0, async () => {
  const ctx = await TestContextHolder.resolve()
  await ConfigManager.getInstance().init(ctx)
  ConfigManager.getInstance().incognito = true
  const before = await getHistoryCount(ctx)
  BrowserContainer.getInstance().add({ url: 'https://a.com', title: 'T' })
  const after = await getHistoryCount(ctx)
  expect(after).assertEqual(before)            // 真行为：无痕模式不写历史
})
```

> 真实 Context 用例必须连真机/模拟器才能跑（第三步处理）。源码 `getInstance()` 在 stub Context
> 不可用时回落读 `globalThis['__app_test_context__']`，与本 Holder 同源。第三步的
> `OpenHarmonyTestRunner.onRun` 已 await 拉起 TestAbility 并轮询此缓存就绪，再启动 `hypiumTest`。

### 2.5 静态依赖单例：暴露实例 + 实例方法 mock（service 持有 `private static repo`/`api` 时）

很多 service 把持久层/接口固化成 `private static repo = new XxxRepository()`。ArkTS 严格模式**禁用
`XxxRepository.prototype` 打桩**（`arkts-no-prototype-assignment`），`Object/Reflect.getPrototypeOf`
也被 `arkts-limited-stdlib` 禁；而 `private static` 又拿不到可达实例 → 没法 mock。**正确做法**：把该
静态字段从 `private static repo` 改成可访问 `static repo`（纯可见性变更、零逻辑改动），再对**实例方法**打桩：

```typescript
// 业务侧一次性改动：XxxService 里 `private static repo` → `static repo`
when(mocker.mockFunc(XxxService.repo, XxxService.repo.findBySiteId))(ArgumentMatchers.any)
  .afterReturn(Promise.resolve([row]))     // 查询类：喂 canned 数据，断 service 的过滤/派生
when(mocker.mockFunc(XxxService.repo, XxxService.repo.upsertByRemoteId))(ArgumentMatchers.any)
  .afterReturn(Promise.resolve())          // 写入类：no-op，让 service 逻辑跑完
const ok: boolean = await XxxService.updatePost(p, fields)
expect(p.title).assertEqual('T')           // 断的是 service 的字段映射，不是断 repo
```

`mockFunc(实例, 实例.方法)` 是官方支持的实例 mock；不出现 `.prototype` 字样即合规。afterEach 要
`mocker.clear(XxxService.repo)` 还原（见 §5）。若 service 路径还会真打 RDB，beforeAll 需 `RdbHelper.init(ctx)`（§5）。

### 2.6 未实装 AC 的「预期 RED」写法

设计表标「未实现→RED」的用例，**直接调 spec 期望的方法 + 断言 spec 期望的结果**，让它因为
stub 返回 null/false 而 RED；实装补完后自动转 GREEN：

```typescript
it('F014_AC06_enter_pip_mode', 0, async () => {
  // Spec 要求进 PiP 返回 session；当前 stub return null → 预期 RED
  const result = await VideoPlaybackController.getInstance().enterPip()
  expect(result).assertNotNull()
  expect(result.isActive).assertTrue()
})
```

---

## 3. 禁止占位断言（命中即重写，不要提交）

下列写法不触达任何 spec 行为、只为让 PASS 数虚高，**一律禁止**——包括「未实现」的 AC（应按 §2.6 写真断言期望 RED，而不是占位）：

```typescript
expect(typeof svc.method).assertEqual('function')   // ❌ 方法存在性：stub 也过
expect(true).assertTrue()                           // ❌ 恒等占位
expect(4).assertEqual(4)                            // ❌ 常量自比
const x = obj.value; expect(x).assertEqual(x)       // ❌ 自己比自己
try { svc.m(null) } catch (e) {}; expect(true).assertTrue()  // ❌ no-throw 兜底
```

自审一句话：**「如果实装只是个空 stub，这个断言还会过吗？」会过 = 占位，必须改写成真行为断言。**

若某 AC 在 ArkTS 严格模式下三种隔离方式都用不了、无法写真断言 → 在返回里标
`BLOCKERS: <用例ID> 无法隔离依赖`，交主线程决策，**不要**自己降级成占位。

---

## 4. ArkTS 严格模式编译要点（生成时就避开）

| 规则 | ❌ | ✅ |
|---|---|---|
| `arkts-no-untyped-obj-literals` | `const m = { id: 1 }` 裸对象 | 复用源码类 `const m = new Medium(); m.id = 1` 或定义 `interface` |
| `arkts-no-any-unknown` | `let x` / `: any` / `as unknown` | 所有变量/参数/返回值显式类型 |
| `arkts-no-ns-as-obj` | `mocker.mockFunc(http, http.request)` 传命名空间 | 包 class shim 后 mock 实例（§2.3） |
| `arkts-no-prototype-assignment` / `arkts-limited-stdlib` | `mockFunc(Repo.prototype, …)`、`Object/Reflect.getPrototypeOf` | 暴露依赖为 `static` 后 `mockFunc(Service.repo, Service.repo.m)`（§2.5） |
| TestKit 大小写 | `AbilityDelegatorRegistry.xxx` | 小写实例 `abilityDelegatorRegistry.getAbilityDelegator()` |
| import 来源 | `from '@ohos.UiTest'` | `from '@kit.TestKit'`；hypium 仍是 `'@ohos/hypium'` |

生成前自查：全文 grep 无裸 `= {` 对象字面量、无 `any`/`unknown`、无 `mockFunc(<namespace>,`、无 `.prototype`。

---

## 5. Mock 生命周期 / teardown（踩坑总结，必须遵守）

**禁止 `afterEach(() => mocker.clearAll())`。** 官方语义（arkxtest README）：`clear(obj)` 会**还原**
被 mock 的函数（恢复原功能）；`clearAll()` 只做"数据和内存清理"、**不还原**。实测 `clearAll()` 还会
delete 掉 mocker 自身实例字段且不重建 → **第 2 个及以后的 `mockFunc()` 直接崩**
（`Cannot convert a illegal value to a String`）；且不还原会让 `verify()`（按方法名匹配）拿到残留匿名 mock 名而误判。

统一 teardown 写法：

```typescript
let mocker: MockKit = new MockKit()          // 用 let，不要 const
afterEach(() => {
  mocker.clear(SomeApi)                        // 每个被 mock 的「静态类」
  mocker.clear(SomeService.repo)               // 每个被 mock 的「实例」
  mocker = new MockKit()                       // 重建，保证用例间隔离
})
```

**beforeAll 要把焦点路径用到的后端都初始化齐**：只 `await PrefsHelper.init(ctx)` 不够——若 service 会
读写 RDB（如 `repo.upsert`/`findBy*` 未被 mock 而走真实库），必须同时 `await RdbHelper.init(ctx)`，
否则真实 repo 调用抛 "not initialized" 被 service 的 try/catch 吞掉 → 用例**假阴性**（看起来是实现缺失，其实是测试没初始化后端）。

```typescript
beforeAll(async () => {
  const ctx: common.Context = await TestContextHolder.resolve()
  await PrefsHelper.init(ctx)
  await RdbHelper.init(ctx)                     // 焦点路径碰 RDB 就必须加
})
```

`ctx` 要是真实 **UIAbilityContext**（由 TestAbility 缓存）；`delegator.getAppContext()` 返回的应用级
Context 可能被 `@ohos.data.preferences`/RDB 判 `invalid`（401）。

`verify(methodName, args)` 按**方法名字符串**匹配 → 被 mock 的方法在打桩时必须仍是"原方法"（已被
`clear` 还原过），`getName()` 才解析得对；这也是必须用 `clear`（而非 `clearAll`，更非不还原）的原因。
