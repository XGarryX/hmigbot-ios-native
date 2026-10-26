---
name: arkts-knowledge-verifier
description: ArkTS 知识验证与查找入口（V2 优先，兼容 V1 查询）。当你对任何 ArkTS/HarmonyOS 知识点不确定时——API 版本兼容性、组件属性是否存在、装饰器语法、V1↔V2 装饰器迁移、权限字符串、ArkTS 与 TypeScript 的差异、配置字段含义、导入路径是否正确——务必触发此 skill。它会指引你到正确的 reference 文件查确切信息，避免生成错误代码。即使只是问"@State 是 V2 合法装饰器吗""ArkTS 能用 any 吗"也应触发。
metadata:
  type: domain
  domain: engineering
  tags:
  - verification
  - api-compat
  - decorator
  - arkts
---
# ArkTS Knowledge Verifier — 知识验证与查找入口（V2 优先 + V1 兼容）

## 项目策略与版本基线

**本项目锁 ArkTS V2（API 12+）**：a2h pipeline 与所有生成代码统一使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @Once / @Event / @Provider / @Consumer / @ObservedV2 / @Trace / @Monitor / @Computed / @ReusableV2`）和 V2 存储 API（`AppStorageV2.connect / PersistenceV2.globalConnect`）。

> 本 skill 是**知识索引**，不是教学 skill。它同时索引 **V2 主参考**（项目实际使用）和 **V1 历史参考**（迁移老项目或阅读老代码时查阅），并能回答"`@State` 是 V2 装饰器吗" / "我能在 `@ComponentV2` 中用 `@Watch` 吗"等版本判定问题。

---

## 何时使用此 Skill

当你对以下任何一类知识点不确定时，使用此 skill 的分层查找策略来验证：

| 不确定性类别 | 典型场景 | 首选查找位置 |
|---|---|---|
| **组件属性** | 不确定某组件是否有某个属性/方法 | `arkts-component-builder/references/common-components.md` |
| **V2 装饰器语法** | `@Local / @Param / @Event / @Provider / @Consumer / @ObservedV2 / @Trace / @Monitor / @Computed / @ReusableV2` 用法与组合 | `arkts-state-manager/references/v2-decorators.md` |
| **V1 装饰器历史** | `@State / @Prop / @Link / @Provide / @Consume / @Observed / @ObjectLink / @StorageLink / @Watch`（仅老项目兼容） | `arkts-state-manager/references/state-decorators.md`（legacy） |
| **V1→V2 装饰器映射** | "我把 V1 的 `@StorageLink` 升级到 V2 应该怎么写" | 本 skill `references/v2-migration-patterns.md` |
| **V2 全局/持久化存储** | `AppStorageV2.connect / PersistenceV2.globalConnect` | `arkts-state-manager/references/v2-global-state.md` |
| **权限字符串** | 不确定权限的完整名称 | `arkts-project-scaffolder/SKILL.md` 权限速查表 |
| **配置字段** | 不确定配置文件的字段名/格式 | `arkts-project-scaffolder/references/config-reference.md` |
| **导入路径** | 不确定 @kit.* 的正确模块名 | 本 skill 的 @ohos→@kit 映射表（见下文） |
| **版本兼容** | 不确定某 API 在目标版本是否可用 | 本 skill `references/api12-baseline.md` / `v2-decorator-rules.md` |
| **语言限制** | 不确定 ArkTS 相对 TypeScript 的限制 | 本 skill `references/arkts-vs-typescript.md` |
| **网络 API** | 不确定 HTTP 请求的参数/用法 | `arkts-data-layer/references/network-service.md` |
| **动画 API** | 不确定动画函数的参数 | `arkts-animation-builder/references/explicit-animation.md` |
| **导航 API** | 不确定 NavPathStack 的方法/参数 | `arkts-navigation-builder/references/nav-patterns.md` |

完整索引见 `references/verification-index.md`。

---

## 装饰器版本快速判定（V1 vs V2）

被问到任意装饰器名时，可用此表立刻判断版本归属、是否合法、V2 等价物：

| 装饰器名 | 所属版本 | V2 等价 / 处理 | 在 `@ComponentV2` 中可用？ |
|---|---|---|---|
| `@ComponentV2` | V2 | — | ✓ 必须 |
| `@Component` | V1 | `@ComponentV2` | ✗ |
| `@Local` | V2 | — | ✓ |
| `@State` | V1 | `@Local` | ✗ |
| `@Param` | V2 | — | ✓ |
| `@Param + @Once` | V2 | — | ✓（只读语义） |
| `@Prop` | V1 | `@Param`（可改）/ `@Param + @Once`（只读） | ✗ |
| `@Event` | V2 | — | ✓ |
| `@Link` | V1 | **没有直接等价** — `@Param + @Event` 回调 | ✗ |
| `@Provider()` | V2 | — | ✓（必须带括号） |
| `@Provide` | V1 | `@Provider()` | ✗ |
| `@Consumer()` | V2 | — | ✓（必须带括号 + 默认值） |
| `@Consume` | V1 | `@Consumer()` | ✗ |
| `@ObservedV2` | V2 | — | ✓（类装饰器） |
| `@Observed` | V1 | `@ObservedV2` | ✗ |
| `@Trace` | V2 | — | ✓（@ObservedV2 类属性） |
| `@ObjectLink` | V1 | **取消** — `@ObservedV2` 实例直接通过 `@Param` 传 | ✗ |
| `@StorageLink('key')` | V1 | `AppStorageV2.connect(Cls, key, () => new Cls())` | ✗ |
| `@StorageProp('key')` | V1 | 同上（只读） | ✗ |
| `@LocalStorageLink` | V1 | `@Provider()/@Consumer()` 或页面根 `@Local`+`@Param`（无 LocalStorageV2） | ✗ |
| `@LocalStorageProp` | V1 | 同上 | ✗ |
| `PersistentStorage.persistProp` | V1 | `PersistenceV2.globalConnect({type, key, defaultCreator})` | — |
| `@Monitor('prop')` | V2 | — | ✓（方法装饰器，签名带 `IMonitor`） |
| `@Watch` | V1 | `@Monitor` | ✗ |
| `@Computed` | V2（V1 无） | — | ✓ |
| `@ReusableV2` | V2 | — | ✓ |
| `@Reusable` | V1 | `@ReusableV2` | ✗ |
| `@Track` | V1（API 12+） | `@Trace`（语义不同：V1 整类启用过滤；V2 属性级精确观察） | ✗ |
| `@Entry / @Builder / @BuilderParam / @Styles / @Extend` | V1/V2 通用 | — | ✓ |

**判定示例**：

> **Q**：`@State` 是合法的 V2 装饰器吗？
> **A**：不是。`@State` 是 V1 装饰器。V2 等价物是 `@Local`。本项目锁 V2，新代码请用 `@Local`。如阅读老项目，参阅 `arkts-state-manager/references/state-decorators.md`（legacy）。

> **Q**：我能在 `@ComponentV2` 内用 `@Watch` 吗？
> **A**：不能。`@Watch` 是 V1 装饰器，与 `@ComponentV2` 不兼容（编译报错"V1/V2 mixed usage"）。V2 用 `@Monitor('propName') method(monitor: IMonitor): void`。

> **Q**：V1 的 `@Link` 在 V2 怎么写？
> **A**：V2 没有 `@Link` 直接等价，改用 **`@Param + @Event` 回调**模式：父持 `@Local`，传 `value + onValueChange` 给子；子用 `@Param value` 接收 + `@Event onValueChange` 回调通知父。

完整 V2 装饰器语法/边界 → `arkts-state-manager/references/v2-decorators.md`。
完整 V1→V2 装饰器迁移规则 → 本 skill `references/v2-migration-patterns.md`。

---

## 分层查找策略

遇到不确定的知识点时，按以下层次查找：

### Layer 1：查本地 reference 文件（总是可用）

1. 在上方"何时使用此 Skill"表中找到对应类别
2. 读取"首选查找位置"指向的 reference 文件
3. 如果该文件能回答你的问题，直接使用

这一步不需要任何外部工具，任何环境都可以执行。

### Layer 2：查官方文档（条件性）

若工具环境有网络搜索/获取能力（WebSearch / WebFetch / MCP 文档服务等），查阅华为开发者文档：

- API 参考首页：`https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V5/`
- 版本 Release Notes：`https://developer.huawei.com/consumer/cn/doc/harmonyos-releases/`
- 搜索特定 API：WebSearch `"HarmonyOS [API名称] site:developer.huawei.com"`

如果没有网络工具，**跳过此步**，直接进入 Layer 3。不要假装查阅了文档。

### Layer 3：标注不确定性（兜底）

当 Layer 1 和 Layer 2 都无法确认时：

1. 用 `[待验证]` 标记不确定的信息
2. 给出你的最佳猜测 + 推理依据（例如"根据 API 12 的模式推断..."）
3. 建议用户通过以下方式确认：
   - 在 DevEco Studio 中查看自动补全和文档提示
   - 查阅华为开发者官方文档
   - 编译验证

**示例**：
```
Text 组件支持 .fontColor() 设置字体颜色（参见 common-components.md）。
注意：Text 没有 .color() 属性 — 这是 CSS/Web 的写法，ArkTS 中用 .fontColor()。

Text 支持 .letterSpacing() 设置字符间距（签名 letterSpacing(value: number | ResourceStr)，
API 12 起可用，syscap SystemCapability.ArkUI.ArkUI.Full）—— 这是已验证属性，直接给肯定结论，
不要标 [待验证]。（Search / Span / TextInput / TextArea 同族也有 .letterSpacing()。）
```

> **别把已验证属性标成 `[待验证]`**：`[待验证]` 只用于你**确实无法**从 reference / 本表 / 官方文档确认的名称。
> 若某属性/API 已在本 skill 的 reference 或纠错/清单里给出确定结论，就下肯定结论，不要用 `[待验证]` 回避。
> `[待验证]` 兜底针对的是「查遍 Layer 1 仍无结论」的真未知项，不是「不想承担判断」的挡箭牌。

---

## ArkTS vs TypeScript 关键差异速查

LLM 最大的幻觉来源是把 TypeScript 经验直接套用到 ArkTS。以下是最关键的差异：

| 特性 | TypeScript | ArkTS | 常见错误 |
|---|---|---|---|
| 组件声明 | `class` | `struct`（不能继承、不能 new） | 写成 `class MyComp` |
| 组件装饰器 | 无（React 用函数/类） | V2: `@ComponentV2` / V1: `@Component` | V2 项目误用 `@Component` |
| UI 语法 | JSX `<Comp prop={v}/>` | 链式调用 `Comp().prop(v)` | 写 JSX 标签语法 |
| build() | 无限制 | 只能放 UI 描述 | 在 build() 里声明变量、console.log |
| `any` 类型 | 允许 | **禁止** | 用 `any` 声明类型 |
| 对象解构 | `const {a,b} = obj` | 受限 | 在组件中解构 |
| DOM API | 可用 | **不存在** | 用 `document.getElementById` |
| npm 包 | 可用 | **不可用** | 试图 import npm 包 |
| 模块导入 | `from 'pkg'` | `from '@kit.*'` | 用 `@ohos.*`（已废弃） |
| 对象字面量类型 | `(data: {a: number}) => {}` | **禁止**（用 class 替代） | 回调参数用对象字面量类型 |
| `as` 类型转换 | `x as Type` | ✅ **合法**（ArkTS 唯一转换语法；仅 `<Type>x`、`as const` 禁用） | 转换/窄化用 `as T`，可配 instanceof |
| 回调参数类型 | 匿名接口 | **必须用 class** | 系统回调用对象字面量 |

**详细差异 + 代码示例**：见 `references/arkts-vs-typescript.md`

---

## 常见幻觉警示

LLM 生成 ArkTS 代码时最常犯的 11 类错误，遇到时请特别警惕：

### 1. 虚构组件属性
❌ `Text('hello').color('#333')` — Text 没有 `.color()`，应该用 `.fontColor()`
❌ `Image($r('app.media.img')).src('url')` — Image 的图片源在构造参数中传入，不是 `.src()`

### 2. 在 build() 中写逻辑语句
❌ `build() { let x = 1; ... }` — build() 中不能声明变量
❌ `build() { console.log('render'); ... }` — build() 中不能 console.log

### 3. 用 class 代替 struct
❌ `@ComponentV2 class MyComp { ... }` — 必须用 `struct`（V1 的 `@Component class` 同理错）

### 4. 使用废弃的 @ohos.router
❌ `import router from '@ohos.router'` — API 12+ 已废弃，用 Navigation + NavPathStack

### 5. V1/V2 装饰器混用（V2 项目最常见编译错误）
❌ 在 `@ComponentV2` 内用 `@State / @Prop / @Link / @Watch` — 编译报错"V1/V2 mixed usage"
✓ 全部改 V2：`@Local / @Param / @Param+@Event / @Monitor`

### 6. @Param 不初始化
❌ `@Param title: string` — V2 强制要求默认值：`@Param title: string = ''`
（V1 `@Prop` 自 API 12+ 也强制初始化，规则一致）

### 7. 使用 any/unknown 类型
❌ `let data: any = ...` — ArkTS 禁止 any/unknown

### 8. 虚构权限字符串
❌ `"ohos.permission.NETWORK"` — 正确的是 `"ohos.permission.INTERNET"`
权限字符串必须精确匹配，查阅 project-scaffolder 的权限速查表

**高频精确权限陷阱**（完整权限表仍见 `arkts-project-scaffolder` 权限速查表；这里只收 knowledge-verifier 该拦的成对/易错约束）：

| 场景 | 权限字符串 | 成对 / 约束 |
|---|---|---|
| **精确定位** | `ohos.permission.LOCATION` | **不能单独申请**，必须**同时**申请 `ohos.permission.APPROXIMATELY_LOCATION`（模糊定位）；即精确定位 = 两个一起。单独 `APPROXIMATELY_LOCATION` 只给模糊位置；单独 `LOCATION` 申请会失败。**不是** Android 的 `ACCESS_FINE_LOCATION` / `ACCESS_COARSE_LOCATION`。 |
| 后台持续定位 | `ohos.permission.LOCATION_IN_BACKGROUND` | 建立在已获前台定位权限之上，额外申请。 |

### 9. 使用 @ohos.* 导入
❌ `import { http } from '@ohos.net.http'` — 用 `import { http } from '@kit.NetworkKit'`
查阅下方的 @ohos→@kit 映射表

### 10. 函数表达式当值
❌ `const f = function(){...}` / `arr.forEach(function(x){...})` — ArkTS 不支持函数表达式，改箭头函数 `=>`

### 11. 依赖 structural typing / 对象字面量当 class 实例
❌ `let c: C = { x: 1 }`（C 是 class）— ArkTS 不支持 structural typing，类实例必须 `new C()`；匿名类同样不支持（用具名/嵌套类）

---

## 已验证 sys.symbol 名称清单

LLM 经常虚构不存在的 SymbolGlyph 名称。详见 `references/verified-symbols.md`（由 a2h-retrospect 自动维护）。

> 不确定的名称请标注 `[待验证]`，建议在 DevEco Studio 中编译确认。

---

## API 命名纠错表

| 错误名称 | 正确名称 | 来自 |
|---------|---------|------|
| `promptAction.ShowActionMenuSuccessResponse` | `promptAction.ActionMenuSuccessResponse` | @kit.ArkUI |

详见 `references/api-corrections.md`。

---

## API 版本概览

| HarmonyOS 版本 | API 级别 | 发布时间 | 关键变化 |
|---|---|---|---|
| 5.0.0 | **API 12** | 2024.11 | 首个 NEXT 稳定版，@kit.* 推荐，router 废弃，**ArkTS V2 装饰器引入**（`@ComponentV2 / @Local / @Param / ...`） |
| 5.0.1 | **API 13** | 2025.01 | 增量优化 |
| 5.0.2 | **API 14** | 2025.02 | Reader Kit, GPU 渲染 |
| 5.0.3 | **API 15** | 2025.03 | 2in1 设备 API, C API 扩展 |
| 5.0.5 | **API 17** | 2025.03 | ArkUI/Ability/ArkData 变更 |
| 5.1.0 | **API 18** | 2025.06 | 媒体和 Web 能力增强 |
| 6.0.0 | **API 20** | 2025.06 | 大版本更新，V2 装饰器全面成熟 |
| 6.0.1 | **API 21** | 2025.11 | 当前最新稳定版 |
| 6.x | **API 23** | 2026.02 | 最新 Dev Beta |

> ArkTS V2 装饰器（`@ComponentV2 / @Local / @Param / AppStorageV2 / ...`）要求 **API 12+**。本项目锁 V2，确保 `build-profile.json5` 的 `compatibleSdkVersion >= 12`。

---

## 版本检测方法

生成代码前，先确认用户的目标 API 版本：

```
读取项目的 build-profile.json5 → app.products[].compatibleSdkVersion
括号内的数字（或直接的数字）就是 API 级别。

示例：
  compileSdkVersion: 12              → API 12
  compileSdkVersion: "5.0.0(12)"     → API 12
  compatibleSdkVersion: 22           → API 22
```

如果无法确定版本，**默认按 API 12 + V2 装饰器生成代码**（项目锁 V2 的最低基线）。

---

## @ohos → @kit 模块映射表

API 12+ 推荐使用 `@kit.*` 导入。完整映射见 `references/api12-baseline.md`，以下是最常用的：

| 旧 (@ohos.*) | 新 (@kit.*) |
|---|---|
| `@ohos.window` | `@kit.ArkUI` |
| `@ohos.router` | `@kit.ArkUI`（但 router 本身已废弃，用 Navigation） |
| `@ohos.curves` | `@kit.ArkUI` |
| `@ohos.net.http` | `@kit.NetworkKit` |
| `@ohos.net.connection` | `@kit.NetworkKit` |
| `@ohos.data.preferences` | `@kit.ArkData` |
| `@ohos.data.relationalStore` | `@kit.ArkData` |
| `@ohos.app.ability.UIAbility` | `@kit.AbilityKit` |
| `@ohos.app.ability.common` | `@kit.AbilityKit` |
| `@ohos.multimedia.image` | `@kit.ImageKit` |
| `@ohos.file.fs` | `@kit.CoreFileKit` |
| `@ohos.hilog` | `@kit.PerformanceAnalysisKit` |
| `@ohos.notification` | `@kit.NotificationKit` |

---

## 废弃 API / V1 装饰器替代方案（概要）

核心替代模式（详细代码见 `references/v2-migration-patterns.md` 与 `references/migration-patterns.md`）：

| 废弃 / V1 | 替代 / V2 | 说明 |
|---|---|---|
| `router.pushUrl()` | `navPathStack.pushPathByName()` | API 12+ |
| `router.back()` | `navPathStack.pop()` | API 12+ |
| `@ohos.data.preferences` | `import { preferences } from '@kit.ArkData'` | 仅导入路径变化 |
| `@Component struct` | `@ComponentV2 struct` | V2 项目锁定 |
| `@State x` | `@Local x` | V2 组件内部状态 |
| `@Prop x = ''` | `@Param x = ''`（可改）/ `@Param @Once x = ''`（只读） | V2 单向数据流 |
| `@Link x` | `@Param x = '' + @Event onXChange = () => {}` | V2 用回调实现双向 |
| `@Provide / @Consume` | `@Provider() / @Consumer()` | 必须带括号 |
| `@Observed class` | `@ObservedV2 class`，属性加 `@Trace` | V2 属性级精确观察 |
| `@ObjectLink x` | `@Param x = new Cls()` 直接持有 `@ObservedV2` 实例 | V2 取消 `@ObjectLink` |
| `@StorageLink('k')` | `@Local x = AppStorageV2.connect(Cls, 'k', () => new Cls())!` | V2 用 connect API |
| `@LocalStorageLink('k')` | `@Provider()/@Consumer()` 或页面根 `@Local`+`@Param`（无 LocalStorageV2） | 同上 |
| `PersistentStorage.persistProp` | `PersistenceV2.globalConnect({type, key, defaultCreator})` | V2 一站式持久化 |
| `@Watch('m') x` | `@Local x` + `@Monitor('x') m(monitor: IMonitor): void` | V2 是方法装饰器 |
| `@Reusable` | `@ReusableV2` | 配合 `@ComponentV2` |

---

## 各版本 Breaking Changes 概要

- **API 12**（基线）：@Prop 必须初始化、@Link 不需 $ 前缀、router 废弃、@kit.* 推荐、keyframeAnimateTo 新增、**ArkTS V2 装饰器引入**（`@ComponentV2 / @Local / @Param / @Event / @Provider / @Consumer / @ObservedV2 / @Trace / @Monitor / @Computed / AppStorageV2 / PersistenceV2`）
- **API 13~15**：增量优化，无 Breaking Changes
- **API 17**：部分组件属性调整、RelationalStore 接口微调
- **API 18~20**：媒体/Web 增强，权限模型微调，V2 装饰器特性逐步完善
- **API 21**：稳定性优化

**详细变化清单**：见 `references/api13-21-changes.md`

---

## canIUse() 特性检测

运行时检查设备是否支持某个系统能力：

```typescript
if (canIUse('SystemCapability.Multimedia.Camera.Core')) {
  // 有相机能力
}

// 常用系统能力
'SystemCapability.Communication.NetStack'          // 网络
'SystemCapability.Multimedia.Camera.Core'           // 相机
'SystemCapability.Location.Location.Core'           // 定位
'SystemCapability.ArkUI.ArkUI.Full'                // 完整 ArkUI
```

---

## 生成检查清单

- [ ] 确认了用户的目标 API 版本（读 build-profile.json5）
- [ ] 对不确定的知识点执行了分层查找
- [ ] 导入使用 `@kit.*` 而非 `@ohos.*`
- [ ] 导航使用 `Navigation` 而非 `@ohos.router`
- [ ] 组件使用 `@ComponentV2`，状态使用 `@Local`，单向使用 `@Param (+ @Once)`，双向使用 `@Param + @Event`
- [ ] 没有在 `@ComponentV2` 中混入任何 V1 装饰器（`@State / @Prop / @Link / @Watch / @Provide / @Consume / @Observed / @ObjectLink / @StorageLink ...`）
- [ ] 可观察类用 `@ObservedV2`，可观察属性加 `@Trace`
- [ ] 全局/持久化用 `AppStorageV2.connect / PersistenceV2.globalConnect`
- [ ] `@Param` 变量有默认初始值（V2 强制）
- [ ] 没有使用 `any` / `unknown` 类型
- [ ] 组件属性名称已验证（如 `.fontColor()` 而非 `.color()`）
- [ ] 权限字符串经过查证
- [ ] 不确定的信息已标注 `[待验证]`

---

## Skill 路由指南

当你被触发但用户的需求超出本 skill 范围时，使用以下决策树判断应该读取哪个 skill 的内容：

### 决策树

```
用户请求的核心是什么？
│
├─ 问知识点/验证语法 → 在本 skill 内回答（分层查找策略）
│
├─ 问 V1 装饰器是不是 V2 / V2 装饰器存不存在 → 本 skill 顶部"装饰器版本快速判定"表
│
├─ 要 UI 组件/页面布局 → 读取 arkts-component-builder/SKILL.md
│
├─ 要完整业务功能（列表详情页、搜索、登录等）
│   └─ 读取 arkts-pattern-library/SKILL.md（它有编排协议引导后续步骤）
│
├─ 要从零搭建项目
│   └─ 读取 arkts-project-scaffolder/SKILL.md（它有 6 步编排指南）
│
├─ 要动画效果 → 读取 arkts-animation-builder/SKILL.md
│
├─ 要页面导航/路由 → 读取 arkts-navigation-builder/SKILL.md
│
├─ 要状态管理/数据通信（V2 优先） → 读取 arkts-state-manager/SKILL.md
│
├─ 要数据请求/持久化 → 读取 arkts-data-layer/SKILL.md
│
├─ 要三方库替代方案 → 读取 arkts-library-migration/SKILL.md
│
├─ 要媒体播放/AVPlayer/后台播放 → 读取 arkts-media-playback/SKILL.md
│
├─ 要文件下载/下载管理 → 读取 arkts-download-manager/SKILL.md
│
├─ 要 Android UI 对齐/Material 迁移 → 读取 arkts-ui-alignment/SKILL.md
│
└─ 要系统能力（媒体/权限/文件/后台任务） → 读取 arkts-system-capabilities/SKILL.md
```

### 综合回答

即使被触发的是 knowledge-verifier，你也可以读取其他 skill 的 reference 文件来给出综合回答。例如用户问"下拉刷新列表怎么做"，可以同时读取 pattern-library 的模式模板和 data-layer 的 BasicDataSource 实现来组织完整回答。

> 完整的请求分类矩阵、场景路由表和输出合并协议见 `references/skill-routing-guide.md`

---

## References

### 版本与迁移（V2 优先）

- `references/v2-decorator-rules.md` — **V2 装饰器规则速查**（`@ComponentV2 / @Local / @Param / @Once / @Event / @Provider / @Consumer / @ObservedV2 / @Trace / @Monitor / @Computed / @ReusableV2` 与 V2 存储 API）
- `references/v2-migration-patterns.md` — **V1→V2 装饰器迁移完整规则**（13 类映射 + `@Link` / `@StorageLink` 等结构性改写示例）
- `references/api12-baseline.md` — API 12 基线：完整的导入映射 + 状态装饰器规则（V1 历史 + V2 引导）+ 导航方案
- `references/api13-21-changes.md` — API 13~21 每个版本的增量变化清单
- `references/migration-patterns.md` — `@ohos→@kit` 迁移代码对照、router→Navigation 迁移步骤、V1 `@Prop / @Link` 语法过渡（V1 项目升 API 12 用，跨 V1→V2 升级请优先看 `v2-migration-patterns.md`）

### 语言与索引

- `references/arkts-vs-typescript.md` — ArkTS 与 TypeScript 的所有关键差异 + 代码示例（含 V2 装饰器示例）
- `references/verification-index.md` — 全 skill 体系知识查找索引
- `references/skill-routing-guide.md` — Skill 路由与编排指南（请求分类矩阵 + 场景路由表 + 输出合并协议）
- `references/real-migration-pitfalls.md` — 22 条实战踩坑百科（AVPlayer/下载/UI/语言/导航/数据库/网络）
- `references/verified-symbols.md` / `references/api-corrections.md` — 已验证 sys.symbol 与 API 名称纠错（auto-maintained by a2h-retrospect）

### 跨 Skill 主参考

- `arkts-state-manager/references/v2-decorators.md` — V2 装饰器完整语法与边界（主参考）
- `arkts-state-manager/references/v2-global-state.md` — `AppStorageV2 / PersistenceV2` 完整模板
- `arkts-state-manager/references/v2-update-patterns.md` — V2 数据更新模式
- `arkts-state-manager/references/state-decorators.md`（legacy） — V1 装饰器历史参考（仅老项目兼容查阅）
