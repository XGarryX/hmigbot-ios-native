# 应用 UI 测试与配对证据

本规程描述可选 UI 验证的边界和入口，不作为项目已运行或验收通过的证据。适用范围为任务明确指定的应用、设备/模拟器、构建和场景。先读 [应用 UI 验证边界](../rules/app-ui-validation-boundary.md)；禁止桌面接管不等于禁止官方应用截图或测试。

## 实际入口

| 路径 | 作用与边界 |
| --- | --- |
| `scripts/ios_ui_automation.py` | iOS 官方应用截图、控件查询与固定回放适配；prepare/run/validate 的参数以当前 `--help` 为准。生成测试设施不等于真实执行成功，实际结果来自原测试退出码和绑定收据。 |
| `scripts/ios_ui_automation.py collect` | 从本次已结束的原 XCTest 结果恢复附件和收据；不重新执行 UI，已有完整收据只读验证后复用。恢复与本次实际测试分别记录。 |
| `scripts/harmony_ui_automation.py preflight/prepare/run` | 指定模拟器与应用后，优先官方 Emulator 的无窗口实例、控件布局和截图能力；仅所需能力缺失时使用 Hypium 测试 HAP。预检核对实际 HAP 最低 API 与镜像 API，不能用降低项目最低版本替代兼容测试环境。 |
| `scripts/ui_validation_evidence.py validate` | 离线核验证据文件摘要及应用/设备/构建/配置身份；当前身份用 `--current` 传入。校验旧证据文件完整不表示它仍属于当前构建。 |
| `scripts/ui_validation_evidence.py pair` | 消费当前 iOS 与鸿蒙对应检查点，按规则和实际差异给出配对结果；只有一端不能记双端通过。 |
| `scripts/ui_validation_evidence.py impact` | 根据明确的改动与检查点/共享文件归属生成复查范围，未知归属扩大范围；不猜测全部依赖。 |
| `scripts/ui_validation_evidence.py benchmark` | 读取实际范围和计量，比较同口径前后记录；不把预期收益或口头宣传数字写成实测。 |
| `scripts/ui_validation_evidence.py bind-mapping` | 将调用者提供的控件对应关系绑定到当前源码位置、引用与文件摘要；不改 iOS 源或自动猜测对应关系。 |
| `scripts/ui_validation_evidence.py configuration` | 通过 Apple CLI 只读查询明确 UUID 的模拟器主题、字号、语言和区域，保留命令/原输出/缺口。属于设备配置，不代替应用自身覆盖的配置。 |

各入口应先读取自己的 `--help`。鸿蒙设备执行须有实际可用的官方 CLI/测试后端和明确目标；测试准备、测试执行、证据消费分开记账，不用离线配对器冒充设备执行。旧 scenario/UI/visual 扩展及角色仍按 [延期标记](DEFERRED-CAPABILITIES.md) 处理，不恢复业务样例、默认账号数据或 Android 操作脚本。

源端采集也由 spec 主线消费：init 选择源 UI 策略；`source-analysis` 的 source-ui 步骤按明确的 `ui_capture` 请求实际调用原 iOS 适配器或校验复用；`spec-authoring` 将绑定的原图/控件树提供给对应页面作者，并渲染原生观察段与既有 meta 候选。协议见 [源端 UI 采集与规格消费](../skills/ios-source-analysis/references/source-ui-capture.md)。工作缓存留在目标 `.build/hmigbot-source-ui/`，只发布原收据和列举附件到 spec；既不把构建缓存软链带入合同，也不把一次首屏观察冒充全部页面/业务完成。

## 运行与验收

1. 固定实际应用、构建摘要、源版本、设备标识、语言/区域、主题、字号、场景和检查点。设备选择直接使用已确认范围；真实缺失的输入具体列明，不扩大到个人真机。
2. 从已知入口和明确测试数据执行稳定控件定位、就绪等待、固定步骤与断言。保存实际 argv、原输出、退出码、截图、控件信息、时间和产物摘要；失败和有限恢复均保留。
3. 按页面/状态/组件匹配源与目标检查点。控件证据是测试系统暴露的层级，可能不包含自绘或框架内部结构；缺口明确保留。
4. 视觉差异与事件、导航、错误处理、持久化行为分别判断。相似截图、结构 PASS、编译成功互不替代。字体和平台控件差异需要当前规则及来源说明，不能以一个宽泛容差掩盖遗漏。
5. 首次与终态按既定范围完整核验；中间改动按实际受影响页面和共享消费者复查。只有源/目标、配置、规则、场景与产物仍匹配时才可复用相应结果；复用不冒称本次又执行了设备测试。

基础截图/控件观察使用明确的 `observations_only` 请求及配对 `--observations-only`。语言、主题、字号未实际观测时保留具体缺口，不为一次截图强制修改产品加入 probe 或构建测试 HAP；该模式不授予 UI/业务验收通过。两端平台本地场景名称不同，可用 `--business-recipe` 指定同一业务配方；其规范摘要和完整检查点必须同时匹配两份原始证据，不能手改截图收据凑相同名称。

具体应用转换的报告推荐写 `spec/reports/ios-ui-pair.json` 与 `spec/reports/ios-ui-preflight.json`；原始采集按本次选定目录保存在项目 `spec/ref/ui-validation/`。官方截图必须写入已创建的专用目录，并有界等待完整 PNG 落盘；不要扫描用户图库当作截图收集步骤。具体 build/source/device 已改变时旧观察失效；无关测试缓存和进度文件不充当产品构建输入，真实产品及源文件软链仍遵循原完整性检查。

具体应用转换的结果和原始证据放在该鸿蒙工程 `spec/` 内，进度为 `spec/reports/ios-progress.md`。为优化工具开展的验证使用独立维护目录，其进度、报告、中性样例、实测采集和测试产物均保存在应用项目与发行树之外，不写入应用转换记录；这是维护工作与应用运行记录的范围区分，不增加转换门禁。应用验证未选择、缺环境和实际失败分开；未选后端或缺桌面屏幕权限不成为基本转换、构建和报告的总门禁。

## Preview 与当前测量边界

Apple Preview 可检查固定输入下的长文字、空态、主题和大字号组件；保存对应配置和输出，标记为 preview，不能作为真实业务链路已运行的证明。宿主没有实际可执行 Preview 入口时记录具体不可用条件，不使用桌面自动操作凑数。

能力声明分别报告“允许”“宿主可用”“已实现入口”“实际执行”“验收结果”。每个项目必须引用自己的当前收据；工具维护回归、中性样例通过或其他项目截图不增加该项目的转换进度。不承诺未实测的端到端提速百分比。

## 跨端匹配和可解释判定

现有 `pair` 同时输出兼容的稳定 ID 结构结果，以及每个检查点的 `cross_platform`、`assessment` 和总 `ui_assessment`。前者列出节点索引、匹配方法、候选、歧义与覆盖范围；后者列出差异、缺失证据、计分依据和不能关单的具体原因。没有控件数据、截断树或 unknown 配置不能得到完整分数。

匹配依次使用：调用者明确提供并绑定源码的映射、两端唯一稳定语义标识、两端唯一的文案与类型；最后只输出归一化位置提示。运行时 widget ID 不用作跨运行身份。文案仅做 Unicode NFC 和空白规范化，不去掉小数点、符号、大小写或自行中英翻译。文案/类型匹配标记为推断，不具有源码身份已确认的效力；重复文案保留所有候选，不贪心选第一个。iOS point 与鸿蒙 pixel 通过各自有效视口归一化，不采用固定 ±10px。未匹配意味着证据不足，不能直接判定目标控件未实现。

可选映射草案使用 `controls[]`；每项包含 `control_id`、`checkpoint_id` 和 `ios` / `harmonyos` 两个端点。每个端点包含相对于所选源码根的 `path`、`line`、`selector`；selector 使用 `identifier`，或同时给出 `role` 与原始 `label` / `descendant_label`。通用 Button 标签下的实际子文本可提供候选，原标签及推导来源保留；不能由旁边的无关文本命名控件。用 `bind-mapping --input <草案> --source-root <iOS源码> --target-root <鸿蒙工程> --output <工程spec内映射>` 生成 `hmigbot-ui-controls-map/1`。消费时用 `pair --control-mapping <映射>`；真实锚点文件或对应行改变必须更新映射，无关页面改动不强制重建所有映射。绑定源码字节不等于机器已理解源码语义，映射对应关系的来源明确为调用者提供。没有源码证据时不伪造全量映射、不强制修改原 iOS 源或给全部控件加 ID。迁移规则应保留源中真实已有的 accessibility 标识，并在所需目标控件上按 ArkUI 的唯一 `.id()` 能力实现。

差异至少区分内容、状态、类型、相对布局、配置与单端对话框/Sheet。原生树不暴露的颜色、遮挡或自定义弹窗不能靠标签猜测。可用 `--visual-observations <审阅文件>` 引入 human/agent 的实际读图观察：schema 为 `hmigbot-ui-visual-review/1`，绑定两份 manifest SHA256；每项绑定 checkpoint_id 和两端原始 screenshot SHA256，记录 category、severity 与具体 reason。报告保留外部审阅来源，不冒充离线算法自动检测像素。无任何外部 LLM 服务、固定模型或新权限依赖；运行时不擅自上传图片。

可选 `--exceptions` 只消费逐差异的明确复核决定，不自动给设计/动态内容豁免。schema 为 `hmigbot-ui-exceptions/1`，绑定当前两份 manifest，`decisions[]` 每项带 checkpoint_id、difference_id、observation_sha256、category、reason、reviewed=true 和 evidence。evidence 指向实际 source（platform/path/sha256/line/quote）或设计决定引用的 capture（platform/path/sha256），逐项校验。动态/配置豁免要求源码证据；配置豁免还须存在实际观测差异。应用错误弹窗、控件类型和状态错误不能通过这类豁免排除。摘要证明绑定，不认证某个人实际作出审批。

差异清单评分采用工具自己的局部 rubric：high 扣 0.05、medium 扣 0.02、low 扣 0.01，有已验证豁免的不扣。`rubric_score` 是规则分，**不是截图像素相似度**；证据不全时为 null，另列临时规则分。即使单条 high 差异只将分数降到 0.95，仍不能关闭。`equal_control_observations` 仅说明本次比较的控件观测一致，不宣布完整视觉或业务验收。

原生 iOS 采集保留 1000 节点总预算，深度上限为 64，达到限制必须标记截断；SwiftUI 深容器链不应在原来的 16 层直接丢掉正文。`configuration` 的 `simctl ui UUID appearance/content_size` 为官方只读查询；`defaults` 读取保留原结果和错误，不默认 en/light/1.0。应用实际观测优先来自已明确的 App probe / Harmony AbilityContext、ResourceManager；设备级设置和测试请求分别呈现，不能覆盖应用 unknown。鸿蒙不使用 Android 的 getprop/settings 命令冒充官方配置能力。

官方依据：[Apple XCUIAutomation](https://developer.apple.com/documentation/xcuiautomation)、[SwiftUI EnvironmentValues](https://developer.apple.com/documentation/swiftui/environmentvalues/)、[HarmonyOS Component ID](https://developer.huawei.com/consumer/en/doc/harmonyos-references-V13/ts-universal-attributes-component-id-V13)。对应关系、候选算法、差异分类和 rubric 为本工具实现，不能称为官方判定规则。
