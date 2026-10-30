# 页面、子内容、状态和任务参考材料

本规程贯穿 Spec → Plan → Execute → Verify。它消费现有 iOS page-spec 和已选原生观测，不另建 Swift/ObjC 解析器或采集后端。

## 由已有规格生成完整清单

Spec 作者完整填写 page-spec 的 `组件层级`、`状态接口`、`交互与导航`，包括弹层、隐藏标签、错误/空内容状态、关闭和确认后的数据刷新；所有描述保留真实 iOS 源锚点。未知内容保留 unknown 和恢复条件，不用正常态截图替代。

不能在没有结构化状态/交互库存时只生成一个 page 单元报完整。确实无状态或无交互的页面，在相应小节写明确的 `not_applicable: <源依据与原因>`，保留当前源锚点；有实际内容则填表，不以不适用删除真实义务。

Plan 的 indexed 任务和所有权形成后、`plan-ir` 冻结前执行：

```sh
python3 <runtime>/scripts/a2h_ios.py ui-delivery draft --project <target> --apply
python3 <runtime>/scripts/a2h_ios.py ui-delivery check --project <target>
```

`spec/baseline/plans/ui-delivery.json` 从现有规格逐行导出稳定 ID：页面外壳、每个组件、每个状态、每个交互都进入清单。生成/装配/核验任务与实际 UI 计划项绑定，输出范围来自原任务所有权。修改清单不能删掉源表中的义务，Plan 会重新导出对账并冻结文件摘要。无 UI 的工程不需要建立此清单。

draft 负责导出源义务；Plan 作者随后为每个非 page 单元填写 `target_bindings`，再运行 check 和 plan-ir：

```json
{"unit_id":"<真实unit_id>","path":"<原UI任务拥有的.ets文件>","symbol":"<本单元实际目标属性/组件/处理函数>"}
```

状态的 symbol 必须与规格中的目标 Owner.state 对应。默认在 `build` 中核对状态的显示读取；若按已审设计使用独立渲染方法，Plan 可额外声明 `render_symbol` 为该方法名。所有绑定在生成前冻结，不能生成后任挑一个无关符号补账。源规格尚无具体目标接口时，先完成本次技术映射设计，不以页面壳冒充全部子内容。

## 按单元、状态和区域分配参考

Plan 作者在冻结前，依据实际 source-ui 观测和规格对应关系填写清单 `reference_bindings`：

```json
{"unit_id":"<draft产生的真实unit_id>","checkpoint_id":"<现有采集的真实检查点>","region":[0,0,320,640],"required":false}
```

`region` 是源截图像素坐标 `[x,y,width,height]`，只负责整个画面时可省略。必须核实状态、页面、场景和区域；不能把示例 ID、尺寸或正常态画面填给错误态/弹窗。多个单元可引用同一张图的不同区域。尺寸越界、错源、错配置和文件摘要变化会被拒绝。

未选采集或未采到状态时保留对应 gap 和原有义务，不伪造截图。只有当前任务已明确必须具备该观测时才标 `required:true`，其缺失只约束受影响页面生成，不能扩成全局设备门禁。

执行交接器复用 `authoring_observations` 的原始 XCTest 证据验证结果，生成 `spec/execution/ui-delivery/packets/page_####.json`，在逐页 meta 中给出路径和摘要。源码推导结构、真实截图与 Preview 的证据强度继续分开。

## 页面作者必须消费材料

```sh
python3 <runtime>/scripts/a2h_ios.py ui-delivery consume --project <target> --page <page-id>
```

该命令实际读取本任务必需的源、规格、原始图片和结构字节，先完整解析 JSON/XML 再返回结构；返回每张图的绝对路径及单元/区域，生成独立消费收据并记录真实读取量。作者必须继续使用宿主图片读取能力检查返回的原始像素，CLI 读取图片字节不代表已经完成视觉理解或验收。禁止只查看 meta 摘要后声称看过图片。

包与清单必须分别是 execution-contract 固定的输出和输入，不能由 worker 删除 `inputs` 或改变义务。材料内容变化使旧消费失效；材料位置改变时，核验同内容摘要并重新交接/消费，既有实现文件仍须逐项复核，可以保留未受影响的输出，不无故重做全部页面。

## 生成、装配与收尾对账

作者为自己负责的每个 unit 写实际输出证据，生成和装配分别提交，不能用“页面文件存在”代替所有状态已经交付。回执路径：

```text
spec/execution/ui-delivery/receipts/<sha256(真实plan_item_id)>-generated.json
spec/execution/ui-delivery/receipts/<sha256(真实plan_item_id)>-assembled.json
```

格式如下，均用当前真实输入及输出值：

```json
{
  "owner":"<真实plan_item_id>",
  "phase":"generated",
  "inventory_sha256":"<ui-delivery.json规范JSON摘要>",
  "units":[
    {"unit_id":"<本任务的真实unit_id>","outputs":[
      {"path":"<原计划允许的目标文件>","sha256":"<当前文件摘要>","line":1,"symbol":"<实际实现符号>"}
    ]}
  ]
}
```

`inventory_sha256` 取 `sha256(json_bytes(inventory))`，使用工具统一排序序列化；消费结果的 `packet.inventory_sha256` 已给出该值。装配完成后换为 `phase:assembled`，必须列真实装配/接入符号。匿名视图可用实际 ArkUI 结构符号及准确行号，但不能拿一个空壳符号掩盖没有实现的状态或交互；语义核验和原结构/业务检查仍执行。

不同 unit 的实际 `(path,line,symbol)` 不能无区分地复用同一位置。每个状态还必须分别提供 `role:state_definition` 的目标属性声明，及 `role:state_render` 的显示读取锚点；只有属性声明、没有所绑定渲染函数中的状态读取，或对应条件分支为空，均不能交付该状态。目标 symbol 只出现在注释/字符串中、处理函数为空也会拒绝。这仍是有界静态检查；真实状态到达与业务副作用继续由原运行/行为专项核验。

```sh
python3 <runtime>/scripts/a2h_ios.py ui-delivery verify --project <target> --item <plan_item_id> --phase generated
python3 <runtime>/scripts/a2h_ios.py ui-delivery verify --project <target> --item <plan_item_id> --phase assembled
```

`apply_writeback` 在原引擎写 brief/进度前执行这两个检查。缺任一计划内组件/状态/交互、没有当前消费收据、引用不存在/过期符号或超出写权会拒绝结算。单元交付 PASS 仅是静态完整性，不是业务、运行状态或整页视觉 PASS；Verify 继续消费同一清单并按已选范围核验真实效果。
