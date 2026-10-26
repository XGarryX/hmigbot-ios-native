---
name: arkts-data-layer
description: 生成 ArkTS/HarmonyOS 数据层代码（V2 优先，API 12+）。当用户需要创建数据模型、网络请求服务、IDataSource/LazyDataSource/BasicDataSource、EventHub 事件通信、HTTP 请求、Promise/async-await 异步、Preferences 持久化、文件读写、JSON 解析、RdbStore CRUD，或任何数据获取/存储/传输相关代码时，务必触发此 skill。即使只说"怎么请求接口""存一下数据"也应触发。完整业务功能（下拉刷新列表、列表详情页）优先 arkts-pattern-library。
metadata:
  type: domain
  domain: data
  tags:
  - data
  - network
  - persistence
  - rdb
---
# ArkTS Data Layer — 数据层生成器（V2 优先）

## API 版本与项目策略

本 skill 的代码模板基于 **API 12+（HarmonyOS 5.0.0+）和 ArkTS V2 装饰器体系**。

> **项目锁 V2**：本项目所有新生成代码使用 V2 装饰器（`@ComponentV2 / @Local / @Param / @Event / @ObservedV2 / @Trace / @Monitor / @Computed / AppStorageV2 / PersistenceV2`）。Model 层用 `@ObservedV2` + `@Trace` 标记可观察属性；UI 层用 `@ComponentV2` + `@Local` 持有实例；服务单例用 `AppStorageV2.connect(...)` 共享。如需查阅 V1 老写法（`@Observed / @ObjectLink / @State / @StorageLink` 等），参阅 `references/model-patterns.md` / `references/datasource-patterns.md` / `references/network-service.md` 等 V1 历史文档（已加 legacy 标识），同时阅读对应的 `v2-*.md` V2 主参考。

数据层相关的导入变化：

- HTTP 请求：`import { http } from '@kit.NetworkKit'`（不要用 `@ohos.net.http`）
- 网络状态：`import { connection } from '@kit.NetworkKit'`（不要用 `@ohos.net.connection`）
- 本地存储：`import { preferences } from '@kit.ArkData'`（不要用 `@ohos.data.preferences`）
- 关系型数据库：`import { relationalStore } from '@kit.ArkData'`
- Ability：`import { common } from '@kit.AbilityKit'`（不要用 `@ohos.app.ability.common`）
- V2 状态管理：`import { AppStorageV2, PersistenceV2 } from '@kit.ArkUI'`（**无 `LocalStorageV2`**；页面子树共享用 `@Provider`/`@Consumer`，见 `references/v2-network-service.md` §6.3）

生成代码前，先确认用户的目标 API 版本 ≥ 12。检查方法：读取 `build-profile.json5` 的 `compatibleSdkVersion` 字段。遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 arkts-knowledge-verifier skill。

---

## 数据层架构（V2）

ArkTS V2 应用的数据层通常包含三个层次：

```
UI 层（@ComponentV2）
    ↓ 使用 @Local / @Param 持有
Model 层（@ObservedV2 class，属性加 @Trace）
    ↓ 调用方法获取数据
Service 层（网络请求 / RdbStore / Preferences）
    ↓ 返回 Promise<T>
外部（HTTP API / 关系型数据库 / Preferences / 文件系统）

跨页/全局共享：AppStorageV2.connect(Cls, key, () => new Cls())
持久化（驱动 UI）：PersistenceV2.globalConnect({type, key, defaultCreator})
```

V2 数据层关键差异（vs V1）：

| 方面 | V1 写法 | V2 写法 |
|---|---|---|
| Model 类装饰器 | `@Observed` | `@ObservedV2` |
| 可观察属性标记 | 默认观察第一层 | 显式 `@Trace`（属性级精确） |
| 子组件持有 Model | `@ObjectLink` | `@Param`（直接传 `@ObservedV2` 实例） |
| 全局共享 | `@StorageLink('key')` | `@Local x = AppStorageV2.connect(Cls, key, () => new Cls())!` |
| 持久化 | `PersistentStorage.persistProp` + `@StorageLink` 双层 | `PersistenceV2.globalConnect({type, key, defaultCreator})` 一站式 |
| 监听数据变化 | `@Watch('method')` | `@Monitor('prop') method(m: IMonitor)` |

### 数据存储决策树

```
数据要存哪里？
│
├─ 网络 API（远程数据）
│   └─ HttpUtil + Service 层（见下方第 3 节）
│
├─ 键值对设置（用户偏好、配置）
│   ├─ 仅持久化、不需 UI 响应 → Preferences（见下方第 5 节）
│   └─ 持久化 + UI 响应 → PersistenceV2.globalConnect（见下方第 6 节）
│
├─ 本地关系型数据库（结构化数据、需要 SQL 查询）
│   └─ RdbStore / relationalStore（见 references/rdbstore-dao-patterns.md）
│       · 单例初始化 + SecurityLevel
│       · 手写 CREATE TABLE SQL（替代 Room @Entity）
│       · DAO 类 + querySql()（替代 Room @Dao）
│       · ResultSet 必须 close()
│
├─ 跨页 / 全局运行时状态（不持久）
│   └─ AppStorageV2.connect（见下方第 6 节）
│
└─ 事件通信（组件间数据传递）
    └─ EventHub（见下方第 4 节）
```

---

## 数据模型 / 数据源 / 网络请求（详见 references）

> **MUST**：写数据层代码前，按需先读对应 reference——

> - 数据模型（@ObservedV2 + @Trace 类、fromJson 反序列化） → `references/v2-model-patterns.md`
> - IDataSource / BasicDataSource / LazyDataSource 列表数据源 → `references/v2-datasource-patterns.md`
> - HTTP 请求（http.createHttp / destroy）、Promise/async-await 封装 → `references/v2-network-service.md`

---

## EventHub 事件通信

适用于没有直接父子关系的组件间通信（与 V1/V2 装饰器无关）：

```typescript
import { common } from '@kit.AbilityKit'

// 发送事件
const context = this.getUIContext().getHostContext() as common.UIAbilityContext
context.eventHub.emit('cartUpdated', { count: 5 })

// 接收事件（在 @ComponentV2 struct 内）
aboutToAppear(): void {
  const context = this.getUIContext().getHostContext() as common.UIAbilityContext
  context.eventHub.on('cartUpdated', (data: Record<string, number>) => {
    this.cartCount = data.count
  })
}

// 取消订阅（防止内存泄漏）
aboutToDisappear(): void {
  const context = this.getUIContext().getHostContext() as common.UIAbilityContext
  context.eventHub.off('cartUpdated')
}
```

**事件名称建议定义为常量**：

```typescript
export class EventConstants {
  static readonly CART_UPDATED = 'cartUpdated'
  static readonly LOGIN_STATE_CHANGED = 'loginStateChanged'
  static readonly THEME_CHANGED = 'themeChanged'
}
```

> V2 项目中，跨组件事件通信也可考虑用 `@Provider() / @Consumer()`（适合祖先→后代）或 `AppStorageV2.connect`（适合无层级关系的全局状态）。EventHub 更适合需要"主动 emit + 被动 on"的事件流模式（如登录态变更广播）。

---

## 本地持久化 / 全局状态（详见 references）

> **MUST**：本地存储或全局状态前，先读 reference——

> - Preferences 本地持久化（put 后必须 flush） → `references/v2-network-service.md`
> - AppStorageV2（运行时共享）/ PersistenceV2（持久化+响应式）；页面子树共享用 `@Provider`/`@Consumer`（无 `LocalStorageV2`） → `references/v2-model-patterns.md`
> - **RDB 关系数据库进阶（事务 / batchInsert / RdbPredicates 全算子 / version 升级迁移 / encrypt 加密）** → `references/v2-rdb-advanced.md`（基础 CRUD 见 `references/rdbstore-dao-patterns.md`）

---

## 文件读写（fileIo）

> **MUST**：读写文件 / 缓存 / 导入导出前，先读 `references/v2-file-io.md` —— 沙箱目录、整文件文本读写、JSON 落盘、分块二进制、目录管理。⚠️ 用 `@kit.CoreFileKit`（非废弃 `@ohos.fileio`），路径必须用沙箱路径，`closeSync` 配对。

---

## 常见错误速记（V2）

| # | 错误 | 正确做法 |
|---|---|---|
| 1 | HTTP 请求没 destroy | 用完调用 httpRequest.destroy() |
| 2 | BasicDataSource 整体 reload | 用 notifyDataAdd/Change/Delete 增量通知 |
| 3 | Preferences 没 flush | put 后 await flush() |
| 4 | EventHub 没取消订阅 | aboutToDisappear 里 off() |
| 5 | 忘记给 Model 属性加 @Trace | 需观察的属性加 @Trace |
| 6 | V2 项目混入 V1 装饰器 | 全用 V2 |
| 7 | AppStorageV2 key 拼写不一致 | key 用常量集中定义 |
| 8 | 自定义错误类不 `extends Error` 就 `throw` | 自定义错误类必须 `extends Error` 且构造器调 `super(message)`，否则 `throw new XxxError()` 报 **arkts-limited-throw**（ArkTS 只能 throw Error 及其子类） |
| 9 | `ResultSet.getColumnType` 当同步用 | `getColumnType(id): Promise<ColumnType>` 是 **async**（ResultSet API18+），须 `await rs.getColumnType(idx)`；已知列类型时直接 `getBlob(getColumnIndex('col'))` 更稳 |
| 10 | 组件内取 UIAbilityContext 用旧 `getContext(this)` | 用 `this.getUIContext().getHostContext() as common.UIAbilityContext`（新写法，文档明示在页面中返回 UIAbilityContext） |
| 11 | catch 形参标 `unknown`/`any`，或把 error 传给 `(e: unknown)` 形参 | **catch 形参省略类型标注**：`catch (error) {…}`（标 `unknown`/`any`/任何类型都报 **arkts-no-types-in-catch**）；要把它传给函数或存量，形参/变量类型用 **`Object`**（非 `unknown`/`any`，否则 **arkts-no-any-unknown**），再 `instanceof`/`as` 收窄 |
| 12 | 裸对象字面量 / `{} as T` 充当返回值或入参 | 每个对象字面量须对应**已声明的 class/interface 且字段补齐**（否则 **arkts-no-untyped-obj-literals**）；**禁 `{} as T` / 裸 `{}`**（泛型或空对象对应不上声明类型）——「空/缺省」用可空字段 `data: T \| null` 返回 `null`，或 `new` 一个真实类型实例 |
| 13 | multipart 上传把选择器路径/uri **直接**当 `filePath`（或当文本 `data`）传 | 上传前**先** `fileIo.copyFile` 把选中文件拷进沙箱（`cacheDir`/`filesDir`），`multiFormDataList` 文件项 `filePath` 用**沙箱路径**、文本项用 `data`；外部选择器路径 http 读不到 → 后端收空（接口仍 200）。详见 v2-network-service §1b |
| 14 | 把 `@ObservedV2` 实例**直接** `JSON.stringify` 当请求体/落盘 | `@Trace` 字段 key 全变 `__ob_xxx`、后端不识别（编译零提示、接口可能仍 200）——序列化出口走 `toJson()` 显式映射，或用**无装饰器纯 DTO**；UI 模型照常装饰、不为此剥装饰器。详见 v2-model-patterns §3 |

> **MUST**：每条完整「错误 vs 正确」代码见对应 reference（v2-model / v2-datasource / v2-network-service）。

---

## 生成检查清单（V2）

- [ ] 数据模型类用 `@ObservedV2`（不是 V1 `@Observed`）
- [ ] 模型的可观察属性都加了 `@Trace`
- [ ] 子组件接收模型实例用 `@Param`（不是 V1 `@ObjectLink`）
- [ ] 构造函数使用 Partial + 默认值防御（防御网络数据缺字段）
- [ ] HTTP 请求有 try-finally + destroy 清理
- [ ] module.json5 声明了 INTERNET 权限
- [ ] 文件上传（multipart）：选中文件**先落沙箱**（`fileIo.copyFile`），`multiFormDataList` 文件项用 `filePath`（沙箱路径）、文本项用 `data`（不把外部路径/uri 当值传）
- [ ] 发给后端/落盘的序列化走 `toJson()`（或无装饰器纯 DTO）——不直接 `JSON.stringify` `@ObservedV2` 实例（`__ob_` 前缀陷阱）
- [ ] async/await 正确使用，错误统一在 catch 中转换；**自定义错误类 `extends Error` + `super(message)`** 才能被 `throw`
- [ ] catch 形参不标类型（`catch (error)`，非 `unknown`/`any`）；error 传入的函数形参/变量用 `Object` 再 instanceof/as 收窄
- [ ] 所有对象字面量都有声明类型（class/interface 字段补齐 或 Record）；不写 `{} as T`，空/缺省值用 `T | null` + 返回 `null`
- [ ] Preferences 写入后调用了 flush
- [ ] EventHub 在 aboutToDisappear 中取消订阅
- [ ] BasicDataSource 通知方法与操作匹配（add/change/delete vs reload）
- [ ] 全局状态用 `AppStorageV2.connect` + `@ObservedV2` 类（不是 V1 `@StorageLink`）
- [ ] 持久化 + UI 响应用 `PersistenceV2.globalConnect`（不是 V1 `PersistentStorage.persistProp` + `@StorageLink` 双层）
- [ ] AppStorageV2 / PersistenceV2 的 key 拼写一致（建议常量化）
- [ ] 同一文件不混用 V1/V2 装饰器（如 `@Component` + `@ComponentV2`，`@State` + `@Local`）

---

## References

### V2 主参考（推荐，本项目实际使用）

- `references/v2-model-patterns.md` — 完整的 `@ObservedV2 + @Trace` Model 模式（带 fromJson、单例、嵌套、枚举、计算属性、表单验证）
- `references/v2-datasource-patterns.md` — V2 LazyDataSource / BasicDataSource / PaginatedDataSource / FilteredDataSource 完整实现 + Repeat 替代方案
- `references/v2-network-service.md` — V2 网络请求封装、拦截器、错误处理、AppStorageV2 / PersistenceV2 全局状态、离线降级 + 请求缓存

### V1 历史参考（仅老项目兼容查阅，已加 legacy 标识）

- `references/model-patterns.md` — V1 `@Observed` Model 模式
- `references/datasource-patterns.md` — V1 BasicDataSource + `@ObjectLink` 配合模式
- `references/network-service.md` — V1 网络请求封装、`@StorageLink` 全局状态

### 装饰器无关参考（V1/V2 通用）

- `references/rdbstore-dao-patterns.md` — RdbStore 单例初始化 + 建表模板 + ResultSet 解析 + DAO CRUD + 冲突处理策略
- `references/advanced-dao-patterns.md` — 多表 JOIN、ResultSet 安全、批量操作、ON CONFLICT
- `references/feed-update-service.md` — HTTP→XML→DB→EventBus 刷新管线

---

> 遇到版本兼容性或其他不确定的 ArkTS 知识点（如属性、语法、权限等），参阅 **arkts-knowledge-verifier** skill。状态管理装饰器细节参阅 **arkts-state-manager** skill。
