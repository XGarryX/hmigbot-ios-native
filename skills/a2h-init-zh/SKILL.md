---
name: a2h-init-zh
description: "中文初始化入口，使用 a2h-init 的原生 iOS 配置与环境检查协议。"
---


# 初始化原生 iOS 迁移

先读取用户已提供路径及 `.migbot/config.json`，不要重复询问已知信息。
本包用于读取 iOS 源工程并实现鸿蒙目标。工作区/工具目录不是待迁移源工程，
没有选源工程时可以完成工具安装与自检，不创建虚构应用 baseline。

1. 核对 iOS 源根与鸿蒙目标根真实存在且互不包含。识别 Xcode/SwiftPM/源码入口，
   不要求源必须能在 Windows 编译。
2. 找本包 runtime：工作区安装在 `.hmigbot-ios/plugin`；插件原目录就是 runtime。
   执行 `python <runtime>/scripts/a2h_ios.py init --source <ios> --project <target>`。
3. config 必须保存 `source_platform=ios`、`ios`、`harmonyos`、language、confirmed。
   路径可含空格。现有不同源平台或不同源根不能静默改写；先报告具体冲突。
4. 检查目标 hvigor/node/DevEco/SDK 与可用 hdc；配置真实文件路径，运行 validate。
   只做源分析不以缺目标设备阻断；执行目标 build 前需要相应工具。
5. iOS 的 Xcode、Mac、iPhone、Apple skills/MCP 是独立能力：分别记录 available、
   configured、executed。云编译日志不能代替 iPhone 安装/功能验证。
6. 输出已检测项和可执行阶段，按现有授权进入 a2h-run/spec。

不写账号密码、证书私钥到配置。现有业务源和目标代码不因初始化被覆盖。
配置文件只记录事实，缺工具写 unavailable，不生成虚假路径。
重复运行应幂等；源更换需要先保留并重审旧 baseline，不能沿用其成功状态。
