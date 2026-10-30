# 源分析自动编排协议

入口 `source-analysis --project <target>` 在未规划的新工程或当前源索引上工作；`--plan-only` 只读返回决策，不写基线。旧索引或已有计划必须走受审刷新/重排。

## 自动选择与执行

1. 检查工程、宿主、语言、框架和当前证据；真实歧义列出字段与候选。
2. 优先导出并读取适用的 Apple 官方技能；连接 Xcode MCP 后只调用允许的源读取/文档查询。发现、查询和审阅分别记录。未授权不自动打开工程、修改全局权限或操作设备。
3. 当前完整编译证据匹配所选范围时回放；Mac/Xcode 工程缺证据时实际采集一次构建，供成员、配置和 Clang AST 共用。存在 C-family 条件但没有匹配条件证据时，auto 在原生宿主自动补采；replay 保持缺失。
4. 有 Swift 和兼容工具链时构建 Swift 官方库的 SwiftSyntax 适配器；SwiftPM 实际执行 dump-package；按输入选择 IB、资产和本地化分析。失败保留原始命令、stdout/stderr，不把可用标签写成执行成功。
5. 真实输出交给原 facts/literals、expertise-plan 和规格候选消费。业务语义、AC 和产品决策继续由原作者审阅；不会自动批准。
6. 已明确选择源端 UI 策略时，source-ui 步骤在规格候选前实际调用 XCUITest 或校验复用当前证据，随后由 spec-authoring 的对应页面消费原图/原生树；首次选择及协议见 [源端 UI 采集](source-ui-capture.md)。缺范围只限制相应采集，模拟器观察独立于源编译 SDK。

显式 providers 或 variant 保留调用者确定的范围。底层 facts 入口仍可独立使用；普通工作流以 source-analysis 为入口。

## 配置

默认读 `<target>/spec/ref/ios-analysis-config.json`，或 `--analysis-config <path>`。schema_version=1；mode 可取 auto/native/replay/static。

- auto 自动选择；native 要求本机真实采集；replay 要求当前完整证据；static 显式限定文件分析，不能替代原生验证。
- selection 支持 project、workspace、scheme、target、configuration、sdk、arch、destination。project/workspace 二选一；唯一 scheme 或目标同名 scheme 自动选择。缺省 Debug、iphoneos、arm64、generic destination 会记入收据，证据仅对应该配置。
- evidence 支持 build/compilation/conditional/manifest，路径必须在 target/spec/ref 下；明确指定的坏证据直接拒绝，不能悄悄换路径。多个有效构建范围需要输入，不能任选。
- official_skills 默认 true；require_official 默认 false，设 true 时未取得当前官方资料将阻断；timeout_seconds 为 1..3600，默认 600。
- mcp_server 可指向 stdio 配置，env 只接受 MCP_XCODE_PID、MCP_XCODE_SESSION_ID；第三方服务保留第三方身份。
- mcp 可为 ask/enable/skip，`source-analysis --mcp` 可传入当前会话的明确选择；已保存项目选择自动沿用，默认 ask 不覆盖它。pending 在 JSON 和可读 stderr 中明确展示，由主控收取选择后才连接 MCP；CLI 的独立工作可继续。选择状态不等于服务、工程授权或实际调用成功。

## 进度与恢复

- stderr 输出当前阶段、total/completed/failed/blocked；completed 表示步骤处理完成，unavailable 与原始错误在 stages/degraded 列出，不表示该能力通过。
- `spec/ref/analysis-runs/AR-*/plan.json` 记录选择理由；progress.json 和 `spec/reports/derived/source-analysis.json` 保存执行收据。
- ios-official-analysis.json、ios-analysis-provenance.json、ios-expertise-plan.json 保存资源、来源、实际结果及审阅要求。官方资源摘要改变必须重读、重审。
- ios-source-analysis-inputs.json 将本轮有效输入纳入计划冻结；派发后修改会阻断原计划消费。
- 命令失败时先看收据和原始日志；修复宿主/授权/配置后重跑。源变化用 source-refresh，不能删除旧证据规避。

## 官方能力与权限

| 能力 | 来源与用途 | 读写范围 |
|---|---|---|
| agent skills export | Apple Xcode，读取适用 SwiftUI、App Intents 等官方指引 | 导出到目标 spec/ref；不修改业务源码 |
| DocumentationSearch、XcodeRead/Grep/Glob | Apple Xcode MCP，文档/源证据 | 只读白名单，记录请求和原始响应 |
| xcodebuild | Apple Xcode，发现 scheme、配置和实际编译成员 | 读源；写目标分析目录的 DerivedData 和日志；禁签名 |
| SwiftSyntax/SwiftParser | Swift 官方库，准确语法及源跨度 | 读 Swift 文件；编译本包适配器并写目标证据 |
| SwiftPM dump-package | Swift 官方 CLI，解析实际 Package.swift | 执行受控 manifest 评估，保存版本与结果；不执行 App |
| Clang AST / preprocessor | Xcode 提供的 Apple Clang（LLVM），核对 C/ObjC 语法和配置分支 | 读实际编译上下文；写证据；不操作设备 |

本包分析规程与适配器属自编；AvdLee、Axiom 为第三方备用。官方技能资料读取不证明业务行为。设备远程控制不在默认范围；CLI/MCP 缺授权时记录错误，由用户自行完成必要授权步骤。
