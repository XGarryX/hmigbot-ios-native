---
name: ios-api-inventory
description: "iOS→HarmonyOS 迁移源分析第 4 类（API 接缝层）：从 Swift/ObjC 源码提取外部服务契约（URLSession/Alamofire/GraphQL/WebSocket/SSE/WKWebView bridge）、系统框架与权限/entitlements/privacy、三方 SDK 与本地桥接接缝，产出带源锚点与调用证据的 api-inventory。当用户说“梳理这个 iOS 项目的接口/API/权限/三方 SDK”“盘点 iOS 侧系统能力”或 a2h-spec 组织四类分析时使用。不要用于：工程边界与 target 成员（用 ios-project-inspector）、UI 结构（用 ios-ui-analyzer）、功能行为链（用 ios-feature-analyzer）、目标库选型与移植实现（用 arkts-library-migration 等 arkts-* 技能）。"
metadata:
  type: domain
  domain: migration
  tags:
  - ios
  - analysis
  - api
  - evidence
---

> **调用关系**：本 skill 是 `ios-source-analysis` 组织的四类分析之一（API 类），负责「服务/系统能力/权限/三方接缝」维度。本 skill **不派发 subagent**，全部步骤在主会话或由派发方（a2h-spec / ios-source-analysis）作为子代理调起执行；若作子代理调起，任务书自足（写清源锚点、scope=api、输出契约），完成后由派发方按 Join 协议收口——**完成依据按 [a2h-join](../a2h-join/SKILL.md)：本轮可信宿主 `completed` 或经过身份与时序核验的原生 `FINAL_ANSWER`；产物存在不能代替完成**；本 skill 自身不嵌套外派。
>
> 路径约定：`$IOS_SRC` 从 `<target>/.migbot/config.json` 的 `ios` 字段读取；`<target>` = 鸿蒙目标工程根；`<runtime>` = 本包 runtime（`scripts/a2h_ios.py` 所在根，可用 `<skill>/scripts/run.py --runtime-root` 解析）。产物落 `<target>/spec/`，**禁落会话临时目录**。机器信号文件（`ios-api-signals.json`）由 facts-view 单写，主会话/作者禁手改。

# ios-api-inventory — 外部服务、系统能力与三方 SDK 接缝

适用的 Apple 官方技能与 Xcode MCP 优先。先读取 `spec/ref/ios-expertise-plan.json` 与 `ios-official-analysis.json` 中为本类选择的资源，按原始摘要完成审阅；官方资料、只读 MCP、CLI 和编译器分别记录来源、用途、读写范围及实际结果。无官方证据时记录降级原因，保持相关 unknown；不把第三方资料或自编规程称为 Apple 官方。设备远程控制不在默认调用范围，界面授权由用户自行完成。


### 官方分析的执行责任（0.13.1）

当 `ios-expertise-plan.json` 为当前主题选择 Apple 资源时，对应主题的分析过程由导出 skill 的适用规程承担：逐项执行其相关参考的审阅步骤，沿真实源码记录观察、未决项和影响；本技能保留迁移输出字段、归属和门禁合同。不得仅确认已读资料后继续用自编经验替代官方审阅。SwiftUI 使用 swiftui-specialist 的相关结构、状态、身份、环境或文本章节；App Intents 使用 app-intents-specialist 的执行模型、实体/参数、结果及快捷短语章节；文档型 SwiftUI 与 C bounds 仅在实际源输入适用时执行对应导出 skill。没有覆盖该主题的官方 skill 时明确保留自编/第三方分析，不伪称官方执行。

每条 Apple 源观察用 `expertise-review` 写入 `official_basis` 数组，字段为固定资源的 `path`、`sha256`、实际适用的 `section` 与具体 `application`。同时保留 `source`、`interpretation`、`unknowns`。只有资源确认、没有资源规则如何应用到源码的记录将被拒绝；此合同核验不替代对模型判断的独立复核。官方语义规程不能批准产品取舍或目标平台替代。

Swift 文件的词法/声明结构优先消费当前 facts 中固定的 SwiftParser/SwiftSyntax 产物，不能为了旧 Python 闭合语法可接受而改写源文件。编译上下文由实际 Xcode CLI 产物或经过校验的同源回放承担；MCP 不可用保留原错误和未决项。远程控制、界面读取及权限修改不在此分析范围。

## 0. 定位与纪律

### 设计理念与边界

**脚本/命令管「信号与事实」，模型管「理解与编目」；本 skill 只做源侧编目（inventory），不做对账。**

- 机器事实（`facts` + `facts-view --scope api`）负责把 Swift/ObjC 里的调用点、依赖、权限键、entitlements、privacy manifest 等**确定性抽出来**，产出 `ios-api-signals.json`；模型不重扫这些信号，只沿它们追源码语义，再现场撰写含义、归组、契约与决策。
- **边界（重要）**：本 skill 只产出**源侧静态契约**。iOS↔HarmonyOS 的**双边对账（runtime / reconciled 段）不属于本 skill**——那归 `arkts-network-troubleshoot`。三段式 endpoint 契约中本 skill 只写 `static` 段，`runtime`/`reconciled` 一律留 `null`。编目可泛化，对账不并入，两者别混。

- **前置**：`<target>/.migbot/config.json` 存在且 `source_platform=ios`；上游已跑 `source-index` + `facts`（缺 → 提示先由 a2h-spec 完成 §1 基线启动，不代跑）。API 事实建立在机器 `facts` 之上，不另起炉灶。
- **输入**：iOS 源码（Swift/ObjC 调用点）、`Info.plist`、`.entitlements`、`PrivacyInfo.xcprivacy`、`Package.resolved`/`Podfile.lock` 等依赖锁定文件、公开接口与源测试。**依赖名只用于候选定位，不证明被使用**——真正调用点靠沿源码追。
- **输出**：`spec/baseline/api-inventory/{api-inventory.json,api-inventory.md}`（分层形态另加 `common.md` + `apis/<模块>.md`）；机器事实视图 `spec/ref/ios-api-signals.json`（facts-view 单写）。JSON 保留 HMigBot 契约 `services[].endpoints[].static.{http_method,path,protocol}` 与 `services[].auth_type`，另加 `source_platform: "ios"`、`source_anchors`、`fact_ids` 与平台能力表。
- **唯一交互点**：无。机械检查由 exit code 判定（0=PASS，非 0=FAIL）；业务判断全部下沉到门禁与 facts 裁决，不交互追问。
- **第一条可见输出必须是一行阶段计划**（机器事实 → 外部服务 → 系统能力 → 配置隐私 → 三方桥接 → 目标决策 → 验收），然后才执行 §1。

### 无人值守处置阶梯（每道门禁 FAIL 一律套用）

> FAIL → 按命令 `retry_hint`/错误原文派修复并重跑同一命令，**最多 2 轮**；2 轮仍不过或确定模型修不了 → **记欠账放行**（账记全：修过几轮、每轮失败原因、判“修不了”的依据）；要拍板的模型自决并留痕；任何分支不得停机呈报人工。设备/账号类门可欠账；静态门即便开了 `stage_debt` 也照常修到 PASS。

## 1. 机器事实与信号（先读，不手改）

| # | 命令 | 产物 | exit / 处置 |
|---|---|---|---|
| 1.1 | `python <runtime>/scripts/a2h_ios.py facts --project <target>` | `spec/baseline/ios-facts.json` + `ios-obligations.json` | 非 0 读错误原文修配置重跑，最多 2 轮 |
| 1.2 | `python <runtime>/scripts/a2h_ios.py facts-view --project <target> --scope api` | `spec/ref/ios-api-signals.json`（机器信号） | 非 0 = 依赖/调用点信号未抽全，补 facts 后重跑 |
| 1.3 | `python <runtime>/scripts/a2h_ios.py product-literals --project <target> [--output <path>]`（按需） | 业务常量/字面量账本（缺省落点以命令返回为准） | 非 0 记 warning，不阻断；常量/字面量保留实际值 |

- 先读 `ios-api-signals.json` 与工程依赖，**沿真正调用点**识别 URLSession/三方 client、存储、系统框架、权限、entitlements、xcprivacy、登录/支付/广告/客服接缝。**禁止手写或篡改机器信号**，也不采用上游重构建议改写源行为。
- 事实读法（源码证据分级）按 `../ios-source-analysis/references/source-semantics.md`；证据强度区分“源码位置 / AST / 符号服务 / 构建 / 运行”，**不能互相升级**，未解析的动态分派/宏/闭源模块进未知清单。`product-literals` 只提供常量视图，**不替代沿调用点追语义**；API 关键常量（base host、路径片段、签名盐、业务码）保留源表达式文本与源锚点，不自求值。

### 单写者分区（违者 PROCESS_VIOLATION）

| 文件 | 唯一写者 | 内容 |
|---|---|---|
| `spec/baseline/ios-facts.json` + `ios-obligations.json` | facts 命令 | 机器事实/义务 |
| `spec/ref/ios-api-signals.json` | facts-view 命令 | API 机器信号 |
| `spec/baseline/api-inventory/*` | 本 skill（模型作者） | 人类/机器契约 |
| `spec/.a2h/open-findings.json` | 产生该 finding 的检查 | 未关闭发现 |

主会话与作者手改上表“机器/命令单写”文件即契约违规。

## 2. 识别技术栈与接缝类型

先判定项目网络层与接缝形态（对应安卓版的“识别项目技术栈”），决定 §3–§6 的提取重点，避免按模板硬套：

| 接缝类型 | Swift/ObjC 证据（候选信号，仍需沿调用点证实） | 提取重点 |
|---|---|---|
| 原生 REST | `URLSession` / `URLSessionDataTask` 实际构造与 `.dataTask(with:)` | method/path/base URL/header/编码/错误信封 |
| 三方 REST 客户端 | `Alamofire`（`AF.request`/`Session`）、`Moya`（`TargetType`+`Endpoint`） | 拦截器/插件、参数编码、token 注入 |
| GraphQL | `Apollo`（`@GraphQLQuery`/`ApolloClient`） | operation 名/变量/响应成型的 model_class |
| WebSocket | `URLSessionWebSocketTask`、`SocketRocket`、`Starscream` | 连接建链/心跳/重连/帧协议 |
| SSE | 自定义 `URLSession` streaming、`EventSource` 类库 | 事件流、重连、`null` reset 语义 |
| 系统 WebView bridge | `WKWebView`/`WKScriptMessageHandler` | JS 桥消息名、原生↔Web 协议、userContentController |
| 本地桥接/NAPI | `@_silgen_name`、C/ObjC 桥、闭源 `.xcframework` 导出符号 | 类型/缓冲区/所有权/线程边界 |

**识别四项（Phase 2 心智模型，不产出文件）**：
1. **技术栈**：纯 URLSession？Alamofire/Moya 封装？SDK 主导（云服务/登录/支付全部黑盒）？离线应用？
2. **模块/域划分**：从目录、`enum`/`struct` 命名空间（`UserApi`、`PayApi`）、URL 常量命名约定推断业务域。
3. **鉴权方式**：读 auth 相关源码——`Bearer` token 注入？`apiKey`/`appId`+签名？（HMAC/SHA256/AWS-style）多套并存？设备指纹 header？
4. **三方分组**：按 provider/域名把同源调用聚为一组（推送、客服、AI、广告、支付等）。

### 2.1 依赖探测与补扫判定（对应安卓 Phase 1b）

先做快速探测，不凭感觉决定是否补扫：

**规则 A — 网络层存在性探测**：在源码根 grep 网络框架标识（`URLSession`、`Alamofire`、`Moya`、`Apollo`、`Starscream`、`SocketRocket`、`WKScriptMessageHandler`）。零命中且无 `URLSession`/`URLRequest` 语义 → 项目可能无 HTTP 网络层，分类为「离线 / 无外部 API」，跳到 §9 离线形态输出。

**规则 B — 信号量判定是否补扫**：看 `ios-api-signals.json` 的调用点/URL 常量/三方域数量：

| 情况 | 判定依据 | 处置 |
|---|---|---|
| 正常 REST 客户端项目 | 端点信号 ≥ 3 | 信号已充分，进 §3 |
| 混合（框架 + 裸 URLSession/WebView） | 端点 ≥ 1 且硬编码 URL/域名信号 ≥ 5 且多数未归属 | 补扫裸流式/桥接 |
| 非网络框架 / SDK 黑盒主导 | 端点 0 且三方依赖 ≥ 1 | 进 SDK 黑盒处置（§6），按导出符号与调用点编目 |
| 离线 / 无网络项目 | 端点 0 且三方域 0 | 直接产“本项目无外部 API”文档 |

**补扫范畴**：裸 `URLSession` streaming、WebSocket、SSE、GraphQL、gRPC、SDK 黑盒。**完整判定线索始终以 §6 的依赖锁定文件（Podfile.lock / Package.resolved）为准**，不放大混入业务。

## 3. 外部服务契约

- 从实际调用（URLSession、URLRequest、自定义 client、Alamofire、GraphQL、WebSocket、SSE、WKWebView bridge）追 `method/path`、base URL 选择（`Info.plist`/`.xcconfig`/`#if DEBUG` 环境切换/build setting 注入）、header、编码、签名、token 刷新、超时、重试、分页、缓存与错误信封。
- **源码未确定的 URL 片段/响应类型显式标 `dynamic`/`unknown`，不拼造完整端点**。endpoint 三段式契约中本 skill 只写 `static` 段，`runtime`/`reconciled` 一律留 `null`（归 arkts-network-troubleshoot 侧回填）。
- 公共鉴权与公共参数放 `common.md`；每个功能 spec 引用所属 endpoint ID，不重复展开。响应结构强制记录 `model_class`（响应类型），读不到时标 `model_class: "unknown"` + 原因，**不省略整个 response**。Swift `Codable` 结构体的字段名即 JSON 键（`CodingKeys` 别名单独还原），ObjC 侧按 `NSDictionary` 键值还原；`@_silgen_name`/运行时反射构造的字段记 `unknown`。
- 硬约束：**不抄源签名/账号配置到目标**；目标 bundle、证书、支付/推送注册各自核验，目标是另一套凭据域。

### 3.1 端点静态契约属性清单

每个 endpoint 的 `static` 段至少覆盖（读不到就标 `unknown`/`dynamic`，不删字段）：

| 属性 | 说明 | 未知处置 |
|---|---|---|
| `http_method` / `path` / `protocol` | REST/SSE/WebSocket + method/path | 路径片段动态 → `dynamic` + 保留表达式 |
| `base_url` | 环境/base host + 来源（config/`#if`/build setting） | env 未定 → 标候选 + `unknown` |
| `headers` / `params` | 静态头/公参/字段 | header 大小写/签名真值缺 → `unknown` |
| `encoding` | JSON/form/multipart/自定义 body 组装 | 组装逻辑读不到 → `unknown` |
| `auth_type` / `auth_detail` | bearer/apiKey/签名算法 | 算法不明 → `unknown` + 建不确定项 |
| `timeout` / `retry` | 超时/重试/退避 | 读不到标 `unknown` |
| `pagination` / `cache` | 分页/缓存策略 | 记 `unknown` |
| `error_envelope` | 响应信封 + 业务码/负值码语义 | 码语义缺 → ② 类不确定项 |
| `model_class` + 字段表 | 响应模型（强制的响应结构） | 拆不出 → `model_class: "unknown"` + 原因 |
| `feature_ids` / `source_anchors` | 关联 Feature + 源锚点 | — |

### 3.2 鉴权模型与数据链路

登录类功能打不通的缺口常在机制层而非端点清单。沿 `ios-api-signals.json` 的调用点线索主动 grep 补捕获盲区，重建鉴权链路六要素（对应安卓 auth_model）：

1. **token 获取** `token_acquisition`——auth 类端点（login/oauth/refresh）与 handler 位置；
2. **token 存储** `token_storage`——Keychain/UserDefaults/文件落点（**设备级字段通常保留，见 §6**）；
3. **token 注入** `token_injection`——header/body 注入点与字段名（`Authorization: Bearer` / 自定义签名头）；
4. **token 失效** `token_expiry`——业务码（负值码/`401`/自定义 code）+ 适用范围 + 动作（登出/踢出/游客态差异）；
5. **token 清除** `token_clearing`——退出/注销/被踢清什么、**留什么**；
6. **身份模型** `identity_model`——`device-bound` / `account-only`；游客态语义 + 不可逆边（首绑手机号后回不到游客态）判不出填 `unknown` 并建不确定项。

**任意要素读不到都显式填 `unknown` + 建不确定项，不能省略字段**——这些空洞就是下游 grill/对账要问的题目。将链路叙事（endpoint → 客户端 → UI/存储副作用）写入 `data_flows`，`chain: "auth"` 强制产出；支付、启动配置等链路按重要度选做。Keychain 的通用密码/service 分组、访问控制（`kSecAttrAccessible`）与设备的 iCloud 同步语义都要连同记录（影响鸿蒙侧持久化等价）。

7. **身份轴分类**（把机制显式化，供下游分支判定）：据上述证据填三轴——
   - **轴 A（游客 token 角色）**：登录前是否已拿到游客 token，游客登录语义是“新建游客”还是“取回设备身份”；
   - **轴 B（设备对登录的作用，可多占）**：设备标识是否掺入签名 / 作为绑定实体；
   - **轴 C（登录方式子集）**：账号密码 / 短信验证码 / 第三方登录 / 苹果登录（Sign in with Apple）/ 游客。
   对不上已知分支即 novelty 冒泡建不确定项，不硬套。

### 3.3 不确定项清单

遇到“拿不准”不要只在 md 标 unknown：逐条收进 `uncertainties[]`，分级铁律（对 iOS 语义）：

- **① 源码可定** —— 不入清单，模型自答写进 `static`/`auth_model`；
- **② 需真包/真环境**（响应壳形状、字段真实类型与默认值、业务码语义、header 大小写、`model_class: unknown` 的响应结构、加密 body 内容、`@_silgen_name` 的真实符号）—— 入清单，等 grill 索证或抓包销账；
- **③ 策略待确认**（bundle/签名发哪个包、联调期加密开关、多网关取舍、HarmonyOS 无等价公参字段的处置）—— 入清单，grill 必问用户。

每条必填所属链路与影响（不答会影响什么实现决策），人类可读投影落 `api-inventory.md` 末尾「不确定项清单」段。

### 3.4 边界案例与常见坑（iOS 语义）

- **动态 URL**：`URLComponents`/字符串插值拼路径、自定义 `enum` 常量的 `rawValue` 拼 host+path——端点 path 标 `dynamic` 并保留拼接表达式与常量来源，不伪造唯一完整路径。
- **环境切换**：`#if DEBUG`/`.xcconfig`/`Info.plist` 注入的 base host 多套并存——全部登记、标环境名，不默认只记生产。
- **`CodingKeys` 别名**：JSON 键与 Swift 字段名不一致（snake_case→camelCase、自定义映射）——按 `CodingKeys` 还原真实 JSON 键；“字段名即 JSON 键”只是 `Codable` 默认情形。
- **同域名多 endpoint**：同一 provider 域名对应多个 Action/endpoint（参数化 URL，如云服务 Action 参数）——按 provider/域名归组，不按域名只建一条。
- **跨 target 重复端点**：主 App 与扩展分别定义同 path（如 `/push/register`）——去重并说明多处定义，不误判为互斥。
- **multipart/流式 body**：`multipartFormData` 组装点、`InputStream` body——记录组装函数与字段表，防字段漏抽。
- **SSE 在鸿蒙支持有限**：保留 `protocol` 与重连/`null` reset 语义标签，供下游标 `migration_concerns`。

## 4. 系统能力矩阵

为每个使用点记录：框架、方法、触发、返回数据/句柄域、回调线程、权限前后状态、应用与扩展可用性、设备/版本限制、后台约束、失败表现。覆盖实际出现的相机/媒体/相册/位置/蓝牙/NFC/通知/后台/联系人/日历/文件/分享、StoreKit、Sign in with Apple、HealthKit、CloudKit、WidgetKit、App Intents 等能力。**列表只是检查线索**：未出现的能力写「不适用」，不能给任意应用捏造接口。

### 4.1 能力→框架→权限映射（译自安卓“平台能力→SDK 映射”）

| 能力域 | iOS 框架/入口 | 权限键（Info.plist 用途字符串 / entitlement） | 迁移关注点 |
|---|---|---|---|
| 相机/麦克风 | `AVFoundation`（`AVCaptureDevice`） | `NSCameraUsageDescription` / `NSMicrophoneUsageDescription` | 权限授予时机与回调线程 |
| 相册/照片库 | `Photos`（`PHPhotoLibrary`）/ `PhotosUI`（`PHPickerViewController`） | `NSPhotoLibraryUsageDescription` / `NSPhotoLibraryAddUsageDescription` | PHPicker 无权限弹窗（受限库）与 PHAsset 全量访问区别 |
| 位置 | `CoreLocation`（`CLLocationManager`） | `NSLocationWhenInUseUsageDescription` / `NSLocationAlwaysAndWhenInUseUsageDescription` + `UIBackgroundModes=location` | 前台/后台/always 授权路径与临时精确授权 |
| 蓝牙 | `CoreBluetooth` | `NSBluetoothAlwaysUsageDescription` / `NSBluetoothPeripheralUsageDescription` | 中心/外设角色与后台限制 |
| NFC | `CoreNFC`（`NFCTagReaderSession`） | `com.apple.developer.nfc.readersession.formats` entitlement | 仅读、格式列表在 entitlement |
| 通知 | `UserNotifications`（`UNUserNotificationCenter`） | `aps-environment` entitlement + 授权请求 | 前台/后台/静默推送、token 注册与回执 |
| 联系人 | `Contacts` | `NSContactsUsageDescription` | 读/写权与 `CNContactStore` 授权 |
| 日历/提醒 | `EventKit` | `NSCalendarsUsageDescription` / `NSRemindersUsageDescription` | 事件/提醒分开授权 |
| 健康 | `HealthKit`（`HKHealthStore`） | `com.apple.developer.healthkit` entitlement + `NSHealthShareUsageDescription` / `NSHealthUpdateUsageDescription` | 读/写类型分别在 entitlement 授权 |
| 运动与健身 | `CoreMotion` | `NSMotionUsageDescription` | 计步/传感器数据 |
| 语音识别 | `Speech` | `NSSpeechRecognitionUsageDescription` | 在线/离线识别 |
| 面容/FaceID | `LocalAuthentication` | `NSFaceIDUsageDescription` | 生物特征与 Keychain 保护联动 |
| 云同步 | `CloudKit` | `com.apple.developer.icloud-container-identifiers` / `-services` + `aps-environment` | 容器/环境切换与服务类型 |
| 支付 | `StoreKit`（`SKPaymentQueue`/`StoreKit2`） | —（Transaction 凭据） | 内购产品/订阅/沙盒验证；鸿蒙 IAP 无 1:1 等价 |
| 苹果登录 | `AuthenticationServices`（`ASAuthorizationAppleIDProvider`） | `com.apple.developer.applesignin` entitlement | 匿名化标识、回调域配置 |
| 广告追踪 | `AdSupport` + `AppTrackingTransparency` | `NSUserTrackingUsageDescription` | ATT 弹窗与 IDFA 获取 |
| 小组件/App Intents | `WidgetKit` / `AppIntents` | 独立 extension target | 时间线刷新与意图参数 |
| 分享/Activity | `UIActivityViewController` / `ShareExtension` | `NSExtension` 声明 | 分享扩展在独立 target |
| 本地网络 | `Network`/`MultipeerConnectivity` | `NSLocalNetworkUsageDescription` | 局域网发现与隐私弹窗 |

每条记录“权限申请时机 → 授予/拒绝/受限 → 回调与撤销路径 → 失败表现”，**用途字符串只证明声明，不能证明用户实际授权**，见 §5。

### 4.2 Info.plist 用途键完整性核对

用途字符串键 = 系统能力的**声明证据**，必须与 §4.1 实际调用点逐一交叉核对。未出现在 §4.1 表内但工程实际声明/使用的键也应完整登记（清单式核对表，不捏造）：

| 键 | 能力 | 与 §4.1 调用点的核对 |
|---|---|---|
| `NSLocationAlwaysUsageDescription` | 旧版始终定位（iOS 11 前） | 与 `NSLocationAlwaysAndWhenInUse*` 并存时只算兼容声明 |
| `NSSiriUsageDescription` | 发送数据给 Siri | 与 `SiriKit` 调用点绑定 |
| `NSAppleMusicUsageDescription` | 媒体资料库 | 与 `MediaPlayer`/`MPMediaLibrary` 绑定 |
| `NSDesktopFolderUsageDescription` / `NSDocumentsFolderUsageDescription` / `NSDownloadsFolderUsageDescription` | 文件访问（沙盒外） | 与 `UIDocumentPickerViewController`/安全作用域绑定 |
| `NSVideoSubscriberAccountUsageDescription` | 订阅账户 | 与 `VideoSubscriberAccount` 绑定 |
| `NSBluetoothPeripheralUsageDescription` | 蓝牙外设（旧） | 与 `CBPeripheralManager` 绑定 |

**红线**：用途字符串缺失但存在对应框架调用 → 记 finding（崩溃级风险）；用途字符串存在但无对应调用 → 记「未使用声明」，不作为迁移依据。

### 4.3 entitlement 枚举与迁移关注点

| entitlement | 用途 | 迁移关注点 |
|---|---|---|
| `com.apple.developer.aps-environment` | 推送环境（development/production） | APNs token 生命周期、鸿蒙 Push 无 1:1 等价 |
| `com.apple.security.application-groups` | App Group 共享容器 | 主 App 与扩展的共享数据容器映射 |
| `keychain-access-groups` | Keychain 共享组 | 跨扩展凭据共享组映射 |
| `com.apple.developer.associated-domains` | Universal Link / handoff | applinks 域名与鸿蒙深度链接 |
| `com.apple.developer.healthkit` | 健康数据读写 | 鸿蒙健康数据无等价时记 HARD-DIV |
| `com.apple.developer.nfc.readersession.formats` | NFC 标签格式 | 与鸿蒙 NFC 能力覆盖对账 |
| `com.apple.developer.icloud-container-identifiers` / `-services` | CloudKit 容器/服务 | 云同步替代方案 |
| `com.apple.developer.applesignin` | Sign in with Apple | 账号体系替代 |
| `com.apple.developer.in-app-payments` | Apple Pay | 支付替代 |

entitlement 只是声明，实际能力仍按 §4.1 调用点 + 授权请求路径核实；**不把 entitlement 存在当作能力已生效**。

## 5. 配置与隐私

交叉核对调用点、usage descriptions、entitlements、URL schemes、associated domains、ATS、App Groups、Keychain groups、背景 modes 与 privacy manifest：

| 配置面 | iOS 载体 | 核对内容 |
|---|---|---|
| 用途字符串 | `Info.plist` 的 `NS*UsageDescription` | 每处系统能力调用必有对应键；键声明≠授权 |
| 系统能力须给 | `.entitlements` | `aps-environment`/`application-groups`/`keychain-access-groups`/`associated-domains`/`healthkit`/`nfc`/`icloud-container-*` |
| 网络安全 | `Info.plist` 的 `NSAppTransportSecurity` | ATS 例外（`NSAllowsArbitraryLoads`/`NSAllowsLocalNetworking`/`NSExceptionDomains` 按域名例外）与鸿蒙明文/证书策略差异 |
| URL 回调 | `CFBundleURLTypes` + `associated-domains` | scheme、Universal Link 的 applinks |
| 后台模式 | `UIBackgroundModes` | 后台音频/定位/后台拉取/远端通知等，与系统能力矩阵联动 |
| 隐私清单 | `PrivacyInfo.xcprivacy` | 声明的数据收集类型/用途与原码实际访问是否一致（`NSPrivacyAccessedAPITypes`） |

- **用途字符串只证明声明，不能证明用户实际授权**；权限拒绝与撤销路径继续读实现，不能停在 Info.plist 键。
- 隐私事实按 `../a2h-privacy/SKILL.md` 的口径记录敏感数据流（存在时），仍以本 skill 的接缝身份交出权限边界。**不把隐私清单声明当作运行时行为真值**；`NSPrivacyAccessedAPITypes` 与源码实际用法不一致时标 `mismatch` 并记 finding。

## 6. 三方与本地桥接

- 每个依赖记录版本、源码可见性、调用点、数据协议、资源、初始化/释放与平台限制。优先查厂商官方鸿蒙支持与对应版本，再查公开实现；保留来源日期与实测状态。

依赖接缝分类（iOS 等价于安卓的“源码包/预编译/动态加载/插件”）：

| 接缝形态 | 载体 | 处置 |
|---|---|---|
| 源码包（可见符号） | SwiftPM（`Package.swift`/`Package.resolved`）、CocoaPods（`Podfile`/`Podfile.lock`，源码可见） | 记录精确版本 + package identity + 调用点 + 公开协议 |
| 预编译二进制 | `.xcframework`/`.framework`/`.a`/`vendored_framework`（`Podfile.lock` 标记） | 记 `opaque`，只记录可见导出符号与所需公开契约/运行证据 |
| 动态加载 | `dlopen`/`Bundle`/`NSClassFromString` 运行时装配 | 记 `dynamic`，可观测行为与失败表现 |
| 本地桥接 | `@_silgen_name`、Bridging Header、`module.modulemap`、NAPI 风格 C 桥 | **NAPI 方案必须定义类型、缓冲区、所有权与线程边界** |

### 6.1 依赖锁定文件枚举

依赖**版本锁定文件**用于确定候选与精确版本，**不代表被使用**：

| 依赖管理 | 锁定文件 | 内容 |
|---|---|---|
| CocoaPods | `Podfile.lock` | pod 名/版本/checksum/`vendored` 标记 |
| SwiftPM | `Package.resolved` | package identity/版本/commit hash |
| Carthage | `Cartfile.resolved` | 框架名/版本 |

- **NAPI 方案必须定义类型、缓冲区、所有权与线程边界；禁止把 `.xcframework` 改扩展名当目标库**。无法读到的内部行为记 `opaque` 并指定所需公开契约或运行证据。**不能根据包名猜其运行行为**——`依赖只用于候选定位`。

## 7. 目标映射与决策

- **映射不是 API 名字替换**。区分「行为等价但实现不同」的 HARD 与「行为变化」的 HARD-DIV。
- **HARD-DIV 必须有决策 ID、源行为、替代数据流、被替代 AC 与新差异 AC**，按本轮授权确认产品选择；未知工具能力不能伪造为可用。典型 HARD-DIV：内购 StoreKit→IAP 无等价、苹果登录→鸿蒙账号、推送 token 生命周期、Keychain 共享组、ATS 例外策略。
- 目标库核验交 `arkts-library-migration` / `hmos-sdk-docs`；选择依据须匹配当前 SDK 与实际接口，不能靠相似名称。目标实现按实际领域使用 `arkts-system-capabilities`、`arkts-data-layer`、`arkts-login`、`arkts-payment`、`arkts-media-playback`、`arkts-webview` 等技能（引用技能名作下行衔接，不在本 skill 展开）。对账与运行时差异回 `arkts-network-troubleshoot`。

## 8. 外部资料与工具证据

1. `python <runtime>/scripts/a2h_ios.py expertise-plan --project <target>` → `spec/ref/ios-expertise-plan.json`；按本轮 API 主题清单读取实际上游资料（swiftui/concurrency/uikit pack 中与本 skill 相关项），再用 `expertise-review --input <review.json>` 提交源观察。未连接工具保持 `unknown`/`unavailable`；**不伪造官方执行**。
2. 需要符号证据时 `python <runtime>/scripts/a2h_ios.py mcp-query --project <target> --server <server.json> --request <query.json>`（示例见 `../ios-source-analysis/assets/mcp-server.example.json` 与 `mcp-query.example.json`）。只有固定源读工具白名单可调用；失败/超时写 failure.json，绝不写成功索引。
3. 工具来源、版本、实际是否执行写入 provenance；源码、Apple 文档、运行 trace 三源分列，不自编规程冠为官方。

## 9. 输出文档组织（按规模分层）

`api-inventory.md` **不固定单文件**——按项目规模选形态：

| 项目规模 | 产出形态 |
|---|---|
| 端点 ≤ ~15，或单 service | 单文件 `api-inventory.md`：逐个 endpoint 展开 + 一个「公共约定」段 |
| 端点 > ~15，或多 service | 分层：`api-inventory.md`（索引+导航表）+ `common.md`（公共约定）+ `apis/<模块>.md`（每模块一文件） |
| 离线 / 无外部 API | 单文件 `api-inventory.md`，说明无外部 API + 列系统级依赖即可 |

### 9.1 api-inventory.json 字段（机器可读事实源）

- **`api-inventory.md`**（分层时）＝总览索引：技术栈+数据总览、文档导航表（链到 `common.md` 与各 `apis/*.md`，标注端点数）、网络层架构摘要、三方 API 分组、Feature 候选 / 覆盖度分析。不放逐个 endpoint 明细。
- **`common.md`** ＝公共约定：响应信封、签名头、鉴权链路（鉴权模型的可读投影）、公共请求参数、共享响应体、业务码。文件名固定 `common.md`。
- **`apis/<模块>.md`**：每模块/功能域一文件，按代码命名空间或 service 划分；过小合并，目标 5–10 个文件。
- **端点统一模板**：方法+路径（+协议 REST/SSE/WebSocket）、调用位置（文件:行）、请求参数表、响应参数表（**强制表格化**，嵌套逐层展开，读不到标 `unknown`+原因）、runtime 状态（`⬜ static-only` / `✅ verified` / `⚠️ mismatch`，后两者归 arkts-network-troubleshoot）。
- **「合并一类」原则**：多端点复用的公参、共享响应体、信封/签名在 `common.md` 写一次，各文件用链接引用（`→ 见 common.md`），不重复展开。
- 可选链接视图 `spec/baseline/api-contract-links.json` 只连接既有端点 ID→feature/源锚点/精确 MD 标题，**不覆盖** `api-inventory.json` 的 `services` 结构；JSON 合法只代表字段形态，语义仍须独立源复核（见 `../a2h-spec/references/optional-json-contracts.md`）。

### 9.2 项目适配性说明

| 项目类型 | 适配度 | 备注 |
|---|---|---|
| URLSession/Alamofire + 多模块 + 拦截器签名 | ✅ 良好 | 端点与鉴权模型完整可抽 |
| URLSession 单模块 | ✅ 良好 | §2 按命名空间区分业务域 |
| SDK 黑盒主导（登录/支付/云服务） | ⚠️ 需手动识别 SDK 暴露接口 | 按导出符号与调用点编目，记 opaque |
| 离线 / 无网络层 | ✅ 简化输出 | 文档直接说明“无外部 API” |
| JS/Web 壳（WebView 承载） | ⚠️ 需桥接层分析 | 接口在 WKWebView bridge 与前端，Swift 层看不到业务接口 |

## 10. 覆盖度分析与 feature 候选（按 spec 状态分支）

先看 `spec/baseline/` 是否存在 feature 产物，再选分支（对 iOS 语义）：

| spec 状态 | 判定 | 分支 |
|---|---|---|
| 完整 spec 存在 | `feature-index.md` 与 `features/F*.md`（≥1）都在 | 分支 A：覆盖度审计 |
| 部分 spec | `feature-index.md` 在但 `features/` 空/稀疏 | 分支 B：增量对齐 |
| spec 未生成 | 无 `feature-index.md` 且无 `F*.md` | 分支 C：输入源模式 |

- **分支 A**：与各 `F*.md` 的 API 接口表对比，`missing_in_spec` / `missing_in_scan` 写入 `coverage` 字段与 md「覆盖度分析」节。`missing_in_scan` 可能因路径拼写不同、SDK 封装或真的遗漏，需模型判断。
- **分支 B**：对已生成 Feature 做分支 A 对齐；对未生成 Feature 用 `feature_ids` 反推“该 Feature 预期含哪些接口”，输出「Feature 待生成辅助」。
- **分支 C**：转为 feature 候选建议者。① 按路径前缀聚类端点（`/user/*`、`/pay/*`）；② 按三方 provider 提议；③ 标注迁移关注点（SSE/WebSocket、自定义签名、multipart、submit→poll→result 异步任务、跨 service 重复端点）；④ 输出到 `coverage.feature_candidates`。措辞标明“候选，spec 作者可采纳/调整/重划”，**不写成定论**。分支 C 的输出目标＝喂给 a2h-spec，不是终版交付。

## 11. 输出验收（门前自检）

- 每条记录可回到源文件:行；公共字段与 feature 引用一致；动态部分保留表达式与依赖。
- **没有设备或服务账号的测试保留 `not_run`，不用静态调用存在声称设备功能通过**。发布报告分开列生成、编译、协议观察与设备结果。
- 与 UI/功能作者的交接按 `references/analysis-v2.md` §「与功能/UI作者交接」：共享鉴权/数据类型/协议/生命周期放公共合同；领域动作的终态交唯一 feature/base 作者，本清单引用动作 ID 不另写终态。
- 源码变化时：重提 `facts`、重跑 `expertise-plan`、重审受影响项；旧清单/记录归档，旧 PASS 不继承。

## 12. 读取时机（references）

| 触发时机 | 必读文件 |
|---|---|
| 执行前确定机器产物/状态写者 | ../ios-source-analysis/references/harness-v2.md |
| 源码证据分级、动态分派/宏处置 | ../ios-source-analysis/references/source-semantics.md |
| facts 前身份/字段/溯源规则 | ../ios-source-analysis/references/native-facts.md |
| expertise-plan/review、MCP 查询边界 | ../ios-source-analysis/references/external-expertise.md |
| 服务/系统/三方接缝提取与交接 | references/analysis-v2.md |
| 与功能作者定义动作终态 | ../a2h-spec/references/action-contracts.md |
| 产物 profile/格式/作者/消费者 | ../a2h-spec/references/artifact-contracts.md |
| 可选 JSON 协议（api-contract-links.json） | ../a2h-spec/references/optional-json-contracts.md |

## 13. 交接

- 门前闸：`python <runtime>/scripts/a2h_ios.py source-check --harness --project <target>` exit 0 才交接；含 external-expertise 门禁（资料摘要/清单新鲜度/必需审阅/源范围）。FAIL 按 §0 阶梯最多修 2 轮，记欠账放行时如实呈报。
- 移交产物：`spec/baseline/api-inventory/*` + `spec/ref/ios-api-signals.json` + 审阅记录与 provenance 片段。随后把平台能力无法等价的项与决策 ID 交 `decision-ledger`，并把本层证据交回 `ios-source-analysis` / `a2h-spec`（同会话可直接续跑 Phase C 功能 baseline）。
- **与 a2h-spec 的集成契约**：本 skill 是四类源分析之一，由 `ios-source-analysis`/`a2h-spec` 组织调起；此时 spec 通常尚未生成 → §10 走分支 C，产出 `coverage.feature_candidates` 供 Phase C 功能拆分消费。被派发时返回 summary（服务数/端点数/feature 候选数/不确定项 open 数/鉴权模型是否产出），供编排侧收口判定。离线/SDK 黑盒 → 按降级逻辑产说明文档并显式标 `degraded`，不阻塞流水线。
- 本 skill 无独立 stage 水位（无 mark-stage）；`source-check --harness` 绿即是本维度的最终收口。