# 并发资源增量与唯一收尾者（0.13.5）

适用于 Execute 的 **Stage 1 UI Batch** 和 **Stage 3 Slice Group**。Stage 0 的资源前置仍先执行；本协议处理并发施工产生的新资源。并发 worker 不直接写 `resources/*/element/*.json`，避免两个任务分别读旧文件后覆盖对方新增键。

## 派发前固定本批/组

先成功运行当前 `execution-contract --apply`。新合同须有 `resource_protocol: task-deltas-v1`。旧合同不能补字段或沿用旧 PASS，按原受审 replan/重新交接流程恢复。

由派发方生成 scope 输入文件，再执行：

```sh
python3 <runtime>/scripts/a2h_ios.py resource-delta init --project <target> --manifest <scope-input.json>
```

输入结构如下，尖括号内容必须从本次任务/合同读取，不能照抄示例 ID：

```json
{
  "schema_version": 1,
  "scope_id": "<本批或组的唯一标识>",
  "closer_id": "<唯一收尾任务标识>",
  "tasks": [
    {"task_id": "<worker唯一标识>", "attempt": 1, "plan_item_ids": ["<合同中的实际计划项>"]},
    {"task_id": "<唯一收尾任务标识>", "attempt": 1, "plan_item_ids": ["<本批组实际计划项>"]}
  ],
  "resources": [
    {"path": "entry/src/main/resources/base/element/string.json", "type": "string"},
    {"path": "entry/src/main/resources/base/element/color.json", "type": "color"}
  ]
}
```

- `tasks` 必须完整列出实际 workers，以及承担 sweep 补漏的 closer 自身。closer 作为一个预登记的提交任务，不再享有资源直写例外。
- `plan_item_ids` 必须存在于冻结合同；全部任务的计划项并集，必须恰好等于本次 writeback 选择的 product 计划项。可由多个任务共同对应一个计划项。
- `resources` 是允许新增条目的完整目标文件清单，按实际模块和 qualifier 填写，不能默认全部属于 `entry/base`。路径须在目标工程模块的 `src/main/resources/<qualifier>/element/*.json` 内。
- 本批完全没有 element 资源目标时可登记 `resources:[]`；全部预登记任务仍提交 `{"resources":[]}`，由 closer 生成零写入合并收据，不能猜写无关路径。
- init 固定源身份、配置、工具规则、冻结计划、任务 attempt 和资源原像。输入变化后不能刷新旧 scope 的摘要；保留旧证据，恢复到合法新轮次。

## worker 提交自身增量

每个 worker 只写自身代码和增量输入文件，结束前提交：

```sh
python3 <runtime>/scripts/a2h_ios.py resource-delta submit --project <target> --scope <scope-id> --task <task-id> --attempt 1 --input <own-delta.json>
```

```json
{
  "resources": [
    {"path": "entry/src/main/resources/base/element/string.json", "type": "string", "entries": [
      {"name": "login_title", "value": "登录"}
    ]}
  ]
}
```

没有新增资源也必须提交 `{"resources":[]}`，不能靠“完成”消息省略。增量属于登记的 task 和 attempt，不能冒用其他任务、补改计划归属或改写已提交内容。返回提交收据及 `$r(...)` 引用清单。媒体/复杂资产沿用 Stage 0 和原资源转换协议，不将二进制资产伪装成 element JSON 条目。

## closer 统一检查、合并

全部 workers 经 Join 验收后，唯一 closer 穷举本批/组代码的 `$r(...)` 引用，对照源资源核查缺项，将 sweep 补项写入**自己的增量**并 submit；没有补项也提交空增量。所有增量齐备后：

```sh
python3 <runtime>/scripts/a2h_ios.py resource-delta check --project <target> --scope <scope-id> --closer <closer-id>
python3 <runtime>/scripts/a2h_ios.py resource-delta merge --project <target> --scope <scope-id> --closer <closer-id>
python3 <runtime>/scripts/a2h_ios.py resource-delta check --project <target> --scope <scope-id> --closer <closer-id> --require-merged
```

同一模块/qualifier/type/name 的相同条目去重；值或属性不同则报告冲突并停止，不能按完成先后覆盖。原有条目保留。所有文件预检通过后才落盘；单文件采用原子替换，跨文件使用项目级互斥和先写日志，保留中断恢复依据。

closer 返回 `scope_id`、`closer_id`、合并收据路径和原 writeback manifest。主线程使用原回写入口：

```sh
python3 <a2h-execute>/scripts/apply_writeback.py <writeback-manifest> --project-root <target> --resource-scope <scope-id> --resource-closer <closer-id>
```

对于新合同的 batch/group，缺参数、计划项不匹配、未全部提交、未合并或收据过期，均在原引擎写 brief/账本前拒绝。原 indexed receipt 记录所消费的合并证明。资源已合并只证明资源状态，不替代编译、结构或业务验收。

## 中断与续跑

- `check` 和 `--require-merged` 只读，不创建目录/锁/报告；前者 ready 只说明可合并，不能代替后者的 merged。
- 相同输入的重复提交与合并保持幂等；任务/源/计划/资源被外部修改时拒绝借用旧收据。
- 存在 pending 事务时，先由登记的 closer 执行 `resource-delta recover --project <target> --scope <scope-id> --closer <closer-id>`。恢复核对冻结输入和各文件原像/后像，外部改动则停止，不能直接删除日志、重跑 init 或手工盖写。
- 合并后继续新增资源，必须按当前状态开新的完整 scope；不能在原合并收据后直写 JSON。writeback 的重放仍须当前证明有效；后续批次已改变资源时不能把旧收据当作本批的当前状态。
