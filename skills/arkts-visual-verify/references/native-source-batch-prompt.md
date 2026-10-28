> 先读 [原生功能边界](native-functional-boundary.md)：Type#component 是分析键；source_native_selector 仅供 iOS，声明定位仍须现场确认；目标使用自己的真实层级。

# iOS 源端子任务派发补充

派发时填本工程真实参数：project_root、ios_source_root、tree_slice（只含本 slice）、walk_plan 相关步骤、trip、owned source observer workspace/UDID、原 ledger/grounding/blackbox 路径和既定场景。沿原 join、单设备串行、截图批量下放、账目与失败回流协议。

先读本 skill `native-xcode-source.md` 及当前 phase 的原语义规则。你负责按原 edge-walk 编排真实 iOS UI，并在本 slice 内结 capture、grounding、blackbox 与 edge truth 三账。禁止把旧 Android 示例当 iOS 命令；源设备操作只用该 owned Xcode session。不要操纵其他已 booted Simulator、HDC 目标或另一个工程。

1. 读取 fresh source facts/当前树 slice，复核真实原生 identifier/label/type、页面身份与触发条件。源码 `.id`、控件变量名、生成 component ID 都不是 accessibilityIdentifier。
2. 以公开 XCTest capture/find 观察现场，再按 walk step 选择 tap/type_text/swipe/long_press/openurl 和真实返回控件。系统权限或 Widget 桌面显式 scope=springboard；按原场景记录具体选择，不一律允许。
3. 每页 capture 通过原 ledger settle 调 native provider，必须验证实际页面、系统遮挡、配对 PNG/XML/native JSON 与 hash。错误页面不能套目标文件名；失败使用真实非零状态和原恢复上限。
4. 普查用 native sweep 批处理已定位的安全动作，或公开 command 对异常逐项恢复。每项实际前后截图、树、响应是观测；collector ok 不是功能 PASS。按原 oracle/grounding 规则写 canonical expected_ios/ios_trusted 与 precondition，再填写 edge_results 和 blackbox manifests。未知、动态、未判、未应用、未执行均保留，不缩小分母。
5. widget/系统扩展必须真实呈现在对应系统承载界面；无截图或无法到达就是缺货/未完成，不能用主应用图片替代，也不将整类功能一律豁免。
6. 回传原 manifest、缺货/恢复记录与待反哺项。主会话只收文字/manifest；图片判断仍在批次子任务。不要自行改原 gate 状态、做全局清理、发布或关机。

主会话在所有片收口后执行同一原 finalize 顺序与原覆盖/functional/evidence/round/fixer-reviewer 门控；本补充不新增审批或阶段。

.38 动作计划按本页 functional_checks 的零基 check_idx + 原 feature_path 列表构造，并用 runtime.native_visual.functional_snapshot(page) 绑定静态身份指纹；name 重复不得改名或只按文字认领。原唯一 name 字典仍可用。读取 run_meta.checks 的 idx/name 和真实前后证据；交给判读者的快照保留这些字段。判读回传 check_idx/check_name/feature_path/functional_checks_sha256，未知和未观测项不写可信真值。

activity_root/tab 宿主按原协议只 settle/capture、不 sweep；原生 provider 只从源声明和 canonical containment 派生 host/leaf 层。每层仍须真实唯一签名，宿主所需签名为空时先用现场AX做身份grounding，不得删掉叶页身份、删除宿主目标或用 expected in matched 硬过。

.39 开工先读 spec/visual-verify/native_dialog_catalog.json，核对 native-dialog-catalog/1 和 source_sha256=当前tree.native_source_sha256。读取全部 unsupported_constructs，在现场按源语义补查。它只记录静态声明，analysis_key/字面文案不是运行标识，字面文案可能是本地化key；selector_candidate 也必须实际唯一查询。cancel声明不等于自动点击许可。忽略并保留旧 dialog_id_catalog.json，不能把native目录交给旧Android/HDC reader。

源端局部子任务的返回不代表整轮 visual skill 退出。round_budget 的 begin/next/end 和轮次生命周期由主会话统一执行；源树/准备/行走子任务只回传本段结果，不调用这些控制入口，也不自行标记阶段完成。

.41 同落点检查可直接用原 deferred_same_destination 与 inherit_from_edge={from,to,trigger}，同时保留页内 check_idx/feature_path/静态指纹及当前 plan 的 walk_id/step。普通 deferred_to_walk 不自动代表同落点；旧归宿只有与当前计划中唯一原检查精确绑定时才可投影。缺绑定继续留账。实际边必须记录真实 device_state；其它 trip 的图或边不能声称为本 trip 新观测。原 core 决定继承和 retap，源作者不提前裁可信真值。

目录按需读取：先用脚本取schema、source SHA与全部unsupported_constructs，再只取当前chunk涉及的dialog条目；不要整读全部源码身份、控件与其它页面目录。

.43 系统提供的表面仍照实记录 landing_ability、真实前后观察及关闭动作；external_system_ui 只是归属线索。source_anchor 优先用 {file,line,sha256} 指向实际呈现 API 调用，旧“文件:行+API”格式仍可定位。工具对直接 ShareLink 使用当前 Release 源和 Xcode 官方语义解析确认归属；不能因按钮文字静态就把系统面板当成应用页面。未建模 API、歧义及失败继续留账。原行为账和功能分母保留，出现分享面板不代表分享成功。
