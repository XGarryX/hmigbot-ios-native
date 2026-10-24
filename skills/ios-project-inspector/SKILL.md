---
name: ios-project-inspector
description: "iOS→HarmonyOS 迁移源分析第 1 类（工程边界层）：读取原生 iOS 工程结构——.xcodeproj/project.pbxproj、.xcworkspace、shared schemes、.xcconfig、Package.swift/Package.resolved、Podfile/lock——区分 target/scheme/configuration、语言与混合边界、依赖与生命周期入口（App/Scene/extension），产出带证据分级的工程地图 ios-project.md。当用户说“分析这个 iOS 工程结构”“梳理 Xcode 工程 targets/schemes/依赖”“iOS 工程边界”或 a2h-spec 组织四类分析时使用。不要用于：UI 结构分析（用 ios-ui-analyzer）、功能行为链（用 ios-feature-analyzer）、外部服务与权限（用 ios-api-inventory）、目标工程架构设计（用 arkts-* 技能）。"
metadata:
  type: domain
  domain: migration
  tags:
  - ios
  - analysis
  - project
  - evidence
---

> **调用关系**：本 skill 是 `ios-source-analysis` 组织的四类分析之一（工程类），负责「编译单元、语言、依赖、目标入口与条件」维度。本 skill **不派发 subagent**，全部步骤在主会话或由派发方作为子代理调起；若作子代理调起，任务书自足（写清 scope=project、输出契约、源根），完成后由派发方按 Join 协议收口——**完成的唯一合法信号是 `agent_status=completed`，绝不是产物文件存在**；本 skill 自身不嵌套外派。
>
> 路径约定：`$IOS_SRC` 从 `<target>/.migbot/config.json` 的 `ios` 字段读取；`<target>` = 鸿蒙目标工程根；`<runtime>` = 本包 runtime（可用 `<skill>/scripts/run.py --runtime-root` 解析）。本 skill 独占写 `spec/ref/ios-project.md`；机器信号 `ios-project-signals.json` 由 facts-view 单写，禁手改。本 skill 不改签名、账号或源仓配置，也不创建 Xcode 工程。

# ios-project-inspector — iOS 工程结构与构建边界

适用的 Apple 官方技能与 Xcode MCP 优先。先读取 `spec/ref/ios-expertise-plan.json` 与 `ios-official-analysis.json` 中为本类选择的资源，按原始摘要完成审阅；官方资料、只读 MCP、CLI 和编译器分别记录来源、用途、读写范围及实际结果。无官方证据时记录降级原因，保持相关 unknown；不把第三方资料或自编规程称为 Apple 官方。设备远程控制不在默认调用范围，界面授权由用户自行完成。

## 0. 定位与纪律

### 设计理念与边界

本 skill 只做**工程事实分层索引**：把 `.xcodeproj`/`.xcworkspace`/`Package.swift`/`Podfile` 里的「target / scheme / configuration / 语言模式 / 依赖 / 入口 / 条件编译」抽成一张带证据分级的工程地图，**不解析业务行为，也不做目标架构设计**。它是“事实索引层”，不是“生成器”——语义理解（每个入口/模块做什么）由下游 UI/功能/API 分析补。

- **前置**：`<target>/.migbot/config.json` 存在且 `source_platform=ios`；`spec/baseline/ios-source-index.json` 已由上游建立（缺 → 提示先由 a2h-spec 跑 `source-index`，不代跑）。源不可读是阻塞，不以文件夹名或旧报告补造结构。
- **输入**：iOS 源码根、迁移范围、已读 `.migbot/config.json`。本 skill 不修改签名、账号或源仓配置。
- **输出**：`spec/ref/ios-project.md`（本 skill 独占）；机器事实视图 `spec/ref/ios-project-signals.json`（facts-view 单写）。模块/成员清单交 a2h-spec Phase 0 消费。
- **唯一交互点**：无。机械检查由 exit code 判定（0=PASS，非 0=FAIL）；不经猜测填满表格。
- **第一条可见输出必须是一行阶段计划**（机器事实 → 工程地图 → 运行边界 → 依赖语义 → 清单求值 → 证据提升 → 输出检查），然后才执行 §1。

### 无人值守处置阶梯（每道门禁 FAIL 一律套用）

> FAIL → 按命令 `retry_hint`/错误原文派修复并重跑同一命令，**最多 2 轮**；2 轮仍不过或确定模型修不了 → **记欠账放行**（账记全：修过几轮、每轮失败原因、判“修不了”的依据）；要拍板的模型自决并留痕；任何分支不得停机呈报人工。缺 Apple 构建设备属证据层级未验证（可欠账）；工程地图的源解析错误是合同阻断（静态门照修到 PASS）。

## 1. 机器事实与信号（先读，不手改）

| # | 命令 | 产物 | exit / 处置 |
|---|---|---|---|
| 1.1 | `python <runtime>/scripts/a2h_ios.py source-index --project <target>`（首轮，或源 sha 变化后再索引） | `spec/baseline/ios-source-index.json` | 非 0 = 源在索引期变化或索引已存在，按提示处置，禁删旧索引硬建 |
| 1.2 | `python <runtime>/scripts/a2h_ios.py facts --project <target>` | `spec/baseline/ios-facts.json`（身份/词法/结构事实） | 非 0 读错误重跑，最多 2 轮；数据不完整不阻塞视图，缺处标 unknown |
| 1.3 | `python <runtime>/scripts/a2h_ios.py facts-view --project <target> --scope project` | `spec/ref/ios-project-signals.json` | 非 0 = 工程信号未抽全，补 facts 后重跑 |

- **索引只是范围与线索**：对每个业务结论继续读实际函数、调用点、配置与资源。`facts-view --scope project` 读到的 `ios-project-signals.json` 是机器信号，禁止手写或篡改。
- 机器信号提供「target 列表 / build phases / 依赖方向 / 条件编译 / 宏 / 入口」等确定性线索；模型据此建地图，但**线索不等于绑定**——未解析的动态规则与未知对象类型记 `unresolved`，不据此声称有效构建。

### 单写者分区（违者 PROCESS_VIOLATION）

| 文件 | 唯一写者 | 内容 |
|---|---|---|
| `spec/baseline/ios-source-index.json` | source-index 命令 | 文件快照/索引 |
| `spec/baseline/ios-facts.json` | facts 命令 | 身份/词法/结构事实 |
| `spec/ref/ios-project-signals.json` | facts-view 命令 | 工程机器信号 |
| `spec/ref/ios-project.md` | 本 skill（模型作者） | 工程地图 |

主会话与作者手改上表“机器单写”文件即契约违规。

## 2. 建立工程地图

- 枚举 `.xcworkspace/contents.xcworkspacedata`、`.xcodeproj/project.pbxproj`、shared schemes、`.xcconfig`、`Package.swift`、`Package.resolved`、`Podfile`/`Podfile.lock`。
- 区分 workspace 引用的多个 project、project 内 targets、SwiftPM targets 与代码目录。**`PBXFileReference` 只表示引用**：结合 build phases、target dependencies、synchronized groups 的例外才能推断构建成员。动态规则与未知对象类型记 `unresolved`。
- 每个 target 记录 product type、入口、deployment target、device family、conditional compilation、bundle 配置、资源成员与依赖方向。

### 2.1 pbxproj 对象类型与语义（索引分层依据）

`project.pbxproj` 是 Xcode 工程的自有对象图，每个对象靠 `isa` 区分角色。**同一 `FileReference` 是否属于某 target 的编译成员，只能由 BuildFile 链接 + BuildPhase 归属证明**：

| 对象 `isa` | 角色 | 对“有效成员”的贡献 |
|---|---|---|
| `PBXProject` | 工程根（targets 列表、buildConfigurationList） | target 全集与默认配置 |
| `PBXNativeTarget` / `PBXAggregateTarget` | 原生/聚合 target | product type、build phases、dependencies |
| `PBXFileReference` | 文件引用 | **仅引用，不证明编译成员** |
| `PBXBuildFile` | build phase ↔ 文件的链接 | 连接文件到 Sources/Frameworks/Resources 阶段 |
| `PBXGroup` / `PBXVariantGroup` / `XCVersionGroup` | 目录组 / 本地化变体 / 版本模型组 | 组织视图，非成员关系 |
| `PBXSourcesBuildPhase` / `PBXFrameworksBuildPhase` / `PBXResourcesBuildPhase` | 编译/链接/资源阶段 | **成员真值来源**（含 `PBXBuildFile` 列表） |
| `PBXShellScriptBuildPhase` | 脚本阶段 | 生成代码/资源，须记录不执行 |
| `PBXTargetDependency` / `PBXContainerItemProxy` | target 依赖 / 跨工程引用代理 | 依赖方向与嵌入扩展 |
| `XCBuildConfiguration` / `XCConfigurationList` | 构建配置 | build settings、宏/条件、SDK/架构 |
| `PBXFileSystemSynchronizedRootGroup` | 同步组（Xcode 15+） | 目录级自动成员，需按例外规则补 |

### 2.2 target 记录字段清单（索引完整性规则）

每个 target 至少记录下列字段；**逐字段标证据分级（observed / static-inferred / unresolved）**，缺处不得留白猜：

| 字段 | 说明 | 无证据时 |
|---|---|---|
| target ID / name / product type | 稳定标识 | `unresolved`（product type 读得到才算 observed） |
| entry point | App/Scene/delegate/main/extension 入口（文件:行） | 见 §3，标 unresolved |
| deployment target / device family | 最低系统版本 / iPhone/iPad/通用 | 读不到标 unknown |
| languages | Swift/ObjC/ObjC++/C/C++ 及混合边界 | 见 §2.4 判定 |
| conditional compilation / 宏 | `#if`/`SWIFT_ACTIVE_COMPILATION_CONDITIONS`/`GCC_PREPROCESSOR_DEFINITIONS` | 未解析的宏标 unresolved |
| bundle 配置 | bundle id、Info.plist 路径、签名/entitlements | 交叉配置文件确认 |
| sources/resources frameworks | build phases 成员 | `PBXFileReference` 不等于成员 |
| dependencies | 依赖方向（target dep / 嵌入扩展 / 本地包） | 逐条给 `PBXTargetDependency`/package 引用 |

硬约束（红线）：**文件索引不代表有效编译成员**；没有 Xcode 时保留 `static-inferred`，**绝不改标 compiler binding**。词法证据 ≠ 编译器绑定。

### 2.3 product type 枚举

| product type | 含义 |
|---|---|
| `com.apple.product-type.application` | App 主体 |
| `com.apple.product-type.app-extension` | 普通扩展（Today/Share/Action 等） |
| `com.apple.product-type.app-clip` | App Clip |
| `com.apple.product-type.widgetkit-extension` | Widget 扩展 |
| `com.apple.product-type.framework` | 动态 framework |
| `com.apple.product-type.static-library` | 静态库 |
| `com.apple.product-type.bundle.unit-test` / `bundle.ui-testing` | 单元/UI 测试 |
| `com.apple.product-type.extensionkit-extension` | App Intents / ExtensionKit 扩展 |

### 2.4 语言判定

- **语言判定**：`.swift` 为 Swift；`.m` 为 Objective-C；`.mm` 为 Objective-C++；`.h` 按导入与符号解析判定。**C/C++ 引擎与 JS/Web 内容单独记录，不能转成 Swift 的假事实**。
- **`.h` 头文件按导入与符号归属解析**：`#import <模块/头>` 与 `module.modulemap` 决定它属于 ObjC 还是桥接到 Swift；单凭扩展名不能定论。
- 语言模式影响下游语义：Swift 的值复制/actor/并发、ObjC 的 nil messaging/ARC/KVO、ObjC++ 的混编边界、C/C++ 引擎的指针/句柄生命周期，都按调用链保留（读法见 `../ios-source-analysis/references/source-semantics.md`）。

### 2.5 边界案例与推断封装

| 边界案例 | 正确处置 | 禁止的错误封装 |
|---|---|---|
| `PBXFileReference` 未挂到任何 `PBXBuildFile`/BuildPhase | 不属于编译成员，记 `static-inferred`/引用 | 不能凭出现在工程里就标“成员存在” |
| 头文件隐式包含 | 保守保留全仓扫描，不删成员 | 不能按目录名排除 |
| 多 project workspace | 按 workspace 引用逐个 project 闭合，再合并 | 不能把 A 工程的 target 挂到 B 工程 |
| 同步组（`PBXFileSystemSynchronizedRootGroup`） | 按例外规则补目录成员 | 不能假设目录树＝编译成员全集 |
| 产品源中的活动 `#if` / 宏未解析 | 记 `unresolved`，**继续阻断** | 不能按一个分支的展开当全集 |
| 测试与产品共享文件 | 保留共享文件，测试独占文件列 `test_only_oracle` | 不能按 Tests 目录直接排除 |
| 跨工程 / 本地包依赖 | 依赖方向逐条给 `PBXTargetDependency`/package 引用 | 不能靠 target 名猜依赖 |
| 未知 `isa` 对象、动态规则 | 记 `unresolved` + 原对象片段 | 不能把“解析失败”改写为“没有模块/没有权限” |

## 3. 沿入口理解运行边界

- SwiftUI `App`/`Scene`、`UIApplicationDelegate`/`UISceneDelegate`、`main.m`/自定义 main，分别追到实际根界面及服务初始化。记录多 Scene、URL/Universal Link、通知、后台唤醒与 extension 入口；**某入口无 UI 不代表其功能不存在**。
- App Clip、Widget、Share、Notification Service、Intents 等扩展按独立 target 建图。记录 App Group、共享容器、Keychain group、主应用通信协议与权限边界。
- 将平台专有入口交 `ios-api-inventory`；**不能承诺所有扩展一对一映射**到目标。

### 3.1 入口形态枚举

| 入口形态 | 载体 | 追到 |
|---|---|---|
| SwiftUI App | `@main struct Xxx: App` + `Scene`/`WindowGroup` | 根 `body` 的初始视图 + 服务初始化 |
| UIKit App | `@UIApplicationMain`/`@main class Xxx: AppDelegate` 或 `main.swift`/`main.m` 的 `UIApplicationMain` | `didFinishLaunching` 的 window/rootVC + 服务 |
| Scene 生命周期 | `Info.plist` 的 `UIApplicationSceneManifest` + `UISceneDelegate` | 多场景、`UISceneConfiguration` |
| 扩展 | `NSExtension`（`NSExtensionPrincipalClass`） | 扩展入口类与宿主通信 |
| 后台唤醒 | `BGTaskScheduler` / `URLSession` background / 推送 | 后台任务与处理链 |

## 4. 解析依赖与混合语义

- 区分源码包、预编译 `.xcframework`/`.framework`、动态加载、插件与资源 bundle。记录版本锁定、调用点、公开协议、许可证位置及源码是否可见。
- Swift/ObjC bridging header、generated Swift header、module map、`NS_SWIFT_NAME`、泛型擦除与 nullability 边界都影响下游类型理解。**不能根据包名猜其运行行为**。
- SwiftSyntax provider 可给语法节点与位置；**编译条件、宏展开、overload resolution 未解析时不能标 resolved**。SourceKit-LSP 或 Xcode 数据必须注明工具版本与目标配置。

### 4.1 依赖锁定文件与混合边界

| 载体 | 记录内容 |
|---|---|
| `Podfile` / `Podfile.lock` | pod 名/精确版本/checksum/`vendored` 标记/子依赖树 |
| `Package.swift` / `Package.resolved` | package identity/版本/commit/产品 targets |
| `Cartfile` / `Cartfile.resolved` | 框架名/版本 |
| Bridging Header（`SWIFT_OBJC_BRIDGING_HEADER`） | Swift↔ObjC 桥接面 |
| generated Swift header（`-Swift.h`） | ObjC 可见的 Swift 符号 |
| `module.modulemap` / `umbrella.h` | 模块映射与导出头 |

- 混合语义边界单独登记：显式桥接头、`NS_SWIFT_NAME` 重命名、nullability 注解、泛型擦除，都影响下游类型理解与目标 mapping。

## 5. 清单求值与产品成员证据

`Package.swift` 未求值，或需区分 Xcode 产品源与测试编译源时，按 `../ios-source-analysis/references/source-input-evidence.md` 采集（输入 schema 以随包 runtime 的 `schemas/source-manifest-evidence.schema.json` 为权威）：

| # | 命令 | 产物 | exit / 处置 |
|---|---|---|---|
| 5.1 | `python <runtime>/scripts/a2h_ios.py manifest-evaluate --project <target> --config <target>/spec/ref/manifest-evaluate.config.json --output <target>/spec/ref/ios-manifest-evidence/<capture-id>` | 清单求值证据 | exit 2 = `capture_failed`（版本失败/超时/非零退出/非法 JSON/源变化），保留日志修正后重采 |
| 5.2 | `python <runtime>/scripts/a2h_ios.py facts --project <target> --manifest-evidence <目录或manifest.json>` | 解除精确路径 `Package.swift` 未求值 | 非 0 重跑；证据过期/篡改拒绝 |
| 5.3 | `python <runtime>/scripts/a2h_ios.py facts --project <target> --variant <target>/spec/ref/project-targets.json>`（有可解析 pbxproj 时） | 产品成员（`source_files`/`source_membership`/`target_closure` 等） | 解析器从工程推导，调用者不能自写文件白名单或改派生字段 |

- 清单求值只标 `manifest_evaluated`（范围 `current_host_manifest_evaluation`）；工程成员只标 `evidence=project_declared_membership`、`effective_build=unresolved`。**两者都不证明依赖已解析、已编译或已迁移完成**，不把声明标成已构建。
- 测试独占文件由工程成员确定并列为 `test_only_oracle`，不作为产品编译源扫描；与产品共享的文件保留。**不按 Tests 目录名直接排除**。

## 6. 环境可用时提升证据

- 先确认用户授权范围与实际 Xcode。用只读项目查询核对 targets/schemes/build settings；需要构建时执行已授权配置并保存完整日志、命令、SDK、工具版本与退出码。
- **无 Mac 时保留静态工程地图，构建成员标 `static-inferred`，不阻断独立源阅读**。云端构建仅证明选定 scheme/configuration 的构建，不证明全部功能与设备行为。
- 宿主能力三态（available/configured/executed）与 provenance 记录遵循 `../ios-source-analysis/references/apple-capabilities.md`；未连通 Apple skill/MCP 记 `unavailable`/`not_loaded`，不伪造官方执行。

## 7. 输出与检查

- `ios-project.md` 逐行含 target ID、类型、入口文件:行、语言、UI 框架、构建配置证据、依赖与未知项。**代码量是分工参考，不能当覆盖率**。
- **每条推断标 `observed`/`static-inferred`/`unresolved`，并说明如何消除不确定性**。将运行入口交 UI/功能分析；将依赖与系统能力交 API inventory；重复事实引用同一 ID。

### 7.1 证据分级（索引完整性规则）

| 分级 | 含义 | 消除不确定性方式 |
|---|---|---|
| `observed` | 源配置/锁定文件直接读到的声明或机器信号 | —（已有源锚点） |
| `static-inferred` | 静态解析推断的构建成员（无 Xcode 有效构建） | 取得真实 Xcode 构建证据后升级 |
| `unresolved` | 动态规则/宏/未知对象类型未解析 | 标注所需额外证据（真实构建/符号服务） |

- 失败恢复：路径失效重新定位；解析器不支持则保留原文件与对象片段，**不要把解析失败改写成“没有模块/没有权限”**，不经猜测填满表格。
- 源码变化时：先按 harness-v2 的 `source-refresh --review` 协议更新索引，再重读变化路径并重跑门禁；旧图归档，旧 PASS 不继承。

## 8. 读取时机（references）

| 触发时机 | 必读文件 |
|---|---|
| 执行前确定机器产物/状态写者 | ../ios-source-analysis/references/harness-v2.md |
| 身份/字段/溯源与 evidence 分级规则 | ../ios-source-analysis/references/native-facts.md |
| Package.swift 未求值 / 区分产品与测试成员 | ../ios-source-analysis/references/source-input-evidence.md |
| Apple skill/MCP/宿主能力三态与 provenance | ../ios-source-analysis/references/apple-capabilities.md |
| expertise-plan/review、MCP 边界 | ../ios-source-analysis/references/external-expertise.md |
| 工程事实提取、复核、恢复模板 | references/analysis-v2.md |

## 9. 交接

- 门前闸：`python <runtime>/scripts/a2h_ios.py source-check --harness --project <target>` exit 0 才交接；含 external-expertise 门禁与溯源检查。FAIL 按 §0 阶梯最多修 2 轮。
- 移交产物：`spec/ref/ios-project.md` + `spec/ref/ios-project-signals.json` + provenance 片段。项目未知项逐条交给具体 provider/源码/产品决定；源解析错误是合同阻断，缺 Apple 构建设备只是证据层级未验证。随后交 `ios-source-analysis` / `a2h-spec` Phase 0（同会话可直接续跑）。
- 本 skill 无独立 stage 水位（无 mark-stage）；`source-check --harness` 绿即工程维度的最终收口。