# 语义能力目录

当前审定 **93 项独立可核验能力**。这里按明确目的、输入对象、输出证据和失败保证计数；来源、命令、包装器、平台后端、62 条检查清单及 96 技能/29 角色资源不重复加总。聚合入口列为非计数编排。

编译成员与预处理依赖虽沿用旧字段 source_files，受不同版本合同解释，分别登记；配置读取与目标构建、迁移轴报告与四项验证报告分别登记。Swift/ObjC/条件/资源 facts 共用一个引擎；两种候选入口共用一个内容生产器。

每项的唯一实现、旧别名、目的/证据保证、需求编号及回归路径见 [机器目录](../../src/hmigbot_ios/semantic_capabilities.json)。完整计数只取该目录独立 ID 去重，不取下表别名数量；本地合并审计台账与验收过程记录不随仓库提交。

| Canonical ID | 语义名称 | 阶段 |
|---|---|---|
| `source.snapshot` | 源内容快照 | all |
| `runtime.capability-discovery` | 宿主与工具能力诊断 | init |
| `runtime.preflight` | 所选动作准入 | init |
| `runtime.entry-permissions` | 受控入口执行位准备 | init |
| `runtime.quarantine` | 项目隔离属性修复 | init |
| `runtime.execution` | 原生载荷运行 | all |
| `runtime.timeouts` | 子进程时间界限 | all |
| `source.project-survey` | 源工程概览 | spec |
| `source.project-membership` | 工程声明成员识别 | spec |
| `source.dependency-inventory` | 依赖声明盘点 | spec |
| `source.compile-membership` | 实际编译成员识别 | spec |
| `source.conditional-evidence` | 预处理依赖及生效文本核验 | spec |
| `source.build-settings` | Xcode生效配置读取 | spec |
| `source.swift-syntax` | Swift原生语法采集 | spec |
| `source.clang-ast` | Clang原生AST采集 | spec |
| `source.interface-builder` | IB结构与连接采集 | spec |
| `source.asset-inventory` | 资产及变体盘点 | spec |
| `source.localization-inventory` | 本地化目录读取 | spec |
| `source.asset-conversion` | 资产资源转换 | execute |
| `source.localization-conversion` | 本地化资源转换 | execute |
| `source.reading` | 格式与源坐标服务 | spec |
| `source.facts` | 源事实与义务提取 | spec |
| `source.literal-inventory` | 原始源字面量提取 | spec |
| `source.manifest-evaluation` | 清单真实工具求值 | spec |
| `source.mcp-evidence` | 源只读MCP证据采集 | spec |
| `source.expertise-integrity` | 专业资料完整性核验 | spec |
| `source.expertise-review` | 项目专业资料审阅合同 | spec |
| `source.provider-attempts` | Provider采集尝试管理 | spec |
| `source.reviewed-refresh` | 受审源索引刷新 | spec |
| `spec.content-contract` | 规格内容合同检查 | spec |
| `spec.responsibility` | 源责任投影 | spec |
| `spec.coverage-ownership` | 产品义务AC归属核验 | spec |
| `spec.object-discovery` | 规格对象集合核验 | spec |
| `spec.finding-identity` | 提取诊断稳定身份 | spec |
| `spec.content-rendering` | 未审规格初稿渲染 | spec |
| `spec.content-commit` | 候选受控创建 | spec |
| `spec.authoring-review` | 原生语义作者候选核验 | spec |
| `spec.upgrade` | 规格合同受审升级 | spec |
| `spec.literal-projection` | 产品及历史字面量投影 | spec |
| `spec.coverage-report` | UI覆盖派生报告 | spec |
| `plan.contract-validation` | 计划与规格对应校验 | plan |
| `plan.ir-generation` | 原调度计划生成 | plan |
| `plan.prompt-scope` | 任务提示输入投影 | plan |
| `plan.input-validation` | 冻结输入去重校验 | execute |
| `plan.replan` | 受审重排 | plan |
| `plan.projection` | 计划派生视图 | plan |
| `execution.dispatch` | 原内核任务派发 | execute |
| `execution.landing` | 原内核回执落账 | execute |
| `execution.recovery` | 阻塞任务受审恢复 | execute |
| `execution.usage-budget` | 用量及全程预算 | all |
| `execution.join` | 并行工作结果汇合 | execute |
| `execution.target-build` | 鸿蒙目标构建 | execute |
| `target.build-diagnostics` | 鸿蒙构建日志诊断 | execute |
| `execution.migration-report` | 迁移证据轴汇总 | execute |
| `verify.scope` | 验证范围归一 | verify |
| `verify.behavior` | 行为效果链核验 | verify |
| `verify.report` | 四项验证报告 | verify |
| `verify.oracle-comparison` | 独立源目标观察比较 | verify |
| `workflow.evidence-workspace` | 迁移证据工作区管理 | init |
| `workflow.agent-packet` | 代理任务证据包 | spec |
| `target.project-scaffold` | 目标工程骨架生成 | execute |
| `target.closed-grammar-generation` | 闭合SwiftUI子集草稿转换 | execute |
| `cloud.source-build` | 源构建准备及采集 | spec |
| `cloud.dispatch` | 显式云构建派发 | spec |
| `cloud.fetch` | 云证据下载校验 | spec |
| `source.evidence-package` | 源证据封装与校验 | spec |
| `source.capture` | 显式外部观察采集 | spec |
| `verify.ipa-inspection` | IPA内容检查 | verify |
| `distribution.upgrade` | 安装升级回滚 | init |
| `distribution.package-integrity` | 源码包完整性 | retrospect |
| `distribution.release-audit` | 发行合同核验 | retrospect |
| `target.static-lint` | ArkTS静态声明核验 | verify |
| `target.slice-wiring` | Slice接线闭包核验 | verify |
| `target.assembly` | 目标装配语义核验 | verify |
| `target.binding` | 目标绑定门禁 | verify |
| `target.dead-shell` | 空壳实现门禁 | verify |
| `target.carrier` | 交互载体门禁 | verify |
| `target.hit-test` | 命中区域门禁 | verify |
| `target.resource-names` | 资源名称门禁 | verify |
| `target.literal-readiness` | 目标字面量就绪核验 | verify |
| `target.icon-sizing` | 图标尺寸核验与受控修复 | verify |
| `target.capability-ledger` | 目标能力接线账本核验 | verify |
| `target.writeback` | 实现回写合同核验 | verify |
| `spec.source-provenance` | 源索引及文档源归属 | spec |
| `spec.native-claims` | 原生事实声明核验 | spec |
| `spec.obligation-coverage` | 义务覆盖完整性核验 | spec |

目录计数不等于项目验收通过：Windows 原生、目标 HAP 与设备业务验证分别记录实际结果；已验证范围以各轮本地保存的当前验收记录为准，缺失证据保持未验证。

## 共有兼容合同补充

最后核查公开调用时，另补入既有身份配置、唯一源路径解析、旧显式任务包草稿/绑定/交接、草稿完整性和通用事实引用核验七项。这些是原来就能调用的不同对象合同；未重新启用已拒绝的工具版本或路由，也不增加另一套主控流程。

| Canonical ID | 语义名称 | 阶段 |
|---|---|---|
| `runtime.project-identity` | 源目标身份配置 | init |
| `source.path-resolution` | 唯一源路径解析 | spec |
| `source.contract-draft` | 源功能任务包草稿 | spec |
| `distribution.external-binding` | 旧外部工具绑定完整性 | init |
| `execution.legacy-handoff` | 旧显式合同任务包交接 | execute |
| `target.draft-integrity` | 草稿源与产物完整性核验 | verify |
| `source.fact-provenance` | 通用事实引用合同核验 | spec |
