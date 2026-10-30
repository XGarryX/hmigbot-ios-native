# 运行结果与验证统计

## 协议与逐组解析

按 [HarmonyOS 单元测试指南](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/unittest-guidelines) 和 [OpenHarmony OhReport 源码](https://github.com/openharmony/testfwk_arkxtest/blob/46945da5b1d0376772a6fc73f833e821ca2497f3/jsunit/src/module/report/OhReport.js) 区分状态：

| `OHOS_REPORT_STATUS_CODE` | 含义 | 计数 |
|---|---|---|
| `1` | 用例开始 | 不计结束结果 |
| `0` | Pass | 原始 GREEN |
| `-1` | Error | ERROR |
| `-2` | Failure | RED |
| `-3` | Ignore / skip | 未验证 |

`OHOS_REPORT_CODE` 和 shell 退出码不能代替逐用例判定。汇总为 `Tests run: N, Failure: F, Error: E, Pass: P, Ignore: I`，其中 `N = F + E + P + I`，含 Ignore。不得用 `N-F-E` 推算 Pass。

每个 round、运行组、尝试独占一个原始 `aa test` stdout 文件，放在 `spec/verify/ut/round-N/logs/`；构建指纹、映射和注册清单与日志对应。保留失败尝试以供诊断，最终统计只选择当前输入对应的最新完整尝试。不同运行组均须保留；不得拼接重试日志或混入 hilog。正式验证不用 dryRun/stress 的输出代替执行结果；如果实际 Hypium 版本或并行 worker 的日志格式不在脚本支持范围，先按该版本的官方 reporter 核实并适配，不能猜测状态。

```bash
python3 "$SKILL_DIR/scripts/hypium_results.py" parse \
  --log "$RUN_LOG" --expected-ids "$GROUP_REGISTERED_IDS" > "$RESULT_FILE"
```

`GROUP_REGISTERED_IDS` 是从该组实际声明或 dryRun **独立提取**并已与 generation 对账的 JSON 字符串数组。包含保留的范围外注册项时，也须列入该组清单，报告按设计范围另做筛选，不能删原注册以凑数。未生成项不放入运行清单。

脚本按 `test` 与 `current/class` 关联开始和结束，只接受完整终态；兼容 reporter 分次 print 未自动补换行时的 `numtests/stream/test` 拼接，检查缺失、额外、重复 ID、未结束用例、唯一完整汇总、计数一致性及 `taskconsuming` 完成标记。输出 `status/raw/observed/cases/diagnostics`，输入错误退出 2，对账失败退出 1。`invalid` 组保留真实观察结果和诊断，但不得授予充分验证；先修测试基础设施或重新取得完整日志，仍缺失的 ID 列未验证。缺少 Pass/Ignore 的旧格式须先核实该版本协议，不能推算通过数。Ignore 有原始结果但没有验证结论。

## 三种比例

| 指标 | 分子 / 分母 | 含义 |
|---|---|---|
| `RAW_PASS_RATE` | 原始 Pass / (Pass + Failure + Error) | 当前范围在所有适用组的终态执行次数；含假绿的原始 Pass，Ignore 单列 |
| `DESIGN_VERIFICATION_RATE` | 所有适用组均真实 GREEN 且独立质量门合格的用例 ID / 全部逻辑设计用例 ID | 用例按稳定 ID 去重；分母包含 no_entry、needs_review、Ignore、skipped-compile、未执行、假绿 |
| `AC_COMPLETION_RATE` | 全部逻辑用例义务均已验证且必要生产接线完整的 AC / 全部含逻辑义务的源 AC | 以稳定源 AC ID 去重；一个 AC 有多条义务时须全部完成；未展开用例的逻辑 AC 仍在分母 |

纯 UI AC 不进入逻辑分母；混合 AC 的逻辑部分进入，UI 部分单列未验证范围。同一用例在多个适用组运行时，原始运行数按执行次数统计，设计与 AC 比例各只计一次；某组失败不能被其它组 Pass 覆盖。必要生产接线缺失时可保留方法用例的验证结果，AC 不计完整。

三种比例各自报告，**不相乘、不称为代码覆盖率或业务实现率估算**。分母为 0 时显示 `N/A`。代码行/分支覆盖率仅在实际插桩并取得对应构建的覆盖报告时另报，未采集写“未采集”。8 通过、2 失败时原始通过率与设计验证比例均为 80%，不再相乘为 64%；10 个运行 Pass 中 5 个假绿时原始通过率仍为 100%，设计验证比例为 50%。

## 确定性计算输入

executor 独立复核后保存 `metrics-input.json`。`logic_ac_ids` 来自 `AC_INPUTS` 与逻辑/UI 分类，`cases` 来自全部已冻结逻辑设计并与 generation 对账，不可仅从已运行用例反推。每条 `source_ac_ids` 必须与设计和 generation 一致。`required_groups` 是本用例全部适用运行组，不得因为该组失败或缺日志而删去；尚无可执行方案的 deferred 用例用空数组，仍在设计分母。质量与接线字段只据独立证据填写，缺证据用 false，不读原始 Pass 自动赋 true。

```json
{
  "logic_ac_ids": ["F001-AC01", "F001-AC02"],
  "cases": [
    {"case_id": "F001_AC01_match", "source_ac_ids": ["F001-AC01"], "required_groups": ["real"], "quality_passed": true, "wiring_complete": true},
    {"case_id": "F001_AC02_missing", "source_ac_ids": ["F001-AC02"], "required_groups": [], "quality_passed": false, "wiring_complete": false}
  ],
  "groups": []
}
```

实际 `groups` 逐项为 `{"group_id":"real","result": <该组 RESULT_FILE 的完整 JSON>}`，不得手工改写 parser 结果。上例空 `groups` 表示尚无运行证据，不能报告已验证。

```bash
python3 "$SKILL_DIR/scripts/hypium_results.py" metrics \
  --input "$METRICS_INPUT" > "$METRICS_FILE"
```

输出三个比例的分子、分母、百分比（`null` 显示 N/A）、组原始数字、范围内终态计数、验证/未验证 ID，以及 `invalid_groups/missing_groups/incomplete_groups`。`raw_pass_rate_complete=false` 时原始通过率须标“不完整”；无效或缺失组不产生已验证用例，命令退出 1。脚本不自动判定断言质量、接线或设计是否覆盖全部 AC，这些仍由 executor 对照源证据独立核验。
