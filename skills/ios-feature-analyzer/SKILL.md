---
name: ios-feature-analyzer
description: "iOS→HarmonyOS 迁移源分析第功能步：沿 Swift/ObjC 的事件、任务、委托、服务与持久化链提取状态转移、错误/取消、数据契约与独立验收真值，写功能事实与原生语义供 a2h-spec/plan 消费。当用户说“分析这个 iOS 项目的功能/业务逻辑”，或 a2h-spec/ios-source-analysis 组织功能源分析时使用；不要用于：UI 结构与导航（用 ios-ui-analyzer）、系统 API/权限/三方接缝清单（用 ios-api-inventory）、工程边界与编译单元（用 ios-project-inspector）、写鸿蒙生产代码（用 a2h-execute）。"
metadata:
  type: domain
  domain: migration
  tags:
  - ios
  - feature
  - source-analysis
  - source-evidence
---

> **调用关系**：本 skill 是 `ios-source-analysis` 组织的四类源分析之一（功能主责），结果由 `a2h-spec` 收口。若宿主支持 subagent，按 `ios-feature-analyzer` 角色名派发（`fork_turns:"none"`，任务书写清功能候选/入口/输出契约）；不派发时主会话顺序执行。遵守 **Join 协议（收口五条款）**：① 循环 wait——完成唯一合法信号是 `agent_status=completed`；② 死句柄与验收——3 次超时后 `list` 核对，completed≠验收；③ 收口锚点——最终报告前收口全部句柄；④ 放行≠遗弃；⑤ fire-and-forget 仅正文显式声明的派发免收口。**谁派谁收**；契约产物必须出自承担任务的子代理。本 skill 只读源、写功能事实，**不派发下级 worker、不写目标代码、不决定未经授权的平台差异**。
>
> 路径约定：`$IOS_SRC` 从 `<target>/.migbot/config.json` 的 `ios` 读取；`<target>` = 目标根；`<runtime>` = 本包 runtime（`scripts/a2h_ios.py` 所在根）。产物落 `<target>/spec/ref/ios-feature-facts.md`（本 skill 单写）；原生语义由 a2h-spec 的 `spec-authoring` 落为 `spec/baseline/ios-semantics.json` feature 部分（机器校验）。本 skill 自有：`references/analysis-v2.md`、`scripts/run.py`。

# ios-feature-analyzer — iOS 功能行为与验收事实

适用的 Apple 官方技能与 Xcode MCP 优先。先读取 `spec/ref/ios-expertise-plan.json` 与 `ios-official-analysis.json` 中为本类选择的资源，按原始摘要完成审阅；官方资料、只读 MCP、CLI 和编译器分别记录来源、用途、读写范围及实际结果。无官方证据时记录降级原因，保持相关 unknown；不把第三方资料或自编规程称为 Apple 官方。设备远程控制不在默认调用范围，界面授权由用户自行完成。


### 官方分析的执行责任（0.13.1）

当 `ios-expertise-plan.json` 为当前主题选择 Apple 资源时，对应主题的分析过程由导出 skill 的适用规程承担：逐项执行其相关参考的审阅步骤，沿真实源码记录观察、未决项和影响；本技能保留迁移输出字段、归属和门禁合同。不得仅确认已读资料后继续用自编经验替代官方审阅。SwiftUI 使用 swiftui-specialist 的相关结构、状态、身份、环境或文本章节；App Intents 使用 app-intents-specialist 的执行模型、实体/参数、结果及快捷短语章节；文档型 SwiftUI 与 C bounds 仅在实际源输入适用时执行对应导出 skill。没有覆盖该主题的官方 skill 时明确保留自编/第三方分析，不伪称官方执行。

每条 Apple 源观察用 `expertise-review` 写入 `official_basis` 数组，字段为固定资源的 `path`、`sha256`、实际适用的 `section` 与具体 `application`。同时保留 `source`、`interpretation`、`unknowns`。只有资源确认、没有资源规则如何应用到源码的记录将被拒绝；此合同核验不替代对模型判断的独立复核。官方语义规程不能批准产品取舍或目标平台替代。

Swift 文件的词法/声明结构优先消费当前 facts 中固定的 SwiftParser/SwiftSyntax 产物，不能为了旧 Python 闭合语法可接受而改写源文件。编译上下文由实际 Xcode CLI 产物或经过校验的同源回放承担；MCP 不可用保留原错误和未决项。远程控制、界面读取及权限修改不在此分析范围。

## 0. 定位与纪律

- **前置**：上游已跑 `harness-init` + `source-index` + `facts`。先加载 `../ios-source-analysis/references/harness-v2.md`（机器产物/状态写者），外部证据按 `../ios-source-analysis/references/external-expertise.md` 执行，未连接工具保持 unknown/unavailable。
- **输入**：工程地图、页面事件、后台/扩展入口、服务调用、真实调用链与机器 feature 信号（`spec/ref/ios-feature-signals.json`）。**源不可读是阻塞**，不以旧报告补造行为。
- **输出**：`spec/ref/ios-feature-facts.md` + 每 feature 的源锚点 + 覆盖映射；随后由 a2h-spec 形成 `features/FNNN-*.md`、`ios-semantics.json` feature 部分与 `ios-coverage.json`（机器校验）。**本 skill 不直接手写 ios-semantics.json/ios-coverage.json（机器单写）**，只提供源行为事实与候选 AC。
- **唯一交互点**：无交互追问；歧义回源，不现场造分支。机械检查由 exit code 判定（0=PASS，非 0=FAIL）。
- **第一条可见输出必须是一行功能分析计划**（读信号 → 划分功能 → 读行为链 → 语言语义 → 数据/生命周期 → 形成 AC → 覆盖与交接）。
- **信号是待审线索**：先沿源码解释行为，再发行有具体期望的 AC；源测试仅作独立 oracle，不计为目标产品实现或测试通过。

### 无人值守处置阶梯（每道门禁 FAIL 一律套用）

> FAIL → 按命令 `retry_hint`/错误原文派修复并重跑同一命令，**最多 2 轮**；2 轮仍不过或确定模型修不了 → **记欠账放行**（账记全：修过几轮、每轮失败原因、判“修不了”的依据）；要拍板的模型自决并留痕；任何分支不得停机呈报人工。设备/账号类证据可欠账；静态门（facts/信号/语义）即便开了 `stage_debt` 也照修到 PASS。

## 1. 机器事实与信号读取

| # | 命令 | 产物 | exit code / 失败处置 |
|---|---|---|---|
| 1.1 | `python <runtime>/scripts/a2h_ios.py facts-view --project <target> --scope feature` | `spec/ref/ios-feature-signals.json`（state/write/branch/task/persistence/service/language/ownership/lifecycle 九类信号 + obligations） | exit 0 有效；非 0 → 回上游重跑 `facts` 后重试，最多 2 轮；**禁手改信号** |
| 1.2 | （可选）`python <runtime>/scripts/a2h_ios.py mcp-query --project <target> --server <server.json> --request <query.json>` | `spec/ref/mcp-runs/MCP-ID/*` | 失败写 failure.json；真实服务缺工具保留 unavailable/unknown，**禁止换假服务** |
| 1.3 | 交付前诊断 `python <runtime>/scripts/a2h_ios.py source-check --harness --report-only --project <target>` | 只读诊断 | 非 0 → 按 §7 阶梯 |

### 单写者分区（违者 PROCESS_VIOLATION）

| 文件 | 唯一写者 | 内容 |
|---|---|---|
| `spec/baseline/ios-facts.json` + `ios-obligations.json` | `facts` 命令 | 机器事实/义务 |
| `spec/ref/ios-feature-signals.json` | `facts-view --scope feature` 命令 | 本 skill 九类机器信号 |
| `spec/ref/ios-feature-facts.md` | 本 skill 作者（唯一 owner） | 功能行为事实可读分析 |
| `spec/baseline/ios-semantics.json` + `ios-coverage.json` 的 feature 部分 | a2h-spec `spec-authoring` | 语义/覆盖（机器校验） |
| `features/FNNN-*.md` | a2h-spec | 功能规格 |

- 图中的 token 片段不是已绑定的跨函数调用；接收者与泛型/宏/动态派发需额外证据（协议实现、注入点、selector）。
- 每条机器 obligation 绑定真实 AC 与 source_review；一个 AC 可覆盖多个事实，但场景必须具体。

## 2. 划分功能

按用户目标与系统行为分 feature，**不按 class/file 一对一建功能**。每个 feature 记录所有 UI、深链、通知、后台、扩展入口与目标范围。共享鉴权、缓存、数据库、配置归 feature-base；领域行为仍属对应 F ID。**声明、调用、可达执行链三者分开**，发现方法名不能当成已证实功能。

### feature 边界与入口穷举（不要漏）

| 入口类别 | 实例 | 归属 |
|---|---|---|
| UI 动作 | 按钮/手势/表单提交 handler | 对应 feature |
| 深链/URL scheme | `AppDelegate.open(url:)`/`onOpenURL`/Universal Link | 目标 feature |
| 通知 | 远程推送/本地通知/`UNUserNotificationCenter` delegate | 目标 feature |
| 后台/共享 | 后台 fetch、extension、Widget、App Clip、共享 target | 对应 feature 或 feature-base |
| 生命周期/启动 | `App` init、`scenePhase`、数据库迁移、登录态恢复 | feature-base |

## 3. 读出行为链

- 对每个入口读动作处理器及实际实现，追 protocol/conformance、delegate、closure、extension/category、默认实现、注入实例、动态 selector。**同名方法、protocol 继续追实现与注入点**。
- 记录触发条件、状态前值、输入校验、数据变换、调用顺序、副作用与可观察结果。当调用目标受运行时配置、宏或二进制影响时记录多个候选与不确定来源。
- 为源码存在的分支建状态转移表：正常/边界输入、错误、超时、取消、重复提交、并发回调、权限拒绝、无网络、会话过期、应用重启与恢复。**不能用统一模板发明分支**。
- 每个行为填 `input / precondition / processing / state transition / side effects / observable` 六段；每次写入发生的时点都要记录，不能只摘最终赋值。
- **异步取消三时点铁律**：点击后标记取消、请求停止、完成回调移除（或实际立即移除）分别记录；还要读出回调是否仍可能成功、旧回调是否仍写状态、重复取消如何处理。**不能把“cancel() 返回”当“操作完成”**。
- **清理完成边界铁律**：即时效果（UI 列表清空/内存释放）与完成事件（磁盘删除结束/失败/重启后重载）分开；公开 `clear()` 返回“已提交”还是“已完成”从实现确认。
- 业务常量、阈值、取整、单位、时区、排序、编码、精度保留原值及行号（与 `literal-ledger.json` 一致）。

### 行为链分析维度枚举（成功/错误/取消/重入/释放/持久化恢复，逐分支还原）

| 维度 | 要回答的问题 | 只展开源码存在的分支 |
|---|---|---|
| 成功 | 正常输入 → 状态与可观察结果 | 沿真实 handler 到 UI/服务回写 |
| 错误 | 校验失败/网络错/解析错/服务错 → 用户反馈 | 错误映射是否吞掉、返回码语义 |
| 取消 | 三时点：标记取消/请求停止/回调移除；取消后是否仍回调 | 旧回调是否覆盖新状态 |
| 重入/重复提交 | 同一动作再次触发、按钮连点、并发请求 | 幂等、去重、锁/串行队列 |
| 释放/生命周期 | 释放时机、weak/unowned、悬空回调、defer | 对象共享 vs 值复制 |
| 持久化恢复 | 写后重读、重启/杀进程重载、迁移失败 | 恢复失败分支、敏感数据边界 |

逐动作用下表留痕（分析工作记录，不是新增控制账本；每行能回证据）：

| 时点 | 触发/回调 | 内存与 UI 变化 | 服务/磁盘变化 | 对外可观察结果 | 源证据 |
|---|---|---|---|---|---|
| 例：点击 | 按钮 handler | 置 busy/禁用 | 发起请求 | — | 源文件:行 |

- 输入、状态、线程/actor、句柄所有权必须能回到证据；没有实际运行时，"可观察结果"描述源规则并标 `runtime=not_run`。
- 对同步返回、异步完成、错误/取消、再次触发分别填表；**只展开源码存在的分支**，无法确定的顺序写 unknown、原因与补证位置。

## 4. 保留语言语义与并发模型

### Swift

- 值/引用语义：Optional 与 nil、enum associated values、struct 值语义、class identity、copy-on-write。记录对行为的影响，再由目标接口选择表示；**不能把 enum 直接压成任意字符串**。
- 错误：`throws`/`Result`/`rethrows`、`defer`、`do-catch` 映射关系——错误是否上抛、映射、吞掉，逐处还原。
- 闭包：`escaping`/`non-escaping`、`@Sendable`、捕获列表、`weak/unowned`、悬空回调。
- 并发：`actor`/`MainActor`、`Sendable`、structured/unstructured `Task`、`Task` cancellation、`AsyncSequence`/`AsyncStream`。记录隔离域、线程切换、取消传播。
- 属性包装器状态流：见 §5 状态发布流表。

### Objective-C（含桥接）

- nullability（`nullable/nonnull/__nullable/__nonnull`）、nil messaging、`selector`、`category`/`extension`、protocol `@optional`。
- block 捕获与 `__weak/__strong`、ARC/retain cycle、weak delegate、KVC/KVO 注册与移除、`NSError` 双指针返回、`dispatch_queue`/`dispatch_async` 线程语义。
- Swift↔ObjC 桥接：`NS_SWIFT_NAME`、`@objc`、桥接类型差异对行为的影响。

### Objective-C++/C++

- ABI、指针/句柄、资源所有权、回调线程；**不能承诺直接语法转写**。

### 事件/通知机制分类（区分发布与订阅的真实绑定）

| 机制 | 发布→订阅方向 | 记录要点 |
|---|---|---|
| delegate | 一对一弱引用回调 | 是否 weak、回调线程、set 时机 |
| NotificationCenter | 广播 | 注册/移除成对、observer 释放、线程 |
| KVO | 属性变化 | 注册键路径、移除、崩溃风险 |
| Combine | `@Published`→`sink`/订阅 | 订阅生命周期、线程、背压、首值 |
| target-action/block | 控件→闭包 | 捕获、循环引用、回调次数 |
| @MainActor/@Sendable 回调 | 跨隔离域 | 隔离切换、数据竞争、可观察时序 |

## 5. 数据与生命周期

- 追 URLSession/Combine/async await 等执行上下文：**取消后是否仍回调、旧请求是否覆盖新状态、重试是否幂等、缓存是否先发、错误映射是否吞掉**，均用真实实现作证。
- 持久化：见下表。**不要只给存储 API 名**；状态区分值复制与对象共享，不能把普通 var 直接翻成全局 store。
- 网络记录服务参数、鉴权、编码、响应和错误到用户反馈。

### 状态发布流分类（SwiftUI/Combine：状态、绑定、发布流）

| 载体 | 方向/持有 | 行为还原要点 |
|---|---|---|
| `@State`/`@Binding` | 视图内私有/双向投影 | 值复制、写回链、身份重置 |
| `@StateObject`/`@ObservedObject` | 持有/订阅对象 | 所有权、对象共享、订阅触发 `body` |
| `@EnvironmentObject`/`@Environment` | 环境注入/环境值 | 注入源、缺注入行为 |
| `@Observable` + `@Bindable`（iOS 17+） | Observation 追踪 | 属性级细粒度重算 |
| `@Published`/`CurrentValueSubject`/`PassthroughSubject` | Combine 发布 | 订阅时序、首值、线程 |
| `AsyncSequence`/`AsyncStream` | 异步流 | 取消、缓冲、并发迭代 |

### 执行上下文分类（URLSession/Combine/async await 的取消、竞争与幂等）

| 上下文 | 还原要点 |
|---|---|
| `URLSession dataTask/uploadTask` | 取消后是否仍回调、旧响应覆盖新状态、重试幂等 |
| Combine pipeline（sink/assign） | 订阅取消、背压、`receive(on:)` 线程、首值/错误 |
| `async/await` + `Task`/`TaskGroup` | structured/unstructured、取消传播、并发迭代、`Task.sleep` |
| `DispatchQueue`/`OperationQueue` | 串行/并发、`qos`、死锁、`@Sendable` 捕获 |
| delegate + callback（block） | 回调线程、weak 捕获、重复回调、旧回调扣写 |

### 持久化介质表（记录 key/schema/事务/迁移/恢复失败，不只要 API 名）

| 介质 | 还原要点 |
|---|---|
| Core Data | model schema、context 并发（viewContext/background）、持久化协调器、迁移、fetch/fault |
| SwiftData | `@Model` schema、`ModelContainer/ModelContext`、迁移与版本 |
| SQLite/GRDB/FMDB | SQL、事务、索引、迁移脚本、写冲突 |
| 文件/沙盒 | 目录（Documents/Library/Caches/tmp）、原子写、序列化格式 |
| UserDefaults | key、默认值、类型、`synchronize` 语义、跨进程 |
| Keychain | 服务/账号 key、访问组、删除/恢复、敏感数据边界 |

## 6. 形成 AC 输入

- 每个可断言行为给稳定 F ID 的候选 AC、源符号、可观察结果与独立真值。`判:unit/contract/route/ui/visual/device/static` 根据行为选择；**静态函数存在不能证明副作用**。
- 期望值来自 iOS 源码、源测试、真实 trace/device 或已批准 decision，**不来自生成的 .ets**。
- 纯逻辑、平台能力、视觉行为分别选择验证方法，不强制所有行为都是单元测试。独立真值：unit 用源规则与边界样本、contract 用真实协议样本、ui/device 用真实动作与观察。

### 验证方法选择表（按行为性质选，不强制全是单测）

| 判 | 适用行为 | 独立真值来源 |
|---|---|---|
| unit | 纯逻辑/算法/校验/格式 | 源规则 + 边界样本 |
| contract | 协议/接口/编码 | 真实协议样本 |
| route/ui | 导航/页面到达 | 真实动作 + 观察 |
| visual | 视觉/布局/深色/动态字体 | 真实截图证据（有条件一致） |
| device | 系统能力/权限/传感器 | 真实设备动作 |
| static | 符号/类型存在性 | 源码锚点（不证明副作用） |

- 目标平台差异先列原行为、不可等价原因、候选替代、用户影响，交 decision-ledger。**未经批准的替代不能写成 source fact**。复杂功能把状态机/协议细节放 addendum，稳定 AC 留主 feature spec 并给 `impl:` 指针。

### 常见陷阱（iOS 功能领域，避免微失真）

- **名称撞车＝同一功能**：同名方法/protocol 必须追到实现与注入点；默认实现、category、动态 selector 都会改变实际调用目标。
- **取消≠完成**：`cancel()` 返回不是操作完成；取消三时点（标记/请求停止/回调移除）分别记录，不合并。
- **枚举压字符串**：Swift enum（含 associated values）不能直接压成任意字符串，先把语义保留再由目标接口选表示。
- **装饰器拼写≠语义**：`@State`/`@StateObject`/`@ObservedObject` 所有权不同，只按拼写判等价会写错写回链。
- **普通 var ≠ 全局 store**：值复制与对象共享要区分，不能把视图内普通 var 直接翻成全局状态。
- **回调悬空**：`weak/unowned`、闭包捕获、释放时机要还原；不能默认“所有回调都会安全返回”。
- **静态存在≠副作用**：`static`/符号存在只能证明存在，不能证明运行副作用；独立真值按实际行为选 unit/contract/ui/device。

## 7. 硬约束

- **禁止**手改 `facts-view`/`facts` 产出的机器信号、`ios-facts.json`、`ios-obligations.json`（PROCESS_VIOLATION）。
- **禁止**用统一模板发明分支；状态转移、错误/取消、持久化恢复只展开源码存在的分支。
- **禁止**把生成的目标实现结果反推为期望；expected 不来自 .ets。
- **不得**以 AC 数量、文件数量或扫描数量宣称完备；逐项列未解释调用、不可读二进制、缺配置、未运行场景。
- **不得**用“已处理/N/A”清空 unknown 维度；unknown 必须带原因与补证步骤。
- **不越权**：UI 结构归 ios-ui-analyzer；协议/SDK 清单归 ios-api-inventory；本 skill 只解释完整可观察行为与验收依据。

## 8. 读取时机（references）

| 触发时机 | 必读文件 |
|---|---|
| 执行前；机器产物/状态写者存疑 | `../ios-source-analysis/references/harness-v2.md` |
| 源事实字段、语言/框架语义 | `../ios-source-analysis/references/native-facts.md` + `source-semantics.md` |
| 外部资料/MCP 证据 | `../ios-source-analysis/references/external-expertise.md` |
| 逐动作执行与取消/清理正反例 | `references/analysis-v2.md` |
| 共享/异步/取消动作合同 | `../a2h-spec/references/action-contracts.md` |
| 转 baseline 与 AC 交付 | `../a2h-spec/references/spec-delivery-contract.md` + `../a2h-spec/templates/feature-spec-template.md` |

## 9. 交接

- 前置门闸：每 feature 的 `state_transitions/concurrency/lifetime/persistence/platform_capabilities` 及语言维度经 `source-check --harness`（a2h-spec 执行）无新增 finding。
- 移交：数据流、源行为表（含状态转移表）、错误/取消模型、目标接缝约束、候选 AC 与独立真值、unknown 清单、待决策项、source-notes（保留语言语义，避免 worker 再从零猜业务）。
- 下一步提示：交 `a2h-spec`（Phase C 生成 `features/FNNN-*.md` 与决策账本）；平台差异交 decision-ledger；对应页面事件与 UI 分析去重引用同一动作 ID。