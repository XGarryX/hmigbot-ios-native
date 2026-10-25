---
name: ios-resources-convert
description: 将 iOS Asset Catalog、strings/xcstrings、颜色、图片、字体及应用身份输入转换为 HarmonyOS 资源；保留原 Stage 0 和已有工程保护。
metadata:
  type: domain
  domain: migration
---

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# iOS Resources Convert

先读 [原生输入协议](../a2h-spec/references/native-input.md)。本技能是原资源阶段的平台输入实现，不生成新的 SPEC/PLAN 或资源验收规则。

1. 原初始化保护：目标非空则跳过模板初始化；仅目标不存在/空目录时使用随包模板。
2. 资源来源：优先使用用户已有且来源明确的 Release 构建产物/Asset Catalog 信息；Windows 静态场景读取源码资源并记录库/生成资源缺口。不运行其他源平台构建/解包工具，不为了静态分析强制 iOS 构建成功。
3. 用已保留的 `hmigbot_ios.atoms.run_atom` 的 asset-inventory/localization-inventory 查看所有变体与语言；按 asset-convert/localization-convert 在隔离目录输出转换资源。源文件不修改。default locale 来自源配置或用户确认。
4. 转换与合并：保留图片 scale/尺寸、深浅色/高对比变体、Color Asset、strings/xcstrings/复数、字体、AppIcon。不能用统一密度猜图标大小；SF Symbols、向量/编译资源无法直接还原时记录待替换项并进入原占位/决策流程。
5. 写入已确认的目标 resources，检查重名/编码/引用和应用身份，保留用户文件；运行原资源引用/结构门禁与 Stage 0 鸿蒙编译。转换完成不等于编译或视觉通过。

底层转换器保留在包内 `src/hmigbot_ios/resources.py`；实际调用入口 `scripts/ios_resources.py`，输出产物和缺口后由原 execute 单写者合并。
