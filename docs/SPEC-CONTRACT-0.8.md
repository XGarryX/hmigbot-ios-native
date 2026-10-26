# 0.8.0 规格内容合同

## 目标与来源
以原 HMigBot spec 的行为保持、UI/功能对接、共享定义、稳定追踪和有证据的范围为基础，按 plan 的接口/接线消费与 execute 的目标锚点/定向源码阅读要求改造。软件设计采用行为/接口合同、独立期望与单一业务真源；声明式源结构不需要伪造 XML。

## 实际实现
spec_contract.py 读取权威 Markdown，检查主文档/调度元数据、功能正文、目标符号、页面目标状态、精确共享引用、AC期望/延期和import/Preview真值。spec-check只读；source-check --harness汇入原findings。既有专业资料、原生语义、事实覆盖、原索引与原校验继续执行。

source_scope.py 是保守词法Preview区间定位器。原机器图和义务保留；仅preview-only审阅、当前文件摘要、精确区间和skip-list相符时允许无产品AC，报告excluded_obligation_ids。生产信号不能借此排除，plan仅消费已通过harness的集合。

domains冻结决策账本及contract_refs传递依赖。执行进度索引继续遵循既有可变规则；精确路径spec/baseline/plans/resource-mapping.md属于资源任务输出，仍受文件写权和真实回执哈希检查，不能借例外修改其他规格。

## 规程与交付
详见[交付合同](../skills/a2h-spec/references/spec-delivery-contract.md)和[内容复核](../skills/a2h-spec/references/spec-content-review.md)。维护功能/UI/Base/manifest及Gate C模板，接入spec、plan、execute和原生UI/功能分析入口。

## 验证方法
新增正负例先失败再实现：完整合同、薄规格、目标未定义、源状态冒充目标状态、静态/Preview范围、延迟断言、缺期望、坏共享引用、传递冻结与执行可变边界。既有原生harness及原消费者回归、完整工具测试、资源字节审计、技能检查和独立ZIP安装检查分别记录在发行验证产物。

独立前向评估从tests/fixtures/uikit_interaction原始源码，在临时工程生成1页、1功能、9条具体AC和27条义务映射，实际通过spec-check、source-check --harness、addenda、divergence、literals与traceability六项检查。按公共模板复现的共享接口误拒绝已由回归测试覆盖；UI清单补齐plan读取的目标文件、优先级、confidence和状态字段。

评估还实际构造了错误Add期望和缺少Reset对接链；机械检查均未发现。独立内容复核必须逐事件检查具体运算结果和接线，不能用这些PASS替代源码理解。评估未执行目标构建或设备操作。

## 升级与限制
保留旧page/F/AC/决策ID；补全合同后重提facts/literals、审阅资料、源门禁及显式replan。改变提取规则会让旧图失配，不能手工改图或继承旧PASS。原版兼容source-check仍仅为兼容检查，不能绕过--harness。

内容门禁基于明确格式和已知反例，不验证任意自然语言结论。Preview定位不是完整AST或有效构建分析；条件编译、动态绑定和外部二进制仍需证据。生产与预览同一行等无法区分的情况保持保守，不能宣称自动覆盖所有语言形态。本轮交付工具能力，不重写既有应用baseline，也不代表完整App编译或双端验收。
