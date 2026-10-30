# Stage 1：按真实容量持续补位

运行 `execution-contract --apply`、Stage 0 和原 UI 输入检查之后，使用当前 indexed 执行控制器；不启动 legacy domains 调度。控制器从冻结的 UI Batch 表、plan_items、parents 和 ownership 建队列，不改变批组成。F01 收口与 F02 资源增量规程继续生效。

```sh
python3 <runtime>/scripts/a2h_ios.py indexed-dispatch init --project <target>
# 已有预算时给 init 同时传 --usage-ledger <原账本> --usage-run-id <原run-id>
python3 <runtime>/scripts/a2h_ios.py indexed-dispatch next --project <target> --phase ui --capacity <宿主实际可用并发总额>
```

1. `next` 前实际调用宿主完整 `list_agents`。capacity 来自当前宿主实际能力，计入 converter、worker、closer、builder、预热等在飞任务，不照抄固定数字。未完成当前批 writeback 前不能跳到下一批。
2. 对返回的每个任务，用当前宿主真实 `spawn_agent`；使用返回的唯一 `task_name`、expected-set、plan refs 和读写范围。`next` 是建议，不是已派发；真实工具成功返回后立即 `indexed-dispatch bind --project <target> --job <job-id>`。无真实 spawn 记录不能 bind。
3. 收到可信完成或等待返回后，先实际调用完整 `list_agents`，再 `indexed-dispatch observe --project <target>`。它读取当前 `CODEX_THREAD_ID` 原始日志，复用 F01 身份/轮次与产物规则。产物缺失不算成功；没有新完成则有界等待，不重复空轮询。
4. 立刻再次 `next`，补本批下一个依赖满足且不争写的任务；不等最长任务才补位。平台 thread limit 后须等待真实容量改变，禁止忙重试。空交付降低有效并发；停止/中断任务仍保留写权，不能因超时自动重派。
5. 本批全部 returned 后按原 Batch closer → F02 merge → `apply_writeback` 落盘；再 `indexed-dispatch checkpoint --project <target> --name <本批checkpoint> --receipt spec/execution/receipts/<原回写收据>.json`。它核对真实原回写与当前输出后才能开下一批。

预算耗尽只停止新派发，bind/observe、必要回写、资源合并和收尾继续。旧任务及其子进程停止写入无法核验时保持 stopped，保留原始错误，按既有受审尝试恢复；不能修改控制器 state 来借用旧完成。

控制器初始化生成 `spec/a2h/_work/expected_indexed_*.json`，join_point 为 `indexed-dispatch`。同一派发者创建 closer/builder 的 expected-set 时沿用该 join_point，声明实际输出；外置 build 证据应有工程内含原路径与摘要的交付引用，不能只交 `.done`。最终仍跑 F01 Join gate。控制器状态位于 `spec/execution/indexed-dispatch/`，不替代原账本。
