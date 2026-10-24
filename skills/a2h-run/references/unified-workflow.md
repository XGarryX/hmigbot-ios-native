# 单一转换流程与公开调用映射

统一阶段为 init → spec → plan → execute → verify → retrospect。execute 内保留资源 → UI → Base → Slice → 结构/终态编译，派发继续使用原 next-batch → 执行 → v2 receipt → land-results。owner 与三账本写者不变。

## 环境准备

先核对源/目标路径与既有身份。复用本会话已确认路径和授权；只有真实身份冲突或缺失输入需要确认。明确选择用量目标时，在必要环境准备之前启动 usage-start；等待、重试、spec、构建与验证都属于同一次计时。保留预算 schema 1/2、真实计费和 UNKNOWN；耗尽仅阻止新派发，不阻止回收。

配置身份后，先执行 `init-environment --project <target>` 只读盘点。一次说明受控入口执行位、已发现 quarantine、临时目录及各能力缺口；在已有授权内执行 `init-environment --project <target> --prepare`。输出为 `spec/reports/init-environment.json`，包含实际动作和剩余问题。仅项目内托管 runtime 的明确清单可修复，外部 checkout 只能检查，需要时走已授权安装。执行位和隔离属性分别处理；不操作源代码、HOME、系统目录或任意用户脚本。

单独调用 spec/plan/execute/verify 同样复用这一步准入。后续 helper 只检查，不再隐式 xattr/chmod 原 runtime；失效时返回 init-environment 恢复路径。ASCII 临时副本执行位是短期运行布局的一部分，不能据此修复外部来源。doctor 仍只读。

源可读、Xcode 原生采集、目标构建、设备验证分别报告。缺目标 SDK、设备或 MCP 不阻断可行源分析；也不把静态结果当成已请求的原生证据。Xcode 许可、TCC 和设备信任由系统/用户完成，不伪造批准。

## spec 与候选写入

Provider 采集属于 spec。build-settings 的旧调用有 config 时只消费 config，无 config 时消费冻结 input。未消费 input 不参与预检或身份；完整计划预检在任何 Provider 启动之前完成。失败保留原件，新 attempt 不覆盖旧成功，成功前核对实际消费字节和当前源。

facts 保留其已定义的 spec 生成动作。source-analysis 默认只更新机器事实、字面量、候选与回执；spec-scaffold 默认纯预览。二者使用 gate_artifacts 的同一内容渲染器；显式 apply 只创建允许范围内缺失的未审 MD，不批准 AC/语义。main 的 feature-base、API 模板和稳定页面 ID 规则为权威。旧 schema 1 候选安全拒绝，提示重生成；schema 2 重算内容并验证所有路径，失败只回滚本调用仍未改动的文件。正式合同与源审阅保持原 owner。

发现并提前披露的 WF14：旧 main 的 harness-init CLI 会附带 spec 初稿生成；这与 init 不写业务 baseline 冲突。统一后 harness-init 只写既有 harness 标记，初稿留在 facts/gate-artifacts 的 spec 动作，显式 import-legacy 保留原导入边界。

## verify 明确范围

CHECK-1/2 固定，CHECK-3 视觉和 CHECK-4 UT 可选，沿用 main 编号、相对顺序与四项整体判定。旧 main 附加行为请求、旧 git CHECK-5 都映射同一个 behavior 范围；不按包来源切换流程。已有明确选择直接使用，旧工程记录不明为 pending，不从“全部”或历史 PASS 推断行为授权；只询问缺少的范围。

behavior-check 仅在 behavior 明确选中时调用；真实 `--run` 还需已有授权且具备独立源 oracle。结果独立报告，不加入四项整体计算。未选不启动，不读取旧行为结果当本轮执行。verify-report 由命令单写，verifier 的当前输入/证据通过 verify-results.json 绑定；四项通过不等于业务或 UI 完整等价。

## 升级与证据

在途任务先经原完成、回收或受审终止协议结束，再升级工具。冻结 revision 覆盖读取、语言、候选、责任、Provider 和实际 helper；变化后按原复审/replan 恢复，不能继承旧 PASS。源索引、作者 Spec/AC、责任/语义/覆盖、决策账本、预算及原三账本保留。只归档已核验 marker/形状的机器输出。

编译成员与预处理依赖是两个证据对象；旧 source_files 按版本解释，不能互相替代。源采集、鸿蒙目标构建、行为/设备结果分账。
