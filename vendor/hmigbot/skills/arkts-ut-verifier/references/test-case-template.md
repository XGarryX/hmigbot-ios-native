# 测试用例模版（UT Code）

第二步「测试用例生成」的代码模版。输入是第一步的设计文档（`spec/verify/ut/ut-design/F*.md`），
输出是 arkxtest（`@ohos/hypium`）单元测试代码，写到
`entry/src/ohosTest/ets/test/ut/F{编号}_{英文名}.test.ets` 并注册到 `List.test.ets`。

**一条 `testability=ut` 的逻辑设计 = 一个 `it()`**，名称沿用用例 ID。`no_entry/needs_review` 保留契约并逐 ID 写入生成记录，`ui_only` 另列；不能遗漏可执行行或用占位测试填数。完整记录格式见生成 agent 的“逐用例生成记录”。

## 导航

- §1 文件骨架；§2 真实执行与必要隔离；§3 断言有效性
- §4 ArkTS 编译要点；§5 生命周期；§6 匹配、异步与版本

> **API 拿不准时**：写桩 / 断言若不确定某个 hypium API 的用法或语义，查 `references/api/hypium.md`（基于官方资料整理的版本化 API 参考）。

---

## 1. 文件骨架

```typescript
import { describe, it, expect } from '@ohos/hypium'
// 需要隔离依赖时再按需引入：MockKit, when, ArgumentMatchers
// import { describe, it, expect, MockKit, when, ArgumentMatchers } from '@ohos/hypium'
import { Xxx } from '../../../../main/ets/models/Xxx'   // 复用源码类型，对象字面量需有类型上下文

export default function F00X_FeatureName() {
  describe('F00X_FeatureName', () => {
    it('F00X_AC01_description', 0, () => {
      // 1) 构造输入  2) 调被测方法  3) expect 断言
    })
  })
}
```

注册到 `entry/src/ohosTest/ets/test/List.test.ets`：

```typescript
import F00X_FeatureName from './ut/F00X_FeatureName.test'
export default function testsuite() {
  F00X_FeatureName()
  // …其它 Feature
}
```

> 命名：describe 与文件同名 `F00X_FeatureName`；it 名 = 设计表的用例ID `F{编号}_AC{序号}_{行为}`。

---

## 2. 依赖处理（先判必要性，再选写法）

先读 [最小必要 mock 策略](mock-policy.md)，以设计表的真实链路和替换理由为准。业务源码中的类名、接口和方法以下均为示例，应替换为项目已有定义；不要为了套模板新增业务接口或公开私有成员。

### 2.1 真实逻辑与本地协作

```typescript
it('F006_AC01_filter_by_filename', 0, () => {
  const a = new MediaItem(); a.filename = 'a.jpg'
  const b = new MediaItem(); b.filename = 'b.png'
  const result = SearchService.filterMedia([a, b], 'a')
  expect(result.length).assertEqual(1)
  expect(result[0].filename).assertEqual('a.jpg')
})
```

真实 model、解析器、排序器与 service 可以一起参与本用例。它们位于不同文件不代表必须隔离。

### 2.2 已有构造器注入（确需替换外部边界时）

被测类已经接收依赖接口时，测试传最小 fake。下面假设项目已有 `HttpClient/HttpOptions/HttpResponse` 类型和 `TranslateService` 的注入接口：

```typescript
class FakeHttpClient implements HttpClient {
  public lastUrl: string = ''
  public calls: number = 0
  async request(url: string, opts: HttpOptions): Promise<HttpResponse> {
    this.lastUrl = url
    this.calls += 1
    // URL 和返回体必须按项目真实接口契约填写，意外调用应明确报错。
    if (url !== 'https://example.test/translate?text=hello&lang=zh') {
      throw new Error('Unexpected request: ' + url)
    }
    const response: HttpResponse = { responseCode: 200, result: '{"data":"你好"}' }
    return response
  }
}

it('F004_AC02_translate_calls_api', 0, async () => {
  const fake = new FakeHttpClient()
  const svc = new TranslateService(fake)
  const result = await svc.translate('hello', 'zh')
  expect(fake.calls).assertEqual(1)
  expect(fake.lastUrl).assertEqual('https://example.test/translate?text=hello&lang=zh')
  expect(result).assertEqual('你好')
})
```

此用例证明请求参数和真实 service 的响应处理，不证明远端接口可用。真实持久化契约不能换成 fakeDb 后沿用“保存成功”的结论。

### 2.3 已有实例上的局部 MockKit

源码已有可传入/可取得的包装对象时，只替换必要调用。先构造确定类型的响应，再创建桩；异步行为优先按调用产生 Promise：

```typescript
const mocker: MockKit = new MockKit()
const shim: HttpShim = existingShim
try {
  const mockReq: Function = mocker.mockFunc(shim, shim.request)
  when(mockReq)(expectedUrl, expectedOptions)
    .afterAction(async (url: string, opts: HttpOptions): Promise<HttpResponse> => {
      const response: HttpResponse = { responseCode: 200, result: '{"data":"你好"}' }
      return response
    })
  // 调真实被测 service；它必须使用同一个 shim，再断言其输出/状态。
} finally {
  mocker.clear(shim)
}
```

`existingShim/expectedUrl/expectedOptions` 来自本用例实际 fixture。未匹配桩可能执行原方法，不能用宽泛 matcher 假定已覆盖所有参数，尤其 null/undefined、可选参数和零参数。需要完全阻止外部调用时优先 §2.2 的严格 fake。

源码直接使用命名空间且没有可用注入点时，按 `import-mock.md` 评估模块替换；生成 agent 不自动给业务代码增加 wrapper。

### 2.4 真实 Context 与存储 fixture

Preferences/RDB 的接口要求有效 `Context`，没有“所有场景必须使用 UIAbilityContext”的通用限制。先使用真实 delegator Context；需要特定 Ability/模块上下文时按 API 和项目初始化路径取得。出现 401 时检查上下文来源、生命周期、模块与路径，不能直接认定 ApplicationContext 无效。

可复用测试侧 holder（由执行阶段单点创建，生产代码不读取它）：

```typescript
// entry/src/ohosTest/ets/test/TestContextHolder.ets
import { common } from '@kit.AbilityKit'
import { abilityDelegatorRegistry } from '@kit.TestKit'

export class TestContextHolder {
  static abilityContext: common.UIAbilityContext | undefined = undefined

  static async resolve(requireUIAbility: boolean = false, timeoutMs: number = 5000): Promise<common.Context> {
    if (!requireUIAbility) {
      return abilityDelegatorRegistry.getAbilityDelegator().getAppContext()
    }
    const deadline: number = Date.now() + timeoutMs
    while (Date.now() < deadline) {
      const ctx = TestContextHolder.abilityContext
      if (ctx !== undefined) return ctx
      await new Promise<void>((resolve) => setTimeout(resolve, 50))
    }
    throw new Error('Required test UIAbilityContext was not initialized')
  }
}
```

真实存储测试先创建测试独占的文件/库名，并通过**被测 repository/service 的真实保存和读取方法**完成断言。fixture 可用官方 Preferences API 准备、刷新与清理存储，例如：

```typescript
import { preferences } from '@kit.ArkData'

const ctx = await TestContextHolder.resolve()
const options: preferences.Options = { name: testStoreName }
try {
  const store = await preferences.getPreferences(ctx, options)
  // 将此真实 store/名称交给项目已有注入点；调用被测实现保存测试数据。
  await store.flush()
  await preferences.removePreferencesFromCache(ctx, testStoreName)
  const reopened = await preferences.getPreferences(ctx, options)
  // 通过真实读取路径/重开的 store 断言保存后的关键字段；不能只断调用次数。
} finally {
  await preferences.deletePreferences(ctx, testStoreName)
}
```

以上是 fixture 片段，必须补入真实焦点调用和契约断言后才能成为用例。清缓存重开只证明该重开路径；Spec 要求进程重启时，安排实际重启与复核，不能用上述片段冒充已验证重启。

RDB/文件遵循同样原则：独占资源、完成事务/flush、关闭 ResultSet/句柄、读回字段、最终清理。只初始化实际调用链需要的后端。

### 2.5 私有成员与静态依赖

- 本地公共方法：确需隔离时 `mockFunc(instance, instance.method)`。
- 本地静态方法：官方从 Hypium 1.0.16 起支持 `mockFunc(ClassName, ClassName.method)`；仍要确认生产调用路径在项目编译模式下实际命中。
- 实例私有方法：1.0.25 起可 `mockPrivateFunc(instance, 'methodName')`。
- 实例属性（含私有属性）：1.0.25 起可 `mockProperty(instance, 'propertyName', value)`，适用于必要的依赖替换；不能预写待验证状态刷绿。
- 私有静态字段、未导出模块函数与实例私有成员不能混为一谈。优先真实执行和已有注入点，再按版本验证局部替换或 import mock。
- 私有方法如果属于焦点算法内部步骤，保持真实，通过公共入口测试。框架支持不等于应该替换。
- 不默认把 `private static repo` 改成 public，也不通过修改 prototype 或 globalThis 找命名空间。确实需要生产接缝时写明原因，交主线程安排最小改造。

被替换对象必须恢复，见 §5。某个编译环境下静态替换不生效，应记录版本、调用路径和最小复现，不能据此断言所有跨模块静态调用均不支持。

### 2.6 断言写法与"是否已实装"无关（不写"预期 RED"的弱版本）

设计不预测红绿，生成也**不分**"预期绿 / 预期红"两种写法——**每条可执行用例都写满 Android 已核实行为或明确批准平台差异的强断言**，调用设计核实的
真实生产入口 + 断言有来源依据的**具体值、状态变化和必要副作用**。Spec 管范围与 AC，不能仅凭概述编预期。源码若是占位，它**自然**会红；实装正确后转绿。这个红绿由第三步
实跑测量，**不是你预先决定、更不是你为了"让它现在红"而写个最小断言**：

```typescript
it('F014_AC06_enter_pip_mode', 0, async () => {
  // 示例前提：Android 已核验进 PiP 返回 active session；填写实际 oracle path:line，按真实契约补齐必要副作用。
  const result = await VideoPlaybackController.getInstance().enterPip()
  expect(result).not().assertNull()
  if (result === null || result === undefined) {
    expect().assertFail()
    return
  }
  expect(result.isActive).assertTrue()        // 验证已核实的具体状态，不能停在非空
})
```

> **反例（禁止）**：因为"看起来没实装"就只写 `expect(result).not().assertNull()` 当作"预期红"，把 `isActive`
> 等真实契约省掉——这等于把强断言降级成"够检测占位"的最小断言，实装一落地它就变成假绿（非空但内容全错也过）。
> 无论你以为它实没实装，断言强度**必须一致**。
> fixer 更新或新增测试也使用同一标准，见 [fixer 测试更新策略](fixer-test-policy.md)。正确原断言优先保留，只有 Android 证据、明确批准差异或测试本身错误支持时才调整预期；不能照着修改后的鸿蒙输出改断言。缺少有效预期时标 `needs_review`、未验证，不用简单测试凑绿。

---

## 3. 禁止占位断言（命中即重写，不要提交）

下列写法不验证已核实的业务行为、只为让 PASS 数虚高，**一律禁止**——包括「未实现」的 AC（有证据时按 §2.6 写完整真断言，缺证据时记录待复核）：

```typescript
expect(typeof svc.method).assertEqual('function')   // ❌ 方法存在性：stub 也过
expect(Reflect.has(svc, 'method')).assertTrue()     // ❌ 属性存在性：同上
expect(Object.keys(obj).indexOf('k') >= 0).assertTrue()  // ❌ 键存在性
expect(fn.toString().indexOf('targetApi') >= 0).assertTrue()  // ❌ 检查函数文本不能证明目标行为
expect(true).assertTrue()                           // ❌ 恒等占位
expect(4).assertEqual(4)                            // ❌ 常量自比
const x = obj.value; expect(x).assertEqual(x)       // ❌ 自己比自己
Reflect.set(globalThis, '__hit__', true)            // ❌ 哨兵全局量（源码里也埋 __hit__ 配合）
try { svc.m(null) } catch (e) {}; expect(true).assertTrue()  // ❌ no-throw 兜底
// ❌ 自 mock 自断：mock 掉被测方法本身、再断言它的返回（套套逻辑）
```

**断言有效性闸门（sabotage check）**：每条用例选择其应识别的具体业务错误（如字段映射颠倒、排序反向、丢失状态更新或未发生必要副作用），检查对应断言能否失败；相关错误发生仍通过即无效，必须改写。禁止为通过而删除有效用例/边界、缩减断言、mock 焦点逻辑、吞异常或无依据放宽精度/超时；不要求为了审查永久修改生产代码。

#### 强制静态门（第二步生成自检 + 第三步计 GREEN 前各跑一遍）

除上面的禁止占位外，再加 5 条**弱形状**。**复核确认命中无效断言时，判该用例不合格、重写且不计入 GREEN**：

```
1. 看**整个 it() 体**：对焦点单元零调用 / 不触达任何焦点状态（no focal call）—— 是看整段 it 体，非断言那一行
2. assertInstanceOf('Function') / typeof === / Reflect.has        —— 存在性，桩也过
3. 解析/映射契约只断 expect(result.length).assertEqual(n)        —— 同长度下字段全错也过
4. 直接断被 mock 的焦点返回或预写的焦点状态，未经过真实行为       —— 自设自断
5. expect(a).assertEqual(a) / 常量自比 / undefined === undefined  —— 恒等，源码改坏也不红
```

可机检的 grep 信号（供自检脚本）：`assertInstanceOf\('Function'\)`、`typeof .*===`、`Reflect\.has`、
以 `expect\([^\n]*\.length\)` 查找仅断条数的候选、以及"`it` 体内不含任何对主源码符号的调用"。
**第二步**：复核确认无效 → 当场重写成真契约断言，不得交给下游。**第三步**：对实跑 GREEN 的用例复核，确认无效者从
真 GREEN 中剔除、按 RED 写入 `round-N/ut/`（kind=RED，§3 实际写"假绿：<命中的弱形状>"），避免实现率虚高。

**合法豁免（不算弱形状，别误杀）**：

- **反向存在性断言**：`expect(Reflect.get(x,'m')).assertUndefined()`（断某方法 / 字段**不该存在**，如回归守卫）——断"不存在"是有效 oracle，不属第 2 条。
- **条数契约**：当焦点就是计数/基数判断时，条数可以是完整契约；解析/映射需补字段断言。
- **真实转发**：依赖 fixture 经真实焦点处理/转发后返回同值可以合法；须验证契约要求的参数、错误路径或状态，禁止直接断 mock 自身。
- **常量 / 枚举表**：被测对象本身就是常量 / 映射表（`expect(Config.MAX).assertEqual(100)`），读常量即"调用焦点"，不属第 1 条。
- **间接副作用 IO**：写文件再读回、写 pref 再 `getXxx()` 比对——焦点调用在 it 体别处，断言行没有 `focal(...)` 字样不算第 1 条。

机检边界：grep 仅定位候选，所有命中都结合 it 体、焦点调用及契约复核；不能因方法名、.length 或预期值与 fixture 相同就判假绿。

若某 AC 在 ArkTS 严格模式下，真实执行及所有必要的边界隔离方式均不可行（见
`test-design-template.md`「隔离方式选型」），无法写真断言 → 在生成记录中标
`no_entry/needs_review`，附实际入口核查、环境与版本证据，继续其它可执行行。主线程复核分类差异；不能降级成占位或直接当作 PASS。

---

## 4. ArkTS 严格模式编译要点（生成时就避开）

| 规则 | ❌ | ✅ |
|---|---|---|
| `arkts-no-untyped-obj-literals` | `const m = { id: 1 }` 裸对象 | 复用源码类 `const m = new Medium(); m.id = 1` 或定义 `interface` |
| `arkts-no-any-unknown` | `let x` / `: any` / `as unknown` | 所有变量/参数/返回值显式类型 |
| `arkts-no-ns-as-obj` | `mocker.mockFunc(http, http.request)` 传命名空间 | 复用已有实例或按必要性配置 import mock（§2.3） |
| `arkts-no-prototype-assignment` / `arkts-limited-stdlib` | `mockFunc(Repo.prototype, …)`、`Object/Reflect.getPrototypeOf` | 真实执行、已有实例/注入点或受版本支持的成员替换（§2.5） |
| TestKit 大小写 | `AbilityDelegatorRegistry.xxx` | 小写实例 `abilityDelegatorRegistry.getAbilityDelegator()` |
| import 来源 | `from '@ohos.UiTest'` | `from '@kit.TestKit'`；hypium 仍是 `'@ohos/hypium'` |

生成前自查：对象字面量有明确的接口/类上下文类型，避免 any/unknown 与命名空间作为对象；不能以出现 `= {` 就拒绝合法的有类型对象。

---

## 5. Mock 生命周期与真实资源清理

`clear(obj)` 恢复该对象被替换的方法/属性；`ignoreMock(obj, name)` 可恢复单个成员；`clearAll()` 不恢复函数，不能单独用于 teardown。当前 master 的 clearAll 还会删除 mocker 自身字段；恢复对象后直接丢弃 mocker，不复用清空实例。

```typescript
let mocker: MockKit = new MockKit()
let dependency: HttpShim | undefined = undefined

beforeEach(() => {
  mocker = new MockKit()
  dependency = createExistingTestDependency()
})

afterEach(() => {
  if (dependency !== undefined) mocker.clear(dependency)
  dependency = undefined
})
```

`createExistingTestDependency` 代表项目现有的测试 fixture 工厂；不在此创建新的业务接缝。涉及多个对象时逐一恢复；同名方法需要独立 mocker/capture。局部桩也可用 §2.3 的 finally 写法。

真实 Context 只在需要时取得；后端初始化、独占资源创建、缓存和 AppStorage 场景状态的清理，按实际调用链安排并 await 完成。初始化失败应暴露为测试/环境错误；不要在生产源码添加测试 Context 回退或吞掉初始化异常。

## 6. 匹配、异步与版本检查

- 先检查锁文件、安装包声明与 SDK 版本。1.0.28 的 `verify` 参数 matcher、`assertMatchObj`、`it(timeout, tag)` 不能无条件生成到旧版工程。
- `verify` 的当前 master 实现支持结构比较，并非统一将对象转成字符串；旧版行为不确定时核对安装包，用精确参数或类型明确的 capture。
- `mockFunc` 未匹配桩时可能执行原方法；`ArgumentMatchers.any` 不含 null/undefined。真正需要阻止 IO 时，确保参数覆盖或使用严格 fake。
- `afterReturn` 返回给定值。需要按调用创建对象、Promise 或捕获参数时使用 `afterAction`/fake；Promise 拒绝与同步抛异常分别设计。
- `assertPromiseIsRejected*`、`assertPromiseIsResolved*` 返回 Promise，必须 await。callback 接口优先封装成 Promise 后 await；若使用 done，成功、失败与超时路径都要正确结束，不能吞断言异常。
- `describe` 回调保持同步。测试准备放在 hook 或 it 中；一次用例不混用 async 返回 Promise 与 done 两种完成协议。
- `assertMatchObj` 只做部分匹配；契约要求完整对象/集合时使用 `assertDeepEquals` 或逐字段/全集断言。
- 直接导入不等于自动全局变量；不要从 globalThis 猜测系统命名空间。模块替换的生命周期见 `import-mock.md`。

来源与版本条件见 `api/hypium.md` 和 `mock-policy.md`；项目经验需注明实际版本/编译模式，不升级为普遍限制。
