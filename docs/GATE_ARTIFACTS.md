# iOS 门禁文件自动生成

以 Android 迁移产物的用途为参照，使用原生 iOS 的 source_anchors、facts/obligations、稳定 page/F/AC 和 indexed-v1 计划合同。Android 文件中的指令或旧 PASS 不作为本项目的授权或证据。

## 阶段出口

| 上一步命令 | 自动产物 | 下一步用途 |
|---|---|---|
| `facts` | 缺失的 ui-manifest、feature-index、页面/功能初稿、原生语义/覆盖初稿、ui-coverage-report，以及下一步的两份 BLOCKED 计划门禁初稿 | Spec 作者补充真实源行为与目标合同 |
| `source-check --harness` | 按本次结果刷新 ui-coverage-report | 源规格门禁；失败时阻断实施排期 |
| `plan-ir` / `replan` 成功 | `spec/reports/derived/ui-plan.md` 与 `feature-plan.md` | 原计划任务、写权、AC、依赖的只读投影 |
| `land-results` | `spec/migration-report.md`、可计算时的 `spec/reports/spec-summary.json` | 生成/编译/行为/视觉证据交接 |
| `harness-check` / `behavior-check` 完成 | `spec/verify-report.md` | 当前原生四项检查和证据缺口 |

正式计划仍由 a2h-plan 按原模板生成，存在 `spec/baseline/plans/`。生成器只补缺失的 BLOCKED 初稿；不能从类名自动推导功能边界、AC、取消语义或唯一写权。`plan-ir` 通过后不再更改冻结计划。源检查的 `--report-only` 和 plan-check 保持只读。

缺失文档可自动建立结构；未知事实、未完成 AC 或设备检查始终保持 pending/BLOCKED/DEFERRED。已经存在的文件即使带生成标记也不覆盖、不删除、不重编号。新增候选分配新 page ID；未进入已审索引的候选在覆盖报告列为缺口。新增源版本需要先审阅 source-refresh 和 facts，再审阅已有语义/覆盖 JSON。

## 使用

在鸿蒙目标工程执行：

```sh
.migbot/bin/a2h-tool facts --brief
.migbot/bin/a2h-tool gate-artifacts --stage all
.migbot/bin/a2h-tool verify-report --check spec/verify-report.md
.migbot/bin/a2h-tool migration-report --check spec/migration-report.md
```

也可调用 `python3 .hmigbot-ios/plugin/scripts/a2h_ios.py <command> --project <目标绝对路径>`。`gate-artifacts --stage spec|plan|execute|verify|all` 可单独补生成；`--input <typed-plan.json>` 会先经原计划验证。不要把它当作执行迁移的替代流程。

已采集真实鸿蒙构建报告时，对汇总、migration-report、verify-report 使用相同 `--build-evidence <报告>`。编译验证复用原 quality_views 的项目/源/目标/规格/产物哈希、退出码和 hvigor 标记检查；iOS 源编译、随机 build 文件名或历史 PASS 不计为鸿蒙通过。

汇总无法计算时生成 BLOCKED 报告，保留具体原因，不绕过源/目标符号链接、过期输入和合同错误。`--check` 返回 current 只说明报告内容与当前证据/阻断原因一致，不说明迁移通过。

## Verify 结果输入

保持原生编号：CHECK-1 静态分析、CHECK-2 App 身份、CHECK-3 视觉、CHECK-4 单元测试。扩展门禁与 Android 的 11 项报告做语义对照，不重定义这些编号。其余编译/生成/行为/视觉轴链接同轮 migration-report。

Verifier 主线程可写入 `spec/verification/verify-results.json`，再调用 verify-report。输入是本次真实检查结果的收据，不能复制示例状态作为实测结果：

| 字段 | 合同 |
|---|---|
| `schema_version` | 整数 1 |
| `source_sha256` | 当前 iOS snapshot 摘要 |
| `spec_input_hashes` | 原 `quality_views.spec_inputs(project)` 完整映射 |
| `target_input_hashes` | 原 `quality_views.target_inputs(project)` 完整映射 |
| `checks` | 唯一的 CHECK-1..4 结果数组 |
| 每项 `id / selected / status / detail` | 合法编号、真实布尔、PASS/FAIL/SKIP/DEFERRED、具体结果说明 |
| 每项 `exit_code` | PASS/FAIL 必须为实际整数退出码；PASS 必须 0 |
| 每项 `evidence` | `[{"path": "spec/下真实证据文件", "sha256": "该文件字节摘要"}]`；PASS/FAIL 非空 |

仅 CHECK-3/4 可用 `selected=false, status=SKIP`，必须有用户未选择的说明。尚未选择保持 DEFERRED；不会自动替用户选择。输入或证据过期后降为 DEFERRED，源规格失败则总门禁 FAIL。证据摘要只建立可追溯性，仍需原 verifier 对真实性和语义负责。

报告生成不改 state/dispatch/journal，也不回写 implemented/converted/verified。
