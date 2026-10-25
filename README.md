# HMigBot iOS 1.5.2 · Mac 原生输入版

独立工具包，版本 `1.5.2-ios.30`，分发 ID `hmigbot-ios152`。以 HMigBot CodeX 1.5.2 的流程、模板、规则和门禁为基础，输入为原生 iOS 工程，目标为原生 HarmonyOS 工程。后续只维护 Mac，尽可能调用 Xcode / Apple Swift 官方能力。

Mac 运行库的原始执行位由随包 `docs/macos-runtime-modes.json` 保留。安装和升级会修复同内容旧文件的错误执行位；制作分发包后可运行 `python3 -B scripts/check_runtime_permissions.py` 校验，`--fix` 仅恢复清单中内容 SHA 一致文件的执行位。

## 当前输入实现

- 通过 `xcode-select` / `xcrun` / `xcodebuild` 定位完整 Xcode、Swift 编译器和 SDK；命令级 DEVELOPER_DIR 不改变全局系统设置。
- 工程文件的 OpenStep 语法由 Apple `plutil` 解析为 plist；现有 target / 文件声明与依赖适配继续保留其证据边界。
- SwiftParser / SwiftSyntax 提供正式 Swift tokens、声明、继承、imports、枚举 case 与静态字符串解码。原 F/AC、实例 ID 及业务信号规则继续消费兼容输入。
- SwiftIfConfig 在原始语法树上选择条件分支。查询由真实 iOS Release 编译器探针回答，完整表达式再交叉核对；未知继续报缺，不猜成 false。
- Mac 的 Release 捕获入口真实调用 Xcode，保存 argv、cwd、DEVELOPER_DIR、退出码、stdout/stderr 与哈希。`--build` 另外执行无签名 Release 构建，保存实际 SwiftDriver 参数。
- Xcode 随带的 Swift 源码工具库属于工具链兼容接口。小型 provider 从随包源码构建，按 Xcode 路径/版本、Swift 版本、源码哈希缓存；缓存放在安装归属目录之外，工具链变化或二进制哈希不符即重建。构建失败不退回旧 Swift 扫描器。

## 安装与开始

需要 Python 3.11+、完整 Xcode，以及 Mac DevEco / HarmonyOS SDK。当前随包阶段引擎为 arm64，安装支持 Apple Silicon Mac。安装到专门的鸿蒙目标工程：

```sh
bash <本工具目录>/install.sh --target <鸿蒙目标工程>
```

在目标工程依次执行 `$a2h-init`、`$a2h-spec`、`$a2h-plan`、`$a2h-execute`。阶段规则与用户门遵循原有规程和本轮用户授权。本包不安装遥测 hooks，上传不是本地使用前提。

源码、鸿蒙目标、产品范围以用户当前指令为准，不将某个项目的 Widget、登录、支付或推送范围固化为工具默认值。源工程的构建依赖闭包不自动等于获准迁移的产品范围。

本包与安卓原版独立；不要装入同一迁移项目或同一用户级技能目录。工具带齐自身所需模块、模板、代理及原编译程序，不依赖外部安卓目录。安装归属、升级冲突与既有用户修改保护继续生效。

安装器仅对本包清单内、当前架构且哈希一致的原生程序逐文件移除下载隔离标记，记录处理前后哈希，失败按原事务回滚。原阶段包装器既有的 `xattr -dr` 调用仍保留；本轮没有修改它们或关闭系统 Gatekeeper。

## Release 输入

详见 [Release 输入](docs/RELEASE-INPUT.md)。原生入口支持：

```text
python3 scripts/ios_input.py environment
python3 scripts/ios_input.py capture-release --src <源根> --project <工程.xcodeproj> --scheme <scheme> --build --out <新的捕获目录>
python3 scripts/ios_input.py prepare-source --src <源根> --project-root <目标工程> --bundle <捕获目录> --variant <variant.json> --out <目标工程>/spec/ref/source-views/<新批次>
```

provider 自动从当前 Xcode 构建；通常不再手填 provider JSON。原有 `--provider` 数组配置接口保留供明确指定。

## 证据与边界

语法解析、工程声明、配置查询、实际 App 构建、签名、设备运行及行为等价是不同结果，分别报告。`showBuildSettings` 不提供完整的实际编译成员，也不代表 App 编译成功。实际成员采集模块保留，须消费真实编译记录。

- 原有闭合 SwiftUI 降级器和 Objective-C 候选识别仍有受限实现，不宣称获得编译器符号语义；主 Swift 事实输入已走官方语法树。
- 多架构、不同 target 条件、响应文件、桥接头和自定义 Clang 上下文超出当前捕获适配范围时明确报缺。不能由宿主 macOS 的模块可用性推定 iOS 条件。
- 查询省略的 Swift flags，仅在真实 Release 编译参数与官方配置相符时按未设置处理；有冲突继续阻断。原始输出不补写通过值。
- 原生 VERIFY 路由源扫描仍有历史缺口；工具验证不代表该阶段已通过，也不代表任一应用迁移完成。
- 历史多平台文件本轮尚未全面裁剪；当前安装和执行依赖 Mac，不继续增加 Windows 兼容实现。

版本 `.12` 的 644 项 Windows 回归为历史记录，不冒称本版 Mac 回归。当前验证以实际命令、报告和 Claude 依据所提交材料的文字复核为准；后者不替代测试。

原编译程序继续复用，未声称获得或重编其内部源码。来源、许可与历史 provider 信息见 [第三方说明](docs/THIRD-PARTY-NOTICES.md)。

结构检查的 Mac 实现与兼容边界见 [结构检查说明](docs/MAC-STRUCTURAL-CHECKS.md)。iOS 适配维护：Garry；原作者及许可保留。

## 可选的目标显隐映射

当原 SPEC 已批准源可选值经过官方卡片数据通道变成目标布尔条件时，SPEC 原作者可以按 [输入格式](skills/a2h-spec/references/native-binding-projections.md) 保存对应关系。这个文件不是必需的阶段产物；不存在时走原检查路径。声明不是豁免，源谓词、目标生产者、官方扩展与实际渲染链任一项不能证明，原显隐 FAIL 仍保留。

FV 适配保留原后端测量与 canonical 结果各自的日志、退出码。未完成事务会在下一次 pipeline 调用前报缺，须依据该事务的真实备份/哈希恢复，不以旧 PASS 推进。整包验证状态与应用执行状态分别记录。

宿主直接子任务的完整上下文 fork 按外层继承标记及真实父日志核验：前置元数据、连续继承前缀、创建自身的原 spawn 调用与返回均须吻合，继承内容完整参与解析及哈希，但不冒充当前任务操作。仅支持已观察的 depth1 形状；宿主变换的 reasoning 只解析及哈希，其余继承 payload 必须与父日志有序匹配。实际子任务的派发与收口规则保留。

终态回写补齐原规程的 `feature_index.verified` 字段，仅在 final 模式把已 implemented 的条目写为 verified；无此字段保持原入口。该状态仍只表示 FV-1/FV-2 的工程结果，不能代替设备验收。原引擎先 dry-run 再执行，状态单文件原子写入；后处理失败返回 3，原引擎已完成的写入保留，可重放同一 manifest。

冷启探针继续调用官方 HDC/aa/ps/hilog，验证每次远端状态标记，使用官方 aa 成功输出并核对完整进程名。明确锁屏错误 10106102 返回 3 并保留 `unverified-cold-start`；应用失败返回 1。crash、网络和附加文案仍用原 grep 判据在主机处理。设备不可观测不能证明启动或界面成功，原 verify 粘性债门控继续生效。

冷启日志按官方 HiLog 默认级别列排除 D/I 级的宽泛 Fault 匹配；W/E/F 或未知格式仍阻断。AppRecovery 按完整标识符识别，配置方法名子串不表示崩溃。官方框架源码参考为 master，ROM 对应版本未证实；未知作用域/tag 仍可能保守报错。crash/网络仍用全局日志，不能解释成本应用专属证据。
