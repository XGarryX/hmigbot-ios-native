# 全流程实际计量（F14）

配置真实 iOS 源和目标、确定本轮范围后，在 Init 的环境准备之前开始计量。首次创建目标和选择范围尚未计量时如实注明，不补写虚构的历史起点。具体应用数据只保存在该目标 `spec/reports/derived/execution-measurements/`，可读进度仍为 `spec/reports/ios-progress.md`。

主控从本轮实际计划和验收要求生成请求，字段如下：

```json
{
  "run_id": "<本轮唯一标识>",
  "scope": {"stages": ["init", "spec", "plan", "execute", "verify"], "pages": ["<实际页面ID>"]},
  "quality_protocol": {"required_commands": ["source-check", "plan-ir", "build", "harness-check"]},
  "cache": "cold"
}
```

范围和命令必须来自本轮实际选择；上例不能代替项目事实。cache 使用 cold / warm / unknown，是明确声明而非工具自动检查缓存。不同缓存条件或 unknown 不计算提速比例。

```sh
python3 <runtime>/scripts/a2h_ios.py pipeline-metrics start --project <target> --input <run-request.json>
```

项目配置、实际源摘要、宿主环境与所选范围会固定到本轮记录。工具版本另记，不因新旧版本不同就禁止比较；源、配置、范围、质量要求和缓存条件仍须一致。实际写入命令通过现有 ProjectProgress 自动记录，资源合并和原 writeback 链也接入；任务实际 bind/回收、修复/构建/复查、材料实际消费分别由对应适配器记录。

普通调用、任务、等待、编译、返工、合并、回写和材料读取分别统计。需要计量宿主层的 Spec 子任务或 wait 时，在真实调用前使用 `begin`，结束后使用 `end`，不能用调度建议或计划时长冒充实际执行：

```json
{"stage":"spec","operation":"<真实任务或等待名称>","category":"task","metadata":{}}
```

```sh
python3 <runtime>/scripts/a2h_ios.py pipeline-metrics begin --project <target> --input <begin-request.json>
```

保存返回的 run_id/span_id token；只有宿主调用真实结束、任务按 Join 收口后，才提交结束记录。等待调用用 category=wait；任务用 task，普通调用的嵌套不能算作额外 worker 并发。

```json
{"token":{"run_id":"<返回值>","span_id":"<返回值>"},"status":"<实际结果>","exit_code":0}
```

```sh
python3 <runtime>/scripts/a2h_ios.py pipeline-metrics end --project <target> --input <end-request.json>
```

收尾时传入实际原检查报告的项目内路径；读取、归档其真实结果和摘要，计量器不制造质量 PASS：

```json
{"status":"completed","quality_evidence":["<本轮原检查的JSON报告>"]}
```

```sh
python3 <runtime>/scripts/a2h_ios.py pipeline-metrics finish --project <target> --run <run-id> --input <finish-request.json>
python3 <runtime>/scripts/a2h_ios.py pipeline-metrics summary --project <target> --run <run-id>
python3 <runtime>/scripts/a2h_ios.py pipeline-metrics compare --project <target> --run <new-run-id> --baseline <old-run-id>
```

finish 自动生成本轮 `summary.md`，分别列实际总经过时间、分类次数、耗时之和、重叠时间和最大已计量任务并发。summary 和 compare 只读。两次运行必须完整结束、实际记录要求的检查成功、具有当前有效的原质量报告，才计算提速；缺基线/缺计量/要求不一致则输出 not_comparable。相同输入快了多少应连同 build、rework、wait、merge/writeback 时间一起查看。

存在未结束 span 时不能声明本轮 completed。中断记 interrupted，失败记 failed，保留原记录；计时本身不停止任务或改写应用进度账本。时钟域改变则保留未决记录，不补写时长。原始业务结果不受派生计量故障影响。
