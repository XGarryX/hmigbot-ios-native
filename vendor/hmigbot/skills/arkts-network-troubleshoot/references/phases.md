# Phase 0-6 排查流程

> 正向预防：按 Phase 0 → 6 顺序推进。每个 Phase 是闭环（检查项 + 工具命令 + 失败对策 + 通过标准），**前一 Phase 不通不要跳下一 Phase**。
> 反向救火：先查 [error-lookup.md](error-lookup.md) 定位 Phase，跳到对应章节排查，修复后回 Phase 6 重测。
> **设备依赖**：Phase 0.2 / 1 / 2 / 4 / 5 是纯静态分析 + 编码，无设备可全程跑完；**Phase 0.3 真机抓包、Phase 3 签名 200 实测、Phase 6 联调**需设备 —— 被流水线（Base-3）无设备调用时，这三步延后到 a2h-verify，不阻塞静态产出。

## 目录

- [Phase 0: 抓证据](#phase-0-抓证据)
- [Phase 1: Spec 对账（6 张表 + 1.8 鉴权链路）](#phase-1-spec-对账6-张表--18-鉴权链路)
- [Phase 2: 启动期初始化对账](#phase-2-启动期初始化对账)
- [Phase 3: 字节级验证（加密 / 编码）](#phase-3-字节级验证加密--编码)
- [Phase 4: 响应链路验证](#phase-4-响应链路验证)
- [Phase 5: UI 响应式订阅](#phase-5-ui-响应式订阅)
- [Phase 6: 联调实测](#phase-6-联调实测)

---

# Phase 0: 抓证据

## 目标

不写一行代码，先把"Android 端事实 + 服务端契约 + HMOS 当前状态"摆齐。后续所有 Phase 都依赖这一步产出物。跳过 Phase 0 直接进编码，联调阶段几乎一定会回头补做。

## 检查项

| # | 检查项 | 工具 / 命令 | 产出位置 |
|---|--------|------------|---------|
| 0.1 | Android 源码本地可访问 | 文件系统检查 | `spec/android_source_anchors.md` |
| 0.2 | Android 网络层关键文件清单 | `grep -rn 'object\s\+\w*Url\b' android_src --include='*.kt'` | `spec/baseline/android-network-files.md` |
| 0.3 | Android 真实运行抓包样本（≥5 条核心接口） | 见 [capture-android-traffic.md](capture-android-traffic.md)（3 方法 + 前置闸门） | `spec/baseline/sample-requests.md` + 回填 `api-inventory.json` 的 `runtime` 段 |
| 0.4 | HMOS 当前 service 文件清单 | `find <hmos>/src/main/ets/network -name '*.ets'` | `spec/baseline/hmos-network-files.md` |
| 0.5 | HMOS hilog 输出域 ID | grep `const DOMAIN = 0xXXXX` | 联调时实时取 |
| 0.6 | 服务端 enum / DB schema | 找后端要 / 查后端代码仓 | `spec/baseline/backend-contracts.md` |

## 0.2 Android 源码清单

把 Android 工程内所有定义 URL / body / 签名 / 公参的文件都列出来：

```bash
grep -rn 'object\s\+\w*Url\b' android_src --include='*.kt' | grep -v '/build/'
grep -rln '@POST\|@GET' android_src --include='*.kt' | grep -v '/build/'
grep -rn 'mutableMapOf.*toRequestBody' android_src --include='*.kt' | grep -v '/build/'
grep -rln 'HmacSHA1\|MessageDigest\|MD5_TABLE\|b2hStr' android_src --include='*.java' --include='*.kt' | grep -v '/build/'
grep -rln 'Interceptor\|chain\.proceed' android_src --include='*.kt' | grep -v '/build/'
grep -rln 'AppFormInfo\|PlatformInfo\|CommonParams' android_src --include='*.kt' --include='*.java' | grep -v '/build/'
grep -rn '@SerializedName(' android_src --include='*.kt' --include='*.java' | grep -v '/build/'
```

## 0.3 Android 真实抓包（最重要）

光看代码不够。要抓到 Android 端真实运行的请求 + 响应原文，至少 5 条核心接口（启动 / 登录 / 业务 / 上传 / 支付各 1-2 条）。

**为什么必须抓真包**——以下这些光看代码都猜不准：

- 字段类型：JSON 里 `userId` 是 int 还是 long string？默认值 `-1` 还是 `0`？
- 响应包装：`{code, msg, data}` 还是 `{status, toastMsg, data}` 还是 `{data: {status, ...}}`
- header 拼写：`token` vs `Token` 大小写
- 业务码语义：`status: 0` 成功 vs `code: 0` 成功

**抓之前先过 3 道前置闸门**（任一不过先解决再抓，否则白忙）：

1. **设备 / 模拟器在线** —— `adb devices` 看到 `<serial> device`（非 unauthorized / offline / 空）
2. **目标 App 已安装 + debug 构建 + 能跑业务** —— `adb shell pidof <applicationId>` 有 PID
3. **抓取通道就绪** —— 按下表三选一

**3 种抓取方法**（详细步骤 + 闸门细则 + 选择决策见 [capture-android-traffic.md](capture-android-traffic.md)）：

| 方法 | 适用 | 前置依赖 |
|---|---|---|
| A. App 自带日志拦截器 → `adb logcat` | 零配置首选，看响应结构 / 字段类型 | 闸门 1+2，App 是 debug 包 |
| B. Android Studio Network Inspector | 要完整 headers + 大 body + 导出 HAR | 闸门 1+2+3，App debuggable |
| C. 抓包代理 Charles / mitmproxy | 要真实字节做 Phase 3 签名对账 | 设备配代理 + 信任 CA + 无 pinning |

URL / body 字段结构这类静态信息不必抓包，读源码或 `spec/baseline/api-inventory/api-inventory.json` 即可。

### 抓包前先看定向清单（v1.3）

若 `api-inventory.json` 含 `uncertainties[]`（v1.3 schema），其中 `status: needs_capture` 的条目就是**定向抓包清单**——grill #2 已确认这些问题只有真包能回答（响应壳形状 / 字段真实类型 / 业务码语义 / header 大小写）。抓包目标端点优先覆盖这些条目涉及的 endpoint（`chain: auth` 的最优先），而不是漫抓 5 条了事。

**open 项分流（与 checklist 第 0 步第 2 点一致，勿一刀切排除）**：`needs_capture` 是本清单**本体**；`tag=②需真包` 且 `status` 仍 `open` 的条目（未走 grill 的手动项目）按 ② 原纪律**同样是抓包候选** —— 设备 / 通道就绪时列入本清单（可标次级 / 待升格 `needs_capture`），**别与 ③ 策略类 `open` 并列排除**。`③策略待确认` 的 `open` 项走 grill / 照搬兜底 + 留标记、**不入本抓包清单**（抓包答不了它）。

### 抓包结果回填 contract `runtime` 段 + 销账 uncertainties

若工程内有 `spec/baseline/api-inventory/api-inventory.json`，抓到的真包不要只堆进 `sample-requests.md` —— 还要**按 endpoint key 回填**每个 endpoint 的 `runtime` 段（key = `"<HTTP方法> <path>"`，如 `"POST /user/initUser"`）。`runtime` 段记录抓包才能确定、源码推不准的运行期事实：

- `response_wrapper`：响应真实包装层级（`{code,msg,data}` / `{status,toastMsg,data}` / 扁平）
- `business_code`：真实业务码字段名 + 成功取值（`status==0` / `code==0`）
- `field_types`：响应字段真实类型 / 默认值（`userId` 是 int 还是 string、默认 `-1` 还是 `0`）
- `headers`：请求头真实拼写大小写、签名头字节（方法 C 抓到才有）
- `source` / `captured_at`：抓取方法与时间

`runtime` 段 schema 见 [android-api-inventory output_schema](../../android-api-inventory/references/output_schema.md)。抓不到的 endpoint（需人工触发 / 设备未就绪）其 `runtime` 留 `null` —— 这是允许的部分闭合，不是缺陷。`sample-requests.md` 仍照常产出，作为人类可读的抓包原文留存，与 contract 互为印证。

**销账（v1.3）**：抓到的证据能回答某条 `uncertainties[]` 时，就地更新该条：`status → resolved`、`resolution` 填实测值、`resolved_by` 填 `runtime <endpoint> @<日期>`；工程有 `spec/decision-ledger.md` 时同步把 ledger 对应条目（grill #2 C17 标 `needs_capture` 的 D/事实条目）标注已实证。抓不到的保持 `needs_capture` —— 与 `static-only` 一样是允许的部分闭合。

## 0.6 服务端契约

强烈推荐找后端要 3 份信息：(1) 接口必填字段清单 (2) DB 表 NOT NULL 字段 (3) 服务端枚举值（后端常根据公参某字段反查 enum，如渠道来源 / 媒体号 / 支付渠道等 enum 的允许取值）。否则盲调成本很高。

## Phase 0 通过标准

- ✅ Android 网络层文件清单已落 `spec/baseline/android-network-files.md`
- ✅ ≥5 条 Android 真实请求/响应原文已落 `sample-requests.md`
- ✅ 有 `api-inventory.json` 时：已抓 endpoint 的 `runtime` 段已按 endpoint key 回填（未抓到的留 `null`，允许部分闭合）
- ✅ HMOS hilog 域 ID 已知
- ✅ （强烈推荐）后端契约文档已拿到

---

# Phase 1: Spec 对账（6 张表 + 1.8 鉴权链路）

## 目标

把 Android 网络层的字面值事实逐项抽到 `spec/baseline/`，HMOS 实现严格 1:1 对齐。本 Phase 完成后，Phase 2-5 编码几乎不用脑补，照表抄即可。

6 张表的 markdown 模板见 [templates/spec-baseline.md](templates/spec-baseline.md)。

> **6 表与 API contract 的关系**：当工程内有 `spec/baseline/api-inventory/api-inventory.json` 时，它是 endpoint-keyed 的 contract 主存储（每个 endpoint 三段式 `static` / `runtime` / `reconciled`）；6 张对账表是同一份 contract 的「按维度投影」——`url-mapping` 投 URL 维、`sign-algorithms` 投签名维…依此类推。此时以 contract 为准填写（`static` 来自 api-inventory、`runtime` 由 Phase 0.3 回填），6 表从 contract 派生即可，不要两边各填一遍导致不一致。工程内无 `api-inventory.json` 时，6 表即对账主产物，照常 grep 自抽。
>
> **ledger 预填（v1.3，填表前先做）**：工程内有 `spec/decision-ledger.md` 时，先读其 D 编号决策与「事实」段 + `api-inventory.json` 的 `uncertainties[]`——grill #2 C17 已收口的项（`answered`）直接采用 `resolution` 填表（来源标 D 编号 / uncertainty id），**不重复推断**；`needs_capture` 项在表中标 🟡 待抓包（Phase 0.3 销账后回填）。这是上游 grill 前置问询的下游承接点：用户已经答过的问题，不要在这里再猜一遍。

## 1.0 重建既有实现前：先锁消费方接口面

迁移工程常已产出一版**能编译但脑补**的网络层（URL 全错 / 无签名 / 无公参）。推倒重建前，
**先 grep 全部调用点**，锁定要保持稳定的方法签名集，避免改完接口层引发级联编译爆炸：

```bash
grep -rn 'PlatformService\.\|XxxService\.' hmos_src --include='*.ets'
```

产出一张「方法 × 调用方 × 现签名 × 返回类型」清单。重建时**保持方法名与返回类型不变**、
只改内部 URL/body/解包 —— 则消费方（Repository / ViewModel）零改动或仅个别适配，改一处不炸一片。

## 1.1 URL 全表对账

```bash
grep -rn 'const val\s\+\w\+\s*=\s*"/' android_src --include='*.kt' | grep -v '/build/'
grep -rn '@POST("/\|@GET("/' android_src --include='*.kt' | grep -v '/build/'
```

每个 Service 一张表：HMOS Service.method × Android URL 来源 × Android URL 字面值 × HMOS URL 常量 × 对账状态。

**典型陷阱（90% 项目必撞）**：

- ❌ HMOS URL 省略 `/user/` `/system/` `/app/` `/anti/` `/push/` 等命名空间前缀
- ❌ HMOS URL 方法名与 Android 不一致（Android 接口方法名常与服务端实际 path 不同 —— 例如方法名简写为 `bindMobile`，服务端实际 path 却是 `/user/bindMobileBySmsCode`。必须填服务端实际 path）
- ❌ HMOS URL 用客户端方法名而非服务端实际路径

## 1.2 Request body 字段对账

```bash
grep -rn 'mutableMapOf("' android_src --include='*.kt' -A 5 | grep -v '/build/'
```

**典型陷阱**：漏看似无意义的常量字段（如 `source: 1` / `type: 0`）；字段类型错（Android `Int` vs HMOS `string`）；字段名拼写错；嵌套对象漏抽。

## 1.3 JSON 字段映射（@SerializedName）

```bash
grep -rn '@SerializedName(' android_src --include='*.java' --include='*.kt' | grep -v '/build/'
```

每条 `@SerializedName("json") javaField` 记录到对账表。HMOS 端集中在 HttpClient.unwrapAndMirror 配置表展开（见 Phase 4）。

## 1.4 签名算法对账

```bash
grep -rln 'MD5_TABLE\|b2hStr\|byteToHex\|toHex' android_src --include='*.java' --include='*.kt'
grep -A 3 -B 1 "'[a-fA-F]'" $(grep -rln 'MD5_TABLE\|toHex' android_src --include='*.kt' --include='*.java')
```

| 签名链路 | 算法步骤（示例） | hex 大小写（示例） | 最终编码 | HMOS 入口 |
|---|---|---|---|---|
| 自有业务签名 | `SHA1(body+ts+token+MD5(minute+token)+key)` | MD5/SHA1 **大写** | hex | `SignUtil.md5()` / `sha1()` |
| 三方厂商签名 | `base64(HmacSHA1(MD5(appId+ts), secret))` | MD5 **小写** | base64 | `SignUtil.md5Lower()` / `computeVendorSignature()` |

**关键经验**：同一项目内可能同时有 ≥2 套签名链路，hex 大小写不同。HMOS SignUtil 必须暴露大小写两个入口（`md5` / `md5Lower`），不要试图统一。

## 1.5 公参（platformInfo）字段对账

| 字段类别 | Android API | HMOS 等价 | fallback |
|---------|------------|----------|----------|
| 应用 ID | `context.packageName` | `bundleInfo.name` / 硬覆盖 Android applicationId | — |
| 应用版本 | `PackageManager.getPackageInfo().version*` | `bundleManager.getBundleInfoForSelfSync().version*` | — |
| 应用名 | `applicationInfo.loadLabel(pm)` | `ctx.resourceManager.getStringSync(labelId)` | 硬编码常量 |
| 屏幕 | `DisplayMetrics` | `display.getDefaultDisplaySync()` | — |
| 系统版本 | `Build.VERSION.RELEASE` | `deviceInfo.osFullName` | — |
| 品牌/型号 | `Build.BRAND / Build.MODEL` | `deviceInfo.brand / .productModel` | — |
| 运营商 | `TelephonyManager.networkOperatorName` | `sim.getSimOperatorNumericSync(0)` | `'un_know'` |
| IMEI | `DeviceIdentifier.getIMEI()` | （无 API） | 空串 |
| Android ID | `Settings.Secure.ANDROID_ID` | （无 API） | 首启 `util.generateRandomUUID()` 持久化 |
| OAID | `DeviceIdentifier.getOAID()` | `@kit.AdsKit.identifier.getOAID()` + APP_TRACKING_CONSENT | 占位 `0...0` |
| 安装来源 | `getInstallerPackageName()` | （无 API） | 空串 |
| 渠道 | Walle / manifest meta-data | （无 API） | 硬编码 defaultChannel |
| 构建类型 | manifest meta-data | （无 API） | 硬编码常量 |

完整 PlatformInfo 模板见 [templates/code/platform-info.ets](templates/code/platform-info.ets)。

## 1.6 构建期注入字段

```bash
grep -n 'productFlavors\|manifestPlaceholders\|buildConfigField' android_src/app/build.gradle*
cat android_src/channel/product.xml
grep -A 1 '<meta-data' android_src/app/src/main/AndroidManifest.xml
```

多 product 应对：单 product → 全硬编码；2-3 product → build-profile.json5 buildProfileFields；多 brand → 独立 HSP 模块（详见 pitfalls.md F1）。

## 1.7 API Contract DIFF（static ↔ runtime）

> 仅当工程内有 `spec/baseline/api-inventory/api-inventory.json` 时执行；无则跳过（6 表即对账终点）。

把 contract 的 `static` 段（源码静态推断）与 `runtime` 段（Phase 0.3 抓包实测）逐 endpoint 比对，结果写入该 endpoint 的 `reconciled` 段，并汇总产出 `spec/baseline/api-contract-diff.md`。这是 §7 闭环的 **DIFF#1**（DIFF#2 是 a2h-verify Phase 6 联调实测）。

**比对维度**（static 给「契约的形状」，runtime 给「契约的实况」）：

| 维度 | static 来源 | runtime 来源 | 典型 mismatch |
|---|---|---|---|
| 响应包装层级 | 源码推不准 | 抓包确认 | 源码按扁平 Bean 写，实际是 `{code,msg,data}` |
| 字段名 | Bean 字段名 / `@SerializedName` | 真实 JSON key | 源码 Bean 写 `errorCode`，真实 JSON 是 `status` |
| 字段类型 / 默认值 | 声明类型 | 抓包实测 | 声明 `int`，实际是 long string |
| 业务码语义 | 推不出 | 抓包确认 | `status:0` 成功 vs `code:0` 成功 |
| 请求头 / 签名字节 | 读 Interceptor | 真实 header 字节、hex 大小写 | 源码看不出 hex 大小写 |

**`reconciled.status` 三态**：

- `verified` —— `runtime` 已抓且与 `static` 一致
- `mismatch` —— `runtime` 已抓且与 `static` 有差异（差异逐条记入 `reconciled.discrepancies`）
- `static-only` —— 该 endpoint `runtime` 仍为 `null`（未抓 / 设备未就绪），无法验证

**`api-contract-diff.md` 结构**：① 汇总计数（verified / mismatch / static-only 各几个）；② mismatch 清单（每条：endpoint、维度、static 值、runtime 值、对 HMOS 实现的影响）；③ static-only 清单（待补抓的 endpoint）。

mismatch 项在 Phase 2-5 实现 HMOS 网络层时**按 `runtime` 实况为准**（而非 `static`）。`reconciled` 段 schema 见 [android-api-inventory output_schema](../../android-api-inventory/references/output_schema.md)。

**DIFF 后销账（v1.3）**：`reconciled` 判定给出的实证同样用于 `uncertainties[]` 销账（`needs_capture` → `resolved`），规则同 Phase 0.3。

## 1.8 鉴权/登录链路对账（v1.3 · auth-chain.md）

> **为什么单列一张表**：login.md 复盘证明登录打不通的缺口在机制层，不在接口清单——6 张通用表按"维度"切（URL / body / 签名…），登录问题恰恰跨所有维度、沿"链路"发生。本表按 token 生命周期六要素纵向对账，是 Phase 6.2 登录链路联调的静态前置。

**事实源**：工程有 `api-inventory.json` 时直接投影其 `auth_model` 段（v1.3，android-api-inventory Phase 2.75 产出）+ `data_flows[chain=auth]`；无则按下列 grep 自抽：

```bash
grep -rn 'initUser\|login\|oauth\|token' android_src --include='*Service*.kt' --include='*Api*.kt' | grep -v '/build/'
grep -rn 'MMKV\|SharedPreferences\|putString.*token\|encode.*token' android_src --include='*.kt' | grep -v '/build/'
grep -rn 'addHeader\|-100[0-9]\|tokenExpired\|forceLogout\|kick' android_src --include='*Interceptor*.kt' | grep -v '/build/'
```

**自抽项分级边界**（走上面 grep 自抽、无 `uncertainties[]` 可查时按此填 —— 有 `api-inventory.json` 走投影路径的用下方「填表纪律」）：自抽的六要素**多数**能从源码字面证明 → 按 `①源码可定` 直接填 + 附「文件:行号」证据；但两类事实**源码字面 ≠ 线上真值**，即便常量可见也只是 ① 候选、线上真值属 ②，须显式标记、不得当 ① 填死：

- **注入头名的线上大小写拼写**：源码常量（如 `Constant.TOKEN="token"`）只给候选字面，真实请求头拼写（`token` / `Token`）须真包才能定 → 标 🟡 待抓包（②需真包，同下表 #3 典型坑），别拿常量小写当「①源码可定」填死。
- **身份模型 device-bound vs account-only**：裁剪/单文件片段判不出（有 per-user 动态域名 / device 维度头 / ICS 设备端点迹象时尤甚）→ 显式标 unknown/待确认（同下表 #6 典型坑），别按直觉断言 account-only（或 device-bound）。
- **负向守卫**：其余源码字面能证的项（存储层 / 失效码值集 / 端点集 / 清除动作 / body 常量字段）仍按 ① 从源码读出照填，**别误标 🟡** —— ② 边界只落在上述「源码字面≠线上事实」两项，不要泛化到整表。
- **作用域**：本「分级边界」只约束 §1.8 fallback（无 `uncertainties[]` 可查）自抽填表时的 ①/② 判定与标注；**Phase 0.3 抓包清单的候选取舍另走 §0.3「抓包前先看定向清单」/ checklist 第 0 步**，别把本块「② 标 🟡 待抓包 / 标 unknown 待确认」话头当 Phase 0.3 的抓包排除依据。

**对账表**（模板见 [templates/spec-baseline.md §7](templates/spec-baseline.md)）——六要素逐行，Android 事实 × HMOS 实现 × 状态：

| # | 要素 | Android 事实（auth_model 字段） | HMOS 实现落点 | 典型坑 |
|---|------|------------------------------|--------------|--------|
| 1 | token 获取 | `token_acquisition`（哪些端点发 token、guest/bound 语义差异） | SplashService.initUser / LoginService | 端点业务语义搞错（游客登录 ≠ 新建游客） |
| 2 | token 存储 | `token_storage`（key + 存储层） | PreferencesUtil + AppStorage（V2 单一源，pitfalls B7） | 存储 key 拼写 / 层级不一致 |
| 3 | token 注入 | `token_injection`（拦截器 + header/body + 名字） | HttpInterceptor.addHeader | header 名大小写（②需真包） |
| 4 | token 失效 | `token_expiry`（码 + 适用范围 + 动作） | ResponseInterceptor 失效判定 | guest -1001 误清 token（pitfalls D4c）|
| 5 | token 清除 | `token_clearing`（触发 × 清什么 × **留什么**） | UserRepository.logout | 把设备级字段（deviceNo）一起清掉 |
| 6 | 身份模型 | `identity_model` + `irreversibles` | 登录页 / 「我的」Tab 状态机 | 把 device-bound 当纯账号态实现 |

**填表纪律**：`auth_model` 里标 `unknown` 的字段 → 查 `uncertainties[]` 对应条目状态：`answered` 用 `resolution`；`needs_capture` 表中标 🟡 待 Phase 0.3 抓包；`open`（未走 grill 的手动项目）按 ②③ 铁律处理，不猜。

## Phase 1 通过标准

- ✅ 6 张对账表全部填齐（URL / body / JSON 字段 / 签名 / 公参 / 构建期注入）
- ✅ 每张表 HMOS 列 100% 与 Android 列对齐（或显式标注差异 + fallback）
- ✅ 有 `api-inventory.json` 时：每个 endpoint 的 `reconciled.status` 已判定，`mismatch` 项已逐条记入 `api-contract-diff.md`（允许 `static-only` 行存在，不要求 100% verified）
- ✅ **auth-chain.md 六要素全部有归属**（事实 / 待抓包 🟡 / 显式 unknown+uncertainty，不允许整行空白）—— 工程有登录/用户体系时必做，纯离线项目可标 N/A
- ✅ `uncertainties[]` 无 `open` 遗留（走过 grill 的项目；`needs_capture` 允许存在）
- ✅ "硬覆盖" / "硬编码" 临时方案都已在 `spec/baseline/decisions.md` 登记成本与回滚路径

---

# Phase 2: 启动期初始化对账

## 目标

让 EntryAbility / Splash / Service 启动期的"同步 init + 异步 await + AppStorage 注入"全部就位。90% 的"协议每次冷启都弹"/"download 报 No UIAbilityContext"/"拦截器读全空"问题根因都在本 Phase。

关键事实：`UIAbility.onCreate(want, launchParam): void` 签名**不允许 async**，但 PreferencesUtil / SDK init 都是 Promise。fire-and-forget 后立即 loadContent，SplashPage 起来时这些工作还没就绪。

## 检查项

| # | 检查项 | 失败征兆 |
|---|--------|---------|
| 2.1 | EntryAbility.onCreate 同步注入 AppStorage 必备 key | `download failed: No UIAbilityContext` / HttpLog 静默 |
| 2.2 | PreferencesUtil.init Promise 保留 + onWindowStageCreate await | 协议每次冷启都弹 / 拦截器公参全空 |
| 2.3 | EventBus.init(context) 同步完成 | `EventBus.post called before init` |
| 2.4 | SDK want 分发（OAuth SDK）冷+热启动都调 | 微信 / 支付宝回调 onResp 永不触发 |
| 2.5 | module.json5 配 querySchemes + skill | `canOpenLink('weixin://')` 永远 false |
| 2.6 | SplashService 异步链路顺序合理 | OAID/androidId 没就位 initUser 提前跑 |

## 2.1 AppStorage 必备 key 全清单

`EntryAbility.onCreate` 内**同步**注入：

| key | 类型 | 用途 |
|---|---|---|
| `'context'` | UIAbilityContext | HttpClient.download / 资源 / ctx 依赖 |
| `'isDebug'` | boolean | HttpLogInterceptor 守卫 |
| `'mHttpUrl'` | string | 自有业务域，拦截器 isOwnBusinessRequest 判定 |
| `'chanelId'` | string | 渠道号 |
| `'userData'` | UserData | 登录态全局响应式（SplashService.initUser 后写）|
| `'appConfig'` `'userConfig'` | Bean | 远程配置 |
| `'oaid'` `'androidId'` | string | 启动期聚合后写 |

## 2.2-2.3 EntryAbility 启动模板

完整模板见 [templates/code/entry-ability.ets](templates/code/entry-ability.ets)。核心套路：**sync onCreate + async onWindowStageCreate + Promise 保留 + await 后再 loadContent**。

## 2.6 SplashService 启动链路顺序

```
ensurePrivacyAgreed → uploadFirstStart → initThirdPartySdks
  ↓
并发：
  ├─ runOaidAndInitUser:  ensureAndroidId() → aggregateOaid() → initUser()  （三步串行）
  ├─ fetchInitialConfig
  └─ progressLoad
  ↓
enterApp
```

**为什么 ensureAndroidId 要先于 initUser**：initUser body 带 `platformInfo.androidId`，后端 USER_INFO 表 ANDROID_ID 列可能 NOT NULL，必须 initUser 调用前 AppStorage('androidId') 已写。

**⚠ 启动期请求时序必须对齐 Android 实测**：上图「并发」是默认编排，但 `initUser` 等建号/鉴权接口可能依赖 `fetchInitialConfig`（如后端在 `/app/config` 时为设备建立会话/媒体上下文）。Phase 6 联调时务必用抓包对比 Android 实测时序 —— 若 Android 是 `config → 等响应 → initUser` 串行，HMOS 也必须串行（`await fetchInitialConfig()` 后再 initUser），不能并发抢跑。判断方法：对比两端请求发出顺序 / `tt` 时间戳间隔（并发 ≈ 几 ms，串行 ≈ 一个 round-trip）。

## 2.5 module.json5 必备配置

```json5
{
  "module": {
    "querySchemes": ["weixin", "wxopensdk", "alipay", "alipays"],
    "abilities": [{
      "skills": [
        { "entities": ["entity.system.home"], "actions": ["ohos.want.action.home"] },
        { "actions": ["wxentity.action.open"] }
      ]
    }],
    "requestPermissions": [
      { "name": "ohos.permission.APP_TRACKING_CONSENT", "reason": "...", "usedScene": {...} }
    ]
  }
}
```

漏配 querySchemes → `bundleManager.canOpenLink('weixin://')` 永远 false → 微信登录按钮自动隐藏 / 微信支付走不出去。

## Phase 2 通过标准

- ✅ 冷启动 → SplashPage → HomePage 全程无 hilog warn（重点 `prefs not init` / `context is undefined`）
- ✅ 第二次冷启动协议弹窗不再弹
- ✅ `hdc shell hilog | grep -i HttpInterceptor` 能看到请求/响应 body
- ✅ 有 OAuth SDK 时：登录 → 授权 → 回调 onResp 触发

---

# Phase 3: 字节级验证（加密 / 编码）

## 目标

让 SignUtil 产出的字节序列与 Android 端**完全**一致。

> **对账基线优先用 probe golden fixture**：若 spec 期跑过场景 E 活性探针，`spec/baseline/api-inventory/data-chains/chain-auth.golden.json` 已存一次**被后端接受**的真实请求（含签名输入串 + 字节）。Phase 3 用 `verify-sign.js` 拿它做 ArkTS SignUtil 的离线字节对账——比"设备实测"更早、无需设备，闭"spec 证明契约可复现 → execute 证明 ArkTS 复现了它"的回路。无 golden 时才回退真机 200 实测。
ArkTS 在加密链路有 3 个叠加陷阱（详见 pitfalls.md A 类）：

1. `buffer.from(str,'utf-8').buffer` 返回内存池整段（含脏数据）
2. `util.TextEncoder.encodeInto(str)` 可能返回带 byteOffset > 0 的 view
3. `createSymKeyGenerator('HMAC|SHA1')` 在 HMOS NEXT 6.0+ 某些 build 不被识别

## 检查项

| # | 检查项 | 失败征兆 |
|---|--------|---------|
| 3.1 | SignUtil 用 utf8Bytes 防御性拷贝 | `ConvertSymmKey: Invalid param: input key length is invalid!` |
| 3.2 | HMAC 用 `createSymKeyGenerator('HMAC')` 无后缀 | 同上 |
| 3.3 | hex 大小写按签名链路区分 | 签名长度对但与服务端不一致 → 401 |
| 3.4 | base64 vs hex 输出选对 | 服务端拒绝 |

## 3.1-3.2 核心修复

```typescript
// 防御性拷贝
private static utf8Bytes(str: string): Uint8Array {
  const encoded = new util.TextEncoder('utf-8').encodeInto(str);
  const own = new Uint8Array(encoded.length);
  own.set(encoded);   // 强制 byteOffset=0 + 独立 ArrayBuffer
  return own;
}

// HMAC 无后缀写法
const mac = cryptoFramework.createMac('SHA1');
const symKeyGen = cryptoFramework.createSymKeyGenerator('HMAC');   // 不要 'HMAC|SHA1'
```

完整模板见 [templates/code/sign-util.ets](templates/code/sign-util.ets)。

## 3.4 诊断手段

```typescript
hilog.info(DOMAIN, TAG,
  'key.len=%{public}d byteOffset=%{public}d buffer.size=%{public}d',
  keyBytes.length, keyBytes.byteOffset, keyBytes.buffer.byteLength);
```

判定：`byteOffset === 0` ✅ + `buffer.byteLength === length` ✅。任一不符 → 走防御性拷贝。

## 3.5 与 Android 字节级对比

**先离线验证算法再写代码**：用 [scripts/verify-sign.js](../scripts/verify-sign.js) 把 Phase 0 抓到的真实请求（body + ts + token + 期望 ss）喂进去，用 Node 跑候选签名算法逐字节比对 —— 对上了再写 HMOS SignUtil，把"实现后赌联调"变成"验证后写代码"。

在 Android + HMOS 端用同样的 input + secret 跑算法，对比中间值：中间值不同 → §1.4 对账表抽错（大小写）；中间值同但最终不同 → HMAC algName / encodeInto 字节问题。

## Phase 3 通过标准

- ✅ 至少 1 个签名接口 200 响应（不再 401）
- ✅ hilog 中 signature 非空（不再 `convert sym key failed`）
- ✅ Android + HMOS 同 input 算出的签名字节级一致

---

# Phase 4: 响应链路验证

## 目标

让 `HttpClient.executeAndParse<T>` 返回的对象真实包含业务字段。Android Retrofit + ResponseInterceptor 隐式做了 body unwrap + @SerializedName 字段映射，ArkTS 没有，必须显式做。

## 检查项

| # | 检查项 | 失败征兆 |
|---|--------|---------|
| 4.1 | HttpClient.unwrapBaseBean 自有业务实例启用，三方实例关 | HTTP 200 但 userData 字段全 undefined |
| 4.2 | unwrapAndMirror 含字段镜像（status→errorCode 等） | isResponseSuccess 永远 false |
| 4.3 | @SerializedName 业务字段全加入 FIELD_MAP | 部分 Bean 字段读不到 |
| 4.4 | ResponseInterceptor token 过期检测基于 unwrap 后字段 | Token 失效不触发重登 |

## 4.1-4.2 核心实现

Android 后端常见响应：`{ "code": 0, "data": { "status": 0, "token": "...", ... } }`。三方厂商域（如调用第三方 API 服务）响应结构与自有业务不同，**不要** unwrap。

```typescript
private static unwrapAndMirror(root: Object): Object {
  const top = root as Record<string, Object>;
  const dataField = top['data'];
  const body = (typeof dataField === 'object' && dataField !== null && !Array.isArray(dataField))
    ? dataField as Record<string, Object>
    : top;   // 兼容扁平响应
  // 镜像 @SerializedName 等价：status→errorCode / toastMsg→errorMsg / ...
  HttpClient.FIELD_MAP.forEach((arktsName, jsonName) => {
    if (body[jsonName] !== undefined && body[arktsName] === undefined) {
      body[arktsName] = body[jsonName];
    }
  });
  return body;
}
```

完整模板见 [templates/code/http-client-unwrap.ets](templates/code/http-client-unwrap.ets)。

## Phase 4 通过标准

- ✅ HTTP 200 接口返回的 typed 对象字段非空
- ✅ `isResponseSuccess(userData)` 正确返回 true
- ✅ Token 失效时正确抛 TokenExpiredException
- ✅ 三方域接口响应不被误 unwrap

---

# Phase 5: UI 响应式订阅

## 目标

保证登录态 / VIP 等级变化后 UI 即时刷新。Android Fragment 被 Activity 注入数据，迁移到 HMOS Component 时容易沿用心智用 `@Prop`，但 ArkUI 调用方 `MineComponent()` 直接调用不传参 → 全部默认值 → UI 永远未登录态。

## 检查项

| # | 检查项 | 失败征兆 |
|---|--------|---------|
| 5.1 | 依赖全局 AppStorage 数据的字段用 @StorageProp 而非 @Prop | UI 永远默认值 |
| 5.2 | UserRepository.saveUserData 派发 USER_DATA_UPDATE | 跨页面 UI 不同步 |
| 5.3 | 写入 AppStorage 都通过统一入口（Repository） | 漏派发事件 |
| 5.4 | 账号详情类页面 @StorageLink + EventBus 双订阅 | 跨页面切换不刷新 |

## 5.1 反模式 vs 正模式

```typescript
// ❌ 反模式：@Prop 让父级传，调用方常漏传
@Component
export struct MineComponent {
  @Prop isLogin: boolean = false;
  @Prop userId: string = '';
}

// ✅ 正模式：@StorageProp 自治订阅
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

## 5.3 UserRepository 写入入口

所有 AppStorage('userData') 写入通过 `UserRepository.saveUserData`：写 AppStorage → 同步 Preferences → `EventBus.post(USER_DATA_UPDATE)`。业务侧禁止直接 `AppStorage.setOrCreate`。

## Phase 5 通过标准

- ✅ 冷启后未登录 → 「我的」Tab 显示 "立即登录"
- ✅ 登录流程走完 → 「我的」Tab 自动显示真实昵称 / ID
- ✅ 退出登录 → 自动切回未登录占位
- ✅ VIP 支付成功后 → 入口图标自动切换

---

# Phase 6: 联调实测

## 目标

按业务链路四级测：启动 → 登录 → 业务 → 支付。前一级未通不要测下一级。

> HMOS 侧「编译 → 签名 → 装包 → 冷启 → 过隐私门 → 抓 hilog → 与 Android 基线对账」的完整操作手册见 [phase6-runbook.md](phase6-runbook.md)。

## 6.1 启动链路

```
[ ] 冷启动 → SplashPage 进度条满 → 进 HomePage
[ ] /app/config 返回 status:0 + 业务字段
[ ] /user/initUser 返回 status:0 + token 非空 + userId>0
[ ] AppStorage('userData' / 'oaid' / 'androidId') 写入成功
[ ] 第二次冷启动协议弹窗不再弹
[ ] HttpLogInterceptor 输出请求/响应日志
[ ] 启动期请求时序与 Android 一致（抓包顺序 / tt 时间戳；Android config→initUser 串行则 HMOS 不能并发抢跑）
```

**与 Android 基线对账**：HMOS 冷启动抓取（hdc 镜像 adb 流程，纯命令行可脚本化）+ 与 Phase 0.3 `sample-requests.md` 逐接口对比的方法，见 [capture-android-traffic.md](capture-android-traffic.md) 的「与 HMOS 侧冷启动对比」节 —— 这是启动链路最硬的证据。

## 6.2 登录链路

> 静态前置是 §1.8 `auth-chain.md`：联调前六要素应已全部有归属；本节逐条实测就是对那张表的运行期验证。测出的差异回写该表 + 销账对应 `uncertainties[]`。

```
[ ] 发送验证码接口 返回 status:0 + 短信下发
[ ] 验证码登录 / 三方登录接口 返回 status:0 + 新 UserData
[ ] UserRepository.saveUserData + EventBus.post(USER_DATA_UPDATE)
[ ] 个人中心页显示真实昵称 / ID
[ ] 退出登录接口 → UserData 清空 + 个人中心页切回未登录
[ ] 游客/设备身份语义与 Android 一致（auth-chain #6：退出登录后「游客登录」按 identity_model 预期回原身份或新建）
[ ] token 失效场景（mock 失效码）→ 按 auth-chain #4 的适用范围规则处理（guest 态不误清）
```

## 6.3-6.5 业务 / 支付 / 推送链路

按工程具体接口逐个测：列表 / 详情 / 上传 / 下载 / 三方域接口 / 支付（preCreate → 调起 SDK → onResp → queryOrderStatus）/ 推送（getuiCid 上报 → 收消息 → 点通知路由）。

## 网络异常场景

```
[ ] 离线 → NetworkUnavailableException + UI 离线占位
[ ] 超时 → NetworkTimeoutException
[ ] 5xx → HttpException + 友好提示
[ ] Token 失效（mock -1001）→ TokenExpiredException + 跳登录
[ ] JSON 解析失败（mock HTML 错误页）→ 友好提示
```

## Phase 6 通过标准

- ✅ 6.1 / 6.2 全部通过（启动 + 登录基线打通）
- ✅ 6.3 至少核心业务 3 条接口通过
- ✅ 网络异常场景至少覆盖断网 / 超时 / 5xx / Token / JSON 错
- ✅ 全程 hilog 无 ERROR 级日志

## 联调中发现新问题

按 [error-lookup.md](error-lookup.md) 反查 Phase，**回到那个 Phase 闭环修复**，然后 Phase 6 当前点重测。不要在 Phase 6 直接改代码绕开问题，不要跳过失败接口继续测。

**后端业务错误（-500 / NPE / 字段类）首修未中 → 禁止连续盲试**：不要「改字段 → 重编译 → 再试」连刷。每轮 build→install→冷启→抓 hilog 成本 3-4 分钟，盲试 3 轮 ≈ 浪费一个 Phase。首修没命中 → 立刻回 Phase 0 用代理抓 Android 真实请求（headers + body，见 [capture-android-traffic.md](capture-android-traffic.md)），与 HMOS 逐字节对比，一次找全所有差异再批量修。详见 pitfalls D4 / D6。
