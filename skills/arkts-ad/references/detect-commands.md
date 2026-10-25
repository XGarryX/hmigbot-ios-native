# 原生广告依赖识别

读取同一选定 target/Release Source 与工程依赖清单：Package.swift/Package.resolved、Podfile.lock、工程 frameworks/Embed Frameworks、xcframework 与实际 wrapper。依赖存在不等于本轮产品实际使用；沿初始化、广告位、加载/展示/关闭、错误/超时、奖励与隐私调用链确认。

Info.plist 的 SKAdNetworkItems、使用说明、entitlements 和真实 bundle 只是辅助证据，不能替代调用链。未知/动态加载保留候选与源锚点，不按文件数量或零命中判定无广告。得到真实源 SDK/版本与场景后进入原 catalog 路由，再核验目标版本/许可/API/初始化与隐私条件。
