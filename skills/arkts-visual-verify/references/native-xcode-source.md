> .36 功能投影与公共门控入口见 [原生功能边界](native-functional-boundary.md)。

# Xcode 原生源端流程

.45 `build_page_queue.py` 与 `build_batches.py` 的 iOS 输入按原 UI 规格的结构化“iOS 页面”（兼容“iOS 页面/系统表面”）“输出文件”字段、source_anchors 的值和当前选定 Source 的官方类型事实认领输出合同。字段缺失时仅允许文件内唯一页面 owner 回退；不按锚点键或 View/Page 后缀猜对应。完整 ETS/配置投影中的原解析器决定唯一性，原生已解析或歧义结果优先；内联页按原 navigation.inbound 父级机制探测。队列/批次保持原身份及分组，旁路 native-mapping 凭据只说明静态定位；原批次就绪门禁仍先执行。

.44 数据桥仅投影已声明的路径参数和 phase2_needs 的树路径位置，trip、页名和轮数等标量交原检查器解析。错误文本中的已登记临时路径按原样或转义形式完整还原；若还原失败且原检查器已失败，保留其真实退出码及明确标记的原始输出，不将包装诊断冒充原检查结论。

本文件是 source_platform=ios 的可执行分支。沿原 Phase 1→源基线→HMOS 回放/多模态→fixer/reviewer→原轮次闸执行；三账、覆盖分母、到达、功能真值、证据和预算规则不变。Android 的 adb、Activity、uiautomator、BACK、pm clear 不作为 iOS 操作。

## 1. 当前源与独立观察环境

`RUNTIME=<目标工程>/.agents/hmigbot-runtime`。源根、选定 Xcode targets/Release 及 source view 从本工程配置读取。先按 ios-fact-tree/SwiftUI/UIKit 原分析流程生成并补全树；新工具也提供共享语法脚手架：

设备预检使用 `a2h-verify/scripts/probe_devices.py --project-root "$PROJECT_ROOT" --json`；有目标 serial 时显式传 `--serial`，多设备不能随意选。iOS 分支只读 Xcode/runtime、可选自有 session 与 HDC 列表，不调用 ADB，也不创建设备。保留原 0=ALL_READY、10=HMOS_ONLY、20=HMOS_UNAVAILABLE；`source_setup=pending` 放在子字段，0 仅表示可以进入准备，不能代表双端已观测或 baseline 通过。退出 2 是工具/配置错误，不能当 DEFERRED。完整 Xcode 已安装但全局选 CLT 时按命令级 DEVELOPER_DIR 使用；license/first-launch 问题明确报错，不自动修改环境。

`check_prereq_freshness` 的 NEED:both 是树/索引欠缺，不是缺设备；`check_dimension_prereqs` 仍检查原自闭环成员与可选维度。二者的原数据/功能/成员门保留，不由设备预检替代。

```sh
python3 "$RUNTIME/scripts/ios_visual.py" facts --src "$IOS_SOURCE_ROOT" --project-root "$PROJECT_ROOT" --bundle "$IOS_BUNDLE_ID" --out "$WORK/source-tree-scaffold.json" --facts-out "$WORK/native-source-facts.json"
python3 "$RUNTIME/scripts/ios_visual.py" build-source --src "$IOS_SOURCE_ROOT" --project-root "$PROJECT_ROOT" --out "$WORK/source-build"
```

build-source 以选定项目应用 target 推定同名 scheme；不唯一时显式传 `--xcode-project`/`--scheme`。实际执行 Xcode Release Simulator build，记录命令、退出码和构建产物。Simulator 与 device Release 条件差异须报告；不能据此宣称真机行为已验。

源观察构建使用 Xcode 本地 Simulator ad-hoc 签名（YES/REQUIRED=YES/identity=-），保留源工程 Team/Profile，不自动改配置或退回 unsigned。`build.json` 分别保留声明、Xcode 生成的 Simulated.xcent、最终各架构的 linked entitlements 与 codesign 输出；源 AppGroup 必须保留在最终产物中。Simulator 的 codesign 空字典不能单独证明无 entitlement。其他能力及真机授权仍按实际验证。

脚手架仍需原分析者完成页面/fragment、containment、导航触发、场景、functional_checks 与 oracle 的补全，并过原树数据闸。它不是已验证功能账，也不以旧 SPEC 导航图充当独立源 oracle。

Tab 成员/顺序/标签作为 `native_tab_groups` 声明交给分析者补全既有树关系，不自动生成两两导航边，也不把声明当运行观察。原路由 wire 沿 Android 1.5.2 的独立 `tab_groups` 合同。

fact-tree 沿原 `$schema_version=1` 与 `source` 对象合同，原生来源写 platform/ios_root。旧 `source="ios"` 字符串稿须重新生成，不能静默转换后当已验证树。@main App/AppDelegate 记在 native_application_roots/native_bootstrap_type；原 launcher_activity/short 由源分析者在 enrich 时填写真实渲染入口/初始屏，不能用 bootstrap 类冒充页面。条件首屏保留全部候选，再结合真实首启观测定态；未补全脚手架照常不能通过原树闸。

```sh
python3 "$RUNTIME/scripts/xcode_ui.py" start --workspace "$WORK/ios-observer" --app "$BUILT_SIMULATOR_APP"
export HMIGBOT_IOS_SESSION="$WORK/ios-observer"
```

provider 只创建全新、带归属记录的 Simulator；所有 mutation 明确使用该 UDID。它不选择 `booted`、不修改全局 xcode-select，不访问其他工程设备。目标 HDC 设备仍按原前置和串行约束；若目标 bundle 与其他运行工程共用，先确认当前被测包和使用时间，不覆盖正在由另一个工程使用的同名应用。

安装时保存实际 source app binary SHA 与匹配 `build.json` 的身份；采集 metadata 引用该安装记录。已知 source snapshot 不符时先重建，不把旧 unsigned 采集当作新构建证据。直接提供、没有工具构建记录的 observer QA app 明确标为 unrecorded。

## 2. 原边行走与真实动作

计划继续由 `plan_edge_walk.py` 生成，LLM 按既定安全分级编排，机械步骤记入原 ledger。公开动作通过 XCUITest：

```sh
python3 "$RUNTIME/scripts/xcode_ui.py" command --workspace "$HMIGBOT_IOS_SESSION" --operation launch
python3 "$RUNTIME/scripts/xcode_ui.py" capture --workspace "$HMIGBOT_IOS_SESSION" --output "$EW/current"
python3 "$RUNTIME/scripts/xcode_ui.py" command --workspace "$HMIGBOT_IOS_SESSION" --operation tap --arguments '{"selector":{"identifier":"实际原生identifier"}}'
```

selector 支持真实 `identifier`、精确 `label` 和公开 `element_type` 数字；query 必须唯一。输入用 type_text，滑动用 swipe，深链用 openurl；Home 用 press_home，长按用 long_press。坐标必须显式 `coordinate_space=screen_points`，从实际层级取值。长按系统图标可能触发 XCTest 约一分钟的 idle 等待，本轮实测 62.26 秒，默认有界预算 120 秒；launch 与系统 scope 的 tap 预算 180 秒，给 XCTest 自身约 60 秒的 idle 等待及后续实际响应留出空间，其余动作默认 60 秒。显式 timeout 优先，超时是 observer 错误而非 App 崩溃。

没有 iOS 通用硬件 BACK。按源边语义点击真实导航返回/关闭控件，或使用原路由约定动作；不把 Home 当返回上页。

系统权限/桌面操作显式 `scope=springboard`，仅针对自有 Simulator。按当前真实树选按钮，沿既定 baseline 场景记录选择，不自动批准全部权限。AUT foreground 不证明无遮挡；默认采集同时保留 SpringBoard 树与 alert 观测。

Widget/实时活动须观察真实系统承载界面，可使用公开 Home、系统 scope、长按、滑动与点击。没有通用高级“添加任意 widget”API 的承诺；没真正呈现/采集时必须留未完成项，不能拿 App 截图当 Widget baseline。源页 `native_identity.scope=springboard` 表示以真实系统界面采集，仍须唯一身份与配对证据。

## 3. 到达、采集与普查

每页在树记录 `native_identity={required:[{identifier|label,element_type|type}],excluded:[...],scope:app|springboard}`。这些是源/运行 grounding 注释，不是工具内置业务常量；`.id()` 不等于 accessibilityIdentifier。没有身份、页面不对、匹配歧义或系统遮挡时不能用期望页面名落图。

LLM 走到位后照常调用 `walk_ledger.py settle ...`；其内部 `capture_page_e2e --capture-only` 在 iOS 自动走新 provider。也可直接调用原公开 capture 入口做补漏。实际 source session 用 `HMIGBOT_IOS_SESSION`，`--serial` 若传入必须是该 session UDID，不能传 HDC 目标 serial。

采集保存真实 PNG、原生 JSON、`.ios.xml` 与 arrival/capture metadata。XML 使用 `XCUIElementType*`，真实 identifier 独立保留，`resource-id` 为空；clickable 保留截图内 enabled 的原生交互候选，查询得到的真实 hittability 独立保存在 native_hittable（三态）。未知或同名不静默从发现分母移除；动作是否成功仍按实际响应/到达判断，不能由候选属性认定。frame 原值为屏幕 point，bounds 使用同次截图实测 pixel 映射，不固定 3x。Apple ImageIO 检查 PNG 解码、尺寸与黑屏样本；这不替代多模态判断。

AX 原件包含屏外节点。比较 XML 仅把旧消费者使用的 bounds/text/content-desc/clickable 投影到同次截图范围：部分交集裁 bounds，完全屏外或 exists=false 的比较字段置空；Application/Window 的容器名只留 native_label。原 JSON、原 frame、原 bounds、原标签与哈希保留，disabled/hittable=false 不等于文字不可见。此投影不改变页面/功能覆盖分母，也不证明未观测的遮挡关系。

`ios_visual.py sweep --workspace ... --tree ... --page ... --actions ... --out ...` 批量执行 LLM 已确定的普通安全动作，并把每个 functional check 的实际前后图/树/响应写入原工作目录 `run_meta.json`。actions 的 checks 按原 check_name 索引，每步写 operation/arguments/safety=normal；不执行的项明确 deferred/not_found，原分母保留。collector 的 ok 仅指动作执行，grounding/blackbox 裁决仍由原分析者完成，未判、未应用或绑定债照常拦截。

.45 sweep 继承页面 native_identity.scope（缺省 app）；动作参数显式 scope 优先。每项 plan 可显式 after_scope=app|springboard 决定动作后采集范围，非法 scope 在执行前报错。跨范围采集不证明到达或功能通过，after_identity 与独立 judge 继续判断；native JSON 记录实际 scope，系统截图引用也保留 scope。普通 App 页的调用参数、路径、索引和结果合同保持原样。

失败沿原 settle 路由：12=empty_state，13=dump_unavailable，14=screenshot_failed，15=wrong_page；工具/配置错误非零中断，不写“空成功”。原重试上限、自愈梯、分支 BLOCKED 及缺货账不变。

XCTest 动作层的 recorded failure 可能终止 runner。宿主将失败如实报告并使会话失效，保留 runner 日志/xcresult；关闭该自有 session 后再恢复观察，不能把 observer 失败记成 App 崩溃或动作成功。

## 4. 正式落位与原比较器

.46 支持消费原生 adapter 在切换趟次时保存在 `ledger.settled_by_trip` 的历史捕获。原流程每趟应及时落位；补落位时给 `walk_place_baselines.py` 或 `walk_finalize.py` 显式传 `--source-app <当前官方源构建的绝对.app路径>`。匹配请求趟次的当前工作行仍优先，历史行只读请求趟次；构建身份、当前源上下文、原页面身份、原件及归档副本哈希不符即拒绝。`placement_sources` 只记录历史证据来源，不能宣称新运行或新真值；冻结、原门禁和分母保持。


工作截图仍在 edgewalk/shots，不是正式 baseline。`walk_finalize.py` 的 iOS 编排保持原 inherit→writeback→materialize→source placement→readiness 顺序。grounding 的 canonical 真值是 expected_ios/ios_trusted，内部原编译器旧字段仅由一次性哈希检查的镜像派生，不允许旧 Android 文件反向覆盖。

正式源目录只有 `screenshots/ios/<trip>/<page>.png` 和 `<page>.ios.xml` 等既有白名单文件。raw native JSON 留在工作证据目录，capture metadata 连接其 hash、request ID 与时间；三者不成对不能计覆盖。冻结后不覆盖。若沿原 ≤1800px 规则缩图，使用官方 sips，并同步投影 XML bounds，保留原 point 坐标、原件和变换记录。

原 replay compiler 通过只读临时 bare `<page>.xml` 输入镜像读取 native XML；这是修正旧程序误把 `.ios` 当页面名的问题。输出计划和证据引用还原正式 iOS 路径，哨兵、功能分母及 not_planned 欠账必须保留。原目标 HDC/replay、placement、artifact/gap/evidence/round gates 继续执行，不以脚本 exit 0 或文件存在单独判 PASS。

Mac 原编译器子进程兼容在本安装私有 content cache 内执行：分发 bin 不改，缓存副本经 Apple install_name_tool 修改 Python dylib 依赖名、ad-hoc 重签，并放入真实 Python 子进程 shim 与逐字节公开 wrapper。记录原/新 hash、otool、签名与 argv；不修改其他工程缓存。CLI dispatcher 无法使用的入口由明确兼容层/可读编排处理，不能把 malformed-argument 或 skipped-gate 误当检查结果。

缓存只接受随包固定的 macOS arm64 原 dist SHA 清单，复制后逐文件核对；只在这份私有副本内归一化下载隔离元数据并验证所有 Mach-O 签名，不改变原包或系统安全策略。命中缓存仍核对完整文件集合、哈希、执行位与原生加载元数据；异常重建，失败明确报路径。

黑盒发现的原生静态/动态分类及 PageVariant 源 producer 为可读适配实现；原编译 core 的行为账继承继续执行。真实渲染锚点的 Swift 静态字符串/IB/选定资源支持 static，带锚点的插值支持 dynamic；未知走既有待裁决债，不能静默从分母移除。原生 finalizer 与 round 聚合是可读编排，保留原 per-trip artifact/gap/evidence core、原预算/状态/判定顺序。已对中性合同样本差分验证，不宣称覆盖 opaque core 的所有输入。

分类 receipt 单独记录选定文本资源的内容 SHA、分类器/Source 上下文及发现账；下游严格核对，source collector 只允许保持稳定输入下追加新观察，不能改删已物化条目。新增分类资源内容集合按选定产品；既有 source guard 仍含全源快照，可能因未选文件变化保守报 stale，本轮不改变此旧合同。未做黑盒物化的树不新增 receipt 必填条件。

结束时 `xcode_ui.py close --workspace "$HMIGBOT_IOS_SESSION"`，保留宿主证据后仅删除本 session 自建的 Simulator。物理 iOS 签名 runner、旧 SDK fallback 运行及完整 Widget 场景只按实际测试披露，不自动等同于已验收。

## .38 重名检查的采集合同

功能 name 可以重名，原 feature_path 和分母保留。actions.checks 新列表逐项写页内零基 check_idx、原 feature_path，可附原 check_name；动作仍按原安全分级。计划的 functional_checks_sha256 用运行时 `native_visual.functional_snapshot(page)` 从当前页面生成（page id、顺序、idx/path/name/kind），不包含 GT。执行时不匹配会报错。旧按唯一 name 的字典继续可用，重名动作不能借该形式猜选。

run_meta 使用原消费方的 checks 数组，每项有 idx/name（另留 check_idx/check_name）、feature_path、静态身份指纹和实际前后观察。每次执行项重新取 before，不复用第一条检查的状态。未执行项仍逐条记 not_found/deferred，collector ok 只表示动作发生。判读结果保留 check_idx/check_name/feature_path/functional_checks_sha256 后交原 writeback；最终化和写回前核对当前指纹，索引错位不能写入。旧 records 形状的未完成采集需重新采集，不能改名后当新观察。

## 宿主和叶页共屏的原身份语义

沿原 edge-walk 的 activity_root/tab 约定，宿主仍须 capture，只不普查；tab 控件由计划边结 grounding。原生输入保留 is_container、parent_in_nav 和 native_tab_groups。只有 activity_root 容器、源声明的 TabView host，以及声明 targets/contains/实际 tab 子页 parent 集合完全相符时，provider 才派生宿主身份层；不接受调用方写 role 冒充宿主。普通页保持叶层。

每层仍须独立的真实唯一签名。宿主与当前叶页可同时命中，必须有已声明的祖先关系；同层多义、无关宿主、空签名、循环/断链、遮挡或非前台仍拒绝。多宿主同时命中保守失败，尚不宣称支持未实测的嵌套宿主。matched_pages 保留请求层的命中，all_matched_pages 保留全部真实命中，原观察不改；正式源基线和覆盖门仍执行。宿主签名由源分析者按真实 AX 填写，不能由子页成功代替；原 walk_whereami 继续必须显式 --expect，不新增无目标推断模式。

## .39 准备数据接口

Phase 1 的 `enrich_factree_anchors.py` 在私有树/规格镜像中运行原算法，转换 source_anchors 和 source 根字段，再将原输出映射到 ios_source_refs。每条新引用必须来自原匹配器认领的规格中声明的文件，属于当前选定源码；全字段守恒与输入哈希核对后才写回。未匹配项保持明确缺口，文件级别名不要求是类型名。

弹窗静态目录使用 `extract_dialog_ids.py --ios-root ... --package ... --project-root ... --out spec/visual-verify/native_dialog_catalog.json`。它复用官方 SwiftParser 事实，记录实际 Source/Release/target 身份；schema 为 native-dialog-catalog/1，保留所有已建模弹层、调用位置、控件和 unsupported_constructs。status 只指静态建模是否有未知；runtime_verified 恒为 false。Source 配置或解析失败非零，不以空目录放行。iOS 拒绝 --layout-pattern 和旧输出文件名，避免 opaque Android 消费者将新格式当成没有弹窗。

每个源端 chunk 先读此目录，核对 schema/source_sha256 与当前树一致。analysis_key 和 declared_text_literal_or_key 是源码线索，可能是本地化 key；只有实际 accessibilityIdentifier 给 selector_candidate，仍须 fresh Xcode query 验证唯一性。source_role=cancel 仅是明确声明的 ButtonRole，不授权自动点击；未知、动态及组合内容按现场与源语义补查。旧 dialog_id_catalog.json 若存在，记录路径/hash并忽略，保留原件，不删除。这个目录不交给旧 Android/HDC 的 popup reader；原生设备动作仍按本文件公开 XCUITest 流程。

.40 配对时间比较复现 XML 生产者的 str 格式：原 JSON 数字与 XML 文本逐字匹配，旧字符串时间同样精确匹配。不存在容差或重写证据。失败采集保留原件和尝试记录；工具修复后重新公开 settle 产生新 request，不用只读校验结果补账。

## .41 同落点继承接线

原生 actions 支持原 `disposition=deferred_same_destination` 与 `inherit_from_edge={from,to,trigger}`。它表示已按原全 walk 计划认领的同落点检查，不能把普通导航归宿一律当同落点。保留 check_idx、feature_path、functional_checks_sha256；新采集可附 walk_evidence 的 walk_id/step。旧 deferred_to_walk 只有与当前计划、唯一原检查精确绑定时才在私有输入中投影；settled_by_walk 不重解释，无法绑定的原项不填真值，仍属欠账。原始采集和边记录保留。

继承仍由原 core 执行。原生索引输入以明确 --device-state 选取本 trip 的临时边输入，未知或其它 trip 的边不冒充本 trip；隔离明细与输入哈希记 inherit.native-input.json。这修正了原程序未按此参数过滤混合 trip 边的实现行为，属于单向收严，不是逐输入判定等价。整个目录无索引时走旧输入路径；混合目录整体按明确 trip 投影，receipt 同时列出 legacy 节点和排除的边。索引目录若未传 --device-state 且存在混合或未知 trip，明确拒绝，不能猜当前态。原输出的 feature_path/指纹只从当前已核对的 node+idx+name 采集绑定补回，不重写继承结论；原 retap、三账、到达/功能/证据/轮次规则继续执行。

索引继承还核对 node 与目录、当前功能身份及采集记录的 Source 指纹。原计划可选指纹语义未经证实，只记录不另加跨轮次拒绝条件；调用期间由输入 guard 保护，正常 writeback 改写树不使下一次继承误停。新增继承结论须来自本次 mapped 检查；原 core 未改变的旧行按原样保留并披露有效、过期或未绑定，不重绑、不补字段，后续 native writeback 仍拒绝与当前采集身份不符的行。retap 是欠账，可唯一匹配当前采集时补回身份；歧义或身份冲突原样留账并披露，不能据此产生可信结论。

receipt 的 prior_retained 记录未改变的旧结论；prior_retained_without_current_mapping=true 表示当前采集并不支持新继承，不能据此声称重测成功。unbound_retap 记录未绑定的原欠账。已知恢复限制：检查身份变化后，既有 native writeback 会因过期或缺身份旧 GT 整体拒绝；.41 不删除旧 GT，也不关闭此门。应以真实新观测/独立裁决替换对应行；是否具备完整公开恢复入口仍待核对，不能手工删旧行来宣称通过。

## .43 系统呈现的归属

直接 SwiftUI ShareLink 的系统表面不生成应用 PageVariant。external_system_ui 仅触发核查；实际判定绑定当前父 Source 调用、真实采集 Source/hash、唯一静态触发器，以及 Xcode 的真实源码语义解析。复用 pinned Release compiler_context 与捕获的目标 SwiftFileList，包含构建生成输入；在隔离源码副本中由官方 driver 生成 primary-file job，先 typecheck 并记录 loaded-module trace，再在相同上下文 dump AST。两次命令差异、源码映射、模块/宏/生成输入哈希及真实声明记入 receipt。此模式用于语义解析，不等于原 Release 构建或行为验收。无法唯一解析、依赖缺失、同名遮蔽或不支持的 API 保留既有欠账。

公开 materialize 从原始发现账重算，只撤掉未冻结的错误系统节点及其对应待补截图项；正式基线已冻结时明确要求从受影响源基线恢复。原 behavior_ledger 的动作、前后观察、关闭和 outcome 不改，仍由原 core 物化并进入原 reconcile；不新增伪 walk 边、不填写无消费方的 replay 注记，不声称分享成功。其余节点、功能分母、三账与轮次门禁不变。导入模块、宏或生成输入变化会使旧语义 proof 失效，需要重新物化。
