# 安装、升级和卸载 0.13.7

当前发行只支持 macOS Apple Silicon（arm64/aarch64），需要 Python 3.11+。Xcode 及目标 DevEco Studio/SDK 由开发者按实际转换任务安装；Intel、Windows、Linux 标记为 deferred，不提供可执行支持承诺。

## 安装

```sh
PYTHON=python3 sh install.sh /absolute/conversion-workspace
```

安装器在写入之前检查宿主和现有托管文件；不支持的宿主不会产生半安装目录。结果包含 `.agents/skills`、`.codex/agents`、`.migbot/bin` 和 `.hmigbot-ios/plugin` 的所选运行资源，实际文件由同一发行 profile 决定。它保留业务源、Spec、目标产物与用户已有规则；已有用户配置不被替换。安装后重新打开会话发现 `$a2h-run`。

初始化命令只填写开发者自己的路径：

```sh
python3 .hmigbot-ios/plugin/scripts/a2h_ios.py init --source /absolute/ios-source --project .
python3 .hmigbot-ios/plugin/scripts/a2h_ios.py init-environment --project . --mcp ask
```

源与目标须互不包含。`init-environment` 前置列出实际可用能力、用途、读写范围、授权选择与恢复路径；未选入口缺件仅提示，所选入口缺件才约束该动作。

## Xcode MCP 与权限

选择开启 MCP 可补充 Xcode 工程与官方文档信息；关闭时继续 CLI，所缺 MCP 交叉核验标未执行。开发者可在 `Xcode > Settings > Intelligence > Model Context Protocol` 开启服务，并手动打开目标工程、批准当前 agent 和工程目录。工具只使用本次允许的只读工具；服务器开关和逐工具权限不是同一件事。

只有明确选择 `--mcp enable --prepare` 才尝试官方 CLI 开启，仍需系统授权时给出具体手动步骤；不自动操作界面、不申请屏幕或设备权限。授权前后的可用、获准、实际调用、结果分别记录。详见 [权限选择](../skills/a2h-init/references/xcode-mcp-choice.md) 和 [Apple 官方说明](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode)。

## 应用 UI 测试范围

安装不会自动授予设备或桌面操作权限。指定测试应用/模拟器的截图、控件查询和固定回放按任务已确认范围调用官方测试框架；Preview 仅作组件证据。禁止桌面接管、无关应用和自动操作系统授权设置；录屏和未指定设备没有因此获准。规则见 [应用 UI 验证边界](../rules/app-ui-validation-boundary.md)。MCP 关闭或缺少桌面屏幕权限不等于 Xcode CLI/XCUITest 不可用。

升级同时刷新安装器拥有的 `.agents/skills` 和 runtime 规程。用户自行维护的 `AGENTS.md`、范围或权限条款不被静默改写；若其仍有旧截图总禁令，报告具体冲突和来源，由当前用户明确意图确定生效范围。上游 vendor 的历史文字为来源记录，当前适配合同优先，不能把旧平台命令自动当作 iOS 后端。

## 升级与卸载

重复运行安装命令即升级。用户修改过的托管文件会报出具体冲突并保留；先合并该修改再重试。安装写入失败恢复原文件。旧冻结计划不能自动继承新规则的通过状态；按实际受影响输入执行 replan，业务规格与账本不由安装器重写。

0.13.7 的资源增量协议需要新的 `task-deltas-v1` 执行合同；不能给旧合同补字段后继续施工。活动 Join 尝试也绑定其工具实现指纹：使用原尝试工具完成收尾，或按既有受审恢复流程核验新尝试，不改写历史完成证据。新协议与命令见 [资源增量规程](../skills/a2h-execute/references/resource-deltas.md)。

```sh
sh uninstall.sh /absolute/conversion-workspace
```

卸载只移除仍与安装清单匹配的托管文件，修改过的文件保留并报告。项目代码、Spec、构建成果和其他插件不受清理。

## 发行与运行边界

包/安装共用同一 macos-arm64 文件选择：项目数据、开发测试/夹具/结果、维护报告、缓存和其他平台资产不进入运行资源。通用模板、schema、必要原引擎及许可证保留。下载隔离属性仅在已校验的项目内运行目录按实际需要处理，保留结果，不改变系统 Gatekeeper 策略。目标编译、运行和视觉验收分别以真实 SDK/设备证据报告。
