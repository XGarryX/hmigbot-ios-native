# 单一转换流程与公开调用映射

统一阶段为 init → spec → plan → execute → verify → retrospect。execute 内保留资源 → UI → Base → Slice → 结构/终态编译，从 execute 起按 [执行交界合同](execution-boundary.md) 使用 Garry indexed 阶段、closer/writeback 与原始宿主日志 join。旧 v2 三账本只用于原合同收尾/恢复，不能并跑两套执行调度。

## 项目进度位置

当前转换的可读进度固定为 `<target>/spec/reports/ios-progress.md`，各阶段沿用同一文件，不在用户级 `.codex`、工具源目录或其他应用目录另建临时进度。实际调用的阶段、结果、步骤计数、问题、证据位置与恢复条件由当前运行更新；原始证据和控制账本仍沿用项目内既有路径。该报告不作为正式合同输入，不因缺失或更新而阻塞转换；只读 `doctor`、`plan-check`、`--report-only`、`--plan-only`、`--check` 保持只读。

主控在每次交接和交付时给出此项目进度文件路径。直接调用的领域引擎没有通过本CLI时，主控依据实际返回更新该文件中托管区之外的交接说明，不把未执行项记为完成，也不复制工具维护/发布记录到应用转换进度。已有用户备注保留。

## 环境准备

先核对源/目标路径与既有身份。复用本会话已确认路径和授权；只有真实身份冲突或缺失输入需要确认。明确选择用量目标时，在必要环境准备之前启动 usage-start；等待、重试、spec、构建与验证都属于同一次计时。保留预算 schema 1/2、真实计费和 UNKNOWN；耗尽仅阻止新派发，不阻止回收。

配置身份后，先执行 `init-environment --project <target>` 只读盘点。一次说明受控入口执行位、已发现 quarantine、临时目录及各能力缺口；在已有授权内执行 `init-environment --project <target> --prepare`。输出为 `spec/reports/init-environment.json`，包含实际动作和剩余问题。仅项目内托管 runtime 的明确清单可修复，外部 checkout 只能检查，需要时走已授权安装。执行位和隔离属性分别处理；不操作源代码、HOME、系统目录或任意用户脚本。

单独调用 spec/plan/execute/verify 同样复用这一步准入。后续 helper 只检查，不再隐式 xattr/chmod 原 runtime；失效时返回 init-environment 恢复路径。ASCII 临时副本执行位是短期运行布局的一部分，不能据此修复外部来源。doctor 仍只读。

源可读、Xcode 原生采集、目标构建、设备验证分别报告。缺目标 SDK、设备或 MCP 不阻断可行源分析；也不把静态结果当成已请求的原生证据。Xcode 许可、TCC 和设备信任由系统/用户完成，不伪造批准。

初始化与直接进入 spec 均消费 `capability_choices`。首次 pending 必须由主控展示中文选项和权限差异并收取开发者选择，不能只读取 options JSON 后自动跳过；这不受阶段内“无额外交互”约束。已有明确选择和授权直接沿用。未选择只暂缓 MCP 调用，独立 CLI 继续；不能将沉默记作选择 CLI，也不能把受限进程的 disabled 认定为宿主开关关闭。选择 MCP 后先核对真实可见性、目标工程和 agent 授权，工具不自动修改系统设置。

## spec 与候选写入

Provider 采集属于 spec。build-settings 的旧调用有 config 时只消费 config，无 config 时消费冻结 input。未消费 input 不参与预检或身份；完整计划预检在任何 Provider 启动之前完成。失败保留原件，新 attempt 不覆盖旧成功，成功前核对实际消费字节和当前源。

facts 保留其已定义的 spec 生成动作。source-analysis 默认只更新机器事实、字面量、候选与回执；spec-scaffold 默认纯预览。二者使用 gate_artifacts 的同一内容渲染器；显式 apply 只创建允许范围内缺失的未审 MD，不批准 AC/语义。main 的 feature-base、API 模板和稳定页面 ID 规则为权威。旧 schema 1 候选安全拒绝，提示重生成；schema 2 重算内容并验证所有路径，失败只回滚本调用仍未改动的文件。正式合同与源审阅保持原 owner。

发现并提前披露的 WF14：旧 main 的 harness-init CLI 会附带 spec 初稿生成；这与 init 不写业务 baseline 冲突。统一后 harness-init 只写既有 harness 标记，初稿留在 facts/gate-artifacts 的 spec 动作，显式 import-legacy 保留原导入边界。

## verify 明确范围

融合版统一七项编号：CHECK-1 编译、2 静态、3 占位、4 身份、5 页面、6 路由、7 视觉/运行；稳定语义 key 与独立 Git 旧五项的对应见 [编号与范围合同](../../a2h-verify/references/check-keys-and-scope.md)。不因当前合同文件有无将同一个编号解释成另一项能力。

默认检查基础 1–4；已有真实页面/导航输入时加入适用 5/6，显式 scope 可选择子集。无适用占位清单可由当前检查证据给 N/A，身份未确认保留提示/待确认。CHECK-7 与行为/设备执行只按明确选择和已有授权调用；指定应用的截图、控件查询和固定回放与桌面远控分开，选择不授予桌面接管、录屏或未指定设备权限。

报告总能生成。所选检查的实际 PASS、FAIL、DEFERRED、NOT_APPLICABLE 与未选项分别记录；基础范围通过不代表完整迁移等价。已绑定真实失败不会因未选择该项被隐藏。同签名原始证据跨阶段共享，只有实际相关输入/配置/规则变更才重验。

## 升级与证据

在途任务先经原完成、回收或受审终止协议结束，再升级工具。冻结 revision 覆盖读取、语言、候选、责任、Provider 和实际 helper；变化后按原复审/replan 恢复，不能继承旧 PASS。源索引、作者 Spec/AC、责任/语义/覆盖、决策账本、预算及原三账本保留。只归档已核验 marker/形状的机器输出。

编译成员与预处理依赖是两个证据对象；旧 source_files 按版本解释，不能互相替代。源采集、鸿蒙目标构建、行为/设备结果分账。

当前交付的原生执行 payload 选择 macOS ARM64；Intel/macOS-x64、Windows 的运行验收记 deferred/not_tested，保留兼容入口而不纳入该主线计划冻结。切换执行平台须显式重建合同并验证对应运行程序。


> **当前发行边界：旧设备/视觉后端延期，官方应用测试单独取证。** `arkts-scenario-runner`、`arkts-visual-verify`、`arkts-ui-verifier`、`ios-screenshot-analyzer`（及历史 Android 截图别名）和 `scenario-builder` / `visual-fixer` / `visual-fixer-reviewer` 尚未恢复交付，不调用或要求补装这些旧后端，也不因其缺件阻断基本转换/构建/报告。指定应用/模拟器的官方截图、控件查询和固定回放按执行交界合同及实际适配入口运行，不因旧后端延期或缺少桌面屏幕权限一概记 not_run。许可、宿主可用、已实现、实际执行与验收结果分开；缺真实后端/输入仅限制对应检查。外部原始证据核对版本、配置、范围和来源，未执行不记 PASS，真实产品失败保留。下文旧调用/目录仅为兼容映射。



0.13.5 的全流程实际耗时、并发、等待、返工及质量一致性比较按 [实际计量](execution-measurements.md) 执行：范围固定后启动run，沿真实调用记录，最终生成summary.md；缺可比基线不宣称提速。
