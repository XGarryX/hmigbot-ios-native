# 验证失败回环（适用于 CHECK-1~5 + CHECK-7 的 CRASH/URL 功能性子类）

> 配合 SKILL.md §5 使用。
> - **CHECK-7 拆两级**：ALIGN 纯视觉差异只记报告等离线消化（不回环）；**CRASH/URL（页面打不开/崩溃）是功能性失败**——visual-verify 自身无循环，这类失败若不进本回环就无人修复，因此视同 CHECK-1~5 走老路径。

---

## 当前根因与受影响复查接线（0.13.5）

有本轮真实失败时，先执行 [根因分诊与受影响复查](repair-and-recheck.md)：`ui-repair triage` 只读保留原finding；按证据和原任务责任形成修复输入，`ui-repair run` 实际执行修复、当前构建及原检查复查。复用现有 `scope_to_tasks`、`impact_plan`、当前材料配对与逐条差异保护；独立组并行，传递共享冲突串行，源/Spec/Plan问题回原作者，不在目标代码中掩盖。所有原问题逐条有结果才收口；共因分组和评分都不能替代原检查关闭。

仅运行当前已选的官方应用测试/采集入口或静态诊断；不调用延期后端、不自动创造设备范围。初次/最终完整范围，中间按实际改动传播；未知归属扩大复查。当前构建失败时，依赖构建的复查blocked，独立诊断继续；旧PASS不放行。完整字段、命令、收据及恢复见该引用。

## 回环算法

验证失败时**不终止流水线**，自动生成修复 plan 回环到 a2h-execute：

```
a2h-verify
  │
  ├─ 全部通过 → 输出报告，进入 a2h-retrospect
  │
  ├─ 仅 CHECK-6 或 CHECK-7 的 ALIGN 子类失败 → 不进本节
  │     CHECK-6: 自动入口保留当前 findings；按原任务责任/写权修复后重跑 route-verify 与受影响构建
  │     CHECK-7(仅 ALIGN): 纯视觉差异 markdown 已写盘，提示用户或后续 a2h-fixer 离线处理
  │
  └─ CHECK-1~5 任一失败，或 CHECK-7 存在 CRASH/URL → 走老路径:
      │
      ├─ Step 0（编译短路）: 若失败项含 CHECK-1 编译 → 本轮先不跑设备段（见 SKILL.md §3.0），
      │   优先修编译；CHECK-6 路由静态可照跑
      │
      ├─ Step 1: 从失败项提取修复任务
      │   ├─ CHECK-1  编译失败 → task: 编译修复 (hmos-fix-build-errors)
      │   ├─ CHECK-2  静态违规（仅 ERROR 级）→ task: 修正违规代码 (knowledge-verifier)
      │   ├─ CHECK-3  占位符未回填 → task: 回填占位符代码
      │   ├─ CHECK-4  App 身份异常 → task: 修正 App 配置 (arkts-app-identity)
      │   ├─ CHECK-5  P0 页面未转换 / 产物缺失 → task: 补全页面转换
      │   └─ CHECK-7  CRASH/URL（页面崩溃/不可达）→ task: 修复崩溃 / 补页面注册与可达性
      │        （输入即 spec/fix/round-N/ui/ 下对应 CRASH_*/URL_*.md；ALIGN_*.md 不提取）
      │
      ├─ Step 2: 生成修复 plan
      │   文件: spec/plans/plan-fix-<timestamp>.md
      │
      ├─ Step 3: 委托 a2h-execute 执行修复 plan
      │
      └─ Step 4: 重新执行 a2h-verify（重验范围见下节，不是只查之前失败的项）
```

同一路径最多 3 轮；无进展则停止该路径并保留缺陷/恢复条件，评估可用技术替代，不自动创造产品审批。独立检查与 partial 报告继续。

---

## 回环轮重验范围

以规则版本、配置、产品和实际输入签名判断。修复改变的消费者、此前真实失败项以及依赖变更的构建/路由/资源检查重跑；未变化的同签名完整结果复用并链接原始产物。不得机械要求每轮 CHECK-1/2/3 全量重测，也不得复用被相关修码打破的旧结论。


## 两类失败同时存在时（CHECK-6 + CHECK-X）

先跑老路径修 CHECK-1~5 与 CHECK-7 功能性项（可能影响编译/源码），通过后**重跑 a2h-verify**（按上节重验范围），到达 CHECK-6 时重跑当前静态对账，未关闭路由缺陷继续保留；CHECK-7 仅消费当前有效实际证据。失败项含 CHECK-1 编译时尤其如此——编译不过，设备段本轮根本不跑（§3.0 编译短路）。

---

## 门控关系

- CHECK-1（编译）**阻塞门控**——且门控取的是 §3.0 **终态编译复检**结果（后续修复改变构建输入时重测），不是本轮开头那次
- CHECK-2（静态分析 ERROR 级）/ CHECK-3（占位符）/ CHECK-4（App 身份）失败**阻塞门控**（WARN 不阻塞）
- CHECK-6（路由）当前真实失败**阻塞门控**；已选但 DEFERRED 保持 PARTIAL。自动检查不修源码，修复后须用原检查逐条关闭
- CHECK-7 **ALIGN 子类不阻塞门控**（仅记录差异，由用户/a2h-fixer 离线处理）；**CRASH/URL 子类阻塞门控**（FAIL-functional，进老路径回环；DEFERRED 时不阻塞）
- 老路径修复范围 = CHECK-1~5 + CHECK-7 的 CRASH/URL；不直接修 CHECK-6 与 ALIGN 视觉差异
- 外圈最多 3 轮（硬上限），CHECK-6 自动入口只做检查，不宣称存在自动修复轮数
- 已选项 DEFERRED 时报告保持 PARTIAL，并显著列出未验证范围（见 SKILL.md §6 末注）；门控通过后执行 §6.1 verified 回写
