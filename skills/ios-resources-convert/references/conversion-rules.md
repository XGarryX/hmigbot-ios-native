# iOS 资源 → HarmonyOS 转换规则

按 ios-resources-convert/SKILL.md 的原 Stage 0 顺序执行，不重新初始化非空目标。读取选定 target/Release 的实际资源成员与构建设置；不能把未选扩展的资源都算入本轮，也不能漏掉主应用确实引用的共享资源。

| 原生来源 | 转换与保留 |
|---|---|
| Asset Catalog imageset / appiconset / colorset 的 Contents.json | 名称、实际文件、scale、idiom、appearance、color space、rendering mode；按真实支持与目标限定目录映射，不能把像素直接当逻辑尺寸 |
| .strings / .stringsdict / .xcstrings | 源 locale、占位符、转义、复数/变体与上下文；复用 localization-inventory/convert，不能假装所有语言已翻译 |
| 字体文件与 UIAppFonts / 源注册调用 | 字体文件、实际 family/weight、许可与加载方式；目标引用需真实存在 |
| Bundle / SwiftPM resource bundle、音视频、动画 | 真实 target 成员、引用路径、依赖版本和生命周期；编译后资源或不可转换格式记缺口 |
| SVG / PDF / SF Symbol / Core Graphics 绘制 | 按实际格式处理；SVG 可复用标准 XML 规则，PDF/符号/绘制不冒充 XML drawable，无法转换时进原决策/占位流程 |

使用随包 scripts/ios_resources.py 与已保留的 asset/localization atoms，在隔离目录生成，检查后由原 execute 单写者合并。目标 base/element、media、profile、rawfile 与语言/外观目录按原资源结构使用。保留用户文件、冲突报告和 source-to-target mapping。

每个目标静态资源引用必须可解析，缺少源资源则按原 MISSING_xxx / resource-pending-asset 规则登记。fallback 翻译保留 TODO 标记与 resource-pending-translation 条目。原 Stage 0 资源门、编译门和后续残量 sweep 均不变；转换不代表视觉或运行验证。
