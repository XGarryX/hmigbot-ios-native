# Mac Release 源输入

本发行版面向完整 Xcode 的 Mac，直接取得当前源工程的官方配置与编译证据。不要搬入 Windows 的有效 STATE、配置确认或通过记录。

## 1. 官方环境与产品发现

运行 `python3 scripts/ios_input.py environment`。原生适配器通过 xcrun 查询实际 Swift 编译器和 SDK；显式 DEVELOPER_DIR 错误时直接失败，不偷偷换工具链。INIT 发现项目与 scheme；迁移产品范围仍按 SPEC 与用户当前授权确定。

## 2. 真实 Release 捕获

```text
python3 scripts/ios_input.py capture-release --src <源根> --project <工程.xcodeproj> --scheme <已确认scheme> --build --out <新的捕获目录>
```

输出目录必须在源根之外且尚不存在。入口执行 Xcode project list 和显式项目的 Release / iphoneos 全 target 配置查询，保存未经改写的原始输出。使用 alltargets 是为了取得 scheme 主目标以外的嵌入产品配置，不将这些产品自动纳入迁移范围。

`--build` 在新的外部 DerivedData 目录执行所选 scheme 的无签名设备 Release 构建，保留 `.xcresult`、stdout/stderr 和实际 SwiftDriver 参数。其成功只证明这次构建，不证明签名或运行。未带 `--build` 只做查询；遇到 xcconfig 下省略的 flags 时，prepare-source 可能要求补齐真实构建参数证据。

捕获保留 `release-build-settings.json`、全树 `source-files.json`、`command-execution-records.json`、stderr、`bundle-files.sha256`；不修改原字段来伪造成功。原有 validate_capture 继续校验源内容、配置归属、argv 和输出哈希。

Xcode 索引设置可能使用 Debug 参数，即使命令写了 Release。不能未经核对就用它作为设备 Release 的条件依据；本版采用实际 Release 构建参数交叉检查。

## 3. 选择与 provider

variant JSON 沿用原协议：

```json
{
  "scope": "project-targets",
  "project_path": "<工程>.xcodeproj/project.pbxproj",
  "targets": ["<获准迁移的产品target>"],
  "configuration": "Release"
}
```

provider 从选择的 Xcode 自带 SwiftParser / SwiftSyntax / SwiftIfConfig 编译，缓存为 `~/Library/Caches/hmigbot-ios/swift-syntax/<身份哈希>/`，不在受管安装目录内构建。哈希绑定 Xcode/Swift 身份、SDK 路径及 provider 源码；不分发或复制 Apple SDK / Xcode 动态库。

默认无需 provider JSON；需要指定时仍使用独立 argv 数组：

```json
{
  "command": ["<实际provider绝对路径>", "--conditional-source"],
  "version_command": ["<实际Swift编译器绝对路径>", "--version"],
  "timeout_seconds": 120
}
```

## 4. 固定源视图

```text
python3 scripts/ios_input.py prepare-source --src <源根> --project-root <迁移项目> --bundle <捕获目录> --variant <variant.json> --out <迁移项目>/spec/ref/source-views/<新批次>
```

正式消费者共享同一个 active pointer。掩码保持原始 UTF-8 字节位置与换行，不改源工程；Swift tokens 的字符偏移在该掩码文本上转换。源、配置或掩码过期/变化时须重新捕获，不复用旧通过状态。

SwiftIfConfig 的条件原子由真实 iOS 编译器查询，版本模式也通过探针确定；完整表达式与编译器再核对。canImport 缺少已声明工程模块、未知查询、失败编译或不同 target 的不一致输入继续报 unknown，不以 false 放行。受限的历史 custom-boolean 协议仅作为内部兼容接口，不代表已处理完整 SDK 上下文。

静态候选、配置查询、源视图生成、实际构建与行为验证分别记录。
