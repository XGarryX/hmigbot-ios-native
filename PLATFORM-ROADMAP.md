# 平台支持标记

当前交付版本：`0.13.4`。当前发布配置：`macos-arm64`，支持 macOS Apple Silicon。

| 平台 | 当前状态 | 恢复支持需要的独立工作 |
| --- | --- | --- |
| macOS Apple Silicon | 当前运行与发布路径 | 使用本机 Xcode、适用的官方技能/MCP/CLI 和目标官方 SDK；实际执行证据分别记录 |
| Intel Mac | deferred | 完整 Intel 辅助引擎、解释器/动态库依赖、权限与官方工具链组合验证；不能仅凭一个启动器宣称支持 |
| Windows | deferred | 完整平台引擎、解释器与 Job Object/超时/清理验证、路径与编码验证、iOS 官方证据的明确获取路径 |
| Linux | deferred | 完整平台引擎与依赖、iOS 官方证据路径，以及目标 SDK 的实际支持与组合验证 |

暂缓平台不参与当前后端选择，不回退为 Windows static 或 Intel 原生。宿主发现可只读返回 `unsupported` / `deferred`；运行入口和安装器在写入前拒绝不支持的宿主。

`process_runtime.py` 只保留当前 Mac 路径的 CPython `subprocess.run` 语义，包括命令参数、独立 stdout/stderr、超时与调用者的错误恢复；它不宣称实现 Windows Job Object 或额外的后代进程终止保证。Windows 专用调度、进程所有权和解释器引导模块不进入当前发布包，未来恢复时应在独立平台实现中验证。

平台发现、工具可用、真实调用和业务验收是不同证据。MCP/CLI 未连接或 SDK 未构建时，不得把当前平台支持状态写成原生采集或业务转换完成。本标记不授权设备控制、屏幕读取、远程服务或 Git 操作。
