#!/usr/bin/env bash
# validate.sh — static sanity checks for the migbot Codex port.
# Asserts the conversion invariants Codex hard-fails on (or the spec requires).
# Exit 0 = all good; non-zero = failures printed.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

fail=0
err() { echo "FAIL: $*"; fail=1; }

NAME_RE='^[a-z0-9]+(-[a-z0-9]+)*$'

# Pick a python that can count Unicode characters (bash wc is byte/locale-bound).
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "print(1)" >/dev/null 2>&1; then PY="$c"; break; fi
done
desc_len() {  # echo char length of the description value in $1 (SKILL.md)
  [ -n "$PY" ] || { echo 0; return; }
  "$PY" - "$1" <<'PYEOF'
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
# frontmatter is between the first two '---' lines
m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
fm = m.group(1) if m else t
d = re.search(r"^description:\s*(.*)$", fm, re.M)
if not d:
    print(0); sys.exit()
val = d.group(1).strip()
# YAML block scalar '|-' / '|' : join following indented lines
if val in ("|", "|-", ">", ">-"):
    lines = [ln for ln in fm.splitlines()
             if re.match(r"^description:", ln) or re.match(r"^  ", ln)]
    # collect indented continuation lines after the description key
    body, on = [], False
    for ln in fm.splitlines():
        if on and re.match(r"^  ", ln): body.append(ln.strip())
        elif on: break
        if re.match(r"^description:", ln): on = True
    val = "".join(body)
print(len(val))
PYEOF
}

# ── Skills ──────────────────────────────────────────────────────────
sc=0
for d in skills/*/; do
  name="$(basename "$d")"
  md="$d/SKILL.md"
  [ -f "$md" ] || { err "skill '$name' has no SKILL.md"; continue; }
  sc=$((sc+1))
  [[ "$name" =~ $NAME_RE ]] || err "skill dir '$name' violates name pattern"
  fn="$(awk -F': *' '/^name:/{print $2; exit}' "$md")"
  [ "$fn" = "$name" ] || err "skill '$name' name field is '$fn' (must equal dir)"
  awk '/^description:/{found=1} END{exit !found}' "$md" || err "skill '$name' missing description"
  dlen="$(desc_len "$md")"
  [ "$dlen" -gt 1024 ] 2>/dev/null && err "skill '$name' description is $dlen chars (>1024)"
  # Codex discovers .agents/skills/ — no residual .claude/skills/ self-references
  # in text assets (binaries/embedded strings excluded).
  if grep -rq --include='*.md' --include='*.txt' --include='*.sh' --include='*.yaml' \
        '\.claude/skills' "$d" 2>/dev/null; then
    err "skill '$name' still references .claude/skills/ in text"
  fi
  # command-isms must be gone from skill frontmatter
  grep -qE '^(allowed-tools|compatible):' "$md" && err "skill '$name' still has allowed-tools/compatible frontmatter"
done
echo "skills checked: $sc"

# ── Agents (Codex TOML) ─────────────────────────────────────────────
ac=0
for f in agents-codex/*.toml; do
  [ -f "$f" ] || continue
  ac=$((ac+1))
  n="$(basename "$f")"
  [ -n "$PY" ] && {
    "$PY" - "$f" "$n" <<'PYEOF' || true
import sys
try:
    import tomllib
except Exception:
    sys.exit(0)  # cannot validate without tomllib; skip silently
f, n = sys.argv[1], sys.argv[2]
try:
    d = tomllib.load(open(f, "rb"))
except Exception as e:
    print(f"FAIL: agent '{n}' is not valid TOML: {e}"); sys.exit()
for k in ("name", "description", "developer_instructions"):
    if not d.get(k):
        print(f"FAIL: agent '{n}' missing required field '{k}'")
for k in ("tools", "skills", "color", "model"):
    if k in d:
        print(f"FAIL: agent '{n}' still has dropped field '{k}'")
PYEOF
  }
done
echo "agents checked: $ac"

# ── Command -> skill conversions must carry a default_prompt ────────
for s in a2h-init a2h-init-zh a2h-run a2h-run-zh a2h-build a2h-build-zh \
         a2h-privacy a2h-privacy-zh \
         migbot-increment-init migbot-increment-workflow \
         migbot-increment-review migbot-increment-archive; do
  y="skills/$s/agents/openai.yaml"
  if [ ! -f "$y" ]; then
    err "command->skill '$s' missing agents/openai.yaml"
  elif ! grep -q 'default_prompt' "$y"; then
    err "command->skill '$s' openai.yaml has no default_prompt"
  fi
done

# ── No leftover underscore skill names in functional assets ─────────
if grep -rlE 'hmos_fix_build_errors|android2hmos_resources_convert' \
     --include='*.md' --include='*.json' --include='*.yaml' --include='*.toml' \
     skills agents-codex >/dev/null 2>&1; then
  err "leftover underscore skill name reference(s):"
  grep -rlE 'hmos_fix_build_errors|android2hmos_resources_convert' \
     --include='*.md' --include='*.json' --include='*.yaml' --include='*.toml' \
     skills agents-codex
fi

# ── Binaries present for all platforms ──────────────────────────────
for a in a2h-darwin-amd64 a2h-darwin-arm64 a2h-linux-amd64 \
         a2h-linux-arm64 a2h-windows-amd64.exe a2h-windows-arm64.exe; do
  [ -f "bin/$a" ] || err "missing binary bin/$a"
done

# ── The pre-a2h multicall runtime must be gone ────────────────
# a2h-usage-hook is intentionally absent: the hooks exec a2h directly.
# bin/a2h-codex-* is the retired distribution alias of the very same binary.
for a in bin/a2h-usage-hook bin/a2h-codex-darwin-amd64 bin/a2h-codex-linux-amd64 bin/a2h-codex-windows-amd64.exe; do
  [ -e "$a" ] && err "stale pre-a2h artifact: $a"
done
# No skill may call the retired `a2h metrics|stats <sub>` interface.
if grep -rqE 'a2h(\.exe)? +(metrics|stats) ' --include='*.md' --include='*.yaml' skills 2>/dev/null; then
  err "skill(s) still call the retired 'a2h metrics/stats' interface:"
  grep -rlE 'a2h(\.exe)? +(metrics|stats) ' --include='*.md' --include='*.yaml' skills
fi
# The five pipeline skills must still carry their closing stage marks. An
# upstream skill sync has silently dropped these sections before; the sentinel
# mark-stage writes is what $a2h-run probes for completion, so a missing call
# deadlocks the pipeline at retrospect and leaves the run "unfinished" server-side.
for s in spec plan execute verify retrospect; do
  md="skills/a2h-$s/SKILL.md"
  [ -f "$md" ] || continue
  grep -qF "a2h mark-stage a2h-$s" "$md" \
    || err "skills/a2h-$s/SKILL.md lost its closing 'a2h mark-stage a2h-$s' call"
done
# verify / retrospect also inventory LOC, and count-lines MUST precede
# mark-stage: completion lands server-side the moment the stage mark uploads,
# so the line counts have to be in place first.
for s in verify retrospect; do
  md="skills/a2h-$s/SKILL.md"
  [ -f "$md" ] || continue
  cl=$(grep -nF 'a2h count-lines' "$md" | head -n1 | cut -d: -f1)
  ms=$(grep -nF "a2h mark-stage a2h-$s" "$md" | head -n1 | cut -d: -f1)
  if [ -z "$cl" ]; then
    err "skills/a2h-$s/SKILL.md lost its closing 'a2h count-lines' call"
  elif [ -n "$ms" ] && [ "$cl" -gt "$ms" ]; then
    err "skills/a2h-$s/SKILL.md runs count-lines after mark-stage (count-lines must come first)"
  fi
done
# Claude-only dispatch wording must not leak back in from an upstream sync.
# The `Codex subagent dispatch convention` banner legitimately names both terms
# while telling the model to use spawn_agent/agent_type instead, so skip it.
_leak=$(grep -rnE '(subagent_type|Task tool)' --include='*.md' --include='*.yaml' skills 2>/dev/null \
          | grep -v 'Codex subagent dispatch convention')
if [ -n "$_leak" ]; then
  err "skill(s) use Claude dispatch wording — Codex spawns via spawn_agent/agent_type:"
  printf '%s\n' "$_leak" | cut -d: -f1 | sort -u
fi
# Hooks must exec a2h, not the old launcher. Match the hook *wiring*
# only — the installers legitimately name a2h-usage-hook in the sweep of files
# that older installs left behind.
if grep -qE '^hooks = \[\{.*(a2h-usage-hook|a2h\.exe usage-hook)' install.sh install.ps1 2>/dev/null; then
  err "installer still wires the retired usage-hook launcher into [hooks.*]"
fi
if ! grep -qE '^hooks = \[\{.*a2h hook' install.sh; then
  err "install.sh does not wire [hooks.*] to 'a2h hook'"
fi

# ── Windows PowerShell wrappers present (spec §3.5 / §6) ────────────
for w in a2h-bootstrap.ps1 a2h-tool.ps1 a2h-agreement.ps1; do
  [ -f "bin/$w" ] || err "missing Windows wrapper bin/$w"
done

# ── Config seed + installers present ────────────────────────────────
[ -f "config-seed.toml" ] || err "missing config-seed.toml"
# Windows variant used by install.ps1: identical except the sandbox section. On
# Windows + codex 0.150.x workspace-write is downgraded to read-only and every
# command dies (issue #48), so Windows must seed danger-full-access.
[ -f "config-seed.windows.toml" ] || err "missing config-seed.windows.toml"
# Orchestration prerequisites (issue #1): subagent dispatch + depth-2 reviewer loop
for seed in config-seed.toml config-seed.windows.toml; do
  grep -qE '^multi_agent = true' "$seed" || err "$seed missing [features] multi_agent = true"
  grep -qE '^max_threads = ' "$seed" || err "$seed missing [agents] max_threads"
  grep -qE '^max_depth = 2' "$seed" || err "$seed missing [agents] max_depth = 2"
done
# Platform sandbox split: Unix keeps workspace-write (works on codex 0.150.x
# there); Windows must be danger-full-access, and the workspace-write-only
# sub-key must not leak into the Windows variant.
grep -qE '^sandbox_mode = "workspace-write"' config-seed.toml \
  || err "config-seed.toml missing sandbox_mode = workspace-write"
grep -qE '^sandbox_mode = "danger-full-access"' config-seed.windows.toml \
  || err "config-seed.windows.toml missing sandbox_mode = danger-full-access"
grep -qE '^sandbox_workspace_write' config-seed.windows.toml \
  && err "config-seed.windows.toml must not carry sandbox_workspace_write (n/a under danger-full-access)"
[ -f "install.sh" ] || err "missing install.sh"
[ -f "install.ps1" ] || err "missing install.ps1"

echo ""
[ $fail -eq 0 ] && echo "VALIDATE: PASS" || echo "VALIDATE: FAIL"
exit $fail
