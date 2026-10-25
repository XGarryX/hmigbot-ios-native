---
name: arkts-scenario-runner
description: 在 iOS/HarmonyOS 模拟器上执行复杂 UI 场景（登录、上传图片、跳转到需要前置状态的页面等），为下游验证 skill（如 arkts-visual-verify、a2h-verify）提供"已登录 / 已上传 / 已导航到 XX 页"的就绪状态。当用户说"先登录再截图"、"模拟上传图片"、"跳过登录直接进首页"、"给我造一个已登录的场景"、"HomePage 需要登录态怎么办"、"visual-verify 过不了登录页"、"复杂交互测试"时触发。即使用户只说"登录"、"上传图片"、"造数据"、"mock 登录态"、"scenario"、"前置条件"，只要上下文涉及模拟器驱动或自动化测试，也应触发。核心能力：adb + hdc 双端驱动、YAML 场景脚本、静态 token 注入登录（后续扩展短信/第三方）、相册图片推送 + 系统 picker 选择。与 arkts-visual-verify 是上下游关系：本 skill 负责"把 App 带到指定状态"，visual-verify 负责在那个状态下截图对比。
metadata:
  tags:
  - automation
  - testing
  - scenario
  - login
  - upload
  depends_on: []
---

> **iOS 源输入**：读取 Swift/Objective-C、SwiftUI/UIKit、Xcode 工程及原生资源；实际源构建与设备观测依赖可用的源平台环境。鸿蒙侧构建和验收保持原流程。源侧操作详见 `a2h-spec/references/native-input.md`。

> **iOS 源输入适配**：执行源分析/源设备操作前，读 [原生输入协议](../a2h-spec/references/native-input.md)。它仅替换平台输入；原阶段、模板、规则、门禁、模式和 target 侧执行保持 1.5.2。

> **Codex subagent dispatch convention.** This skill dispatches subagents. In Codex, spawn them with the `spawn_agent` tool and pass `agent_type` = the role name **exactly as written in this skill** — the roles registered under `.codex/agents/*.toml` use the same hyphenated names, so no translation step is involved: `a2h-ios-converter`, `a2h-ios-analyzer`, `a2h-closer`, `a2h-fixer`, `a2h-migration-worker`, `ad-profile-builder`, `compose-fact-analyzer`, `hmos-builder`, `scenario-builder`, `visual-fixer`, `visual-fixer-reviewer`. The built-in `general-purpose` agent_type is unchanged. (Claude's `subagent_type` field is written `agent_type` for Codex; `Agent(...)` dispatch calls are `spawn_agent(...)`; there is no `Task` tool in Codex.)
>
> **Join 协议（收口五条款）。** Codex 子代理完成后**不会**唤醒主会话——结果必须由派发方主动收口，违者=静默卡死（实测事故）。
> ① **循环 wait**：每个 `spawn_agent` 句柄用循环调用 `wait_agent` 收口；单次超时只代表"还在跑"，继续再调；**禁止以"等待子代理"为由结束回合**。醒后必调 `list_agents` 确认是谁完成——**完成的唯一合法信号 = `agent_status` 为 `{"completed": …}`，绝不是产物文件的存在/条数**（文件会中途落盘，读半截=实测事故）；completed 态会在数轮后从 list 中消失，所以每次醒来都要及时查。正文所有"等待完成 / join / 到点即收"表述一律指此循环。
> ② **死句柄与验收**：连续 3 次超时后调 `list_agents` 核对，可配 `wait_for_artifact.py` 探产物活性；已 completed 且 summary 可读 → 直接消费；句柄消失且从未观测到 completed → 按断点重派（带原 prompt + 已落盘产物，上限 2 次），禁止继续等待。**completed ≠ 验收通过**：join 点跑 `python3 .agents/skills/a2h-join/scripts/join_gate.py --project .` 验产物完整性，FAIL 视同未取回、按本条重派。
> ③ **收口锚点**：本 skill 最终完成报告前必须收口全部句柄（join_gate exit 0）；正文写明的显式 join 点优先按正文执行。发用户门（Gate）时允许句柄跨 Gate 存活，但 Gate 摘要必须列明未收口句柄清单 + 各自的指定 join 点。
> ④ **放行 ≠ 遗弃**：正文"非阻塞放行/到点即收/降级继续"只推迟收口时机，不豁免收口义务。
> ⑤ **fire-and-forget**：仅正文显式声明"结果丢弃/不 gate"的派发（如 a2h-execute 的 env-prewarm）免收口；审计只认 join_gate 内静态 allowlist，正文声明只是文档层。
> **派发纪律**：`task_name` 必须唯一（带 page-id/slice-id/round-N 后缀）；并行派发前把预期产物清单写 `spec/a2h/_work/expected_<join点>.json`（join_gate 对账用，契约只认派发方、不认子代理自报）；**谁派谁收**——sub-agent 内部需要"等齐 N 片再合并"时禁止嵌套外派后自行退出，要么同步自做、要么把分片清单回报主会话代派（sub-agent 一停止，收口能力即丢）。**契约产物必须出自承担任务的子代理**：重派上限后仍产不出 → 如实报缺并停在未完成态；禁止派发方代写占位产物让 gate 转绿（声明过也不行——绿账必须对应真产物）。

> **路径约定**：下文 `$SKILLS_ROOT` = 本套 skills 的安装根目录。执行任何脚本前先设一次：`SKILLS_ROOT="$(cd "$(dirname 本SKILL.md)/.." && pwd)"`（用户级安装=`~/.agents/skills`；项目级=`<project>/.agents/skills` 或 `<project>/skills`）。

# arkts-scenario-runner — 复杂 UI 场景执行器

## 0. 用户视角的最短路径（一键化）

用户**只需做一件事**：提供手机号 + 万能验证码。**Agent 模式下(被 模型调用)用户就在聊天框里直接答,模型自动把答案落到 `<project>/spec/scenarios/creds.local.json`;之后自动复用。** 文件名带 `.local.` 中缀表示"本地敏感、不可上传"，脚本写入时自动追加 `.gitignore` 规则。**提包前用 `--purge-creds` 一键清理。**

```bash
# 一条命令搞定,无需先 mkdir、无需先准备 YAML
python $SKILLS_ROOT/arkts-scenario-runner/scripts/scenario_run.py \
    --scenario login --device harmonyos
```

脚本启动时**自动**:
1. `bootstrap`:缺啥补啥 —— 从 skill assets 拷贝 `login.yaml` / `upload_image.yaml` / `scenario.template.yaml` / `default_test_image.jpg` 到项目 `spec/scenarios/`(已存在则跳过)
2. `.gitignore`:把敏感路径(prefs / test_token / artifacts)追加到项目根
3. 解析 `--scenario`:支持裸场景名(`login` → `spec/scenarios/login.yaml`)或完整路径
4. 合并 creds:CLI 的 `--phone`/`--code` > `<project>/spec/scenarios/creds.local.json` 里 `<pkg>` 下的值(找不到时降级读 legacy `~/.arkts-scenario-runner/creds.json`);**缺失时不再阻塞在 stdin prompt,而是写 `needs_input.json` + 退出码 2,由上层(模型)识别并在聊天框问用户**

### 用户配置(零交互目标)

**一次性配好 `<project>/spec/scenarios/creds.local.json`,后续所有 skill 调用全自动**(每个项目一份，不同项目可用不同测试账号):

```bash
# 推荐：直接靠脚本自动收集（首次跑 scenario 时交互式录入 + chmod 600 + 自动加 .gitignore）
python $SKILLS_ROOT/arkts-scenario-runner/scripts/scenario_run.py --scenario login --device harmonyos

# 或显式手动写
python $SKILLS_ROOT/arkts-scenario-runner/scripts/scenario_run.py \
  --save-creds --package com.example.demoapp --phone 138... --code 888888

# 提包前一键删
python $SKILLS_ROOT/arkts-scenario-runner/scripts/scenario_run.py --purge-creds
```

**安全标记**：
- 文件名 `creds.local.json` —— `.local.` 中缀按惯例视为不可上传
- 首次写入自动追加到 `.gitignore`：`spec/scenarios/creds.local.json` + `**/creds.local.json`
- 文件顶层 `_marker.do_not_ship: true` 字段提醒读者
- 文件权限 chmod 600（仅文件所有者可读写）
- CI 可加防呆检查：`find spec -name "creds.local*" && exit 1`

**单文件格式**(按 `<bundleName>.<device>` 两级组织,双端各用一套账号,避免同账号在 iOS/HarmonyOS 互踢登录):
```json
{
  "com.example.demoapp": {
    "ios":   { "phone": "10000000000", "code": "888888" },
    "harmonyos": { "phone": "13800138001", "code": "888888" }
  }
}
```

- `--save-creds --device ios ...` 只写 ios 分支
- `--save-creds` 不带 `--device` → 两端同时写同一份(适合只有一个账号的情况)
- 向后兼容旧 flat 格式 `{pkg: {phone, code}}`:脚本读到会当作两端共用,下次有 `--device` 写入时自动迁移到嵌套结构

**没事先配也不要紧**:模型调 skill 时脚本检测到缺 creds,会在聊天框直接问你,答完自动写入 JSON,以后都复用。图片上传默认选第一张,相册为空时推 skill 自带默认测试图 —— 用户无需手动准备。

### Agent 模式契约(模型调用本 skill 的标准流程)

```
1. 模型直接跑: scenario_run.py --scenario login --device harmonyos
2. 脚本缺 creds → 退出码 2,写 artifact_dir/needs_input.json + result.json.needs_input
3. 模型读 needs_input.json,看到 kind="sms_creds" fields=["phone","code"]
4. 模型在聊天框问用户手机号 + 万能验证码
5. 模型拿到答复后跑: scenario_run.py --save-creds --package <pkg> --phone <...> --code <...>
6. 模型重跑原命令,这次 creds 已就位,场景一路跑通
```

**退出码语义**:
- `0` 成功
- `1` 通用失败(UI selector 找不到、设备离线等)
- `2` 缺输入,等用户答题;检查 `artifact_dir/needs_input.json`

**登录策略默认是 `auto`**：
- 有缓存 prefs → 秒级 `static` 注入
- 无缓存 → `sms` 走 UI 自动登录（手机号 → 万能码 → 登录），**成功后自动把 user_prefs 拉回缓存**，下次直接 static

**图片上传**：用 `pick_first_image_from_gallery` action，自动选第一张；相册为空时自动推 skill 自带的默认测试图后重试。用户不需要手工准备测试图。

跳过这些自动行为：`--no-bootstrap` / `--no-gitignore` / `--no-interactive`。

---

## 1. 定位与边界

**你解决的问题**：下游验证（visual-verify、a2h-verify、人工回归）经常卡在"进不去页面"—— HomePage 要登录、图片编辑页要先选照片、会员中心要有 VIP 态。本 skill 负责把 App **开到目标状态**，然后把控制权交回去。

**你不做的事**：
- 不做视觉对比（交给 `arkts-visual-verify`）
- 不做代码修复（交给对应修复 skill）
- 不做后端 mock（如果场景需要后端配合，明确告诉调用方缺什么）

**双端驱动**：
- iOS 源端：`adb` + `uiautomator dump` + `input`
- HarmonyOS 目标端：`hdc` + `uitest dumpLayout` + `uinput`

为什么要双端？iOS 是行为基线（权威对照），HarmonyOS 是迁移目标。很多场景在两端都需要跑，确保行为对齐。

---

## 2. 工作流决策树

调用方（人类或 visual-verify）给你一个场景名（比如 `login`、`upload_image`、`goto_home`）和目标设备。你按下面的顺序决策：

```
场景名 → 查 spec/scenarios/<name>.yaml
   │
   ├─ 存在 → 进入 [YAML 执行模式]（§4）
   │
   └─ 不存在 → **派 scenario-builder agent 学**（本 skill 不学习，见 §5）
                 builder 产出 YAML + page_scenarios.json 声明 → 回到上面"存在"分支回放
```

**原则**：已知场景走 YAML（确定性 + 可回放 + 可审计）；未知场景的学习**统一归 scenario-builder agent**（合成优先·报缺不装会·证据准入），产出 YAML 后归一到确定性回放。本 skill 是纯回放侧，不做 LLM 实时探索——那样又慢又不稳，且与 builder 形成两套学习实现（2026-07-10 已裁撤本 skill 的探索职能）。

---

## 3. 目录约定

```
<项目根>/spec/scenarios/
├── login.yaml              # 静态 token 注入登录
├── upload_image.yaml       # 推图到相册 + 走 picker
├── goto_home.yaml          # 复合场景：login → 进首页
└── artifacts/              # 每次执行的产物
    └── <timestamp>_<scenario>/
        ├── run.log
        ├── before.png / after.png
        ├── ui_dump_before.xml / ui_dump_after.xml
        └── result.json     # {success, signals, device, duration_ms}
```

**注意**：skill 代码在 `$SKILLS_ROOT/arkts-scenario-runner/`，**所有场景 YAML 和产物都写到项目的 `spec/scenarios/`**。跨项目复用 skill，但场景是项目私有的。

**.gitignore 自动维护**：`scenario_run.py` 启动时会幂等地把敏感/易腐路径追加到项目根 `.gitignore`（`fixtures/test_token.json`、`fixtures/prefs_logged_in/`、`artifacts/`）。已有条目跳过，块头为 `# arkts-scenario-runner (auto-managed)`。不想要这行为加 `--no-gitignore`。注意：`fixtures/images/` 是测试素材，**应该入库**，脚本不会忽略它。

**缺数据的处理**(agent-first):默认**不**阻塞在 stdin prompt。当脚本缺 creds 之类的输入时:
- 写 `artifact_dir/needs_input.json`(包含 `kind`/`fields`/`resolve_cmd`/`then_rerun`)
- `result.json` 带上 `needs_input` 同款内容
- 退出码 2,上层(模型)识别后从聊天框问用户,然后用 `--save-creds` 落盘再重跑
- 人类直接在终端跑也能用:TTY 场景下 `inject_token` 发现 `prefs_file` 不存在会提示手动登录后按回车拉回文件;加 `--no-interactive` 可强制走 agent 模式

---

## 4. YAML 执行模式

### 4.1 Schema

场景 YAML 的完整字段见 [references/yaml-schema.md](references/yaml-schema.md)。最小骨架：

```yaml
name: login
description: 静态 token 注入登录，绕过登录页
platforms: [ios, harmonyos]   # 或只写一端
preconditions: []                  # 依赖的其他场景
steps:
  - action: launch_app
    package: com.example.demoapp
  - action: inject_token
    strategy: static
    token_file: spec/scenarios/fixtures/test_token.json
  - action: relaunch_app
  - action: wait_for
    signal: ui_contains
    value: "首页"
    timeout_ms: 5000
success_signals:
  - type: ui_contains
    value: "首页"
artifacts:
  - screenshot: after.png
  - ui_dump: ui_dump_after.xml
```

### 4.2 执行器

用 `scripts/scenario_run.py` 驱动。读 YAML，按 action 分发到 `scripts/drivers/` 下对应的实现。

```bash
python $SKILLS_ROOT/arkts-scenario-runner/scripts/scenario_run.py \
  --scenario spec/scenarios/login.yaml \
  --device harmonyos \
  --device-id emulator-5554
```

分发到的双端驱动命令（adb / hdc 对照）见 [references/drivers.md](references/drivers.md)。

### 4.3 action 速查

| action | 用途 | 关键参数 |
|---|---|---|
| `launch_app` / `relaunch_app` / `kill_app` | App 生命周期 | `package` |
| `inject_token` | 写登录态（登录的核心） | `strategy`, `token_file` |
| `push_file` | 推图片/文档到设备 | `src`, `dst` |
| `tap` / `long_press` / `swipe` | 基础交互 | `x, y` 或 `selector` |
| `input_text` | 键盘输入 | `text`, `selector` |
| `wait_for` | 等待信号 | `signal`, `value`, `timeout_ms` |
| `screenshot` / `dump_ui` | 产物采集 | `save_to` |
| `assert` | 断言成功条件 | `signal`, `value` |
| `run_scenario` | 嵌套调用 | `name` |
| `pick_first_image_from_gallery` | picker 选第一张；空相册自动补图 | `first_image`, `confirm_btn` |

---

## 5. 未知场景 → 派 scenario-builder（本 skill 无学习职能）

**v2026-07-10 裁撤原"探索模式"**：学习/探索/修配方统一归 `scenario-builder` agent——它的纪律
（合成优先：读树 precondition_recipe 源码锚点，不盲探；报缺不装会：NEED_* 结构化缺口 +
≥3 次实质不同尝试留痕；产出 YAML + page_scenarios.json 声明 + check/create 双配方 + 回放 ×2 验收）
是本 skill 旧探索模式不具备的。两套学习实现并存曾造成派发混乱（exit-10 三处指引两个答案）。

**你（runner）遇到 YAML 不存在 / 回放跑挂需要改配方时**：不要自己探索或改 YAML，
返回结构化信号让调用方（主会话）派 `scenario-builder` agent；builder 学完后调用方重跑回放验证。

---

## 6. 登录策略（核心场景）

登录在所有场景里最常被需要，所以单独讲。

### 6.0 默认策略：`auto`（推荐）

一行配置就能登录，逻辑见 §0 和 [references/login-strategies.md](references/login-strategies.md) 的 `auto` 节。绝大多数场景直接写：

```yaml
- action: inject_token
  strategy: auto
  package: com.example.demoapp
```

### 6.1 静态 token 注入（strategy: `static`）

**原理**：跳过 UI 登录流程，直接把一个已在后端签发好的有效 token 写到 App 的持久化存储里，重启后 App 认为自己已登录。

**产物准备**（一次性，人工）：
1. 在真机或模拟器上手工登录一次测试账号
2. 用 `hdc shell cat /data/app/el2/100/base/com.example.demoapp/haps/entry/files/UserPreferences.xml`（或 Preferences 对应路径）导出 token、userId、vipLevel 等字段
3. 存为 `spec/scenarios/fixtures/test_token.json`：
   ```json
   {
     "token": "eyJhbGc...",
     "userId": "12345",
     "vipLevel": 0,
     "iosId": "test-ios-id"
   }
   ```

**执行时**：脚本把这些字段写入三处（对齐 AGENTS.md 的"token 三路同步"）：
- `AppStorage['token']`
- `UserPreferences` 对应键
- `lib_network.UserData`

写入手段优先级：
1. **首选**：App 重启后读配置文件加载 —— 直接 push 一份预置 Preferences XML 到沙箱（最稳）
2. **次选**：通过 `hdc shell aa start` 传参启动，配合 App 端一个 "debug entry" 启动器（需要一次性在 App 里加）
3. **下策**：UI 自动化走完整登录流程（慢且易碎）

详见 [references/login-strategies.md](references/login-strategies.md) 的 "static token 完整步骤"。

### 6.1.1 Debug entry 策略（`strategy: debug_entry`，推荐，尤其登录页未实现时）

**适用场景**：鸿蒙端登录页还没迁移完，但业务页需要登录态才能测。

**原理**：App 在 EntryAbility 里预埋 ~10 行 debug-only 代码，识别启动参数 `debug_inject_token` 后把 token 同步写到三处（`AppStorage` + `UserPreferences` + `lib_network.UserData`）。`BuildProfile.DEBUG` 保证 release 构建整段被剥离。

```yaml
- action: inject_token
  strategy: debug_entry
  package: com.example.demoapp
  ability: EntryAbility
  token_file: spec/scenarios/fixtures/test_token.json   # { "token": "..." }
  verify_signal: "首页"        # **强烈建议必填**：启动后 wait_for 文本/selector，不命中判注入失败 → scenario_run.py 返回 exit 1。下游（如 visual-verify）只信 exit 码判 scenario 成功与否；缺 verify_signal 时 scenario_run.py 跑完所有 action 就返回 exit 0，无法识别"App 在前台但停在错页"
  verify_timeout_ms: 6000
```

**为什么比 `static` 更可靠**：
- 不依赖沙箱写权限（非 root 真机 push prefs 会失败）
- 不依赖 iOS/鸿蒙 prefs 格式对齐（XML vs 二进制）
- 冷启动 / 热启动都覆盖（onCreate + onNewWant）

App 侧完整模板、校验方法见 [references/login-strategies.md](references/login-strategies.md) §手段 B。

### 6.2 SMS 策略（已实现）

通常由 `auto` 内部触发，用户不需要直接写。手机号 + 万能验证码按 bundleName + device 存在 `<project>/spec/scenarios/creds.local.json`（不同 App / 不同项目万能码可能不同）。**建档信息优先从契约参考文件 `spec/baseline/dev_info.json` 取**（迁移产物约定的联调信息，存在才读；LLM 编排层读它后跑 `--save-creds` 转档，脚本机械层仍只认 creds.local.json），没有才要人工提供。UI selector 有默认值，不同 App 可通过 `sms_flow` 字段覆盖。详见 [references/login-strategies.md](references/login-strategies.md)。

### 6.2.1 HarmonyOS ArkUI TextInput 注入失效的正解（实测坑）
鸿蒙端 ArkUI 的 `TextInput` 用 `uitest uiInput inputText <x> <y> <text>` / `uitest uiInput text` / `uinput -K -t <text>` **常全部静默失效**(字段仍是 placeholder,dump 也抓不到)。**正解 = 走真实软键盘**:
1. 用 `uitest dumpLayout` 拿 `type=TextInput` 节点的真实 bounds(普通 dump 过滤空输入框,抓不到),tap 其中心**聚焦**;
2. 截图确认软键盘弹出(数字键盘/全键盘),按**键位坐标**用 `uinput -T -c <x> <y>` **逐键点击**输入(数字键位固定,可表驱动);每键间隔 ≥0.4s(批量循环过快会丢键);
3. 输完按键盘「完成/收起」再点提交按钮(键盘可能盖住提交键)。
> iOS端 `adb shell input text <数字串>` 正常,无需此法;此坑仅鸿蒙 ArkUI。

### 6.2.2 登录/前置失败 → 必先对照实验,别默认 needs_input/环境（防漏测铁律）
登录(及上传/授权等前置)**本身就是被迁移的功能点**。当本 skill 驱动它在某端失败时,**不要立即归因 needs_input/UI mismatch/环境** —— 那条路没有 FAIL 通道,会把真·功能退化掩盖成"没就绪"(已发生真实漏测:鸿蒙登录按钮不真正发起登录、点完<1s即关页退回登出态,差点被当"模拟器网络问题")。失败时 `notes`/`needs_input.json` 必须带上对照信息供上层判:
- **另一端相同输入是否成功**(如iOS同账号同万能码能否登录);
- **失败端平台是否健康**(ping 通 / UI 控件完整 / 其它 scenario 能跑);
- **失败形态**:即时失败(<1s 关页/无 loading/无报错 = 处理没真执行,强指向功能未实现) vs 等待超时(才考虑网络)。
上层(visual-verify / a2h-verify)据此:另一端成功 + 平台健康 + 即时失败 → 判**门禁功能退化**写 P0 FAIL,而非升级用户。详见 visual-verify SKILL.md「门禁功能对照实验铁律」。

### 6.3 OAuth 策略（预留）

第三方登录，见 [references/login-strategies.md](references/login-strategies.md) 的 OAuth 节。

---

## 7. 上传图片场景

**拆解**：
1. 把图片 push 到设备相册（`/storage/emulated/0/Pictures/` 或 HarmonyOS 的 media library）
2. 触发相册媒体扫描（让系统感知到新图）
3. 驱动 App 走"选图"入口，等系统 picker 出现
4. 在 picker 里选中刚推进去的图
5. 等 App 回到"已选图"状态（用 `wait_for`）

关键是**picker 的识别**：iOS 是 `com.ios.documentsui`，HarmonyOS 是 `com.huawei.hmos.photos`（或系统 Photo Picker）。两端 selector 不同，YAML 里用 `platforms` 字段分别配置。

详见 [references/upload-image.md](references/upload-image.md)，含 push 命令、扫描命令、picker selector 速查表。

**设备自动化踩过的坑（真机 / 模拟器通用，必读）**：见 [references/device-automation-pitfalls.md](references/device-automation-pitfalls.md)。核心 4 条：
1. 系统进程（PhotoPicker 等）`dumpLayout` **能**看到节点，不要凭经验目测坐标；坐标用物理像素，不是截图视觉尺寸
2. 长等待前先把 `screen_off_timeout` 调大或用 swipe 心跳保活；永远别主动按 Power 键
3. 中途状态判断用 `aa dump -l` / `dumpsys activity top`，截图只留给最终视觉取证；tap + 取证打成一条 bash
4. 摸到稳定 selector 立刻回写 reference；文本 selector > class+index > 硬编码坐标

---

## 8. 产物协议（供下游消费）

每次执行完，在 `spec/scenarios/artifacts/<timestamp>_<scenario>/` 下生成 `result.json`：

```json
{
  "scenario": "login",
  "device": "harmonyos",
  "device_id": "emulator-5554",
  "success": true,
  "duration_ms": 8432,
  "signals_matched": ["ui_contains:首页"],
  "artifacts": {
    "screenshot_after": "after.png",
    "ui_dump_after": "ui_dump_after.xml"
  },
  "notes": ""
}
```

下游（visual-verify 等）读这个文件决定是否继续。`success: false` 时 `notes` 字段要写清失败原因（哪个 action 卡住、超时还是 assert 失败）。

---

## 9. 与 arkts-visual-verify 的契约

（v2026-07-10 更新，对齐 visual-verify 现役调度模型）scenario 的执行**归主会话、在 trip/batch 边界统一调度**，sub-agent 不跑 scenario：

```
visual-verify 主会话（trip 起点 / batch 边界）
   → python3 $SKILLS_ROOT/arkts-visual-verify/scripts/run_scenario_with_verify.py --trip <trip> \
         <scenario> <device> --device-id <id> --package <pkg>
   （包装脚本内部调本 skill 的 scenario_run.py——失败计数 + transient retry + exit code 机械路由：
    0=继续 / 10=派 scenario-builder 学·修 / 20=凭据 / 30|40=对照实验 / 50=环境）

visual-verify sub-agent 遇 precondition 不满足
   → trip 级态（login/门链）：不自己造，写 SKIPPED/BLOCKED 交主会话按路由处理
   → 数据态（state_required）：先走自愈梯（复验 check → 限额 1 次重放 create → 才 BLOCKED；
     配方名读 progress.json.states_provisioned，无配方不自学——学习归 scenario-builder）
```

**严格禁止**：①sub-agent 自己跑 scenario / 手敲 adb input 满足 preconditions（状态漂移无人追踪）；②**建态/造态**（trip 态+数据态）裸跑 `scenario_run.py`（吞 needs_input 信号、丢失败计数）——一律走包装脚本。
**豁免（嵌入引擎消费者，2026-07-10 划界）**：`verify_outcome.py`（判定工具——事务跑不通**本身就是判定结果** reached_outcome=false=真退化该出 P0 单；套包装脚本会把它误诊成"配方坏了"去自修，正是 Q2 漏测病根）与 scenario-builder 的学习验收回放，**保持直调 scenario_run.py，禁止"好心"改走包装脚本**。判界一句话：造态=包装脚本（失败要自修），判定/学习=直调引擎（失败是数据）。

### 9.1 precondition kind → scenario name 映射表（源头固化）

调用方（visual-verify 主会话建 trip 态 / builder 学配方命名）看 fact-tree.preconditions[].kind 后**按本表选 scenario name**。本表是单一权威源——visual-verify SKILL.md / sub-agent prompt 不重复定义、直接 reference 这里。

| fact-tree precondition.kind | scenario name | 何时触发 | YAML 模板 |
|---|---|---|---|
| `login_required` | `login` | UserData.isLogin() 检查 | spec/scenarios/login.yaml |
| `login_conditional` | `login` | interceptAuth==1 等条件登录 | 同上 |
| `vip_required` | `mock_member` | UserData.isVip() / VipFunctionInterceptDialog | spec/scenarios/mock_member.yaml |
| `credits_required` | `mock_credits` | freeCount/remainCount<=0 | spec/scenarios/mock_credits.yaml |
| `intercept_dialog` | （上游 login + vip 两套 scenario 通常已覆盖） | showInterceptDialog | — |
| `param_required` | **见 §9.2 param 映射子表** | Activity 读 intent extra + finish() gating | — |
| `state_required` | （case by case，看 record.preconditions[].required_state） | 需特定运行时状态 | — |

### 9.2 param_required 子表（按 required_params 内容映射 scenario）

`param_required` 是最常见的"页面需特定 intent extra 才能渲染"模式（如 CreateOutLinePage 必须有 `query` 或 `filePath`）。本表按 params 集合命名对应 scenario：

| required_params | scenario name | 业务语义 | 默认输入源 |
|---|---|---|---|
| `["query"]` / `["query","filePath"]` | `input_ppt_topic` | 在 HomeFragment 输入主题后跳 CreateOutLinePage | creds.local.json.${pkg}.topic / 默认 "AI 赋能企业培训方案设计" |
| `["filePath"]` | `upload_doc_for_ppt` | 在 HomeFragment 切到导入文档 tab，选文件后跳转 | spec/scenarios/fixtures/sample.docx |
| `["jsonStr"]` / `["templateId"]` | `goto_choice_template` | 先到 ChoicePPTTemplatePage 选个模板，再跳 PPTTemplatePreviewPage | — |
| `["payFrom"]` | `goto_member_center` | 任意触发会员中心入口 | — |
| `["url"]` / `["webUrl"]` | （不需要专门 scenario） | WebViewActivity 类，url 在 navigation.params 里已有，直接传 extras | — |
| 其它未知 params | （sub-agent 必须 escalate） | 写 needs_input.json 让主会话补 YAML | — |

**新增 scenario 流程**：发现新的 `param_required` 没列表时，sub-agent → 调本 skill → skill 检测无对应 YAML → exit 2 + 写 needs_input.json → 主会话引导用户补 YAML 到 spec/scenarios/ 并扩本表。

### 9.3 wizard_step / tab 不走 scenario，走 visual-verify 内的导航

`relationship_kind == "wizard_step"` 或 `"tab"` 不应该调 scenario-runner——它们是同 host 的兄弟节点，正确做法是 visual-verify 自己用 dumpLayout + tap 切到对应 step/tab（按 host.wizard_steps[i].fragment_id 顺序 + label）。本 skill 只处理跨 Activity / 需要后台数据注入的场景。

调用方要自己设超时（建议 60s），本 skill 不做外部超时兜底。

---

## 10. 常见坑

**坑 1：token 注入后 App 不认**
多半是 `UserPreferences` 和 `AppStorage` 不同步。务必三路都写，或直接 push 一份完整 Preferences 文件覆盖，让 App 冷启动读。

**坑 2：坐标点击在不同分辨率失效**
YAML 里永远优先 `selector`（resource-id / text），坐标是最后手段（builder 学配方时同规矩）。如果必须用坐标，在 YAML 里标注 `resolution: 1260x2720` 给后人提醒。

**坑 3：UI dump 空 / uitest 卡住**
HarmonyOS 的 `uitest` 偶发超时。重试 2 次，仍失败就 kill uitest 进程再试（`hdc shell pkill uitest`）。

**坑 4：图片推进去相册但 App 里看不到**
没触发媒体扫描。iOS：`adb shell am broadcast -a ios.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://<path>`。HarmonyOS：用 `photoAccessHelper` 的重新扫描接口或直接 reboot emulator（慢但有效）。

---

## 11. 扩展新场景的最短路径

1. 确认场景名，查 `spec/scenarios/<name>.yaml` 是否存在
2. 不存在 → 派 `scenario-builder` agent 学（§5）→ 产出 YAML
3. 存在 → 直接 `scenario_run.py` 跑
4. 新的 action 类型没有 → 在 `scripts/drivers/` 加一个新 driver，更新 §4.3 表格
5. 新的登录策略 → 读 [references/login-strategies.md](references/login-strategies.md) 的扩展设计，落在 `inject_token` 的 strategy 分支里

保持一个习惯：**每个场景只学一次、沉淀为 YAML**——学习是 builder 的一次性动作，回放是本 skill 的无限次动作。
