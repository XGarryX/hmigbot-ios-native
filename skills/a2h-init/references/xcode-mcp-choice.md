# 可选 Xcode MCP：选择、真实状态与恢复

初始化先说明以下选择，沿用开发者已经表达的授权，不重复询问已授权步骤。

| 选择 | 能力与代价 | 执行方式 |
|---|---|---|
| 使用只读 MCP + Apple CLI | 可以增加 Xcode 提供且实际发现的工程上下文、构建设置、编译参数等只读工具；部分服务也提供官方文档查询。仍用 CLI 获取编译证据。需要 MCP 服务可见、目标工程及可能单独的 agent／工程目录授权。 | 已有选择直接沿用；`init-environment --mcp enable --prepare` 记录此选择并只读检查，不自动修改系统授权设置。 |
| 继续 CLI | 不新增 MCP 授权；继续使用 `xcodebuild`、`xcrun`、Swift 编译器／Swift 官方语法库及 Apple 提供的 Clang。部分交互工程上下文、官方查询工具可能不可用。 | `init-environment --mcp skip --prepare`；缺少 MCP 不能作为全局初始化或转换失败条件。 |

未选择时 `--mcp ask` 返回 `capability_choices`，stderr 同时显示中文选择卡。主控必须将两项差异展示给开发者并收取选择，不能将 JSON 中存在 options、初始化 ready 或 exit 0 当成“用户已经选过”。宿主有提问接口时使用该接口；没有时在对话中列出两项。等待只影响 MCP 调用，独立 CLI 工作可继续；沉默不是同意启用，也不是已选择 CLI。命令应由当前 `<runtime>/scripts/a2h_ios.py` 执行，附上当前 `--project <target>`；本参考不设置具体开发者或样例项目路径。

已选择 MCP 但当前进程看不到服务时，先只读比较宿主状态；不能据此直接认定宿主关闭。确认为关闭后，由开发者手动在 Xcode 设置中开启，或在宿主终端执行官方命令。管理员验证不能由工具代填：

```sh
sudo xcrun mcp-server enable
xcrun mcp-server status --format json
```

也可以由开发者自行在 `Xcode > Settings > Intelligence > Model Context Protocol` 开启外部 agent 访问；工具不自动打开设置、不操作界面。已经开启却仍报 disabled 时，先比较当前受限进程与宿主终端的 `status`，不要让开发者反复开启。状态只证明开关／服务进程，不证明已连接或具有工程授权。

每次真实连接先进行 MCP 协商和工具发现。默认服务与实际运行的 Xcode 实例分别尝试，PID 必须来自当前进程观测，不能固化示例 PID。保存请求、原响应、失败分类和所选配置。`DocumentationSearch` 不存在时记录 `not_advertised`，继续其他已发现的只读能力或原生 CLI；不能声称所有 MCP 不可用。

本工具的 **MCP 客户端**只允许明确的读取操作，例如 `GetTargetBuildSettings`、`GetFileCompilerFlags`、`XcodeRead`、`XcodeGrep`、`XcodeGlob` 和 `XcodeLS`；仍须检查当次实际 schema 和 mutating 声明。此只读客户端不调用写工具、运行应用／调试代码或界面执行工具；这不构成对独立 Xcode CLI/XCUITest 应用截图与测试的总禁令，后者按已确认的应用/设备/场景范围单独运行并取证。Apple 的服务权限按 agent／目录信任，不是一个全局只读开关；本工具执行客户端只读白名单，不能宣称服务已经在所有客户端上禁止写入。不得使用允许所有 agent 的 unsafe 开关，不自动批准 agent 或文件夹，不扩整盘授权。若当前宿主无法满足开发者要求的权限粒度，就保持 CLI 路径。

工程查询需要真实的目标工程上下文，授权失败与工具缺失分别报告。不要自动打开运行中的迁移项目，也不要为通过门禁扩大目录授权。实际选定构建配置仍由原生 CLI／原编译日志交叉核验；MCP 构建设置字段不自动等同某次真实编译。Swift 的编译单位为模块，单文件 compiler flags 字段也不能直接代替真实 Swift driver 参数。

新项目直接运行 spec 时，`source-analysis` / `--plan-only` 同样返回选择卡。已有会话只读授权由主控通过 `--mcp enable` 传入，选 CLI 用 `--mcp skip`；两者也可放在分析配置的 `mcp` 字段。初始化 `--prepare` 保存的明确选择自动沿用，默认 ask 不覆盖它。仅只读盘点不会写入选择文件；没有保存文件不能被解释为允许自动连接 MCP。显式选择之后重试不重复问开关；服务开关、当前进程可见性、已打开工程、agent/目录授权、协议发现与实际查询分别记录。

每项能力都在 `permission_preflight` 说明用途、读取与写入范围、宿主手动授权步骤以及可选路径差异。后续运行记录分开写 `capability_available`、`authorized`、`actually_invoked` 和 `result`：工具存在不能代替授权，开关启用不能代替 MCP 连接或工程授权，已发现工具不能代替真实调用，文档查询成功不能代替真实构建配置。未知授权用 `null`，未运行用 `not_run`，不能写成通过。沿用已有明确授权；不要仅为初始化重复索要权限。

发生缺口时给出可执行备选项和差异，保留开发者选择：例如继续 CLI 并保留 MCP 证据缺口，或按真实状态解决特定 agent／工程授权后重试。只有官方 `status` 实际提供了待批 ID 时才讨论该 ID 的批准；日志中的短活动标识不是可猜测的审批 ID。当前官方 CLI 的 agent／文件夹批准不是逐工具只读授权；如果开发者要求服务端严格禁止写工具而宿主不能表达该粒度，则继续 CLI，不扩大信任来绕过。

`init-environment` 仅对明确选中的入口准备执行权限和隔离状态；全包缺件与许可完整性留给安装／发行审计，实际每次载荷调用保留严格准入。报告缺口、真实错误、CLI 降级和恢复条件，不能将工具环境状态写成产品功能已验证。
