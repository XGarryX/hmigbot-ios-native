> **.33 VERIFY 源输入**：路由与视觉现有流程分别读取 [原生路由适配](../../arkts-router-verify/references/native-route-source.md) 和 [Xcode 源端流程](../../arkts-visual-verify/references/native-xcode-source.md)。这两个入口替换平台输入及内部旧 wire，不新增阶段、审批或必交件。

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

# iOS 输入与 1.5.2 原合同

这份参考只替换源平台输入。A → B → Gate B → C → 原全局检查/grill → Gate C，原模板、F/AC 编号、判/真规则、组/skip 记账、PLAN/EXECUTE/VERIFY 顺序均沿用 1.5.2。不要引入旧 iOS 包的 harness、逐条 obligation 审阅、semantic_refs 全覆盖、强制六列表或 typed-v2 前置门。

## 路径、范围与 Release

`.migbot/config.json` 的 `source_platform` 为 `ios`，`ios` 是 `{ "source_root": "...", "variant": { "scope": "project-targets", "project_path": "App.xcodeproj/project.pbxproj", "targets": ["实际选择"], "configuration": "Release" } }`。没有确认 target 时不写示例 target。原生公开配置仅使用 `ios.source_root`，不要求额外源平台路径别名。

INIT 先检查 Mac 的完整 Xcode、Swift 与 iOS SDK，使用 `capture-release --src <源根> --project <工程.xcodeproj> --scheme <实际scheme> --build --out <新的包外捕获目录>` 保存真实 Release 查询、无签名构建和 SwiftDriver 参数。仅收集环境、路径和配置上下文。**迁移范围在 SPEC 3.0 确认**：先列出实际产品 target，再按源码命中的登录、支付、推送、Widget、实时活动等能力逐类询问，允许保留/替换/延期，不沿用工具开发项目的选择。

工程发现使用 `.xcodeproj/project.pbxproj` / `.xcworkspace` / `Package.swift`，不以其他平台的构建声明替代。多模块条件不变（≥2 个真实模块、多子仓或 ≥500k LOC），模块来源改为 target/SwiftPM 模块。目录数量不等于模块数量。

```text
python .agents/hmigbot-runtime/scripts/ios_input.py environment --out spec/ref/ios-environment.json
python .agents/hmigbot-runtime/scripts/ios_input.py inventory --src <源根> --project-root <目标根> --out spec/ref/ios-input.json
```

首次发现尚可在范围确认前读取未选择的工程声明；正式 UI、API、profile、ownership 均使用同一个选定的产品源码上下文。SPEC 确认 target 后，用真实捕获执行 `prepare-source --src <源根> --project-root <目标根> --bundle <捕获目录> --variant <variant.json> --out <新的source-view目录>`，不传 `--provider`，由当前 Xcode 自动构建官方 SwiftIfConfig provider，保持字节偏移与行号。含条件编译的 Swift 不能把两支都当 Release；复杂 SDK/os/canImport 或无法解析的条件须明确技术缺口，不能猜成 false。缺省 Swift flags 需要 `--build` 所得的真实编译参数证据。没有实际构建不声明“已编译/已签名/已运行”。

## Phase A：三源准备

三源仍为 `meta.json`、`view.xml`、真实源 UI/资源。UIKit/Storyboard/XIB、SwiftUI 是输入实现差别：

| 数据类别 | iOS 输入 | 保留的下游形式 |
|---|---|---|
| 页面与入口 | 实际 App/Scene、UIViewController、路由与 Tab/模态中的 SwiftUI 页面 | ui-manifest、page_id、snapshot 目录 |
| 布局与样式 | SwiftUI 视图与 modifier、UIKit 视图/约束、Storyboard/XIB、Asset Catalog | 源文件路径与来源说明 |
| 运行时层级与截图 | 已有 iPhone/Simulator 观测 | view.xml/screenshot，保留真实来源 |
| 无设备时合成布局 | 原生源码静态 outline，再由分析者补层级/状态/交互 | synthesized=true、bounds 未知，不伪称运行时层级 |

`synthesize_meta_json.py` / `synthesize_view_xml.py` 已接原生生产器，参数保持原样。`--activity` 是历史 wire 名，传真实 iOS 类型；`layout_sources` 填 Swift/ObjC/IB 源文件。脚本只给骨架，**原 Phase A 的语义补充仍须执行**，尤其自定义容器、ForEach 身份、Binding、任务取消、导航参数、Tab/模态嵌套、UIKit delegate 和生命周期。不能把所有 View 类型都视作独立入口。

iOS 样式不使用旧 XML 主题继承。`resolve_theme.py` 对 iOS 返回原来已允许的无主题状态（exit 2），按原 fallback 读 Asset Catalog、UIAppearance、SwiftUI environment，并在全局约定披露；这不是跳过页面样式分析。显隐生产器输出原 `visibility-bindings.v1` rows，供原 target binding gate 消费。

## Phase B：API 与 UI

API 的 Phase 1 只生成词法调用、URL、模型及请求组装候选，不自动解析所有 SDK、参数或签名；Phase 1b/2 沿 URLSession/URLRequest、Alamofire/Moya、Codable/CodingKeys、Keychain 和真实调用链补齐；继续 Phase 1b 补扫、2 上下文、2.5 平台映射、2.75 认证链、3 原格式库存。`raw_apis.json` 结构不另起一套。动态 URL、请求字段、响应壳和 decode 失败次序必须读实际代码，不能因正则没命中而宣称无网络。

认证专项按原规则：静态链 → 测试访问资料 → 有界、源代码推导的协议探针 → 不确定项/grill。缺账号或环境不一律阻断；禁止对真实注册/SMS/用户登录无限试探。范围取用户当前决定，不内置密码/IAP/Push Kit 结论。

分页规格沿用原章节（溯源、页面结构、转换决策、状态接口、导航、安全区）。写成可独立理解、据此实现和验收的规格。源代码只作出处或必要的小例，不复制页面实现正文充当规格。原模板的 `source_anchors` **仍为文件级兼容键**，iOS 填真实 `.swift/.m/.mm` 路径；complex 的要求和 simple 的可选性均不变。不额外要求 node_id、逐控件 AC、六列表或 source_review 文件。

## Phase C：证据与 AC

`profile_feature.py` 把 iOS 构造映射到原 coverage-rules 的同一组信号；一般赋值、普通函数、布局初值不自动成为行为信号。具名枚举、事件、数值常量、权限调用、SDK 和 JS 桥按原类别记账：AC 点名 / `组:{…}` / skip 三选一，可多项共用一条行为 AC。Swift `extension` 与 ObjC category 文件按原 partial_class 角色追溯。

原 `lint_coverage.py` 入口已接线：局部 `--only-feature` 现场建 profile、只读、不推进修复次数；全局写原 findings section、沿用原熔断和回流。特征/实例/判/真/addendum 判定复用原编译引擎；Swift/ObjC 文件归属、入口声明、全局文件全集由平台包装层补输入，沿用原 rule ID 和严重度。仅检查文件对应，不做额外编译器符号/行号合法性硬门。

### 共享文件的可选实例转引

多个功能锚定同一源文件时，消费者可以在主规格的 `## 共享实例引用` 节使用下表，引用已在其他主规格直接验收的行为；没有转引表时按原规则检查。表是现有规格内的可选说明，不是新账本，也不复制 AC。

| 实例ID | 源位置 | owner AC |
|---|---|---|
| `enum:LoadState.ready` | `Sources/Domain.swift:12` | `F003-AC08` |

实例ID沿用当前 `feature-profiles.json`，源位置是实例记录中的文件和声明行；同一ID合并了多个位置时逐位置列出。owner必须是其他主规格中未被替代、具备源/判/真的真实AC，锚定同一源文件且直接覆盖该实例；合法的 `组:{…}` 字段仍可使用。全量检查要求owner主规格及该实例也在本轮画像范围内；自由文本F-ID、skip和链式转引不产生豁免。源位置陈旧、AC缺失、不同来源的同名值或原引擎不能确认覆盖时保留原缺项。

`lint_coverage.py` 在临时目录分别用原编译引擎测量消费者与被引AC，再展开已确认的直接引用；正式profile不变，总数保留，新增覆盖在既有findings context的 `instance_stats.shared` 中披露。按具体实例集合核对展开后未覆盖集合恰为展开前集合减去已确认转引项；总数和原全量统计也须一致，否则保留该类别原阻断。第一遍其他findings和warning不被展开结果取代。局部 `--only-feature` 和 `--report-only` 不写正式findings；全局仍由原writer重跑闭环。拒绝原因和源指纹在既有context中留证。

原 `extract_literals.py` 读的是定稿 SPEC，保持原实现；不能换成源码所有数字，否则会扩大原字面量收货义务。原 `score_complexity`、traceability index、addenda closure、HARD-DIV、plan/execute/verify coverage 检查继续原实现。原主线与旧 reference 有 AC 数量措辞冲突时，按原主线和 coverage-rules 的“对数量不设上下限”执行，不新增配额。

## PLAN、EXECUTE、VERIFY

PLAN 使用原 indexed-v1、coverage-matrix、owner 与原 legacy/shadow/v2 模式语义，缺 mode 仍是 legacy。EXECUTE 原三阶段、原收尾/账本作者、结构与编译步骤不变；资源输入改为 Asset Catalog/strings/xcstrings/字体/应用身份，保留已有工程，不调用其他源平台的解包或构建工具。

VERIFY 保留原实际 CHECK 顺序，首先编译鸿蒙目标，目标静态/占位/身份/页面状态/路由/视觉及终编译照原规程。源端观测使用实际可用的 Simulator/iPhone/Xcode 材料；无源设备时对源观测记 DEFERRED，写原因与关闭条件。目标设备要求不因此免除，尤其冷启债按原规则处理。生成、编译、行为验证分别报告。

## 用户授权选择（单独披露）

INIT/SPEC 范围分离是用户明确要求。默认不安装遥测 hooks、不上传、拒绝参与不禁用本地迁移；本地阶段标记继续由原 `a2h mark-stage` 生成，不手写完成哨兵。这些是授权选择，不冒称平台必须差异。

## C4.6b 原生四层审计

正常入口 `compute_feature_coverage.py --ios-root <源根> --project-root <项目>` 执行 L1 源领域、L2 ref能力、L3 API候选、L4 页面归属，并执行原发行程序实际的机械 L5 深度规则。复用同一 Source 的 target 成员、Release 过滤、源码哈希与行号；不生成其他语言源码投影。阈值与模糊匹配边界以随包原 CLI 的成对对照为准。

规格和计划公开使用文件级 `source_anchors` / `source_anchors_ref`，不增加逐语句映射。局部/全局 lint 和索引已验证此字段可直接消费。源码 ownership 兜底保留单独入口，正常审计 FAIL 或技术错误不得自动降级。L5 行数统计不替代独立的行为语义审阅。

所有实现与引擎随本包分发，不依赖外部工具目录。内部引擎存在不可变协议标识，集中记录于 `docs/engine-compatibility.json`；公开入口和规格写法使用原生名称。

## 历史工具名称和输出的 iOS 对照

| 原示例/输出 | 本分发的 iOS 处理 |
|---|---|
| `--ios-root`、`source_anchors`、`ios-*` | 原编译消费者的包内接口；输入真实 iOS 源目录、路径或原生节点，不另装其他平台包 |
| `SPEC.MANIFEST_ACTIVITY_UNACCOUNTED` 等 rule ID | 实际 App/Scene/导航/Storyboard 入口的记账；严重度和 skip/决策约束不变 |
| 源设备启动、层级与截图 | 使用实际可用的 iPhone/Simulator/Xcode 观测；没有设备或工具时源观测 DEFERRED，写关闭条件，不假装采集完成 |
| 源构建与资源输入 | 工程读取 Xcode/SwiftPM；资源使用 Asset Catalog/strings/IB；源 App 构建仅 Mac 以实际 project/workspace/scheme/Release 运行 xcodebuild，Windows 不尝试此命令，缺环境时 DEFERRED |
| `scan_ios_ui.ps1`、`deep_verify.ps1` 的 iOS 源清单路径 | 旧源扫描辅助器不进入本分发 iOS 主线。用 `ios_input.py inventory/meta/view` 和原 Phase A 语义补充，之后交原 UI/功能覆盖流程；不能让旧扫描器空扫描成为证明 |
| hdc、hvigor、ArkTS 目标错误和编译门 | 目标侧原步骤，照实际工程执行，源设备缺席不豁免目标检查 |

部分旧二进制仍可能打印原平台词或命令建议，无法在本轮修改其内部字符串。按上表解释，不执行这些旧源端命令；报告不得声称二进制输出已经全部清理。当前分发只支持项目级安装；不安装到用户级技能目录。Python/Swift 的开发环境发现会读主机环境，但新输入模块、安装器、findings 和项目配置均使用本项目路径。原编译程序全部可选分支的用户级缓存/网络行为未独立审计，不能承诺其全局状态已经全部验证隔离。


## UI 图输入边界

四文件图遵守 ios-ui-graph-builder/references/schema_v2.md。正式组件使用 ios_id，身份种类与锚点独立记录；分析分组 class=analysis:semantic_region，不是框架组件。原只读 validator/query 由入口做临时字段名适配，保留原检查、退出码、原输出和哈希，不写正式图。所有查询经原生 query_graph.py 入口，下游 JSON 使用 ios_id。规范化历史槽位不是 iOS API；源码导航和入口仍以本协议既有 App/Scene、NavigationStack/Link、sheet、UIKit push/present/segue/URL 口径为准。


## 图片与原结构自愈

转换器以源 frame/约束/真实逐图 scale 为尺寸证据；不按默认倍率猜。原结构循环 pipeline 的所有 detector 保留，由 launcher 在前后检查原图标自愈是否可能按假设改写。有 would-fix 项先按源证据补齐；没有则照常执行原循环。只读 guard 不写目标代码或原状态账本，不是新增 SPEC 门。同行/同缩进 Image 修饰链可能被原审计误判，先保持尺寸值仅规范为更深缩进后续行，再复审，不以乱改尺寸洗掉提示。

## VERIFY 原生输入与验证边界（.33）

路由读取独立的原生源码事实并交给原比较器；视觉使用 Xcode 官方能力做源端观察，目标侧沿用原 HDC。按 a2h-verify 的原顺序和回环执行。适配回归通过不代表项目路由或视觉已通过，项目仍须实际续跑。动态路由与 Objective-C 解析的不确定项见 [原生路由输入](../../arkts-router-verify/references/native-route-source.md)；Widget 视觉、物理 iOS 设备与签名环境的未验证边界见 [Xcode 源端流程](../../arkts-visual-verify/references/native-xcode-source.md)。不豁免目标构建与结构门，不自动重写已批准的规格。


退出码约定沿用原程序：0=CONVERGED、1=CONTINUE、2=ESCALATED、3=参数/输入/IO错误（含原生图片保护）。3时立刻停止，不读旧result、不finalize或推进阶段，也不原地自动重试。先读取本次guard证据，按已授权源事实修正输入后才可显式重新调用。原detector仅icon自愈会改产品代码，其余只读；结构修复worker在两次loop调用之间执行，不在guard前后快照范围内。后续格式化若改变Image链排版可能误拦，保留正确尺寸值仅按原解析约定排版复审，不能更改值迎合提示。

## 可选目标显隐映射

原 SPEC 已批准的平台映射可由原作者按 [可选输入格式](./native-binding-projections.md) 记录完整谓词到官方 Form 数据/渲染链的对应。保持原源行、AC 和阶段；没有该文件照原检查，有声明也须实际整链证明，不是改名、删除源条件或豁免失败。
