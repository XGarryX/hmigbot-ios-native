# 设置和点击效果链专项

沿用现有 `behavior-check`，不新增 CHECK 编号。只有本轮明确选择效果链专项时，向 `spec/verification/ios-behavior.json` 加 `effect_review`；现有未选专项的行为用例不因此失效。

先由 iOS 功能分析依据真实源事实、默认值、读写者、业务副作用和反馈产生独立 oracle。不得从待审 ArkTS 或其当前输出反推 expected，来源不足则留待核实。

```json
{
  "effect_review":{
    "selected":true,
    "chains":[{
      "id":"<唯一效果链>","kind":"setting",
      "source_fact":"<当前persistence事实ID>","case_id":"<现有真实行为case ID>",
      "owner":"<负责该功能的任务>","ac_ids":["<该case覆盖的AC>"],
      "stages":{"default":["default"],"save":["saved"],"reload":["reloaded"],"business_effect":["notification_sent"]}
    }]
  }
}
```

设置必须分别观察 default/save/reload/business_effect；点击 `kind:click` 必须分别观察 input/processing/side_effect/feedback，并绑定当前 event 事实。每阶段指向 case stdout JSON 中一个不同的实际值路径，不能把同一个“保存成功”字段重复算成读回和实际生效。case 原有 oracle.expected 必须提供相同路径的独立预期值；target_hashes、命令、运行器与 AC 继续由原协议校验。

运行原 `behavior-check --run` 后，专项直接消费该次进程的 stdout、退出码、真实值和独立 oracle：保存/重载符合预期而业务效果不符合时，失败定位到 business_effect；点击有响应但无副作用/反馈时分别列出。仅函数名、存储关键字、`reviewed` 或 `APPLIED` 均不能替代实际观察。

结果保存在原 `spec/reports/ios-behavior-check.json` 的 `effect_review` 与派生 `spec/reports/ios-behavior-review.json`。确认失败逐项进入原 failures，包含稳定 id、source_fact、case_id、stage、owner、ac_ids，供修复分组消费；来源不足、未运行或证据失效保持 UNVERIFIED/not_run，不自动猜测修复。

只读复核现有当前输出可用：

```sh
python3 <runtime>/scripts/behavior_review.py --project <target>
```

复核重新验证原事实图、源/目标/规格摘要和原 stdout，不执行用例、不写报告；过期结果须重跑原 behavior-check。普通进程输出证明对应声明范围的观察，设备真实性与完整语义仍取决于原后端及独立审核；本适配器不宣称完成了新的原生设备采集或全程序调用图分析。
