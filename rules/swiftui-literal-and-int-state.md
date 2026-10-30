# swiftui-literal-and-int-state/1

状态：已实现的受限页面草稿规则。不是完整 Swift 编译器，也不是已验证的 UI 等价规则。

前提：单文件仅导入 SwiftUI，只有一个 `struct Name: View`；成员为零或多个页内 `@State [private] var x[: Int] = 整数字面量`，随后是 `var body: some View`。整个文件必须被语法规则消费。额外 helper、宏、扩展、其他 import 或声明一律拒绝。

支持：VStack/HStack（可选数字 spacing）、ZStack、Text 字面量、Text 的已声明整数状态插值、Button 字面量及单条整数赋值/加减语句、Spacer、Divider；数字 padding、frame width/height。生成 Column/Row/Stack/Text/Button/Blank/Divider 及页内 @State。

0.2.0 增加 `Image("name")`，要求提供与源码摘要匹配的 asset-convert 产物，绑定唯一资源并设置逻辑尺寸。字面量 Text/Button 可绑定 localization-convert 语言表；`Text(verbatim:)` 保留原文。歧义资源名、字符串 namespace、未经验证的资源包拒绝转换。SF Symbols、格式参数/复数、gamut/主题变体等不属于此规则。

正例：`tests/fixtures/swiftui_counter`、`tests/fixtures/swiftui_static`。反例覆盖动态文本、异步、循环、导航、额外副作用、未知 modifier、非法尺寸及大整数。

尚未保证：默认布局、字体、颜色、可访问性、国际化、整数溢出、Swift 状态更新时序、生命周期、导航和源 App 入口。Swift 点与 ArkUI vp 及默认 spacing 需要双端视觉校验。规则只生成独立页面预览工程。自动闭包、跨文件类型遮蔽、有效构建条件还需要 SwiftSyntax/SourceKit/编译器适配器。

版本：代码使用 Stage/ArkTS 1.x；构建 profile 显式传入，最低 API 不低于 12。实际测试的 SDK、工具和结果记录在当轮外置验证证据中；其他版本仅可生成，未宣称验证通过。

规范依据：[Apple SwiftUI](https://developer.apple.com/documentation/swiftui)、[华为 ArkUI Stage](https://developer.huawei.com/consumer/cn/arkui/arkui-stage)、[华为 ArkTS](https://developer.huawei.com/consumer/cn/arkts)。映射是本项目实现，官方文档不构成自动迁移等价证明。
