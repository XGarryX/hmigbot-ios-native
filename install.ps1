<#
.SYNOPSIS
  Install migbot (Codex port) into a project (Windows, repo-only).
.DESCRIPTION
  migbot ships as a plain repo: clone it, run this installer, done. No plugin
  marketplace, no `codex plugin add` — skills/hooks/agents/runtime/config all
  come from this single script.

  It stages: skills\* -> .agents\skills\, agents-codex\*.toml -> .codex\agents\,
  the a2h runtime -> .migbot\, a config.toml seed (if absent; Windows variant
  config-seed.windows.toml), ensures [features].hooks=true and a working
  sandbox_mode (idempotent; heals the old workspace-write seed on codex
  0.150.x — issue #48), appends cwd-relative [hooks.*] to .codex\config.toml
  (unless -NoConfigHooks), and an AGENTS.md marker block (if absent).
  Idempotent.
.PARAMETER Target
  Project directory to install into. Defaults to the current directory.
.PARAMETER Lang
  Forwarded to $a2h-init guidance only.
.PARAMETER Standalone
  Accepted for backward compat (no effect; everything is always staged now).
.PARAMETER NoConfigHooks
  Never write [hooks.*] to config.toml.
.PARAMETER NoConsent
  Skip the install-time User Experience Improvement Plan prompt (decide later
  with $a2h-privacy accept). Implied automatically for a non-interactive shell.
#>
param(
  [string]$Target = (Get-Location).Path,
  [string]$Lang = "",
  [switch]$Standalone,
  [switch]$NoConfigHooks,
  [switch]$NoConsent
)
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path (Join-Path $ScriptDir 'src/hmigbot_ios152')) {
  & python (Join-Path $ScriptDir 'scripts/manage_install.py') install --workspace $Target
  exit $LASTEXITCODE
}

# -- UI language: -Lang, else LANG/LC_ALL (zh* -> zh), else en. Every user-facing
#    line goes through T so zh/en stay side by side. --------------------------
$UiLang = if ($Lang -in @("zh","en")) { $Lang } elseif ("$env:LANG $env:LC_ALL" -match 'zh') { "zh" } else { "en" }
$MSG = @{
  en = @{
    installing       = 'Installing migbot (Codex) into: {0}'
    target_missing   = 'target not found: {0}'
    no_binary        = 'no prebuilt binary for windows/{0} ({1})'
    agents_updated   = '  .codex\agents updated ({0} agents)'
    no_agents        = 'no agents-codex\*.toml found'
    skills_updated   = '  .agents\skills updated'
    staged           = '  .migbot\bin + .migbot\policies staged ({0})'
    consent_flag     = '  -NoConsent: skipping install-time consent (decide later with: $a2h-privacy accept)'
    consent_recorded = '  consent already recorded in config.json - not re-prompting'
    consent_nontty   = '  non-interactive shell: skipping install-time consent (decide later with: $a2h-privacy accept)'
    plan_header      = '-- User Experience Improvement Plan ---------------------------------'
    plan_l1          = '  Joining is a precondition for using migbot; participation is binary'
    plan_l2          = '  (join = all work-process artefacts shared; decline = migbot disabled).'
    plan_l3          = "  The full plan should have opened in a window. If it didn't, open it:"
    plan_fulltext    = '  Full text: {0}'
    plan_prompt      = '  Join the plan and enable migbot? [y/N]'
    enrolled         = '  OK enrolled - migbot enabled.'
    sid              = '    migbot_session_id: {0}'
    keep_sid         = '    (keep this - it is your handle for data-deletion requests)'
    declined         = '  OK declined - migbot stays DISABLED. Re-enable later with: $a2h-privacy accept'
    recorded_init    = '  Recorded for $a2h-init (config.json is written on the first Codex run).'
    created_seed     = '  created .codex\config.toml (seed)'
    warn_hooks_false = "config.toml sets 'hooks = false' - lifecycle hooks won't fire; set it to true manually"
    inserted_hooks   = '  inserted hooks=true into existing [features] table'
    ensured_hooks    = '  ensured [features].hooks=true in .codex\config.toml'
    warn_multi_false = "config.toml sets 'multi_agent = false' - subagent dispatch (a2h-execute/a2h-verify/...) won't work; set it to true manually"
    inserted_multi   = '  inserted multi_agent=true into existing [features] table'
    ensured_multi    = '  ensured [features].multi_agent=true in .codex\config.toml'
    warn_max_depth   = "config.toml sets '[agents] max_depth' < 2 - the arkts-visual-verify reviewer dispatch will fail; raise it to 2"
    healed_sandbox   = '  healed .codex\config.toml: sandbox_mode workspace-write -> danger-full-access (Windows + codex 0.150.x requires it; issue #48)'
    ensured_sandbox  = '  ensured sandbox_mode = "danger-full-access" in .codex\config.toml (Windows + codex 0.150.x requires it)'
    warn_sandbox_ro  = "config.toml pins sandbox_mode = 'read-only' - on Windows + codex 0.150.x NO command can run (CreateProcess 1920); set it to danger-full-access manually"
    appended_hooks   = '  appended [hooks.*] to .codex\config.toml'
    migrated_hooks   = '  migrated .codex\config.toml hook commands from a2h-codex to a2h'
    trust_warn       = 'migbot telemetry hooks are NOT yet trusted by Codex - nothing will be uploaded until you open Codex in "{0}", run /hooks and trust them. Re-check any time with: .migbot\bin\a2h.exe hook-trust'
    created_agents   = '  created AGENTS.md (marker block)'
    platform_block   = '  wrote migbot-platform block to AGENTS.md (use .ps1 / a2h.exe, never bash)'
    dispatch_block   = '  wrote arkts-domain-agents dispatch block to AGENTS.md'
    done             = 'Done. Next steps:'
    next1            = '  1. cd "{0}"'
    next2            = '  2. Restart Codex (it reads config.toml + skills/agents at startup).'
    next3            = '  3. In Codex run /hooks once and TRUST the migbot telemetry hook'
    next3b           = '     (verify with: .migbot\bin\a2h.exe hook-trust - until it says OK, NOTHING is uploaded).'
    next4            = '  4. Run:  $a2h-init{0}'
    next4b           = '     (If you skipped the plan above, $a2h-init asks once more - but'
    next4c           = "      the popup can't be raised inside Codex's sandbox, so prefer"
    next4d           = '      deciding here at install time, or via $a2h-privacy accept.)'
  }
  zh = @{
    installing       = '正在把 migbot(Codex 版)安装到:{0}'
    target_missing   = '目标目录不存在:{0}'
    no_binary        = '没有 windows/{0} 的预编译二进制({1})'
    agents_updated   = '  .codex\agents 已更新({0} 个 agent)'
    no_agents        = '没有找到 agents-codex\*.toml'
    skills_updated   = '  .agents\skills 已更新'
    staged           = '  .migbot\bin + .migbot\policies 已就位({0})'
    consent_flag     = '  -NoConsent:跳过安装时的同意环节(之后可用 $a2h-privacy accept 决定)'
    consent_recorded = '  config.json 里已有同意记录 —— 不再询问'
    consent_nontty   = '  非交互式终端:跳过安装时的同意环节(之后可用 $a2h-privacy accept 决定)'
    plan_header      = '-- 用户体验改善计划 ---------------------------------------------------'
    plan_l1          = '  加入计划是使用 migbot 的前提;参与是二选一的:'
    plan_l2          = '  (加入 = 共享全部工作过程产物;拒绝 = migbot 停用)。'
    plan_l3          = '  计划全文应该已经在窗口里打开;如果没有,手动打开:'
    plan_fulltext    = '  全文:{0}'
    plan_prompt      = '  加入计划并启用 migbot?[y/N]'
    enrolled         = '  OK 已加入 —— migbot 已启用。'
    sid              = '    migbot_session_id:{0}'
    keep_sid         = '    (请保存 —— 这是你申请删除数据时的凭据)'
    declined         = '  OK 已拒绝 —— migbot 保持停用。之后可用 $a2h-privacy accept 重新启用'
    recorded_init    = '  已记录,供 $a2h-init 使用(config.json 在第一次运行 Codex 时写入)。'
    created_seed     = '  已创建 .codex\config.toml(种子)'
    warn_hooks_false = "config.toml 里写着 'hooks = false' —— 生命周期 hook 不会触发;请手动改成 true"
    inserted_hooks   = '  已在现有 [features] 表中插入 hooks=true'
    ensured_hooks    = '  已确保 .codex\config.toml 中 [features].hooks=true'
    warn_multi_false = "config.toml 里写着 'multi_agent = false' —— 子代理派发(a2h-execute/a2h-verify/...)无法工作;请手动改成 true"
    inserted_multi   = '  已在现有 [features] 表中插入 multi_agent=true'
    ensured_multi    = '  已确保 .codex\config.toml 中 [features].multi_agent=true'
    warn_max_depth   = "config.toml 的 '[agents] max_depth' < 2 —— arkts-visual-verify 的 reviewer 派发会失败;请改成 2"
    healed_sandbox   = '  已修复 .codex\config.toml:sandbox_mode 由 workspace-write 改为 danger-full-access(Windows + codex 0.150.x 必需,issue #48)'
    ensured_sandbox  = '  已确保 .codex\config.toml 中 sandbox_mode = "danger-full-access"(Windows + codex 0.150.x 必需)'
    warn_sandbox_ro  = "config.toml 里写着 sandbox_mode = 'read-only' —— Windows + codex 0.150.x 下任何命令都无法执行(CreateProcess 1920);请手动改成 danger-full-access"
    appended_hooks   = '  已把 [hooks.*] 追加到 .codex\config.toml'
    migrated_hooks   = '  已把 .codex\config.toml 里的 hook 命令从 a2h-codex 迁移为 a2h'
    trust_warn       = 'Codex 尚未信任 migbot 的遥测 hook —— 在你于 "{0}" 打开 Codex、运行 /hooks 并信任它们之前,不会上传任何数据。随时可用这条命令复查:.migbot\bin\a2h.exe hook-trust'
    created_agents   = '  已创建 AGENTS.md(标记块)'
    platform_block   = '  已在 AGENTS.md 写入 migbot-platform 块(用 .ps1 / a2h.exe,不走 bash)'
    dispatch_block   = '  已写入 AGENTS.md 的领域 agent 派发块(arkts-domain-agents)'
    done             = '完成。接下来:'
    next1            = '  1. cd "{0}"'
    next2            = '  2. 重启 Codex(它在启动时读取 config.toml 和 skills/agents)。'
    next3            = '  3. 在 Codex 里运行一次 /hooks,信任 migbot 的遥测 hook'
    next3b           = '     (用 .migbot\bin\a2h.exe hook-trust 复查 —— 它报 OK 之前,不会上传任何数据)。'
    next4            = '  4. 运行:  $a2h-init{0}'
    next4b           = '     (如果上面跳过了计划,$a2h-init 会再问一次 ——'
    next4c           = '      注意 Codex 沙箱里弹不出窗口,所以最好在安装时决定,'
    next4d           = '      或者用 $a2h-privacy accept 决定。)'
  }
}
function T([string]$Key, [object[]]$Fmt = @()) {
  # NB: the parameter must not be called $Args - that is PowerShell's automatic variable.
  $s = $MSG[$UiLang][$Key]; if ($null -eq $s) { $s = $MSG.en[$Key] }
  if ($Fmt.Count -gt 0) { $s -f $Fmt } else { $s }
}

if (-not (Test-Path $Target)) { throw (T 'target_missing' @($Target)) }
$Target = (Resolve-Path $Target).Path
Write-Host (T 'installing' @($Target))

# 1. Detect arch (Windows binaries shipped for amd64 + arm64)
$arch = if ($env:PROCESSOR_ARCHITECTURE -match "ARM64") { "arm64" } else { "amd64" }
$asset = "a2h-windows-$arch.exe"
if (-not (Test-Path (Join-Path $ScriptDir "bin\$asset"))) {
  throw (T 'no_binary' @($arch, $asset))
}

# 2. Copy subagent TOMLs -> .codex\agents\
$agentsDir = Join-Path $Target ".codex\agents"
New-Item -ItemType Directory -Force -Path $agentsDir | Out-Null
$tomls = Get-ChildItem -Path (Join-Path $ScriptDir "agents-codex\*.toml") -ErrorAction SilentlyContinue
if ($tomls) {
  Copy-Item -Force $tomls.FullName $agentsDir
  Write-Host (T 'agents_updated' @(@($tomls).Count))
} else {
  Write-Warning (T 'no_agents')
}

# 2b. Ship skills (unconditional — repo-only)
$cskills = Join-Path $Target ".agents\skills"
New-Item -ItemType Directory -Force -Path $cskills | Out-Null
Copy-Item -Recurse -Force (Join-Path $ScriptDir "skills\*") $cskills
Write-Host (T 'skills_updated')

# 3. Stage runtime -> .migbot\
$mb = Join-Path $Target ".migbot"
New-Item -ItemType Directory -Force -Path (Join-Path $mb "bin") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $mb "policies") | Out-Null
Copy-Item -Force (Join-Path $ScriptDir "bin\$asset") (Join-Path $mb "bin\a2h.exe")
# Migration: older installs staged the same binary as a2h-codex.exe. Now that
# a2h.exe is provisioned, drop the stale alias. Also sweep the pre-a2h
# multicall runtime's hook launcher.
foreach ($stale in @("a2h-codex.exe","a2h-codex","a2h-usage-hook","a2h-usage-hook.exe")) {
  Remove-Item (Join-Path $mb "bin\$stale") -ErrorAction SilentlyContinue
}
Remove-Item (Join-Path $mb "bin\a2h-windows-*.exe") -ErrorAction SilentlyContinue
foreach ($w in @("a2h-tool","a2h-bootstrap","a2h-agreement")) {
  $src = Join-Path $ScriptDir "bin\$w"
  if (Test-Path $src) { Copy-Item -Force $src (Join-Path $mb "bin\$w") }
}
# PowerShell wrappers (spec sec 3.5 — native Windows path, zero Git Bash dependency).
# The hook runs a2h.exe directly via config.toml commandWindows, so it needs no .ps1 wrapper.
foreach ($w in @("a2h-tool.ps1","a2h-bootstrap.ps1","a2h-agreement.ps1")) {
  $src = Join-Path $ScriptDir "bin\$w"
  if (Test-Path $src) { Copy-Item -Force $src (Join-Path $mb "bin\$w") }
}
# Unblock downloaded binaries (clear Zone.Identifier MOTW).
Get-ChildItem (Join-Path $mb "bin") -File | Unblock-File -ErrorAction SilentlyContinue
$pol = Join-Path $ScriptDir "policies\*.md"
if (Test-Path $pol) { Copy-Item -Force $pol (Join-Path $mb "policies") }
Write-Host (T 'staged' @($asset))

# 3b. User Experience Improvement Plan — consent at install time.
# The GUI opener (Start-Process) works HERE because the installer runs in the
# user's real session — NOT inside Codex's sandbox, where no window can be
# raised. Collect the decision now and hand it to a2h-bootstrap.ps1 via a sidecar
# (.migbot\pending-consent.json); $a2h-init then sees a decided state and skips
# its (un-poppable) in-agent consent flow.
$consentLang = $UiLang
$cfgJson  = Join-Path $Target ".migbot\config.json"
$sidecar  = Join-Path $Target ".migbot\pending-consent.json"

$alreadyDecided = $false
if (Test-Path $cfgJson) {
  $cfgTxt = Get-Content -Raw $cfgJson -ErrorAction SilentlyContinue
  if ($cfgTxt -match '"telemetry_consent"\s*:\s*"(granted|denied)"') { $alreadyDecided = $true }
}
$interactive = [Environment]::UserInteractive -and (-not [Console]::IsInputRedirected)

if ($NoConsent) {
  Write-Host (T 'consent_flag')
} elseif ($alreadyDecided) {
  Write-Host (T 'consent_recorded')
} elseif (-not $interactive) {
  Write-Host (T 'consent_nontty')
} else {
  # Show the plan out of band: popup (Plan A) + always-printed openable path.
  # Pass the staged policy's ABSOLUTE path (a2h-agreement's default is
  # cwd-relative, but the installer's cwd is the migbot repo, not $Target).
  $policyAbs = Join-Path $mb "policies\user-experience-improvement-plan.$consentLang.md"
  $agreePs1  = Join-Path $mb "bin\a2h-agreement.ps1"
  # Already inside PowerShell (past execution policy), so call the wrapper
  # directly with & — no nested powershell.exe, no -File/-File ambiguity.
  $agrVer = ""
  try {
    $verdict = & $agreePs1 -Lang $consentLang -File $policyAbs 2>$null
    if ($verdict) { $agrVer = (($verdict | ConvertFrom-Json).version) }
  } catch { }
  if (-not $agrVer) {
    try {
      $probe = & $agreePs1 -Lang $consentLang -File $policyAbs -Check 2>$null
      if ($probe) { $agrVer = (($probe | ConvertFrom-Json).version) }
    } catch { }
  }

  Write-Host ""
  Write-Host (T 'plan_header'); Write-Host (T 'plan_l1'); Write-Host (T 'plan_l2'); Write-Host (T 'plan_l3')
  Write-Host "      start `"$policyAbs`""
  Write-Host (T 'plan_fulltext' @($policyAbs))
  Write-Host ""
  $ans = Read-Host (T 'plan_prompt')
  $norm = ($ans -replace '\s','').ToLower()
  $decision = if ($norm -in @("y","yes","accept","agree","1")) { "granted" } else { "denied" }

  $sid = [guid]::NewGuid().ToString().ToLower()
  $now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  New-Item -ItemType Directory -Force -Path (Join-Path $Target ".migbot") | Out-Null
  $scJson = @"
{
  "telemetry_consent": "$decision",
  "telemetry_consent_at": "$now",
  "migbot_session_id": "$sid",
  "agreement_version": "$agrVer"
}
"@
  # BOM-less UTF-8 (serde_json rejects a leading BOM), mirroring a2h-bootstrap.ps1.
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($sidecar, $scJson, $utf8NoBom)

  if ($decision -eq "granted") {
    Write-Host (T 'enrolled'); Write-Host (T 'sid' @($sid)); Write-Host (T 'keep_sid')
  } else {
    Write-Host (T 'declined')
  }
  Write-Host (T 'recorded_init')
}

# 4. Seed .codex\config.toml (if absent)
$codexCfg = Join-Path $Target ".codex\config.toml"
if (-not (Test-Path $codexCfg)) {
  Copy-Item -Force (Join-Path $ScriptDir "config-seed.windows.toml") $codexCfg
  Write-Host (T 'created_seed')
}

# 4a. Ensure [features].hooks=true (idempotent). Codex gates all lifecycle hooks
# behind features.hooks; if the user already had a config.toml without it, hooks
# silently never fire.
# Match ONLY the scalar `hooks = true` boolean. The event blocks below carry
# `hooks = [{ ... }]` (an array); a bare `hooks =` match would false-skip the
# gate. And if a [features] table already exists, insert the key INTO it —
# never append a second [features] header (a duplicate table is a TOML parse
# error that makes Codex reject the whole config).
$cfgRaw = Get-Content -Raw $codexCfg -ErrorAction SilentlyContinue
if ($cfgRaw -match '(?m)^\s*hooks\s*=\s*true(\s|#|$)') {
  # features.hooks already true
} elseif ($cfgRaw -match '(?m)^\s*hooks\s*=\s*false(\s|#|$)') {
  Write-Warning (T 'warn_hooks_false')
} elseif ($cfgRaw -match '(?m)^\s*\[features\]\s*$') {
  # [features] exists but lacks hooks: insert the key right under the header.
  $re = [regex]'(?m)^(\s*\[features\]\s*)$'
  $patched = $re.Replace($cfgRaw, "`$1`nhooks = true", 1)
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($codexCfg, $patched, $utf8NoBom)
  Write-Host (T 'inserted_hooks')
} else {
  Add-Content -Path $codexCfg -Value "`n# -- Lifecycle hooks gate (added by migbot install) --`n[features]`nhooks = true"
  Write-Host (T 'ensured_hooks')
}

# 4a'. Ensure [features].multi_agent=true (idempotent). The orchestration skills
# (a2h-execute / a2h-verify / arkts-visual-verify / arkts-ut-verifier) dispatch
# subagents via spawn_agent, which Codex gates behind features.multi_agent.
# config-seed carries it, but a pre-existing config.toml without it breaks every
# subagent dispatch. Same table-aware insertion as hooks above: never append a
# duplicate [features] header.
$cfgRaw = Get-Content -Raw $codexCfg -ErrorAction SilentlyContinue
if ($cfgRaw -match '(?m)^\s*multi_agent\s*=\s*true(\s|#|$)') {
  # features.multi_agent already true
} elseif ($cfgRaw -match '(?m)^\s*multi_agent\s*=\s*false(\s|#|$)') {
  Write-Warning (T 'warn_multi_false')
} elseif ($cfgRaw -match '(?m)^\s*\[features\]\s*$') {
  # [features] exists but lacks multi_agent: insert the key right under the header.
  $re = [regex]'(?m)^(\s*\[features\]\s*)$'
  $patched = $re.Replace($cfgRaw, "`$1`nmulti_agent = true", 1)
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($codexCfg, $patched, $utf8NoBom)
  Write-Host (T 'inserted_multi')
} else {
  Add-Content -Path $codexCfg -Value "`n# -- Multi-agent gate (added by migbot install) --`n[features]`nmulti_agent = true"
  Write-Host (T 'ensured_multi')
}

# 4a''. Subagent-depth sanity check (warn-only). visual-fixer ->
# visual-fixer-reviewer is a depth-2 dispatch; Codex defaults [agents].max_depth
# to 1. config-seed sets 2. We never rewrite a numeric value the user chose.
$cfgRaw = Get-Content -Raw $codexCfg -ErrorAction SilentlyContinue
if ($cfgRaw -match '(?m)^\s*max_depth\s*=\s*[01](\s|#|$)') {
  Write-Warning (T 'warn_max_depth')
}

# 4a'''. Ensure sandbox_mode (idempotent; this installer is Windows-only). On
# Windows + codex 0.150.x `workspace-write` is downgraded to read-only, and
# read-only cannot spawn the default shell (Store PowerShell under WindowsApps)
# - EVERY command dies with CreateProcess 1920 / "blocked by policy" (issue #48).
#   * `workspace-write` (the old seed value we wrote) -> heal to danger-full-access;
#   * `read-only` -> warn only (a deliberate user choice we must not rewrite);
#   * absent -> inject danger-full-access at the TOP of the file (TOML top-level
#     keys must precede the first [table] header);
#   * any other value -> leave untouched.
$cfgRaw = Get-Content -Raw $codexCfg -ErrorAction SilentlyContinue
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
if ($cfgRaw -match '(?m)^\s*sandbox_mode\s*=\s*"workspace-write"(\s|#|$)') {
  $patched = $cfgRaw -replace '(?m)^(\s*)sandbox_mode\s*=\s*"workspace-write"(\s*(?:#.*)?)$', '${1}sandbox_mode = "danger-full-access"${2}'
  [System.IO.File]::WriteAllText($codexCfg, $patched, $utf8NoBom)
  Write-Host (T 'healed_sandbox')
} elseif ($cfgRaw -match '(?m)^\s*sandbox_mode\s*=\s*"read-only"(\s|#|$)') {
  Write-Warning (T 'warn_sandbox_ro')
} elseif ($cfgRaw -notmatch '(?m)^\s*sandbox_mode\s*=') {
  $patched = "# -- Windows sandbox mode (added by migbot install) --`n" +
             'sandbox_mode = "danger-full-access"' + "`n`n" + $cfgRaw
  [System.IO.File]::WriteAllText($codexCfg, $patched, $utf8NoBom)
  Write-Host (T 'ensured_sandbox')
}

# 4b. Append cwd-relative [hooks.*] (repo-only: unconditional unless -NoConfigHooks).
# Both platforms exec the a2h binary directly — no wrapper in the hook chain.
$hooksBlock = @'

# -- migbot raw-telemetry hook (cwd-relative, repo-only) --------------
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
'@

if (-not $NoConfigHooks) {
  # Migration: hook entries written by older installs exec `a2h-codex hook`.
  # The binary is now provisioned as `a2h` (see step 3), so rewrite those
  # entries in place — idempotent, touches only the `a2h-codex` token.
  $cfgRaw = Get-Content -Raw $codexCfg -ErrorAction SilentlyContinue
  if ($cfgRaw -match 'a2h-codex') {
    $patched = $cfgRaw -replace '\.migbot/bin/a2h-codex hook', '.migbot/bin/a2h hook'
    $patched = $patched -replace '\.migbot\\\\bin\\\\a2h-codex\.exe hook', '.migbot\\bin\\a2h.exe hook'
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($codexCfg, $patched, $utf8NoBom)
    Write-Host (T 'migrated_hooks')
  }
  if ((Get-Content -Raw $codexCfg -ErrorAction SilentlyContinue) -notmatch '\[hooks\.SessionStart\]') {
    Add-Content -Path $codexCfg -Value $hooksBlock
    Write-Host (T 'appended_hooks')
  }
}

# 4c. Hook TRUST self-check. Codex >= 0.129 silently skips any non-managed hook
# the user has not reviewed in /hooks (and does not load the project .codex
# layer until the project is trusted) — a migration then runs with ZERO
# telemetry and no error anywhere. Read-only check; we never write Codex's
# trust state ourselves (undocumented hash format, openai/codex#21615).
$a2hCodex = Join-Path $mb "bin\a2h.exe"
if (-not $NoConfigHooks -and (Test-Path $a2hCodex)) {
  Write-Host ""
  & $a2hCodex hook-trust --lang $UiLang --project-dir $Target
  if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Warning (T 'trust_warn' @($Target))
  }
}

# 5. Drop AGENTS.md marker block (if absent)
$agentsMd = Join-Path $Target "AGENTS.md"
if (-not (Test-Path $agentsMd)) {
  @'
# AGENTS.md

<!-- migbot:start -->
<!-- migbot writes the active language directive here on first run of $a2h-init.
     Do not delete this marker block. -->
<!-- migbot:end -->
'@ | Set-Content -Encoding UTF8 $agentsMd
  Write-Host (T 'created_agents')
}

# 5b. Platform block in AGENTS.md (always refreshed, idempotent) — tells the
# agent this project lives on Windows, so skills must use the .ps1 twins and
# a2h.exe instead of `bash` (which may resolve to WSL and misreport, #41).
$platBlock = @'
<!-- migbot-platform:start -->
migbot-platform: windows
- This project is on Windows. For every migbot command, NEVER run `bash` (it may be WSL, which cannot see `C:\` paths).
- Use `powershell -NoProfile -ExecutionPolicy Bypass -File .migbot\bin\<a2h-bootstrap|a2h-agreement|a2h-tool>.ps1 ...`,
  `.migbot\bin\a2h.exe <subcommand>`, and `Test-Path` / `Get-Command` for path and tool checks. See `$a2h-init` section 0.
<!-- migbot-platform:end -->
'@
$cur = Get-Content -Raw -Encoding UTF8 $agentsMd
$re  = '(?s)<!-- migbot-platform:start -->.*?<!-- migbot-platform:end -->'
if ($cur -match $re) { $new = [regex]::Replace($cur, $re, $platBlock.TrimEnd()) }
else { $new = $cur.TrimEnd() + "`n`n" + $platBlock }
if ($new -ne $cur) { Set-Content -LiteralPath $agentsMd -Value ($new.TrimEnd() + "`n") -Encoding UTF8 -NoNewline; Write-Host (T 'platform_block') }

# 5c. Domain-agent dispatch block in AGENTS.md (always refreshed, idempotent) — the
# arkts-* domain agents land in .codex/agents/, but the rule telling the main session
# WHEN to spawn them (and to check their trailing `loaded_skills:` line) lives only in
# AGENTS.dispatch.md. Without this block the agents install fine yet are never dispatched,
# and the failure is silent because every .toml looks correct. Mirrors install.sh 5b.
$dispatchSrc = Join-Path $ScriptDir "AGENTS.dispatch.md"
if (Test-Path $dispatchSrc) {
  $dspBlock = (Get-Content -Raw -Encoding UTF8 $dispatchSrc).TrimEnd()
  $cur2 = Get-Content -Raw -Encoding UTF8 $agentsMd
  $re2  = '(?s)<!-- arkts-domain-agents:begin.*?<!-- arkts-domain-agents:end -->'
  # MatchEvaluator (not a plain replacement string): the block is authored upstream and
  # may contain `$a2h-...` skill references, which .NET would otherwise eat as $-group
  # substitutions. A ScriptBlock evaluator passes the text through verbatim.
  if ($cur2 -match $re2) { $new2 = [regex]::Replace($cur2, $re2, { param($m) $dspBlock }) }
  else { $new2 = $cur2.TrimEnd() + "`n`n" + $dspBlock }
  if ($new2 -ne $cur2) {
    Set-Content -LiteralPath $agentsMd -Value ($new2.TrimEnd() + "`n") -Encoding UTF8 -NoNewline
    Write-Host (T 'dispatch_block')
  }
}

Write-Host ""
Write-Host (T 'done'); Write-Host (T 'next1' @($Target)); Write-Host (T 'next2'); Write-Host (T 'next3'); Write-Host (T 'next3b')
$langHint = if ($Lang) { "   (language: $Lang)" } else { "" }
Write-Host (T 'next4' @($langHint)); Write-Host (T 'next4b'); Write-Host (T 'next4c'); Write-Host (T 'next4d')
