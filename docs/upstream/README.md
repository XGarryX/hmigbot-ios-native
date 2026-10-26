# MigBot × Codex CLI

> Android → ArkTS / HarmonyOS 迁移工具包，移植到 **Codex CLI**（repo-only：clone → install → 用）。
> 90 个 skill · 7 个子 agent · a2h 运行时 · 中英双语。
> 目标 Codex CLI `0.143.0`（Rust 版）。移植依据见 [`docs/PORTING.md`](./docs/PORTING.md)。

[English](#english-below) · 中文为主文档

---

## ⚠️ 先读：与 Claude 版的三点关键区别

如果你用过 Claude 版的 migbot，请先注意：

| 项 | Claude 版 | **Codex 版** |
|---|---|---|
| **触发前缀** | `/a2h-run`（slash 命令） | **`$a2h-run`**（`$` 前缀，或 `/skills` 选择器，或自然语言）— Codex 无自定义 slash 命令 |
| **安装** | 一步装插件 | **一步**：clone 仓库 → 跑 `install.sh`/`install.ps1`（一次性落地 skills+hooks+agents+runtime+config+AGENTS.md） |
| **指令文件** | `CLAUDE.md` | **`AGENTS.md`** |

> `$` 不是笔误。Codex 的 slash 命令是编译期写死的，没有自定义入口——所以 12 个命令转成了 skill，用 `$a2h-run` 触发。

---

## 1. 它能做什么

把一个现有 Android 应用迁移成 HarmonyOS（ArkTS）工程：自动分析 Android 源码 → 生成迁移规格与计划 → 逐特性执行迁移 → 编译/视觉验证 → 复盘归档。一条 `$a2h-run` 跑完五阶段流水线，每阶段暂停确认、断点自动续跑。

核心命令：

| Skill | 作用 |
|---|---|
| `$a2h-init` / `$a2h-init-zh` | 首次初始化：探测路径 + 同意《用户体验改善计划》 |
| `$a2h-run` / `$a2h-run-zh` | 跑完整迁移流水线（spec → plan → execute → verify → retrospect） |
| `$a2h-build` / `$a2h-build-zh` | `hvigorw assembleHap` 编译 HarmonyOS 工程 |
| `$a2h-privacy` / `$a2h-privacy-zh` | 查看 / 授予 / 撤回《用户体验改善计划》同意 |
| `$migbot-increment-init` 等 | 增量迁移（init → workflow → review → archive） |

---

## 2. 环境要求

| 组件 | 要求 |
|---|---|
| **Codex CLI** | `0.143.0`+（`codex --version`） |
| **DevEco Studio** | 已安装（提供 hvigorw、hdc、HarmonyOS SDK） |
| **Android 源码** | 待迁移的 Android 工程（与 HarmonyOS 工程同级或可被探测到） |
| **adb** | Android SDK platform-tools（验证阶段检测设备/模拟器在线） |
| **hdc** | HarmonyOS commandline-tools（同上） |
| **设备/模拟器** | 至少一台 Android 与一台 HarmonyOS 设备/模拟器在线（验证阶段需要） |

macOS / Linux / **Windows**（原生 `.ps1`，不依赖 Git Bash）均支持。

---

## 3. 安装

### 第 ⓪ 步（前置）：安装并登录 Codex CLI

Codex CLI 是本插件的宿主，必须先装好。先检查是否已有：

```bash
codex --version    # 应输出 0.143.0 或更高
```

若未安装——Codex CLI 虽用 Rust 编写，但官方通过 npm 分发：

```bash
# 方式一：npm（需先装 Node.js 18+，npm 随附）
npm install -g @openai/codex

# 方式二：macOS Homebrew
brew install --cask codex
```

装好后首次运行 `codex`，按提示完成登录（ChatGPT 账号或 OpenAI API key）。`codex` 能正常进入会话后，再继续下面两步。

> 参考官方文档：<https://developers.openai.com/codex/cli> · <https://github.com/openai/codex>

> **桌面版用户**：无需安装 CLI——直接用 Codex 桌面应用（Windows：Microsoft Store 的 ChatGPT 应用；macOS：Codex App），§3 的安装脚本照跑。但钩子信任必须在应用设置 UI 里手动打开，见 [§5 桌面版使用说明](#5-codex-桌面版codex-app--chatgpt-桌面应用使用说明)。

### 第 ① 步：clone 仓库

```bash
git clone fuxi-ailabs/hmigbot-CodeX
cd hmigbot-CodeX
```

### 第 ② 步：跑安装脚本（一次性落地全部）

一条命令把 skills、hooks、agents、runtime、config、AGENTS.md 全部写到你**目标 HarmonyOS 工程**里（不走任何插件市场）：

```bash
# macOS / Linux（在 hmigbot-CodeX 仓库根目录）
./install.sh --target /path/to/your-harmony-app

# Windows（默认 ExecutionPolicy=Restricted 会拦截直接 .\ 运行，用 Bypass 跑）
powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target C:\path\to\your-harmony-app
```

> **语言**：`--lang zh|en`（PowerShell `-Lang`）同时决定安装脚本的全部输出、协议弹窗语言、`hook-trust` 自检文案，以及 `$a2h-init` 之后走中文还是英文技能。不传时按系统 locale（`LANG`/`LC_ALL` 含 `zh` → 中文，否则英文）。`a2h hook-trust` 单独运行时也接受 `--lang`，或设 `A2H_LANG=zh`。

> 安装脚本在**真实终端**里会弹出「用户体验改善计划」协议窗口并当场询问是否加入（`--no-consent` / `-NoConsent` 可跳过，无人值守安装自动跳过）。**务必在这里决定**——Codex 沙箱内无法弹窗，若留到 `$a2h-init` 里只能手动打开文件阅读。加入与否的结果会记进 `.migbot/config.json`。

安装脚本会往目标工程写入：

```
your-harmony-app/
├─ .agents/
│   └─ skills/               # 90 个 skill
├─ .codex/
│   ├─ agents/*.toml          # 7 个子 agent
│   └─ config.toml            # 配置（sandbox + [features] hooks/multi_agent + [agents] 并发/深度 + [hooks.*] usage hook）
├─ .migbot/
│   ├─ bin/                   # a2h 遥测二进制 + a2h-tool/a2h-bootstrap（bash/.ps1）
│   └─ policies/              # 《用户体验改善计划》中英文
└─ AGENTS.md                  # 语言指令标记块
```

> 安装是**幂等**的：重跑只覆盖分发资产，不重复写 config，永不覆盖你的 `.migbot/config.json`。

---

## 4. 首次使用

```bash
cd /path/to/your-harmony-app   # HarmonyOS 工程根目录（oh-package.json5 所在处）
codex
```

进入 Codex 后：

```text
$a2h-init        # 首次初始化（中文输出用 $a2h-init-zh）
```

`$a2h-init` 会：

1. **探测路径**：自动找 Android 源码、DevEco、hvigorw、adb、hdc，生成 `.migbot/config.json` 骨架，然后逐项跟你确认。
2. **弹出《用户体验改善计划》**：用系统原生窗口打开（`a2h-agreement`），**绝不把全文贴进对话**。参与是使用前提。
3. **同意** → 生成安装句柄 `migbot_session_id`，由 `a2h init-run --consent granted` 写入 config 并固化 `run_id`（不走宿主 OTel，无需为打点重启）。
4. **拒绝** → 迁移流水线（从 `$a2h-spec` 起）禁用，期间不上报任何数据；随时可 `$a2h-privacy accept` 启用。


> 路径确认无误后，`.migbot/config.json` 的 `confirmed: true`，之后 `$a2h-run` 不会再跳回 init。

---

## 5. Codex 桌面版（Codex App / ChatGPT 桌面应用）使用说明

> 桌面版（Windows 上即 Microsoft Store 的 **ChatGPT** 应用；macOS 上为 **Codex App**）与 CLI **共享同一套配置与钩子**（`~/.codex/config.toml` + 工程的 `.codex/`），§3 的安装脚本照常适用。差异只在两处：**工作区打开方式**，与**钩子信任必须到应用设置 UI 里手动点开**（桌面版没有 `/hooks` 命令）。

### 5.1 把工程目录作为工作区打开（否则钩子不加载）

桌面版默认在 `Documents/Codex/...` 建自己的工作区。在默认工作区里，工程的 `.codex/config.toml` **不会被加载，钩子不触发，服务端零数据**。必须显式把 HarmonyOS 工程目录作为工作区/文件夹打开：


### 5.2 在应用设置里信任 6 个 migbot 钩子

1. 应用设置 → **编码/开发者**（Settings → Coding）→ **Hooks** 面板；
2. 找到该工程下列出的 6 个 migbot 钩子（命令为 `.migbot/bin/a2h(.exe) hook`）；
3. 逐个点开 **Trust / 启用**。
<img width="492" height="405" alt="image" src="https://github.com/user-attachments/assets/153a69a1-4580-4454-8579-9841e86fd03d" />
<img width="1635" height="827" alt="image" src="https://github.com/user-attachments/assets/e31fa760-68c6-46cf-b796-307149853557" />
<img width="1635" height="825" alt="image" src="https://github.com/user-attachments/assets/ab069f67-3b7a-47ce-8822-86a1de332a57" />


- **点击即时生效，无需重启应用**；
- 未信任的钩子被 Codex **静默跳过**——面板里"看得到 6 个钩子" ≠ 在触发；服务端表现是"有 msid、无会话数据"；
- 信任按**工程路径**记录：换机器、换工程目录后要重新信任。

### 5.3 信任后的验证

```bash
# macOS / Linux
.migbot/bin/a2h status        # 出现会话登记 = 钩子已触发
.migbot/bin/a2h hook-trust    # 自检（其 "NOT TRUSTED" 判定有已知单引号误报，
                              # 以应用 Hooks 面板的 Active 状态为准）

# Windows（PowerShell）
.\.migbot\bin\a2h.exe status
.\.migbot\bin\a2h.exe hook-trust
```

### 5.4 桌面版与 CLI 的已知差异

- 桌面版自带独立的 codex 运行时（实测 0.153.0-alpha.5），与终端 `codex --version`（npm 安装）**互相独立**；两侧读同一份 `~/.codex/config.toml`；
- Windows 桌面版会向用户级配置写入 `[windows] sandbox = "unelevated"`（桌面专用键），实测不影响钩子执行；
- 桌面版会话文件与 CLI 同目录（`~/.codex/sessions/`），服务端切片链路一致。

---

## 6. 端到端迁移工作流

```text
$a2h-build       # 先确认 HarmonyOS 空工程能编译
$a2h-run         # 跑完整流水线（每阶段暂停确认，断点自动续跑）
$a2h-build       # 编译迁出来的代码
```

`$a2h-run` 的五阶段：

| # | 阶段 skill | 产出标志 |
|---|---|---|
| 1 | `a2h-spec` | `spec/baseline/ui-manifest.md` + `feature-index.md` |
| 2 | `a2h-plan` | `spec/baseline/plans/ui-plan.md` + `feature-plan.md` |
| 3 | `a2h-execute` | `spec/migration-report.md` |
| 4 | `a2h-verify` | `spec/verify-report.md` |
| 5 | `a2h-retrospect` | `docs/retrospect-report-*.md` + `.migbot/metrics/*/retrospect.done` |

**断点续跑**：`$a2h-run` 每次启动先按上表检查产出标志，从未完成的阶段接着跑。
**单阶段触发**：每个阶段也是独立 skill，可自然语言触发，如「生成 spec」「`$a2h-spec 登录页`」。单跑某阶段也会打点。

> ⚠️ `.migbot/metrics/` 下的 `retrospect.done` 等标记**必须由 `a2h mark-stage <阶段>` 真实生成**（它会剥掉 `a2h-` 前缀），禁止手写伪造。

---

## 7. 其他常用 skill

| Skill | 用途 |
|---|---|
| `$a2h-privacy status` | 查看当前同意状态与你的 `migbot_session_id` |
| `$a2h-privacy accept` / `deny` / `off` | 授予 / 撤回同意 |
| `$migbot-increment-init` | 增量迁移起步（之后用 `$migbot-increment-workflow` / `-review` / `-archive`） |
| `$a2h-build` | 编译 HarmonyOS 工程 |
| `/skills` | 在 Codex 里列出全部 skill 用选择器触发 |

**语言**：`-zh` 后缀 skill 输出中文，英文版无后缀。语言在 `$a2h-init` 选定后写入 `.migbot/config.json:language` 与 `AGENTS.md` 标记块，后续即便跑英文 skill，输出仍按所选语言渲染。

---

## 8. 隐私与打点（必读）

打点是 **Layer-1 + hooks 被动采集，全部由 `.migbot/config.json:telemetry_consent` 门控**（不走宿主 OTel）：

- **hooks 被动采集（数据本体）**：6 个 Codex 事件 → `a2h hook` → 把本次 Codex rollout 记录按字节水位切片、gzip 后 POST 到 ingest 端点（`host=codex`）。token / skill / subagent 维度的用量由**服务端**解析切片得出。
- **阶段标记**：每个流水线阶段收尾调用 `a2h mark-stage <id>`，写 stage-marks fact 与 `<stage>.done` sentinel，供服务端做阶段归因。二进制内部即时门控——`telemetry_consent != granted` 时全部 no-op。

**退出**：随时 `$a2h-privacy deny`（或 `off`），或临时 `A2H_TELEMETRY_OFF=1` 环境变量（二进制内置的 kill switch，优先级最高）。`migbot_session_id` 是你日后申请删除已上报数据的凭据，请妥善保存。

**采集边界**：客户端只打开 hook payload 里点名的 transcript 文件（`transcript_path` / `agent_transcript_path`），绝不触碰 `~/.codex/auth.json`、`*.sqlite`、`history.jsonl` 或 `shell_snapshots/`。

完整说明见 [`docs/PORTING.md`](./docs/PORTING.md) §3。

---

## 9. Windows 用户

- **不依赖 Git Bash**：安装脚本走原生 PowerShell（`.ps1` wrapper）。
- **默认执行策略**：Windows 客户端 PowerShell 默认 `ExecutionPolicy=Restricted`，直接 `.\install.ps1` 会被拒。用 `powershell -ExecutionPolicy Bypass -File .\install.ps1 -Target ...` 运行。
- **安装期同意**：`install.ps1` 在真实终端里用 `Start-Process` 弹出协议窗口并 `Read-Host` 询问，把决定写进 `.migbot\config.json`。这是首选路径——Codex 沙箱内 `Start-Process` 弹不出窗口。`-NoConsent` 或非交互 shell 会跳过、留待 `$a2h-privacy accept`。
- hooks 的 `commandWindows` 字段直接调 `.migbot\bin\a2h.exe hook`（原生 exe，不经 `.ps1`），无需 bash、无编码坑。
- **skill 在 Windows 上一律走原生 PowerShell / `a2h.exe`**：`$a2h-init` §0 给出 bash → PowerShell 的换算表（`a2h-bootstrap.ps1` / `a2h-agreement.ps1` / `a2h-tool.ps1` / `Test-Path`），`install.ps1` 还会在 `AGENTS.md` 写入 `migbot-platform: windows` 块提醒 Agent。**不要**让 Agent 在 Windows 上调 `bash`：若它解析到 WSL（`C:\Windows\system32\bash.exe`），`C:\` 路径在 WSL 里不可见，路径校验与 a2h 就位检查会全部误报（#41）。
- **WSL 兜底**：即使 bash 版 `a2h-bootstrap` / `a2h-tool` / `a2h-agreement` 被从 WSL 里调起（工程位于 `/mnt/<盘>/…`），它们也会自动转交给同名 `.ps1`（`powershell.exe`）以 Windows 视角执行。

---

## 10. 常见问题

| 报错 / 现象 | 处理 |
|---|---|
| `hvigorw not executable` | macOS/Linux：`chmod +x <harmony-root>/hvigorw` |
| `android path missing` / `harmonyos path missing` | 重跑 `$a2h-init` 修正路径 |
| `adb command not found` / `hdc command not found` | 检查 Android SDK platform-tools / HarmonyOS commandline-tools 是否在 PATH |
| `No Android/HarmonyOS device or emulator found online` | 连接设备或启动模拟器后重跑 `$a2h-build` |
| `/skills` 里看不到 hmigbot skill | 没跑过 install：到 hmigbot-CodeX 仓库执行 `./install.sh --target <工程>`（或 `install.ps1`）后**重启 Codex** |
| hooks 不生效 / 看板没数据 | 先跑 `.migbot/bin/a2h hook-trust`（install 结束和 `$a2h-init` 也会自动跑）——它会指出是项目未信任还是哪几个 hook 未信任。修法：Codex 里跑 `/hooks`（**桌面版没有该命令：设置 → 编码/开发者 → Hooks 面板**），**手动信任** migbot 遥测 hook（非托管 hook 默认**静默**不运行，`codex exec` 下连警告都没有；**面板里看得到钩子 ≠ 已触发，必须点开 Trust**）；另需 `~/.codex/config.toml` 里本项目 `trust_level = "trusted"`，否则项目层 config 整个不加载。改过 hook 命令行后要重新信任（hash 只算 hook 定义，不算二进制内容，升级 runtime 无需重信任） |
| `$a2h-run` 一直跳回 init | `.migbot/config.json` 的路径失效或 `confirmed` 不是 true，重跑 `$a2h-init` |

---

## 11. 维护

- **更新版本**：到 hmigbot-CodeX 仓库 `git pull`，再重跑 `./install.sh --target <工程>`/`install.ps1` 取最新 skills/hooks/agents/runtime（你的 `.migbot/config.json` 不动）。
- **切语言**：改 `.migbot/config.json` 的 `"language": "en" ↔ "zh"`，再重跑 `$a2h-init` 刷新 `AGENTS.md` 标记块。已生成的 spec/plan/report 不会回译。
- **本地开发**：`git clone` 本仓后，`install.sh --target <工程>` 指向你的 checkout 即可跑未发布改动。

---

## 12. 参考文档

- [`docs/PORTING.md`](./docs/PORTING.md) — 能力映射、移植规则、Windows 方案、端到端验收清单
- [`policies/user-experience-improvement-plan.zh.md`](./policies/user-experience-improvement-plan.zh.md) — 《用户体验改善计划》全文（也会在 `$a2h-init` 时弹窗展示）
- [`validate.sh`](./validate.sh) — 仓库自检（skill 命名、agent TOML、二进制齐全、无残留引用）

---

## English (brief)

Android → ArkTS/HarmonyOS migration toolkit, ported to Codex CLI (**repo-only**: clone → install → run, no plugin marketplace). **Key differences from the Claude version**: skills trigger with **`$a2h-run`** (not `/a2h-run`) — Codex has no custom slash commands; install is a **single step** (`install.sh`/`install.ps1` stages skills+hooks+agents+runtime+config+`AGENTS.md`); the instruction file is `AGENTS.md` (not `CLAUDE.md`).

Prerequisite: install **Codex CLI** itself first if you don't have it — `npm install -g @openai/codex` (or `brew install --cask codex` on macOS), then run `codex` once to log in.

Quick start: `git clone fuxi-ailabs/hmigbot-CodeX && cd hmigbot-CodeX`, then `./install.sh --target <your-harmony-app>` (or `.\install.ps1`). `cd` into the project, run `codex`, then `$a2h-init` → `$a2h-run` → `$a2h-build`. After granting consent, you're ready to run. Full details above (Chinese) and in [`docs/PORTING.md`](./docs/PORTING.md).
