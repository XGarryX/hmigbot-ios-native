---
name: a2h-incremental-migration
description: "对比 iOS 当前源码与既有 HMigBot baseline 的用户可见行为变化，保留原生语义并经 spec/plan/execute/verify 增量同步。"
---


# iOS 行为增量同步

1. 固定旧源快照、当前源、旧 baseline/decision、目标版本；缺旧证据先说明比较范围。
2. 比较入口、UI 状态、Binding/生命周期、业务规则、API/权限、资源与持久化的行为变化。
   文件 diff 只用于定位；改名或移动不自动等于新功能，未改文件也可能受依赖变化影响。
3. 用四类 iOS 分析技能重读受影响调用链，记录新增/修改/删除/无行为变化与证据。
4. 保留稳定 page/F/AC ID；真正新增断言发新号，删除/替代保留理由与 decision 关联。
5. 将可审阅差异交用户既有授权范围判断；未授权产品替代才请求明确选择。
6. 调用 arkts-spec-evolver 更新原 baseline，再走 a2h-plan/execute/verify；
   复用未受影响且输入未变的证据，变化范围重新验证。

源索引更新必须在影响分析与规格更新之后，禁止只刷新 hash 消除 stale finding。
plan 保持只读调度，执行状态仍进原 brief/findings。未执行设备验证保持 not_run。
