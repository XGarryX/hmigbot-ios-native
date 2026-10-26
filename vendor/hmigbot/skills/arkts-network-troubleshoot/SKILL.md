---
name: arkts-network-troubleshoot
description: Android → HarmonyOS NEXT ArkTS 迁移项目的网络层 / 启动期 / 加密签名 / UI 响应式订阅的系统化排查与预防 SOP。**正向预防**：新启动迁移项目时按 Phase 0-6 抓证据 + 6 张对账表 + 启动模板 + 字节验证逐步推进；**反向救火**：联调出现 401 / -500 / `Missing request attribute` / `ConvertSymmKey invalid` / `No static resource` / 后端 enum 字段 NPE / DB 字段 NOT NULL 报错 / signature 为空 / 协议每次冷启都弹 / 「我的」Tab 永远未登录态等典型症状时，按错误 → Phase → 修复模板查找；**standalone 报告**：不走迁移、只抓 Android 侧 API 运行时实况并产 contract 报告；**auth-chain 活性探针（场景 E）**：spec 期无设备"试发送"验登录链路是否打通（读 chain-auth + dev_info.json，判业务成功码，回写 uncertainties + 存 golden fixture）。当用户提到「Android 迁移到鸿蒙/HMOS」「接口报 401/500」「HMAC 签名错」「模板/列表加载失败」「登录失败」「拦截器怎么写」「PreferencesUtil race」「BaseBean unwrap」「PlatformInfo 公参」「设备标识 / ANDROID_ID / OAID」「@SerializedName 等价」「productFlavor / 多渠道」「ohpm SDK 替代」「@StorageProp vs @Prop」「API 契约对账」「接口运行时实况报告」等关键词，务必触发本 skill；即使用户只说「迁移项目联调问题」「鸿蒙后端调不通」「鸿蒙启动初始化顺序」也应触发。
metadata:
  type: domain
  domain: data
  tags:
  - domain
  - network
  - migration
  - troubleshoot
  - contract
  - http
  - sign
  - startup
  - runtime
  version: v1.3
---
# Android → HMOS NEXT ArkTS 迁移排查与预防 Skill

## 这个 skill 解决什么

任何 Android Java/Kotlin（Retrofit + OkHttp + Gson + 自定义拦截器 + MMKV + productFlavor）项目迁移到 HarmonyOS NEXT ArkTS 时，**编译过 ≠ 联调通**。绝大多数运行期失败不在 ArkUI 写法，而在 9 个底层差异：

```
Android                                ArkTS
─────────────────────────             ─────────────────────────
Gson @SerializedName            →    无等价（class cast 不重命名）
javax.crypto.Mac 标准库          →    cryptoFramework 有 byteOffset / algName 怪癖
ByteArray + ByteBuffer          →    Uint8Array view 容易带 byteOffset
MMKV.defaultMMKV()              →    preferences.init 必须 await
ContextCompat 单例 context       →    AppStorage 跨实例传递 context
@StringRes / getString          →    resourceManager.getStringSync(id)
Settings.Secure.ANDROID_ID      →    无 1:1 等价（OAID/UUID 替代，G3）
manifest meta-data / BuildConfig →    无 productFlavor 机制
Application.onCreate            →    UIAbility.onCreate 不允许 async
Retrofit @POST(UserUrl.xxx)     →    抽 URL 时易漏前缀
ResponseInterceptor body 改写    →    HMOS 必须显式 unwrap
```

任何 Android 工程迁过来都会撞上面 9 条中至少 5 条。本 skill 把"撞坑"系统化拆成两套姿势：

- **正向预防（推荐）**：新项目启动时按 Phase 0-6 走完静态对账 + 启动期模板 + 字节验证。比联调时再 debug 节省 5-10 倍时间。
- **反向救火**：已经联调撞坑时，按"错误 → Phase → 修复" 速查。

## 写码前第一步：过决策清单

本 skill 的模板**只给通用机制 + 字段获取方式**，不替你预设任何项目级取值。动手前先过
[references/network-decision-checklist.md](references/network-decision-checklist.md)，按三类标签把每个决策点定下来：

- `[①源码可定]` 读你项目 Android 源自查填；`[②需真包]` 抓真包验 / 无设备标待验；`[③策略待确认]` 先照搬 Android 原版行为兜底实现 + 留显式标记，待集成期 / 后端确认。
- **ledger 预填（v1.3，先做）**：工程内有 `spec/decision-ledger.md` 时（走过 a2h-plan grill #2 的项目必有），②③ 项**先查 ledger 的 D 编号决策与「事实」段**——上游 C17（API 契约不确定项）已收口的直接采用（来源标 D 编号），不重复问、不重新猜；同时读 `api-inventory.json` 的 `uncertainties[]`：`answered` 项直接采用其 `resolution`，`needs_capture` 项就是本 skill Phase 0.3 要抓包销账的清单。C17 收口流程见 [a2h-plan grill #2](../a2h-plan/references/grill-2-decision-gates.md) §7.2d。
- **铁律**：能从源码证明的才填，证不了的标记或待 verify，策略项先照搬兜底 + 留标记，**绝不拿默认值 / 空值兜底**。

> [references/templates/code/](references/templates/code/) 里凡 `<...>` 占位 / "照搬你项目" 注释处都是项目级，取值来自上面清单 —— 不要把占位当成品照抄。

## 流水线定位与上游 skill（先读这段）

本 skill 服务于 Android→HMOS 迁移流水线的 **`a2h-execute` 阶段**（最多向上联动 `a2h-plan`），负责「HMOS 侧网络层怎么 1:1 实现 + 字节级验证 + 联调不撞坑」。它**不是 spec 阶段工具** —— Android 侧的 API 静态清单由 spec 阶段的 **`android-api-inventory`** skill 负责抽取。

两者上下游配套、职责不重叠：

| skill | 阶段 | 回答的问题 | 产出 |
|-------|------|----------|------|
| `android-api-inventory` | spec | Android / HMOS 侧有哪些接口 / 怎么签名 / 第三方 SDK 鉴权方式（写 contract **`static`** 段） | `spec/baseline/api-inventory/api-inventory.{json,md}` |
| `arkts-network-troubleshoot`（本 skill）| execute | HMOS 侧怎么把这些接口跑通 + 启动期初始化 + 联调救火；抓真包写 **`runtime`** 段 + 产 **`reconciled`** DIFF | HttpClient / 拦截器 / SignUtil 实现 + 6 张对账表 + `api-contract-diff.md` |

**API contract 字段所有权**：`api-inventory.json` 每个 endpoint 为三段式（`static` / `runtime` / `reconciled`，schema 见 [android-api-inventory output_schema](../android-api-inventory/references/output_schema.md)）。`static` 由 `android-api-inventory` 写；`runtime`（抓包实测）与 `reconciled`（static↔runtime DIFF）由本 skill 写 —— 两个 skill 不抢写同一段。

**复用约定**：进入 Phase 0 / Phase 1 前，先看工程内有没有 `spec/baseline/api-inventory/`：

- **已存在** → 把 `api-inventory.json` 的 `static` 段当作 URL / 第三方鉴权 / base_url 对账的事实源直接读入；phases.md 中 Phase 0.2、1.1、1.4 的 Android 源码 grep 命令降级为**补漏与交叉校验**，不要从零重抽。Phase 0.3 抓包后按 endpoint key 回填 `runtime` 段，Phase 1.7 比对产 `reconciled` DIFF。**v1.3 追加**：同时读三个顶层段——`auth_model`（Phase 1.8 鉴权链路对账与 Phase 2/4/5 的 token 相关实现直接以它为 Android 侧事实源）、`data_flows`（Phase 5 UI 订阅审查的链路清单）、`uncertainties[]`（`needs_capture` 项 = Phase 0.3 的定向抓包清单；抓到证据后**销账**：`status → resolved`、`resolution` 填实测值、`resolved_by` 填 `runtime <endpoint> @日期`，并同步更新 `spec/decision-ledger.md` 对应条目状态）。
- **不存在** → 按 phases.md 原流程用 grep 自抽，Phase 0/1 本身即是完整自洽的闭环；此时 6 张对账表即对账主产物。

### 被流水线调用时的执行路径（Base-3）

被 `a2h-execute` 的 Base-3 Network 任务调用时，**不做下文「选择使用姿势」的交互式场景判断** —— 固定走 Phase 0 → 5：

```
Phase 0 抓证据 → Phase 1 Spec 对账（6 表 + 1.7 contract DIFF + 1.8 鉴权链路）→ Phase 2 启动期
  → Phase 3 SignUtil → Phase 4 响应 unwrap → Phase 5 UI 订阅
```

- **产物落点**：6 张对账表 + `api-contract-diff.md` 落 `spec/baseline/`；HttpClient / 拦截器 / SignUtil / PlatformInfo 按 [references/templates/code/](references/templates/code/) 实例化落 HMOS 工程。
- **设备依赖边界**：Phase 0.2 / 1 / 2 / 4 / 5 是纯静态分析 + 编码，**无需设备，Base-3 全程可跑完**。需要设备的步骤 —— **Phase 0.3 真机抓包**、**Phase 3 签名 200 实测**、**Phase 6 联调** —— 流水线无设备时标记「待 a2h-verify 阶段补做」，不阻塞 Base-3 交付（SignUtil 仍按 sign-algorithms 表 + 离线 `verify-sign.js` 落代码，真机字节验证延后）。
- 交互式场景 A/B/C/D 的姿势选择只用于**手动**调用本 skill。

## 选择使用姿势

> **手动调用**才在此选场景；被 `a2h-execute` Base-3 调用时直接走上文「被流水线调用时的执行路径」，跳过本节。

### 场景 A：正向预防（新项目 / 项目初期）

触发条件：
- 用户刚进入 a2h-execute 阶段的网络层迁移（Stage 2 Feature Base），准备 1:1 实现拦截器 / 签名 / HttpClient
- a2h-spec / a2h-execute 还未跑或刚跑完，准备进 Stage 2 网络层
- 项目还没到联调阶段
- 用户问"网络层迁移有哪些必查项"/"启动期要做什么初始化"

**行动**：读 [references/phases.md](references/phases.md)，从 Phase 0 顺序往下走：

- Phase 0 抓证据 → Phase 1 Spec 对账（6 张表）→ Phase 2 启动期初始化 → Phase 3 字节级加密验证 → Phase 4 响应 unwrap + 字段镜像 → Phase 5 UI 响应式订阅 → Phase 6 联调实测

每个 Phase 是闭环：检查项 + 工具命令 + 失败对策 + 通过标准。**前一 Phase 不通不要跳下一 Phase**。

### 场景 B：反向救火（联调出错）

触发条件：用户已经在跑联调，给了具体错误日志或症状。

**行动**：

1. **先读 [references/error-lookup.md](references/error-lookup.md)** — 用错误日志关键词反查 Phase
2. 跳到 [references/phases.md](references/phases.md) 对应 Phase 章节按检查项排查
3. 如需通用陷阱说明，看 [references/pitfalls.md](references/pitfalls.md) 对应大类（A-H）

**关键**：救火模式下也要遵循 Phase 隔离原则。修复完后**回到 Phase 6** 重新跑同条链路验证 → 再继续下一个问题。

### 场景 C：跨场景混合

最常见：用户已经走完一部分 Phase 但联调时冒出新错。

**行动**：用救火表先解临时阻塞，标记残留 Phase 任务，闭环完整个 Phase 再继续 spec 工作。

### 场景 D：standalone API 报告模式（不走迁移）

触发条件：用户只要一份 Android 侧 API 报告（接口盘点 / 后端对接 / 迁移前评估），**不实现 HMOS 网络层**。

**行动**：

1. 确认工程内已有 `spec/baseline/api-inventory/api-inventory.json`（`android-api-inventory` 产的 `static` 段）；没有则先跑 `android-api-inventory`。
2. 只跑 **Phase 0.3 抓真包** + **Phase 1.7 contract DIFF** —— 抓包结果按 endpoint key 回填 `runtime` 段，比对 `static` 产 `reconciled`；`uncertainties[]` 中 `needs_capture` 项一并销账（v1.3）。
3. **跳过 Phase 2-6 的 HMOS 实现 / 联调** —— 本模式产物定位为「Android 侧 API 运行时实况」，不是迁移代码。

产物：回填了 `runtime` / `reconciled` 的 `api-inventory.json` + `api-contract-diff.md` —— 即「静态 + 运行时实测」的完整 Android API 报告。

### 场景 E：spec 期 auth-chain 活性探针（probe · 无需设备）

触发条件：**spec 收尾、grill #1 之前**，验证登录链路是否真能打通。由 a2h-spec 在 `chain-auth` 生成后调用（execute 阶段无设备运行时、真机抓包多落空，故改"试发送"、且前移到 grill 前，让 execute 保持无阻断）。

**与场景 A–D 的区别**：不抓包、不需设备——**拿静态签名 + 设备替代值从零构造真实请求、打后端测试环境**，判**业务成功码**（非 HTTP 200）。直接证明"能不能构造一个后端接受的请求"这个终态。**不是单发——是有界自愈循环**：发→读业务错误→归类(客户端可调/后端/人输)→从源码派生候选调一个字段→重试，直到 code:0 或到上限跳过；成功回填真值+存 golden，novel 错误模式沉淀进知识库。把"人肉剥洋葱、发现一个门补一个 spec"的打地鼠自动化掉。

**前置**：`spec/baseline/dev_info.json`（测试 base_url + 业务成功码 + 测试账号）+ `spec/baseline/api-inventory/data-chains/chain-auth.md`（定靶子 + 公参字段的**值来源**）。缺 dev_info → 不静默跳过，产早期 grill 问题（`U-ENV`/`U-ACCOUNT`）。

**行动**：**MUST 读** [references/probe-runbook.md](references/probe-runbook.md)（循环骨架 + 错误三分类 + 候选来源约定 + 上限跳过 + 成功回填）+ [references/probe-error-remediation.md](references/probe-error-remediation.md)（错误→修法知识库，可增长）。复用 `scripts/verify-sign.js` 的签名实现。

## 关键执行原则

**1. 不要凭脑补猜后端契约。** 字段不一致时先回 Phase 0 抓真实抓包样本 + 找后端要 enum / DB schema。

**2. 不要跳 Phase。** 拦截器 unwrap 没修就实现业务 Service → service 拿到错对象 → 所有调用者都跟着错。

**3. 字节级问题需要 hilog 实测验证。** 不要假设 `util.TextEncoder.encodeInto` 返回独立 buffer，加 hilog 打 `byteOffset` / `buffer.byteLength` 看真实值。

**4. 任何"硬覆盖"必须 spec 登记。** 临时补丁必须在 `spec/baseline/decisions.md` 登记成本/回滚路径。

**5. 编译过 ≠ 运行通。** ArkTS 严格模式只能保证类型一致，业务码 / 字段 / 字节级行为都需要联调实测。

## 通用陷阱快速索引

详细解释看 [references/pitfalls.md](references/pitfalls.md)（9 大类 A-I），按出现概率排序：

### 100% 必撞

- **B1** ArkTS 没有 @SerializedName — JSON 字段镜像必须显式做
- **B2** JSON.parse as T 不安全 cast — class method / setter 静默失败
- **B3** AppStorage dot-notation 不展开 — `'userData.token'` 永远 undefined
- **B4** 行内 `{}` 禁止 — 必须 new Object() 或 interface
- **B7** V2 @ObservedV2/@Trace 实例不可入 V1 AppStorage — token/状态走 V2 单一源（AppStorageV2.connect），别建 V1 镜像
- **C1** onCreate 不能 async + PreferencesUtil race — 必须 sync onCreate + async onWindowStageCreate
- **C2** AppStorage 必备 key 未注入 — context / isDebug / mHttpUrl
- **D1** ResponseInterceptor unwrap 缺失 — Android 隐式 unwrap data，HMOS 必须显式
- **D2** URL 路径常量化抽取漏前缀 — `/user/` `/system/` 等命名空间易丢
- **D3** Request body 字段抽取不全 — Tools.kt 函数内字段易漏
- **E1** 登录态用 @Prop 反模式 — 应该 @StorageProp 自治订阅
- **I1** `response.result` 三态未指定 `expectDataType` — 编译 PASS / BUILD 成功 / 但所有接口走 exception（HMOS NetworkKit 自动 parse 行为与 OkHttp 不同）
- **I3** `JSON.parse('')` 抛 SyntaxError — HTTP 200 + 空 body 时误判为 exception；必须 length 守卫
- **I4** 缺 `ohos.permission.INTERNET` — 编译过但请求未发出即被拒；module.json5 必须显式声明（Android 习惯易漏）

### 90% 高概率撞（加密 / 后端契约 / 用户系统）

- **A1** buffer.from 返 pool 整段 — 凡加密签名工程
- **A2** createSymKeyGenerator algName 兼容性 — 凡 HMAC
- **A3** hex 大小写边界 — 凡 ≥2 套签名链路
- **D4** 公参字段不全 / 后端 schema 约束 — 凡有用户系统
- **D5** App ID 不对齐 — 凡 Android 已上线 + HMOS 新建脚手架
- **D4b** 字段缺等价"照搬 Android + 留标记"、禁静默空 — 凡公参含 HMOS 无等价字段
- **D4c** guest/匿名态 -1001 不清 token — 仅 bound 账号（userState≥2）失效才登出

### 50%-30% 中低概率撞

- B5 bundleInfo.label 资源引用未解析
- F1 productFlavor → HMOS 替代
- G2 OAuth SECRET 在客户端反模式
- G3 设备唯一标识无 1:1 等价 — `@kit.AdsKit` `identifier.getOAID()`（拒绝授权返全 0）+ 首启 UUID 持久化兜底
- H1 HAR 资源命名空间冲突

## 工程产出物结构

按本 skill 走完一遍 Phase 0-1 后，应在工程内得到：

```
spec/baseline/
├─ android-network-files.md       Phase 0.2
├─ sample-requests.md              Phase 0.3
├─ url-mapping.md                  Phase 1.1
├─ request-bodies.md               Phase 1.2
├─ json-field-mapping.md           Phase 1.3
├─ sign-algorithms.md              Phase 1.4
├─ platform-info.md                Phase 1.5
├─ product-config.md               Phase 1.6
├─ manifest-metadata.md            Phase 1.6
├─ auth-chain.md                   Phase 1.8（v1.3：鉴权/登录链路对账，token 生命周期六要素）
├─ backend-contracts.md            Phase 0.6
├─ api-contract-diff.md            Phase 1.7（static↔runtime DIFF 报告）
└─ api-inventory/
   └─ api-inventory.json           Phase 0.3 回填 runtime 段 + 销账 uncertainties / Phase 1.7 回填 reconciled 段
```

> 6 张对账表（url-mapping … product-config）是 `api-inventory.json` 这份 endpoint-keyed contract 的「按维度投影」—— contract 是主存储，6 表是派生视图（见 [phases.md](references/phases.md) Phase 1 开头）。工程内无 `api-inventory.json` 时，6 表即对账主产物。v1.3 增设**第 7 张专项表 `auth-chain.md`**（Phase 1.8）：`auth_model` 段的按维度投影，登录链路打通的对账主表；无 `api-inventory.json` 时按 phases.md §1.8 的 grep 自抽。

Markdown 模板见 [references/templates/spec-baseline.md](references/templates/spec-baseline.md)。

代码模板见 [references/templates/code/](references/templates/code/) —— **只含通用机制 + 字段获取方式**；凡 `<...>` 占位 / "照搬你项目" 处为项目级，按决策清单填，勿照抄占位当成品。

## 5 天上手节奏（新项目）

- **Day 1**: Phase 0 抓证据 + Phase 1.1/1.2 URL/body 对账
- **Day 2**: Phase 1.3-1.6 剩余 4 张表 + Phase 1.8 鉴权链路对账（auth-chain.md）
- **Day 3**: Phase 2 启动期模板 + Phase 3 SignUtil + Phase 4 HttpClient.unwrap
- **Day 4**: 按 spec 1:1 写业务 Service / Repository / ViewModel
- **Day 5**: Phase 5 UI 订阅审查 + Phase 6 联调实测

**期间不要跳步**。每个 Phase 验证通过再下一步，比"全做完一次性测"快 3 倍。

## 工具速查

- **网络层决策清单（写码前第一步：通用机制 vs 项目级决策，三类标签）**：[references/network-decision-checklist.md](references/network-decision-checklist.md)
- 错误码 → Phase 反查表（含官方 2300xxx / 1762xxxx 权威错误码轴）：[references/error-lookup.md](references/error-lookup.md)
- 网络栈选型（裸 http vs rcp 拦截器/会话模型，API 12+）：[references/http-vs-rcp.md](references/http-vs-rcp.md)
- 抓 Android 真实请求日志（3 方法 + 前置闸门 + 隐私门处理）：[references/capture-android-traffic.md](references/capture-android-traffic.md)
- 明文 HTTP 抓包代理（零依赖，抓完整 headers+body，对账签名头/请求时序）：[scripts/http-capture-proxy.js](scripts/http-capture-proxy.js)
- 签名算法离线验证脚手架（拿真实抓包逐字节核对，验证后再实现）：[scripts/verify-sign.js](scripts/verify-sign.js)
- **auth-chain 活性探针 Runbook（场景 E，spec 期无设备试发送验登录链路 + golden fixture 交接）**：[references/probe-runbook.md](references/probe-runbook.md)
- 冷启动日志 → 有效请求提炼脚本：[scripts/extract_startup_requests.py](scripts/extract_startup_requests.py)
- Phase 6 HMOS 联调操作手册（编译→装包→冷启→过隐私门→抓包对账）：[references/phase6-runbook.md](references/phase6-runbook.md)
- hilog grep / Android src 扫描命令：[references/grep-cheatsheet.md](references/grep-cheatsheet.md)
- spec 对账表模板：[references/templates/spec-baseline.md](references/templates/spec-baseline.md)
- 代码模板：[references/templates/code/](references/templates/code/)
