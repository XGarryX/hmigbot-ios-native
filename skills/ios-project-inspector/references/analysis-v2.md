# 工程事实：提取、复核、恢复

输入：配置中 ios 源根、目标根、选定 scope、真实工具可用性。输出：机器 ios-project-signals.json 与模型 ios-project.md，事实进入 v2 semantics；不改目标生产代码。

1. 对照 project_inventory 中每个 target 的 sources/resources/frameworks phase、configuration、xcconfig 引用和 sourceTree 路径。检查多 group、同步 group、外部文件、脚本 phase 和生成代码。
2. workspace 与 project 的有效 scheme/configuration/sdk/arch/编译宏由实际捕获确定。没有捕获时明确 repository scope 和 effective_build unresolved，不能用 target 名称猜有效成员。
3. 核对 SwiftPM/Pods/Carthage 锁版本及实际 imports/calls。可执行 manifest 不在扫描中执行；二进制 framework 的公开接口与使用点成为接缝，不能凭依赖名称自动选鸿蒙库。
4. 确认 App/Scene 生命周期、extension/后台入口、桥接头、ObjC++、Swift actor 和条件编译。每种入口分配稳定事实 owner，交 UI/feature/API 分析，不因没有主页面而遗漏。
5. 将项目未知逐条交给具体 provider/源码/产品决定；源解析错误是合同阻断，缺 Apple 构建设备是该证据层级未验证。既有快照过期要重读变化路径，不只换摘要。

模板：ios-project.md 写源摘要与范围、targets/configuration、成员证据、依赖版本、入口、桥接与生成代码、未知/所需工具。ios-analysis-provenance 只记真实执行的版本/参数/输出；不可把本技能标成 Apple 官方导出技能。

交接验收：每个业务源文件归属页面、功能或经复核的 disposition；与 source-index 相同快照；目标规划前运行 harness-check。失败返回 rule/path/owner/恢复条件，保留独立 findings section。
