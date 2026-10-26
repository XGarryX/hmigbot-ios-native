---
name: android-api-inventory
description: '从 Android 或 HarmonyOS 源码中提取所有外部 API 使用清单（HTTP REST、WebSocket、SSE、第三方 SDK），生成结构化文档。平台参数化（platform: android | harmony，可自动探测）。当用户需要梳理 Android / 鸿蒙项目的接口使用情况、检查 API 覆盖度、准备迁移前的接口规格、做鸿蒙增量开发的接口盘点、或说"梳理接口"、"API清单"、"接口文档"、"有哪些API"时，务必触发此 skill。即使用户只说"看看用了哪些接口"或"接口梳理"，也应触发。'
metadata:
  type: domain
  domain: migration
  tags:
  - domain
  - analysis
  - migration
  - api
  version: v1.3
---
# API Inventory（android-api-inventory）

从 **Android 或 HarmonyOS** 源码中系统提取所有外部 API 调用，生成**项目定制**的接口清单文档，供迁移规划、HarmonyOS 侧接口对接、鸿蒙增量开发的接口盘点使用。

> **关于 skill 名**：本 skill 已平台参数化（支持 `platform: android | harmony`），但目录与 `name` 仍沿用历史名 `android-api-inventory`，以保持 `a2h-spec` 等上游引用稳定。命名是历史包袱，能力不受限 —— 调用时用 `platform` 参数选平台即可。

## 设计理念

**脚本管"找到"，模型管"理解"；编目（inventory）平台参数化。**

- **Phase 1**（脚本，**平台专属**）— 纯机械扫描。`platform: android` → `extract_android_apis.py`（Retrofit/OkHttp）；`platform: harmony` → `extract_arkts_apis.py`（@kit.NetworkKit / ApiService URL 常量 / HttpInterceptor / ArkTS Bean）
- **Phase 1b**（补扫框架）— 「按技术栈选 grep 策略」框架，两平台共用
- **Phase 2-4**（模型，**平台无关**）— 基于扫描结果做**项目定制**的语义分析、文档组织和交叉验证

Phase 2-4 不使用模板或字典——每个项目都由 模型根据该项目的**实际情况**组织文档结构、撰写描述、关联 Feature。这套语义层对 Android 与 ArkTS 同样成立，因此一次 run 只编目**一个**平台（`platform` 决定 Phase 1 用哪个 scanner），Phase 2-4 逻辑共享。

> **边界（重要）**：本 skill 只做「编目（inventory）」，平台参数化的也只是编目。Android↔HMOS 的双边**对账（reconciliation / diff）不属于本 skill** —— 那归 `arkts-network-troubleshoot`（它写 contract 的 `runtime` + `reconciled` 段）。编目可泛化，对账不并入，两者别混。

## 何时使用

- Android→HarmonyOS 迁移前的接口盘点（`platform: android`）
- 鸿蒙增量开发：在已有 HMOS 工程上盘点接口 / 审计 API 覆盖度（`platform: harmony`）
- 检查 spec 中 API 覆盖是否完整
- 需要一份完整的接口规格文档供后端/前端对接
- 审计项目中所有的外部通信点

## 输入

1. **源码路径** — Android 或 HarmonyOS 工程根；优先从 `.agents/settings.local.json` 或项目 AGENTS.md 中读取，用户也可手动指定
2. **platform** — `android` | `harmony`；不指定则**自动探测**：源码根有 `build.gradle` / `settings.gradle` → `android`；有 `build-profile.json5` / `oh-package.json5` → `harmony`。两者都有（迁移工程同仓）时按用户意图取，默认 `android`
3. **输出目录** — 默认 `spec/baseline/api-inventory/`，与 a2h-spec 产出同级
4. **现有 spec 产物**（可选）— `spec/baseline/feature-index.md`、`spec/baseline/features/F0xx-*.md`、`spec/baseline/feature-base.md` 用于交叉引用
5. **hmos_references_file**（可选 · 仅 `platform: android` 有意义）— 用户预知 HarmonyOS 等价物参考文档，通常是 `spec/ref/hmos-references.md`，由 a2h-spec Step 3.0c「用户预知阶段一」收集。提供时触发 **Phase 2.5 等价物预标注**，把命中信息追加到 markdown 输出。**仅消费、不修改**该文件；本 skill 也**不**因此变更 `api-inventory.json` schema
6. **backend_facts_file**（可选 · v1.3）— 用户预知的**后端契约**参考文档，通常是 `spec/ref/backend-facts.md`，由 a2h-spec Step 3.0c2「后端契约预知收集」产出（接口文档 / Postman / Swagger 链接、响应壳约定、业务成功码与 token 失效码、关键接口必填字段与 enum）。提供时 Phase 3 生成 `uncertainties[]` 前先拿它**预销账**：能直接回答的不确定项建为 `answered`（`resolved_by` 标该文件 section），不留给下游 grill 重复问。**仅消费、不修改**该文件

## 执行流程

### Phase 1：脚本化机械扫描（按 platform 分派）

先确定 `platform`（输入未给则按 ## 输入 的探测规则判定），再运行对应平台的 scanner。

**`platform: android`** — Retrofit/OkHttp 项目：

```bash
python .agents/skills/android-api-inventory/scripts/extract_android_apis.py \
  --source-dir "<source_root>" \
  --output-dir "spec/baseline/api-inventory"
```

**`platform: harmony`** — HarmonyOS ArkTS 项目：

```bash
python .agents/skills/android-api-inventory/scripts/extract_arkts_apis.py \
  --source-dir "<source_root>" \
  --output-dir "spec/baseline/api-inventory"
```

两个 scanner 产出**同结构**的 `raw_apis.json`：
- `platform`（本次扫描平台）
- `services`（Service 类 + endpoint 列表 + 参数；v1.3 endpoint 含 `static_headers`（@Headers 注解）/ `path_is_dynamic`（@Url 动态 URL）/ `callers`（调用点回溯，见下））
- `base_urls`（Base URL 配置；v1.3 含 `environment: build-config` 的 BuildConfig 动态拼接来源）
- `url_constants`（路径常量引用→实际路径映射，已自动解析）
- `api_related_constants`（**非路径**的 API 类常量：header 名 / 请求字段名 / 状态·错误码 / appKey·appId·secret 等；预分桶 `header` / `param` / `code` / `app_secret` / `other`，模型可按文件位置再分类）
- `hardcoded_urls`（第三方/硬编码 URL）
- `third_party_domains`（按域名聚合的第三方调用）
- `interceptors`（**v1.3 起两平台均有**：Android 侧抽 `: Interceptor` / `implements Interceptor` 实现类并打 evidence 标签（token_injection / signing / common_params / body_rewrite / logout_kick），HMOS 侧抽 `implements HttpInterceptor` —— 都是 Phase 2.75 auth_model 的首要素材）
- `body_assembly_sites`（**v1.3 Android 专有**：Retrofit 接口之外的请求体组装点 —— `mutableMapOf("k" to v)` / `JSONObject().put` / `FormBody.Builder().add`，含所在函数与字段表；防 pitfall D3「Tools.kt 常量字段漏抽」）
- `gradle_config`（**v1.3 Android 专有**：`buildConfigField` / `manifestPlaceholders` / `applicationId` / flavor 等构建期注入行 —— 网络层运行时消费的配置来源）
- `bean_classes`（HMOS scanner 专有：ArkTS class Bean 字段表 —— ArkTS 字段名即 JSON key，供 模型填 `response` 结构）

**两平台 Phase 1 是两套独立 scanner**（不是「再加个 grep 策略」）：
- Android scanner 认 Retrofit 注解（`@POST`/`@GET` + `@Field`/`@Body`）—— 声明式，endpoint 易抽。**v1.3 泛化**：Kotlin 与 **Java 接口**（`Call<T> login(@Field ...)`）都认；`@GET` 裸注解 + `@Url` 参数的动态 URL 端点标 `path_is_dynamic`；扫描后做**第二遍调用点回溯**（每个 endpoint 方法在非 Service 文件中的 `.methodName(` 调用位置写入 `callers`，供 Phase 2.75 重建数据链路）。
- HMOS scanner 认 `@kit.NetworkKit` 的 `http`、`ApiService` 里的 `const URL_*`、`implements HttpInterceptor`、ArkTS class Bean —— HMOS 网络调用是命令式，endpoint 靠「URL 常量 + 调用点」拼。
- **关键差异**：ArkTS 无 `@SerializedName`，class 字段名默认即 JSON key；HMOS scanner 抽响应结构时直接取字段名，不套 Android 的 Gson 别名机制。

**适用前提**：scanner 针对各平台主流网络栈设计。其他技术栈需要 Phase 1b 补扫。

### Phase 1b：补充扫描判定与执行

> **平台说明**：下文规则 A 的 `import retrofit2` 探测、「裸 OkHttp / Ktor」grep 策略是 `platform: android` 的写法。`platform: harmony` 时规则 A 改探测 `@kit.NetworkKit` / `http.createHttp`（零命中说明项目无 HTTP 网络层）；「按技术栈选 grep 策略」这个**框架**两平台通用，HMOS 侧补扫目标换成 `@kit.NetworkKit` 的 WebSocket / 三方 SDK 即可。

#### 判定：是否需要补扫？

脚本跑完后，模型按以下**具体规则**决定下一步（不要凭感觉判断）：

**规则 A — 完全跳过 Phase 1，直接做 Phase 1b**

先在源码根跑一次快速探测（一个 Grep 够了）：
```
Grep "import retrofit2" in source_dir
```
如果**零命中**，说明项目根本不用 Retrofit，Phase 1 注定跑空。此时直接进 Phase 1b。

**规则 B — Phase 1 跑完后判断是否补扫**

看 raw_apis.json 的四个数字：

| 情况 | services 数 | hardcoded_urls 数 | 处置 |
|------|------------|-------------------|------|
| 正常 Retrofit 项目 | ≥ 3 | 任意 | Phase 1 已足够，进 Phase 2 |
| Retrofit + 裸 HTTP 混合 | ≥ 1 | ≥ 5 且多数未归属到 services | Phase 1 + 补扫裸 HTTP |
| 非 Retrofit 项目 | 0 | ≥ 1 | 进 Phase 1b 全量补扫 |
| 离线 / 无网络项目 | 0 | 0 | 跳过 Phase 1b，直接 Phase 3 输出"本项目无外部 API"文档 |

"hardcoded_urls 未归属到 services" 的判断：hardcoded_urls 里的 URL 如果不在任何 service 的 endpoint path 里出现，就是未归属的——这些是裸 HTTP 或第三方 SDK 调用。

#### 执行：Phase 1b 补扫什么

按项目技术栈选 grep 策略（不要全部跑，按 `build.gradle` 实际依赖筛选）。**完整 grep 关键字表 + HMOS 侧对应物 + 补扫产物落地方式**见 [references/phase1b-grep-strategies.md](references/phase1b-grep-strategies.md)。

涉及范畴：裸 OkHttp / Ktor / WebSocket / SSE / GraphQL / gRPC / SDK 黑盒。

#### 极端情况的降级

**规则 C（React Native / Flutter 壳 / 离线项目）**：详见 [references/phase1b-grep-strategies.md §极端情况降级](references/phase1b-grep-strategies.md#极端情况降级规则-c)。简言之：RN/Flutter 壳跳过 Kotlin 扫描产说明文档；离线项目跳过 Phase 1b 直产「无外部 API」文档。

### Phase 2：项目上下文理解

模型读取扫描结果后，做以下判断：

1. **识别项目技术栈** — 纯 Retrofit？混合 Retrofit+裸 OkHttp？SDK 主导？离线应用？
2. **识别业务模块划分** — 从文件路径、包名、module 归属推断业务域
3. **识别认证方式** — 读 Interceptor 源码：Token 注入？自定义签名（AWS-style/XXTEA/HMAC）？Bearer？多套并存？
4. **识别第三方 API 分组** — 把同域名/同 provider 的调用聚合（Volcano Engine、OpenAI、字节 TTS 等）
5. **读取现有 spec 交叉参考** — 如果 `spec/baseline/features/` 存在，读每个 F0xx 文件的 "API Endpoints" 表，建立路径→Feature 映射
6. **识别 URL 常量层级** — 从 `url_constants` 推断常量命名约定（`UserUrl.xxx`、`PayUrl.xxx`），作为模块/域划分依据

这一步**不输出文件**，是 模型构建"项目心智模型"的过程。

### Phase 2.5：HarmonyOS 等价物预标注（platform: android 时执行）

**目的**：把「这个 Android API 在鸿蒙用什么」的已知答案**就近落到本 skill 的 markdown 输出**，避免下游 a2h-plan grill #2 阶段二再重复问同样的 SDK / API。两个子步来源不同、互补，落同一个提示段。

#### 2.5a 框架 API 基础映射（无条件 —— `platform: android` 即执行）

**MUST 读** [references/framework-kit-mapping.md](references/framework-kit-mapping.md)（经 harmony-docs 官方快照逐条核验的静态映射表，**零运行时依赖**，无需用户输入），把扫描结果中的**标准框架栈**写入「已命中」表，来源列固定填 `framework-kit-mapping.md`：

- 网络栈：Retrofit/OkHttp → NetworkKit `http` 或 rcp（有拦截器架构时优先提示 rcp）；WebSocket → `webSocket`；SSE → 流式自实现（`migration_concerns` 必标）
- 序列化：`@SerializedName` → **无等价**（字段镜像，`migration_concerns` 必标）；加密签名：javax.crypto → `@kit.CryptoArchitectureKit`
- 存储：SharedPreferences → `preferences`；Room → `relationalStore`；下载 → `request.agent`
- 设备标识：ANDROID_ID → **无 1:1 等价**（UUID 持久化）；OAID → `@kit.AdsKit`

> 「无等价 / 无官方 Kit」的条目**也要写入提示段**——它们正是迁移关注点素材，不要因"没有对应物"跳过。三方 SDK（微信/支付宝/个推等）不查映射表，归 2.5b。

#### 2.5b 三方 SDK 等价物（hmos_references_file 时追加）

把用户在 a2h-spec Step 3.0c「用户预知阶段一」提供的 HarmonyOS 资料（厂商手册 / 内部镜像 / 总索引）匹配进同一提示段。

**触发条件**（全满足才执行 2.5b，否则只跳过本子步、2.5a 不受影响）：
1. `platform: android`（HMOS 自身工程不需要等价物提示）
2. 输入参数包含 `hmos_references_file`
3. 该文件存在且可读

**强制约束**：
- **不动 `api-inventory.json` schema** —— 任何 entry（service / endpoint / third_party_apis）**不新增字段**
- 等价物提示只以"附加 markdown 段"形式落到 `api-inventory.md`（**只追加到总览索引文件，不下沉到 `apis/*.md`**，避免分层场景多处重复）
- 该 markdown 段是**提示性内容**，下游消费方（a2h-plan grill #2 Step 0）通过读 markdown 或直接读 `hmos_references_file` 都能消费，**不形成新的 JSON 数据契约**

**流程**：

1. **读 hmos-references.md 三段**：
   - 总索引（通用 HarmonyOS API 文档入口 / ArkTS 手册 / 内部 Wiki）
   - 厂商迁移指南（按 SDK 名：微信 / 支付宝 / 华为账号 / 火山引擎 / 个推 / ...）
   - 内部资源（私有镜像 / 合作方未公开版本 / 内部已迁移过的方案）

2. **匹配本次扫描结果**（基于命名 / 域名 / SDK 标识 / build.gradle 依赖名）：
   - `services` 中各 Service 类与 `third_party_apis` 的 `provider` → 优先匹配「厂商迁移指南」段的 SDK 名
   - `third_party_domains`（按域名聚合）→ 优先匹配厂商迁移指南的域名（如 `weixin.qq.com` 对应微信条目）
   - 认证拦截器 / 网络层基础设施（如自定义签名）→ 匹配「总索引」段
   - 完全无法对应的扫描项 → 跳过本步骤，不强行猜测

3. **追加 markdown 段到 `api-inventory.md` 末尾**（在「Feature 候选建议」之后，如有；否则在文档末尾）。段标题固定为 `## HarmonyOS 等价物提示（来自 spec/ref/hmos-references.md）`，含三个子段：**已命中** / **未命中** / **参考未触及**。完整 markdown 模板与子段填法见 [references/templates/hmos-hint-section.md](references/templates/hmos-hint-section.md)。

4. **降级路径**：
   - `hmos_references_file` 不存在或为空 → 仅跳过 2.5b；**2.5a 框架命中非空时仍写提示段**（只含框架命中 + 未命中三方清单）
   - 文件存在但与扫描结果零交集 → 仍写本段：框架命中（2.5a）照常，三方部分只列「未命中」与「未触及」两个子段

5. **不影响其他 Phase 输出**：Phase 3 的 `api-inventory.json`、`common.md`、`apis/*.md`、`raw_apis.json` 都不因为本 Phase 而改变；本 Phase 仅向 `api-inventory.md` 追加一段。

**为何不下沉到 `apis/*.md`**：等价物提示是按 SDK / provider 粒度的（不是按 endpoint），落到模块文件会重复 N 份；放总览索引文件一处即可，下游 grep 范围明确。

**为何不动 JSON schema**：每个 endpoint 上的 `hmos_equivalent_hint` 字段会变成新的契约,引入下游消费方对该字段的依赖,后续要演进 schema 时拖累整个三段式 contract 体系。当前需求仅是"让用户预知信息别白填",markdown 提示已足够;真要做结构化 contract 是另一件事（属 `arkts-network-troubleshoot` 的 reconciled 段或新 skill 范畴）。

### Phase 2.75：鉴权模型与数据链路追溯（v1.3 新增）

**为什么需要**：登录类功能打不通的缺口不在接口清单，而在机制层（login.md 复盘实证）——token 从哪来、存哪、谁注入、什么码判失效、身份模型是什么，这些藏在拦截器和 Repository 里，端点级编目看不到。本 Phase 把它们抽成 `api-inventory.json` 的两个顶层段（schema 见 [references/output_schema.md](references/output_schema.md) §v1.3 顶层段）：

**2.75a `auth_model`（必产，`platform: android` 时）**

沿 raw_apis.json 的线索读源码 + **按 [references/phase1b-grep-strategies.md](references/phase1b-grep-strategies.md) §auth 链专项 grep 字典逐层主动 grep**（补捕获盲区，尤其 L2 签名/加密、L3 设备身份——治 fitness"19 header 抽 0 签名"整层漏抓），重建鉴权链路六要素 + 轴分类：

1. **token 获取**：从 `endpoints` 里找 auth 类端点（initUser / login / oauth 等命名 + feature 候选归类），记 `token_acquisition`
2. **token 存储**：顺 `endpoints[].callers` 找响应写入点（MMKV / SharedPreferences key），记 `token_storage`
3. **token 注入**：读 `interceptors` 中带 `token_injection` / `signing` evidence 的拦截器源码，记 `token_injection`（位置 header/body + 具体名字）
4. **token 失效**：`api_related_constants[code]` 的负值码 + 拦截器 `logout_kick` evidence 处的判定逻辑，记 `token_expiry`（码 + 适用范围 + 动作 —— 注意 guest/bound 态差异，pitfall D4c）
5. **token 清除**：退出登录 / 注销 / 被踢的清除路径，记 `token_clearing`（清什么、**留什么**——deviceNo 类设备级字段通常保留）
6. **身份模型**：判定 `identity_model`（device-bound / account-only）——游客登录的语义是"新建游客"还是"拿回设备身份"？有无不可逆边（首绑手机号后回不到游客态）？判不出填 `unknown` 并建 uncertainty（② 类）
7. **轴 A/B/C 分类**：据上述证据填 `axis_a_guest_token_role`（游客 token 角色）/ `axis_b_device_role`（设备对登录的作用，数组可多占）/ `axis_c_login_methods`（登录方式子集）——把机制显式化，供 Phase 2.8 `chain-auth` 分支；对不上已知分支即 novelty 冒泡建 uncertainty（详见 output_schema §auth_model 轴说明）

**每个要素读不到就显式填 `unknown` + 建 uncertainty，不许省略字段** —— auth_model 的"空洞"正是 grill 要问的题目。

**2.75b `data_flows`（auth 链必产，其他链路按重要度可选）**

基于 `endpoints[].callers` + `body_assembly_sites` 顺调用链读源码，重建「endpoint → Repository → ViewModel → 存储/UI 副作用」的链路叙事。`chain: "auth"` 强制产出；支付、启动配置等链路按 `feature_candidates` 重要度选做。这是下游 `arkts-network-troubleshoot` Phase 5（UI 响应式订阅）与 Phase 2（启动期时序）的直接输入。

**产物落点**：两段写入 `api-inventory.json` 顶层；人类可读投影落 `common.md` §鉴权链路（分层形态）或单文件的「公共约定」段。

### Phase 2.8：数据链路契约生成（chain-auth）

**为什么需要**：`auth_model`/`data_flows` 把登录机制抽成了 JSON，但那是 API 视角、且散点；登录链路是**横切 L0–L7、跨 feature/base** 的整体，需要一份"逐层点名 owner + 标捕获/接线 + 定 probe 靶子"的契约——既当实现 SOP，又当**完整性兜底**（对抗 feature 分解漏层，尤其漏 L1 隐私）。**平台 `android` 时必产 `chain: auth`。**

**MUST 读** [references/templates/chain-contract-template.md](references/templates/chain-contract-template.md) 作骨架，逐步：

1. **投影 API 层**（L0 base_url / L2 / L3 / L4 / L5 / L6）：来自本次 `auth_model`（含轴 A/B/C）+ `data_flows.chain=auth` + `base_urls`——**只投影、不重新捕获**（单一源 = api-inventory.json，护栏1）。
2. **非 API 层交叉核 owner**（L1 隐私 / L0 应用身份，`auth_model` 不覆盖）：grep `feature-index.md` 找 owning feature——**无 owner → RED**（护栏2）。api-inventory 天生不编目隐私门控，此步补盲区。**`feature-index.md` 尚未生成时**（B-API 并行轨 / 分支 C，此时 feature 文档还没产出）→ 改用**源码交叉核**：grep 隐私门控/启动初始化的实现位置，判它归属哪个 Activity/模块；**碎片化于多个基类/多标志位而无单一 owner → RED**（scope=chain-owner，喂 grill）。
3. **逐层填两列** `[捕获? | 消费/接线者]`：一层多机制（L2 签名 / body 加密 / 防重打包）**拆子行**；`平台替代` 层填 `backend-contract`（未对齐 → 🔴 `BLOCKED-PENDING-BACKEND`，禁"传空串兼容"软化措辞）；`契约照搬` 层字节真值缺失标 `MISSING-TRUTH`（值在源码、非占位）。
4. **5.2b 跨层依赖 + 链内时序**：门控（L1 门控 L2/L3 的 SDK init）、供数+时序（如 deviceNo 掺进签名、换 deviceNo 首请求不带 deviceNo）。
5. **RED → 共享 `uncertainties[]`**（不留 chain-auth 私有）：每条 RED 建为 uncertainties 条目，`chain=auth`；`scope` 用 `chain-owner`（L1/身份 owner 缺）或复用 `auth_model`（API 层）；probe 前置缺失（`dev_info.json` 无成功码/base_url）建 `U-CODE`/`U-ENV`/`U-ACCOUNT`。答案回填走**重投影**（chain-auth 从更新后的 auth_model/uncertainties 重生成，不手改）。
6. **定 probe 靶子**：据轴A（有无游客 token 端点）/ 轴B（设备替代值）标出 probe 该打哪个端点——供 spec 收尾 `arkts-network-troubleshoot` 场景 E probe 消费。

**产物落点**：`spec/baseline/api-inventory/data-chains/chain-auth.md`（人类可读契约，是 auth_model 的 SOP 形态投影，单一源仍是 api-inventory.json）。summary 返回加 `chain_auth_red_count`。

### Phase 3：文档生成

模型根据 Phase 2 的理解，**现场撰写**输出文件：机器可读的 `api-inventory.json` + 人类可读文档（按项目规模决定单文件或分层，见 §3.2）。描述与组织应反映项目的实际特点，不套模板。

#### 3.1 api-inventory.json（机器可读）

结构参考 `references/output_schema.md`，核心字段：
- `platform`：本次扫描平台（`android` | `harmony`）
- `summary`：服务数、端点数、第三方数、模块列表
- `services`：按模块/Service 类组织的 API 接口树。**每个 endpoint 为三段式**：`static`（本 skill 写的静态契约）/ `runtime`（置 `null`，由 `arkts-network-troubleshoot` 抓包回填）/ `reconciled`（置 `null`，由其 DIFF 回填）
- `third_party_apis`：按 provider 聚合，含 auth_type、endpoints 列表
- `base_urls`：Base URL 配置（环境、来源文件）
- `coverage`：与现有 spec 的差异分析
- `auth_model` / `data_flows`（v1.3）：Phase 2.75 产出的鉴权链路与数据链路段
- `uncertainties[]`（v1.3，**强制**）：②③ 类不确定项结构化清单，见下方专节

**本 skill 只写 endpoint 的 `static` 段**，`runtime` / `reconciled` 一律置 `null` —— 字段所有权见 output_schema.md，不要替下游 skill 代填。

#### 3.1b uncertainties[] 生成（v1.3 强制）

Phase 2 / 2.75 / 3 全程遇到"拿不准"，**不要只在 md 里标 unknown 就完事** —— 逐条收进 `uncertainties[]`（schema + status 状态机见 output_schema.md §v1.3 顶层段三）。分级铁律：

- **① 源码可定** —— 不入清单。模型自答写进 `static` / `auth_model`。
- **② 需真包**（响应壳形状 / 字段真实类型与默认值 / 业务码语义 / header 大小写 / `model_class: unknown` 的响应结构 / 加密 body 内容…）—— 入清单，等 grill 索证或抓包销账。
- **③ 策略待确认**（包标识发哪个包名 / 联调期加密开关 / 多网关取舍 / HMOS 无等价公参字段的处置…）—— 入清单，grill #2 必问用户。

每条必填 `chain`（业务链路归属，auth 最优先）与 `impact`（不答会影响什么实现决策）——grill 按链路打包呈现时靠它们。**`backend_facts_file` 提供时先预销账**：能从该文件直接回答的项建为 `answered`（`resolved_by` 标文件 section），不留给 grill 重复问。

人类可读投影：`api-inventory.md` 末尾「## 不确定项清单（grill 输入）」段（`id | tag | 链路 | 问题 | 状态` 表，auth 链路置顶）。

**关键字段由 模型根据源码和 spec 填写**：
- `description`（中文功能说明）— 从方法名、参数、响应类型、调用上下文推断
- `feature_ids`（关联 Feature）— 通过调用方追溯到 Activity/Fragment/页面，对照 feature-index.md 归属
- `auth_type` / `auth_detail` — 读 Interceptor 定义推断
- `provider`（第三方分组名）— 根据域名和用途命名
- **`static.response`（响应结构）— 强制**：每个 endpoint 至少记 `model_class`（响应 Bean 类名）+ 字段表。Android 读 Bean 的 `@SerializedName`（JSON 名↔字段名）；ArkTS 无 `@SerializedName`，直接取 class 字段名为 JSON key。读不到 Bean 定义时（响应是泛型 / 动态类型）显式标 `model_class: "unknown"` + 原因，不要省略整个 `response`

#### 3.2 人类可读文档（按规模分层）

人类可读文档**不再固定单文件**——按项目规模选形态。详细结构与每个 API 的统一模板见 `references/output_schema.md`「api-inventory 文档结构」一节。

**第一步：拆分判定**

| 项目规模 | 产出形态 |
|---------|---------|
| 端点 ≤ ~15，或单 service | **单文件** `api-inventory.md`：内部用下述 API 模板逐个展开 + 一个「公共约定」段 |
| 端点 > ~15，或多 service | **分层**：`api-inventory.md`（索引）+ `common.md`（公共约定）+ `apis/<模块>.md`（每模块一文件） |
| 离线 / 无外部 API | 单文件 `api-inventory.md`，说明无外部 API + 列系统级依赖即可 |

**第二步：分层结构**（端点多时）

- **`api-inventory.md`** —— 总览索引：概览（技术栈 + 数据总览）、**文档导航表**（链接到 `common.md` 与各 `apis/*.md`，标注端点数）、网络层架构摘要、第三方 API、Feature 候选 / 覆盖度分析。**不放逐个 endpoint 明细**。
- **`common.md`** —— 公共约定：响应信封、签名头、**鉴权链路**（v1.3：`auth_model` 的人类可读投影）、**公共请求参数**（多端点复用的，如 `platformInfo`）、**共享响应体**（多端点复用的 Bean，如 `UserData`）、`BaseBean` 基类字段、业务状态码。文件名固定 `common.md`（**不加下划线前缀**——下划线在 Docusaurus 等工具里有"排除页面"的副作用）。
- **`apis/<模块>.md`** —— 每个 service / 功能域一文件，按代码的 Service 划分；过小的 service 合并；目标 5–10 个文件。文件名用业务域短名（如 `user.md`、`pay.md`）。

**第三步：每个 endpoint 的统一模板**（写进 `apis/*.md` 或单文件）

每个 `apis/*.md` 开头一张「端点速览表」（方法 / 路径 / 接口名 / runtime 状态），随后逐个 endpoint 按统一模板展开：

- **方法**：`HTTP方法 路径`（+ 协议 REST/SSE/WebSocket）
- **调用位置**：Service 方法（文件:行号）/ ViewModel / Feature ID
- **请求参数表**：`参数 | 类型 | 必需 | 说明`
- **响应参数表（强制表格化）**：`字段 | 类型 | 说明`；嵌套 Bean 逐层展开为子表；读不到 Bean 时标 `unknown` + 原因，**不省略**
- **runtime 状态**：⬜ static-only（本 skill 初版默认）/ ✅ verified / ⚠️ mismatch（后两者由 `arkts-network-troubleshoot` 抓包回填后刷新）
- **特殊标注**：suspend、multipart、分页、轮询等

**「合并一类」原则（关键）**：多个 endpoint 重复出现的请求参数（公参）、响应体（共享 Bean）、信封/签名 —— 在 `common.md` 写**一次**，各 `apis/*.md` 用链接引用（如 `→ 见 common.md`），不重复展开。这是分层的核心收益。

**允许并鼓励的叙事性内容**：第三方 provider 的业务角色说明、异步任务（submit→poll→result）流程、覆盖度分析的补录建议 —— 放进 `api-inventory.md` 索引或对应 `apis/*.md`。

### Phase 4：交叉验证（按 spec 是否存在分支）

本 skill 可以在两种时机运行：**spec 生成之后**（作为审计工具）或 **spec 生成之前**（作为输入源）。因此 Phase 4 不是单一流程，而是按 spec 状态分支。

模型进入 Phase 4 时，先检查 `spec/baseline/` 的存在情况，按下表选对应分支：

| spec 状态 | 判定方式 | 走哪个分支 |
|-----------|----------|-----------|
| 完整 spec 存在 | `feature-index.md` 和 `features/F*.md`（至少 1 个）都存在 | 分支 A：覆盖度审计 |
| 部分 spec 存在 | `feature-index.md` 存在但 `features/` 为空或只有少数 | 分支 B：增量对齐 |
| spec 尚未生成 | 无 `feature-index.md` 且 `features/` 下无 `F*.md`（不论 `spec/baseline/` 及其 `ui-manifest.md`/`ui-snapshots/` 是否已存在） | 分支 C：输入源模式 |

#### 分支 A — 覆盖度审计（spec 已生成）

这是原本的用法：拿扫描结果对照已有的 Feature Spec 找差异。

读取 `spec/baseline/feature-base.md` Section 2.2 和各 `spec/baseline/features/F0xx-*.md` 的 API Endpoints 表，与 inventory 对比：

- **missing_in_spec**：扫描发现但 spec 未记录 → 可能是 spec 遗漏或基础设施接口未细化，在 inventory.md 最后一节列出并给出建议
- **missing_in_scan**：spec 记录但扫描没找到 → 可能是路径拼写不同、SDK 封装、或真的遗漏了，需要 模型判断

把分析结果写入 `api-inventory.md` 的"覆盖度分析"一节，以及 `api-inventory.json` 的 `coverage` 字段。

#### 分支 B — 增量对齐（spec 生成中）

如果 `feature-index.md` 存在但 `features/F*.md` 还在逐个产出（仅手动在 a2h-spec Phase C 进行中调用本 skill 时才会命中；pipeline 的 B-API 并行轨因早于 feature 文档产出，永远走分支 C），做**部分对齐**：

- 对已经生成的 Feature 文件做分支 A 同样的对齐
- 对 feature-index 里列了但文件还没生成的 Feature，用 inventory 的 `feature_ids` 字段反推出"该 Feature 预期包含哪些接口"，输出到 `api-inventory.md` 的"Feature 待生成辅助"一节，作为 a2h-spec 后续生成那个 F 文件的素材
- coverage 字段里把这种情况标为 `pending_in_spec`（既不是 missing，也不是 documented，而是"spec 生成中"）

#### 分支 C — 输入源模式（spec 尚未生成）

**这是 a2h-spec Phase B 的 B-API 并行轨调用本 skill 时的标准分支**（详见下文「与 a2h-spec 的集成契约」）。没有任何现成 feature 文档可对照，Phase 4 转变角色：从"审计者"变成"feature 候选建议者"。

具体做什么：

1. **按路径前缀聚类端点** — 自动提议 feature 候选。例如：
   - `/user/*` (12 个端点) → 候选 Feature: "User Authentication & Account"
   - `/pay/*` + `/product/*` (13 个端点) → 候选 Feature: "Payment & VIP Subscription"
   - `/asset/*` + `/productComm/*` (10 个端点) → 候选 Feature: "Coin Economy & Free Quota"
   - `/starburst/*` (6 个端点) → 候选 Feature: "StarBurst Content Feed"

2. **按第三方 provider 提议 feature** — 每个重要 provider 通常对应一个 AI 能力 feature
   - 如 Volcano Engine CV → "AI Image Generation"

3. **标注迁移关注点** — 扫描结果里对迁移难度高的接口打标签，供 spec 生成时重点描述：
   - SSE / WebSocket 接口（HarmonyOS 支持有限）
   - 自定义签名认证（AWS-style / XXTEA / HMAC，需要移植签名算法）
   - Multipart 上传
   - 异步任务模式（submit → poll → result）
   - 跨 Service 重复的端点（同一路径多处定义）

4. **输出到 `api-inventory.md` 的专用章节** "Feature 候选建议"，并在 `coverage` 字段下填 `feature_candidates` 数组。**完整 markdown 模板 + JSON schema 示例 + 输出措辞约定**见 [references/templates/feature-candidates-section.md](references/templates/feature-candidates-section.md)。

**重要**：分支 C 的输出目标是**喂给 a2h-spec**，不是终版交付。措辞上要说清楚"这是候选，spec 作者可以采纳/调整/重划"，不要写得像定论。

## 输出文件

| 文件 | 路径 | 用途 |
|------|------|------|
| raw_apis.json | spec/baseline/api-inventory/raw_apis.json | 脚本扫描的原始数据（中间产物，供重跑验证） |
| api-inventory.json | spec/baseline/api-inventory/api-inventory.json | 结构化数据，供其他 skill 消费 |
| api-inventory.md | spec/baseline/api-inventory/api-inventory.md | 人类可读文档；分层时为**总览索引** |
| common.md | spec/baseline/api-inventory/common.md | 分层时产出 —— 公共约定（信封/签名/公参/共享响应体/状态码） |
| apis/&lt;模块&gt;.md | spec/baseline/api-inventory/apis/ | 分层时产出 —— 每个 service/模块的详细 API 文档 |
| data-chains/chain-auth.md | spec/baseline/api-inventory/data-chains/chain-auth.md | Phase 2.8 产出 —— auth 数据链路契约（auth_model 的 SOP 形态投影 + 非 API 层 owner 交叉核） |

> `common.md` + `apis/` 仅在「分层」形态下产出（判定见 §3.2）；小项目只产 `api-inventory.md` 单文件。`api-inventory.json` 始终是机器可读唯一事实源，下游 skill 只读它。`data-chains/chain-auth.md` 是 auth_model 的人类可读 SOP 投影，单一源仍是 api-inventory.json。

## API contract 中的角色

`api-inventory.json` 的每个 endpoint 是一份三段式 API contract（`static` / `runtime` / `reconciled`）。本 skill 是 **`static` 段的唯一生产者**：

- `platform: android` → 产 **Android static**
- `platform: harmony` → 产 **HMOS static**
- `runtime`（抓包实测）与 `reconciled`（static↔runtime DIFF）始终由 `arkts-network-troubleshoot` 写，本 skill 一律留 `null`。

由此 contract 不绑定迁移场景：

- **迁移项目**：Android static（`platform:android`）+ Android runtime → 验证后的 Android 契约，驱动 HMOS 实现。
- **鸿蒙增量开发**：HMOS static（`platform:harmony`）+ HMOS runtime（抓 HMOS 真包）→ 一份**单平台 contract**，即纯鸿蒙项目的「静态 + 运行时实测」API 报告。

三段字段定义与所有权见 [references/output_schema.md](references/output_schema.md)。

## 与 a2h-spec 的集成契约

本 skill 是 a2h-spec 初始迁移流程 **Phase B 的 B-API 并行轨**。a2h-spec 在 Phase B 开始时（Step B0）派后台子 agent 调用本 skill，与 UI 清单生成（B-UI 轨）并行；Step B-join 收口后，产出供 Phase C 消费。**a2h-spec 永远以 `platform: android` 调用本 skill** —— 迁移流程的 spec 阶段只编目 Android 侧；多模式 skill 在某阶段只用一种模式是正常用法。

被 a2h-spec Phase B 并行轨调用时，本 skill 必须遵守以下契约：

1. **分支固定**：此时 `feature-index.md` 与 `features/F*.md` 均未生成 → Phase 4 必走**分支 C（输入源模式）**，产出 `coverage._mode == "candidate"` 与 `coverage.feature_candidates[]`。
2. **输出路径固定**：`spec/baseline/api-inventory/`（`raw_apis.json` + `api-inventory.json` + `api-inventory.md`；分层形态下还有 `common.md` + `apis/*.md`）。
3. **返回 summary（v1.3 扩为 7 字段；+ Phase 2.8 加 1）**：子 agent 结束时返回 `services 数 / endpoints 数 / feature_candidates 数 / coverage._mode + hmos_hint_section_present (boolean) + uncertainties_open_count (number) + auth_model_present (boolean) + chain_auth_red_count (number)`，供 a2h-spec Step B-join 判定 `api_inventory_status`、是否已落 HarmonyOS 等价物提示段，以及向下游 a2h-plan grill #2 C17 通报待收口的不确定项规模（含 `chain-auth` 冒泡的 RED）。
4. **降级不阻塞**：离线项目 / React Native·Flutter 壳 → 按既有降级逻辑产说明文档，summary 显式标 `degraded`；a2h-spec 据此把 `api_inventory_status` 置 `degraded`，Phase C 回退自扫，**不阻塞** Gate B / Phase C。
5. **hmos_references_file 透传**：a2h-spec Step B0 派发子 agent 时，prompt 包含 `hmos_references_file: $HMOS_REFS_FILE`（来自 Step 3.0c 产出，未提供时为 null 或空）。**Phase 2.5a 框架映射无条件执行**（platform: android 即跑，不依赖该参数）；收到非空且文件存在时**追加 2.5b 三方等价物预标注**，为空或文件不存在则只跳过 2.5b。Phase 2.5 的产物仅追加段到 `api-inventory.md`，不影响 `coverage._mode` 与 `feature_candidates` 的产出形态。
6. **backend_facts_file 透传（v1.3）**：prompt 包含 `backend_facts_file: $BACKEND_FACTS_FILE`（来自 Step 3.0c2 后端契约预知收集，未提供时为 null）。非空且文件存在时 Phase 3.1b 用它对 `uncertainties[]` **预销账**；为空则所有不确定项以 `open` 状态交给 a2h-plan grill #2 C17。Phase 2.75 auth_model / data_flows **不依赖该参数**，无条件执行。

Phase C 对本 skill 产物的消费点：

| a2h-spec 步骤 | 消费 api-inventory 的内容 |
|--------------|--------------------------|
| Step C1 源码分析 | 网络层直接读 `services` / `third_party_apis` / `base_urls`，取代自行 Grep |
| Step C2 功能拆分 | `coverage.feature_candidates` 作为功能划分的第三输入源（与 UI 侧、源码侧互补） |
| Step C3 feature-base | 网络层章节由 `base_urls` + `auth_type/auth_detail` + endpoints 全集生成 |
| Step C4 feature spec | 每个 F00x 的「## API 接口」段从对应候选的端点选取 |
| Step C4-pre 复杂度判定 | 端点含自定义签名 / SSE / WebSocket / 三方 SDK 或 `migration_concerns` 非空 → 判 `complex` |

> 手动单独调用本 skill（非 pipeline 并行轨）时，分支由上文 Phase 4 决策表按 spec 实际状态决定，不受本契约约束。

## 项目适配性说明

本 skill 对不同项目的适配能力：

| 项目类型 | 适配度 | 备注 |
|---------|--------|------|
| Retrofit + 多模块 + Interceptor 签名 | ✅ 完美 | 如 AIImage / AIPPT |
| Retrofit + 单模块 | ✅ 良好 | Phase 2 按包名划分模块 |
| 裸 OkHttp + 部分 Retrofit | ⚠️ 需 Phase 1b | 如 Feeder |
| SDK 黑盒主导 | ⚠️ 需手动识别 SDK 暴露的接口 | 如 Twire 的 twitch4j |
| 离线 / 无网络层 | ✅ 简化输出 | 如 Auxio / Calendar，文档直接说明 |
| React Native / Flutter 壳 | ❌ 不适用 | 如 Joplin，Kotlin 层扫不到业务接口 |

模型在 Phase 2 判断出项目类型后，应主动调整 Phase 3 的文档组织方式，不要生硬套用 Retrofit 项目的模板。

## 参考文件

- `scripts/extract_android_apis.py` — Phase 1 Android scanner（Retrofit Kotlin+Java / @Url / @Headers / Interceptor / body 组装点 / gradle 注入 / 调用点回溯）
- `scripts/extract_arkts_apis.py` — Phase 1 HarmonyOS scanner（@kit.NetworkKit / ApiService URL 常量 / HttpInterceptor / ArkTS Bean）
- `references/output_schema.md` — 输出文件的字段定义和推荐结构（含 v1.3 changelog + 三段式 contract schema + auth_model / data_flows / uncertainties 顶层段）— Phase 2.75 / Phase 3 前**必读**
- `references/phase1b-grep-strategies.md` — Phase 1b 补扫的完整 grep 关键字表（裸 OkHttp / Ktor / WS / SSE / GraphQL / gRPC / SDK）+ 极端情况降级（RN/Flutter 壳、离线项目）
- `references/framework-kit-mapping.md` — Phase 2.5a 框架 API→Kit 静态映射表（harmony-docs 核验，网络/序列化/加密/存储/设备标识；零运行时依赖）— platform: android 必读
- `references/templates/hmos-hint-section.md` — Phase 2.5 HarmonyOS 等价物提示段的 markdown 模板（已命中 / 未命中 / 参考未触及 三子段）
- `references/templates/feature-candidates-section.md` — Phase 4 分支 C 的 Feature 候选 markdown + JSON schema 模板
- `references/example-layered/` — 分层产出骨架示例（v1.2 schema，Retrofit + 多模块场景，含 mismatch 演示）— 需要产出样例参照时读
- `references/templates/chain-contract-template.md` — Phase 2.8 数据链路契约模板（通用骨架 + auth 首个 profile + 实例填写区）— 生成 `data-chains/chain-<name>.md` 时**必读**

## 注意事项

- Retrofit 注解中 `@POST(PayUrl.productList)` 这种常量引用，脚本会自动在 endpoint 的 `resolved_path` 字段回填实际路径
- 同一第三方域名可能对应多个 Action/endpoint（如火山引擎的 Action 参数化 URL），Phase 2 需要识别并正确归组
- SSE 接口在迁移到 HarmonyOS 时需要特殊处理（HarmonyOS 的 @ohos.net.http 对 SSE 支持有限），在文档里明确标注协议类型
- 多模块项目中可能存在相同接口在不同模块中的重复定义（如 `/push/getuiCid` 在 AppApiService 和 PushApiService 里都有），需要去重或说明
- 对于 AWS-style 签名的第三方 API（如火山引擎 CV），在 auth_detail 里写明具体算法（HMAC-SHA256）和必需 Header，迁移时这是难点
- `platform: harmony` 时：HMOS 网络调用是命令式（`http.createHttp().request(...)`），endpoint 靠「`ApiService` 里的 URL 常量 + 调用点」拼；ArkTS class 字段名默认即 JSON key（无 `@SerializedName`），scanner 抽响应结构按此处理 —— 若工程有 unwrap 镜像层，那是运行期行为、归 `arkts-network-troubleshoot` Phase 4，不在本 skill 编目范围
