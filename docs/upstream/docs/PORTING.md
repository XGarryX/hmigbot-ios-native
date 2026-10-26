# PORTING.md — migbot → Codex CLI

> Codex port of migbot (the Claude variant at `C:\AI\migbot\migbot`).
> Target: Codex CLI `0.143.0` (Rust). Authored against `spec-v2.md` — all Codex
> capability claims there are source-verified against `codex-rs`.

This document is the operator-facing companion to `spec-v2.md`: what changed,
how to install, how to verify, and where the structural asymmetries live.

---

## 1. Capability mapping (Claude → Codex)

| migbot (Claude) | Codex target | What changed |
|---|---|---|
| `skills/<n>/SKILL.md` (87) | `skills/<n>/SKILL.md` → installed to `.agents/skills/` | self-reference paths rewritten (`.claude/skills/` → `.agents/skills/`); skill-to-skill calls `Skill({})` → `$<name>` explicit mention |
| `agents/<n>.md` (7) | `agents-codex/<n>.toml` → `.codex/agents/` | MD frontmatter → TOML; body → `developer_instructions`; `tools:` CSV → `sandbox_mode` |
| `commands/<n>.md` (12) | `skills/<n>/SKILL.md` + `agents/openai.yaml:default_prompt` | **command → skill** (Codex has no custom slash commands); `$<name>` / `/skills` / natural-language trigger |
| `hooks/hooks.json` (7 ev.) | `.codex/config.toml [hooks.*]` (6 ev. + `commandWindows`) | dropped `SessionEnd`; `hooks.*` written by the installer (cwd-relative), not a plugin `hooks.json`; each execs `a2h hook` directly |
| `bin/a2h-*` + multicall | `bin/a2h-*` (6 platform binaries + bash + **.ps1 wrappers**) | **the Claude multicall runtime is replaced by `a2h`** — a raw-telemetry-only client (`hook`/`init-run`/`mark-stage`/`count-lines`/`status`/`flush`). Not on PATH; calls prefixed `.migbot/bin/` |
| `.claude-plugin/{plugin,marketplace}.json` | — (repo-only: no plugin manifest) | dropped; the repo itself is the distribution |
| `CLAUDE.md` lang block | `AGENTS.md` marker block | marker + refresh logic |
| `.claude/settings.json` OTel env | — | **dropped**: migbot telemetry is a single raw channel; host OTel was never part of the data flow |
| `allowed-tools:` | — | removed; use `sandbox_mode` + `[permissions]` |

---

## 2. The one structural asymmetry: no custom slash commands

Codex's slash commands are a compile-time `EnumString` (`codex-rs/tui/src/slash_command.rs`); there is no dynamic registration and no `commands/` field in the plugin manifest. The old `~/.codex/prompts/*.md` → `/name` mechanism is removed (Skills replace it).

**Result:** the 12 migbot commands become Skills, triggered by **`$a2h-run`** (note the `$` prefix, **not** `/`), the `/skills` picker, or natural language. Functionally equivalent, prefix-asymmetric.

The command body is carried by `agents/openai.yaml: interface.default_prompt` — selecting the skill auto-attaches that prompt, which is the Codex equivalent of "running the command." Each of the 12 command→skill conversions has this file (enforced by `validate.sh`).

---

## 3. Telemetry & consent

The Codex port runs the `a2h` runtime: a **raw channel only** client. It has
no usage.v2 layer, no `metrics`/`stats` subcommands, and no client-side token
accounting. Everything is consent-gated by the binary reading
`.migbot/config.json:telemetry_consent` (and the `A2H_TELEMETRY_OFF=1` kill
switch always wins).

- **Data body — hooks (passive).** The 6 Codex lifecycle events exec
  `a2h hook`. It registers the `transcript_path` from the payload, catches
  every registered rollout file up past its byte watermark, and spawns a detached
  flush that POSTs gzip slices (`host=codex`) to the ingest endpoint.
- **Stage attribution.** Each pipeline skill closes with
  `a2h mark-stage <id>`, which writes a `stage-marks` fact and the
  `.migbot/metrics/<project>/<stage>.done` sentinel (the `a2h-` prefix is
  stripped, so `a2h-retrospect` → `retrospect.done` — the same glob `$a2h-run`
  already used).
- **Usage is derived server-side.** migbot-server's rollout parser reassembles
  the slices, parses them line-by-line into `derived_usage` /
  `derived_run_summary`, attributes stages from the facts, and the agent-perf
  dashboard admits derived-only runs (`host` column).
- **Consent handle.** `a2h init-run --consent granted --migbot-session-id <id>`
  replaces the old `gen-consent-id` + `register-consent` pair. The id is minted
  locally (`uuidgen`); the server authenticates on `X-API-Key`, which the binary
  mints internally, so the handle is only an uploaded metadata label.

**Collection boundary (red line).** The client opens ONLY the transcript files
named in hook payloads (`transcript_path` / `agent_transcript_path`). It never
touches `~/.codex/auth.json`, `*.sqlite`, `history.jsonl`, or `shell_snapshots/`.

> **No host-native OTel.** The Claude variant's `.claude/settings.json` OTel env
> block (and the Codex `[otel]` equivalent) is **not** migbot telemetry and is
> intentionally **not** wired in this port — no `[otel]` block, no
> `otel-endpoint`/`keygen` wiring, no restart-for-consent step.

---

## 4. Windows (zero Git Bash dependency)

Decision (spec §8.2 #2): Windows does **not** depend on Git Bash.

- **Hooks:** the `[hooks.*]` entries in `.codex/config.toml` carry a `commandWindows` field that runs the native `a2h.exe hook` directly (no `.ps1` launcher in the hook chain). The arch-matched `a2h.exe` is staged by the installer. It never fails the session (every path exits 0).
- **Skill-initiated helpers:** PowerShell mirrors of the bash wrappers ship in `bin/` — `a2h-bootstrap.ps1` (provisioning), `a2h-tool.ps1` (validate/build), `a2h-agreement.ps1` (out-of-band agreement popup). The installers stage them into `.migbot/bin/` alongside the bash originals (kept for environments where Codex's Bash tool is Git Bash).
- **Hook chain:** the installer writes cwd-relative `[hooks.*]` into `.codex/config.toml` with `commandWindows = ".\\.migbot\\bin\\a2h.exe hook"` (direct native exe; no `.ps1` in the chain, so there is no PowerShell encoding pitfall).

`validate.sh` asserts the three `.ps1` wrappers (`a2h-bootstrap`/`a2h-tool`/`a2h-agreement`) are present.

---

## 5. Installation

Recommended (repo-only — no plugin marketplace):

```bash
git clone fuxi-ailabs/hmigbot-CodeX
cd hmigbot-CodeX
./install.sh --target /path/to/your-harmony-app   # macOS / Linux
.\install.ps1 -Target C:\path\to\your-harmony-app  # Windows
```

The installer stages **everything**: `skills/` → `.agents/skills/`, `agents-codex/*.toml` →
`.codex/agents/`, the runtime → `.migbot/{bin,policies}` (the arch-matched
`a2h` binary plus the bash/.ps1 wrappers), `config-seed.toml` (Unix) /
`config-seed.windows.toml` (Windows) →
`.codex/config.toml` (if absent; also ensures `[features].hooks=true` and
`[features].multi_agent=true` idempotently, warns if `[agents].max_depth` < 2,
and on Windows ensures `sandbox_mode = "danger-full-access"` — issue #48),
cwd-relative `[hooks.*]` → `.codex/config.toml` (each execs `a2h hook`
directly — no wrapper in the hook chain), and the `AGENTS.md` marker (if absent).

Flags: `--target <dir>`, `--standalone` (accepted for backward compat; no effect now),
`--no-config-hooks` (never write `[hooks.*]`).

Idempotent: re-running overwrites shipped assets, never duplicates config.

---

## 6. End-to-end verification

- [ ] `codex /debug-config` — no "Configuration is invalid".
- [ ] `/skills` lists the skills (incl. the 12 command→skill conversions).
- [ ] `/hooks` shows the 6 events pending trust — approve the migbot telemetry hook. Also requires `[projects."<abs path>"] trust_level = "trusted"` in `~/.codex/config.toml`, else the project-level config (hooks included) is not loaded at all.
- [ ] `.codex/agents/*.toml` — 7 agents dispatchable via `spawn_agent` (`agent_type` = role name); `visual-fixer` can dispatch `visual-fixer-reviewer` (needs `[features] multi_agent = true` + `[agents] max_depth = 2`).
- [ ] `$a2h-init` runs the consent flow and writes `.migbot/config.json` (`telemetry_consent:"granted"`, `run_id`, `migbot_session_id`).
- [ ] `$a2h-run` drives the five stages (spec → plan → execute → verify → retrospect), auto-resuming; `retrospect.done` + per-stage `mark-stage` sentinels correct.
- [ ] Hook fires: `a2h hook` receives the Codex payload, and `a2h status --json` shows the session watermark advancing with `outbox.pending == 0`.
- [ ] Server: `raw_slices` row with `host=codex` and a `content_sha256` matching the local rollout prefix; parse worker turns it into `derived_usage`; the agent-perf dashboard lists the run.
- [ ] macOS / Linux / Windows (with the `.ps1` wrappers) — runtime executable on all three.

---

## 7. Differences from the opencode port

| Dimension | opencode | codex (this port) |
|---|---|---|
| skill discovery path | `.claude/skills/` (compat, no rewrite) | `.agents/skills/` (self-refs rewritten) |
| agent format | MD frontmatter + `tools:` map | **TOML** (`name`/`description`/`developer_instructions`/`sandbox_mode`) |
| commands | kept as `.opencode/commands/*.md` | **→ skill** (`default_prompt`) |
| hooks | **dropped** | **kept** (6 events + `commandWindows`, via installer-written `.codex/config.toml [hooks.*]`, exec'ing `a2h hook`) |
| telemetry | Layer-1 `a2h metrics` + host OTel dropped | **raw channel only** (`a2h`); usage derived server-side |
| config | `opencode.json` (Windows `shell` pin → Git Bash) | `.codex/config.toml` (no `shell`; Windows → `.ps1`) |
| instruction file | `CLAUDE.md` | `AGENTS.md` |
| run marker | legacy `summary.json` | `retrospect.done` + per-stage `mark-stage` sentinels |
