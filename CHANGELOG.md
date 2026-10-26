## [0.13.4] Git/Garry 阶段能力融合

- init/spec/plan 的冲突实现由 git 主导，execute 本身及后续由 Garry 主导。
- 采用 Garry 的执行/收口规程、签名路径适配、原始宿主日志 join、失败派发/授权恢复和图标输入守卫；不复制第二套源解析包。
- 新增 execution-contract，实际校验并冻结上游输入，生成明确为静态的下游 meta/outline；拒绝混用两套 domains 调度。
- 源事实/官方能力链、预算、受审重排、所有权、安装事务和旧冻结任务恢复保持各自合同。新增来源与阶段机器目录，过程证据保存在工具包外。
- 本记录仅说明实现；真实测试、未验证平台与应用迁移结果分开交付。

# 0.12.0 — 2026-10-23（原生能力归一）

- 以原生 Xcode、资源坐标、ObjC、条件证据、责任及门禁内容为主，融合 Swift 边界/计算属性/identity、缓存、Provider attempts、预算、调度与 Windows 适配。
- 显式 init-environment 准备受控入口与隔离属性；运行时只读复核。候选预览与提交共用内容生产器，schema 1 候选需重生成，作者文件与原账本写权保持。
- 区分编译成员与预处理依赖；config 优先输入身份，未消费 input 不参与预检。明确行为范围，不扩大四项总体判定。
- 验收结果与平台未验证项另记，工具回归不表示应用迁移或设备验收通过。

# 0.9.7 — 2026-10-23（工具审计与责任投影闭环）

- 新增项目边界内按需隔离属性修复（含原launcher约束）与显式repair-permissions；升级前归档清理旧机器派生文件、失败回滚，保留作者合同/原始证据/控制账本。
- 二进制/XML plist 由真实格式解析器验证；语义证据使用实际资源坐标及字节摘要，坏资源继续阻断，Swift/OC 源码严格解码。
- 同一只读 source responsibility 合同贯通原生语义、typed claims、覆盖、活动目标 AC、计划、调度、动作和质量视图；保留源事实、历史义务/AC、私有 unknown 与普通应用责任。
- 批准替代核对原 helper 重建的 AC/决策、精确应用方法/公开调用、历史动作边界；支持合法混合目标动作但普通 app AC 仍需覆盖和归属。无可靠可达性证据的 unused_symbol 继续拒绝。
- 冻结审阅、决策、语义、页面锚点、构建/条件证据、责任载荷、原解析器与通用规则；候选不能直接授权派发，变化在落账前拒绝。
- UI 派生报告按精确源锚点登记，并展示全部复合类型；保留现有作者计划，不把文件存在或报告改善算作门禁通过。
- 修复安装冒烟实测发现的macOS同目录别名共享合同报错，目录根归一后保留完整传递依赖；新增目录别名回归。
- 新增工具/项目结果分离规程和托管 AGENTS 规则；工具回归、发布、安装、项目实测分别记录。安装与项目重跑见 [安装说明](docs/INSTALL.md) 和 [升级清理规则](docs/UPGRADE-CLEANUP.md)。

# 0.9.6 — 2026-10-23（Objective-C状态事实修复）

- 在0.9.5交付目录上保留资源路由、打包和安装修复，增加真实property/ivar状态事实。
- 保留owner/type/ownership、存储依据、零初始化与独立init/lifecycle赋值证据；未知宏、字符字面量等不支持语法显式阻断。
- 修复自定义setter、self遮蔽、属性宏、条件上下文边界，原typed消费者继续拒绝篡改和漏项，提取器纳入冻结revision。
- 工具回归与源事实核验不能替代业务覆盖、主工程构建或设备验收；完整边界见docs/objc-state-facts.md。

# 0.9.5 — 2026-10-23（本地目录交付修正）

- 直接维护hmigbot-ios-main，以该目录为唯一交付源；README主标题与四处版本字段统一0.9.5。
- 打包保留源目录名、文件内容、权限、ZIP精度的修改时间与空目录；新增根目录配置会随源树进入交付。
- 显式列出系统缓存与本地状态排除项；输出位于源目录外，链接与打包期间的源变化拒绝生成完成收据。
- 新增逐项源目录/ZIP/清单核对，安装冒烟从清单定位目录并验证，覆盖二进制资源及OC共存回归。
- 0.9.3优化与0.9.4资源读取修复保留在本目录；未自动更新迁移工程，未上传服务器。

# 0.9.4 — 2026-10-22（本地修复版）

- 修复 source-check --harness 对资源事实无条件UTF-8读取并扫描Preview的问题；只对Swift源文件执行支持的Preview词法区间识别。
- 规格汇总使用相同文件路由；plist/entitlements/xcprivacy/stringsdict等资源仍保留原事实、义务、AC与源摘要检查。现有plist格式分析器继续按字节使用plistlib解析。
- 增加binary/XML plist、完整后续义务诊断、伪Preview排除拒绝、资源变更过期、损坏Swift及report-only不写回归。
- 将source_scope/ios_harness绑定到冻结工具revision；已有冻结任务按原协议审阅/replan，不继承旧PASS。
- 当前迁移项目仅做只读诊断，未自动升级其安装副本或修改任何共享账本；本次修复不宣称业务迁移完成。

# 0.9.3 — 2026-10-22（本地发布候选）

- 整合工程中已验证的 pragma、路径/调度、Spec/Plan、能力接线、结构审计、失败恢复及证据报告优化；逐项来源和限制保存在当轮外置整合证据中。
- 选择性纳入 Clang 条件证据生产/回放/冻结及独立门禁诊断；保留未解析、不适用矛盾和过期阻断。
- 接入门禁文件自动生成、零 AC 诚实汇总、精确派生文件审计与 shell/PowerShell 参数透传。
- 修复 macOS 中文安装路径下原Nuitka检查器初始化abort，公共包装器统一ASCII临时执行位置。
- 修复 macOS 原落账内核的共享库/解释器冲突和结构检查器布局；不修改原二进制字节或三账本算法。
- 修复 Xcode 自动 AST 采集的 DerivedData/response 生命周期、失败构建拒绝及输出参数；真实 Clang 回归验证。
- 发行检查改用 pytest 收集全部测试；登记原包既有参考资料差异，保留上游摘要、无二进制字节变更。
- 本次验证范围为工具合同和本机安装/升级；不代表任何真实 App 的迁移、HAP 或双端行为验收。未上传服务器。

# 0.9.2 — 2026-10-17

- 精确识别Xcode自动自引用workspace、已知IDE检查缓存和直属xcuserdata；真实workspace引用、共享Scheme、锁文件、配置与源码继续使摘要过期。
- 新增只读spec-authoring完整清单与受当前源/MD摘要绑定的候选渲染；生成器与原门禁共享disposition schema、native维度/事实校验及源真值锚点规则。
- 同步Spec规程、模板、产物合同及续跑步骤；未知/缺失/重复/越界和NA矛盾继续拒绝，不改应用源码或放宽门禁。

# 0.9.1 — 2026-10-16

- 统一真实 Markdown 表格解析及目标列权限，处理相邻表、代码示例、行号/单元格跨度、核心标题歧义、缺件合并和显式未完成断言。
- 按 catalog 的核心节/表头/稳定 ID 精确投影进度，阻断业务状态、范围与归属变化，typed segments 消除原文占位符碰撞；同步 Spec/Plan MD。
- Swift 字符串保留完整 raw 分隔符、表达式和跨度，无法解码时标记 unresolved，不输出错误 value；同步资源消费 MD。
- 新增只读 spec-upgrade 和明确选择候选的受控应用，不猜语义、不自动切 profile 或继承 PASS。
- summary schema 2 逐页连接计划、原调度身份/落账、回执和当前输出；行为从本页 AC 原始观察推导；新增确定性 migration-report/--check，并在 Execute/Verify MD 实际调用。
- 增加边界反例、独立审查及中性真实构建/逻辑评估；实际业务工程和双端设备验收仍不在本次完成范围。

# 0.9.0 — 2026-10-16

- 以 MD 为主完善源分析步骤、正反例、页面组件/布局/ArkUI映射/资源表、共享动作单源、逐动作联读和原作者返修/独立复查；同步 Spec/Plan 模板、派发协议与角色。
- 新项目启用 spec_contract_version=2；catalog/schema 与实际只读检查器共同限定核心章节、表头、页面 meta、动作定义/消费及按需 JSON 引用视图；原 API inventory 服务协议保留。
- Plan 的 indexed MD、plan_items 投影与 typed task 对账 AC、页面、依赖、写权、范围及验证义务；冻结传递输入与工具合同版本，索引仅精确进度可变，禁止降级绕过。
- 执行任务注入精确合同闭包，未读 addenda 阻断受影响 AC；独立 FV 无全工程写权，修复回原责任任务；统一既有六种 placeholder kind。
- 新增 product-literals/spec-summary/plan-check；不覆盖 raw 字面量或三控制账本，不把历史 verified/brief PASS 当运行证据。编译和行为报告绑定当前源码、目标及规格摘要。
- 增加正反例回归、实际模型生成的旧/新规则样本及独立源复核。发行检查验证工具合同和安装使用；不宣称真实 App 双端设备验收。

# 0.8.0 — 2026-10-14

- 从原spec原则、下游plan/execute消费者和软件设计实践完善主规格、目标公共接口、状态/对接点与独立AC合同；保留原五阶段和三账本写者。
- 增加只读spec-check，并集成source-check --harness；检查正文、明确目标符号、UI目标状态、精确共享引用、延期断言及import/Preview真值反例。
- import不再生成持久化操作义务；保留Preview原始事实和义务，通过哈希、精确词法区间、审阅与skip-list验证非产品排除。
- domains冻结共享合同的传递依赖与决策账本，保留进度索引可写性，并将Stage 0真实资源映射留在执行所有权/回执检查中。
- 新门禁证明内容/消费者合同，不能证明全量语义或设备行为；旧baseline需补合同、重提事实并显式重排，不继承旧成功。

# 0.7.0 — 2026-10-12

- 固定并随包导入 AvdLee SwiftUI、Swift Concurrency 和 Axiom UIKit/内存主题，3 个 MIT 快照、87 个真实文件；逐文件来源和 SHA256 审计。
- 增加 expertise-plan/review：按真实源 token 路由、固定资料摘要、逐源文件观察与审阅记录；接入 source-check --harness 和 domains 计划冻结。旧 0.6.0 项目续跑需补审阅，保持原 ID。
- 增加 stdio MCP 源读客户端：初始化/发现/白名单查询、分页、超时与错误证据、原始响应和 transcript 摘要；语义以 tool_evidence_ids 关联，失败/过期/无关证据拒绝。
- README 明确初始化及五阶段细分步骤、skill/MCP、产物路径、门禁和前后衔接；恢复/复盘继续复用原账本。
- 本机实际验证为源审阅合同、隔离 MCP 协议进程及原消费者/安装；未实测真实 Serena/SourceKit/Xcode 服务或完整 App 双端行为。

# 0.6.0 — 2026-10-09

- 新增机器 iOS 事实图和规则派生义务，四类分析视图与实际 provider 接入；保留解析层级、源码片段、摘要和未知。
- v2 事实门禁阻断 NA 矛盾、错误初值、无关锚点、漏义务及弱 oracle；七技能补可执行入口、专业规程、模板和 ArkUI 语义映射。
- 接入字节不变的 CodeX 1.7.0 四拍核心；typed task/所有权/DAG/fact/AC、任务书和 baseline 冻结，真实回执及文件差异检查。
- 增加事件/存储效果链和显式进程观察；默认未运行为 UNVERIFIED，不继承旧版 PASS。
- 显式旧版导入、源刷新、重排与历史留存；Windows 冻结核心的宿主解释器适配；发行检查失败/超时保留报告。
- 独立使用发现并修复单页 Batch 规则冲突、差异表头误报与字面量零扫描；原字面量入口改为真实 iOS 源提取。
- 验收范围为工具与隔离样本，真实 App/Apple 构建/鸿蒙 HAP/双端设备验收仍未验证。

# 0.5.0

- 原生重写 spec 前端；工程/UI/功能/API 四分析规程，保留 SwiftUI/UIKit/语言语义与独立行为真值。
- 通用 source_anchors 与 ios-semantics 检查；保持原 a2h 计划/实施/验证消费者兼容。
- 启用层全局清理源平台残留；96 技能、29 角色；完整 3,516 原资源独立归档随包。
- 退出旧源画像/路由/默认尺寸推断入口；初始化无旧平台回退，图片检查只读前置。
- 明确 Apple 官方技能存在但本次未加载，MCP 未连接；更新安装、README 和验证边界。

# 0.4.0 — 2026-09-29

- 将原独立 HMigBot 1.6.1 的 99 个技能、31 个角色、模板、参考、运行时和编译依赖复制入包；新增 3 个 iOS 技能与 2 个角色。
- 恢复原 a2h 五阶段主线和原 spec/双计划/AC/findings/brief 接口；源分析、页面、资源、oracle 改为 iOS 分支。
- 安装器改为独立全资源安装，清退旧六入口和外部绑定，保留用户修改与安全卸载。
- 加入原消费者兼容、失败路径与独立发行包验证；记录原结构检查对空处理器的检测边界。

# 0.3.1 · 2026-09-29

- 六个入口改为直接维护的迁移规程，补齐上下文选择、源语义决策、实际实施与接线、失败修复、验收和续跑；增加各自按需参考。
- 同步脚本只维护目录和机器索引，旧生成入口兼容但不再覆盖技能正文。
- pipeline-status不再把缺失或空复盘报告标为已就绪；已登记的未关闭问题阻止进入验收审查。
- 新增技能维护保真、参考安装/卸载回归，文档链接检查覆盖技能参考。
- 本轮属于执行规程与状态正确性修正，不代表复杂应用或长任务代理行为已验证。

# 0.3.0 · 2026-09-28

- 纠正主线为“iOS源码/功能契约 → 原HMigBot鸿蒙技能 → 实际目标代码”，撤回0.2.0已完成通用工具的表述。
- 新增原HMigBot绑定、契约草稿、真实原技能路由与执行前新鲜度校验；任务准备不冒充代码已生成。
- 6个迁移入口取代66个入口，62项保留为内部检查清单；旧CLI和原子ID兼容。
- 安装器支持原HMigBot路径，保留绑定、编辑保护，升级清理已退休的原生成技能。
- 原Android单测oracle、闭包/覆盖消费者尚未适配，禁止假冒接通；云构建/iPhone回归辅助验收定位。

# 0.2.0 · 2026-09-28（历史记录，架构缺陷已在0.3.0纠正）

- 62个独立原子技能及完整编排，保留3个快捷入口，共66个；维护源、自动生成脚本、明确执行模式与验收契约。
- pbxproj/锁文件/IB/SwiftSyntax/Clang实际provider，源锚点与过期证据检查。
- 原生Stage骨架、PNG与字面量本地化转换、资源调用绑定；目标构建支持模块/产品与人工代码修订。
- 五阶段运行目录、功能覆盖、独立oracle比较、实际外部采集。
- 私有GitHub云Xcode构建、证据下载和IPA设备架构检查；Windows普通Apple账户本地签名教程。
- 完整安装/升级/卸载脚本、中文/空格路径、归属及用户编辑保护，重写使用说明和范围说明。

完整性、自测和局部构建不能代替任意业务应用的双端验收，验证结果以当轮外置证据为准。

# 0.1.0 · 2026-09-28

首个源码开发版：原生工程静态扫描、事实/配置/证据契约、迁移计划、闭合 SwiftUI 子集到 ArkUI 页面草稿、Stage 工程生成、显式 Hvigor 编译和可移植插件打包。

通用规则与业务示例分离。未知语法拒绝转换，旧配置冲突拒绝读取，生成不覆盖已有工程，旧摘要不能证明新源码，完整性/编译/行为验证状态分别记录。

完整原生应用迁移、编译器语义 provider、UIKit 转换、跨端运行等价与 HMigBot 原五阶段集成尚未完成。具体证据保存在当轮外置验证记录中。

# 0.11.0 — 2026-10-22

- Align decision-ledger paths, source/build admission and failed-hard-gate handling; expose existing prompt scopes through maintained author instructions, examples and schema.
- Validate shared task input paths and conflicting hashes before hashing each distinct file once per scheduler step; retain full current evidence gates.
- Add atomic explicit usage reservations, settlement and audited uncalled releases. First reservation upgrades ledgers to schema 2 so older readers cannot ignore in-flight bounds; unresolved usage remains blocking.
- Preflight complete provider plans before execution; record current discovery-only host/provider guidance in source preparation receipts without claiming native execution or compiler binding.
- Reuse existing Windows extended-length IO at provider capture/config/input/retry boundaries, with real deep-path lifecycle regression coverage and portable contract paths.
- Distinguish exact reviewed platform comparisons from unreviewed legacy instructions in native-surface audits; preserve adjacent-command and stale-review rejection.
- Make full-suite release timeout and fresh dedicated test paths explicit and retain timeout evidence; correct the Execute skill description for the official validator.
- Deliver a standalone Mac handoff with native evidence design; application acceptance still requires separate verification.
- Preserve original pipeline, vendor resources, control-state writers and local verification semantics. Real App equivalence and end-to-end scale/time/token goals remain unverified.

# 0.10.1 — 2026-10-21

- Distinguish replayed identity member reads from ForEach and identity modifier calls; allow unit/contract/UI observations for value reads while retaining conservative UI judgments for calls, writes and unknown uses.
- Bind contextual selectors and lexical classification policy to the complete rules digest; preserve fact IDs/counts and reject tampered metadata through source replay.
- Require existing baselines to be re-extracted and reviewed with the current runtime; no stale gate success is inherited. Tool checks do not establish application UI or functional equivalence.

# 0.10.0 — 2026-10-20

- Add fresh source preparation and source-bound, unreviewed specification scaffolds.
- Guard Unicode feature discovery, zero-object checks, input/output isolation and coverage ownership.
- Keep target-specific extraction findings distinct; restore the original Swift string regression cases.
- Project explicit decision consumers into task prompts while preserving shared decisions and full ledger hashes.
- Add replayable usage and wall-time budgets, boot/host checks and isolated synthetic scale probes.
- Check explicitly selected usage budgets before scheduler dispatch; preserve landing after exhaustion.
- Make subprocess limits configurable by stage with a shared deadline; isolate default pytest collection from vendor archives.
- Add three neutral host behavior baselines with separate business/guard denominators and explicit runtime selection.
- Bind per-file fact caches to content hashes and preserve concurrent provider attempts and their exact inputs.
- Capture actual Xcode compiler membership and pin its identity when a selected-build scope consumes it.
- Save reviewed Harmony build diagnostics, reject contradictory success logs and stage the real base Python on Windows.
- Preserve unknown/unsupported/unverified states. Application equivalence and end-to-end performance require separate evidence.

# 0.9.2 — 2026-10-17

- 精确识别Xcode自动自引用workspace、已知IDE检查缓存和直属xcuserdata；真实workspace引用、共享Scheme、锁文件、配置与源码继续使摘要过期。
- 新增只读spec-authoring完整清单与受当前源/MD摘要绑定的候选渲染；生成器与原门禁共享disposition schema、native维度/事实校验及源真值锚点规则。
- 同步Spec规程、模板、产物合同及续跑步骤；未知/缺失/重复/越界和NA矛盾继续拒绝，不改应用源码或放宽门禁。

# 0.9.1 — 2026-10-16

- 统一真实 Markdown 表格解析及目标列权限，处理相邻表、代码示例、行号/单元格跨度、核心标题歧义、缺件合并和显式未完成断言。
- 按 catalog 的核心节/表头/稳定 ID 精确投影进度，阻断业务状态、范围与归属变化，typed segments 消除原文占位符碰撞；同步 Spec/Plan MD。
- Swift 字符串保留完整 raw 分隔符、表达式和跨度，无法解码时标记 unresolved，不输出错误 value；同步资源消费 MD。
- 新增只读 spec-upgrade 和明确选择候选的受控应用，不猜语义、不自动切 profile 或继承 PASS。
- summary schema 2 逐页连接计划、原调度身份/落账、回执和当前输出；行为从本页 AC 原始观察推导；新增确定性 migration-report/--check，并在 Execute/Verify MD 实际调用。
- 增加边界反例、独立审查及中性真实构建/逻辑评估；实际业务工程和双端设备验收仍不在本次完成范围。

# 0.9.0 — 2026-10-16

- 以 MD 为主完善源分析步骤、正反例、页面组件/布局/ArkUI映射/资源表、共享动作单源、逐动作联读和原作者返修/独立复查；同步 Spec/Plan 模板、派发协议与角色。
- 新项目启用 spec_contract_version=2；catalog/schema 与实际只读检查器共同限定核心章节、表头、页面 meta、动作定义/消费及按需 JSON 引用视图；原 API inventory 服务协议保留。
- Plan 的 indexed MD、plan_items 投影与 typed task 对账 AC、页面、依赖、写权、范围及验证义务；冻结传递输入与工具合同版本，索引仅精确进度可变，禁止降级绕过。
- 执行任务注入精确合同闭包，未读 addenda 阻断受影响 AC；独立 FV 无全工程写权，修复回原责任任务；统一既有六种 placeholder kind。
- 新增 product-literals/spec-summary/plan-check；不覆盖 raw 字面量或三控制账本，不把历史 verified/brief PASS 当运行证据。编译和行为报告绑定当前源码、目标及规格摘要。
- 增加正反例回归、实际模型生成的旧/新规则样本及独立源复核。发行检查验证工具合同和安装使用；不宣称真实 App 双端设备验收。

# 0.8.0 — 2026-10-14

- 从原spec原则、下游plan/execute消费者和软件设计实践完善主规格、目标公共接口、状态/对接点与独立AC合同；保留原五阶段和三账本写者。
- 增加只读spec-check，并集成source-check --harness；检查正文、明确目标符号、UI目标状态、精确共享引用、延期断言及import/Preview真值反例。
- import不再生成持久化操作义务；保留Preview原始事实和义务，通过哈希、精确词法区间、审阅与skip-list验证非产品排除。
- domains冻结共享合同的传递依赖与决策账本，保留进度索引可写性，并将Stage 0真实资源映射留在执行所有权/回执检查中。
- 新门禁证明内容/消费者合同，不能证明全量语义或设备行为；旧baseline需补合同、重提事实并显式重排，不继承旧成功。

# 0.7.0 — 2026-10-12

- 固定并随包导入 AvdLee SwiftUI、Swift Concurrency 和 Axiom UIKit/内存主题，3 个 MIT 快照、87 个真实文件；逐文件来源和 SHA256 审计。
- 增加 expertise-plan/review：按真实源 token 路由、固定资料摘要、逐源文件观察与审阅记录；接入 source-check --harness 和 domains 计划冻结。旧 0.6.0 项目续跑需补审阅，保持原 ID。
- 增加 stdio MCP 源读客户端：初始化/发现/白名单查询、分页、超时与错误证据、原始响应和 transcript 摘要；语义以 tool_evidence_ids 关联，失败/过期/无关证据拒绝。
- README 明确初始化及五阶段细分步骤、skill/MCP、产物路径、门禁和前后衔接；恢复/复盘继续复用原账本。
- 本机实际验证为源审阅合同、隔离 MCP 协议进程及原消费者/安装；未实测真实 Serena/SourceKit/Xcode 服务或完整 App 双端行为。

# 0.6.0 — 2026-10-09

- 新增机器 iOS 事实图和规则派生义务，四类分析视图与实际 provider 接入；保留解析层级、源码片段、摘要和未知。
- v2 事实门禁阻断 NA 矛盾、错误初值、无关锚点、漏义务及弱 oracle；七技能补可执行入口、专业规程、模板和 ArkUI 语义映射。
- 接入字节不变的 CodeX 1.7.0 四拍核心；typed task/所有权/DAG/fact/AC、任务书和 baseline 冻结，真实回执及文件差异检查。
- 增加事件/存储效果链和显式进程观察；默认未运行为 UNVERIFIED，不继承旧版 PASS。
- 显式旧版导入、源刷新、重排与历史留存；Windows 冻结核心的宿主解释器适配；发行检查失败/超时保留报告。
- 独立使用发现并修复单页 Batch 规则冲突、差异表头误报与字面量零扫描；原字面量入口改为真实 iOS 源提取。
- 验收范围为工具与隔离样本，真实 App/Apple 构建/鸿蒙 HAP/双端设备验收仍未验证。

# 0.5.0

- 原生重写 spec 前端；工程/UI/功能/API 四分析规程，保留 SwiftUI/UIKit/语言语义与独立行为真值。
- 通用 source_anchors 与 ios-semantics 检查；保持原 a2h 计划/实施/验证消费者兼容。
- 启用层全局清理源平台残留；96 技能、29 角色；完整 3,516 原资源独立归档随包。
- 退出旧源画像/路由/默认尺寸推断入口；初始化无旧平台回退，图片检查只读前置。
- 明确 Apple 官方技能存在但本次未加载，MCP 未连接；更新安装、README 和验证边界。

# 0.4.0 — 2026-09-29

- 将原独立 HMigBot 1.6.1 的 99 个技能、31 个角色、模板、参考、运行时和编译依赖复制入包；新增 3 个 iOS 技能与 2 个角色。
- 恢复原 a2h 五阶段主线和原 spec/双计划/AC/findings/brief 接口；源分析、页面、资源、oracle 改为 iOS 分支。
- 安装器改为独立全资源安装，清退旧六入口和外部绑定，保留用户修改与安全卸载。
- 加入原消费者兼容、失败路径与独立发行包验证；记录原结构检查对空处理器的检测边界。

# 0.3.1 · 2026-09-29

- 六个入口改为直接维护的迁移规程，补齐上下文选择、源语义决策、实际实施与接线、失败修复、验收和续跑；增加各自按需参考。
- 同步脚本只维护目录和机器索引，旧生成入口兼容但不再覆盖技能正文。
- pipeline-status不再把缺失或空复盘报告标为已就绪；已登记的未关闭问题阻止进入验收审查。
- 新增技能维护保真、参考安装/卸载回归，文档链接检查覆盖技能参考。
- 本轮属于执行规程与状态正确性修正，不代表复杂应用或长任务代理行为已验证。

# 0.3.0 · 2026-09-28

- 纠正主线为“iOS源码/功能契约 → 原HMigBot鸿蒙技能 → 实际目标代码”，撤回0.2.0已完成通用工具的表述。
- 新增原HMigBot绑定、契约草稿、真实原技能路由与执行前新鲜度校验；任务准备不冒充代码已生成。
- 6个迁移入口取代66个入口，62项保留为内部检查清单；旧CLI和原子ID兼容。
- 安装器支持原HMigBot路径，保留绑定、编辑保护，升级清理已退休的原生成技能。
- 原Android单测oracle、闭包/覆盖消费者尚未适配，禁止假冒接通；云构建/iPhone回归辅助验收定位。

# 0.2.0 · 2026-09-28（历史记录，架构缺陷已在0.3.0纠正）

- 62个独立原子技能及完整编排，保留3个快捷入口，共66个；维护源、自动生成脚本、明确执行模式与验收契约。
- pbxproj/锁文件/IB/SwiftSyntax/Clang实际provider，源锚点与过期证据检查。
- 原生Stage骨架、PNG与字面量本地化转换、资源调用绑定；目标构建支持模块/产品与人工代码修订。
- 五阶段运行目录、功能覆盖、独立oracle比较、实际外部采集。
- 私有GitHub云Xcode构建、证据下载和IPA设备架构检查；Windows普通Apple账户本地签名教程。
- 完整安装/升级/卸载脚本、中文/空格路径、归属及用户编辑保护，重写使用说明和范围说明。

完整性、自测和局部构建不能代替任意业务应用的双端验收，验证结果以当轮外置证据为准。

# 0.1.0 · 2026-09-28

首个源码开发版：原生工程静态扫描、事实/配置/证据契约、迁移计划、闭合 SwiftUI 子集到 ArkUI 页面草稿、Stage 工程生成、显式 Hvigor 编译和可移植插件打包。

通用规则与业务示例分离。未知语法拒绝转换，旧配置冲突拒绝读取，生成不覆盖已有工程，旧摘要不能证明新源码，完整性/编译/行为验证状态分别记录。

完整原生应用迁移、编译器语义 provider、UIKit 转换、跨端运行等价与 HMigBot 原五阶段集成尚未完成。具体证据保存在当轮外置验证记录中。
