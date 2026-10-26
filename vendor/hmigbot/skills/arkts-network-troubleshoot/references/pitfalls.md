# 通用陷阱手册（A-H 八大类）

> 与具体业务无关。每类列：通用症状 / 通用根因 / 通用修复模式。按出现概率组织。

## 目录

- [Class A: 字节级陷阱](#class-a-字节级陷阱cryptoframework--uint8array)（90%）
- [Class B: ArkTS 语言陷阱](#class-b-arkts-语言陷阱)（100%）
- [Class C: 启动期初始化 race](#class-c-启动期初始化-race)（100%）
- [Class D: 后端契约对齐](#class-d-后端契约对齐)（100%）
- [Class E: UI 响应式订阅](#class-e-ui-响应式订阅)（100%）
- [Class F: 构建期注入字段差异](#class-f-构建期注入字段差异)（50%）
- [Class G: 三方 SDK 替代](#class-g-三方-sdk-替代)（50-90%）
- [Class H: 资源 / 国际化 / 主题](#class-h-资源--国际化--主题)（30%）
- [Class I: HMOS NetworkKit 平台陷阱](#class-i-hmos-networkkit-平台陷阱)（100%）

---

# Class A: 字节级陷阱（cryptoFramework / Uint8Array）

> 触发概率 90%（任何 HMAC / MD5 / SHA / AES 加密签名工程）

## A1. `buffer.from(str, encoding).buffer` 返回内存池整段

**症状**：HCF C++ 层报 `ConvertSymmKey: Invalid param: input key length is invalid!`；hash / HMAC 输出与 Android 字节级不一致。

**根因**：`@kit.ArkTS.buffer.from` 走 buffer pool 分配（如 8192 字节内存池），`.buffer` 字段指向整个池而非字符串实际字节范围。HCF C++ 层读 `.buffer.byteLength` 拿到整个池长度 → 校验失败。

## A2. `createSymKeyGenerator('HMAC|XXX')` 兼容性

**症状**：同 A1，即使 key 长度合法（如 32 字节）。

**根因**：不同 HMOS NEXT 版本对 algName 解析行为不一致，`'HMAC|SHA1'` 带后缀写法在 6.0+ 某些 build 触发额外校验。

**修复**：用无后缀 `createSymKeyGenerator('HMAC')` + `createMac('SHA1')` 组合。实测 HMOS NEXT 6.0+ 真机换成 `'HMAC'` 即解。

## A3. Hex 输出大小写不可一刀切

**症状**：签名值长度对但与服务端比对失败 → 401。

**根因**：Android 工程内不同签名链路用不同大小写 hex（典型：自有业务签名实现用大写 `'A'..'F'`；三方厂商签名实现用小写 `'a'..'f'`）。HMOS SignUtil 只暴露一个大小写入口必然有一套链路签名错。

## Class A 通用修复

```typescript
import { util } from '@kit.ArkTS';
import { cryptoFramework } from '@kit.CryptoArchitectureKit';

// 防御性拷贝：byteOffset=0 + 独立 ArrayBuffer
private static utf8Bytes(str: string): Uint8Array {
  const encoded = new util.TextEncoder('utf-8').encodeInto(str);
  const own = new Uint8Array(encoded.length);
  own.set(encoded);
  return own;
}

// HMAC 无后缀写法
private static async hmacSha1Bytes(input: string, secret: string): Promise<Uint8Array> {
  const mac = cryptoFramework.createMac('SHA1');
  const symKeyGen = cryptoFramework.createSymKeyGenerator('HMAC');   // 无后缀
  const symKey = await symKeyGen.convertKey({ data: SignUtil.utf8Bytes(secret) });
  await mac.init(symKey);
  await mac.update({ data: SignUtil.utf8Bytes(input) });
  return (await mac.doFinal()).data;
}

// hex 大小写双入口
private static bytesToHex(bytes: Uint8Array, upperCase: boolean): string {
  const digits = upperCase ? '0123456789ABCDEF' : '0123456789abcdef';
  let out = '';
  for (let i = 0; i < bytes.length; i++) {
    const b = bytes[i] & 0xFF;
    out += digits.charAt((b >>> 4) & 0x0F) + digits.charAt(b & 0x0F);
  }
  return out;
}
```

**验证**：hilog 打 `byteOffset` / `buffer.byteLength` / `length`，三者一致才正确。完整模板见 [templates/code/sign-util.ets](templates/code/sign-util.ets)。

---

# Class B: ArkTS 语言陷阱

> 触发概率 100%（任何 Android → HMOS 项目都会撞）

## B1. ArkTS 没有 Gson `@SerializedName` 等价

**症状**：HTTP 200 但 `response.errorCode === undefined`；`userData.token` undefined 但抓包里有 `"token"`。

**根因**：Android 用 `@SerializedName("status") int errorCode` 让 JSON 字段名和 Java 字段名解耦。ArkTS `JSON.parse(body) as T` 是不安全 cast：plain object 属性名必须完全等于 class 字段名才能读到值。

**修复**：HttpClient 统一镜像（见 Phase 4），维护 FIELD_MAP 配置表。

## B2. `JSON.parse(body) as T` 不安全 cast

**症状**：`.length on undefined`；class 方法 / setter 静默失败。

**根因**：ArkTS 没有运行时类型检查。`as T` 仅编译期通过，运行时拿到 plain object，class 字段默认值丢失、方法不可调用。

**修复**：class 提供 `fromJson` 静态方法逐字段守卫；或业务侧每次读字段加 `typeof === 'string' && .length > 0` 守卫，不要直接 `.length`。

## B3. AppStorage dot-notation key 不展开

**症状**：`AppStorage.get<string>('userData.token')` 永远 undefined。

**根因**：AppStorage 是扁平 key-value 存储，不支持点号嵌套。`'userData.token'` 是一个完整 key 字符串。

**修复**：整对象读 `AppStorage.get<Object>('userData')` 再读字段；或组件用 `@StorageProp('userData')`。

## B4. Object literal 行内 `{}` 严格模式禁止

**症状**：编译报 `arkts-no-untyped-obj-literals`。

**修复**：声明 interface / 用 `Record<string, Object>` / 空对象用 `new Object()` / JSON 解析占位 `JSON.parse('{}')`。

## B5. `bundleInfo.appInfo.label` 是资源引用而非已解析字符串

**症状**：埋点 / 公参字段中看到字面值 `"$string:app_name"`。

**修复**：labelStr 以 `$` 开头时用 `ctx.resourceManager.getStringSync(labelId)` 解析。

## B6. ArkTS 异步与 Kotlin 协程差异

Kotlin 协程 `runBlocking` 同步阻塞模式 ArkTS 没有。所有 async 函数返回 Promise，必须 await。不能 async 的地方（onCreate）保留 Promise 引用后续 await。

## B7. V2 `@ObservedV2` / `@Trace` 实例不可写入 V1 `AppStorage`

**症状**：把 V2 状态对象存进 `AppStorage` 时运行时崩 —— `Illegal variable value error ... not V2 @ObservedV2 / @Trace class`，值里带 `__ob_xxx` 前缀。

**根因**：`AppStorage.setOrCreate('userData', <V2 @ObservedV2 UserData 实例>)`。V1 AppStorage 只接受普通值 / 普通对象，**拒绝 V2 `@Trace` 装饰类实例**。常见于"想给网络层一个读 token 的 V1 桥"，但 UserData 本身是 V2（现代最佳实践）→ 桥一建就崩，且 login / logout / VIP 等所有写该桥的路径同崩。

**修复**：状态走**单一事实源**。V2 用 `AppStorageV2.connect(UserData, 'user', () => new UserData())` 直接读 / 写 V2 单例；网络层 `readToken()` 也直读 V2 单例。**不要**把 V2 对象镜像进 V1 `AppStorage`，也**不要**用 `AppStorage.get('userData')` 做 V1 桥。

## Class B 通用原则

不要假设 JSON.parse 给你 class instance；不要假设字段名自动重映射；不要假设 AppStorage 支持嵌套；不要假设 ArkTS 像 TS 一样宽松；不要假设 async 能"同步化"。

---

# Class C: 启动期初始化 race

> 触发概率 100%

## C1. `EntryAbility.onCreate` 不允许 async，但 init 是 async

**症状**：协议弹窗每次冷启都弹；拦截器读 Preferences 全走默认值；HttpLogInterceptor 静默。

**根因**：`onCreate(want, launchParam): void` 签名不允许 async。fire-and-forget 后立即 loadContent，SplashPage 起来时 PreferencesUtil.init 还没就绪。

**修复套路**：sync onCreate + async onWindowStageCreate + Promise 保留 + await 后再 loadContent。完整模板见 [templates/code/entry-ability.ets](templates/code/entry-ability.ets)。

## C2. AppStorage 全局 key 未启动期注入

**症状**：`HttpClient.download` 抛 `No UIAbilityContext`；HttpLogInterceptor 静默。

**根因**：多处底层模块依赖 `AppStorage.get('context'/'isDebug'/'mHttpUrl')`，必须 onCreate 同步注入。

## C3. 静态工具类内 `getContext()` 不可靠

**症状**：静态 Util / 拦截器 / Service 单例内调 `getContext(this)` 报 context undefined。

**根因**：`getContext(this)` 是组件级 API，依赖 `this` 是 @Component 实例。

**修复**：从 `AppStorage.get<Context>('context')` 或 `GlobalCont.getContext()` 取。

## C4. SplashService 异步链路顺序错乱

**症状**：initUser body androidId 空 → 后端 ANDROID_ID NOT NULL 报错。

**修复**：`ensureAndroidId() → aggregateOaid() → initUser()` 三步串行（按依赖），与 fetchInitialConfig / progressLoad 并发。

## Class C 通用原则

同步初始化全放 onCreate；异步初始化保留 Promise；onWindowStageCreate 内 await 关键 Promise 后再 loadContent。

---

# Class D: 后端契约对齐

> 触发概率 100%（任何 Retrofit + 自定义 Interceptor 工程）

## D1. Android ResponseInterceptor 隐式 unwrap，HMOS 必须显式做

**症状**：HTTP 200 但 `data.token === undefined`，整个响应类字段全 undefined。

**根因**：Android 后端响应 `{ code, msg, data: {...} }`，Android ResponseInterceptor 把 `body.data` 抽出来当整个 body，Retrofit 反序列化拿到 data 部分。HMOS 没有等价物，必须在 HttpClient 层手动 unwrap。

**修复**：仅对自有业务实例（`defaultInstance`）启用 unwrap，三方域保持 false。见 Phase 4。

## D2. URL 路径常量化 → 抽取易漏前缀

**症状**：后端报 `404 No static resource xxx`。

**根因**：Android `object UserUrl { const val xxx = "/user/yyy" }` 把路径常量化。a2h-spec 抽取容易：只看 `@POST(UserUrl.xxx)` 字面值层、抽到接口方法名而非服务端路径、漏 `/user/` 等命名空间前缀。

## D3. Request body 字段是函数级别构造

**症状**：后端报 `Missing request attribute 'xxx'`。

**根因**：Android `fun sendSmsBody(phone) = mutableMapOf("mobile" to phone, "source" to 1).toRequestBody()`。a2h-spec 只看 `@Body RequestBody` 看不到 `xxxBody` 函数内字段（特别 `source: 1` 这种常量）。

## D4. 公参 / platformInfo 字段不全 + 后端 schema 约束

**症状**：后端 NPE on enum 字段 `.ordinal()`（错误形如 `Cannot invoke "...SomeEnum.ordinal()" because "<字段名>" is null`）；DB INSERT 报 `Column 'XXX' cannot be null`。

**根因**：后端根据 platformInfo 某字段反查 enum / 把全字段 INSERT 业务表。a2h-spec 抽 platformInfo 不全。

**先判定「客户端缺字段」还是「后端问题」** —— 不要一上来就猜字段名往 platformInfo 里塞：

1. 把 HMOS 请求体与 Android **真实抓包**逐字段对齐（body + 公参 + headers，见 capture-android-traffic.md）。
   **⚠ 设备态必须一致**：HMOS 模拟器是后端从没见过的新设备（token 空 / 无归因记录），就必须拿
   Android **`pm clear` 后冷启**的抓包做基线 —— 别拿带 token 的老设备抓包比，否则 token 态 /
   归因态不同会把你引向错误结论。同一接口的成功/失败往往只取决于设备态。
2. 对齐后**仍** NPE → 这不是客户端缺字段，是**后端问题**（后端对 HMOS 端 / 新设备的 enum 反查逻辑有缺陷）。停止猜字段，带抓包证据找后端要 enum 反查规则。
3. 反面教训：凭空加一个 `mediaNo` 之类的字段、把 `baseType` 当兜底值塞 —— Android 根本不发该字段，加了也没用，白费一轮 build-test。
4. **合法对齐 vs 凭空加字段的边界**：把 Android **确实在发**的字段补成与 Android 一致的非空值 =
   合法对齐（实战例：`oaid` —— HMOS 送空串、Android 送持久化 UUID，后端据 oaid 反查媒体号 enum，
   把 HMOS 的 oaid 补成非空持久化 UUID 是对的）；Android **根本不发**的字段（如 `mediaNo`）凭空加 = 错误。

**特殊处理**：

| 字段 | Android 来源 | HMOS fallback |
|---|---|---|
| `androidId` | `Settings.Secure.ANDROID_ID` | 首启 `util.generateRandomUUID(false).replace(/-/g,'')` 持久化复用 |
| `imei` | `DeviceIdentifier.getIMEI()`（现代 Android 受限常空） | HMOS 无 IMEI → **留标记**，替代 AAID(Push Kit)/ODID（禁直接写空） |
| `oaid` | `DeviceIdentifier.getOAID()` | `@kit.AdsKit.identifier.getOAID()` + APP_TRACKING_CONSENT |
| `installSource` | `getInstallerPackageName()` | HMOS 无简单等价 → **留标记**，走 AppGallery 应用归因服务（禁直接写空） |
| `channel` | Walle 渠道包 | 硬编码 Android `defaultChannel` |
| `operators` | `TelephonyManager.networkOperatorName` | `sim.getSimOperatorNumericSync(0)` + try/catch `'un_know'` |

## D4b. 字段缺等价时【照搬 Android + 留标记】，禁静默置空

**原则**：公参每个字段都要可追溯到 Android 原版取值。HMOS 有等价就照搬；**无等价的留显式标记**（占位登记 + Android 源锚点）。**绝不**在文档 / 代码写"该字段可空 / 送空串 / HMOS 无等价→空"——那是把"空"当合法静止态，正是"某标识字段送空 → 后端按它反查枚举 NPE / 拒"这类 bug 的根源。空值只能是"照搬 Android（其值确实为空）+ 已登记标记"的结果，不是单方面给定。

## D4c. guest / 匿名态拿到鉴权失效码不可清 token（仅 bound 账号才登出）

**症状**：启动期建立的匿名 token 在进登录页前被清空（后续 pre-login 接口带空 token → 鉴权失效码 / "未登录"）。

**根因**：`鉴权失效码 → 全局登出 → 清 token` 无差别触发。半成品迁移里某 pre-login 鉴权接口（进站配置 / 配额查询 / 用户信息等）用匿名 token 调用被后端拒，触发全局登出，把刚建的匿名 token 清掉。原 Android 不撞，是因其匿名 token 被所有 pre-login 接口接受、不返失效码 —— **这条不能照搬"无差别登出"**。

**修复**：① 启动期只发 token-less 容忍的接口（配置拉取 / 首启上报等）+ 建立匿名 token 的接口；其余鉴权接口移到 token 建立之后（进主页 / 懒拉），别在启动期发。② `失效码 → 登出` **仅对 bound 账号**（userState ≥ 2 等价）生效；guest / 匿名态的失效码保留 token、不登出。

## D5. App ID 不对齐：HMOS bundleName vs Android applicationId

**症状**：后端按 packageName 派生 enum → null NPE。

**根因**：HMOS 脚手架 bundleName 默认 `com.example.xxx`，Android 一个 product 一个 applicationId。

**修复（三选一）**：

1. **推荐稳定**：改 `AppScope/app.json5 bundleName` 对齐 Android applicationId
2. **短期最快**：platformInfo.packageName 硬覆盖为 Android applicationId（不改 HMOS 真实包名）
3. **长期正规**：后端 enum 白名单加 HMOS 独立 bundleName 映射

无论哪种方案必须在 `spec/baseline/decisions.md` 登记成本与回滚路径。

## D6. HTTP 200 ≠ 业务成功

**症状**：把「HTTP 200」当成功 → 漏判 `data.status != 0` 的业务失败；据此在对账表误写「某字段可不传 / 可省略」。

**根因**：后端统一 `{code, msg, data:{status,...}}` 外壳，HTTP 层几乎永远 200，真实结果在 unwrap 后的 `data.status`（或 `code`）。

**修复**：成功判定必须看 unwrap 后业务码（`status==0` / `code==0`），不是 HTTP code。对账表里「实测可省略 / 可不传」类结论必须基于 `status==0`，不能基于 200。

## Class D 通用原则

不要凭脑补猜后端行为（Phase 0 抓真包 + 找后端要 enum/schema）；URL/body 字段必须 1:1 对账；HMOS 无等价 API 字段必须有明确 fallback；packageName 不对齐三方案选一并 spec 登记。

**禁止连续盲试**：联调出现后端业务错误（-500 / NPE / 字段类），首次修复未命中后**不要**接着「改字段→重编译→再试」连刷 —— 每轮 build→install→冷启→抓 hilog 成本 3-4 分钟，盲试 3 轮 ≈ 浪费一个 Phase。正确做法：首修未中 → 立刻回 Phase 0 用代理抓 Android 真实请求（含 headers），与 HMOS 请求逐字节对比，一次性找全所有差异再批量修。

---

# Class E: UI 响应式订阅

> 触发概率 100%（任何 Fragment → Component 迁移工程）

## E1. 登录态字段用 @Prop 反模式

**症状**：登录成功后某 Tab 仍显示未登录占位；VIP 开通后首页仍显示「开通会员」。

**根因**：a2h-activity-converter 把 Fragment 转 Component 沿用"Fragment 由 Activity 注入数据"心智用 `@Prop`，但 ArkUI 调用方 `MineComponent()` 直接调用不传参 → 全部默认值。

**修复**：

```typescript
@Component
export struct MineComponent {
  @StorageProp('userData') userData: UserData = new UserData();
  private get isLogin(): boolean {
    return this.userData.token.length > 0 && this.userData.userId > 1;
  }
  private get isVip(): boolean {
    return this.userData.vipLevel > 0;
  }
}
```

改造步骤：找所有 `@Prop isLogin/isVip/userId/...` → 加 `@StorageProp('userData')` → @Prop 字段改 private getter → 删 @Prop。

## E2. AppStorage 写入入口散落

**修复**：所有 AppStorage('userData') 写入通过 `UserRepository.saveUserData`（写 AppStorage → 同步 Preferences → `EventBus.post(USER_DATA_UPDATE)`）。业务侧禁止直接 `AppStorage.setOrCreate`。

## E3. 双订阅模式（账号详情类页面）

账号详情类页面 @StorageLink + EventBus.on 双订阅：aboutToAppear 内 `EventBus.on(USER_DATA_UPDATE)` + `LoginService.getInfo()` 主动刷一次，aboutToDisappear 内 `EventBus.off`。

## E4. @StorageProp 字段类型必须匹配 AppStorage 写入

写入侧 `AppStorage.setOrCreate<UserData>('userData', userData)`，读取侧 `@StorageProp('userData') userData: UserData`，双方用同一个 class。

---

# Class F: 构建期注入字段差异

> 触发概率 50%（多渠道 / 多 brand 项目）

## F1. productFlavor / manifestPlaceholders / BuildConfig 在 HMOS 无等价

**症状**：编译产物所有 product 都是同一份 baseType / channel / SDK key。

**根因**：Android `productFlavors {}` 编译期注入不同 brand 配置。HMOS NEXT `build-profile.json5` 的 buildProfileFields 只支持有限基础字段，不能切包名 / 资源。

**修复（按规模）**：

- 单 product → 全硬编码常量
- 2-3 product → `build-profile.json5` buildProfileFields 注入 + `hvigorw assembleHap -p product=brandA` 切换
- 多 brand（>5）→ 独立 HSP 模块每 brand 一个，主壳 ohpm 引用

## F2. AndroidManifest meta-data 在 HMOS 无等价位置

**修复**：首选硬编码常量 + `spec/baseline/product-config.md` 登记来源；次选写 `resources/base/profile/app-config.json` + ReadRawfile 读；再次 module.json5 metadata 段（仅供应用市场审核工具识别）。

---

# Class G: 三方 SDK 替代

> 触发概率 50-90%（登录 / 支付 / 推送 / 广告 / 埋点工程）

## G1. Android SDK 在 HMOS 无对应 ohpm 包

典型映射（2026Q2 参考）：

| Android SDK | HMOS 等价 |
|---|---|
| 微信 OpenSDK | `@tencent/wechat_open_sdk`（ohpm）|
| 支付宝 SDK | `@cashier_alipay/cashiersdk`（ohpm）|
| 华为账号 / 推送 / 广告 | `@kit.AccountKit` / `@kit.PushKit` / `@kit.AdsKit`（系统 kit）|
| 友盟 | 无官方，自实现降级 |
| 火山 AppLog / 百度归因 | `@volcengine/applog` / `@bytedance_ads/app_convert`（私仓）|
| OkHttp / Retrofit | 自写 HttpClient + 拦截器（@kit.NetworkKit）|
| Gson | `JSON.parse` + 手动 fromJson |
| MMKV | `@kit.ArkData.preferences` |
| Greenrobot EventBus | `UIAbilityContext.eventHub` 包装 |

替代决策流程：查 ohpm.openharmony.cn → 查 @kit.* 官方等价 → 查私仓 → 自实现降级。

## G2. OAuth 2.0 客户端职责边界

**反模式**：Android 客户端用 APP_SECRET 直接换 access_token（反编译泄露 SECRET）。

**修复**：HMOS 端遵循 OAuth 2.0 标准，客户端只拿 code，绝不持有 SECRET：`客户端拿 code → 送后端 → 后端用 SECRET 换 token`。微信 code / 支付宝 auth_code / 华为 authorizationCode 都是如此。

## G3. 设备唯一标识

| 标识 | HMOS | 稳定性 |
|---|---|---|
| OAID | `@kit.AdsKit.identifier.getOAID()`（拒绝授权返 `0...0`）| 中 |
| 应用层 UUID | Preferences 持久化 generateRandomUUID | 低（清数据变）|
| 设备 SN | `deviceInfo.serial`（需权限）| 高 |

应对后端 NOT NULL 约束：**OAID 非全 0 才用、否则退持久化 UUID**——OAID 拒授权返全 0 是**实测常态**，故持久化 UUID 才是可靠主路径，OAID 只是"能用则用"；**禁送空串/全 0**（设备即账号型后端据指纹生成 deviceNo，送空/全 0 会 NPE 或 500——这是"传空串兼容后端"反模式的真实死因）。

> **跨平台连续性盲区**：HMOS 指纹（OAID/UUID）≠ Android 端 → 同一设备两端生成的 deviceNo 不同 → **老用户迁 HMOS 被当成新设备、丢原态**。账号连续性须**后端配合**（接受 HMOS 身份映射 / 迁移）；客户端补非空指纹只能保**新装**用户开箱可用，保不了老用户跨端连续。

## G4. 未接入 SDK 的 PLACEHOLDER 处理

未接入 SDK 调用做成 PLACEHOLDER，编号 `P-S<x>-<yy>`，代码内注释 `// PLACEHOLDER: P-Sxx-NNN trigger=...`，`spec/placeholder-registry.md` 登记。V2 解锁时按 P-ID 反查代码。

## G5. 私仓 SDK 配置（.ohpmrc）

`Cannot find module '@private-org/some-sdk'` → 项目根目录 `.ohpmrc` 配私仓源。私仓未配置时**不要保留** import（会让整个 lib 编译失败），暂时注释 export + 登记 `spec/baseline/sdk-status.md`。

---

# Class H: 资源 / 国际化 / 主题

> 触发概率 30%（引入私仓 lib / 多语言 / 主题切换工程）

## H1. HAR 模块资源命名空间合并

**症状**：主题色变成 lib_common 默认值。

**根因**：HAR 模块 `resources/base/element/*.json` 合并进主应用命名空间，同 key 时按 HAR 解析顺序合并。

**修复**：HAR 内资源 key 加前缀避免冲突（lib 用 `libcommon_xxx` / entry 用 `app_xxx`）；或 entry 显式 override + 真机校验。

## H2. resourceManager.getStringSync 必须有 context

静态工具类 / 拦截器 / Service 内不能用 `getContext(this)`，从 `AppStorage.get<Context>('context')` 或 `GlobalCont.getContext()` 取。

## H3. 国际化资源切换

`resources/<locale>/element/string.json` 按系统语言匹配，程序内 `i18n.System.setAppPreferredLanguage('zh-Hans')` 主动切换。详见 arkts-i18n skill。

## H4. ArkUI $r() 解析失败

资源 key 拼写错 / HAR 资源未打进编译产物。用 IDE 跳转验证 key 存在 + `hvigorw clean assembleHap` 后检查编译产物。

---

# Class I: HMOS NetworkKit 平台陷阱

> 触发概率 100%（任何 `@kit.NetworkKit.http` 工程）

这一类陷阱的共同特征：**编译期 PASS + BUILD SUCCESSFUL + 静态分析全过 + HAP 产物正常生成，但运行时所有 HTTP 请求都失败**。隐蔽性最强 —— 迁移联调时常被误判为后端问题、签名问题或 ArkTS cast 问题。先排查这 4 项再谈业务逻辑。

## I1. `response.result` 三态类型 → 必须显式 `expectDataType`

**症状**：所有 HTTP 调用返回但回调一律走 exception 分支；hilog 看不到具体业务报错；JSON.parse 抛 `SyntaxError: Unexpected end of JSON input`；上层判定全是「网络异常」。

**根因**：`@kit.NetworkKit.http.HttpResponse.result` 的实际类型是 `string | Object | ArrayBuffer` 三态：

- 未指定 `expectDataType` 时，HMOS 框架**根据响应 `Content-Type` 自动选择类型**
- `Content-Type: application/json` → 框架可能自动 parse 返回 **Object**（不是 string）
- `Content-Type: text/*` → 返回 string
- 二进制 / 未识别 → 返回 ArrayBuffer

迁移者从 Android Retrofit / OkHttp 心智过来——OkHttp `ResponseBody.string()` 永远返 String，所以惯性写法 `typeof response.result === 'string' ? response.result : ''` 在 JSON 响应时**直接走 else 返回空字符串** → 上层 JSON.parse('') 抛 SyntaxError → 全部请求走 exception 分支。**全工程所有接口看似"网络失败"**。

**修复**：显式指定 `expectDataType: http.HttpDataType.STRING` 强制返回 string，**同时**写防御性 `coerceToString(result)` helper 兼容三种类型（即使框架行为变更也不破坏）：

```typescript
import { http } from '@kit.NetworkKit';
import { util } from '@kit.ArkTS';

const response: http.HttpResponse = await request.request(url, {
  method: http.RequestMethod.GET,
  header: { 'Accept': 'application/json' },
  expectDataType: http.HttpDataType.STRING,  // ← 关键：强制 string，绕过框架自动 parse
  readTimeout: 10000,
  connectTimeout: 10000
});
const bodyStr: string = coerceToString(response.result);

// 防御性兼容三种 result 类型
function coerceToString(result: string | Object | ArrayBuffer): string {
  if (typeof result === 'string') {
    return result;
  }
  if (result instanceof ArrayBuffer) {
    try {
      const decoder = util.TextDecoder.create('utf-8');
      return decoder.decodeToString(new Uint8Array(result));
    } catch (_e) {
      return '';
    }
  }
  if (result !== null && result !== undefined) {
    try { return JSON.stringify(result); } catch (_e) { return ''; }
  }
  return '';
}
```

**验证**：hilog 打 `typeof response.result` + `Array.isArray(response.result)` + `response.result?.constructor?.name`，预期看到 `string` / `false` / `String`。如果出现 `object` / `Object` / `ArrayBuffer` 即命中本 pitfall。

**为什么严重**：编译过 + HAP 跑起来 + BUILD SUCCESSFUL，但跑联调时**100% 接口失败**。最容易被误判为后端问题、网络问题、或拦截器问题。修复前可能盲试几天。

## I2. GET 请求误设 `Content-Type` 应改 `Accept`

**症状**：（非阻塞）GET 请求 header 里设了 `Content-Type: application/json`；少数严格代理 / WAF / CDN 会因此返 400 Bad Request；多数环境无害但不规范。

**根因**：`Content-Type` 描述**请求体**类型，GET 无 body 不应当带 Content-Type。表达期望响应类型应该用 `Accept` header。

惯性来源：Android Retrofit `@Headers("Content-Type: application/json")` 注解写在 interface 上对所有方法生效（GET 也带）—— Retrofit 实际请求时 OkHttp 对 GET 会**忽略** Content-Type，但 HMOS NetworkKit 的 `header` 字段是**原样透传**。

**修复**：按 HTTP 动词区分 default headers：

```typescript
// 错（worker / 模板默认行为）：
this.defaultHeaders['Content-Type'] = 'application/json';   // GET/POST/... 全部设

// 对：按方法区分
private static methodHeaders(method: http.RequestMethod): Record<string, string> {
  if (method === http.RequestMethod.GET || method === http.RequestMethod.DELETE) {
    return { 'Accept': 'application/json' };
  }
  return { 'Content-Type': 'application/json', 'Accept': 'application/json' };
}
```

## I3. 空 body 防御：`JSON.parse('')` 抛 SyntaxError

**症状**：偶发请求走 exception 分支，hilog 显示 `JSON parse error: SyntaxError: Unexpected end of JSON input`，但响应 HTTP code 是 **200**（不是错误响应！）。

**根因**：后端在某些场景返回 HTTP 200 + 空 body：

- 长轮询超时（后端约定空 body 表示无新消息）
- 204 No Content 被网关错误标 200
- 后端业务空响应（如 logout 接口、心跳）
- 网关 / CDN 中间环节剥离了 body

直接 `JSON.parse('')` 抛 `SyntaxError: Unexpected end of JSON input` → 走 catch 分支误判为 exception。Android Retrofit + Gson 的兜底是 `null`，HMOS 没有等价处理。

**修复**：JSON.parse 前 length 守卫，明确区分「空 body」与「解析错误」：

```typescript
if (bodyStr.length === 0) {
  // 空 body：视业务情况返回成功的空 case，或显式 exception
  hilog.warn(DOMAIN, TAG, 'empty response body for url: %{public}s', url);
  return { kind: 'exception', message: 'empty response body' };
}
try {
  const parsed = JSON.parse(bodyStr);
  return { kind: 'success', data: parsed as T };
} catch (parseErr) {
  // 只有非空 body 解析失败才算真正的 parse error
  hilog.error(DOMAIN, TAG, 'JSON parse error, body=%{public}s', bodyStr.substring(0, 200));
  return { kind: 'exception', message: 'JSON parse error' };
}
```

## I4. 缺 `ohos.permission.INTERNET` 权限声明

**症状**：所有 HTTP 请求**根本未发出**，运行时直接抛权限拒绝；hilog 报 `request failed: 201` 或类似权限相关错误码；BUILD log 给 WARN 但**不阻塞编译**；HAP 产物正常生成；app 安装运行后联网功能全废。

**根因**：HMOS 网络访问需要 `ohos.permission.INTERNET` 权限声明（normal 等级，**无需运行时弹窗**，但必须在 module.json5 显式声明）。

从 Android `<uses-permission android:name="android.permission.INTERNET"/>` 迁移过来的工程常常漏配：
- a2h-execute Stage 0 资源迁移**不碰** module.json5（只搬 colors / strings / media）
- a2h-execute Stage 2 Base-3 Network 任务**关注 HttpClient 实现**，不关注权限声明
- DevEco Studio 创建的脚手架 module.json5 默认**无任何 requestPermissions 段**

结果：HttpClient 看似正确实现，编译完全 PASS，但 app 跑起来联网全废 —— 这是 a2h-execute pipeline 当前的**集成缺口**之一。

**修复**：在 `entry/src/main/module.json5` 的 `module` 段追加 `requestPermissions`：

```json5
{
  "module": {
    // ... 其它字段（name / type / mainElement / pages / abilities / extensionAbilities ...）
    "requestPermissions": [
      {
        "name": "ohos.permission.INTERNET",
        "reason": "$string:internet_permission_reason",
        "usedScene": {
          "abilities": ["EntryAbility"],
          "when": "inuse"
        }
      }
    ]
  }
}
```

配套在 `entry/src/main/resources/base/element/string.json` 加 `internet_permission_reason` 字符串（多语言场景每个 locale 都要补）：

```json
{ "name": "internet_permission_reason", "value": "Required for network access to backend API" }
```

**为什么 Phase 0 必查**：本项与 I1 一样具有「编译 PASS + 联调全废」特征，但本项发生在更早阶段（请求根本未发出）。迁移启动时应该**先**确认 module.json5 有 INTERNET 权限再去 debug HttpClient 行为。

## Class I 通用原则

迁移时**永远不要假设 HMOS NetworkKit 与 OkHttp 行为一致**：

| 维度 | OkHttp / Retrofit 行为 | HMOS NetworkKit 行为 |
|------|----------------------|---------------------|
| 响应类型 | 永远 String（ResponseBody.string()） | 三态 `string \| Object \| ArrayBuffer`，按 Content-Type 自动选 |
| GET 的 Content-Type | OkHttp 客户端会忽略 | 原样透传 |
| 空 body | Gson 兜底 null | JSON.parse('') 抛 SyntaxError |
| 网络权限 | AndroidManifest 默认 / 易迁移 | module.json5 必须显式 + Android 习惯易漏 |
| Header 大小写 | OkHttp 规范化 | HMOS 原样透传 |

这 4 类陷阱的**共同症状**是「编译过 + HAP 跑起来 + 静态分析全过 + 但运行时所有请求都失败」。迁移联调出现「全部接口报网络异常 / 全部 JSON parse error / 全部超时」时，**先按 I4 → I1 → I3 → I2 顺序排查**，再谈后端 / 签名 / 业务逻辑。

a2h-execute pipeline 集成建议：Stage 0 资源前置阶段同步检查 module.json5 INTERNET 权限；Stage 2 Base-3 Network 阶段按本手册 §I1 的 expectDataType + coerceToString + 空 body 守卫模板，避免每个 worker agent 自实现踩坑。
