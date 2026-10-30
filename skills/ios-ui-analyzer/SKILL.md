---
name: ios-ui-analyzer
description: "iOS→HarmonyOS 迁移源分析第 UI 步：从 SwiftUI 组合/状态/Binding/身份/环境、UIKit 控制器/约束/outlet/action/委托/生命周期、以及 Interface Builder（Storyboard/XIB）三源静态一致地提取 UI 与交互事实，写页面事实与原生语义供 a2h-spec 生成 ui-manifest 与分页 spec。当用户说“分析这个 iOS 项目的界面/UI”“UI 建模”“组件关系”“页面跳转”或 a2h-spec/ios-source-analysis 组织源分析时使用；不要用于：功能行为与业务规则（用 ios-feature-analyzer）、系统 API/权限/三方接缝（用 ios-api-inventory）、生成鸿蒙/ArkUI 代码（用 ios-ui-to-arkui）。保持 SwiftUI/UIKit/Swift/Objective-C 语义，无运行时截图绝不伪造。"
metadata:
  type: domain
  domain: migration
  tags:
  - ios
  - ui
  - source-analysis
  - source-evidence
---

> **调用关系**：本 skill 是 `ios-source-analysis` 组织的四类源分析之一（UI 主责），结果由 `a2h-spec` 收口。若宿主支持 subagent，按 `ios-ui-analyzer` 角色名派发本技能（`fork_turns:"none"`，任务书写清 page 候选、源锚点、输出契约）；不派发时主会话顺序执行。遵守 **Join 协议（收口五条款）**：① 循环 wait——完成依据按 [a2h-join](../a2h-join/SKILL.md)：本轮可信宿主 `completed` 或经过身份与时序核验的原生 `FINAL_ANSWER`；产物存在不能代替完成；② 死句柄与验收——连续 3 次超时后 `list` 核对，completed≠验收通过，join 点跑门禁验产物；③ 收口锚点——最终报告前收口全部句柄；④ 放行≠遗弃；⑤ fire-and-forget 仅正文显式声明的派发免收口。**派发纪律**：`task_name` 唯一（带 page-id/round/scope 后缀）；派发前写清预期产物清单给 join 门对账；**谁派谁收**（sub-agent 不能嵌套外派后退出）；契约产物必须出自承担任务的子代理，禁止派发方代写占位产物。本 skill 只读源、写分析事实，**不派发下级迁移 worker、不写目标代码**。
>
> 路径约定：`$IOS_SRC` 从 `<target>/.migbot/config.json` 的 `ios` 字段读取；`<target>` = 鸿蒙目标根（源工程与目标工程必须分离）；`<runtime>` = 本包 runtime（`scripts/a2h_ios.py` 所在根）。产物落 `<target>/spec/ref/` 与 `<target>/spec/baseline/`，**禁落会话临时目录**。本 skill 自有文件：`references/analysis-v2.md`（逐页执行步骤与正反例）、`scripts/run.py`（runtime 定位，等价 `python <runtime>/scripts/a2h_ios.py`）、`agents/openai.yaml`。

# ios-ui-analyzer — iOS 界面、状态与导航事实

适用的 Apple 官方技能与 Xcode MCP 优先。先读取 `spec/ref/ios-expertise-plan.json` 与 `ios-official-analysis.json` 中为本类选择的资源，按原始摘要完成审阅；官方资料、只读 MCP、CLI 和编译器分别记录来源、用途、读写范围及实际结果。无官方证据时记录降级原因，保持相关 unknown；不把第三方资料或自编规程称为 Apple 官方。设备远程控制不在默认调用范围，界面授权由用户自行完成。


### 官方分析的执行责任（0.13.1）

当 `ios-expertise-plan.json` 为当前主题选择 Apple 资源时，对应主题的分析过程由导出 skill 的适用规程承担：逐项执行其相关参考的审阅步骤，沿真实源码记录观察、未决项和影响；本技能保留迁移输出字段、归属和门禁合同。不得仅确认已读资料后继续用自编经验替代官方审阅。SwiftUI 使用 swiftui-specialist 的相关结构、状态、身份、环境或文本章节；App Intents 使用 app-intents-specialist 的执行模型、实体/参数、结果及快捷短语章节；文档型 SwiftUI 与 C bounds 仅在实际源输入适用时执行对应导出 skill。没有覆盖该主题的官方 skill 时明确保留自编/第三方分析，不伪称官方执行。

每条 Apple 源观察用 `expertise-review` 写入 `official_basis` 数组，字段为固定资源的 `path`、`sha256`、实际适用的 `section` 与具体 `application`。同时保留 `source`、`interpretation`、`unknowns`。只有资源确认、没有资源规则如何应用到源码的记录将被拒绝；此合同核验不替代对模型判断的独立复核。官方语义规程不能批准产品取舍或目标平台替代。

Swift 文件的词法/声明结构优先消费当前 facts 中固定的 SwiftParser/SwiftSyntax 产物，不能为了旧 Python 闭合语法可接受而改写源文件。编译上下文由实际 Xcode CLI 产物或经过校验的同源回放承担；MCP 不可用保留原错误和未决项。远程控制、界面读取及权限修改不在此分析范围。

## 0. 定位与纪律

- **前置**：上游（a2h-spec / ios-source-analysis）已跑 `harness-init` + `source-index` + `facts`，`<target>/spec/baseline/ios-facts.json` 与 `ios-obligations.json` 存在。缺 → 提示先跑上游（ios-source-analysis §1 或 a2h-spec §1），**不代跑**。本 skill 先加载 `../ios-source-analysis/references/harness-v2.md` 确定机器产物/状态写者与门禁语义。
- **输入**：工程地图（`spec/ref/ios-project.md`）、target/configuration、页面候选、真实 Swift/ObjC + SwiftUI/UIKit + Storyboard/XIB 源码、机器 UI 信号（`spec/ref/ios-ui-signals.json`）。**源不可读是阻塞**，不以页面名、文件夹名或旧报告补造结构。
- **输出**：`spec/ref/ios-ui-facts.md`（本 skill 单写的人类可读分析）+ 每 page 的源原生语义事实；随后由 a2h-spec 的 `spec-authoring` 落为 `spec/baseline/ios-semantics.json` 的 page 部分（机器校验，见 `../ios-source-analysis/references/native-facts.md`）。**本 skill 不直接手写 `ios-semantics.json`/`ios-coverage.json`/`ios-obligations.json`（机器单写）**，只提供 page 源语义与 `ios-ui-facts.md`。
- **唯一交互点**：无交互追问；歧义回源证据，不回用户。机械检查由 exit code 判定（0=PASS，非 0=FAIL）。
- **无人值守**：机器信号缺失/过期 → 按 §1 阶梯回上游重跑，最多 2 轮；确实取不到 → 记 unknown 与补证步骤，**不伪造布局树**。
- **第一条可见输出必须是一行 UI 分析计划**（读信号 → SwiftUI 路径 → UIKit/IB 路径 → 混合 UI → 页面身份穷举 → 交互证据与收口），然后才开始 §1。

### 无人值守处置阶梯（每道门禁 FAIL 一律套用）

> FAIL → 按命令 `retry_hint`/错误原文派修复并重跑同一命令，**最多 2 轮**；2 轮仍不过或确定模型修不了 → **记欠账放行**（账记全：修过几轮、每轮失败原因、判“修不了”的依据）；要拍板的模型自决并留痕；任何分支不得停机呈报人工。设备/账号类证据可欠账；静态门（facts/信号/语义/溯源）即便开了 `stage_debt` 也照修到 PASS。

## 1. 机器事实与信号读取

| # | 命令 | 产物 | exit code / 失败处置 |
|---|---|---|---|
| 1.1 | `python <runtime>/scripts/a2h_ios.py facts-view --project <target> --scope ui` | `spec/ref/ios-ui-signals.json`（state/binding/event/navigation/lifecycle/constraint/identity/composition/modifier/environment/delegate 十类信号 + obligations） | exit 0 有效；非 0（事实过期/未提取）→ 回 `ios-source-analysis` 重跑 `facts` 后重试，最多 2 轮；仍失败记欠账，**禁手改信号** |
| 1.2 | （可选符号证据）`python <runtime>/scripts/a2h_ios.py mcp-query --project <target> --server <server.json> --request <query.json>` | `spec/ref/mcp-runs/MCP-ID/{artifact,transcript,stderr}.json` + `ios-mcp-index.json` | 失败/超时写 failure.json，绝不写成功索引；真实服务缺工具保留 unavailable/unknown，**禁止换假服务凑通过** |
| 1.3 | 交付前诊断 `python <runtime>/scripts/a2h_ios.py source-check --harness --report-only --project <target>` | 不更新 findings/门禁报告的只读诊断（正式门禁由 a2h-spec 执行） | 非 0 → 按 §7 阶梯补事实 |

### 单写者分区（违者 PROCESS_VIOLATION）

| 文件 | 唯一写者 | 内容 |
|---|---|---|
| `spec/baseline/ios-facts.json` + `ios-obligations.json` | `facts` 命令 | 机器事实/义务 |
| `spec/ref/ios-ui-signals.json` | `facts-view --scope ui` 命令 | 本 skill 十类机器信号 |
| `spec/ref/ios-ui-facts.md` | 本 skill 作者（唯一 owner） | 页面事实可读分析 |
| `spec/baseline/ios-semantics.json` + `ios-coverage.json` 的 page 部分 | a2h-spec `spec-authoring` | 语义/覆盖（机器校验） |
| `spec/.a2h/open-findings.json` | 产生该 finding 的检查 | 未关闭发现 |

- 信号只是待审线索，不是视图运行树；逐个点开信号指向的源代码片段与调用点，**按 §2–§5 解释语义**，不把 token_signal 写成 compiler_binding 或 runtime。
- `NA_CONTRADICTION`、`STATE_VALUE_CONTRADICTION`、`CLAIM_SIGNAL_MISSING` 三类 findings **不允许**以“页面已生成”关闭；只能由产生它的检查复跑后关闭。

## 2. SwiftUI 路径

步骤（每步产物并入 `ios-ui-facts.md` 的 page 语义）：

1. **组合展开**：展开 `body`、`@ViewBuilder`、条件/循环、子 View、`ViewModifier`、自定义 `Layout`，保留层级、参数、条件表达式与 `ForEach` 身份键。**不把结构压成截图控件列表**。
2. **modifier 链顺序**：按调用顺序记录 `padding/background/frame/clipShape/overlay` 顺序影响布局、绘制与命中区域。记录 safe area、alignment、`layoutPriority`、`fixedSize`、`GeometryReader`、`PreferenceKey`/`AnchorPreference` 的依赖方向。
3. **状态建模**：为每个状态记录存储者、初值（保留源表达式文本）、生命周期、全部读写者与变化后 UI（见下表）。**不能仅按装饰器拼写判等价**。
4. **Binding 溯源**：`Binding` 追到 get/set 与真正源状态；值类型 copy、对象引用共享、派生值分别建模。View identity 变化导致的状态重建与 `body` 重算分开记录；`.id(...)`/列表身份/条件移除是否重置状态按实际存储者与身份证据裁定。
5. **副作用与生命周期**：记录 `task`/`task(id:)`、`onAppear/onDisappear`、`onChange`、Combine 订阅的启动、取消、线程/actor 与副作用去重。**不能把所有出现回调都改为只执行一次**。
6. **导航与呈现**：`NavigationStack`/`NavigationPath` 的值、destination 分派、pop、深链、恢复；`sheet(item:)`/`sheet(isPresented:)`、`fullScreenCover`、`alert`/`confirmationDialog`、`popover`、`TabView` 选择均保存其状态驱动关系。

### SwiftUI 视图树分层（组件分类，对齐 android-ui-graph 的视图树分层语义）

| 类别 | SwiftUI 元素 | 图谱角色 | 记录要点 |
|---|---|---|---|
| 容器 | `VStack/HStack/ZStack/LazyVStack/LazyHStack/Grid/List/ScrollView/Form/Group` | parent 邻接（不单独成页） | 对齐、间距、惰性加载、滚动轴与身份键 |
| 导航容器 | `NavigationStack/NavigationSplitView/TabView` | 页面 / 二层 | destination 分派、`NavigationPath` 类型、选择绑定 |
| 呈现容器 | `sheet/fullScreenCover/popover/alert/confirmationDialog` | 二/三层（对应独立 page 节点） | `item:`/`isPresented:` 绑定、关闭回写 |
| 叶子交互 | `Button/TextField/Picker/Toggle/Slider/Stepper/DatePicker/ColorPicker` | 交互叶（is_interactive=true） | action 闭包、绑定方向、无视觉结果的空实现 |
| 身份/数据 | `ForEach(id:)/List(selection:)/.id(_:)` | identity 判定 | 身份键稳定性、元素去重与选择状态 |
| 布局 modifier | `frame/padding/alignment/clipShape/overlay/background/offset` | modifier 链（有序） | 顺序语义、safe area、命中区域 |
| 状态载体 | 下表全部属性包装器 | state ownership | 存储者 / 读写者 / 生命周期 / 身份语义 |
| 引擎承载 | `UIViewRepresentable`/`UIViewControllerRepresentable`/`WKWebView`/Metal/SceneKit/SpriteKit | 混合边界 | make/update/dismantle、Coordinator、清理 |

### 状态装饰器/属性包装器完整分类（区分存储者与读写方向）

| 属性包装器 | 存储位置 | 生命周期 | 身份/共享语义 | 常见误判 |
|---|---|---|---|---|
| `@State` | 视图关联私有存储 | 视图身份存续期间 | identity 变化即重置；值类型 copy 非共享 | 把 body 重算当状态重建 |
| `@StateObject` | 视图持有对象 | 首次身份创建 | 身份稳定则复用；负责创建 | 用 `@ObservedObject` 去创建 |
| `@ObservedObject` | 外部传入引用 | 由外部 owner 决定 | 不拥有、只订阅 | 当作创建者 |
| `@EnvironmentObject` | 环境注入 | 环境存续 | 缺注入运行即崩溃 | 忽略环境范围 |
| `@Environment` | 读环境值 | 环境存续 | 非状态源，读环境 | 当成可写状态 |
| `@Binding` | 读写投影 | 委托源状态 | 双向，追 get/set 到真源 | 只登记存在不追写回 |
| `@Bindable` | Observable 绑定投影（iOS 17+） | 委托 | 双向 | 与 `@Observable` 误配 |
| `@AppStorage` | UserDefaults 键 | 持久化，跨重启 | 写即持久化 | 当内存态 |
| `@SceneStorage` | 场景恢复 | 场景存续 | 场景间恢复 | 当持久化 |
| `@Query/@FetchRequest` | 存储查询（SwiftData/Core Data） | 存储驱动 | 数据身份 | 当普通 @State |

### modifier 链顺序语义（顺序影响布局/绘制/命中，须按调用序记录）

| 顺序模式 | 布局效果差异 | 记录要求 |
|---|---|---|
| `frame` → `padding` | frame 内再留 padding，最终尺寸不同 | 保留顺序，不可合并成单一尺寸 |
| `background` 前后 | `background` 在 `frame` 前只包内容，在后覆盖整框 | 记录 sheet/背景的覆盖范围与绘制层级 |
| `clipShape` + `overlay` | 先 clip 再 overlay 描边在裁剪后边界上 | 记录裁剪与描边的相对顺序 |
| `offset` 不改变布局尺寸 | `offset` 只位移绘制，不改变命中/流内尺寸 | 区分 offset（视觉位移）与真实布局改变 |
| `layoutPriority` / `fixedSize` | 优先级影响父容器分配 | 记录竞争方的优先级与固定尺寸 |
| `GeometryReader` / `PreferenceKey` | 子向上传测量值形成依赖反向 | 记录依赖方向与偏好键读写 |

### 导航与呈现的状态驱动关系（不能只记“跳到了某页”）

| 机制 | 状态驱动 | 记录要点 |
|---|---|---|
| `NavigationStack(path:)` | `NavigationPath` / 类型数组 | 值类型、push/pop 来源、深链与恢复 |
| `NavigationStack` 内联 destination | 条件/枚举分派 | 每条 destination 对应 page、参数 | 
| `sheet(item:)` | 可选 item 非 nil 即呈现 | 关闭回写 item=nil、取消/完成语义 |
| `sheet(isPresented:)` | Bool 绑定 | 关闭回写、交互式下拉取消 |
| `alert`/`confirmationDialog` | 状态触发 | 三层、按钮动作闭环、去重 |
| `TabView`/`tabItem` | `selection` 绑定 | 每项 page、默认选中、状态保持 |

## 3. UIKit 与 Interface Builder 路径

1. **控制器分层**：`UIViewController`/自定义容器、navigation/tab/split controller、子控制器 containment 分层记录；追 `viewDidLoad`、出现/消失、trait 与 Scene 生命周期的真实副作用。**控制器生命周期 ≠ 视图创建次数**。
2. **IB 与程序化合成**：Storyboard/XIB 保存 object ID、`customClass/module`、`IBOutlet`/`IBAction`、segue、prototype/reuse identifier；继续读程序化创建与运行时 override。**IB 与程序化改动共同决定运行布局，不把 IB 文件当全貌**、也不拿程序化覆盖抹掉 IB 初值。
3. **Auto Layout**：记录 first/second item、relation、constant/multiplier、priority、active 条件；content hugging/compression resistance、intrinsic size、safe area **不能只压成绝对坐标**；资源尺寸来自 source/asset scale/真实布局，不靠文件像素猜点数。
4. **交互链路**：追 target-action、gesture recognizer、delegate/data source、Notification/KVO、collection/table diffable snapshot 与复用生命周期。记录回调顺序、cell 复用与选择状态恢复。**状态写说明被哪些 view 读取；禁止只登记 Button 和 addTarget 的存在**。
5. **导航**：同时保留 push/pop、present/dismiss、segue 条件、交互式返回取消、路由参数。

### UIKit 组件与视图层级分类（对齐视图树分层）

| 类别 | UIKit 元素 | 记录要点 |
|---|---|---|
| 控制器容器 | `UINavigationController/UITabBarController/UISplitViewController/自定义容器` | containment、子控制器层级、Scene 生命周期 |
| 视图容器 | `UIStackView/UICollectionView/UITableView/UIScrollView` | 布局轴、复用标识、diffable snapshot、复用生命周期 |
| 叶子控件 | `UIButton/UILabel/UITextField/UISwitch/UIDatePicker/UISegmentedControl` | action、绑定方向、`isEnabled/isHidden` 状态 |
| 手势/交互 | `UITapGestureRecognizer/UISwipeGestureRecognizer/UIControl.addTarget` | 手势冲突、target-action、回调顺序 |
| 导航原语 | `pushViewController/present(_:animated:)/dismiss/segue` | 条件、交互式返回取消、路由参数 |

### Auto Layout 字段表（不得压成绝对坐标）

| 字段 | 含义 | 还原要求 |
|---|---|---|
| first/second item | 约束两端视图（或 safe area/父视图） | 保留相对关系，不换算成点坐标 |
| relation | `=`/`≤`/`≥` | 保留不等式，不取近似点值 |
| multiplier / constant | 倍数与偏移 | 保留原值，区分运行期改 constant |
| priority | 1–1000 | 保留优先级与竞争（hugging/compression 亦记） |
| active 条件 | 是否激活、随 trait 切换 | 记录 size class / 横竖屏 / 多窗口条件 |
| intrinsic / hugging / compression | 内容固有尺寸与挤压/抗压优先级 | 说明对最终尺寸的影响，不经验猜想 |

### 三源合成判定矩阵（程序化 + IB + 静态一致）

| 维度 | 程序化（Swift/ObjC 代码） | IB（Storyboard/XIB） | 静态判定 |
|---|---|---|---|
| 视图结构 | `init`/`addSubview`/`addArrangedSubview` | view hierarchy XML | 运行时 = 程序化(若 override) 或 IB |
| 布局约束 | 代码 `NSLayoutConstraint`/stack 构建 | IB constraint | 二者叠加；冲突靠 `isActive`/priority 裁定 |
| outlet/action | `@IBOutlet`/`@IBAction`/`addTarget` 声明 | 连线（connection） | 名称必须一致，断开则运行时 nil/无回调 |
| 状态/属性初值 | 属性初值、`@State` 初值 | IB attribute inspector | 程序化初值与 IB 初值分别记录，谁后覆盖谁 |

## 4. 混合及特殊 UI

- `UIHostingController` 与 `UIViewRepresentable`/`UIViewControllerRepresentable` 保留双边生命周期：`make/update/dismantle`、Coordinator/delegate、状态反馈与资源清理。
- `WKWebView`、Metal/SceneKit/SpriteKit、自绘 Core Graphics、地图/相机/视频叠层，按“承载”与“内容”分开记录；other 页面在 composition 中说明引擎/承载。**插件只提供分析框架，不保证任意引擎自动转写**，不声称有自动转换器。

## 5. 页面身份与二三层 UI 来源穷举

从应用根、路由目的地、presented controller、sheet/popover、扩展入口找页面候选。小型可复用 View 不自动算独立页面；page ID 按入口与功能稳定分配。同一页面的 loading/empty/error/content、登录态/权限态是状态，不随意拆成重复页。

按以下信号穷举二/三层 UI（下游 `arkts-ui-coverage-auditor` 依赖完整识别；漏识别 → 其启动校验 `BUILDER_INCOMPLETE`）：

| # | 信号（SwiftUI） | 层级 | # | 信号（UIKit/IB） | 层级 |
|---|---|---|---|---|---|
| 1 | `sheet`/`fullScreenCover`/`popover` | 二层 | 6 | `present(_:animated:)`/`UIAlertController` | 二/三层 |
| 2 | `alert`/`confirmationDialog` | 三层 | 7 | `pushViewController`/`show`/segue | 一/二层 |
| 3 | `NavigationStack` destination 分派 | 一/二层 | 8 | 自定义容器/child containment | 二层 |
| 4 | `TabView` 每项 | 二层 | 9 | `UIWindowScene` 多窗口/扩展入口 | 根/扩展 |
| 5 | 页内 `when(状态)` 全屏分支 | 二/三层 | 10 | App Clip/Widget/分享等独立 target | 扩展 |

命中 → 必须产生对应 page 节点（带正确 framework 归属与 page ID）；`when(uiState){Loading/Success/Error}` 等加载/错误态不是页（不拆）。记录 iPhone/iPad、横竖屏、多窗口、语言/动态字体条件；无源码证据的条件保留 unknown。

### 页面字段来源表（字段 → 源，对齐 android-ui-graph 的字段定位表）

| 字段 | SwiftUI 来源 | UIKit/IB 来源 |
|---|---|---|
| framework/language | 源码文件（`.swift` + SwiftUI 标记） | `.swift`/`.m`/Storyboard/XIB |
| 入口 | 根视图/setContent/路由注册 | `rootViewController`/`scene`/AppDelegate 启动 |
| source_anchors | `body`/`@ViewBuilder` 行号 | `loadView/viewDidLoad`/IB object ID |
| 组合 | body 树 + 子 View | view hierarchy + containment |
| 状态所有权 | 属性包装器 + 环境注入 | 属性 + delegate/dataSource + KVO |
| 事件链 | action 闭包/task/onChange | target-action/gesture/delegate |
| 导航/返回 | NavigationStack/sheet/popover | push/pop/present/dismiss/segue |
| 布局 | modifier 链 | constraint 字段表（§3）+ intrinsic |
| variants/accessibility | Dynamic Type/VoiceOver 标注 | trait/accessibility 属性 |

### 页面身份判定铁律（判断“拆不拆页”）

- **判据**：注册为导航/呈现目的地的 @Composable/controller，或页内 `when(状态)` 切出的**全屏**内容，是 page；`Loading/Success/Error`、登录态/权限态、`if let` 局部空态是**状态**不拆。
- **page ID 稳定分配**：依入口与功能，不随文件顺序或扫描命中次序变化；同一页面多个 framework 载体（如 UINavigationController 包 UIHostingController）不重复成页。
- **漏识别后果**：下游 `arkts-ui-coverage-auditor` 启动报 `BUILDER_INCOMPLETE`；因此 §5 信号穷举必须逐条核对，命中即产 page 节点，禁止以“复用”为由跳过。

## 6. 交互证据与收口

- 为用户可触发事件记录：前置态 → 动作 → 状态变更 → 可观察 UI/导航/副作用。跨页/异步动作引用 `../a2h-spec/references/action-contracts.md` 的动作 ID，**禁止在页面重写另一套取消/完成语义**。
- 源码初值与 Preview 固定样例分开，应用实际截图按当前场景标注。**没有指定应用的实际测试或可核验运行证据，不生成运行观察结论（runtime=not_run）；不以录屏为前置条件，没有运行时截图不伪造（screenshot=null 合法）**。
- 有设备证据时须含版本、设备、入口、动作、时间与文件引用；运行截图只能补充该场景观察，不能取代约束/状态分析。
- 输出每页：framework/language、入口、source_anchors（path/role/symbol/line）、组合、有序 modifier、状态所有权、事件链、导航/返回、布局、variants/accessibility、unknown。事实不完整写 unknown 与补证步骤，**不生成假布局文件**。
- 动态字符串、无障碍名称、RTL、键盘/focus、手势冲突、深色模式逐项交代。

### iPhone 截图“仅有条件一致”红线（场景 → 截图 → 核对）

| 截图能做 | 截图不能做 |
|---|---|
| 证明某场景、某设备、某入口、某时刻的视觉显示（附版本/设备/入口/动作/时间/文件引用） | 推导全部导航、状态转移、约束关系、身份/生命周期 |
| 补充已由约束/状态分析得出的该场景观察 | 取代约束/状态分析；把该场景当全貌 |
| 标注已确认为运行证据的真机录制产物 | 无录制时生成 runtime 结论（伪造截图违反红线） |

- 无运行证据时 `screenshot=null`、`runtime=not_run` 是**合法值**，不是缺项；任何“截图即证明布局”的表述一律视为伪造。

### 常见陷阱（iOS 领域，避免微失真）

- **SwiftUI 文件扩展名 ≠ SwiftUI 语义**：`.swift` 文件可能纯 UIKit／数据层；不因 `import SwiftUI` 判定整文件都是视图。以 `body`/View 结构实际判定。
- **宏扩展**：`@ViewBuilder`/`#Preview`/自定义 Result Builder 展开后才是真实视图树；不能把宏调用名当已解析结构。
- **`@ObservedObject` 创建对象**：SwiftUI 状态重建即丢，按持有者/注入点反查真正存储者，不按拼写判定。
- **IB 与代码双写**：同一视图既有 IB constraint 又有代码 add/改约束，运行时可能冲突或代码覆盖；两者都要记，不择一。
- **控件空实现**：`Button(action: {})` / `Button("x") {}` 空闭包仍可交互（is_interactive=true）但无视觉结果/跳转，需标注 no-op stub。
- **复用与身份**：cell 复用、`ForEach(id:)` 身份键不稳定会造成回显/选择错位，按身份证据判定，不臆断。
- **多窗口/扩展入口**：`UIWindowScene` 多窗口、Widget/App Clip/分享扩展是根/扩展级页面候选，不能漏识别。
- **动态类型/RTL/深色**：variant、accessibility、RTL、深色逐项从源取证，无证据保留 unknown，不默认“都支持”。

## 7. 硬约束

- **禁止**手改 `facts-view`/`facts` 产出的机器信号、`ios-facts.json`、`ios-obligations.json` 及任何状态账本（PROCESS_VIOLATION）。
- **不得**把 IB 文件当布局全貌，也**不得**用程序化覆盖抹掉 IB 初值——两者合成运行布局。
- **不得**伪造截图、布局树或运行观察；无运行证据时 `screenshot=null`、`runtime=not_run` 是合法值。
- **不得**仅按装饰器拼写判定状态等价；**不得**把 `body` 重算等同于重新创建所有状态。
- **不得**用“已处理/页面已生成/N/A”清空 unknown 维度；unknown 必须带原因与补证步骤。
- **不越权**：业务计算规则归 ios-feature-analyzer；系统 API/权限归 ios-api-inventory；本 skill 不写 ArkUI，只写源事实与原生语义。

## 8. 读取时机（references）

| 触发时机 | 必读文件 |
|---|---|
| 执行任何步骤前；机器产物/状态写者存疑 | `../ios-source-analysis/references/harness-v2.md` |
| 源事实字段、identity/state/evidence 规则 | `../ios-source-analysis/references/native-facts.md` + `source-semantics.md` |
| 外部资料/MCP 证据 | `../ios-source-analysis/references/external-expertise.md` |
| 逐页填录与正反例 | `references/analysis-v2.md` |
| 转页面行为与状态接口 | `../a2h-spec/references/spec-delivery-contract.md` + `../a2h-spec/templates/page-spec-template.md` |

## 9. 交接

- 前置门闸：本 skill 产出的 page 语义经 `source-check --harness`（由 a2h-spec 正式执行）无新增 finding 后交接。
- 移交：`spec/ref/ios-ui-facts.md`、每 page 的源语义事实（composition/layout/state_ownership/events/navigation/accessibility 及 SwiftUI/UIKit 附加维度）、未被解释的 unknown 与现象清单。
- 下一步提示：交 `a2h-spec`（Phase B 生成 `ui-manifest.md` 与分页 `page_NNNN_*.md`）；功能/API 事实分别归 ios-feature-analyzer/ios-api-inventory。