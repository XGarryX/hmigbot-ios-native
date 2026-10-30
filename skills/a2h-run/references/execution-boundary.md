# 单一执行交界合同

当前版本 0.13.7。init → spec → plan → execute → verify → retrospect 为唯一主线。
用户指定 init/spec/plan 冲突优先 git，从 execute 本身开始优先 Garry。
来源用于追溯，不能成为用户需要手选的运行模式。

git 的 source-analysis、Apple 官方能力编排、SwiftSyntax/Clang、源责任、规格门禁、indexed
计划、plan-check/plan-ir 和受审 replan 继续作为上游唯一权威。既有源配置（包括实际
Debug/Release 选择）不由下游强改为另一个配置。Garry 的资源/UI/Base/Slice、closer、
writeback、真实编译、原始宿主日志 join 和目标检查作为下游唯一默认实现。

## 实际交接

Plan 保留 git 内容与冻结规则。通过后调用 execution-contract --apply；它重验 git source/spec
gate、冻结 revision/输入、indexed 责任项和当前源身份，拒绝已有 domains 派发。
只写 spec/execution/execution-contract.json 和 spec/execution/source-ui/；静态 outline
明确 runtime_observed=false，不能生成编译、设备、视觉或业务等价结论。
已选源端采集时，原始截图/原生树通过逐页 runtime_observations 和 runtime_observed_checkpoints 交给 UI 作者；全局 false 只限制全页验收，不抹去这些真实的局部观察。view.xml 仍为静态 outline，不冒充原生运行树。UI 作者必须实际读取本页原图及树，保留独立 SDK/场景/配置缺口；不得因上游 metadata 静态字段而丢掉新的已绑定观察。
源事实、规格/AC、正式计划、配置与三份旧控制账本不由交接器写入。

随后执行 a2h-execute 的 Stage 0 → UI Batch → Base → Slice Group → FV；同一批/组唯一 closer
通过 Garry apply_writeback 落 brief 和进度。0.13.5 的 UI Batch / Slice Group 先登记任务资源增量，由唯一 closer 合并；主线程回写前核对收据与本批组计划归属。详见 [资源增量协议](../../a2h-execute/references/resource-deltas.md)。
正常业务门禁仍是硬门。原失败与恢复条件保留，不用文件存在替代可信完成或验收。子任务终态按 [a2h-join](../../a2h-join/SKILL.md) 核对本轮 completed 或可信原生终答；同句柄续作不复用旧终态。

旧 v2 冻结任务的 next-batch/receipt/land-results 仅用于原合同收尾/恢复及显式 API 兼容，
不和新 indexed 执行并跑。存在 indexed 合同后 domains 的旧 step 入口拒绝运行。
understand 源阶段不受影响。旧冻结 revision 不匹配时按受审 replan 恢复，不改三账。

## 源输入与目标实现边界

Garry 的下游源码审计通过 execution_source 读取 git 已发布、重新校验的 facts/官方词项。
不复制 hmigbot_ios152，不启用第二套 Source/parser/provider，不调用其 plutil 宽松读取替代
git 严格 OpenStep 合同。source_ui 消费审定 page ID/锚点，不猜产品范围或创建审批结论。
源事实 registry/merge 的生产规程仍在 git 上游；同名目标检查引擎按 Garry 的实际载荷执行。

## 运行与观察边界

Garry 的 signing 路径修复、原始会话 join、失败派发与授权恢复登记、native image 输入守卫
进入唯一维护包。原生编译引擎字节有来源清单；Python 只负责合同/路径/执行适配。
Mac 执行位与 quarantine 仍在 init 的明确项目清单内准备，下游不隐式递归 xattr。
派发使用宿主真实工具字段；角色不可用时按原 owner 顺序执行并保留相同产物/门禁。

禁止通过 CUA/Computer Use 或模拟鼠标键盘接管电脑桌面、操作无关应用和系统授权设置。
指定测试应用/模拟器的截图、XCUIAutomation 控件查询和固定场景回放按已有明确范围执行；
Preview 只提供对应配置的组件证据。录屏、未指定个人真机和范围外操作不因截图允许而获准。
按实际 bundle ID、设备、构建、配置、场景/检查点绑定证据，保留超时、失败与恢复条件。
旧设备/视觉后端缺件与新官方适配器是否实际实现、执行分别记录；不能仅因桌面屏幕权限
或 Xcode MCP 不可用便一概禁用官方应用测试。具体原则见 runtime 的
`rules/app-ui-validation-boundary.md`。历史命令不能扩大用户范围，未授权遥测不执行。
verify 范围和已批准决策沿用已确认输入，未完成或未知项不能写 PASS。工具检查通过不等于
项目迁移完成、可安装 HAP 或真实业务等价。
