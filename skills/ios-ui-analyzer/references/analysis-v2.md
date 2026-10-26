# UI 事实：组合、事件、状态与布局

先执行 facts-view --scope ui。输入是真实页面入口、源码、IB 与机器信号，输出是页面规格与 v2 原生语义。扫描只给信号，不能推定视图运行树。

SwiftUI：逐 body 分支读取组合顺序、modifier 顺序、ForEach key、id 重置边界、State 创建者、StateObject/ObservedObject 所有权、Binding 双向流、Environment 范围、task(id:) 启停、Navigation/sheet 参数和关闭后的状态。UIKit：读取 controller 创建/包含/appear/disappear/deinit、view 构建、target-action、delegate/dataSource、outlet/segue 与程序化覆盖。

每个用户动作记录：入口控件及触发条件→handler→校验/状态改变→服务或委托→显示结果。状态写说明被哪些 view 读取；禁止只登记 Button 和 addTarget 的存在。

Auto Layout 保留 first/second item、relation、constant、priority、intrinsic/hugging/compression，核对运行期改约束。资源尺寸必须来自 source/asset scale/真实布局，不能由文件像素猜点数。Snapshot 有真实设备与场景才登记；Preview 不作运行行为证据。

输出模板：page ID、framework/language、入口、source anchors、composition、ordered modifiers、state ownership、event chain、navigation/return、layout、variants/accessibility、未知。value 对象和 fact_ids 与机器图链接，状态 states 字段精确匹配。target mapping 单独写入决策，源事实不含目标装饰器猜测。

失败恢复：机器未知回 provider 或源码；动态 UI 回真实场景采集；来源不符回所属页面 owner。harness-check 中 NA_CONTRADICTION、STATE_VALUE_CONTRADICTION 和 CLAIM_SIGNAL_MISSING 不允许以“页面已生成”关闭。

## 从源码填写页面模板

1. 确认页面身份与生产入口，再按 body/controller 的真实组合给稳定的页内节点 ID。子组件、覆盖层、条件分支和复用单元分别列行；节点 ID 只用于该页结构引用，不替代 page ID。
2. 按 [页面模板](../../a2h-spec/templates/page-spec-template.md) 填组件层级、布局约束、ArkUI映射、资源引用四表。保持父子关系、出现条件、交互区域与源证据；不从截图颜色或文件像素猜数值。
3. 布局逐项读取容器、对齐、间距、尺寸来源、伸缩/截断、safe area和trait条件。源未写固定尺寸时保留“由父容器/内容测量”，不要填统一经验尺寸。
4. 为每个可操作节点回走 handler→源状态→服务→回写→UI。跨页面或异步动作引用 [动作合同](../../a2h-spec/references/action-contracts.md)，禁止在页面重写另一套取消/完成语义。
5. 用实际源码状态检查至少一个常态和每个真实条件分支。Preview/mock、推断与设备截图分别标记。未确定分支保持 unknown 并回流，不能用 N/A 清空表格。

## 通用正反例：SwiftUI条件与Binding

假设父视图以 `if selected != nil` 展示编辑子视图，子视图接收父状态的 Binding。应列出条件节点、子节点及else分支，追 Binding 的 get/set 回父状态，记录提交、取消和父条件变更时的读写链。继续核查 `.id(...)`、列表身份或条件移除是否改变状态生命周期。

合格描述：“条件为真时创建子树；编辑通过Binding写回父Owner字段；子树移除后的状态去留按实际存储者与身份证据记录。”目标状态表写明确 Owner.state 与事件回写，组件表写实际 ArkUI 候选及保留约束。

不合格描述：“编辑页有输入框”“Binding改成子组件本地状态即可”“body重算等于重新创建所有状态”。源码只证明出现控件不能证明写回链；派生Binding必须继续读set逻辑。

## 通用正反例：UIKit约束

假设标题 leading/trailing 约束到safe area，图片宽度约束有priority 750，横屏时程序改constant。应同时记录IB初值和生效的程序化覆盖、relation/multiplier/priority，以及hugging/compression对最终宽度的影响。

合格描述给出约束关系与激活条件，再解释目标布局如何保留挤压/伸缩行为；若ArkUI无法直接对应优先级，记录明确映射与验证场景。

不合格描述：“标题宽320、图片宽80，使用Row布局”。除非这些固定值确为有效源合同，否则它丢失相对约束、动态字体和横屏条件。运行截图只能补充该场景观察，不能取代约束分析。
