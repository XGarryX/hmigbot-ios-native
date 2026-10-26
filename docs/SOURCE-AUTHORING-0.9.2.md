# 0.9.2 源快照与规格生成修复

## Xcode 自动文件

源扫描仅忽略 `.xcodeproj/project.xcworkspace/contents.xcworkspacedata` 的标准自引用XML：Workspace version=1.0，仅含一个 location=self: 的FileRef，无额外内容。空XML、异常XML、额外属性/引用、独立workspace均保留。相同嵌入workspace下，仅含布尔 `IDEDidComputeMac32BitWarning=true` 的 IDEWorkspaceChecks.plist 视为工具缓存，其它内容保留。

仅在 `.xcodeproj/.xcworkspace` 直属 `xcuserdata` 内忽略 UserInterfaceState.xcuserstate，以及仅含已知Scheme显示/自动创建管理字段的 xcschememanagement.plist。共享/本地Scheme、Package.resolved、WorkspaceSettings、其它未知元数据、工程文件、资源与源码继续参与摘要。符号链接检查仍执行；不整目录忽略workspace或xcuserdata。

旧索引已计入这些文件时，升级不会静默换hash或关闭finding。保存旧baseline，用当前工具重提facts、复审受影响输入，再按原 `source-refresh --review` 协议归档并更新索引，重跑专业审阅和源门禁；冻结计划显式replan。原索引拒绝覆盖的保护继续保留。

## 规格生成

新增现有Spec阶段的只读 `spec-authoring`：[操作协议](../skills/a2h-spec/references/native-authoring.md)。它枚举当前全部页面/功能和索引声明，生成unknown填报模板；原作者提交真实事实后，序列化规范JSON字段并生成合法源真值令牌。产出为可审查候选，必须由原作者复核落盘并通过原正式门禁。

`source_disposition` schema、生成器与source-check共享字段要求；owner不会被自动转为范围处置。native维度、证据、typed fact和状态/NA矛盾检查由生成器与正式门禁共用。缺件、重复/多余ID、漏维度、未知声明、错误或过期事实、越界路径/行号均拒绝；不补造语义。

此修复不改应用业务源码，不重写已有应用baseline，不放宽门禁。工具回归、发行安装验证与应用编译/设备验收分别报告。
