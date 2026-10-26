<!-- when: 生成或补齐 iOS baseline 时读取；topics: 公共合同、行为、目标接口、AC、下游消费 -->
# 可实施的迁移规格合同

## 阶段职责
Spec 确定现有行为、公共目标接口、关键映射、已批准差异与独立验收依据。Plan 分配任务、依赖、文件写权、装配和接线责任。Execute 在合同内实现，复杂功能定向回读源码。公开接口和值域在进入实施计划前确定，私有实现细节留给编码。

源事实、目标设计、批准差异分段。专业资料帮助理解源码，不能替当前应用修改行为。共享合同定义一次，feature 精确引用。

生成前加载 [产物合同目录](artifact-contracts.md)，按其作者、版本、适用条件、模板和消费者准备产物。核心机器字段由随包catalog/schema单源限定；MD解释内容深度与交接行为，Python核验已实现的结构/引用/时效，二者不能各维护一套规范。新项目采用spec_contract_version=2，历史兼容/升级按目录执行。

## 生成顺序
1. 固定源版本、target/configuration、入口、扩展与平台条件，披露实际构建范围未知。
2. 区分生产、Preview、测试、依赖和非目标平台；机器信号进入待审清单。
3. 沿真实事件→状态→服务→副作用→反馈建立行为模型，按完整能力分 feature。
4. 统一共享模型、组件、公开接口和生命周期，按 [动作合同](action-contracts.md) 固定异步/取消/共享副作用的即时效果与完成边界，核验目标能力并处理差异决策。
5. 按模板写 baseline 和具体场景 AC；长状态机/协议按 impl 指针分层。
6. 按 [独立内容复核](spec-content-review.md) 逐动作/逐页跨文档联读，finding交原owner返修、独立复查后运行spec-check、source-check --harness及原追踪/差异/覆盖检查，交付Gate C摘要。

不从 signal.kind 查一句通用期望直接发行最终 AC；生成器写入 reviewed 不能代替独立阅读。

## 主交付物
| 文件 | 合同 | 下游 |
|---|---|---|
| ui-manifest.md | 全局导航/主题/资源、页面/覆盖层/内部状态、共享组件归属 | 页面排期和父子装配 |
| ui/page_*.md | 源证据、结构/视觉、目标状态、交互/导航、映射、资源与接线 | UI 与状态/事件实现 |
| feature-index.md | 功能边界、优先级、依赖、complexity/tier/depth、页面 | Base/Slice 排期 |
| feature-base.md | 共享模型、默认值/单位/身份、适用存储/网络/事件/偏好/组件、跨栈基线 | 公共能力与各功能 |
| features/F*.md | 范围、数据流、服务层、实现映射、状态管理、对接点、AC | 实施和验收 |
| skip-list.md、source-coverage-report.md | 排除证据、源归属、覆盖分母与检查限制 | 防漏迁与范围复核 |
| spec/decision-ledger.md | 原则、批准差异、替代数据流、supersedes 与新AC | 决策消费 |
| spec/gate-c-summary.md | 版本、索引、实际检查、缺口和可排期范围 | 阶段交接 |

本表是主业务概览；全部MD/JSON伴随件、版本及冻结例外以产物目录为准。页面必须按模板填写组件层级、布局约束、ArkUI映射和资源引用核心表，不能只有章节名或一段布局概述。

无适用能力给源依据，不因模板包含数据库/网络栏目而发明能力。当前内容门禁检查全部产品主功能；stub 可以保留作分析输入，但未补齐就不能声称整个 baseline 可进入 domains 实施。

## 共享引用与目标锚点
一个主文件加明确引用的公共合同，应足以理解实施与验收范围。对接点写 page.handler→VM/Service→状态反馈，含参数、返回值、线程与释放责任。

外置合同在主 YAML 声明：
```yaml
contract_refs:
  - spec/baseline/feature-base.md#数据模型
  - spec/ref/target-contracts.md#服务层
```
路径是项目内 baseline/ref 下存在的 Markdown；片段是精确标题。允许传递引用，相关文件与决策账本按真实摘要冻结。主业务真源仍是 Markdown；现有事实/语义/覆盖与 requirements-index 保持消费者路径。

目标 Owner.method/Owner.state 在受支持的服务/目标接口、实现映射目标列或页面目标状态列中明确声明；表头须紧随真实分隔行，逐表固定目标列。源列、普通源说明、代码围栏和数据单元格中的“目标/status”等词不能声明目标或重新决定列位置；AC 仅引用，不在自身创造目标。不要机械拼 feature 名与 file/body。文档描述目标类或组件时也需有明确的目标映射。

核心章节与被精确引用的标题须可唯一定位；同名节含相反行为时先诊断歧义并交原作者合并或消歧，不静默取最后一节。独立内容复核判断输入、处理、可观察结果和错误/取消是否完整及符合源码，不以会话短语是否出现代替语义判断。

action-contract/action-use将共享行为归属与引用显式化，机器核验ID、字段和引用关系；自然语言是否忠于源码、UI投影是否改变完成边界仍由独立联读裁定。消费者发现冲突回原owner，不能现场任选、悄悄重定义或以目标实现反向修规格。

## AC 与原生语义
每条 AC 写前提、事件/输入、具体期望，附源/批准决策→标、判定方式、独立真值。判与真使用分开的反引号段。主文件保留全部 AC，ID 不回收；同构参数可以分组，不同分支不能藏在“其余N处见源审阅”。AC 数量由行为决定。

SwiftUI 写身份、持有/借用、Binding/Environment、modifier 顺序、任务取消和状态重建；UIKit 写生命周期、约束、delegate/action 及桥接释放。Optional、值/引用、错误、actor、资源只展开影响行为的部分。声明式结构来自真实源码，无 XML 时不伪造；无设备记录 screenshot=null/runtime=not_run。

## Preview 审阅排除
保留原 facts/obligations。#Preview 或 PreviewProvider 的精确区间可以在原 ios-coverage mapping 写 ac_ids=[]、disposition=preview-only、source_sha256=该文件真实摘要、skip_ref=spec/baseline/skip-list.md#Preview，并保留完整 source_review（status/input/processing/observable/reviewer）。skip-list 的该节须点名源相对路径及理由。

只有区间、当前哈希、审阅与排除说明均相符，harness 才记录 excluded_obligation_ids，plan 才可略过该非产品义务。生产代码、错误摘要、未知条件编译仍阻断；不能仅凭文件名排除整个文件。测试源码可作为独立 oracle 留存，不冒充产品 AC 或目标测试成功；此 Preview 规则不自动放行任意测试路径。

## 升级与边界
旧 baseline 保留 ID；补齐合同，重提 facts/literals、复核专业资料与源门禁，再显式 replan，不继承旧 PASS。import 不再生成伪持久化义务，旧图由工具重提取，不能手改。

Spec进入profile 2冻结后，仅catalog指定两张核心索引表的合法稳定ID行、“状态”进度单元格及白名单受管进度块可变，精确边界见 [Plan交付合同](../../a2h-plan/references/plan-delivery-contract.md#状态解释)。其它业务表即使有status列也全文冻结；范围、owner、依赖、归属和结构变化先复核再显式replan。

spec-check 只读，不更新 findings；source-check --harness 包含内容检查并更新原门禁 findings。排查旧规格或审阅候选修改时使用 `source-check --harness --report-only` 只读诊断，诊断失败仍须修复后过正式门禁。程序检测结构和有证据的反例，不证明全量语义等价；编译与行为验证仍须实际执行。
