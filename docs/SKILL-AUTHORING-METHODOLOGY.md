# iOS 迁移技能写作方法论（提取自原版 HMigBot 1.7.0）

> 本文件是从原版 `hmigbot-CodeX-1.7.0` 的 6 个 a2h-* 技能全文提取的**写法模板与设计原则**，
> 是所有 iOS 技能重写的唯一基准。重写任何 SKILL.md 前必须对照本文件的每一条。
> 造句细节可改，但以下骨架、纪律条款与"机器可执行优先"原则必须保留。

## 0. 三条总原则

1. **机器可执行优先**：每个动作写成精确命令（脚本 + 参数 + 产物路径 + exit code 语义），
   主会话（宿主模型）的开放决策趋近于零——决策全部下沉到脚本裁决。
2. **纪律条款要有出处**：每条"禁止/不得/红线"都标注实证编号（如 E266/E142/V20）或事故描述
   （如 issue #41）。没有实证的新约束先写成普通约束，不编编号。
3. **主文件精炼、细则下沉**：SKILL.md 正文只留步骤表与纪律，细节进 `references/runbook-*.md`，
   用"读取时机表"组织何时读哪个文件。

## 1. 标准骨架（自顶向下）

1. **frontmatter**：`name` + `description`（含四要素）+ `metadata`
2. **头注块**（blockquote）：派发约定 / Join 协议 / 派发纪律 / 路径约定
3. **§0 定位与纪律**：前置、输入、输出、唯一用户交互点、无人值守模式、第一条可见输出
4. **分步命令表**（§1..§N）：每步=命令+产物+exit code+失败处置
5. **硬约束**（穿插在各节，黑体标记）
6. **§读取时机表**：触发时机 → 必读 references
7. **§references 索引**：文件清单（触发见时机表）
8. **§交接**：门前闸 + 移交产物清单 + 下一步提示
9. **收尾：上报本阶段用量**（mark-stage，忽略退出码，绝不阻断）

## 2. frontmatter 规范

```yaml
name: <skill-name>
description: "iOS→HarmonyOS 迁移第 N 步：<做什么>。<输入输出一句>。<触发一句话>；不要用于：<负向路由>。"
metadata:
  type: pipeline
  domain: migration
  tags: [ios, <stage>]
  layer: pipeline   # 仅 pipeline 层 skill
```

description 四要素缺一不可：
- 阶段定位（第几步、做什么）
- 触发语（"当用户说 …… 时使用"，含兼容旧触发语）
- **不要用于**（负向路由，指向该做的事的正确 skill）
- iOS 领域关键词（Swift/ObjC/Xcode/SwiftUI/UIKit）

## 3. 头注块（blockquote）

### 3.1 派发约定
写明本 skill 是否派发 subagent；派发时写清楚：宿主、dispatch 工具名、agent 名单、
`fork_turns` 规则（understand 类=`none` 任务书自足；修复类=`all`）。

### 3.2 Join 协议（收口五条款，凡派发必带）
> ① 循环 wait：完成的唯一合法信号是 agent_status=completed，绝不是产物文件存在；
> ② 死句柄与验收：3 次超时后 list 核对，completed≠验收通过，join 点跑 gate 验产物；
> ③ 收口锚点：最终报告前必须收口全部句柄；④ 放行≠遗弃；
> ⑤ fire-and-forget 仅正文显式声明的派发免收口。

### 3.3 派发纪律
`task_name` 唯一（带 id/round 后缀）；派发前写预期产物清单给 join gate 对账；
**谁派谁收**（sub-agent 不能嵌套外派后退出）；契约产物必须出自承担任务的子代理。

### 3.4 路径约定
`$SKILLS_ROOT`、`$IOS_SRC`（iOS 源码根）、`<runtime>`（本包 runtime 脚本根）、
产物一律落 `<project>/spec/`（禁落会话临时目录）、本 skill 自有脚本清单。

## 4. §0 定位与纪律（必写）

- 前置：上游阶段产物存在性检查（缺 → 提示先跑上游，不代跑）；
- 输入 / 输出（产物清单，精确到文件名）；
- 唯一用户交互点（如 grill / 审批门 / CHECK 选择），其余禁交互追问；
- 无人值守模式说明（默认开启时写 `gates.unattended` 行为）；
- 第一条可见输出必须是一行阶段计划。

## 5. 命令表写作规范

每行 = 一条可复制命令：`python <runtime>/scripts/a2h_ios.py <cmd> --flag --out <path> --json`
- 注明**产物文件**与**exit code 语义**（0=PASS，1=FAIL，2=用法错）；
- FAIL 处置统一为**无人值守处置阶梯**（E266 形态，见 §6）；
- 命令不可手改、产物不可手写；脚本单写的文件（state/dispatch/journal）主会话禁改。

## 6. 无人值守处置阶梯（E266，每个门禁 FAIL 都套用）

> FAIL → 按脚本 `retry_hint` 派修复并重跑同一命令；**最多 2 轮**；2 轮仍不过或确定
> 模型修不了 → **记欠账放行**（账要记全：修过几轮、每轮失败原因、判"修不了"的依据）；
> 要拍板的模型自决并留痕；**任何分支不得停机呈报人工**（`gates.stage_debt=true` 时例外：
> 仅设备/账号类门允许欠账；静态门即便开了 stage_debt 也照常修到 PASS）。

## 7. 单写者分区（凡有多文件账本的 skill 必画表）

| 文件 | 唯一写者 | 内容 |
|---|---|---|
| ... | 脚本A（subprocess） | ... |

主会话与 worker 手改 → 契约违规（PROCESS_VIOLATION）。

## 8. 读取时机表 + references 索引（必写）

| 触发时机 | 必读文件 |
|---|---|
| 具体退出码/错误/场景 | references/xxx.md |

正文引用的每个 references/scripts/templates 文件**必须真实存在**；不存在就不能写。

## 9. 交接（必写）

- 前置门闸（exit 0 才交接）；移交产物清单（文件名级）；
- 提示用户/主会话进入下一 skill（同会话可直接续跑）。

## 10. 收尾：上报本阶段用量（必写，固定句式）

```bash
python <runtime>/scripts/a2h_ios.py usage-finish --project <target>   # 若存在；否则 mark-stage 等价物
```

最后一步执行、**忽略退出码、绝不阻断流水线**；token 用量由宿主生命周期采集，本步不采集。

## 11. iOS 适配映射表（Android 概念 → iOS 等价物）

| 原版（Android） | iOS 版 |
|---|---|
| `$ANDROID_SRC` | `$IOS_SRC` |
| `.migbot/bin/a2h <sub>` | `python <runtime>/scripts/a2h_ios.py <sub>` |
| AndroidManifest.xml / build.gradle | `.xcodeproj` / `Package.swift` / `Podfile` |
| Kotlin/Java/Compose XML 源 | Swift/ObjC + SwiftUI/UIKit + Storyboard/XIB |
| android-fact-tree / compose-fact-tree | ios-facts.json（`facts` 命令） |
| android-api-inventory | `ios-api-inventory`（api-inventory.json） |
| android2hmos-resources-convert | `ios-resources-convert` |
| 三源合成（XML+截图+层级） | 程序化 + IB + 静态一致（无运行时截图不伪造） |
| grill C0–C17 两轮 | Gate C + `spec-check`/`source-check` 程序门禁 + 决策账本 D0 |
| hmos-env-doctor | `doctor`（读 host_profile） |
| a2h-tool validate | `validate` |
| adb | 无（iOS 无 adb）；hdc 保留 |
| 契约六件（domain-map/ownership/…） | blueprint 同名契约 + `spec_contract_version` |
| `count-lines` / `mark-stage` | `usage-*` 命令组 / `migration-report` |

## 12. 重写优先级与验收口径

- 差距量化口径：结构（§0/命令表/硬约束/时机表/交接/收尾）是否齐全 > 行数多少。
- 每个重写后的 SKILL.md 应通过本文件 §1–§10 的逐条自检。
- 引用完整性：正文所有 `references/*`、`templates/*`、`scripts/*` 路径必须可解析。