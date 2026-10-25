---
name: codex-plugin-e2e
description: hmigbot-CodeX(Codex 原生包)的集成 / 端到端测试用例。基本用例 I2 = 完全照《README》第 3-5 章装一遍(codex CLI → clone → install.sh)、起一遍、`$a2h-run` 迁一遍,然后把本地 rollout 与服务端导出的会话逐字节对比,不一致就报 issue。当要验证 Codex 交付形态是否可用、rollout sweep / upload-session 是否上传,或改了 codex 侧 skills / install.sh / AGENTS.md / runtime 的 codex 分支后要回归时使用。触发词:"codex 端到端"、"codex 腿"、"集成测试"、"照手册跑一遍"、"rollout 上传验证"。
---

# hmigbot-CodeX(Codex 原生包)—— 集成 / 端到端

跨仓全景与坑表见用户级 skill `migbot-e2e-telemetry`;本文件只讲 **Codex 线**的用例。

## 铁律:集成测试从客户视角触发

- **用户手册是唯一权威**:[README.md](../../README.md) §3 安装、§4 首次使用、§5 端到端迁移工作流。
  用例每一步都要能在手册里指到出处;手册没写的动作,测试者**不许做**。
- **需要手册外的动作才能继续 = 发现了缺陷**。停下,记 issue,并在报告里写明卡在哪一步、
  绕行后哪一环没验到(§4)。
- 内部脚本(`run-codex-e2e.sh`)是**开发自测**,不是集成用例:它不走 `install.sh`,
  自己搭工程和 config,跑绿了也不证明客户装得上。放在 §5,不许替代 I2。

## 用例 I2(基本集成用例):照手册装 → 起 → 迁 → 对比 → 报错

**类型**:集成 · 端到端 · 客户视角手工/半自动
**验的功能**:一次性安装脚本落地全部资产、`$` 前缀 skill 可触发、五阶段流水线跑得完、
hookless rollout sweep 把会话完整送到服务端。

### 步骤(每一步都标了手册出处)

| 步 | 手册出处 | 客户动作 | 期望 |
|---|---|---|---|
| 1 | §3 第 ⓪ 步 | `codex --version` | ≥ 0.143.0;没装则 `npm install -g @openai/codex` / `brew install --cask codex`,首次 `codex` 完成登录 |
| 2 | §3 第 ① 步 | `git clone` 本仓 → `cd hmigbot-CodeX` | — |
| 3 | §3 第 ② 步 | `./install.sh --target <你的鸿蒙工程>`(Windows:`powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target …`) | 真实终端里**弹出《用户体验改善计划》窗口**并当场询问;工程下出现 `.agents/skills/`(90 个)、`.codex/agents/*.toml` + `config.toml`、`.migbot/bin/` + `policies/`、`AGENTS.md` |
| 4 | §3 幂等说明 | 再跑一次 `install.sh` | 只覆盖分发资产,**不覆盖** `.migbot/config.json` |
| 5 | §4 | `cd <鸿蒙工程>`(有 `oh-package.json5`)→ `codex` | 进入会话 |
| 6 | §4 | `$a2h-init`(中文 `$a2h-init-zh`) | 逐项确认路径 → `.migbot/config.json` 的 `confirmed: true`,`run_id` / `hmigbot_session_id` / `install_id` 齐全,`telemetry_consent: granted` |
| 7 | §5 | `$a2h-build` | 迁移前基线:空工程能编译。**无设备时这步不通过是预期的**,见下方说明,继续走第 8 步 |
| 8 | §5 | `$a2h-run` | 五阶段依次产出手册 §5 表里的标志文件;每阶段暂停确认后自动续跑 |
| 9 | §5 | `$a2h-build` | 迁出来的代码能编译 |
| 10 | §6 | `$a2h-privacy status` | 回显的 `migbot_session_id` 与 config.json 一致 |

> **`$a2h-build` 失败不阻塞 `$a2h-run`**(用户 2026-08-30 裁定)。`a2h-tool validate` 把
> 「设备/模拟器在线」和「路径配置」放在同一个 `failures[]` 里,没有iOS或鸿蒙设备时它返回
> `ok:false`,`$a2h-build` 随之停下 —— 但这只是**这一步**停下,五阶段照常跑。报告里如实写
> 「a2h-build 因无设备未通过,流水线继续」,**不要写成「迁移被阻塞」,也不要去改 `a2h-tool`
> 的门禁**(2026-08-30 曾据此误改并已回退)。定性缺陷前,先看后续步骤是不是真的停了。

> 第 3 步的协议弹窗**必须在真实终端里出现**。Codex 沙箱内弹不出来,若被推迟到
> `$a2h-init` 才处理,那本身就是要报的问题(手册明确要求在安装时决定)。
> 第 8 步的阶段标记必须由 `a2h mark-stage` 真实生成,**禁止手写** `.done` 伪造。

### 验证:本地 rollout vs 远端会话,逐字节

> **前置:远端会话数据要从看板取,看板要登录。首选做法 ——**
> **让使用者自己在浏览器里登录看板**,然后就在那个已登录的浏览器里操作下载
> (跑测试的 agent 可以用 chrome-devtools MCP 接管这个浏览器点)。这样不碰密码,
> 也不受图形验证码影响。
> **使用者没有账号** → 停在这一步,提示他去向 migbot-server 管理员 / 项目负责人申请;
> 不要改用本地替身悄悄绕过 ——「拿不到自己的会话数据」本身就是客户会遇到的问题。
> 无人值守场景才用 `--from-dashboard`:账号写进本 skill 的 `scripts/.env`
> (照 `scripts/.env.example`,已 gitignore),密码只留在 `.env` 里,不写进文档、
> 脚本、issue、报告,也不要贴进对话。
> `--local-server` 只在**本地服务端形态**(自己起的 migbot-server)下用,报告里写明。

浏览器里的下载路径(手册同款):找到本轮 App 的行 → 打开「迁移事件流」→ 弹窗里点
**「下载本次会话数据」**。⚠ 必须先打开时间轴,否则按钮会 alert「请先打开一次会话的
时间轴」;用 MCP 驱动时 alert 会阻塞后续求值,记得 `handle_dialog` 收掉。

```bash
# 首选:浏览器刚下载完,直接取下载目录里最新的包(会核对 run_id 是不是本轮)
python3 tools/codex-plugin-e2e/scripts/compare-sessions.py <工程> --from-downloads
python3 tools/codex-plugin-e2e/scripts/compare-sessions.py <工程> --from-downloads ~/Desktop   # 换了下载目录
# 指定包 / 无人值守 / 本地服务端形态
python3 tools/codex-plugin-e2e/scripts/compare-sessions.py <工程> --tar <包路径>
python3 tools/codex-plugin-e2e/scripts/compare-sessions.py <工程> --from-dashboard
python3 tools/codex-plugin-e2e/scripts/compare-sessions.py <工程> --local-server
```

**通过标准**(缺一不可):

1. `outbox: pending=0 dead=0`;
2. 本地水位线里**每一个**会话都能在导出包里找到 —— Codex 线一个阶段一轮
   `codex exec` 就是一个独立 session,五阶段跑完 session 数应 ≥ 5;
3. 每个会话与 `transcript_path` 指向的本地 rollout **逐字节相同**
   (脚本输出 `✅ N/N 个会话本地与远端逐字节一致`);
4. 看板上该 App 一行,五阶段全归因、verify 后判定已完成,应用名是真实应用名。

**「看板上看得到」不算通过**(2026-08-30 用户裁定)。

本地 rollout 路径以水位线为准:
`.migbot/metrics/<run_id>/session-watermarks/<sid>.enqueue-state.json` 的 `transcript_path`
(Codex 线形如 `~/.codex/sessions/YYYY/MM/DD/rollout-<时间戳>-<sid>.jsonl`)。

## 2. 环境替身:唯一允许的偏离

资源包里的二进制烘焙了**生产**打点端。要在本地闭环验证时,只允许这一处偏离:

```bash
export A2H_INGEST_BASE=http://127.0.0.1:5005      # 必须在启动 codex 之前 export
export A2H_UPLOAD_BASE=http://127.0.0.1:5005/api/v1/ingest
codex
# 验证:compare-sessions.py <工程> --local-server
```

额度耗尽时走 DeepSeek 是**手册外的开发通道**,只用于 §5 自测,不用于 I2:

```bash
export DEEPSEEK_API_KEY=$(cat ~/.deepseek-api-key)
CODEX_EXEC_ARGS="-c model_provider=deepseek -c model=deepseek-v4-flash -c model_reasoning_effort=low" \
  bash tests/smoke/run-codex-e2e.sh     # 脚本在 migbot-runtime-src 仓
```
`~/.codex/config.toml` 里该 provider 必须 `wire_api = "responses"`(codex 已不支持 `"chat"`)。

## 3. 每轮的环境要求

- **每轮新建鸿蒙工程目录**,带时间戳,不复用。
- 安装要在干净工程上做:上一轮的 `.agents/ .codex/ .migbot/ AGENTS.md` 残留会让
  「幂等」与「协议弹窗」两条断言失效。
- 二进制来源:安装器把**资源包 hmigbot-set-codex** 的 `migbot/bin/a2h-<os>-<arch>` 拷进
  工程 `.migbot/bin/`。`a2h-codex-*` 自 runtime **v1.4.1 起已退役**,set 仓里只有 `a2h-*`;
  本地只覆盖 `a2h-codex-darwin-arm64` = 白覆盖,安装器仍取旧版
  (2026-08-30 实测:工程里跑的还是 v1.4.5)。
- `codex exec` 后台跑必须 `< /dev/null`,否则挂在 stdin 上不动。

## 4. 发现错误 → 汇报 → 提 issue

跑用例的人**同时负责把问题落成 issue**,不能只在对话里说"失败了"。

1. **当场留证**:失败步骤的完整输出、`.migbot/config.json`、`a2h status --json`、
   compare 脚本打印的 run_id / msid / 导出包路径。
2. **判断归属仓**:skills / install.sh / AGENTS.md → 本仓;a2h sweep / upload / fact →
   `migbot-runtime-src`;rollout 解析 / 看板 / 导出 → `migbot-server`。跨仓各发一条并互链。
3. **按模板写**:问题描述、复现步骤、修复建议、测试方法,每条带命令输出或 `file:line`。
   模板见 `hmigbot-plus/tools/hmigbot-issue-report/SKILL.md`;发前
   `gh issue list -R <repo> --state all --search "<关键词>"` 查重。
4. **报告写清哪一环没验到**:被绕开的那一环记 FAIL,不因为"最后数据齐了"改判 PASS。

常见结论的定性:

| 现象 | 定性 |
|---|---|
| facts 照常到、会话记录一条没有、`flush` 恒 `sent=0` | 工程 `.migbot/bin` 是旧二进制(无 sweep / `upload-session`)→ 报资源包 / 运行时版本 |
| 远端比本地短、前缀一致 | 尾部未上传 → 先确认 flush 排空;仍缺就是上传截断 bug |
| 一个 session 跨多个 run,服务端 watermark 返回 0 | **按设计**;客户端两道闸(`sessionOwnedByOtherRun` + `run_created_at`)负责不重传,改 sweep 后要专门回归 |
| 协议窗口没弹、只能手动打开文件 | 报本仓 install.sh —— 手册承诺真实终端会弹 |
| 无设备 → `$a2h-build` 报 `ok:false` | **预期的局部失败**,不阻塞 `$a2h-run`;记为「该步未通过(无设备)」,不是缺陷 |

## 5. 开发自测(不是集成用例,不可替代 I2)

```bash
cd ~/Workspace/migbot_set/migbot-runtime-src
bash tests/smoke/run-codex-e2e.sh
```

每阶段一轮真实 `codex exec`(各自独立 session)→ 五阶段产物 → sweep 上传 → 服务端断言。
通过标准:session ≥ 5、五阶段全归因、verify 后看板判定已完成、outbox 清零。
**发版验收仍以 I2 为准。**

改了 runtime 或 server,**必须两条腿都跑**(本腿 + hmigbot 的 CC 腿)。
