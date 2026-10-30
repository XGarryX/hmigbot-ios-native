# 根因分诊、责任修复与受影响复查（0.13.5）

对应 Verify 失败回流：F13 读取现有失败并按证据分组；F09 消费影响计算，实际执行修复、当前构建及复查。沿现有 Verify → Execute 修复 → Verify 路径，不新增默认运行阶段，不恢复延期设备/视觉后端。

## 先读取已有失败

```sh
python3 <runtime>/scripts/a2h_ios.py ui-repair triage --project <target> --input <repair-input.json>
```

`reports` 填本工程当前原生产者的 JSON 报告，如 `spec/reports/ios-behavior-check.json`、已有 UI pair 报告或 findings 队列。支持逐条 `failures` / `findings`、`sections` 及 checkpoint 差异，保留每条原文、来源路径/摘要和稳定 ID；字段缺失不会被当成“没有问题”。

根因无法确认时保持独立。确有共同根因时，`root_causes` 每组提供 `id`、`finding_ids`、`owner_stage`、`kind` 与当前日志/源码的 `evidence:[{path,sha256}]`。只允许同责任阶段的问题合组，不因症状或名称相似合组。`code/source/plan/tool/environment/unknown` 分类保留真实边界；源事实/计划问题回原作者，环境/检查器问题不得假装修好了产品代码。依赖当前 `scope_to_tasks` 映射受影响任务，按真正阻塞的消费者及其下游数量排序。

## 固定本轮任务并实际执行

输入结构：

```json
{
  "schema_version": 1,
  "run_id": "<本轮唯一标识>",
  "reports": ["spec/reports/ios-behavior-check.json"],
  "checkpoint_ids": ["<当前全部检查点>"],
  "phase": "intermediate",
  "available_slots": 1,
  "ownership": {
    "checkpoints": {"<检查点>": {"files": ["<目标文件>"]}},
    "components": {"<公共组件>": {"files": ["<公共文件>"], "checkpoints": ["<使用它的检查点>"]}}
  },
  "repairs": [{
    "id": "<修复任务唯一标识>",
    "task_id": "<execution-contract真实product计划项>",
    "finding_ids": ["<triage返回的原finding ID>"],
    "checkpoint_ids": ["<责任检查点>"],
    "write_files": ["<该计划项实际ownership内文件>"],
    "command": {"argv": ["<明确可执行程序>", "<修复程序及参数>"], "timeout_seconds": 300}
  }],
  "build": {
    "argv": ["<原构建入口>", "<本工程参数>"],
    "report": "spec/reports/<当前构建报告>.json",
    "artifact": "<本工程当前HAP相对路径>"
  },
  "checks": [{
    "id": "<原检查器标识>",
    "checkpoint_ids": ["<实际能检查的检查点>"],
    "finding_ids": ["<由该原生产者复查的问题>"],
    "requires_build": true,
    "argv": ["<原检查入口>", "<本工程参数>"],
    "report": "spec/reports/ios-behavior-check.json"
  }]
}
```

示例尖括号内容均从本工程读取；`available_slots` 使用宿主实际剩余容量，不照抄上游固定并发数。所有命令在工程根目录以 argv 执行，不接受 shell 字符串、桌面/系统授权/远程/提权命令。事前核验全部命令、脚本摘要、原报告与目标路径，不能在执行到一半才发现下一检查入口不存在。

已有预算选择时同时传 `usage_ledger`（工程内原账本相对路径）与 `usage_run_id`；每次新修复调用前复核原预算服务。未知或耗尽阻止新修复，不删除在途证据，不阻止本轮收口和可独立执行的构建/诊断。

```sh
python3 <runtime>/scripts/a2h_ios.py ui-repair run --project <target> --input <repair-input.json>
python3 <runtime>/scripts/a2h_ios.py ui-repair check --project <target> --run-id <本轮唯一标识>
```

执行顺序：

1. 复用 `impact_plan()` 的检查点和传递冲突组：共享待改文件的修复串行，无交集组并行；同时遵守原计划 `parents`。未知归属任务串行安排在已定位任务后，不强行并行。
2. 运行明确的修复命令，收集真实退出码、stdout/stderr、耗时和实际目标文件变化。不得写冻结源、Spec、Plan、控制账本或工具目录；越权改动保留原证据并停止。共享 element JSON 仍必须走 F02 的 resource-delta，不让此执行器绕过唯一写者。
3. 按实际改动再次执行 `impact_plan()`。公共组件扩大到所有消费者；未知文件/归属缺失扩大到全量。首次 `initial` 和最终 `final` 始终完整范围；原失败业务要求即使本轮没有代码改动仍须复查。
4. 执行当前构建并绑定实际产物摘要。构建失败时需要构建/设备的检查保持 blocked；明确 `requires_build:false` 的独立静态诊断继续执行。
5. 实际运行所选原检查命令，逐条核对原问题是否在本轮报告消失。命令失败/超时/报告不完整即不能借旧 PASS 关闭问题；未被复查的问题保持 open。一组共因修好了，不代表组内所有业务要求同时通过。

实际覆盖来自原生产者结果，不能由输入的 `checkpoint_ids` 自报：UI 用重新配对返回的真实 pairs；behavior 用当前源/目标绑定且已执行的 observations。状态名与行为case不同名时，检查项提供 `case_map:{"<检查点>":["<原cases里的真实id>"]}`，映射须覆盖本检查所有状态且绑定当前冻结验证合同。通用检查报告须输出本次真实 `checkpoint_ids`；只返回 PASS/空failures、漏A或实际只检查C，都保持A未覆盖、原问题open。原检查程序不提供范围结果时先补其报告适配，不猜已检查。

需要重新采集/配对 UI 时，选择已确认应用、设备、配置和固定场景的官方入口作为命令，不自动猜设备或接管桌面。检查项可附 `pair:{source,target,current,rules}` 四个工程内输入路径；运行采集命令后，适配器再次调用现有 `pair_evidence()` 验证当前构建/源/场景/配置及原始截图/树，按本轮选中的检查点配对。高评分不关闭差异，不将控件一致等同完整视觉/业务验收。

## 结果与恢复

每轮保存到 `spec/reports/repair-recheck/<run_id>/`：输入、原 finding 分诊、计划/实际影响范围、执行日志、构建证明、逐检查/逐问题结论及 `result.json`。`rechecked` 仅代表本轮声明范围实际复查完成；`partial` 保留未完成/仍失败问题；`blocked` 保留输入或执行错误。三者均不修改原检查器的 findings 分区，不代替应用整体验收。

`check` 只读核对本轮收据、当前源/计划/规则、产品字节、构建、原报告和进程日志，不能读取旧绿灯代替当前执行。`run_id` 不能覆盖重用；中断和失败保留现场，修正输入后使用新轮次。修复进程超时后停止当前后续构建/复查，先核对旧子进程是否确已停止写入，不能声称 CPython 的直接进程超时等于整个后代树终止。

该调度属于合作式写权协议，不提供同系统用户的权限隔离。未选择 UI 运行范围时，静态/报告路径照常工作，相应运行材料保持 not_run/blocked，不制造采集或业务通过结论。
