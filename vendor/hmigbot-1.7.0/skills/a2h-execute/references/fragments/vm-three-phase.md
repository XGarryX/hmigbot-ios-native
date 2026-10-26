# vm-three-phase — ViewModel C7 三段式（complex 域强制）

simple 域只做第三段；complex 域三段缺一即 FAIL。

## 第一段：源码理解（写任何 ArkTS 代码前）
Read 全部 android_source_anchors 文件，响应开头按 5 role 输出摘要（缺一不可）：
```
### Source Understanding Summary
- role=presenter/viewmodel: ①状态机（列全状态枚举）②事件流 ③异常分支
- role=service/repository:  ①接口列表 ②fromJson 兜底 ③缓存策略
- role=interceptor:         ①拦截链顺序 ②header/参数注入 ③加密路径
- role=base_class:          ①基类 lifecycle hook ②opt-in 机制 ③共享状态
- role=util:                ①静态方法清单 ②命中场景 ③副作用
```
- 每个 role 摘要必须含具体 Kotlin 类名或方法名（脚本 grep 反查；缺 → WORKER FAIL）。
- 无 anchor 的 role → 写"该 role 无 anchor"，其余必须填齐。
- 结构化输出必填 `source_summary_roles` 字段。

## 二型锚点规则（AC 锚点）
- `源:<Kotlin 符号> → 标:`（parity）：行为契约 = anchors 源码。
- `决:<PD/D/G-ID> → 标:`（divergence）：行为契约 = 查 spec/blueprint/decision-ledger.md 该决策 ID 正文（替代行为描述 + §数据流"替代路径"行），不要找不存在的 Kotlin 符号；实现落点仍是"标"。
- `[真机]` 标记不豁免实现，仅表示行为断言由 verify 设备实测。

## 第二段：差异清单
对比源码摘要与域 spec，列出 spec 没写但源码有的隐式逻辑（含触发条件 + 代码引用）：
```
### Spec Gap List
- <差异 1>: ...
```
无差异 → 输出"无差异"。

## 第三段：ViewModel 实现（必选）
1. 创建 ViewModel class——（complex）状态机分支对齐第一段"状态机"总结；
2. 定义 @Local / @Param / @Event 状态与回调；
3. 实现 UI 事件处理——（complex）覆盖第一段全部异常分支；
4. UI 组件事件绑定到 ViewModel 方法。

## 落盘（complex 强制）
写 `spec/domains/<key>.source-notes.md` = 第一段 5-role 摘要 + 第二段差异清单（round-1 审计 prompt 注入其路径复用）。缺失 → FAIL。

<!-- source: a2h-execute/references/agent-prompts/5-step3b-vm.md:L26-86 -->
