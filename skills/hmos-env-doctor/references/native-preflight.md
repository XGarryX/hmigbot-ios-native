# 原生体检入口

ios.12 修复公开 CLI 的 argv 接线，入口可使用 `--project`、`--timeout`、`--network-mode`、`--json`、`--markdown` 和 `--help`。编译程序内部源码不可见；已实测原入口将参数拆成字符，不能声称确知其内部根因或逐条复用了不可读实现。

当前 Python 实现按原技能的机械检查类别执行：固定位置的 DevEco/SDK 发现、hvigorw/ohpm/Java/Node 版本、鸿蒙 hdc 在线目标、实际 Python、项目签名文件路径和模块网络权限。检查只读，不构建、不签名、不安装依赖、不修项目。原编译程序及其字节保留作为对照。

- 显式项目路径用于读取该项目 `.migbot/config.json` 与 `build-profile.json5`，不借用当前目录的另一个项目。
- 显式配置的 DevEco 不存在时如实 FAIL；未配置时才查询环境变量与三平台固定候选，不递归搜盘。
- `--timeout` 是每个工具链探针的超时，取值 (0,600] 秒，默认 15 秒；hdc 不超过 10 秒。取消探针的主进程/子树另有有界清理时间。输出采用临时文件快照，主进程实际退出后不等待后台服务关闭继承的输出句柄；不将该情形误报为超时。工具链真超时为 WARN，真实非零退出为 FAIL；检测不到版本记 WARN。
- 带 ea/internal 等后缀或未知格式的 JDK 版本按 WARN 处理，不用位数说明或无关 banner 推断版本。
- 配置读取支持常用 JSON5：注释、单/双引号、ASCII 无引号键、末尾逗号、常见数字形式及 [JSON5 字符串转义规则](https://spec.json5.org/#escapes)。未知或损坏语法报告解析失败，不能用空对象冒充权限检查通过；不宣称实现了全部 Unicode IdentifierName 等 JSON5 语法。
- 网络权限按可选 `--network-mode required|not-required|unknown` 判断，来源写入 `network_mode_source`。省略为 unknown，权限项一律 WARN、`needs_confirmation=true`，即使已有声明也不证明网络能力已验收。required 且配置的 HAP 和库均无 INTERNET 声明时，静态声明项为 FAIL；仅库有声明则因依赖及权限合并未核实保留 WARN；确认 HAP 静态声明覆盖时才 PASS。not-required 为调用方明确声明本轮不需要 INTERNET，记 PASS + `applicable=false` + `offline_verified=false`，不是自动离线检测，已有权限也不删除。
- INTERNET 可以由同一产品的 entry/feature HAP 提供，逐模块披露 `internet_declared`、`network_info_declared` 和 `provided_by`；HAR/shared 的声明单列 library_declarations，不计作已验证的 HAP 提供者；官方 HAR 权限会在依赖构建时合并，本入口不解析依赖关系，不能据库声明判断合并已完成，也不要求重复声明。按现有 `app.products` 与 `modules.targets.applyToProducts` 计算显式成员，不猜缺失/异常 targets 的归属。所有 HAP 自己均已声明时可静态通过；否则各含 HAP 的产品均有提供者才通过。跨产品覆盖混合或成员关系不确定时 WARN，并列出产品和未知成员，不能借另一产品的声明冒称通过。只含库、没有 HAP 时保持 WARN。
- GET_NETWORK_INFO 仅记录是否声明，不参与 INTERNET 的失败条件。模块文件缺失、配置解析错误、坏权限数组、签名材料声明路径不存在仍为 FAIL，不受 not-required 豁免；未声明签名材料路径仍 WARN。检查仅阅读 `src/main/module.json5`，不验证外部依赖、构建变体合并清单、签名或运行时授权/网络；FAIL 仅说明当前配置主清单缺少所要求的声明，自动修复前仍须核实应用实际缺失。
- 调用技能按已确认能力和目标 API 选择模式；不能从空 endpoints、库存 degraded、项目名称或没有 URL 推导 not-required。confirmed 网络能力须传 required 重跑当前同一预检入口；未传参的旧调用返回 WARN，不能据此完成网络权限验收。needs_confirmation 只是调用方确认需求的提示，没有新门、必填文件或用户审批。
- 签名密码不写入报告。项目检查可输出缺失的材料字段名，但不输出原材料对象。
- 签名绝对路径须用本平台规范形式；Windows 使用盘符或 UNC，POSIX 避免双斜杠及 Windows 路径写法，拒绝含义不确定的跨平台路径。
- 鸿蒙目标探测只运行 `hdc list targets`，不操作设备。iOS 输入不要求 Android 设备；iPhone/Simulator 观测需另有真实材料。
- stdout 为 JSON；默认 stderr 为人类可读摘要，`--json` 抑制摘要。`--markdown` 只写明确请求的报告路径；PASS/WARN 返回 0，FAIL 返回 1，参数/IO 异常返回 2。

read_only 指本诊断器不修改 App/迁移配置；各外部探针在隔离临时目录运行，但 SDK 工具可能写用户缓存或启动自己的服务，不能承诺外部进程完全无副作用。只清理本次创建的临时目录；如后台服务仍占用工作目录，保留该目录并记录未清理状态。

后台服务继承的临时输出文件可能存活到服务退出；只取主探针结束时的输出快照。探针 stdin 为 DEVNULL，不等待交互确认。取消后仍不能确认主进程退出时返回异常 exit 2 并停止，不能用 WARN 掩盖未知进程状态。

报告不是 App 构建、签名或行为验证结论。Mac 路径有隔离夹具；Mac/Linux 真实环境均未测试，Linux 安装形态及固定候选仍需真实宿主确认，不从 Windows 回归推导跨平台成功。

权限依据：[官方声明权限](https://github.com/openharmony/docs/blob/master/zh-cn/application-dev/security/AccessToken/declare-permissions.md)要求按实际需要申请，并说明同应用多HAP共享；[官方权限列表](https://github.com/openharmony/docs/blob/master/zh-cn/application-dev/security/AccessToken/permissions-for-all.md)区分INTERNET和GET_NETWORK_INFO。[官方 HAR 说明](https://github.com/openharmony/docs/blob/master/zh-cn/application-dev/quick-start/har-package.md)说明依赖构建时的权限合并。产品关联字段另核对本机DevEco随带ohos-project-build-profile-schema_zh.json；无法确定的成员不补默认推断。
