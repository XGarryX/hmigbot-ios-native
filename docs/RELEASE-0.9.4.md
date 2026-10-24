# 0.9.4 · 二进制 plist 资源读取修复

日期：2026-10-22；基于0.9.3。仅本地发布准备，未上传服务器。

## 缺陷与修复

原ios_harness.coverage_check对每个fact来源无条件执行read_text(utf-8-sig)并扫描SwiftUI Preview。合法bplist00在该位置解码失败，中止当前覆盖循环，使后续义务缺口未被列出。旧891项测试未覆盖此场景，不能据其通过证明已修复。

新增source_scope.preview_source_lines：只有.swift文件进入现有Preview词法分析；所有资源及其他语言文件均不按SwiftUI Preview解释。ios_harness与quality_views共享此路由。此限制仅针对SwiftUI Preview扫描；原有Swift、Objective-C（.m/.mm）及.h头文件的源码提取、字面量分析、事实与义务生成继续执行。真实Swift仍严格UTF-8解码，损坏源码继续报错；没有errors=ignore/replace或吞异常放行。

资源文件不转换、不删除、不从facts/obligations或AC分母排除。plist元数据沿用现有analyze的plistlib.loads(read_bytes())，兼容XML及二进制；resource_locator仍只是定位证据，不自动升级为内容/行为验证。预览样式字符串或伪造skip-list不能免除资源义务。源摘要变化仍使图失效。

## 验证范围

新增test_resource_preview_routing覆盖真实binary/XML plist及binary entitlements/xcprivacy/stringsdict，并验证.m/.mm/.h与二进制plist共存时的源码识别、精确写操作锚点和完整义务集合，保留后续资源条目的完整缺口、源过期和report-only不写。既有Swift Preview及精确排除回归继续执行。原始红灯与绿灯日志保留在包外发布证据目录。最终计数见 docs/reports/release-validation-0.9.4.json 与对应ZIP冒烟收据。

整包回归：898项测试、1541个子测试通过，76项按既有条件跳过；11项发布检查与0.9.3→0.9.4升级检查通过。之后仅追加OC集成回归，相关90项测试、52个子测试通过；最终ZIP再执行安装态回归。首轮测试副本继承macOS隔离标记，原生调度器被系统终止；仅清理临时副本标记后原失败用例及全量回归通过，日志一并保留。

当前项目只读复查：2431项义务/映射；2360项缺失AC全部出现在报告中，UTF-8解码异常为0。整体仍FAIL（另有31原生unknown、18提取未决），没有修改项目、安装副本、findings或三账本。数字只描述该次当前快照，不能当作业务完成率。

## 升级

按 [INSTALL](INSTALL.md) 执行安装/升级。版本字段统一0.9.4；安装器仍拒绝覆盖用户编辑。source_scope与ios_harness现纳入冻结工具revision，既有在途任务先按既有协议收口或明确失败终止，再审阅/replan。不能改hash、改PASS或直接删除旧账本绕过。

本次不自动更新同时迁移中的工程；该线程应在适当检查点固定新版本，再重跑source-check --harness。修复UTF-8异常不保证其余源语义、AC、结构、HAP或设备行为通过。

测试与ZIP冒烟限本机macOS arm64；Windows/Linux实机边界及通用source_build生产入口等0.9.3未完成事项继续保留。包内不加入真实项目源码、源SDK二进制、构建捕获或凭证。
