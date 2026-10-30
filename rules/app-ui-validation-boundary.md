# 应用 UI 验证与桌面远控边界

本规则适用于当前融合版。应用截图、官方 UI 自动测试和桌面接管是不同能力；许可、宿主可用、实现交付、实际调用和验收结果分别记录。

## 范围与授权

- 禁止通过 Computer Use／CUA、模拟鼠标键盘或桌面控制脚本接管用户电脑，操作无关应用、系统设置或授权弹窗。工具不自动改变系统屏幕、辅助功能或设备信任权限。
- 对任务已明确的测试应用、模拟器和场景，允许使用官方测试框架采集应用/窗口/元素截图、查询控件信息，并按固定步骤点击、输入、返回和断言。已有范围和授权直接沿用，不为每个已授权步骤重复确认。
- 应用测试绑定实际 bundle ID、设备标识、构建身份、场景/检查点及语言、主题、字号等配置。没有指定设备时不猜测个人真机或读取其他应用；仅指出真实缺失输入以及可用替代路径。
- 允许截图不等于允许录屏、远控、任意应用或未指定设备。无桌面屏幕权限不能直接成为指定应用截图或 XCUITest 的全局失败理由；必须保存具体工具错误。
- Preview 可用于固定样例、主题、长文字、空态或字号的组件检查，记录输入、配置和输出；Preview 不能证明完整业务链路、导航或持久化行为已经运行。

## 官方路径与证据

源端优先 Apple [XCUIAutomation](https://developer.apple.com/documentation/xcuiautomation)、[XCUIScreenshot](https://developer.apple.com/documentation/xcuiautomation/xcuiscreenshot)、[XCUIElementQuery](https://developer.apple.com/documentation/xcuiautomation/xcuielementquery) 和适用 Xcode CLI。稳定定位优先采用可访问性标识，保存测试系统实际暴露的元素信息；它不是完整的 SwiftUI/UIKit 内部视图树，自绘等信息缺口保留。

[Preview](https://developer.apple.com/documentation/xcode/adding-previews-to-your-interface-files) 与真应用运行证据分开。当前 MCP 客户端继续遵守其只读白名单；MCP 不可用时，可执行的 Xcode CLI/XCTest 路径独立工作，不借测试扩大 MCP 信任或绕过系统授权。

每次运行记录计划、实际 argv/工具来源、退出码、应用/设备/构建与配置、场景和检查点、产物摘要、错误及恢复条件。具体应用转换的截图、控件和回放结果落在该鸿蒙目标工程的 `spec/` 证据域，进度入口为 `spec/reports/ios-progress.md`。仅为优化工具而进行的验证属于工具维护；其进度、报告、样例和采集产物统一保存在应用项目与工具发行树之外的维护目录，不写入应用转换记录。

## 结果与流程

“允许使用”不表示“后端已实现”；“工具存在”不表示“已获得本次范围授权”；“执行成功”不表示“验收通过”。截图相似或控件存在不替代事件、导航、错误处理和持久化行为验证。两端配对必须具有相应检查点的当前源/目标证据；只有一端、构建过期或检查点缺失时保留具体缺口。

旧 `arkts-scenario-runner`、`arkts-visual-verify`、`arkts-ui-verifier`、`ios-screenshot-analyzer` 及关联视觉角色仍按 [延期标记](../docs/DEFERRED-CAPABILITIES.md) 处理；不得借开放应用测试恢复旧 Android 执行脚本、业务样例或默认账号数据。新官方应用测试适配器只按实际入口和收据描述实现状态。

未选 UI 运行验证不阻断基本转换、静态分析、编译和报告；已选但缺环境/输入的项记录具体 `not_run`／`deferred` 与恢复办法。真实执行失败或已归因产品缺陷不改成未执行，也不通过删除范围隐藏。首次与终态按既定验收范围完整核对，中间复查按真实受影响输入和检查点进行；性能收益只报告同一验收口径的实际测量。
