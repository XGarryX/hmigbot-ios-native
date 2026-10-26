# 设备验证

依据开始时的用户选择，仅对已选项按 CHECK-3 → CHECK-4 的相对顺序串行执行。两项均选时执行 visual → 静默 5 秒 → UT；只选一项时直接执行该项。两项均未选则不进入本文件的设备流程。

每项只读取自身所需输入和 verifier 当前 SKILL.md。未选项不要求设备、源码或报告，其状态为 SKIP（用户未选择）。各已选 verifier 内部必要的准备、测试设计、构建和修复仍按自身契约执行。

## 调用准备

传入鸿蒙工程绝对路径、验证范围和已知 Android 源码路径；同时传递当前任务对产品修复的授权范围。各 skill 根目录和内部参数由其自身入口解析，不能套用另一 verifier 的 agent 参数。

- CHECK-3 需要 Android 与鸿蒙两端可用设备（adb、hdc）。
- CHECK-4 需要 hdc 可用；其他输入按各 verifier 要求补齐。
- 缺设备、必要输入或对应 skill，未启动的该项记 DEFERRED。若已启动且产出构建/安装/执行 ERROR，保留该失败，不改写成未执行。
- 只验证时明确传递不修产品代码的约束；测试设施准备仍按 verifier 契约执行。修复模式沿用当前任务授权，不扩大到未授权的业务修复。

## CHECK-3：视觉对齐

调用 `arkts-visual-verify`，由其完成双端真实页面截图、比对和其契约内的 visual-fixer 调度。主线程读取：

- `spec/visual-verify/report.md`；
- `spec/fix/_state.yaml` 指向的当前 `round-N/` 摘要；
- 当前轮 `ui/`、`feat/` 中未解决的问题，包括 carry-forward 项。

按本次实际完成范围和未解决问题判定：

| 实际结果 | CHECK-3 状态 |
|---|---|
| 范围内验证完成，无未解决差异 | PASS |
| 仅有 ALIGN / ALIGNMENT_DIFF 纯视觉差异 | FAIL-visual，附建议项 |
| 存在 CRASH、URL_MISMATCH 或 IMPL_MISSING 等功能性失败 | FAIL-functional |
| 设备执行失败 | FAIL，注明执行原因 |
| 比对未完成或修复后尚未复测 | PARTIAL，保留已确认失败 |

以实际完成的验证轮次为准，不按历史问题文件总数计数。fixer 编辑代码不代表问题关闭；`fixed` 必须来自 verifier 后续实测。外层尚需处理的功能性失败见 [失败处理](failure-loop.md)。

## CHECK-4：单元测试

调用 `arkts-ut-verifier`。默认 `MODE=verify_fix`；任务限定只验证时传 `MODE=verify_only`。Android 源码使用该 skill 的 `ANDROID_SOURCE_ROOT` 入口；缺少源码证据时按其契约继续有依据的验证，明确受影响的未验证点。

读取 `spec/verify/ut/ut-report.md`、`_state.yaml` 和当前轮 `_ut_summary.md`；进入修复循环且已有退出摘要时一并读取 `round-N/final-summary.md`。不要要求 `verify_only` 生成修复循环专属产物。

- 全范围实际 GREEN，且无未验证设计点、待补测或复核项 → PASS。
- 有实际 RED、ERROR 或最终 FAIL → FAIL，分别记录产品、测试和环境原因。
- CONVERGED、缺证据、外部前置阻塞或尚未复测的修复 → PARTIAL；保留原始退出状态，已确认失败仍按 FAIL 报告。

通过率、设计验证率和 AC 完成率按报告原口径引用，不能把已执行用例通过率当作全设计范围已验证。
