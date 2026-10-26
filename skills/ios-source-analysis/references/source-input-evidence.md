<!-- when: Package.swift未求值，或需区分Xcode产品与测试编译源时读取；topics: manifest-evaluate、manifest-evidence、project-targets、续跑 -->
# 清单求值与产品成员证据

两种输入分别回答“这个清单在当前宿主求值得到什么声明”和“这个Xcode工程声明哪些源文件属于所选产品”。按实际需要使用，可组合传给 `facts`。它们不证明iOS有效构建、依赖已解析或运行行为。不要为了消除工具缺口删改应用的合法清单或测试。

## SwiftPM清单实际求值

先确认源根与目标根分离，当前宿主可运行与源清单兼容的Swift。配置JSON放在目标工程，例如 `<target>/spec/ref/manifest-evaluate.config.json`：

```json
{
  "schema_version": 1,
  "manifests": [{
    "path": "Package.swift",
    "command": ["swift", "package", "--package-path", "{package_dir}", "dump-package"],
    "version_command": ["swift", "--version"],
    "timeout_seconds": 120,
    "conditions": "当前宿主的SwiftPM清单求值；未运行iOS构建"
  }]
}
```

`path` 是源根内真实 `Package.swift` 的精确相对路径；嵌套包逐项列出。`command`、`version_command` 必须为显式argv数组，前者包含独立的 `package`、`dump-package` 参数，后者包含 `--version`。`command` 必须且只能给出一个显式 `--package-path`，解析后的目录须等于 `path` 所指清单的父目录。版本输出须包含合法的 `Swift version 主.次[.补丁]`（可带 `Apple` 前缀）；原始dump含 `packageKind` 时，其 `root` 必须唯一且与同一清单父目录匹配。`timeout_seconds` 为1至3600的整数，省略时120；`conditions` 为可选说明字符串。用 `python <当前技能目录>/scripts/run.py --runtime-root` 定位 `<runtime>`，字段与报告合同以随包runtime的 `<runtime>/schemas/source-manifest-evidence.schema.json` 为权威；安装到 `<workspace>/.agents/skills/` 后不要按技能相对路径寻找 `.agents/schemas/`。采集程序校验实际配置，不接受未知字段。

`{source}` 与 `{package_dir}` 展开为采集程序所在宿主的绝对路径；程序不会自动做WSL路径转换。若使用WSL，先核对真实映射，再提供例如 `["wsl", "--", "swift", "package", "--package-path", "/mnt/d/path/to/package", "dump-package"]` 及同一环境的版本命令；不能将Windows路径直接作为WSL目录，也不能把此示例路径当成实际证据。记录宿主差异，清单中的平台条件仍以实际执行环境为限。

```text
python <runtime>/scripts/a2h_ios.py manifest-evaluate --project <target> --config <target>/spec/ref/manifest-evaluate.config.json --output <target>/spec/ref/ios-manifest-evidence/<capture-id>
python <runtime>/scripts/a2h_ios.py facts --project <target> --manifest-evidence <target>/spec/ref/ios-manifest-evidence/<capture-id>
```

输出须位于目标的 `spec/ref/ios-manifest-evidence/` 内，目录必须不存在或为空，且不能与源根重叠；每次重试选新capture-id。`facts --manifest-evidence` 接受该目录或其中的 `manifest.json`，只读取当前源绑定且可回放的成功证据。

采集器实际运行Swift版本查询和 `dump-package`，保存argv、cwd、超时、退出码、原始stdout/stderr、前后源快照和摘要。版本失败、超时、非零退出、非法JSON或采集期间源变化均返回 `capture_failed`（CLI exit 2）；保留日志，修正环境或清单中的真实错误后重采。只有真实源错误才修改源代码，不能手写成功报告。

验证器按当前源与原始日志重算 `name`、`targets`、`dependencies`，拒绝过期、缺失、篡改或摘要与原始结果不符的证据。通过仅表示 `manifest_evaluated`，范围为 `current_host_manifest_evaluation`；`dependency_resolution`、`behavior_equivalence`、`capture_authenticity` 均保持 `not_verified`。摘要核对不认证执行器身份或证据作者。

事实提取只解除证据中精确匹配路径的 `Package.swift` 未求值问题；其他包清单、Podfile、Cartfile的问题仍保留。包的targets/dependencies是清单声明，不能据此宣布依赖解析、编译或鸿蒙迁移完成。

## Xcode工程声明的产品成员

有可解析的真实 `.xcodeproj/project.pbxproj`，需要把产品源与测试oracle区分时，创建variant输入，例如 `<target>/spec/ref/project-targets.json`：

```json
{
  "scope": "project-targets",
  "project_path": "Example.xcodeproj/project.pbxproj",
  "targets": ["Example"],
  "configuration": "Release"
}
```

仅提供这四个字段；替换为源根内真实工程路径、精确app/app-extension根target名字及已声明configuration。解析器从工程推导 `source_files`、`source_membership`、`excluded_sources`、`target_closure` 与摘要，回放时重新推导；调用者不能自写文件白名单或改派生字段。闭包包括 `PBXTargetDependency` 及产品引用中的嵌入扩展/本地依赖，不能只扫描主target目录。

```text
python <runtime>/scripts/a2h_ios.py facts --project <target> --variant <target>/spec/ref/project-targets.json --manifest-evidence <target>/spec/ref/ios-manifest-evidence/<capture-id>
```

无清单证据需求时省略 `--manifest-evidence`。测试独占文件由工程成员确定并列为 `test_only_oracle`，不作为本轮产品编译源扫描；与产品共享的文件仍保留。完整source-index不缩小，测试/依赖的disposition及验收真值责任仍保留，不能按Tests目录名直接排除。头文件因隐式包含关系保守保留全仓扫描，产品源中的活动 `#if` 等未解析信号继续阻断。

结果只标 `evidence=project_declared_membership`、`effective_build=unresolved`。条件build settings不用于删减成员；未知/歧义/越界路径、无归属编译单元、构建脚本、同步组、外部或跨工程依赖、自定义build rules及不支持的产品编译语言均拒绝推断。需要真实所选构建时仍走既有 `selected-build` 与 `source_build`、已哈希 `source-files.json` 证据协议，不能改标记冒充。

## 旧图续跑与交接

保留原失败现场。源未变时，用新输入重新执行 `facts`，由工具归档旧图；源已变时先按Harness的 `source-refresh --review` 协议更新索引并重新采集证据。新图把清单报告路径和 `report_sha256` 绑定到 `manifest_evidence`；`validate_graph` 重放当前源与原始证据，domains计划冻结清单目录中的原始产物。

重生成专业视图及 `expertise-plan`，由原owner复审受影响的semantics、coverage、disposition、规格和专业观察，再运行 `spec-check`、`source-check --harness`。门禁失败就处理当前finding，不复用旧PASS；已有冻结计划按Harness的 `replan` 协议重排。工具输入问题消除后仍可能有未完成规格或行为未知，按实际检查结果继续推进。


## 所选 Clang 构建的活动源码证据（conditional-capture v1）

适用于单 Xcode app target 的 Objective-C/C/C++ 编译单元。仍保留 repository/project-targets 与旧 selected-build 的兼容路径；没有本协议证据时条件编译问题继续阻断。Swift 条件、复杂 module/PCH-only 条件、多target、嵌套response、外部编译单元、源#line重映射、编译器插件/VFS overlay不在此适配器范围，不推断通过。

### 输入与实际生产

先由宿主真实执行所选 xcodebuild、记录完整日志并打包 source_build。此适配器消费以下已经哈希的原始记录，不接受手写文件白名单：

- `commands.json` 与 `capture-report.json`：device-build命令、cwd、exit_code、源摘要/未变、build_succeeded；实际 stdout 必须保留成功标记和完整 Clang -c 行。
- `build-settings.json` 与 `build-settings.stdout.log`：同一次真实查询的解析值与原输出；target/configuration/project/SDKROOT/ARCHS匹配。
- `compile-commands.json`：build_log_line/original_argv/expanded_argv；由工具重新从日志与 `build-inputs/<response basename>` 推导核对，不能自填另一个编译命令。
- `source-files.json`：真实编译/依赖与模块成员；编译单元集合同时与project-targets闭包交叉核对。不是完整资源范围。
- `toolchain-inputs.json`：`{"before": {"<Clang绝对真实路径>": "<sha256>", "<SDKROOT>/SDKSettings.json": "<sha256>"}, "after": {…}}`。构建前后实际采集，两个字典完全相等且必须覆盖全部实际编译器与SDKSettings；旧构建缺少此记录时须重新构建，禁止事后补写before。
- 可选 `framework-header-provenance.json`：数组条目 `source/staged/sha256`，源头文件与本次实际模块输入的复制件逐一匹配；原始module-file-info与构建复制日志保留在source_build包中。声明列表本身不证明头文件条件生效。

配置schema由 `schemas/ios-harness-v2.schema.json` 的 conditionalConfig/conditionalBuildIdentity 定义并由实际采集与回放共同校验。示意（替换为本项目真实值）：

```json
{
  "schema_version": 1,
  "build_evidence": "/absolute/target/spec/ref/ios-build-evidence/capture-id/evidence",
  "expected_build": {
    "project": "Example.xcodeproj",
    "scheme": "Example",
    "target": "Example",
    "configuration": "Debug",
    "sdk": "iphoneos",
    "architecture": "arm64"
  },
  "timeout_seconds": 300
}
```

```text
python <runtime>/scripts/a2h_ios.py conditional-capture --project <target> --config <config.json> --output <target>/spec/ref/ios-conditional-evidence/<fresh-id>
```

工具以原编译参数仅移除目标/诊断/依赖输出动作，追加 `-E -fdirectives-only -dD -CC -Rmodule-import` 与本次依赖输出，实际执行每个单元。Clang决定分支，Python不解释#if表达式。另以同参数正常完整展开执行第二次预处理，对每次include的各条件分支活动交叉核对；例如__COUNTER__或_Pragma引起两种模式分歧时保守拒绝，不使用错误活动范围。保留注释避免跨行注释折叠丢失原token行；以真实token区分注释中的伪line marker/pragma。保留每个翻译单元和每次include独立的活动行，记录宏定义/undef影响后的结果；不能把不同上下文的活动行并成一个虚假程序。

`-Rmodule-import` 的实际加载日志绑定显式和隐式PCM；编译器、SDKSettings、prefix/PCH、hmap、依赖文件与加载模块都记录摘要，前后变化/单元间变化拒绝。源码快照前后相同。输出manifest、commands、原stdout/stderr/dependencies、inputs、guards；失败保存failure.json，不得消费失败目录。

对无文本输出的模块头文件，缺少观察不等于关闭分支。只有**整个文件唯一条件为严格头文件保护**时，才尝试以相同编译参数真实执行 `-fsyntax-only -ast-dump-all=json -ast-dump-filter=<源中实际枚举名>`。必须观察到该头文件对应源位置的完整EnumDecl（有枚举项，或PCM懒加载时有直接回指该源定义闭括号的range.end），复制件与源字节一致，才能证明该唯一保护体被编译；前置声明、同名别处定义、复杂/嵌套条件、guard重定义、alternative directive或拼接指令不成立。未观察到则原问题保留。此证明只决定保护体的活动范围，不把其他token业务事实升级为compiler_binding。

### 消费、冻结与回放

新selected-build输入保留原 `scope/source_files/evidence_path`，增加 `conditional_evidence`（上条命令实际输出目录）和与采集一致的 `expected_build`。source_files须复制经原日志/依赖推导、被原source_build哈希绑定的真实成员集合，不能为了减少告警删文件。

```text
python <runtime>/scripts/a2h_ios.py facts --project <target> --variant <selected-build.json>
```

facts只保留被观察为活动的原始tokens，仍使用原文件/行号/片段摘要；不同include上下文记录build_contexts。原始字面量账本和完整source-index不缩小。仅已完整观察的文本文件或有AST见证的严格保护体解除对应条件告警；资源、运行时@available、动态派发、宏业务语义与闭源行为仍需源复核。

图绑定conditional manifest与source_build manifest的原字节摘要，validate_graph重新核对真实原日志、采集动作、输出派生视图、源码与输入摘要。原scheduler的understand/domains冻结相关证据闭包；在同一路径替换/重打包不能沿用旧图或计划。修改源码/配置/编译器/依赖/证据后重采、重提、复审，不能改摘要继承PASS。

此版回放需要采集时的绝对编译器/SDK/依赖/PCM路径仍可读取且摘要相同，因此是本地绑定的证据，不宣称跨机器可移植。哈希完整性不认证执行器身份；一致恶意重写全部源/证据/审阅历史不属于本地摘要防护承诺。生成/编译/业务行为分开，capture_authenticity与behavior_equivalence保持not_verified。

### 聚合门禁诊断

source-check --harness增加checks视图，独立阶段分别记录PASS/FAIL。缺少专业审阅时仍检查独立的semantics/coverage/AC/spec等；依赖无效图或合同的检查为not_run并列blocked_dependencies，不计算虚假覆盖。report-only仍不写正式finding/report；正式写入继续只由原source-check管理自身section。

Clang参数依据：[官方参数参考](https://clang.llvm.org/docs/ClangCommandLineReference.html)。此协议的分支和AST结论必须来自本次真实调用，不以文档描述代替观察。
