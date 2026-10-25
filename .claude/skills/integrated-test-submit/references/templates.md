# integrated-test-submit 输出模板

每个模板中 `<...>` 为待填充占位。**变量块渲染全量显式值**：所有字段逐项列出（含默认值），不因"等于默认"而省略；来自默认值的行加 `# 默认` 行内注释。变量块首行固定 `# multica`。

## Test App 注册表

> 正本：Spec §2.5"已知 App 注册表"；此处为生成用快照。

| App | 代码量级 | 简称（app_name） | url | 派生 iOS 工程路径（mac，参考——由路径规则从 url 派生，不渲染进块） |
| --- | --- | --- | --- | --- |
| DiceRoller | <1k 行 | `dice` | `https://github.com/fuxi-ailabs/iOS-Beginner-Projects/tree/main/DiceRoller` | `~/migbot_shanghai/StudioProjects/iOS-Beginner-Projects/DiceRoller` |
| AIPPT | ~2 万行 | `aippt` | `https://github.com/fuxi-ailabs/AIPPT` | `~/migbot_shanghai/StudioProjects/AIPPT` |
| AntennaPod | ~10 万行 | `antennapod` | `https://github.com/AntennaPod/AntennaPod` | `~/migbot_shanghai/StudioProjects/AntennaPod` |
| Meshtastic | ~20 万行 | `mesh` | `https://github.com/meshtastic/Meshtastic-iOS` | `~/migbot_shanghai/StudioProjects/Meshtastic-iOS` |
| Jetsnack（Other 自填） | ~6k 行 | `jetsnack` | `https://github.com/ios/compose-samples/tree/main/Jetsnack` | `~/migbot_shanghai/StudioProjects/compose-samples/Jetsnack` |

注册表 url 是渲染缺省值，生成前向用户展示确认；末列路径为路径规则的派生结果（参考信息，不进块）。表外 App 由用户提供 url。各平台路径由对应执行机的 Instruction 路径规则派生。

**评测包注册**（正本：migbot-utils `AutoEval/gt_eval_registry.json`）：当前 **AntennaPod**（两包 llm_judged）与 **AIPPT**（scripted）有评测包；其余 App 选 `gt_eval ≠ off` 将被执行侧判 not_applicable（MC-18 warning）。

> 本 skill 仅支持 merge 验证 PR 一种模式；缺陷修复 Issue / 手动验证 / 评论命令的旧模板见 `docs/Multica_Submission_Spec_Archive.md`。
> 生成结果必须零 error、零 warning 通过 Spec §3 机器校验契约（MC-01 ~ MC-19）。

---

## 模板：PR 描述（merge 验证）

标题建议：正常描述改动即可（Multica Issue 命名由 Adapter/Lead 负责，PR 标题无格式要求）。

变量按语义组组织（执行叙事顺序）：`validation`（验证对象与平台）→ `test_app`（输入 App）→ `local_workspace`（工作目录）→ `deveco_project`（新建工程，**派生值渲染组**）→ `migration`（迁移过程）→ `runtime`（运行时引擎）→ `evaluation`（迁移产物自动评测，可选组恒渲染）。

**导语行（推荐，默认渲染）**：yaml 块上方渲染 2-3 行自然语言意图声明，用 Instruction v8.4 语义分流认得的词汇——Profile 具体标识（仓库对名）、"真实迁移（非 Mock / e2e mock test）"、Runtime。v8.4 下块内标识已足以正确判定 Profile 与 Mock 禁令，导语不是承重结构；保留它是为了块被渲染破坏时的兜底与人类可读摘要。用户要求精简时可省略；渲染时导语与 yaml 块必须一致。

```markdown
## Summary

<一两句话说明本 PR 的改动>

## Validation

使用 <hmigbot-CodeX + migbot-codex-runtime-src｜hmigbot + migbot-runtime-src>（Validation-Profile: <migbot_codex | migbot>）。
在 <平台> 本地以 <Codex | Claude Code> 执行**真实迁移**（<规范App名>），不使用任何 Mock / e2e mock test。

```yaml
# multica
validation:
  profile: <migbot | migbot_codex>      # 触发仓可确定时注明"由仓名确定"
  platform: <mac | windows | dual>
  test_date: <生成日 MMDD，落死具体值>
  release_tag: <可选；不渲染即最新稳定 Release，migbot_version 权威=Release Tag>

test_app:
  url: <https://github.com/... 或 .../tree/<ref>/<subdir>>
  app_name: <简称>
  # 路径类字段（local_path / local_workspace / decisions_path）不渲染：
  # 由 Instruction 路径规则在执行侧派生；用户显式覆盖时才写入

deveco_project:                         # 渲染组（派生值）
  project_name: <具体值：<app_name>_v<test_date>_<简称>；禁止 {MMDD} 等占位符>
  sdk: <SDK/API 版本；缺省 21>
  created_by: devecocli create          # 于路径规则派生的 DevEco 根（…/baseline）下新建，其余工程属性用本机 CLI 默认值

migration:
  stages: [<stage 列表>]
  unanswered_policy: <blocked | wait_human>

runtime:
  launch_mode: <codex_cli（默认）| codex_app>
  model: <模型>
  effort: <力度>

evaluation:                             # 迁移产物完备度评测（advisory，与 Review 并行，不影响验证结论）
  gt_eval: "<off | smoke | full>"       # ★ 值必须加引号：YAML 1.1 会把裸 off 解析成布尔 False
                                        #   缺省 "off"；≠off 需 App 有评测包注册（AntennaPod / AIPPT）
```
```

**示例**（hmigbot-CodeX 的 PR，DiceRoller、无人值守，其余默认；生成日 7 月 28 日）：

```markdown
## Summary

修复 a2h-execute 切片验证的接线闭环误报。

## Validation

使用 hmigbot-CodeX + migbot-codex-runtime-src（Validation-Profile: migbot_codex）。
在 mac 本地以 Codex CLI（codex_cli）无人值守执行**真实迁移**（DiceRoller），不使用任何 Mock / e2e mock test。

```yaml
# multica
validation:
  profile: migbot_codex                 # 由仓名 hmigbot-CodeX 确定
  platform: mac                         # 默认
  test_date: 728                     # 生成日固定值，仅用于 DevEco 工程命名
  # release_tag 未指定：migbot_version 取工具仓最新 published 稳定 Release

test_app:
  url: https://github.com/fuxi-ailabs/iOS-Beginner-Projects/tree/main/DiceRoller   # 默认
  app_name: dice                        # 默认（DiceRoller 内置简称，仅用于 DevEco 命名；归档用规范名 DiceRoller）

deveco_project:                         # 渲染组（派生值）
  project_name: dice_v728_codex         # <app_name>_v<test_date>_<简称>；重名自动加 run 短标识
  sdk: 21                               # 默认
  created_by: devecocli create          # 于路径规则派生的 DevEco 根（…/baseline）下新建，其余工程属性用本机 CLI 默认值

migration:
  stages: [a2h-init, a2h-build, a2h-spec, a2h-plan, a2h-execute, a2h-verify, a2h-retrospect]   # 默认全流水线
  unanswered_policy: blocked            # 默认：未答问题直接失败并记录，不阻塞自动化

runtime:
  launch_mode: codex_cli                # 默认：CLI 无人值守直启（可改 codex_app 桌面优先；同 Runtime 内）
  model: gpt-5.6-sol                    # 默认
  effort: high                          # 默认

evaluation:                             # 迁移产物完备度评测（advisory，与 Review 并行）
  gt_eval: "off"                        # 默认（DiceRoller 无评测包，不适用评测）；引号必需，见模板注释
```
```

---

## 默认值速览快照

> 以 `docs/Multica_Submission_Spec.md` §2.8 为准，此表为不可读时的兜底快照。

| 字段路径 | 缺省值 |
| --- | --- |
| validation.profile | migbot_codex（生成器显式渲染；工具/Runtime 仓由仓名强制确定；Instruction 裸默认 migbot） |
| validation.platform | mac |
| validation.test_date | 生成日 MMDD（落死具体值，仅 DevEco 命名用） |
| validation.release_tag | 不渲染即最新稳定 Release（migbot_version 权威 = GitHub Release Tag） |
| test_app.url | DiceRoller（fuxi-ailabs/iOS-Beginner-Projects main 分支 DiceRoller 子目录） |
| test_app.local_path | 不渲染；由路径规则从 url 派生（显式给出时块优先） |
| test_app.app_name | 注册表内置简称（dice / jetsnack / aippt / antennapod / mesh）；表外 App 回退 URL 末段小写 |
| deveco_project.sdk | 21（可显式覆盖） |
| local_workspace | 不渲染；路径规则缺省 ~/migbot_shanghai/StudioProjects 与 ~/migbot_shanghai/DevEcoStudioProjects/baseline（显式给出时块优先） |
| migration.stages | [a2h-init, a2h-build, a2h-spec, a2h-plan, a2h-execute, a2h-verify, a2h-retrospect]（含 a2h-verify 时提醒开启双端模拟器） |
| migration.decisions_path | 不渲染；路径规则派生 <decisions_root>/<app_name>.md（显式给出时块优先） |
| migration.unanswered_policy | blocked（不阻塞自动化；有人值守可改 wait_human） |
| runtime.launch_mode | codex_cli（CLI 无人值守直启；可改 codex_app 桌面优先） |
| runtime.model / runtime.effort | 本机配置（建议 gpt-5.6-sol / high） |
| evaluation.gt_eval | "off"（smoke/full 需 App 有评测包注册：AntennaPod / AIPPT；≠off 时解析预告固定提醒鸿蒙模拟器与签名 profile；full 档 AntennaPod 约 20h 模拟器独占） |

Profile 配对：hmigbot ↔ migbot-runtime-src（简称 cc）、hmigbot-CodeX ↔ migbot-codex-runtime-src（简称 codex）；server 两套皆含。DevEco 工程名公式：`<app_name>_v<test_date>_<简称>`。
