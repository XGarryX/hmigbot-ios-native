#!/usr/bin/env bash
# install.sh — install migbot (Codex port) into a project.
#
# migbot ships as a plain repo: clone it, run this installer, done. No plugin
# marketplace, no `codex plugin add` — skills/hooks/agents/runtime/config all
# come from this single script.
#
# It stages:
#   * skills/              -> .agents/skills/        (unconditional)
#   * agents-codex/*.toml  -> .codex/agents/
#   * bin/ runtime + policies -> .migbot/{bin,policies}   (a2h + wrappers)
#   * .codex-plugin/plugin.json -> .migbot/plugin.json   (版本 manifest, X-Client-Version 读取)
#   * config-seed.toml     -> .codex/config.toml     (if absent)
#   * [features].hooks=true ensured                  (idempotent, even if config exists)
#   * [hooks.*] appended to .codex/config.toml       (cwd-relative; unless --no-config-hooks)
#   * AGENTS.md marker block                          (if absent)
#
# Usage:
#   ./install.sh [--target <dir>] [--lang zh|en] [--standalone] [--no-config-hooks] [--no-consent]
#     --target            project dir (default: current directory)
#     --lang              forwarded to $a2h-init guidance only
#     --standalone        accepted for backward compat (no effect; everything is
#                         always staged now)
#     --no-config-hooks   never write [hooks.*] to config.toml
#     --no-consent        skip the install-time User Experience Improvement Plan
#                         prompt (decide later with $a2h-privacy accept). Implied
#                         when stdin/stdout is not a TTY (unattended install).
#
# Idempotent: re-running overwrites shipped assets, never duplicates config.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$(pwd)"
LANG_CHOICE=""
STANDALONE=0
NO_CONFIG_HOOKS=0
NO_CONSENT=0

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="$2"; shift 2 ;;
    --lang)   LANG_CHOICE="$2"; shift 2 ;;
    --standalone) STANDALONE=1; shift ;;
    --no-config-hooks) NO_CONFIG_HOOKS=1; shift ;;
    --no-consent) NO_CONSENT=1; shift ;;
    -h|--help) sed -n '2,33p' "$0"; exit 0 ;;
    *) echo "unknown arg / 未知参数: $1" >&2; exit 2 ;;
  esac
done

# ── UI language: --lang, else POSIX locale (zh_CN.* → zh), else 中文优先:
#    默认环境(LC_ALL/LANG 均未设置)也输出中文(MIG-317),仅显式非 zh locale
#    (如 en_US.UTF-8)保持英文。Every user-facing line below goes through t()
#    so zh/en stay side by side. ────────────────────────────────────────
UI_LANG="$LANG_CHOICE"
if [ "$UI_LANG" != zh ] && [ "$UI_LANG" != en ]; then
  case "${LC_ALL:-}${LANG:-}" in
    zh*|*zh_*|*.zh*) UI_LANG=zh ;;   # zh locale → 中文
    '')              UI_LANG=zh ;;   # 默认环境(未设 locale)→ 中文优先
    *)               UI_LANG=en ;;   # 其它显式 locale → 英文
  esac
fi

# t <key> [printf args...] — one line of user-facing text in $UI_LANG.
t() {
  local k="$1"; shift
  case "$UI_LANG:$k" in
    zh:installing)       printf '正在把 migbot(Codex 版)安装到:%s\n' "$@" ;;
    en:installing)       printf 'Installing migbot (Codex) into: %s\n' "$@" ;;
    zh:no_binary)        printf '错误:没有 %s/%s 的预编译二进制(%s)。\n' "$@" ;;
    en:no_binary)        printf 'ERROR: no prebuilt binary for %s/%s (%s).\n' "$@" ;;
    zh:shipped)          printf '随包提供的二进制:\n' ;;
    en:shipped)          printf 'Shipped binaries:\n' ;;
    zh:agents_updated)   printf '  .codex/agents 已更新(%s 个 agent)\n' "$@" ;;
    en:agents_updated)   printf '  .codex/agents updated (%s agents)\n' "$@" ;;
    zh:no_agents)        printf '  警告:没有找到 agents-codex/*.toml\n' ;;
    en:no_agents)        printf '  WARNING: no agents-codex/*.toml found\n' ;;
    zh:skills_updated)   printf '  .agents/skills 已更新\n' ;;
    en:skills_updated)   printf '  .agents/skills updated\n' ;;
    zh:staged)           printf '  .migbot/bin + .migbot/policies + plugin.json 已就位(%s)\n' "$@" ;;
    en:staged)           printf '  .migbot/bin + .migbot/policies + plugin.json staged (%s)\n' "$@" ;;
    zh:consent_flag)     printf '  --no-consent:跳过安装时的同意环节(之后可用 $a2h-privacy accept 决定)\n' ;;
    en:consent_flag)     printf '  --no-consent: skipping install-time consent (decide later with: $a2h-privacy accept)\n' ;;
    zh:consent_recorded) printf '  config.json 里已有同意记录 —— 不再询问\n' ;;
    en:consent_recorded) printf '  consent already recorded in config.json — not re-prompting\n' ;;
    zh:consent_nontty)   printf '  非交互式终端:跳过安装时的同意环节(之后可用 $a2h-privacy accept 决定)\n' ;;
    en:consent_nontty)   printf '  non-interactive shell: skipping install-time consent (decide later with: $a2h-privacy accept)\n' ;;
    zh:plan_header)      printf '── 用户体验改善计划 ─────────────────────────────────────────────\n' ;;
    en:plan_header)      printf '── User Experience Improvement Plan ─────────────────────────────────\n' ;;
    zh:plan_l1)          printf '  加入计划是使用 migbot 的前提;参与是二选一的:\n' ;;
    en:plan_l1)          printf '  Joining is a precondition for using migbot; participation is binary\n' ;;
    zh:plan_l2)          printf '  (加入 = 共享全部工作过程产物;拒绝 = migbot 停用)。\n' ;;
    en:plan_l2)          printf '  (join = all work-process artefacts shared; decline = migbot disabled).\n' ;;
    zh:plan_l3)          printf '  计划全文应该已经在窗口里打开;如果没有,手动打开:\n' ;;
    en:plan_l3)          printf "  The full plan should have opened in a window. If it didn't, open it:\n" ;;
    zh:plan_fulltext)    printf '  全文:%s\n' "$@" ;;
    en:plan_fulltext)    printf '  Full text: %s\n' "$@" ;;
    zh:plan_prompt)      printf '  加入计划并启用 migbot?[y/N] ' ;;
    en:plan_prompt)      printf '  Join the plan and enable migbot? [y/N] ' ;;
    zh:enrolled)         printf '  ✔ 已加入 —— migbot 已启用。\n' ;;
    en:enrolled)         printf '  ✔ enrolled — migbot enabled.\n' ;;
    zh:sid)              printf '    migbot_session_id:%s\n' "$@" ;;
    en:sid)              printf '    migbot_session_id: %s\n' "$@" ;;
    zh:keep_sid)         printf '    (请保存 —— 这是你申请删除数据时的凭据)\n' ;;
    en:keep_sid)         printf '    (keep this — it is your handle for data-deletion requests)\n' ;;
    zh:declined)         printf '  ✔ 已拒绝 —— migbot 保持停用。之后可用 $a2h-privacy accept 重新启用\n' ;;
    en:declined)         printf '  ✔ declined — migbot stays DISABLED. Re-enable later with: $a2h-privacy accept\n' ;;
    zh:recorded_init)    printf '  已记录,供 $a2h-init 使用(config.json 在第一次运行 Codex 时写入)。\n' ;;
    en:recorded_init)    printf '  Recorded for $a2h-init (config.json is written on the first Codex run).\n' ;;
    zh:created_seed)     printf '  已创建 .codex/config.toml(种子)\n' ;;
    en:created_seed)     printf '  created .codex/config.toml (seed)\n' ;;
    zh:warn_hooks_false) printf "  警告:config.toml 里写着 'hooks = false' —— 生命周期 hook 不会触发;请手动改成 true\n" ;;
    en:warn_hooks_false) printf "  WARNING: config.toml sets 'hooks = false' — lifecycle hooks won't fire; set it to true manually\n" ;;
    zh:inserted_hooks)   printf '  已在现有 [features] 表中插入 hooks=true\n' ;;
    en:inserted_hooks)   printf '  inserted hooks=true into existing [features] table\n' ;;
    zh:ensured_hooks)    printf '  已确保 .codex/config.toml 中 [features].hooks=true\n' ;;
    en:ensured_hooks)    printf '  ensured [features].hooks=true in .codex/config.toml\n' ;;
    zh:warn_multi_false) printf "  警告:config.toml 里写着 'multi_agent = false' —— 子代理派发(a2h-execute/a2h-verify/…)无法工作;请手动改成 true\n" ;;
    en:warn_multi_false) printf "  WARNING: config.toml sets 'multi_agent = false' — subagent dispatch (a2h-execute/a2h-verify/…) won't work; set it to true manually\n" ;;
    zh:inserted_multi)   printf '  已在现有 [features] 表中插入 multi_agent=true\n' ;;
    en:inserted_multi)   printf '  inserted multi_agent=true into existing [features] table\n' ;;
    zh:ensured_multi)    printf '  已确保 .codex/config.toml 中 [features].multi_agent=true\n' ;;
    en:ensured_multi)    printf '  ensured [features].multi_agent=true in .codex/config.toml\n' ;;
    zh:warn_max_depth)   printf "  警告:config.toml 的 '[agents] max_depth' < 2 —— arkts-visual-verify 的 reviewer 派发会失败;请改成 2\n" ;;
    en:warn_max_depth)   printf "  WARNING: config.toml sets '[agents] max_depth' < 2 — the arkts-visual-verify reviewer dispatch will fail; raise it to 2\n" ;;
    zh:appended_hooks)   printf '  已把 [hooks.*] 追加到 .codex/config.toml\n' ;;
    en:appended_hooks)   printf '  appended [hooks.*] to .codex/config.toml\n' ;;
    zh:migrated_hooks)   printf '  已把 .codex/config.toml 里的 hook 命令从 a2h-codex 迁移为 a2h\n' ;;
    en:migrated_hooks)   printf '  migrated .codex/config.toml hook commands from a2h-codex to a2h\n' ;;
    zh:trust_warn1)      printf '  !!! Codex 尚未信任 migbot 的遥测 hook —— 在你于 "%s" 打开 Codex、\n' "$@" ;;
    en:trust_warn1)      printf '  !!! migbot telemetry hooks are NOT yet trusted by Codex — nothing will be uploaded\n' ;;
    zh:trust_warn2)      printf '  !!! 运行 /hooks 并信任它们之前,不会上传任何数据。\n' ;;
    en:trust_warn2)      printf '  !!! until you open Codex in "%s", run /hooks and trust them.\n' "$@" ;;
    zh:trust_warn3)      printf '  !!! 随时可用这条命令复查:  .migbot/bin/a2h hook-trust\n' ;;
    en:trust_warn3)      printf '  !!! Re-check any time with:  .migbot/bin/a2h hook-trust\n' ;;
    zh:created_agents)   printf '  已创建 AGENTS.md(标记块)\n' ;;
    en:created_agents)   printf '  created AGENTS.md (marker block)\n' ;;
    zh:done)             printf '完成。接下来:\n' ;;
    en:done)             printf 'Done. Next steps:\n' ;;
    zh:next1)            printf '  1. cd "%s"\n' "$@" ;;
    en:next1)            printf '  1. cd "%s"\n' "$@" ;;
    zh:next2)            printf '  2. 重启 Codex(它在启动时读取 config.toml 和 skills/agents)。\n' ;;
    en:next2)            printf '  2. Restart Codex (it reads config.toml + skills/agents at startup).\n' ;;
    zh:next3)            printf '  3. 在 Codex 里运行一次 /hooks,信任 migbot 的遥测 hook\n' ;;
    en:next3)            printf '  3. In Codex run /hooks once and TRUST the migbot telemetry hook\n' ;;
    zh:next3b)           printf '     (用 .migbot/bin/a2h hook-trust 复查 —— 它报 OK 之前,不会上传任何数据)。\n' ;;
    en:next3b)           printf '     (verify with: .migbot/bin/a2h hook-trust — until it says OK, NOTHING is uploaded).\n' ;;
    zh:next4)            printf '  4. 运行:  $a2h-init%s\n' "$@" ;;
    en:next4)            printf '  4. Run:  $a2h-init%s\n' "$@" ;;
    zh:next4b)           printf '     (如果上面跳过了计划,$a2h-init 会再问一次 ——\n' ;;
    en:next4b)           printf '     (If you skipped the plan above, $a2h-init will ask once more —\n' ;;
    zh:next4c)           printf '      注意 Codex 沙箱里弹不出窗口,所以最好在安装时决定,\n' ;;
    en:next4c)           printf "      note the popup can't be raised inside Codex's sandbox, so prefer\n" ;;
    zh:next4d)           printf '      或者用 $a2h-privacy accept 决定。)\n' ;;
    en:next4d)           printf '      deciding here at install time, or via $a2h-privacy accept.)\n' ;;
    *)                   printf '%s\n' "$k" ;;
  esac
}

TARGET="$(cd "$TARGET" 2>/dev/null && pwd)" || { if [ "$UI_LANG" = zh ]; then echo "目标目录不存在" >&2; else echo "target not found" >&2; fi; exit 1; }
t installing "$TARGET"

# ── 1. Detect platform ──────────────────────────────────────────────
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
case "$OS" in
  darwin|linux) ;;
  mingw*|msys*|cygwin*) OS="windows" ;;
esac
ARCH="$(uname -m)"
case "$ARCH" in
  x86_64|amd64)  ARCH="amd64" ;;
  arm64|aarch64) ARCH="arm64" ;;
esac
EXT=""; [ "$OS" = "windows" ] && EXT=".exe"
ASSET="a2h-${OS}-${ARCH}${EXT}"

if [ ! -f "$SCRIPT_DIR/bin/$ASSET" ]; then
  t no_binary "$OS" "$ARCH" "$ASSET" >&2
  t shipped >&2; ls "$SCRIPT_DIR/bin/" | grep '^a2h-' >&2
  exit 1
fi

# ── 2. Copy subagent TOMLs -> .codex/agents/ ────────────────────────
mkdir -p "$TARGET/.codex/agents"
if ls "$SCRIPT_DIR"/agents-codex/*.toml >/dev/null 2>&1; then
  cp -f "$SCRIPT_DIR"/agents-codex/*.toml "$TARGET/.codex/agents/"
  t agents_updated "$(ls "$TARGET/.codex/agents"/*.toml | wc -l | tr -d ' ')"
else
  t no_agents >&2
fi

# ── 2b. Ship skills (unconditional — repo-only) ─────────────────────
mkdir -p "$TARGET/.agents/skills"
cp -R "$SCRIPT_DIR/skills/." "$TARGET/.agents/skills/"
t skills_updated

# ── 3. Stage the a2h runtime into .migbot/ ──────────────────────────
MB="$TARGET/.migbot"
mkdir -p "$MB/bin" "$MB/policies"
# platform-matched raw-telemetry runtime, under the runtime name `a2h`
# (same program as hmigbot's `a2h`; `a2h-codex` was only a distribution alias).
cp -f "$SCRIPT_DIR/bin/$ASSET" "$MB/bin/a2h${EXT}"
# Migration: older installs staged the same binary as `a2h-codex`. Now that
# `a2h` is provisioned, drop the stale alias so nothing execs an outdated copy.
rm -f "$MB/bin/a2h-codex" "$MB/bin/a2h-codex.exe" 2>/dev/null || true
# Sweep the pre-a2h multicall runtime's hook launcher and per-platform copies.
rm -f "$MB/bin/a2h-usage-hook" 2>/dev/null || true
rm -f "$MB"/bin/a2h-darwin-* "$MB"/bin/a2h-linux-* "$MB"/bin/a2h-windows-* 2>/dev/null || true
# bash wrappers used by $a2h-init (Unix + Git-Bash-present Windows)
for w in a2h-tool a2h-bootstrap a2h-agreement; do
  [ -f "$SCRIPT_DIR/bin/$w" ] && cp -f "$SCRIPT_DIR/bin/$w" "$MB/bin/$w"
done
# PowerShell wrappers (spec §3.5 — native Windows path, zero Git Bash dependency;
# harmless on Unix, used on Windows for direct invocation. The hook itself runs
# a2h.exe directly via config.toml commandWindows, so it needs no wrapper.)
for w in a2h-tool.ps1 a2h-bootstrap.ps1 a2h-agreement.ps1; do
  [ -f "$SCRIPT_DIR/bin/$w" ] && cp -f "$SCRIPT_DIR/bin/$w" "$MB/bin/$w"
done
chmod +x "$MB"/bin/* 2>/dev/null || true
if [ "$OS" = "darwin" ] && command -v xattr >/dev/null 2>&1; then
  xattr -dr com.apple.quarantine "$MB/bin" 2>/dev/null || true
fi
# policy docs (read verbatim by $a2h-privacy and $a2h-init)
if ls "$SCRIPT_DIR"/policies/*.md >/dev/null 2>&1; then
  cp -f "$SCRIPT_DIR"/policies/*.md "$MB/policies/" 2>/dev/null || true
fi
# 版本 manifest —— runtime 的 X-Client-Version 从这里读真实版本号（830 起每次发版
# 人为 bump .codex-plugin/plugin.json 的 version 字段，install 即带到工程目录）。
cp -f "$SCRIPT_DIR/.codex-plugin/plugin.json" "$MB/plugin.json" 2>/dev/null || true
t staged "$ASSET"

# ── 3b. User Experience Improvement Plan — consent at install time ───
# The GUI opener (a2h-agreement's `open`/`xdg-open`) works HERE because the
# installer runs in the user's real terminal — NOT inside Codex's seatbelt /
# landlock sandbox, where LaunchServices/Explorer mach-lookups are denied and
# no window can ever be raised. So we collect the decision now and hand it to
# a2h-bootstrap via a sidecar (.migbot/pending-consent.json); $a2h-init then
# sees a decided state and skips the (un-poppable) in-agent consent flow.
CONSENT_LANG="$UI_LANG"
CFG_JSON="$TARGET/.migbot/config.json"
SIDECAR="$TARGET/.migbot/pending-consent.json"

consent_decided() {
  [ -f "$CFG_JSON" ] || return 1
  grep -qE '"telemetry_consent"[[:space:]]*:[[:space:]]*"(granted|denied)"' "$CFG_JSON" 2>/dev/null
}

if [ "$NO_CONSENT" -eq 1 ]; then
  t consent_flag
elif consent_decided; then
  t consent_recorded
elif [ ! -t 0 ] || [ ! -t 1 ]; then
  t consent_nontty
else
  # Show the plan out of band: popup (Plan A) + always-printed openable path
  # (Plan B). a2h-agreement's default policy path is cwd-relative, but the
  # installer's cwd is the migbot repo, not $TARGET — pass the staged copy's
  # ABSOLUTE path so it opens the right file AND can read the Version: line.
  POLICY_ABS="$MB/policies/user-experience-improvement-plan.${CONSENT_LANG}.md"
  VERDICT="$(bash "$MB/bin/a2h-agreement" --lang "$CONSENT_LANG" --file "$POLICY_ABS" 2>/dev/null || true)"
  POL_PATH="$(printf '%s' "$VERDICT"  | sed -n 's/.*"path":"\([^"]*\)".*/\1/p')"
  AGR_VER="$(printf '%s' "$VERDICT"   | sed -n 's/.*"version":"\([^"]*\)".*/\1/p')"
  [ -z "$POL_PATH" ] && POL_PATH="$POLICY_ABS"
  # If the popup verdict didn't carry a version, probe for it quietly (no window).
  if [ -z "$AGR_VER" ]; then
    AGR_VER="$(bash "$MB/bin/a2h-agreement" --lang "$CONSENT_LANG" --file "$POLICY_ABS" --check 2>/dev/null \
                | sed -n 's/.*"version":"\([^"]*\)".*/\1/p')"
  fi

  echo ""
  t plan_header; t plan_l1; t plan_l2; t plan_l3
  echo "      open \"$POL_PATH\"        # macOS"
  echo "      xdg-open \"$POL_PATH\"    # Linux"
  t plan_fulltext "$POL_PATH"
  echo ""
  t plan_prompt
  ANS=""
  if [ -r /dev/tty ]; then IFS= read -r ANS < /dev/tty || ANS=""; else IFS= read -r ANS || ANS=""; fi

  case "$(printf '%s' "$ANS" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')" in
    y|yes|accept|agree|1) DECISION="granted" ;;
    *)                    DECISION="denied"  ;;
  esac

  SID=""
  if command -v uuidgen >/dev/null 2>&1; then
    SID="$(uuidgen | tr '[:upper:]' '[:lower:]')"
  fi
  [ -z "$SID" ] && SID="$(od -An -tx1 -N16 /dev/urandom 2>/dev/null | tr -d ' \n' | sed -E 's/(.{8})(.{4})(.{4})(.{4})(.{12})/\1-\2-\3-\4-\5/')"
  NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  mkdir -p "$TARGET/.migbot"
  cat > "$SIDECAR" <<JSON
{
  "telemetry_consent": "$DECISION",
  "telemetry_consent_at": "$NOW",
  "migbot_session_id": "$SID",
  "agreement_version": "$AGR_VER"
}
JSON
  if [ "$DECISION" = "granted" ]; then
    t enrolled; t sid "$SID"; t keep_sid
  else
    t declined
  fi
  t recorded_init
fi

# ── 4. Seed .codex/config.toml (if absent) ──────────────────────────
CODEX_CFG="$TARGET/.codex/config.toml"
if [ ! -f "$CODEX_CFG" ]; then
  cp -f "$SCRIPT_DIR/config-seed.toml" "$CODEX_CFG"
  t created_seed
fi

# ── 4a. Ensure [features].hooks=true (idempotent) ───────────────────
# Codex gates ALL lifecycle hooks behind features.hooks. config-seed carries it,
# but if the user already had a config.toml without it, hooks silently never fire.
# Match ONLY the scalar `hooks = true` boolean (the features gate). The event
# blocks below carry `hooks = [{ ... }]` (an array) — a plain `hooks =` grep
# would false-match those and skip the gate, so anchor on the `true`/`false`
# literal. And if a [features] table already exists, insert the key INTO it —
# never append a second [features] header (a duplicate table is a TOML parse
# error that makes Codex reject the whole config).
if grep -qE '^[[:space:]]*hooks[[:space:]]*=[[:space:]]*true([[:space:]]|#|$)' "$CODEX_CFG" 2>/dev/null; then
  : # features.hooks already true
elif grep -qE '^[[:space:]]*hooks[[:space:]]*=[[:space:]]*false([[:space:]]|#|$)' "$CODEX_CFG" 2>/dev/null; then
  t warn_hooks_false >&2
elif grep -qE '^[[:space:]]*\[features\][[:space:]]*$' "$CODEX_CFG" 2>/dev/null; then
  # [features] exists but lacks hooks: insert the key right under the header.
  CFG_TMP="${CODEX_CFG}.migbot.tmp"
  awk '
    /^[[:space:]]*\[features\][[:space:]]*$/ && !done { print; print "hooks = true"; done=1; next }
    { print }
  ' "$CODEX_CFG" > "$CFG_TMP" && mv "$CFG_TMP" "$CODEX_CFG"
  t inserted_hooks
else
  printf '\n# ── Lifecycle hooks gate (added by migbot install) ──\n[features]\nhooks = true\n' >> "$CODEX_CFG"
  t ensured_hooks
fi

# ── 4a′. Ensure [features].multi_agent=true (idempotent) ────────────
# The orchestration skills (a2h-execute / a2h-verify / arkts-visual-verify /
# arkts-ut-verifier) dispatch subagents via spawn_agent, which Codex gates
# behind features.multi_agent. config-seed carries it, but a pre-existing
# config.toml without it breaks every subagent dispatch. Same table-aware
# insertion as hooks above: never append a duplicate [features] header.
if grep -qE '^[[:space:]]*multi_agent[[:space:]]*=[[:space:]]*true([[:space:]]|#|$)' "$CODEX_CFG" 2>/dev/null; then
  : # features.multi_agent already true
elif grep -qE '^[[:space:]]*multi_agent[[:space:]]*=[[:space:]]*false([[:space:]]|#|$)' "$CODEX_CFG" 2>/dev/null; then
  t warn_multi_false >&2
elif grep -qE '^[[:space:]]*\[features\][[:space:]]*$' "$CODEX_CFG" 2>/dev/null; then
  CFG_TMP="${CODEX_CFG}.migbot.tmp"
  awk '
    /^[[:space:]]*\[features\][[:space:]]*$/ && !done { print; print "multi_agent = true"; done=1; next }
    { print }
  ' "$CODEX_CFG" > "$CFG_TMP" && mv "$CFG_TMP" "$CODEX_CFG"
  t inserted_multi
else
  printf '\n# ── Multi-agent gate (added by migbot install) ──\n[features]\nmulti_agent = true\n' >> "$CODEX_CFG"
  t ensured_multi
fi

# ── 4a″. Subagent-depth sanity check (warn-only) ────────────────────
# visual-fixer → visual-fixer-reviewer is a depth-2 dispatch; Codex defaults
# [agents].max_depth to 1. config-seed sets 2. We never rewrite a numeric value
# the user chose — just surface the problem.
if grep -qE '^[[:space:]]*max_depth[[:space:]]*=[[:space:]]*[01]([[:space:]]|#|$)' "$CODEX_CFG" 2>/dev/null; then
  t warn_max_depth >&2
fi

# ── 4b. Append cwd-relative [hooks.*] (repo-only: unconditional unless
#        --no-config-hooks). Both platforms exec the a2h binary
#        directly — no bash/.ps1 wrapper in the hook chain. ────────────
emit_hooks_block() {
  cat >> "$1" <<'TOML'

# ── migbot raw-telemetry hook (cwd-relative, repo-only) ──────────────
[[hooks.SessionStart]]
hooks = [{ type = "command", command = "./.migbot/bin/a2h hook", commandWindows = ".\\.migbot\\bin\\a2h.exe hook", timeout = 30 }]
[[hooks.UserPromptSubmit]]
hooks = [{ type = "command", command = "./.migbot/bin/a2h hook", commandWindows = ".\\.migbot\\bin\\a2h.exe hook", timeout = 30 }]
[[hooks.Stop]]
hooks = [{ type = "command", command = "./.migbot/bin/a2h hook", commandWindows = ".\\.migbot\\bin\\a2h.exe hook", timeout = 30 }]
[[hooks.SubagentStart]]
hooks = [{ type = "command", command = "./.migbot/bin/a2h hook", commandWindows = ".\\.migbot\\bin\\a2h.exe hook", timeout = 30 }]
[[hooks.SubagentStop]]
hooks = [{ type = "command", command = "./.migbot/bin/a2h hook", commandWindows = ".\\.migbot\\bin\\a2h.exe hook", timeout = 30 }]
[[hooks.PreCompact]]
hooks = [{ type = "command", command = "./.migbot/bin/a2h hook", commandWindows = ".\\.migbot\\bin\\a2h.exe hook", timeout = 30 }]
TOML
}

if [ "$NO_CONFIG_HOOKS" -ne 1 ]; then
  # Migration: hook entries written by older installs exec `a2h-codex hook`.
  # The binary is now provisioned as `a2h` (see step 3), so rewrite those
  # entries in place — idempotent, touches only the `a2h-codex` token.
  if grep -q 'a2h-codex' "$CODEX_CFG" 2>/dev/null; then
    CFG_TMP="${CODEX_CFG}.migbot.tmp"
    sed 's#\.migbot/bin/a2h-codex hook#.migbot/bin/a2h hook#g; s#\.migbot\\\\bin\\\\a2h-codex\.exe hook#.migbot\\\\bin\\\\a2h.exe hook#g' \
      "$CODEX_CFG" > "$CFG_TMP" && mv "$CFG_TMP" "$CODEX_CFG"
    t migrated_hooks
  fi
  if ! grep -q '\[hooks.SessionStart\]' "$CODEX_CFG" 2>/dev/null; then
    emit_hooks_block "$CODEX_CFG"
    t appended_hooks
  fi
fi

# ── 4c. Hook TRUST self-check. Codex >= 0.129 silently skips any
#        non-managed hook the user has not reviewed in /hooks (and does not
#        load the project .codex layer at all until the project is trusted).
#        A migration then runs with ZERO telemetry and no error anywhere —
#        so say it out loud here, with the exact remedy. Read-only: we never
#        write Codex's trust state ourselves (undocumented hash format,
#        openai/codex#21615). ─────────────────────────────────────────────
if [ "$NO_CONFIG_HOOKS" -ne 1 ] && [ -x "$MB/bin/a2h" ]; then
  echo ""
  if ! "$MB/bin/a2h" hook-trust --lang "$UI_LANG" --project-dir "$TARGET"; then
    echo ""
    t trust_warn1 "$TARGET"; t trust_warn2 "$TARGET"; t trust_warn3
  fi
fi

# ── 5. Drop AGENTS.md marker block (if absent) ──────────────────────
AGENTS_MD="$TARGET/AGENTS.md"
if [ ! -f "$AGENTS_MD" ]; then
  cat > "$AGENTS_MD" <<'MD'
# AGENTS.md

<!-- migbot:start -->
<!-- migbot writes the active language directive here on first run of $a2h-init.
     Do not delete this marker block. -->
<!-- migbot:end -->
MD
  t created_agents
fi

# ── 5b. Domain-agent dispatch block in AGENTS.md (always refreshed, idempotent) ──
# The arkts-* domain agents ship in agents-codex/ and land in .codex/agents/, but the
# rule telling the main session WHEN to spawn them (and how to validate their trailing
# `loaded_skills:` line) lives only in AGENTS.dispatch.md. Without this block the agents
# install fine yet are never dispatched — the failure is silent, because the .toml files
# all look correct. Same replace-or-append idiom as the migbot-platform block in
# install.ps1 §5b: strip any previous block, drop trailing blanks, append the fresh one.
if [ -f "$SCRIPT_DIR/AGENTS.dispatch.md" ]; then
  _dsp="$(mktemp)"
  awk '{ if ($0 ~ /<!-- arkts-domain-agents:begin/) skip=1
         if (!skip) print
         if ($0 ~ /<!-- arkts-domain-agents:end -->/) skip=0 }' "$AGENTS_MD" \
    | awk '{L[n++]=$0} END{while(n>0 && L[n-1]=="") n--; for(i=0;i<n;i++) print L[i]}' \
    > "$_dsp"
  { if [ -s "$_dsp" ]; then cat "$_dsp"; echo ""; fi
    cat "$SCRIPT_DIR/AGENTS.dispatch.md"; } > "$AGENTS_MD"
  rm -f "$_dsp"
  echo "  已写入 AGENTS.md 的领域 agent 派发块(arkts-domain-agents)"
fi

echo ""
t done; t next1 "$TARGET"; t next2; t next3; t next3b
t next4 "${LANG_CHOICE:+   (language: $LANG_CHOICE)}"; t next4b; t next4c; t next4d
