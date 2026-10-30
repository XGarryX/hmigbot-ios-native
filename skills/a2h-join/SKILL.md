---
name: a2h-join
description: 子代理 join 协议工具库：由派发型 skill 的 join 点调用 join_gate、wait_for_artifact 和 audit_join_coverage，核验真实完成观察及产物。不要用于独立迁移阶段或业务行为验收。
metadata:
  type: tool
  domain: migration
  tags:
  - utility
  - migration
---

> **0.13.4 统一合同（优先于历史示例）**：先读 [执行交界合同](../a2h-run/references/execution-boundary.md)。源读取、选定构建配置、SwiftSyntax/facts、源 AC 和 indexed 计划由当前 git 上游唯一生产；从 execute 起使用本技能的 Garry 实施/收口方法。只使用宿主实际支持的派发字段，不照抄 `agent_type`。已有授权直接沿用；依赖失败输入的任务保持 blocked，不降低静态门禁。权限按交界合同区分：禁止桌面远控；指定测试应用/模拟器的截图、控件查询和固定回放可按已确认范围执行，Preview 不证明业务运行。录屏及未指定设备不在此授权内，未执行项如实记 not_run。未经授权不运行遥测上传。工具修复、工具验证、项目转换、HAP 构建和完整迁移验收分别报告，不能用局部 100% 代表全部完成。



> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../ios-source-analysis/SKILL.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

> **路径约定**：下文 `$SKILLS_ROOT` = 本套 skills 的安装根目录。执行任何脚本前先设一次：`SKILLS_ROOT="$(cd "$(dirname 本SKILL.md)/.." && pwd)"`（用户级安装=`~/.agents/skills`；项目级=`<project>/.agents/skills` 或 `<project>/skills`）。

# a2h-join — 子代理收口协议零件库

## 宿主任务范围

顶层及内部任务都通过实际 `CODEX_THREAD_ID` 唯一定位宿主 sessions 中自身完整原生文件，核对第一条 `session_meta` 的身份。顶层使用当前项目；内部子任务自己派发、自己收口时，必须传 `--project` 的真实绝对路径以及 `--rollout` 的自身原生文件。仅检查其直接孩子，孙任务由对应派发者收口。继承的 `metadata.cwd` 与目标不同必须披露，并检查旧目录未被误写。

分流前先根据实际 `CODEX_THREAD_ID` 定位宿主 sessions 中当前任务自身的元数据，子任务误传父会话日志也会拒绝，不得借顶层分流绕过身份核对。事后审计的哈希及字节数来自本次解析的同一批完整原始字节；文件后续增长不改写已观察记录的指纹。

完整历史派发的子线程会继承父日志，其中可能包含父线程尚未返回的spawn。只有自身session_meta中的真实父线程ID与继承元数据匹配，并收到由该父作用域发往本线程、来源和路由均可信的原生NEW_TASK时，才把该边界之前的调用归属父历史。所有原始字节仍完整解析并计入哈希；坏行、伪造正文、身份不符或边界之后新增的外部元数据都会拒绝。自身边界之后的未返回派发仍须处理。

适配器直接解析原生日志，原二进制保持不变。当前任务可由有效 `list_agents` 的 completed 观察，或平台原生 `agent_message` 中有路由和工具来源的 FINAL_ANSWER 信封证明完成；普通 user/developer 消息、复制的正文和产物存在都不构成完成信号。原生信封必须来自本轮真实派发的直接子任务，author/recipient、Sender/Task name及每项collaboration provenance一致。宿主若将正文存为非空encrypted_content，允许input_text仅保留完整信封头；不解密或依赖正文关键词。消息ID与完整信封摘要都记入完成来源，不支持或不明确的格式保持未完成。

所有派发名在完整宿主历史内唯一，带尝试/轮次后缀；旧任务与旧尝试消息不能复用。仍须在派发前写expected-set并核对交付内容。新增的最终消息或控制终态路径必须有匹配且非空的产物声明；不能仅凭.done文件或完成正文放行。历史completed路径保留原兼容行为，技能不能用它省掉事前产物约定。

已登记尝试的最后一次派发返回后，仍须再次单独调用当前派发者子树的完整 `list_agents`；与派发并行的列表、窄范围或其他筛选结果不能代替。最终消息已可靠返回但任务从列表消失时，完整空列表不抹掉该完成事实，仍须通过产物门禁。明确失败的派发仍要补派并完成；列表错误后用新的完整有效列表恢复，不能以零句柄或不相关任务放行。

followup/send_input/resume调用开始即清除旧完成；返回后须重新观察完成。当前原生最终信封没有已核验的子任务续作编号，因此**同句柄续作后的最终消息不单独证明本次完成**；需要控制返回后才发起的完整list_agents观测到completed，或使用新的唯一任务名。明确error保留失败与旧完成证据，但未执行的续作请求仍阻断收口，真实重试完成后才恢复。未知控制返回结构保留为不可核验，不能当作失败来恢复旧completed，也不能直接当作成功；须补返回之后新发起的完整列表completed。控制尚无返回不能判结束；close/interrupt的previous_status为running时不算成功，关闭仍运行任务记为killed，后续空列表或迟到最终消息不能把它升级成成功。

事后 audit 使用同一作用域，只读取原生日志，记录真实路径、线程身份和 SHA-256，不写 join 账本，不代替实际 join。实际运行仅使用宿主 sessions 中未经修改的原始文件；对照夹具只用于回归。原入口支持的状态、契约检查、静态豁免和账本格式保持一致；未绑定 spawn 返回值不得以零句柄放行。日志更换物理文件时暂停排查，不拼接记录。

用户授权同会话从空工程重跑且旧尝试失败时，先读 [核验恢复与尝试登记](references/recovery.md)。只有完整归档、核验空备份、恢复并安装后才能登记新尝试。Gate 完整解析原日志并核对真实登记调用及成功输出、恢复证据和实现指纹；当前任务仍按原门禁验收，旧失败留在独立历史审计。重复 bootstrap 不移动边界。状态丢失或额外 begin 调用须停止排查，不能删除记录来放行。

## 背景（为什么需要它）

不同宿主的完成通知方式不同：使用其真实派发、等待与通知接口。收到平台原生最终结果时按上面的信封和产物规则核验；没有可靠通知则有界等待、列举状态。不能只在正文里说“等待”，也不能把任意完成文本当真实终态。本技能提供机械零件拦截以下问题：

- **静默卡死**：模型"字面等待"结束回合（issue #23，AIPPT 断网后挂 4.5h）
- **假交接**：completed ≠ 验收——子代理报完成但产物缺失（实测：7 个分片
  agent 派完即停、functional_points 从未合并）

## 三个零件

### 1. join_gate.py — 收口硬闸（join 点必调）

```bash
python3 $SKILLS_ROOT/a2h-join/scripts/join_gate.py --project . --join-point <名字>
```

- 机械枚举本次实际宿主尝试的全部 `spawn_agent` 句柄（不信模型自报）
- 按当前任务的有效completed观察或可信原生最终信封判完成；续作、失败及终止按上文分别处理
- 对已完成任务核对expected-set产物；新增最终信号路径缺匹配非空合同仍失败
- exit 0 → 追加 `spec/a2h/_work/join-ledger.jsonl`；exit 1 → 打印缺口清单，
  **禁止发完成报告/进下一阶段**；exit 3 → 按提示补信息（如先调一次 list_agents）
- 条款⑤ fire-and-forget 豁免 = 脚本内静态 allowlist（改表须过评审），
  正文 `[fire-and-forget]` 声明只是文档层

### 2. wait_for_artifact.py — 活性探针（条款②辅助）

```bash
python3 $SKILLS_ROOT/a2h-join/scripts/wait_for_artifact.py --path 'entry/**/*.ets' --window 120
```

⚠️ **不是完成判断器**——文件会中途落盘，存在/条数不等于完成。完成信号来自有效completed观察或上文定义的可信原生最终信封；同句柄续作适用更严格的重新观察规则。
本脚本只回答"产物还在长吗"：exit 0=活；exit 2=零增长（结合连续 wait 超时
按条款②判死活）。

### 3. audit_join_coverage.py — 事后审计（回归 oracle + ledger 防伪）

```bash
python3 $SKILLS_ROOT/a2h-join/scripts/audit_join_coverage.py <rollout.jsonl>... \
    [--project <项目绝对路径>] [--ledger spec/a2h/_work/join-ledger.jsonl] [--json out.json]
```

对每个句柄判 joined / fire-and-forget / UNJOINED，出可信完成观察的覆盖率；此处joined只表示审计到完成信号，实际交付仍以执行时gate的产物检查为准。
`--ledger`核对账本中声明的完成是否出现在当时读取的完整原始字节快照，核对完成来源和消息身份；后来才出现的最终消息不能回填早先账本。
实际宿主调用只接受自身一个原始文件；历史多文件对照仅用于离线回归。已登记尝试的账本必须匹配 attempt 身份及当时读取的原始字节快照，不能借用稍后才出现的完成观察。

## expected-set 契约（治"completed 但产物缺失"）

并行派发（T1 类 join 点）在 **spawn 前**由派发方落盘：

```json
// spec/a2h/_work/expected_<join点>.json
{"join_point": "stage1_batch2",
 "task_names": ["conv_page_*"],
 "artifacts": [{"path": "entry/src/main/ets/pages/*.ets",
                "min_count": 8, "min_bytes": 200, "json": false}]}
```

- 契约必须来自**派发方**——不认子代理自报 manifest（摸鱼者的 manifest
  会与其半截产物完全吻合）
- 原子.done文件可辅助交付记录，但**新增FINAL_ANSWER路径不能只凭该文件验收**。派发者仍需至少声明可核验的实际文件、数量、大小和适用格式要求；不要把自报正文变成唯一交付依据。
- `task_name` 必须唯一化（带 page-id/slice-id/round-N 后缀），这是
  task_name↔completed 机械配对不误配的前提

## Gate收口判定（audit核对完成观察与账本，不重复产物验收）

| 状态 | 判定 |
|---|---|
| 当前completed观察 + 原产物检查通过 | ✅ joined（原兼容路径） |
| 可信原生FINAL_ANSWER + 匹配非空expected-set通过 | ✅ joined |
| 实际close/interrupt返回previous_status=completed + 匹配非空expected-set通过 | ✅ joined |
| 同句柄成功续作后只有最终文本，没有控制返回后新发起的完整列表completed | ❌ 续作尚未核验完成 |
| 控制返回格式未知，未取得返回之后新发起的完整列表completed | ❓ 不可核验，保留未完成 |
| close返回previous_status=running / interrupt终止运行任务 | ❌ killed / interrupted，不计成功 |
| 静态 allowlist 命中 | ⏭ fire-and-forget |
| 仅在正文声明重派/跨阶段暂留 | 不改变真实状态；按当前恢复与尝试规则核验，不能声明免验收 |
| completed 但契约 FAIL 且未重派 | ❌ completed-but-incomplete |
| 其余悬空 / 无 gate 记录即发完成报告 | ❌ 漏收 |

## 职责边界

- "做错了"（内容级）不归本套管——gate 验齐不齐/格式对不对；内容对错归
  verify / reviewer 轮（反摸鱼质检另有闭环）
- 实际宿主原生日志不可读时保留错误与未核验状态；不把仅产物检查提升为真实任务已完成。离线夹具只用于回归，不代替实际收口。
