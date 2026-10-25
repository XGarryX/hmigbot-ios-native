# 验证失败回环（适用于 CHECK-1~5 + CHECK-7 的 CRASH/URL 功能性子类）

> 配合 SKILL.md §5 使用。
> - **CHECK-7 拆两级**：ALIGN 纯视觉差异只记报告等离线消化（不回环）；**CRASH/URL（页面打不开/崩溃）是功能性失败**——visual-verify 自身无循环，这类失败若不进本回环就无人修复，因此视同 CHECK-1~5 走老路径。

---

## 回环算法

验证失败时**不终止流水线**，自动生成修复 plan 回环到 a2h-execute：

```
a2h-verify
  │
  ├─ 全部通过 → 输出报告，进入 a2h-retrospect
  │
  ├─ 仅 CHECK-6/9 或 CHECK-7 的 ALIGN 子类失败 → 不进本节
  │     CHECK-6: router-verify 已自跑修复闭环，reopened/必崩项写进 ROUTE_VERIFY_SUMMARY.md，提示人工或重跑
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

老路径回环最多 3 轮。3 轮后仍有失败项，输出报告并提示用户手动介入。

---

## 回环轮重验范围（防回归盲区）

修复本身会改源码，**之前 PASS 的结论可能被修复打破**——"只查之前失败的项"会让回归静默漏过门控。每轮回环重跑 a2h-verify 时按下表收程（这是 execution-discipline 铁律唯一认可的合法缩程）：

| 项 | 回环轮是否重跑 | 理由 |
|---|---|---|
| 之前 FAIL 的项 | 必跑 | 回环目标本身 |
| CHECK-1 编译 | **必跑** | 任何源码修复都可能破坏编译（与 §3.0 终态复检同一精神）|
| CHECK-2 / CHECK-3 | **必跑（全量重扫）** | 秒级 grep 成本可忽略；修复最容易引入新违规 / 新 TODO 占位 |
| CHECK-4 | 修复触碰 AppScope/ 资源文件时重跑，否则沿用 | 常规代码修复不碰身份配置 |
| CHECK-5 | 之前 FAIL 才重跑 | 输入是 spec 状态与文件存在性，修复只增不减 |
| CHECK-6 | 已 PASS 但修复触碰了**路由面**时必须重跑，否则沿用 | 编译修复改坏刚修好的路由是已知回归路径 |
| CHECK-7 | 老路径不直接"修"它们，但 **FAIL-functional 的 CHECK-7 属于"之前 FAIL 的项"——回环修复后必须按 §3 正常序重跑 visual 确认 CRASH/URL 已消**；编译短路解除后 DEFERRED 的设备段补跑 | 各 verifier 自管内部循环 |

**"触碰路由面"的判定**：本轮修复改动的文件 ∩（`spec/verify/route/fix_plan.json` 各项 `files_changed` ∪ 路由注册文件 `main_pages.json`/`route_map.json`/pageMap 所在文件 ∪ 任何含 `pushUrl`/`pushPathByName`/`openDialog` 调用的被改文件）非空。

**CHECK-7 已 PASS 后才发生的回环修复**：不强制重测（设备实测成本不对称），但报告门控判定区必须标注"第 N 轮回环修复发生在视觉实测之后，视觉未覆盖该修复"。

> ⚠️ **铁律提醒**："最多 3 轮"是硬上限不是建议。回环必须由本算法的"3 轮跑满"或"全部 PASS"两个出口停下，主线程不得因"省时 / 累计 token / 预估剩余难度高"等理由提前 break。详见 `execution-discipline.md`。

---

## 两类失败同时存在时（CHECK-6 + CHECK-X）

先跑老路径修 CHECK-1~5 与 CHECK-7 功能性项（可能影响编译/源码），通过后**重跑 a2h-verify**（按上节重验范围），到达 CHECK-6/7 时各 verifier 内部循环会自然处理（避免循环里撞编译错误）。失败项含 CHECK-1 编译时尤其如此——编译不过，设备段本轮根本不跑（§3.0 编译短路）。

---

## 门控关系

- CHECK-1（编译）**阻塞门控**——且门控取的是 §3.0 **终态编译复检**结果（CHECK-6 修完源码后重测），不是本轮开头那次
- CHECK-2（静态分析 ERROR 级）/ CHECK-3（占位符）/ CHECK-4（App 身份）失败**阻塞门控**（WARN 不阻塞）
- CHECK-6（路由）失败**阻塞门控**（DEFERRED 时不阻塞）——router-verify 自带修复闭环，失败=有 reopened 或运行时必崩项未解
- CHECK-7 **ALIGN 子类不阻塞门控**（仅记录差异，由用户/a2h-fixer 离线处理）；**CRASH/URL 子类阻塞门控**（FAIL-functional，进老路径回环；DEFERRED 时不阻塞）
- 老路径修复范围 = CHECK-1~5 + CHECK-7 的 CRASH/URL；不直接修 CHECK-6 与 ALIGN 视觉差异
- 外圈最多 3 轮（硬上限），CHECK-6 内部 fix-loop 轮数由各 verifier 自管，互不嵌套
- 门控在若干 DEFERRED 下达成时，报告必须显著标注（见 SKILL.md §6 末注）；门控通过后执行 §6.1 verified 回写
