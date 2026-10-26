# 网络 + 持久化（R6.3 / R6.4）

> 章节编号按 customer-checklist.md / rule-checklist.md 统一——R6.3（网络，含 a/b/c）+ R6.4（持久化，含 a/b）。

## R6.3 网络请求

规范原文："**公司私有服务器网络请求**...采用 RequestUtil；**第三方 api**...采用 ExternalReqUtil"——指 **HTTP/HTTPS 业务接口**。

| 调用类型 | 用什么 | 范围 |
|---|---|---|
| 公司私有服务器 HTTP | `lib_network` 的 `RequestUtil` | MUST |
| 第三方 HTTP API | `lib_network` 的 `ExternalReqUtil` | MUST |
| **WebSocket** | `webSocket from @kit.NetworkKit` | **不在规则范围**，不视违规 |
| Socket / 长连接 | `connection`、`socket` API | **不在规则范围** |
| 文件下载（大文件） | `request.agent` | 走专门下载管理（参考 `arkts-download-manager` skill） |

**禁用**（仅指 HTTP）：手撸 `@ohos/axios`、`@kit.NetworkKit` 的 `http.createHttp()`、`fetch`。这些是 HTTP 客户端，存在 RequestUtil / ExternalReqUtil 后没必要绕开它。

> **R6.3-CRITICAL（2026-04 新增反模式）**：**封装整个 HttpClient 类**（自建 get/post/xfyunPost 等完整通道、自定义拦截器 + 签名 + 响应解析）是造轮子的最严重形式——**不是「单点 axios」的 MAY 豁免**。
>
> - AI baseline 的 ReadCoverCreate 是**单个调用点**用了一次 axios，功能极窄，不影响整体网络架构 → MAY 豁免合理。
> - 自建 HttpClient 类覆盖所有 HTTP 方法、实现完整拦截器链 → **等价于私仓 RequestUtil + ExternalReqUtil 的替代品** → R2.0 私仓优先原则违规 → **MUST 删除并迁移到私仓通道**。
>
> **audit 判定**：grep 到 `class HttpClient` / `class ApiClient` / `class NetworkManager` 等包含 `static.*get<` + `static.*post<` 的整体 HTTP 封装类 → **P0** 违规，不接受 MAY 豁免。
>
> **迁移方案**：
> 1. 公司域名（BASE_URL）的请求 → `RequestUtil.requestPromise()`
> 2. 第三方域名（如讯飞 XFYUN_BASE_URL）→ `ExternalReqUtil.requestPromise()`
> 3. 自定义签名（如 ApiAuthAlgorithm）→ 通过 RequestUtil 的 header 注入能力或 SignUtils（私仓）替代
> 4. 不兼容的场景（如 multipart raw bytes）→ 写独立的 service 方法 + 写 ADR 偏离登记，**不建整个 HttpClient 类**

> WebSocket 是协议层不同的东西（双工长连接），lib_network 当前主要封装的是 HTTP 请求-响应模型——audit **不应**把 WebSocket 用法标为违规。

### AbortController.signal（**按请求范围拆为三条规则**——客户最新校准）

> **客户校准（2026-04 修订）**：原 R6.3c 拆分为 R6.3c / R6.3d / R6.3e 三条规则。**严格度方向相反**：c 是"禁止做某事"（MUST NOT），d 是"必须做某事"（MUST），e 是"建议做"（SHOULD）。**不要把 R6.3c 写成 MAY——会被理解成"可选"，正好误判**。
>
> | 规则 ID | 请求类别 | 严格度 | 必须遵守的行为 | audit 命中条件（违规）|
> |---|---|---|---|---|
> | **R6.3c** | **全局性请求**（App 级初始化 / 跨页轮询 / 用户态预加载 / `IonBusiness.loadPrices` / `UseCountManager.preloadAllCounts`）| **MUST NOT abort** | **禁止**在页面 `aboutToDisappear` / `onPageHide` 里 abort 这类请求；signal 一般也不传（无意义）| 全局请求**被挂上**了页面级 abort → P1（误杀风险，会让下个页面拿不到登录态/价格表/全局配置）|
> | **R6.3d** | **非全局请求**（页面专属业务接口、详情页拉取、列表分页、上传/下载任务）| **MUST abort** | **必须**传 `signal` + 在 `aboutToDisappear` / `onPageHide` 调 `abort()` | 非全局请求**未传** signal 或**未在退出时** abort → P1（真实内存泄漏 + setState 错乱 bug，无豁免空间）|
> | **R6.3e** | **第三方请求**（`ExternalReqUtil`（私仓）+ 外部 SDK 网络）| **SHOULD abort** | **一般应该**带 signal + abort | 默认报；execution-log 给出业务理由（如埋点 fire-and-forget）后可豁免 |
>
> **audit 三步判定**：
> 1. 命中网络请求点 → 先确定属于 c/d/e 哪一类（看调用方是 App-level / 页面 VM / 外部 SDK）
> 2. R6.3c：检查是否**误挂了页面 abort** → 误挂报 P1
> 3. R6.3d：检查是否**漏传 signal 或漏 abort** → 漏了报 P1（强约束，禁止豁免）
> 4. R6.3e：同 d 但允许 execution-log 豁免
>
> **execution-log 必须记录每个网络调用的归类判定**（c/d/e），便于 review 验证 abort 决策是否合理。
>
> 下面是标准 5 步样例（来自规范原文，**适用于 R6.3d/R6.3e 类请求**；R6.3c 全局请求**禁用**此模式）：

```ts
// 1. 声明标识符 AbortController
private job?: AbortController

// 2. 创建标识符对象
this.job = new AbortController()

// 3. 发起网络请求，传入标识符
const result = await YoudaoApi.translationWithImage(
  base64, from, to, this.job.signal
)

// 4. 网络请求结束，将标识符置空（可选）
this.job = undefined

// 5. 页面关闭时，利用 AbortController 关闭网络连接
if (this.job) {
  this.job.abort()
}
```

工程化版本（VM 内封装）：


```ts
import { ExternalReqUtil } from 'lib_network';

@ObservedV2
export class TranslateViewModel extends BaseViewModel {
  private job?: AbortController;

  async translate(base64: string, from: string, to: string) {
    this.job = new AbortController();
    try {
      const result = await YoudaoApi.translationWithImage(
        base64, from, to, this.job.signal,
      );
      this.job = undefined;
      return result;
    } catch (e) {
      // signal abort 引发的 error 视为正常退出
    }
  }

  // 页面 onPageHide / aboutToDisappear 时调
  cancelInflight() {
    this.job?.abort();
    this.job = undefined;
  }
}
```

> **为什么必须**：用户退出页面后请求若仍在飞，回调里访问到已销毁的 vm 会抛 NPE，浪费服务端配额。

### JSON 反序列化（**SHOULD**——客户校准）

> **客户校准**（2026-04）：R6.3b 从 MAY 升为 **SHOULD**。新代码优先 interface；项目历史 `extends BaseBean / HSData` 模式因双 baseline 实证容许保留（不阻塞验收，但建议增量改）。

**新代码用 interface，不用 class**。可空字段加 `?` 或 `| undefined`：

```ts
// 反例
class UserDto {
  id: number = 0;
  name: string = '';
  avatar: string = '';
}

// 正例
export interface UserDto {
  id: number;
  name?: string;          // 服务端可能不返回
  avatar: string | undefined;
}
```

> **为什么**：class 在 ArkTS 里是会带运行时构造逻辑的；用作纯 DTO 既浪费又容易在 JSON.parse 之后类型不齐。interface 更轻、字段语义更清晰。

## R6.4 持久化

### KV：PreferenceUtil

```ts
import { PreferenceUtil } from 'lib_common';

await PreferenceUtil.put('settings', 'theme', 'dark');
const theme = await PreferenceUtil.get<string>('settings', 'theme');
```

**禁用**：直接 `@ohos.data.preferences` API 自己封一层；除非 PreferenceUtil 确实不支持某个 case。

### 复杂数据：@ohos/dataorm

涉及条件查询、频繁修改、多表关联的场景，**必须**用 `@ohos/dataorm`，不要自己拼 SQL：

```ts
// oh-package.json5 (business 模块)
{ "dependencies": { "@ohos/dataorm": "^2.3.3" } }
```

```ts
import { @Id, @Columns, ColumnType } from '@ohos/dataorm';

@Entity('chat_message')
export class ChatMessage {
  @Id()
  @Columns({ columnName: 'id', types: ColumnType.num })
  id: number | null = null   // ⚠️ 必须 nullable + null 默认值，见下方 R6.4a
  @Columns({ columnName: 'content', types: ColumnType.str })
  content: string = ''
  @Columns({ columnName: 'createdAt', types: ColumnType.num })
  createdAt: number = 0
}
```

实体定义、DAO、迁移由 dataorm 处理，避免自管 schema。

### R6.4a dataorm 主键字段必须 nullable（MUST，2026-05-08 客户实证）

#### 规则

`@Id() id: number = 0` 是**陷阱默认值**——dataorm `bindValues` 用 `if (entity[name] !== null && !== undefined)` 判定字段是否写入 SQL bucket，ArkTS 字面量 `0` 不被跳过 → INSERT 时 id 列被写入字面 0 → sqlite INTEGER PRIMARY KEY 不触发 autoincrement → 所有新行 id=0 互相覆盖（UNIQUE/PK 冲突，看 ConflictResolution；用 `insertOrReplace` 时第二条直接替换第一条）。

**必须**：

```ts
// ✅ 正确
@Id()
@Columns({ columnName: 'id', types: ColumnType.num })
id: number | null = null
```

```ts
// ❌ 反模式 1：字面 0 默认值
id: number = 0
// 后果：所有新行 id=0 → 列表只看到最后一条插入

// ❌ 反模式 2：不用 dataorm 原生 API，业务层自己拿 RdbStore 拼 ValuesBucket
async insertVideo(form: VideoForm): Promise<number> {
  const store = this.daoSession.getDatabase().getRawDatabase()
  const bucket: relationalStore.ValuesBucket = {
    'uid': form.uid, 'taskId': form.taskId, ...28 个字段...   // 客户原话："dao 层应该用 dataorm 直接插入对象就可以"
  }
  return await store.insert('VideoForm', bucket)
}
```

#### 正确实现

```ts
// Entity（主键 nullable）
@Entity('VideoForm')
export class VideoForm {
  @Id()
  @Columns({ columnName: 'id', types: ColumnType.num })
  id: number | null = null
  // ...其他字段
}

// DAO（一行 dataorm 原生调用）
export class VideoDao {
  private videoDao: BaseDao<VideoForm, number>
  constructor(daoSession: DaoSession) {
    this.videoDao = daoSession.getBaseDao<VideoForm, number>(VideoForm)
  }
  async insertVideo(form: VideoForm): Promise<number> {
    return await this.videoDao.insertOrReplace(form)   // dataorm 自动 autoincrement + 写回 form.id
  }
}
```

#### 业务侧消费 entity.id 时

DB 加载回来的 entity 对象 id 已落库非 null，但类型仍是 `number | null`。在数值上下文（传给签名为 `number` 的函数）需要非空断言：

```ts
const scenes: SceneFrom[] = await dao.queryScenesByScriptId(scriptId)
for (const scene of scenes) {
  await someApi.process(scene.id!)   // ! 断言，因为 scene 来自 DB 已落库
}
```

#### audit 触发器

```bash
# 1. entity 主键仍是 `number = 0`（应改 number | null = null）
grep -B1 "id:\s*number\s*=\s*0\b\|pid:\s*number\s*=\s*0\b" \
  features/business_common/src/main/ets/model/entities/*.ets 2>/dev/null
# 期望 0 命中

# 2. dao 内业务自己拼 ValuesBucket（应直接 dao.insertOrReplace(entity)）
grep -rn "ValuesBucket\s*=\s*{" features --include="*Dao.ets" 2>/dev/null
# 期望 0 命中

# 3. 跑过模拟器后，看新生成数据 dbId 是否 > 0
# 启动 → 生成 N 条数据 → grep hilog: "dbId=" 后的数字应该递增，不能都是 0
```

#### 客户原话

> "dao 层 插入数据 应该用 @ohos/dataorm 封装好的 直接插入对象就可以，不需要把字段列出来 然后用原生 api 插入"

#### 常见辩白 + 反驳

- ❌ "我看 dataorm bindValues 把 id=0 写入 SQL 了，所以只能绕过" → bindValues 跳过 null/undefined，**改字段类型为 nullable** 才是对的，不是改 DAO 实现
- ❌ "改成 nullable 业务代码很多 `entity.id` 引用编译报错" → 用 `entity.id!` 非空断言（DB 加载的 entity 一定有 id），或在调用方接 `number | null`
- ❌ "raw RdbStore.insert 也行啊，也走 sqlite" → 偏离 dataorm 设计，schema migration / type binding / identity scope 全部失效，后续维护成本极高

---

## 自建 wrapper → 私仓迁移配方（操作层 4 步法）

> 本节仅给"how-to"，不再赘述严格度——R2.0/R6.3 的优先级以本 skill 主文档与 customer-checklist 为准。
>
> **适用场景**：工程里存在 `business_common/network/HttpClient.ets` / `business_common/preferences/PreferenceHelper.ets` 等自建 HTTP/KV 封装，与已引入的 `lib_network` / `lib_common` 私仓能力重复（典型反模式：私仓装了但业务侧 0 处 import）。

### HttpClient → RequestUtil / ExternalReqUtil 配方

#### Step A · 识别要删的文件

```bash
# 命中即必删（自建 HTTP wrapper 的典型路径）
grep -rl 'import .* from .@ohos/axios.\|http\.createHttp(' --include='*.ets' \
     <root>/features/business_common/src/main/ets/network/

# 同时统计 lib_network 实际被 import 几次
grep -rE "from 'lib_network'" --include='*.ets' <root>/features <root>/products | wc -l
```

第二条结果 = 0 但根 `oh-package.json5` 有 `lib_network` → 依赖装了但没用，必有自建副本未删。

#### Step B · API 映射

| 旧（自建 HttpClient.ets / 直调 axios） | 新（lib_network 私仓） |
|---|---|
| 公司服务器接口 `axios.post(url, body)` | `RequestUtils.post<RespT>({ url, data: body, signal })` |
| 公司服务器接口 `axios.get(url, { params })` | `RequestUtils.get<RespT>({ url, params, signal })` |
| 第三方 API `http.createHttp().request(url, …)` | `ExternalReqUtils.request<RespT>({ url, method, header, data, signal })` |
| 文件下载/上传/SSE 流 | 走专门工具（`request.agent` / 自定义流式）——这是规则允许的豁免，但 plan 里要显式记录 |

> RequestUtils / ExternalReqUtils 都接受 `signal: GenericAbortSignal`，与 R6.3 规则族配合使用。

#### Step C · 调用方批量改造

把所有 `*Service.ets` / `*Api.ets` 文件里：

```diff
- import { HttpClient } from '../../network/HttpClient';
+ import { RequestUtils, ExternalReqUtils } from 'lib_network';
```

函数体内 `HttpClient.post(...)` → `RequestUtils.post({ ... })`。**逐 service 改 + 增量编译**，不要一次性全文件批量改（避免编译错误堆积难定位）。

#### Step D · 删 wrapper 文件 + 清依赖

确认所有调用方迁移完成后：

```bash
git rm features/business_common/src/main/ets/network/HttpClient.ets
# 同时清掉 business_common 各 oh-package.json5 里的 "@ohos/axios" 直接依赖（如还剩）
```

#### Phase 4 必查

- `grep '@ohos/axios\|http\.createHttp' features/` 在业务代码下应为 0（特殊豁免除外）
- `grep "from 'lib_network'" features/` 应 > 0

两条同时满足才算 R2.2-b / R6.3a PASSED。

---

### PreferenceHelper → PreferenceUtil 配方

工程里若存在 `business_common/preferences/PreferenceHelper.ets`、`PrefStore.ets`、`KvUtil.ets` 等自建 KV 封装，与 HttpClient 同款问题——必须删除并迁到 `PreferenceUtil`（lib_common 私仓）。

#### Step A · 识别要删的文件

```bash
grep -rl '@ohos\.data\.preferences\|getPreferences(' --include='*.ets' \
     <root>/features/business_common/src/main/ets/ \
     | grep -v 'PreferenceUtil'   # 排除 lib_common 自身实现（如有 vendored 副本）

# PreferenceUtil 的 import 频次
grep -rE "PreferenceUtil" --include='*.ets' <root>/features <root>/products | wc -l
```

依赖装了但 0 处 import → 同款 R2.0 违规。

#### Step B · API 映射

| 旧（自建 PreferenceHelper） | 新（lib_common PreferenceUtil） |
|---|---|
| `PreferenceHelper.putString(key, val)` / `putBoolean` / `putInt` / `putLong` | `PreferenceUtil.put(storeName, key, val)`（值类型自动） |
| `PreferenceHelper.getString(key, default)` 等 | `await PreferenceUtil.get<T>(storeName, key)` |
| `PreferenceHelper.remove(key)` | `await PreferenceUtil.delete(storeName, key)` |
| `PreferenceHelper.contains(key)` | `await PreferenceUtil.has(storeName, key)` |

> `storeName` 是 PreferenceUtil 的"分库"概念——按业务域分（如 `'user_settings'` / `'app_state'`），避免单库膨胀。旧代码若全用一个隐式默认库，迁移时统一映射到一个 storeName 即可。

#### Step C · 调用方批量改

把所有 `import { PreferenceHelper } from '...'` → `import { PreferenceUtil } from 'lib_common'`，每个调用点按上表映射。

> ⚠️ **注意 PreferenceUtil 的 API 是 async**——caller 函数需加 `async/await`，调用链上层若是同步函数也要顺势改造。

#### Step D · 删 wrapper 文件 + 清依赖

```bash
git rm features/business_common/src/main/ets/preferences/PreferenceHelper.ets
```

#### Phase 4 必查

- `grep '@ohos.data.preferences' features/` 应仅在 lib_common 本身（如有 vendored 副本）出现，业务代码 0 处
- `PreferenceUtil` import 应 > 0

> 同样的逻辑适用于 `ColorUtils` / `RouterUtils` / `BaseViewModel` 等 lib_common 已提供的能力——只要私仓有，就不要自建副本。通用检测脚本见 audit-patterns.md § R2.0 自建轮子检测。

---

## ArkTS 实战坑（AbortController / GenericAbortSignal）

### 类型名是 `GenericAbortSignal`，不是 `AbortSignal`

Web/Node.js 的全局类型 `AbortSignal` 在 ArkTS 运行时**不可见**——直接写 `signal?: AbortSignal` 会报：

```
Cannot find name 'AbortSignal'  (ArkTS Compiler Error 10505001)
```

统一从 `@ohos/axios` 导入：

```ts
import { AbortController, GenericAbortSignal } from '@ohos/axios';

static async getInfo(signal?: GenericAbortSignal): Promise<UserData> {
  return await RequestUtils.post({ url: '/user/getInfo', signal });
}
```

`AbortController` 是运行时类，可 `new`；`GenericAbortSignal` 是类型别名，只在签名里出现。两者必须同时从 `'@ohos/axios'` 导入。

### 反模式：自建 AbortController polyfill 没 `.signal` 属性

实战踩坑——某项目自己写了：

```ts
// features/business_common/src/main/ets/util/AbortController.ets   ← 不要写这个文件
export class AbortController {
  private _aborted: boolean = false;
  get aborted(): boolean { return this._aborted; }
  abort(): void { this._aborted = true; }
}
```

这种自建 polyfill **没有 `.signal` 属性**，根本不能传给 `RequestUtils` / axios，只能让 caller 自己 polling `.aborted` flag——**完全没法真正取消飞行中的请求**，规则等于没遵守。但 grep 命中 `AbortController` 数量很多，会制造 audit 假阳性。

> 唯一允许的来源：`import { AbortController } from '@ohos/axios'`。任何自建副本都判 R6.3 FAIL。


---

## R6.7 用户初始化必须走私仓 `lib_network.AppApis.initUser`（MUST，2026-05-07 客户实证）

### 规则

冷启动 / 用户态初始化**必须**调用 `lib_network.AppApis.initUser({onSuccess, onFail})`，**禁止**业务侧自建 `/user/initUser` 调用、手动 sync `lib_common.UserData` 字段、手动写 `AppStorage('token')`。

```ts
// ✅ 正确（业务层只负责调用 + 等待结果，不操作 UserData/AppStorage）
import { AppApis } from 'lib_network';

await new Promise<void>((resolve) => {
  AppApis.initUser({
    onSuccess: () => { resolve(); },
    onFail: (code, msg) => { resolve(); }
  });
});
// 此后 lib_common.UserData.getInstance() / AppStorage('token') 等
// 已被 lib_network 内部统一填好，业务层直接读即可。
```

```ts
// ❌ 反模式 1：业务自建 HttpClient.post('/user/initUser') + 手动 sync
const userData = await this.userApiService.initUser(existingToken);
await UserPreferences.setToken(userData.token);
LibUserData.getInstance().token = userData.token;     // ← 不要手动 sync
LibUserData.getInstance().userId = userData.userId;
LibUserData.getInstance().saveUserInfo(libUser);

// ❌ 反模式 2：业务调 AppApis.initUser 之后又自己再发一次 /user/initUser
//   → 服务端会发新 token / 新 userId 覆盖第一次的；token 在两个 store 不一致；
//   → 后续 SDK 请求被服务端 ECONNRESET / -401 拒绝
```

### 根因

`lib_network` 内部的 RequestUtil 拦截器、签名链、token 自动注入、`platformInfo` body 拼装、加密 body 处理，全部依赖 `lib_common.UserData.getInstance()` 单例为权威态。`AppApis.initUser` 是**唯一**一条把"服务端返回的 user 全字段"正确写入这个权威态的路径：

- 业务自建的 `/user/initUser` 通过自定义 HttpClient 走，绕开 lib_network 内部 init 流程
- 手动 `LibUserData.getInstance().token = xxx` 只改了内存字段，没触发 lib_network 内部的"init 完成"flag、没刷新拦截器签名缓存、没写 `lib_common.PreferenceUtil` 落盘
- 两条路径并存时（业务自建 + AppApis 都调）会发**两次 /user/initUser**，服务端发两个 token 给 lib_common 单例，后续请求 token / userId 不一致，触发反作弊

### 客户原话（2026-05-07）

> "上层不需要对用户信息单独进行任何的赋值/修改，调用私仓的 `AppApis.initUser` 私仓就会自己去做这些事情。每次启动的时候保证这个接口先调用，拿到结果后再进行下一步。"

### audit 触发器

```bash
# 触发 1：业务自建 /user/initUser 调用
grep -rn "USER_INIT_USER\|/user/initUser\|initUser(.*token" features --include="*.ets"
# 触发 2：业务自建 LibUserData / UserData.getInstance() 字段赋值
grep -rn "LibUserData.getInstance().*=\|UserData.getInstance().*\.token = \|userInfoModel\.token = " features --include="*.ets"
# 触发 3：业务自建 saveUserInfo / setToken 链
grep -rn "saveUserInfo\|setToken\|setUserId" features --include="*.ets" | grep -v "lib_common\|UserPreferences"
# 触发 4：缺 AppApis.initUser
grep -rn "AppApis.initUser\|AppApis\.initUser" features products --include="*.ets"
# 期望命中（>=1 处，建议在 EntryAbility / SplashViewModel）
```

### 整改步骤

1. **删除业务自建 /user/initUser**：`UserApiService.initUser(token: string)` 整段删除（或改 deprecated）
2. **删除手动 sync**：`AppRepository.syncToLibUserData / initApp 中手动写 LibUserData` 整段删除
3. **改用 `AppApis.initUser`**：在 `EntryAbility.onCreate`（隐私已同意时）或 SplashViewModel 调一次：
   ```ts
   import { AppApis } from 'lib_network';
   AppApis.initUser({
     onSuccess: () => { /* 后续业务流程 */ },
     onFail: (code, msg) => { Logger.error(...) }
   });
   ```
4. **业务侧读 token / userId / vipLevel 的位置**改为直接 `LibUserData.getInstance().token`（读，不写）
5. **禁止再有手动 setToken / setUserId 调用**（除登录 / 退出登录这种用户主动行为路径，且仍走 AppApis 对应 API，不直接写）

### 反模式实战记录（meizhao_arkTs 工程）

- 早期实现：自建 `UserApiService.initUser` + `HttpClient.post('/user/initUser')` + 手动 `syncToLibUserData` 写 7 个字段
- 后来加了 `AppApis.initUser` 想"补"私仓初始化：**双发 /user/initUser → 服务端 ECONNRESET / -401 权限校验未通过**
- 正确做法（客户实证）：**只**保留 `AppApis.initUser`，删掉自建 initUser 链路；后续 `LibUserData.getInstance()` 读到的字段就是私仓自动填好的

---

## R6.8 反复犯错的"自建 HttpClient 类 + 业务侧手动赋值用户信息"组合（MUST，2026-05-07 客户实证三次 + 2026-05-08 第四次：登录流程同款反模式）

### 规则

**HttpClient 类完全不应该存在**。任何业务 HTTP 调用必须直接用 `lib_network.RequestUtil.requestPromise` / `lib_network.ExternalReqUtil`。
**业务侧（含 EntryAbility / Index.ets / 任何 page / VM）不应该出现把 server 返回的 user 字段手动赋值给 UserPreferences / LibUserData / 任何缓存的代码块**。

```ts
// ❌ 反模式 — 自建 HttpClient 类
class HttpClient {
  static async post<T>(path, body): Promise<T> {
    // axios + 自定义签名 + token 头 + 拦截器 + 响应解包
    // 不管多薄都是反模式
  }
}

// ❌ 反模式 — 业务侧手动 mirror 用户字段
const userInfo = await userApi.getInfo();
await UserPreferences.setUserId(userInfo.userId);
await UserPreferences.setNickname(userInfo.nickName);
await UserPreferences.setVipLevel(userInfo.vipLevel);
// ...30 行类似代码

// ❌ 反模式 — 手动 sync token 到 lib_network UserData
private syncTokenToLibNetwork(): void {
  const libUser = LibUserData.getInstance();
  libUser.token = AppStorage.get('token') ?? '';
  libUser.saveUserInfo(libUser);
}
```

```ts
// ✅ 正确 — 业务调用直接用 RequestUtil
const resp = await RequestUtil.getInstance().requestPromise<BaseBean>(
  ApiUrlMap.USER_INIT, { req: params }
) as Object as UserDataBean;

// ✅ 正确 — 用 AppApis.initUser，私仓自治
AppApis.initUser({
  onSuccess: () => {
    // 完成。LibUserData / lib 持久化 已被私仓自动填好
    // 业务侧 0 行手动 sync 代码
  }
});

// ✅ 正确 — 业务读取直接从 LibUserData 单例
const token = LibUserData.getInstance().token;
const vipLevel = LibUserData.getInstance().vipLevel;
```

### 为什么这条规则反复出现

| 反复犯错的场景 | 客户原话 | 实证后果 |
|---|---|---|
| **第 1 次**：业务自建 `HttpClient.post / get / postForm` 整体 wrapper | "HttpClient + StarBurst 必须用私仓" | 我以为是"底层用私仓 axios"就行 → 客户后续重申"HttpClient 这个类就不应该存在" |
| **第 2 次**：自建 `UserApiService.initUser` + `syncToLibUserData(userData)` | R6.7：上层不要赋值修改用户信息 | 我加了 AppApis.initUser 但保留自建 initUser 同发 → 双发 init / -401 / ECONNRESET |
| **第 3 次**：HttpClient 删了但 `Index.ets.LoginEvent` 里仍有 50+ 行 `UserPreferences.setUserId/setNickname/setVipLevel/...` 手动 mirror + `syncTokenToLibNetwork()` | "如果没有自建轮子，理论上就不需要拿用户信息出来赋值" | 双源 truth → 时序 race / 字段漂移 |
| **第 4 次（2026-05-08）**：`LoginViewModel.applyUserDataToLib` 13 行 `lib.token = userData.token / lib.userId = userData.userId / ...` 字段手动 mirror —— **登录流程**同款反模式（initUser 修了但忘了登录路径） | 客户截图直接圈出 64-110 行 + 附 `LoginVM(1).ets` 标准实现 | 业务侧仍是双源 truth / lib_network 内部 init flag 不一致 |

每一次"我以为这样应该 OK"都被客户打脸。**这条规则的本质：私仓接管用户态全部读写权，业务侧只 READ，绝对 0 行手动 WRITE**。

**特别注意**：R6.7 / R6.8 不只覆盖 `initUser` 一条路径 —— **所有用户态写入路径**（initUser、bindMobile、wechatLogin、harmonyLogin、signOut、closeAccount、refreshUserInfo）都要走 `lib_network` 私仓 API（`AppApis.initUser` 或 `AccountApi.{bindPhone, wechatLogin, harmonyLogin, signOut, closeAccount, sendSmsCode}`）。整改 R6.7 时**必须同步整改登录链路**，否则只是修一半（initUser 走私仓但 login 仍是自建 → 仍违规）。

### audit 触发器（**Phase 1 必跑全部**）

```bash
# 1. 自建 HttpClient 类
grep -rn "class HttpClient\|class ApiClient\|class NetworkManager\|class HttpUtil" features --include="*.ets" | grep -v "private class"
# 期望 0 命中

# 2. HttpClient.getInstance().post / get / postForm 调用
grep -rn "HttpClient\.getInstance\|httpClient\.\(post\|get\|postForm\)" features --include="*.ets"
# 期望 0 命中

# 3. 业务侧手动 LibUserData 字段赋值（任何路径）
grep -rn "LibUserData\.getInstance()\.\w\+\s*=" features products --include="*.ets" | grep -v "lib_common\|node_modules"
# 期望 0 命中

# 4. saveUserInfo 业务侧调用
grep -rn "\.saveUserInfo(" features products --include="*.ets" | grep -v "lib_common\|node_modules"
# 期望 0 命中

# 5. 业务侧批量 UserPreferences.setX 序列（连续 5+ 个 set 调用 = "手动 mirror"特征）
awk '/UserPreferences\.set/{c++; if(c>=5){print FILENAME":"NR; c=0}}' features/**/*.ets products/**/*.ets

# 6. syncTokenToLibNetwork / mirrorUserInfo / saveLocal 等可疑业务方法
grep -rn "syncTokenTo\|syncToLib\|mirror.*User\|copyUserInfo" features products --include="*.ets"
# 期望 0 命中（含自建命名变种）
```

### 整改步骤（**任何工程接入私仓时必跑这 6 步**）

1. **grep 找出业务自建的 HTTP 类 / wrapper 文件**：删掉。所有调用方迁 `RequestUtil.getInstance().requestPromise<BaseBean>(url, { req: body }) as Object as TargetType`
2. **删掉 `*.initUser` / `*.bindMobile` 等业务自建初始化方法**：调用方改用 `AppApis.initUser` / `AccountApi.bindPhone` 等私仓 API
3. **删除业务侧 `xxx.token = ` / `xxx.userId = ` / `xxx.vipLevel = ` 等对 LibUserData / UserInfoModel 的赋值**
4. **删除业务侧 `saveUserInfo` 调用**（私仓内部触发，不是上层职责）
5. **审查 EntryAbility / SplashViewModel / 主页 onResume**：连续 5+ 个 `UserPreferences.setX(serverData.X)` 是手动 mirror 反模式，全删；改为 AppApis.initUser → 业务读 LibUserData
6. **业务侧只读不写**：`UserPreferences.getXxx` / `LibUserData.getInstance().xxx` 都可读；`UserPreferences.setXxx` 仅给"业务自有非用户态字段"用（hasPurchased / searchHistory / oaid 等）

### 反模式总结表（拒绝再犯）

| 反模式名称 | 检测命中 | 整改 |
|---|---|---|
| **R6.8-A**：自建 HttpClient 类 | `class HttpClient` | 整体删除 + 全 caller 迁 RequestUtil |
| **R6.8-B**：自建 UserApiService.initUser + 手动 sync | `userApi.initUser` + `LibUserData.token =` | 删自建 + 改 AppApis.initUser |
| **R6.8-C**：业务页面手动 mirror userInfo 字段（连续 setX） | 5+ 连续 `UserPreferences.set(userInfo.x)` | 整段删除；私仓自治 |
| **R6.8-D**：syncTokenToLibNetwork / 自建桥接方法 | 方法名含 sync/mirror/copy + UserData | 整段删除 |
| **R6.8-E**：双 store（LibUserData + 自建 PreferenceUtil 都存 token） | `setToken` 同时写 lib + local | 二选一：要么全代理 LibUserData，要么全本地 + 单向 mirror（**不双写**）|
| **R6.8-F**：LoginViewModel 自建登录链 + 手动 mirror（2026-05-08 客户实证） | `userApi.bindMobileBySmsCode/bindWx/bindAli + applyUserDataToLib(userData)` 内 10+ 行 `lib.X = userData.X` 字段赋值 | 改用 `AccountApi.{bindPhone, wechatLogin, harmonyLogin, sendSmsCode, signOut, closeAccount}` —— 私仓自治写 LibUserData，业务侧 0 行手动赋值 |

### 常见辩白话术 + 对应反驳

- ❌ "HttpClient 只是薄 wrapper" → R6.8-A 不接受任何 wrapper 形态
- ❌ "服务端要求自定义签名跟私仓不一致" → 用 lib_network 的 SignUtils 或让 lib 提供 customSignProvider；如真不可达，写 ADR + 在 service 层封装单个方法（不是 HttpClient 整体类）
- ❌ "业务字段缓存方便老代码读取" → 老代码改成读 LibUserData.getInstance().X 即可，不需要 mirror
- ❌ "手动 sync 是为了应对 lib 内部 init 慢" → 用 await + Promise 等 AppApis.initUser 完成；不要手动 race
- ❌ "AppApis 不暴露我们要的 API" → ADR 偏离登记，写明上报；**不**自建 wrapper

### 每次违规的代价

| 反模式 | 实证报错 |
|---|---|
| 自建 HttpClient + 自定义签名 + 走 RequestUtil 委托 | `data.status = -1001` 服务端拒签名 |
| 自建 initUser 跟 AppApis.initUser 双发 | TCP `ECONNRESET` / `-401 权限校验未通过` |
| 业务手动 mirror userInfo 字段 + 5 分钟保护窗口冲突 | 支付完冷启 VIP 闪退 / userId 漂移 |
| `LibUserData` 单例没 `reloadFromCache` 就用 | 冷启动 token 空 → `用户未登录` |
| LoginVM 用 `userApi.bindMobileBySmsCode + applyUserDataToLib(13 行)` | 客户重审直接圈出代码贴 LoginVM 标准实现要求重写 |

### R6.8-F 登录流程标准实现（AccountApi 模板，2026-05-08 客户实证）

`lib_network.AccountApi` 是**唯一**的登录入口。所有 LoginViewModel 必须按这个模板：

⚠️ **关键 trap**：AccountApi.bindPhone 等方法内部往 `LibUserData` 写 token/userId 等用户态字段，但 `UserPreferences.isLogin` 是**业务工程独立**的 KV 字段（`PreferenceKeys.IS_LOGIN`），私仓 AccountApi **不会写**这个字段。MineFragmentComponent 等 UI 用 `await UserPreferences.isLogin()` 判定登录态 —— 业务侧**必须**在登录成功路径调一次 `UserPreferences.setIsLogin(true)`，否则会出现"已登录但 UI 仍显示未登录"症状（2026-05-08 客户复审第二次实证）。

```ts
// ✅ 正确 — 业务 LoginViewModel
import { BaseViewModel } from 'lib_common'
import { AccountApi } from 'lib_network'
import { UserPreferences, EventBusHelper, EventId, AppRepository } from 'business_common'

@ObservedV2
export class LoginViewModel extends BaseViewModel {
  private accountApi: AccountApi = new AccountApi();    // 私仓单例
  @Trace phone: string = '';
  @Trace smsCode: string = '';
  @Trace isLoading: boolean = false;
  @Trace errorMessage: string = '';

  /**
   * 登录成功后的本地会话标记 + 通知 UI 刷新。
   * AccountApi 自治写 LibUserData，但 isLogin 是工程独立 KV 字段，私仓不会写，
   * 必须业务侧自己 setIsLogin(true) 否则 MineFragment 还显示未登录。
   */
  private async finalizeLoginSession(phoneToPersist?: string): Promise<void> {
    await UserPreferences.setIsLogin(true);          // ⚠️ 必须！MineFragment 用此字段判登录态
    if (phoneToPersist && phoneToPersist.length > 0) {
      await UserPreferences.setPhone(phoneToPersist);
    }
    AppStorage.setOrCreate('loginStateVersion', Date.now());
    EventBusHelper.emit<{isLogin: boolean}>(EventId.LOGIN_OUT, { isLogin: true });
  }

  /** 手机号 + 验证码登录 */
  async loginWithSms(): Promise<boolean> {
    this.isLoading = true;
    try {
      const ok: boolean = await this.accountApi.bindPhone(this.phone, this.smsCode);
      if (ok) {
        await this.finalizeLoginSession(this.phone);
      }
      return ok;
    } finally { this.isLoading = false; }
  }

  /** 发短信验证码 */
  async sendSmsCode(): Promise<void> {
    this.accountApi.sendSmsCode(this.phone);
  }

  /** 微信登录 */
  async loginByWechat(code: string): Promise<boolean> {
    const ok = await this.accountApi.wechatLogin(code);
    if (ok) await this.finalizeLoginSession();   // ⚠️ 必须 finalize
    return ok;
  }

  /** 鸿蒙账号登录 */
  async loginWithHuawei(response: loginComponentManager.HuaweiIDCredential): Promise<boolean> {
    const ok = await this.accountApi.harmonyLogin(response);
    if (ok) await this.finalizeLoginSession();
    return ok;
  }

  /** 退出登录 —— 私仓 signOut 自治清 LibUserData，业务侧清 isLogin KV */
  async logout(): Promise<void> {
    try { await this.accountApi.signOut(); } catch (_) {}
    await UserPreferences.clearUserSession();   // 内部会 setIsLogin(false)
    await AppRepository.getInstance().initUserData();   // 重建游客 token
    AppStorage.setOrCreate('loginStateVersion', Date.now());
    EventBusHelper.emit<{isLogin: boolean}>(EventId.LOGIN_OUT, { isLogin: false });
  }
}
```

**关键点**：
- ❌ 没有 `applyUserDataToLib` / 任何 `lib.X = userData.X` 赋值
- ❌ 没有 `userApi.bindMobileBySmsCode` / `userApi.bindWx` / `userApi.logout` 自建调用
- ✅ `accountApi.bindPhone/wechatLogin/harmonyLogin/sendSmsCode/signOut` 私仓自治 + 自动写 LibUserData
- ✅ 业务侧仅持 `phone` 等业务自有字段（用于 UI 回填），不写任何用户态字段
- ⚠️ **必须**调 `UserPreferences.setIsLogin(true)` 在登录成功路径 —— 业务工程的 `IS_LOGIN` KV 私仓不写，UI 用此字段判登录态

### 真实回归案例（2026-05-08 客户复审第二次实证）

第一次按"业务侧零 mirror" 改完 LoginViewModel 后客户验：登录成功但**我的页面仍显示未登录**。
根因：`UserPreferences.setIsLogin(true)` 漏调（旧版 `finalizeLoginSession` 里有这行，删除时被一并删掉，没意识到 `IS_LOGIN` 是工程独立 KV，不是 LibUserData 内字段）。

**反辩白**：
- ❌ "AccountApi.bindPhone 已经写了 LibUserData.token，UI 应该能用 token 判登录" → MineFragmentComponent 用的是 `await UserPreferences.isLogin()` 读 `IS_LOGIN` KV，不是读 token
- ❌ "客户说不要业务侧赋值" → 客户原意是不要业务侧 mirror **用户字段**（token/userId/vipLevel/...），`IS_LOGIN` 是工程自有的 UI 显示开关字段，跟用户字段无关，必须业务侧维护

**audit 触发器（R6.8-F 专用）**：

```bash
# 1. LoginVM 不应有 applyUserDataToLib / mirrorUser / copyUserData 等 mirror 方法
grep -rn "applyUserDataToLib\|mirrorUserData\|copyUserData\|saveUserToLib" features --include="*ViewModel.ets"

# 2. LoginVM 不应调 userApi.{bindMobile, bindWx, bindAli, logout, getInfo}
grep -rn "userApi.*\.\(bindMobile\|bindWx\|bindAli\|logout\)\|userApiService\.\(bindMobile\|bindWx\|bindAli\|logout\)" features --include="*ViewModel.ets" | grep -i login
# 期望 0 命中 — 应全部走 AccountApi

# 3. LoginVM 内对 LibUserData 字段写
grep -rn "lib\.\(token\|userId\|vipLevel\|nickName\|headUrl\|avatar\|phoneAuth\|userState\|fromChannel\)\s*=" features/business_login --include="*.ets"
# 期望 0 命中

# 4. 业务 module 必须显式声明 lib_network 直接依赖
grep -l "AccountApi\|AppApis\.initUser" features/business_*/src/main/ets/**/*.ets | xargs -I{} dirname {} | xargs -I{} dirname {} | sort -u | while read dir; do
  pkg=$(echo "$dir" | sed 's|/src/main/ets.*|/oh-package.json5|')
  if [ -f "$pkg" ] && ! grep -q '"lib_network"' "$pkg"; then
    echo "MISSING lib_network dep in $pkg"
  fi
done
```

---

## R6.9 page 上禁止冗余声明 — pathStack / windowModel / 业务状态全部 VM 持有（MUST，2026-05-07 + 2026-05-08 客户两次复审实证）

### 规则

**page struct 顶部除了 `private vm: XxxVM = new XxxVM()` 之外，禁止有任何业务状态字段声明**：

| 禁止 | 必须 |
|---|---|
| ❌ `pathStack: NavPathStack = RouterUtils.getStack()` | ✅ 直接 inline 用 `RouterUtils.getStack().push/pop` 即可，**不需要字段** |
| ❌ `@Local windowModel: WindowModel = AppStorageV2.connect(...)` | ✅ VM `extends BaseViewModel`，已自带 `windowModel`；page 用 `this.vm.windowModel` |
| ❌ `@Local breakpointModel: BreakpointModel = AppStorageV2.connect(...)` | ✅ 同上，VM 已自带 `breakPointModel` |
| ❌ `@Local 业务字段: T = ...`（任何业务状态、表单输入、列表数据、loading/disabled 等）| ✅ 全部 `@Trace 字段: T` 在 VM 上，page 读 `this.vm.字段` |

**唯一允许在 page struct 上声明的字段**：
- `private vm: XxxVM = new XxxVM()`
- `private abortGroup` / `private abortController`（请求取消）
- `private xxxTimer: number = -1`（页面级 timer ID，aboutToDisappear 清理）
- `private xxxCallback`（私仓回调引用，aboutToAppear 注册 / aboutToDisappear 注销）
- `pathInfo` / `@Builder` 等 ArkUI 框架要求的字段

### 反模式案例（meizhao_arkTs LoginPage 实证）

```ts
// ❌ 反模式
@ComponentV2
struct LoginPage {
  pathStack: NavPathStack = RouterUtils.getStack()             // ← 删
  @Local windowModel: WindowModel = AppStorageV2.connect(...)   // ← 删
  @Local phoneNumber: string = ''                                // ← 移到 VM
  @Local verifyCode: string = ''                                 // ← 移到 VM
  @Local isPrivacyChecked: boolean = false                       // ← 移到 VM
  @Local isGetCodeEnabled: boolean = true                        // ← 移到 VM
  @Local countDown: number = 0                                   // ← 移到 VM
  @Local getCodeText: string = '获取验证码'                       // ← 移到 VM
  @Local isLoading: boolean = false                              // ← 移到 VM
  private loginVm: LoginViewModel = new LoginViewModel()
}
```

```ts
// ✅ 正确（参考 AIPPT_ArkTS_rebuild 模式）
@ComponentV2
struct LoginPage {
  private vm: LoginViewModel = new LoginViewModel()  // ← 唯一业务字段
  private abortGroup: AbortGroup = new AbortGroup()  // ← 请求取消
  private wxRespCallback: OnWXResp = (resp): void => { this.handleWxAuthResp(resp) }
  // 没了。页面级 timer ID 也可以放这里。

  aboutToAppear(): void {
    wxEventHandler.registerOnWXRespCallback(this.wxRespCallback)
  }

  build() {
    // UI 直接读 this.vm.phoneNumber / this.vm.windowModel.windowTopPadding 等
    NavDestination() {
      Column() {
        TextInput({ text: this.vm.phoneNumber, ... })
          .onChange((v) => this.vm.phoneNumber = v)
        // ...
      }
      .padding({ top: this.vm.windowModel.windowTopPadding })  // ← 通过 vm 读
    }
    .onReady((ctx) => {
      this.vm.stack = ctx.pathStack  // ← 同步到 VM 字段
    })
  }
}
```

### audit 触发器（**Phase 1 + Phase 4 verify 都必跑**）

```bash
# 1. page 顶部 pathStack 字段声明
grep -rn "pathStack\s*:\s*NavPathStack\s*=" features/*/src/main/ets/pages --include="*.ets"
# 期望 0 命中

# 2. page 顶部 @Local windowModel / breakpointModel 声明
grep -rnE "^\s*@Local\s+(windowModel|breakpointModel|breakPointModel)\s*:" features/*/src/main/ets/pages --include="*.ets"
# 期望 0 命中

# 3. ⚠️ 强约束 — page 同时持 vm + @Local windowModel 的组合（2026-05-08 客户复审重点）
# 【这是 batch VM 抽取后最容易漏掉的反模式】抽 VM 时 agent 看到 page 原本有 @Local windowModel，
# 容易以为它是"基础设施绑定"保留，但实际 vm extends BaseViewModel 已有 windowModel。
for f in $(find features products -name '*Page.ets' -path '*/pages/*' 2>/dev/null | grep -v build); do
  has_vm=$(grep -cE "(private|@Local) vm:\s*\w+ViewModel" "$f")
  has_redundant=$(grep -cE "@Local (windowModel|breakpointModel):\s*(WindowModel|BreakpointModel)" "$f")
  [ "$has_vm" -gt 0 ] && [ "$has_redundant" -gt 0 ] && echo "VIOLATION: $f"
done
# 期望 0 命中 — 该 batch refactor 完后还命中说明 agent 漏了这条

# 4. page 顶部业务 @Local 字段（非 UI 控制 flag 类）— 数量统计
for f in features/*/src/main/ets/pages/*.ets; do
  count=$(grep -c "^\s*@Local " "$f")
  if [ "$count" -gt 3 ]; then
    echo "$f: $count @Local"
  fi
done
# 多于 3 个 @Local 的 page 多半状态没收敛到 VM
```

### 整改步骤

1. **删 `pathStack: NavPathStack = ...` 字段**：所有 `this.pathStack.push/pop` 改为 `RouterUtils.getStack().push/pop`，或在 VM 里加 `@Trace stack: NavPathStack`，业务方法 `this.stack = ctx.pathStack` 在 onReady 同步
2. **删 `@Local windowModel` 字段**：访问点 `this.windowModel.X` → `this.vm.windowModel.X`
3. **删 `@Local breakpointModel` 字段**：访问点 `this.breakpointModel.X` → `this.vm.breakPointModel.X`（⚠️ **大小写陷阱**：BaseViewModel 的字段名是 `breakPointModel` 大写 P，不是 `breakpointModel` —— 直接全文替换会编译报错）
4. **每个业务 `@Local` 字段移到 VM**：在 VM 加 `@Trace 字段: T = 默认值`，page 改读写 `this.vm.字段`
5. **page 上保留**：`vm` / `abortController` / `timer ID` / `第三方回调引用` / `@Builder` / `pathInfo`

### 2026-05-08 客户复审（44 + 13 处漏改实证）

第一轮 R6.1g batch VM 抽取后客户截图圈出 **AiPaintChatPage / ChatPaintDetailsPage** 仍有 `@Local windowModel: WindowModel = AppStorageV2.connect(...)` —— 同时持 vm 和冗余 windowModel。

batch 全工程 grep 后发现：
- **44 个 page** 同时持 vm + `@Local windowModel`
- **13 个 page** 同时持 vm + `@Local breakpointModel`

根因：抽 VM 的 batch agent 看到 page 原本的 @Local 列表里有 `windowModel = AppStorageV2.connect(...)`，把它当作"基础设施 AppStorageV2 binding"保留下来了。但 BaseViewModel 已自带 windowModel，**只要 vm extends BaseViewModel 就完全不需要 page 单独绑**。

**Phase 3 batch agent prompt 必须显式说明**：
> 抽 VM 后 page 顶部**必须删掉** `@Local windowModel: WindowModel = AppStorageV2.connect(...)` 和 `@Local breakpointModel: BreakpointModel = AppStorageV2.connect(...)` —— 这两个字段 BaseViewModel 已自带。访问点全文替换 `this.windowModel` → `this.vm.windowModel`、`this.breakpointModel` → `this.vm.breakPointModel`（⚠️ 注意 P 大写）。**Phase 4 ② audit 重扫时必跑触发器 #3 验证组合冗余**。

### 客户原话（2026-05-08）

> "其他页面也出现了 已经有 vm，但是还是单独定义了 WindowModel，应该直接从 vm 获取。这个逻辑是所有页面通用的，详细检查下所有页面有没有这个问题。"

### 跟 R6.7 / R6.8 的层叠关系

- **R6.7**：用户初始化必须用 AppApis.initUser，不能自建 /user/initUser
- **R6.8**：HttpClient 类不能存在；业务侧不能手动赋值用户字段
- **R6.9**：page 上不能有冗余字段；状态/路由全部 VM 持有

三条规则一起，定义了"私仓自治 + page 极简 + VM 中心"的工程结构。**违反任意一条 → 直接 P0**。

### 客户原话（2026-05-07）

> "其实已经有了 vm，那个这些状态都应该收敛到 vm 里面去，WindowModel 直接从 vm 里面获取就好，不需要再定义一个了"

> "图一所示的取消标识符，参考 AIPPT_ArkTS_rebuild 的实现"

---

## R6.10 登录态 / VIP 态判定**必须**走私仓 LibUserData 方法（MUST，2026-05-08 客户实证）

### 规则

业务代码判定登录态和 VIP 态，**禁止**用工程独立 KV 字段或显式数值比较，**必须**调用私仓 `LibUserData` 提供的方法：

| 判定意图 | ✅ 正确 | ❌ 反模式 |
|---|---|---|
| **是否已登录** | `LibUserData.getInstance().isBinding()` | `await UserPreferences.isLogin()` / `this.userInfoModel.isLogin` / `token.length > 0 && userId > 0` |
| **是否 VIP** | `LibUserData.getInstance().isVip()` | `vipLevel > 0` / `this.vipLevel > 0` / `vipLevel >= 1` |
| **是否 VIP 反向** | `!LibUserData.getInstance().isVip()` | `vipLevel <= 0` / `vipLevel === 0` |

### 客户原话

> "判断是否登录，采用 UserData.getInstance().isBinding() 判断，判断是否开通 vip，采用 UserData.getInstance().isVip() 判断"

### 为什么必须走私仓方法

1. **isBinding() 内部包含完整登录判定逻辑**：不只是 `token.length > 0`，还有 `userId > 0` 的双条件 + `userState !== 4`（注销态）等私仓维护的细节。业务侧手写 `vipLevel > 0` 形态会随服务端语义变化（如新增 `userState=5` 等）失效。

2. **isVip() 内部包含 5 分钟保护窗口逻辑**：支付成功后服务端异步回调慢于客户端时，私仓内部用 `vipManualUpdateTime` 保护本地 vipLevel 不被覆盖。业务侧用 `vipLevel > 0` 直接读会绕过这个保护，导致支付完冷启 VIP 闪退。

3. **私仓方法跟服务端语义同步演进**：未来若加 vipLevel=99 表示企业账号、vipLevel=-1 表示封号过渡态等，私仓 isVip() 会同步更新，业务侧零改动。`vipLevel > 0` 全工程要排查每个调用方。

4. **工程独立 KV `IS_LOGIN`** 是**写**态字段（用于持久化），**读**应用 isBinding() —— 写读分离原则：写 KV 是为了维护业务态，读判断必须走私仓权威方法。

### audit 触发器

```bash
# 1. 业务代码用 await UserPreferences.isLogin() 判登录
grep -rn "await\s\+UserPreferences\.isLogin\s*(" features products --include="*.ets" 2>/dev/null \
  | grep -v "preferences/UserPreferences\.ets" | grep -v build
# 期望 0 命中（除 UserPreferences.setIsLogin 写态调用，那个是另一套）

# 2. userInfoModel.isLogin 直读（应改 LibUserData.isBinding）
grep -rn "userInfoModel\.isLogin\b" features products --include="*.ets" 2>/dev/null
# 期望 0 命中

# 3. vipLevel 显式数值比较（应改 isVip()）
grep -rEn "vipLevel\s*(>|<=|<|>=|===|!==)\s*[0-9]" features products --include="*.ets" 2>/dev/null \
  | grep -v "lib_common\|MembershipRefresher\|build"
# 期望 0 命中（MembershipRefresher 是 5min 保护窗口业务，其内部 vipLevel 比较是私仓内部逻辑等价复刻，可豁免）

# 4. 正面 grep — 全工程使用 isBinding/isVip 的位置（应至少 5+ 处覆盖主要登录/VIP 判断点）
grep -rn "LibUserData\.getInstance()\.\(isBinding\|isVip\)\(\)\|UserData\.getInstance()\.\(isBinding\|isVip\)\(\)" \
  features products --include="*.ets" 2>/dev/null | grep -v build | wc -l
```

### 整改步骤

1. 全文 `await UserPreferences.isLogin()` → `LibUserData.getInstance().isBinding()`（删 await，私仓方法是同步的）
2. 全文 `this.userInfoModel.isLogin` → `LibUserData.getInstance().isBinding()`
3. 全文 `vipLevel > 0` 表达式 → `LibUserData.getInstance().isVip()`（注意 regex 顺序：先匹配 `this.vipLevel > 0` 再匹配裸 `vipLevel > 0`，否则会替换成 `this.LibUserData.getInstance()...` 的错误格式）
4. 每个改动文件加 `import { UserData as LibUserData } from 'lib_common'`（已有 lib_common import 的扩展即可）
5. **保留** `UserPreferences.setIsLogin(true/false)` 写态调用 —— 是为了 logout 时清理持久化 KV，不影响 isBinding() 读判断（isBinding 读的是 LibUserData 内字段）

### 整改实战记录（meizhao_arkTs 工程，2026-05-08）

- 改前：8 处 `await UserPreferences.isLogin()` + 1 处 `userInfoModel.isLogin` + 4 处 `vipLevel > 0`
- 改后：13 处 `LibUserData.getInstance().isBinding/isVip()` 调用
- 涉及文件：MineFragmentComponent / MemberCenterViewModel / MineSettingPage / GuideMemberCenterPage / VideoCreatePicturePage / HomeViewModel / IonBusiness / AppRepository / MembershipRefresher
- 客户原话："判断是否登录，采用 UserData.getInstance().isBinding() 判断，判断是否开通 vip，采用 UserData.getInstance().isVip() 判断"

---
