# 原生 iOS 路由输入

本适配替换源输入及必要内部兼容；仍按本 skill 原七步、85% 唯一 flag 方法裁决门、四视角对账、triage、fix_plan 状态机、修复与复检执行。目标以原编译抽取器为基底，限定补充见下文；比较算法和阈值不变。

## 公开入口

在目标工程执行，`IOS_SOURCE_ROOT` 取本工程 `.migbot/config.json` 的 `ios.source_root`，不使用另一个工程的配置：

```sh
ROUTE_VERIFY_ROOT="$PWD" python3 .agents/skills/arkts-router-verify/scripts/extract_nav_graph.py --platform ios --ios-root "$IOS_SOURCE_ROOT"
python3 .agents/skills/arkts-router-verify/scripts/llm_worklist.py
# 读真实 flagged 方法/闭包，按既有格式写本轮 llm_verdicts.json。
python3 .agents/skills/arkts-router-verify/scripts/apply_llm.py
python3 .agents/skills/arkts-router-verify/scripts/hmos_extract.py
python3 .agents/skills/arkts-router-verify/scripts/build_page_mapping.py
python3 .agents/skills/arkts-router-verify/scripts/build_report.py
python3 .agents/skills/arkts-router-verify/scripts/diff_routes.py
python3 .agents/skills/arkts-router-verify/scripts/hmos_reachability.py
python3 .agents/skills/arkts-router-verify/scripts/thin_shell_probe.py
python3 .agents/skills/arkts-router-verify/scripts/ios_dialog_probe.py
```

后续仍走原 build_fix_plan、逐项定性与 fixer 分派，不以脚本 exit 0 替代报告判断。无 ui-manifest 时保留原命名启发式；存在时使用其真实映射，路径/Markdown 包装在一次性输入镜像内归一化，不修改项目规格。

源单元格的“类型名（说明）”或“类型名 (说明)”仅在当前选定原生事实中唯一对应真实声明时解码为路由使用的 owner；反引号包装亦可。限定名先精确匹配，裸短名必须唯一；未知、重名、多个类型或嵌套说明不猜测。原格、说明、声明文件/行、匹配方式与结果留在既有输入 metadata，原规格字节不改。这是原生输入补充：原 Android 1.5.2 模板示例为裸类名；实际原引擎遇带说明的类名仍保留整格并报 class_not_found 跳过，并未内置此解码。

## 事实和裁决

- `Source` 提供当前选定 target/Release 视图。Apple SwiftSyntax 提供声明、调用、闭包、参数和准确源码位置；不把正则或旧 SPEC 图当独立路由 oracle。
- 识别 SwiftUI NavigationLink/navigationDestination、Tab、状态驱动弹层和 UIKit/IB 导航。动态调用、Objective-C 候选或不能证明的绑定必须在 unknowns/worklist 中披露，由原模型裁决/triage 处理；不宣称具备 Swift 类型检查或完整 Objective-C 编译语义。
- 方法键取工作清单的 `method_key`，包括所属嵌套类型、参数标签/类型、真实闭包位置；extension 归回所属类型。不要手写简化键，以免重载碰撞。覆盖率分母是唯一 flag 方法，不是边数、页面数或控件数。
- 原生零导航单页合法，不加零边门。保留未解析目标与计数，不用虚拟目标补齐；未裁决不能静默删除来提高覆盖率。
- 源失败、语法失败或身份不符不能覆盖成空成功。下游使用本轮 source/input identity；原始 source 产物改变后从抽取重新开始。
- alert/confirmationDialog 的 `isPresented` 等绑定进入原 `state_binding/guard` 及真实触发归属。UIViewRepresentable/UIViewControllerRepresentable 只补充目的地候选，防止把同一呈现区的其他 View 误选为唯一目标；它们不因此加入页面总数。多候选仍走原方法裁决，不能按组件名字选页。

## 共享鸿蒙目标 ETS 补充（.35）

`hmos_extract` 在源平台分派之前执行：iOS 和 Android 使用相同的原目标引擎及官方 ETS 补充，不读取源侧 expected/nav 作为目标事实。源抽取、85% 方法裁决和源专属薄壳 census 仍各自执行；下游比较器和阈值不变。保留原始 `actual_nav.original.json`。目标 receipt 只绑定目标文件、选定 SDK、工具和原引擎身份；源消费者另查源身份。

本工程选定的华为官方 ETS parser/checker 证明真实渲染链：零参 Builder 的 Tab、调用或引用式 bindSheet/bindContentCover、唯一组件的条件/ForEach 弹层，以及有明确实例绑定的 BuilderParam/@Event 转发、间接方法和共享 NavPathStack。未证明的动态/歧义实例、递归、事件 return/throw 后代码及被重新赋值的 stack 不产生补充边；仍保留诊断。非 optional 事件已有原边时只记录链，不重复补边。

尾随闭包按官方语义覆盖 BuilderParam 默认值。同一弹层调用点的真实实例目标不唯一，或其中有未解析实例时不取首个目标；保留全部实例证据与诊断。无实际入参的独立种子不冒充已绑定实例。stack 绑定的中间层同样检查重赋值，V1 @Prop 的复制语义不能用作父子同一 stack 的证明。带条件的事件 push、try/短路/三元事件表达式保留待裁决，不扩展为本轮可选链接补边；渲染条件仍是静态声明，不推断运行真值。

接收者可选链导航仅处理已证明的 `stack?.pushPathByName(...)`。先在私有目标镜像跑原引擎，只有顶层 hmos_root 使用真实原产物的字段字节规范化，其他字节须与原始图完全一致；再按 SDK 的 UTF-16 token 位置只删除该 `?`，由同一原引擎实测边、控件绑定与 stats 差值。真实应用源码零改写，BOM/CRLF 和行号保留。所有增量必须归属到真实 push、注册和点击/调用锚点；既有边或控件身份变动、无法复现或归属时整批记 merge_unknown。调用形式 `pushPathByName?.(...)` 不在本轮补充范围。不能手写 direct/page_level、line 或 stats 猜测原 wire。原图的 literal/注册组件对应关系作为证据保留，实际 wire 值不改名。

生成范围沿用原引擎实测的 `entry/src/main/ets/**`，包括其内子目录；`ohosTest`、`src/test`、其他模块及根目录布局不扩入。范围外真实 import 仍提供 SDK 解析上下文和 SHA；具名/别名的直接成员调用沿原 wire 使用调用名，真实声明另记来源；命名空间、默认或再导出等未证明写法保留 unknown。没有默认目录时沿用原空结果，记录 `scope_status=default_scope_absent`，不另找模块兜底。这是原引擎的多模块布局限制，不能据空结果声称验证通过。别名/软链接 host 只保留原行并记录 `scope_exclusions`，不增设整阶段拒绝门。

补充行带 `supplement=ets_ast`、真实源码 SHA/span、Builder 调用链与官方 parser 身份。原引擎在同调用点的空目标仅在文件/行/API 唯一对应时补充，原行留在证据中；未解析、歧义、未证明参数/动态重复、递归及未引用 Builder 仍可见，不据此猜造边。可选链补边保留原 wire 的 `registered` 口径；附加注册证据交原 triage 核对。

目标文件、SDK/parser、上下文、原引擎及补充代码的身份记录在 `hmos_extract.ets-input.json`，下游拒用过期输入；SDK/解析失败显式返回 incomplete。Android 和 iOS 共用该目标层，原编译比较器照常执行。补充只是静态事实，不能视作设备验证或完整入口可达证明。

triage 同时读取该文件的 `unknowns/merge_unknowns/dead_builders/scope_exclusions`、`optional_measurement` 和 `event_bindings` 及每行来源链；公开入口会打印未解析项数量、scope 状态和文件路径。原报告不会自动裁决这些补充诊断，不能因脚本 exit 0 把它们略过。

`hmos_reachability` 会独立读取目标源码，其原 `layer/summary` 保留；相关页面仅追加 `ets_ast_supplement` 证据。模型须结合原层级、补充链和实际 Entry 入口，按原调查规程判断，不得把补充证据改写成可达结论。mapping/report/diff 仍由原比较器消费派生的 `actual_nav`。

## 弹窗、薄壳与内部字段

弹窗规格来自真实 props、闭包、body 控件和源码锚点，包含 sheet/fullScreenCover/alert/confirmationDialog/popover/UIAlertController。`layout=null` 表示没有 Android XML，不伪造布局。动态规格以未解析项报告，不能记零弹窗通过。

薄壳使用原目标计数与 overlap=0.4、ratio=0.5、min_ctrls=6。源侧分别记录本地化键、字面文本和动态未知项；不把未知当零或通过。无法比较的对保留 skipped 原因，交原 triage 解释，不以成对数为零宣称没有薄壳。

`android_root/android_page/android_ids/string_keys_android` 等是原比较器的历史 wire 名；iOS 分支值来自真实原生事实，并带 `source_platform=ios`、原始源根、目标/配置范围和哈希。它们不表示存在 Android 源码、Activity 或资源。第一方包字段用于 Swift module/target 范围，不要求原生工程具有 Kotlin 包结构。

本轮 VERIFY 的资源范围按选定产品的声明 membership 限定；未选 target 的 IB/strings 不混入。工程图是声明证据，不等于编译打包事实。已有阶段使用全根资源产生的口径差异记为工具输入差异，不能据此定性目标代码缺陷或偷偷重写已批准 SPEC。
