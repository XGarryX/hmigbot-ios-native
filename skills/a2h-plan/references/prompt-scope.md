<!-- when: 生成或修改typed plan request的decisions时加载 -->
<!-- topics: prompt_scope, 决策范围, 全局约束, plan request -->

# 决策上下文范围：采用已有prompt_scope

`prompt_inputs.project_inputs` 已在plan-ir生成器内按task.fact_ids选事实、按显式scope选决策；任务内事实已去重。这里接通作者流程，不创建另一份语义账本、写权或验收标准。完整决策仍保存在冻结blueprint，scope仅改变每个prompt的内联内容。

## 作者步骤

1. 读取权威 `spec/decision-ledger.md` 与真实任务/AC/fact消费关系，保留稳定决策ID和依据。
2. 全局、跨模块、平台共性、安全、状态/数据契约等共享约束缺省**不写prompt_scope**，由现有消费者发给所有任务。没有直接fact引用不能作为删除依据。
3. 仅在作者/计划合同明确采用并审阅所有消费者后添加scope。机器可生成候选，不能自动采纳或缩小范围。保存审阅依据在原计划/决策正文，不另建控制账本。
4. scope只支持 `task_ids`、`ac_ids`、`fact_ids` 的字符串数组；各键匹配消费者取**并集**。AC选择全部承担该AC的任务，fact选择全部读取该fact的任务，不选一个任意owner。
5. scope必须选择至少一个实际消费者。空对象/全空数组、未知ID、无人读取的fact、错拼字段及非数组值均会在schema或现有运行时校验中拒绝。没有scope与空scope不同，不能用空scope表示全局。
6. 运行原 `plan-check`，成功后由 `plan-ir` 冻结；失败修改原作者输入。冻结后改scope同样须显式replan，不手改prompt/blueprint。

## 随包示例及替换规则

读取 [plan-request-template.json](../templates/plan-request-template.json)。它展示两个任务、全局决策、AC局部决策、共享fact决策；是可解析的understand示例，**不是可以直接提交的真实项目计划**。先把零graph摘要、示例fact/AC/任务ID、goal、精确写权全部替换成当前项目事实；domains请求还须完整带 `plan_item_refs` 等profile 2合同字段与真实原Stage任务，不能把understand示例冒作domains成品。

schema显式声明scope形状并保留已有决策扩展字段；已知ID/至少一个实际消费者仍由现有 `project_inputs` 检查，不能仅凭JSON schema通过宣称scope完整。scope不免除必读共享合同和最终验收。

## 采用前负例

- 全局决策没有任何fact引用，仍须出现在全部任务prompt；人为删除应被独立合同检查发现。
- 一个fact由App与Widget两个任务读取，相关决策必须发给两者；不能用一个任务ID替代全部消费者。
- 未标scope的旧决策保持全局；新机器候选未经显式采用不生效。
- 把 `task_ids` 写成 `tasks_ids`、引用未知AC、空scope均应拒绝，不能通过“选不到所以不发送”静默删除约束。

统计实际采用的scope决策与省略内联量，再用真实usage比较总发送量。缓存命中不从总input扣除；更短prompt不自动证明质量等价或20M达标。
