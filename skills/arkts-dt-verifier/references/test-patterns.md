# 测试模式索引

> ⚠️ 生成测试文件前必读 `compile-pitfalls.md` —— ArkTS 严格模式 + arkXtest API 的坑不提前规避会导致满屏编译红。

本文件是索引 + 选型决策树。具体代码骨架已拆到 `templates/` 下：

- **UI 测试骨架 + mountPage / findInScroll helper + beforeEach/findInScroll 触发判据** → `templates/ui-test-skeleton.md`
- **direct-mount 桥（EntryAbility + 根页）** → `templates/direct-mount-bridge.md`
- **TestDataSetup.ets + Service 旁路** → `templates/test-data-setup.md`
- **.id() 注入规范 + 示例** → `templates/id-injection.md`

---

## 单元测试 — 怎么选

```
方法是否依赖外部服务（DB / fileIo / photoAccessHelper / 网络）？
├─ 否 → 纯函数测试：构造对象 → 调方法 → expect 值
│       适用：Model 默认值、布尔 getter、格式化、边界值、排序不变性
│
└─ 是 → MockKit 测试：
        const mocker = new MockKit()
        const mockXxx = mocker.mockFunc(dep, dep.method)
        when(mockXxx)(ArgumentMatchers.any).afterReturn(...)
        ... execute ...
        mocker.verify('method', [...]).once()
        mocker.clearAll()

功能 Spec 定义了但源码未实装？
└─ TODO 占位测试（预期 RED）：正常写断言 + 注释说明「当前 RED」
   测试 RED 就是"待实现"的 TDD 信号，不要跳过
```

### 单元测试文件骨架（参考）

位置：`entry/src/ohosTest/ets/test/spec/F00X_FeatureName.test.ets`；函数/describe 同名 `F00X_FeatureName`；it 名：`F{编号}_AC{序号}_{行为}`。

```typescript
import { describe, it, expect, MockKit, when, ArgumentMatchers } from '@ohos/hypium'

export default function F00X_FeatureName() {
  describe('F00X_FeatureName', () => {
    it('F00X_AC01_description', 0, () => {
      // expect(...).assert...
    })
  })
}
```

---

## UI 测试 — 怎么选

```
目标页能作为 NavDestination 挂载？
├─ 能 → direct-mount：mountPage(driver, '<PageName>', params?)
│       beforeEach 末尾 landmark: ON.id('<page_short>_root')
│       （见 templates/ui-test-skeleton.md；禁用 beforeAll：delegator 未 ready 时 Driver.create 返回 null）
│
└─ 否（FormExtensionAbility / 必须真实 ContentResolver URI）
   → beforeEach throw new Error('Pxxxx setup: <page> unreachable from test context')
     按 Step 3 R2 规则逐 spec 交互点位展开 SKIP 占位，**不得**整页退化为 1 条

describe 里是否含 NAV_* / _opens_dialog / _cab_* / _flips_checked / menu_* ？
├─ 是 → 必须加 beforeEach 重新 mountPage
└─ 否（只读 COMP 断言） → 可省 beforeEach

页面根是否 Scroll/List 且子项超首屏（典型 SettingsPage）？
├─ 是 → 非顶层 landmark 的 ON.id 查找统一走 findInScroll(driver, scrollId, id)
│       注意：driver.scrollSearch 不存在，只有 Component.scrollSearch
└─ 否 → 直接 driver.findComponent(ON.id(...))

Selector 字面量来源（严格优先级）：
  1. ON.id('<page_short>_<purpose>_<kind>')  ← manifest 默认
  2. ON.text('<string.json value>')          ← LazyForEach 动态项 / bindMenu 弹出项；value 来自 manifest "字符串映射"
  3. ON.type('Toggle' / 'Swiper' / ...)      ← spec `## 转换决策` 真实类型兜底
  4. 禁用：凭空翻译的中英文字面量
```

### AC 类型 → 断言形态速查

| AC 类型 | 断言 |
|--------|------|
| SMOKE | landmark `assertComponentExist(ON.id('<page_short>_root'))` |
| COMP | 该页顶层组件 `assertComponentExist(ON.id(...)/.type(...))` |
| NAV | 点按钮 → 落地页 landmark `ON.id('<target_short>_root')` |
| INTERACT_toggle | `isChecked()` 前后取反 |
| INTERACT_opens_dialog | 点击后 `ON.type('Dialog')` 存在 |
| INTERACT_menu | 点击后 `ON.text(manifest 字符串)` 存在 |
| INTERACT_swiper | `getPageSig()` 前后不等 |
| INTERACT_search | `getText()` 等于输入值 |
| INTERACT_scroll_to_bottom | `driver.swipe` + 最后一节的 row id 存在 |

---

## 测试数据构造技巧

### 时间边界（回收站自动清理）

```typescript
const thirtyDaysAgo   = Date.now() / 1000 - 30 * 86400
const thirtyOneDaysAgo = Date.now() / 1000 - 31 * 86400
```

### 最小化数据集（≤10 条覆盖所有边界）

```typescript
const TEST_MEDIA = [
  { path: 'DCIM/img1.jpg',  isFavorite: true,  deletedTimestamp: 0 },              // 收藏
  { path: 'DCIM/img2.jpg',  isFavorite: false, deletedTimestamp: 0 },              // 普通
  { path: 'DCIM/img3.gif',  isFavorite: false, deletedTimestamp: 0 },              // GIF
  { path: 'Videos/v1.mp4',  isFavorite: false, deletedTimestamp: 0 },              // 视频
  { path: 'Trash/old.jpg',  isFavorite: false, deletedTimestamp: thirtyOneDaysAgo },// 超期
]
```

---

## ArkTS 严格模式下的 MockKit 替代方案（ArkTS-compat）

> **背景**：ArkTS 严格模式禁止 `arkts-no-ns-as-obj`（命名空间不能当对象）。MockKit 的 `mocker.mockFunc(target, target.method)` 第一参传 `@kit.*` namespace（如 `http` / `fileIo` / `photoAccessHelper`）时编译失败。**遇到此错绝不能降级到 C 级**（`expect(typeof method).assertEqual('function')` / `expect(true).assertTrue()` / 常量自比 — 见 `step1-unit-test-agent.md §6.1` 禁止清单）。
>
> **三种真断言路径**（按优先级试，命中可行即停；都不行 → BLOCKERS: mockkit_arkts_incompat）：

### 方案 1：构造器注入（推荐，最强可测性）

把 `@kit.*` 依赖通过构造器或工厂方法注入到被测类，测试时传一个 mock 实现。Service 提供一个"测试可见的内部构造器"或一个静态 `withDeps(...)` 工厂方法即可。

**反面教材（来自 EinkBro F004 翻译当前写法）**：

```typescript
// ❌ F004_Translation.test.ets:182 — 私自降级，没有任何行为验证
it('F004_AC2_translateText_calls_google_translate_api', 0, async () => {
  // MockKit 在 ArkTS 下无法 mock @kit.net.http
  expect(true).assertTrue()  // ← C 级占位，PASS 但未覆盖任何 spec 行为
})
```

**正确写法（构造器注入版）**：

```typescript
// 1) 源码侧：TranslateService 接受 HttpClient 接口（生产用真 http，测试用 fake）
export interface HttpClient {
  request(url: string, opts: HttpOptions): Promise<HttpResponse>
}
export class TranslateService {
  constructor(private http: HttpClient) {}
  async translate(text: string, targetLang: string): Promise<string> { /* ... */ }
}

// 2) 测试侧：注入 fakeHttpClient，断言真实调用参数
class FakeHttpClient implements HttpClient {
  public lastUrl: string = ''
  public lastHeaders: Record<string, string> = {}
  async request(url: string, opts: HttpOptions): Promise<HttpResponse> {
    this.lastUrl = url
    this.lastHeaders = opts.header
    return { responseCode: 200, result: '{"data":{"translations":[{"translatedText":"你好"}]}}' }
  }
}

it('F004_AC2_translateText_calls_google_translate_api', 0, async () => {
  const fake = new FakeHttpClient()
  const svc = new TranslateService(fake)
  const result = await svc.translate('hello', 'zh')
  // 真断言：endpoint URL 含 translate.googleapis.com
  expect(fake.lastUrl.includes('translate.googleapis.com')).assertTrue()
  // 真断言：Header 含 x-goog-api-key
  expect(fake.lastHeaders['x-goog-api-key']).assertContain('AIza')
  // 真断言：解析后的输出
  expect(result).assertEqual('你好')
})
```

### 方案 2：Wrapper 函数模式（次选）

源码已固化用 `@kit.*`，无法改成构造器注入时，包一层用户态函数（不是 namespace）。测试 mock 这层 wrapper 即可。

```typescript
// 源码侧 — utils/HttpWrapper.ets
export function makeHttpRequest(url: string, opts: HttpOptions): Promise<HttpResponse> {
  return http.createHttp().request(url, opts)
}

// 测试侧 — 用 MockKit mock 用户态 wrapper（class 实例化版）
class HttpWrapperShim {
  async makeRequest(url: string, opts: HttpOptions): Promise<HttpResponse> {
    return makeHttpRequest(url, opts)
  }
}
const shim = new HttpWrapperShim()
const mockReq = mocker.mockFunc(shim, shim.makeRequest)
when(mockReq)(ArgumentMatchers.any, ArgumentMatchers.any).afterReturn(
  Promise.resolve({ responseCode: 200, result: '{}' })
)
// 然后让生产代码调 shim.makeRequest 而不是 http.createHttp().request
```

### 方案 3：真实 Context + AppStorage seeding（兜底）

无法改源码、无依赖注入点时：用 `@kit.TestKit` 拿 delegator → AppStorage 预置数据 → Service 走 `__TEST_MODE__` 旁路读 AppStorage。

**反面教材（来自 EinkBro F021 Incognito 当前写法）**：

```typescript
// ❌ F021_Incognito.test.ets — 常量自比，毫无信息量
it('F021_AC1_incognito_blocks_addHistory', 0, () => {
  const incognito: boolean = true
  expect(incognito).assertEqual(true)  // ← 自我对比，没有触达任何业务代码
})
```

**正确写法（真实 Context + AppStorage seeding 版）**：

```typescript
import { abilityDelegatorRegistry } from '@kit.TestKit'
import { BrowserContainer } from '../../../../main/ets/data/BrowserContainer'
import { ConfigManager } from '../../../../main/ets/data/ConfigManager'

it('F021_AC1_incognito_blocks_addHistory', 0, async () => {
  // 1) 拿真实 Context
  const delegator = abilityDelegatorRegistry.getAbilityDelegator()
  const ctx = delegator.getAppContext()
  await ConfigManager.getInstance().init(ctx)

  // 2) AppStorage 预置 incognito=true
  AppStorage.setOrCreate<boolean>('__TEST_MODE__', true)
  AppStorage.setOrCreate<boolean>('incognito', true)
  ConfigManager.getInstance().incognito = true

  // 3) 调 BrowserContainer.add 模拟新建标签页
  const initialHistorySize = await getHistoryCount(ctx)
  BrowserContainer.getInstance().add({ url: 'https://example.com', title: 'Test' })
  await new Promise(resolve => setTimeout(resolve, 200))

  // 4) 真断言：history 没增加
  const afterHistorySize = await getHistoryCount(ctx)
  expect(afterHistorySize).assertEqual(initialHistorySize)  // ← 真行为：incognito 屏蔽 addHistory
})
```

### 方案 4：todo AC 的"预期 RED"写法

Spec 已声明、源码未实装的 AC，**必须**写正向行为断言期望 RED，而不是 method_exists。

**反面教材（来自 EinkBro F014 PIP 当前写法）**：

```typescript
// ❌ F014_PipFullscreen.test.ets:26 — method_exists 占位，无法暴露实装缺失
it('F014_AC1_toggleAudioOnly_method_exists', 0, () => {
  const ctrl: VideoPlaybackController = VideoPlaybackController.getInstance()
  expect(typeof ctrl.toggleAudioOnly === 'function').assertTrue()  // ← stub 也能 PASS
})

// ❌ F014_PipFullscreen.test.ets:75 — 常量恒等占位
it('F014_AC6_pip_mode_TODO', 0, () => {
  const expected: boolean = true
  expect(expected).assertTrue()  // ← 永远 PASS，spec 行为没断言
})
```

**正确写法（预期 RED 行为断言版）**：

```typescript
// ✅ 真断言 + 预期 RED
it('F014_AC6_pip_enters_pip_mode_when_user_clicks_pip_btn', 0, async () => {
  // Spec: F014 AC6 — 视频进 PiP 后主页面继续运行
  // 当前实装：PipService 是 PlaceholderPipController，enterPip() return null
  const ctrl = VideoPlaybackController.getInstance()
  const result = await ctrl.enterPip()
  // 预期 RED：实装应返回 PipSession 对象（{ isActive: true, windowSize: {...} }）
  // 但 stub 返回 null —— 测试必 RED，直到 PipKit 集成补完
  expect(result).assertNotNull()           // ← 触达 stub 边界
  expect(result.isActive).assertTrue()     // ← 触达 spec 行为
})
```

**关键差异**：method_exists 在 stub 也 PASS（method 就在那），只验证编译期符号；行为断言 stub 必 RED（return null 不满足 assertNotNull），实装补完后转 GREEN —— 这才是 TDD 的 spec 信号。

---

## 相关文档

- `templates/ui-test-skeleton.md` — UI 测试完整骨架 + helper
- `templates/direct-mount-bridge.md` — Step 2 桥模板
- `templates/test-data-setup.md` — Mock 数据注入
- `templates/id-injection.md` — .id() 注入规则
- `ui-test-antipatterns.md` — False-GREEN 陷阱 6 主题
- `compile-pitfalls.md` — ArkTS / arkXtest 编译期坑
- `testable-id-catalog.md` — id 命名 / manifest 格式圣经
