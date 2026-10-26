<!-- when: 代码规范类目探测到 harmony-docs 未配置（报告标 SKIPPED）、或用户问"怎么配 harmony-docs / 代码规范跳过了" 时读 -->
<!-- topics: harmony-docs MCP 配置, 离线鸿蒙文档, .mcp.json, query.py, HARMONY_DOCS_ROOT, 代码规范前置依赖 -->

# harmony-docs MCP 配置指南（README）

skill-checker 的**代码规范类目**（[`arkts-code-spec-check.md`](./arkts-code-spec-check.md)）靠 harmony-docs 离线文档核验 ArkTS 代码。**未配置时该类目静默跳过**（报告标 `SKIPPED`，不挡 CI）——配好后才会真正核验。本文是配置 + 检测的最小指引。

harmony-docs 同一份 `_index/` 暴露两条路径，两条都建议配（**结果完全一致**）：
- **主会话**：`harmony-docs` MCP server（9 个 `mcp__harmony-docs__*` 工具）—— 走根目录 `.mcp.json`。
- **subagent**：`harmony-docs-cli` skill（`Bash` 跑 `query.py`）—— subagent 里 MCP 工具不可用，只能走 CLI。

---

## 🤖 给 模型的执行清单（照此自动配置）

用户让你"照这个 README 配好 harmony-docs"时，**严格按序执行，任一步失败就停下报错、不要猜**：

1. **确认 `DOCS_ROOT`**（harmony-docs 仓库的下载位置）。
   - 先问用户（或读现有 `.mcp.json` 的 `args` 路径反推）。**§一「下载」是留白的——若用户尚未下载/未给路径，停下来让用户先完成下载并提供 `DOCS_ROOT`，不要编造路径或 URL。**
2. **校验 `DOCS_ROOT` 内容**：确认 `<DOCS_ROOT>/_mcp_server/server.py` 与 `<DOCS_ROOT>/_index/` 都存在（用 Bash `test -e`）。缺则报"下载不完整/路径错"，停。
3. **写根目录 `.mcp.json`**（见 §二）：路径用正斜杠 `/`；若文件已存在，**合并** `mcpServers.harmony-docs` 条目而不是整体覆盖。
4. **配 CLI 路径**（subagent 用，见 §二-3）：若 `DOCS_ROOT` ≠ 默认 `D:/Coding/Arkts/harmonyos-docs-mcp`，设环境变量 `HARMONY_DOCS_ROOT`。
5. **跑检测**（§三）：先跑 CLI 命令（立即可验，不需重启）；MCP 工具需用户**重启 Codex** 后才加载，提示用户重启再验。
6. **回报**：CLI 检测通过 = 代码规范类目对 subagent 可用；MCP 重启后 ToolSearch 命中 = 主会话可用。

---

## 一、下载（用户自行操作）

- 获取方式（仓库地址 / 安装包 / 内网链接）：
   - 本地mcp服务器（harmonyos-docs-mcp） - 下载地址：`https://gitcode.com/third-party-library-for-harmony/harmonyos-docs-mcp`
   - kit mcp知识库 - 下载地址：`https://gitcode.com/third-party-library-for-harmony/HarmonyOSDocs`
- 放置位置 `DOCS_ROOT`，例如：`D:/Coding/Arkts/harmonyos-docs-mcp`
- 下载后请按照harmonyos-docs-mcp中的README.md文档配置目录结构:
```
<DOCS_ROOT>/harmonyos_docs/
├── 指南/                  抓取的指南 md(源文件,不动)  <-- copy
├── API参考/               抓取的 API 参考 md(源文件,不动)  <-- copy
├── 最佳实践/              抓取的最佳实践 md(源文件,不动)  <-- copy
├── FAQ/                   抓取的 FAQ md(源文件,不动)  <-- copy
│
├── _tooling/              结构化索引的构建脚本(Python) <-- 丢弃，不要copy
│   ├── parsers/           ArkTS / NDK / 标准库三套解析器 
│   ├── tests/             解析器单元测试(21 个)
│   └── build_index.py     统一构建入口,生成 _index/ 下所有产物
│
├── _index/                构建产物(详见下表) <-- 丢弃，不要copy
│
└── _mcp_server/           MCP server,把索引暴露成 8 个工具给 Agent <-- 丢弃，不要copy
    ├── server.py
    ├── tools/             一个工具一个文件
    ├── tests/             工具单测 + 集成 smoke(28 个)
    └── README.md          MCP 详细文档(工具 schema、Agent 调用示例)
```

- 下载后必跑一次索引构建（首次约 10 秒）：
```
cd <DOCS_ROOT>/harmonyos_docs/
python _tooling/build_index.py
```
- 显示如下内容即索引构建完成：
```
$ python _tooling/build_index.py
[build] repo root: <安装路径>\harmonyos-docs-mcp
[build] api_index.jsonl: 28216 symbols
[build] syscap_index.jsonl: 360 syscaps
[build] module_index.json: 175 modules
[build] data snapshot (latest fetched_at): 2026-05-24
[build] faq_qa.jsonl: 1559 Q→A pairs
[build] external_link_map.json: 11827 URL mappings
[build] toc.md: 13743 lines
[build] done in 316.52s  → <安装路径>\harmonyos-docs-mcp\_index
```
---

## 二、配置（LLM操作）

### 1. 主会话 — 根目录 `.mcp.json`

在**本仓根目录**（`ArkTs-Core/`）的 `.mcp.json` 写入（已存在则合并 `harmony-docs` 这一条）：

```json
{
  "mcpServers": {
    "harmony-docs": {
      "command": "python",
      "args": ["<DOCS_ROOT>/_mcp_server/server.py"]
    }
  }
}
```

- 路径用正斜杠 `/`（Windows 也是）。例：`D:/Coding/Arkts/harmonyos-docs-mcp/_mcp_server/server.py`。
- macOS / Linux 把 `"command": "python"` 换成 `"python3"`。
- MCP server 从 `args` 给的绝对路径自行定位 `_index`，**无需额外环境变量**。

### 2. 让 MCP 生效

MCP server 在 Codex **启动时加载**——改完 `.mcp.json` 后**重启 Codex**（或重开会话）才会出现 `mcp__harmony-docs__*` 工具。

### 3. subagent — `harmony-docs-cli` skill（CLI 路径）

CLI 脚本已随仓库就位：`.agents/skills/harmony-docs-cli/scripts/query.py`。它按以下顺序定位仓库：

| 来源 | 默认 | 何时要设 |
|---|---|---|
| 环境变量 `HARMONY_DOCS_ROOT` | `D:/Coding/Arkts/harmonyos-docs-mcp` | `DOCS_ROOT` 与默认不同时**必设** |
| 环境变量 `HARMONY_DOCS_INDEX_DIR` | `<ROOT>/_index` | `_index` 不在仓库内时才设 |

设环境变量（`DOCS_ROOT` ≠ 默认时）：

```powershell
# PowerShell（当前会话；永久则用 [Environment]::SetEnvironmentVariable）
$env:HARMONY_DOCS_ROOT = "<DOCS_ROOT>"
```
```bash
# bash / zsh
export HARMONY_DOCS_ROOT="<DOCS_ROOT>"
```

> 前置：`python` 在 PATH 上。`query.py` 已强制 UTF-8 输出，Windows 控制台不会中文乱码。

---

## 三、检测

### A. CLI（立即可验，不需重启）

```bash
python .agents/skills/harmony-docs-cli/scripts/query.py lookup display.isFoldable
```

✅ **配好**：输出 JSON，含 `"data_snapshot"` 和 `result`（`display.isFoldable` 的 signature / syscap / since）：

```json
{ "data_snapshot": "2026-05-24", "result": [ { "symbol": "display.isFoldable", "since": "10", ... } ] }
```

❌ **没配好**：输出 `{"error": ...}`，按提示修：

| error 片段 | 原因 | 修法 |
|---|---|---|
| `harmony-docs repo not found at ...; set HARMONY_DOCS_ROOT` | `DOCS_ROOT` 错 / 未下载 | 校验 §一 路径，设 `HARMONY_DOCS_ROOT`（§二-3） |
| `_index not found at ...; run build_index.py first` | 仓库在但缺索引 | 到 `DOCS_ROOT` 跑 `build_index.py` 生成 `_index/` |

### B. 主会话 MCP（重启 Codex 后）

让 模型执行：`ToolSearch "harmony-docs"` 应命中 9 个 `mcp__harmony-docs__*`；再调一次 `mcp__harmony-docs__lookup_symbol`（name=`display.isFoldable`）应返回带 `since`/`syscap` 的结果。命不中 = `.mcp.json` 未生效（确认已重启 + 路径正确）。

### C. 回到 skill-checker

- 两条任一可用 → 代码规范类目正常核验（报告不再标 `SKIPPED`）。
- 都不可用 → 类目**静默跳过**（标 `SKIPPED：harmony-docs 未配置`，不报错、不计入硬门）——这是设计行为，不是 bug。
