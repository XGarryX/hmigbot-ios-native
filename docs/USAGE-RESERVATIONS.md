# 显式在途Token预留（0.11.0）

预留只约束调用者提交的上界，不估算token、不发起模型请求、不证明宿主已完整上报。统计口径始终是总input（含缓存）+总output；预测/预留与实际消耗分开。

## 顺序与输入

在完整工作的首次必要步骤前开始同一run，直到构建、等待、修复和全部验证结束才finish。以下均在工具根执行；安装副本使用`.hmigbot-ios/plugin/scripts`。示例数值是合成演示。

```sh
python scripts/a2h_ios.py usage-start --project /absolute/target --run-id run-001
python scripts/a2h_ios.py usage-reserve --project /absolute/target --input /absolute/reservation.json
python scripts/a2h_ios.py usage-record --project /absolute/target --input /absolute/actual-usage.json
python scripts/a2h_ios.py usage-summary --project /absolute/target
python scripts/a2h_ios.py usage-finish --project /absolute/target --run-id run-001
```

`reservation.json`：

```json
{
  "call_id": "worker1-attempt1",
  "run_id": "run-001",
  "token_upper_bound": 10000,
  "stage": "convert",
  "agent": "worker1",
  "provider": "openai",
  "attempt": 1
}
```

`actual-usage.json`保留同一身份：

```json
{
  "call_id": "worker1-attempt1",
  "run_id": "run-001",
  "stage": "convert",
  "agent": "worker1",
  "provider": "openai",
  "attempt": 1,
  "normalization_mode": "openai_responses",
  "raw_usage": {
    "input_tokens": 100,
    "input_tokens_details": {"cached_tokens": 40},
    "output_tokens": 20
  }
}
```

实际消耗120，缓存是input子集；本次剩余预留释放。其他供应商使用 [原账本归一合同](RELIABILITY-0.10.md)，不要在未核对原始字段时猜cache是否已含在input中。失败与重试分别用唯一call-id记录；不能同时记录聚合与其组成调用。

## 原子额度和幂等

锁内核对`已用+全部未结算预留+本次上界≤运行额度<20M`。`reserved_tokens`、`active_reservation_count`和`available_tokens`与实际`total_tokens`分别输出。未知partial usage已知部分计入实际量、剩余预留继续占用；未知本身仍阻断新调用。

同一active ID、身份和上界重复请求只恢复原预留，返回`reservation_created=false`、`reservation_status=active`及`reservation_call_id`；**不授权再次执行同一调用**。宿主必须有调用唯一性/恢复记录。已结算、已取消或usage_unknown不能再次reserve；重试需要新call-id/attempt。

预留成功可占满剩余额度，此时reserve退出0表示该次许可成功，`can_continue=false`表示不能再新增未预留工作。不要用泛检查否认已有许可，也不能把同一次许可执行两次。时钟异常、运行已结束/超时、unknown usage或FAIL不授权新预留。超上界的真实usage仍被完整记录，`reservation_overrun_count`展示偏差；是否预算失败按实际总量另判。

第一次reserve把原账本原子升级到schema 2，旧0.10.x读者会拒绝，避免忽略在途。新运行时仍读取没有预留的schema 1；不能人工降级schema绕开预留。

## 真实未调用的取消

仅在确认provider调用尚未发起时使用：

```sh
python scripts/a2h_ios.py usage-release --project /absolute/target --input /absolute/release.json
```

```json
{
  "call_id": "worker1-attempt1",
  "run_id": "run-001",
  "reason": "cancelled before provider invocation"
}
```

取消声明与原因保留，不能删除账本条目。已record的调用不能release；取消后若出现迟到真实usage，保留用量并报告`released_reservation_was_used`失败。无法确认调用是否发起时不要声称未调用，保留未结算。`raw_usage:null`仍是UNKNOWN，不可取消后按0通过。

`finish`拒绝冻结active/usage_unknown预留，调用方需处理真正未调用取消或保留未知状态；完成后的账本不可追加。缺失usage的已保存记录不能靠改写原始证据“修成完整”，应保留该次UNKNOWN并先修宿主上报。

## 调度及平台限制

现有`next-batch --usage-ledger ... --usage-run-id ...`会核对在途，但不自动估算/预留或生成call-id。先获取批次，再为实际调用reserve；已有预留耗尽额度时泛检查拒绝新批次。`land-results`仍可收回已有工作，不因超预算丢结果。

主线程/子代理/失败尝试的完整调用清单与自动run绑定仍需宿主集成和独立对账，账本PASS不证明没有遗漏。也不证明UI、功能、应用规模或2小时整体迁移成功。

当前真实boot identity仅Windows/Linux可验证；Darwin尚未实现，Mac严格计时保持UNKNOWN并拒绝reserve。必须用真实OS启动身份扩展并验证，不可跳过检查取得PASS。
