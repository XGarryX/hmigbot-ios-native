# 来源与许可

主干来自 iOS HMigBot CodeX 1.5.2，原作者、许可与代码来源说明保留；独立分发 ID 为 hmigbot-ios152。所保留的 HMigBot 编译程序逐字节复用，不代表本轮重新编译或取得其未公开实现。

原生输入选择复用本地 iOS 20261022.5 已验证的 Xcode/synchronized groups、成员归属、条件源码、字面量边界、资源及 Windows 路径修复；没有引入其旧 harness 或更重的 SPEC 规则。

Windows provider 静态包含官方 SwiftSyntax/SwiftParser/SwiftIfConfig 604.0.0，许可原文：[Apache 2.0 with Runtime Library Exception](licenses/swift-syntax/LICENSE.txt)。上游项目为 https://github.com/swiftlang/swift-syntax 。provider 源码位于 providers/swift-syntax，固定版本见 Package.swift。

随包文件 `bin/swift-syntax/windows-x86_64/hmigbot-swift-syntax.exe` SHA256：`22628038b655aa066dd67daa9a66d83fca3288f5ecf892158cf27da3124d7a69`。本轮从之前本地已构建的工具副本复制，Package.swift、main.swift、ConditionalSource.swift 三文件逐字节相同，并实跑新副本；本轮没有重编，因此不声称新的构建来源证明或可复现构建认证。Swift 工具链运行库另行安装，本包不分发 Apple SDK。

## ios.13 Mac 运行路径

Mac 入口使用用户已安装 Xcode 内的 SwiftParser / SwiftSyntax / SwiftIfConfig。小型适配程序在本机编译，记录真实工具链身份和源码/产物哈希；Xcode 相关库与 SDK 不被复制进工具分发包。上文 Windows 预编译 provider 的哈希与 604.0.0 说明是历史基线信息，不作为当前 Mac 产物证明。原 HMigBot 编译程序保持原字节，未重编。
