# 0.6.0 实现与验收边界

本版把 iOS skill 的关键约束落入程序：机器源信号→覆盖义务→稳定 AC→冻结任务→真实文件回执→独立观察。五阶段公共规格、indexed 计划和原 ArkTS 实施/验证资源继续复用。

## 实际实现

| 部分 | 实现 | 验收范围 |
|---|---|---|
| 源事实 | ios_facts.py、ios_rules.json，四类 facts-view，工程/依赖/资源及 token/XML 信号 | 可重提取、不可手改、稳定 ID、片段/文件摘要和范围 |
| 源工具接入 | facts --providers，复用 SwiftSyntax/Clang/build-settings/IB/资源原子操作 | 实际 provider 产物与源摘要绑定，失败留档；不自动宣告符号已绑定 |
| 源字面量 | ios_literals.py，literals 与原 extract_literals 入口 | 真实源文本、插值、数字、尺寸线索、符号色与摘要；不把未解析单位/色值猜成已知 |
| 原生事实与义务 | ios_harness.py + 原 native_semantics checker | NA 与信号矛盾、错误状态初值、无关行号、遗漏义务、弱 oracle 均阻断 |
| 计划 | typed request→原 a2h-2.1.0 plan IR，具体 ownership、DAG、fact/AC、决策 | 全 AC 与义务有 owner，禁止控制文件所有权、通配、重叠和依赖环；正文与输入冻结 |
| 四拍控制 | 字节不变的 CodeX 1.7.0 next_batch/land_results/state_update 与 _wavelib | 派发、在途等待、回执、落账、重复落账、重排与不继承旧成功 |
| 执行约束 | 真实输出摘要、派发前后文件差异、原 receipt schema + iOS v2 receipt | 越界文件、缺产物、假 PASS、过期回执、任务书修改拒绝 |
| 行为检查 | behavior.py；事件链、存储链、独立 expected、实际进程观察与 target hashes | 空处理器失败；未运行/未覆盖为 UNVERIFIED；真实运行后比较所声明用例 |
| Skill 配套 | 七个 portable 入口、四个专业规程、共用协议、映射参考、provider/receipt 示例 | 各公共入口可安装、参考可读取、控制面命令可执行 |
| 恢复 | import-legacy、source-refresh、replan，history 保留原图/旧索引/三账/计划 | 明确复核、禁止在途重排、旧 PASS 不继承，源码/计划修改后需重新验收 |

实际控制面采用 **1.7.0 选定调度组件 + 自编 iOS 适配器**。314 个原文件按 archive 清单校验，vendor/hmigbot 的 3,516 个 1.6.1 资源继续保留。没有宣称整套 1.7.0 spec/plan 前端已原样移植；原生成器的源平台依赖不能直接用于原生 iOS。

Windows 冻结程序的嵌套调用所需 python.exe 未随上游组件提供。适配器在临时目录复制不变的核心载荷，并加入当前宿主解释器，保留上游状态算法和 vendor 摘要；不修改宿主系统或原包。当前自动验收覆盖 Windows x64；macOS arm64 资产存在，但本轮未实跑。其余平台缺核心发行资产时明确失败。

## 使用顺序

先配置分离的源/目标，再 harness-init（旧版用 import-legacy）、source-index、facts、facts-view。模型依据完整源链填 ios-semantics v2 与 ios-coverage，运行 source-check --harness；然后原可读计划→plan-ir→next-batch/receipt/land-results。具体字段和命令见 [可执行协议](../skills/ios-source-analysis/references/harness-v2.md)。

源码变化时，facts 归档旧图并重提取。用 source-refresh --review 提交 reviewer/reason/previous_source_sha256/source_sha256，归档旧索引；这不表示 spec 完成，仍需重审 coverage/semantics 并过门。replan --input 需 replan_review，保留全部旧控制产物并开始新 run；有效文件可以重新核对后复用，旧状态不直接搬成成功。

状态区分：source contract PASS、task generated、compiled、declared behavior observed、device verified 是不同证据。四拍的 done 只表示代码任务已落账。目标构建继续通过原真实 assembleHap/HAP 检查；未提供当前 SDK、账户或设备时不生成构建/设备通过。

## 限制

词法信号没有完整 Swift/Objective-C 符号绑定能力，也不是 SwiftUI runtime tree 或 Auto Layout 求解器。任意业务自然语言是否正确仍需要独立源审阅。Xcode 构建成员、条件编译、宏、动态派发、二进制 SDK 和复杂泛型必须走实际工具或保留未知，不能通过目录白名单消除义务。

独立 source_review 与 oracle 的字段及摘要可检查，评审人的判断与外部设备数据真实性仍需独立复核。任何进程 stdout 恰等于 expected 都只证明该进程的声明观察；不能据此扩大为整 App 等价。测试报告限定实际 AC、目标摘要与执行范围。

本轮使用隔离片段夹具及独立使用评估验证工具控制协议；未完成指定真实 App 的双端迁移、Apple 构建、鸿蒙 HAP 或双端设备验收。发行检查报告、日志、ZIP 校验与安装冒烟分别留存，不以文档补写完成标记。
