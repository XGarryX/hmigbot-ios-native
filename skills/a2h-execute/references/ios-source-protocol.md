# iOS 执行输入与原目标闭环

Stage 0 用 ios-resources-convert；Stage 1 用 ios-ui-to-arkui/a2h-ios-converter；
Stage 2 继续原 Base 任务；Stage 3 继续 UI→VM→数据→接线→验证的顺序。
读取 source_anchors/source_anchors_ref、source_root 和 native facts。
SwiftUI/UIKit/Objective-C 的源语义由源 spec 保留，worker 不凭目标 API 名重写行为。
共享文件、placeholder、group/batch closer、apply_writeback、结构闭包、编译和认领账本
保持原 HMigBot 协议。计划只读；执行进展只进 brief/registry/manifest/index。
使用 native-source 主题/字面量输入，不能把未执行检查记为 PASS。
结构扫描能发现孤立 VM，却不能完整证明 handler 调用了正确业务；仍需独立行为验证。
