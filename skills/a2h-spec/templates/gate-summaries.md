# 原生规格交付摘要

以下是报告模板，阶段结束不自动要求重复授权。已有全流程授权则继续；仅真实未决产品选择需要确认。

## Phase A 工程事实

| target/configuration | 语言 | UI 框架 | 入口 | 编译成员证据 | 未知项 |
|---|---|---|---|---|---|

列源码根、版本/指纹、依赖、app/extension、源工具是否实际执行。
静态推断、Xcode 已解析、源已编译、设备已观察分别列出。无截图不能写已采集。

## Phase B 页面规格

| page ID | 源符号 | SwiftUI/UIKit/IB | 状态与交互 | 语义文件位置 | 缺口 |
|---|---|---|---|---|---|

报告 ui-manifest、分页 spec、资源索引与源证据。说明 modifier 顺序、状态所有权、
Binding/Environment、controller 生命周期、布局约束、事件和导航是否逐项核对。
source-check 只检查结构和溯源；UI 分析 skill 另做入口/状态/事件覆盖审查。

## Phase C 功能与验收

| F-ID | 行为链 | AC | 独立真值 | 判定强度 | plan 约束 | 缺口 |
|---|---|---|---|---|---|---|

列 feature-index/base、api-inventory、decision-ledger、ios-semantics 与实际检查报告。
记录 addenda/divergence/traceability/source-check 的命令、退出码、日志路径；未执行写 not_run。
列未经覆盖的源文件、unknown 原生事实、需运行采证的分支和有依据的跳过项。
每个平台差异列 PD/D-ID、supersedes、emits 与批准来源；不得把未决项涂成通过。
静态检查通过只表示该检查范围通过。核心未知事实回到源分析，运行待验交验证阶段。
