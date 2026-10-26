# 原生规格生成协议

`spec-authoring` 是现有 a2h-spec 的生成辅助入口，不替代源分析、独立复核或门禁。源索引、页面/功能 Markdown 与当前配置必须一致；事实/义务仍只由原工具生成。

## 生成完整填报清单

页面/功能清单及初稿就绪后，调用当前安装副本的 runtime：

```text
python <runtime>/scripts/a2h_ios.py spec-authoring --project <target> --output <target>/spec/reports/spec-authoring.json
```

读取 `documents` 与 `acceptance`，逐一核对真实入口和范围。工具枚举所有主页面/功能；feature addenda不新增native ID，但其AC仍进入清单并继承主功能源锚点。索引中声明却未写出的文档会被拒绝。`source_anchors` 给出当前文件摘要与行数，`required_common_facts` 和 `conditional_dimensions` 给出必需维度。索引不决定完整业务范围，遗漏入口仍需源覆盖审计。

把 `input_template` 保存为本轮输入。每个文档声明真实 `languages/frameworks`，按其条件维度补齐 `facts`。模板只写 unknown；原作者读源后填写 typed value、真实 fact_ids 和 evidence，或有据的 not_applicable。未知、缺件、NA矛盾、状态初值不一致和关联不到当前源事实的声明均不能生成候选。

## 字段和锚点单源

- `documents` 必须与清单的 page/F ID 一一对应。8页和5功能即13份，不能复制示例的2份，也不能用重复ID凑数。
- `dispositions` 只写经审阅的范围处置。每条含 `path`、`disposition`、`reason`、`line`、`end_line`、`source_sha256`；disposition 取 dependency/test/not_applicable。owner映射写对应页面/功能的source_anchors。不能按目录名自动判定测试/依赖。
- 每条都是字面量排除证据：`line/end_line` 是该文件当前行内的闭区间，条目 `source_sha256` 是这一个文件当前字节的摘要；顶层 `source_sha256` 是整件源快照摘要，二者不同且都必填。生成器与 source-check 在规划前就按真实文件核对，缺字段、越界/逆序区间和过期摘要都不再等到 Stage0 才被拒绝。
- `truth_anchors` 每项含 `ac_id/path/line`。为每个源真值AC选择该功能 `allowed_sources` 内的实际文件与行。工具生成 `真:src:路径:行`；路径、行号及归属校验与 source-check 共用。已有 test/trace/device/decision 真值保留，不自动改为源真值。
- 源或MD变化后重新生成清单并重审；旧 inventory_sha256 不可沿用。禁止手改摘要或增添无关anchors来迎合校验。

## 渲染并交回原作者

```text
python <runtime>/scripts/a2h_ios.py spec-authoring --project <target> --input <reviewed-input.json> --output <target>/spec/reports/derived/native-candidate.json
```

输出 `files` 是规范路径到内容的映射：两个JSON伴随件和含源真值AC的功能MD。原作者独立复核后将内容完整写入对应规范路径，JSON按JSON序列化；保持稳定ID、断言和目标合同。渲染器不改任何baseline或账本，也不执行自动补锚点、默认N/A、自动判owner或继承PASS。

随后实际运行 `spec-check`、`source-check --harness` 及原独立内容审阅。`status=candidate`、`spec_complete=false`、`behavior_verified=false` 仅说明候选生成；正式门禁和行为验收分别记账。已冻结计划按原明确replan流程处理。
