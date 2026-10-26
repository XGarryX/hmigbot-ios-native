# 上游来源与派生改动

## 0.7.0 iOS 专业资料

本版实际导入三套固定 MIT 快照，原文件不改写；许可文本随各快照提供。
逐文件 URL 对应的 upstream_path、提交和 SHA256 见 [清单](../vendor/ios-expertise/manifest.json)。

| 来源 | 固定提交 | 许可与导入范围 |
|---|---|---|
| https://github.com/AvdLee/SwiftUI-Agent-Skill | 204dba7c67256a8b707ee3fbc5759a824191974f | [MIT](../vendor/ios-expertise/swiftui/LICENSE)；SwiftUI skill 目录 |
| https://github.com/AvdLee/Swift-Concurrency-Agent-Skill | d5770817d2622e1585b1f7eaebc791a9cb0959c8 | [MIT](../vendor/ios-expertise/concurrency/LICENSE)；Concurrency skill 目录 |
| https://github.com/CharlesWiltgen/Axiom | d35eaca69e423d5157bb39c2a1b5f76ff9802f86 | [MIT](../vendor/ios-expertise/uikit/LICENSE)；Codex UIKit 主题和 memory-debugging/objc-block-retain-cycles 参考 |

导入器 scripts/vendor_ios_expertise.py 固定提交、下载字节并核对 MIT 文本；上游资料为
本地分析输入，不自动执行下载脚本，不注册它们的开发 hooks/agents。代码与参考中
保留的外链不表示已导入该外链内容或拥有其他资料的再分发权。

Serena 应用未导入本包。其当前应用为 GPL-3.0-or-later、SolidLSP 为 MIT，依
[上游许可](https://github.com/oraios/serena/blob/main/LICENSE)分别使用。
Xcode/MobileBuildMCP/Apple SDK 为可选环境能力，本次没有分发其二进制或官方导出 skill。
本仓 stdio 客户端依据 [MCP 生命周期](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle)
和 [stdio 传输](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)独立实现。

## 原 HMigBot 来源

本工具基于用户提供的独立 HMigBot CodeX 1.6.1，作者元数据为 fuxi-ailabs，仓库元数据为 https://github.com/fuxi-ailabs/hmigbot-CodeX 。不是 HMigBot Plus。

[原插件清单](upstream/.codex-plugin/plugin.json)声明 license 为 MIT；本机发行目录未发现独立 LICENSE 正文，因此此处如实保留来源和原声明，不代替上游补写授权。原 README、CHANGELOG、安装/配置/调度材料保存在 docs/upstream 中供比对，不作为本版本安装入口。

[导入清单](upstream/import-manifest.json)逐文件记录导入时的路径、大小和 SHA256；忽略的仅为文件系统元数据及构建缓存（如 .DS_Store、._*、__pycache__），不删校验器依赖。[派生修改清单](upstream/derivative-manifest.json)记录当前内容相对导入基线的变化。

原 99 份技能、31 份角色与依赖完整位于 vendor/hmigbot，3,516 文件与导入基线 SHA256 一致。
启用层为 96 技能、29 角色：退出 10 个原源专用技能和 4 个源角色，增加 7 个 iOS 技能和 2 个 iOS 角色，
复用目标规程并改写其源输入。启用入口使用通用 source_anchors 与 ios-semantics，原二进制及平台限制保留。
vendor 不在插件发现路径；旧平台词汇属于真实原文和来源记录，不能通过改写归档伪造原始来源。

完整资源安装到工作区，原目录可完全不在另一台机器上。运行时不读取上述来源路径；仓库地址只是溯源信息。

## 1.7.0 选定调度组件

0.6.0 从用户本机 hmigbot-CodeX-1.7.0.tar.gz 的标准 migbot 树提取 a2h-execute 子树 314 个文件，原文与二进制摘要按 [选定组件清单](upstream/scheduler-1.7.0-manifest.json) 保存。不改写原始归档，不声称整套 1.7.0 已移植。运行状态程序与 _wavelib 直接复用；iOS 输入适配、Windows 临时解释器补充及前置检查为本仓派生实现。
