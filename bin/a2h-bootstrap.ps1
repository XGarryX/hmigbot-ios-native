<#
.SYNOPSIS
  a2h-bootstrap.ps1 — first-run provisioning for the migbot plugin (Windows).
.DESCRIPTION
  PowerShell mirror of bin/a2h-bootstrap. Plugin mode has no install.ps1, so this
  script plays that role on first run (spec §3.5 #1 — the Windows native path,
  zero Git Bash dependency):
    1) Stage the bundled runtime into the project's .migbot/bin (idempotent):
         the platform-matched `a2h` binary (installed as a2h.exe),
         the PowerShell wrappers (a2h-tool.ps1 / a2h-agreement.ps1) AND the bash
         wrappers (kept so the flow still works when Codex's Bash tool is Git
         Bash). Call sites use the subcommand form: `a2h.exe mark-stage ...`.
    2) Stage the policy docs into .migbot/policies (idempotent).
    3) Create .migbot/config.json skeleton (telemetry_consent=unset) if absent.
  Consent itself is NOT handled here — it lives in $a2h-privacy. This script only
  makes the runtime present so that flow can work.
.PARAMETER Lang
  Force language (zh|en). Defaults to the system locale.
.OUTPUTS
  One JSON line on stdout:
    { "status": "created"|"exists"|"error", "path": "...",
      "provisioned": {...}, "config": {...} }
#>
param([string]$Lang = "")
$ErrorActionPreference = "Stop"
$ios152Runtime = Join-Path (Get-Location).Path '.hmigbot-ios/plugin'
if ((Test-Path (Join-Path $ios152Runtime 'scripts/ios_setup.py'))) {
  & python (Join-Path $ios152Runtime 'scripts/ios_setup.py') bootstrap
  exit $LASTEXITCODE
}


$Cfg = ".migbot/config.json"
$ScriptDir  = $PSScriptRoot
$PluginRoot = Split-Path -Parent $ScriptDir

# ── Detect arch ─────────────────────────────────────────────────────
$arch = if ($env:PROCESSOR_ARCHITECTURE -match "ARM64") { "arm64" } else { "amd64" }
$MulticallAsset = "a2h-windows-$arch.exe"

# ── JSON helper (no ConvertTo-Json whitespace / depth surprises) ────
function Json-Escape([string]$s) { return ($s -replace '\\','\\' -replace '"','\"') }

# ── Provision the bundled runtime into the project (idempotent) ─────
$provTool = "missing"; $provRuntime = "missing"; $provPolicies = "missing"

function Copy-Wrapper([string]$name) {
  $src = Join-Path $ScriptDir $name
  if (Test-Path $src) {
    Copy-Item -Force $src (Join-Path ".migbot/bin" $name) -ErrorAction SilentlyContinue
    return $true
  }
  return $false
}

# Resolve language (system locale fallback)
function Resolve-Lang {
  if ($Lang -in @("zh","en")) { return $Lang }
  $loc = "$env:LANG $env:LC_ALL $env:LC_NAME"
  if ($loc -match 'zh') { return "zh" }
  return "en"
}

# ── Detect DevEco install ──────────────────────────────────────────
function Find-DevEco {
  # 1) tools discoverable via env / common SDK roots
  $candidates = @()
  foreach ($d in @("$env:DEVECO_SDK_HOME","$env:HOS_SDK_HOME")) {
    if ($d -and (Test-Path $d)) { $candidates += $d }
  }
  # 2) Scan common Windows install roots for a DevEco* directory
  foreach ($drive in @("C:","D:","E:","F:")) {
    foreach ($parent in @(
      "$drive\Program Files\Huawei","$drive\Program Files",
      "$drive\Program Files (x86)\Huawei","$drive\Program Files (x86)",
      "$drive\codetool","$drive\dev","$drive\tools","$drive\Tools",
      "$drive\devtools","$drive\software","$drive\apps","$drive\Applications"
    )) {
      if (Test-Path $parent) {
        Get-ChildItem -Directory $parent -ErrorAction SilentlyContinue |
          Where-Object { $_.Name -match 'DevEco|deveco|DevEcoStudio' } |
          ForEach-Object { $candidates += $_.FullName }
      }
    }
  }
  foreach ($c in $candidates) { return $c }
  return ""
}

# ── Detect Android source path (sibling dir) ───────────────────────
function Find-Android {
  $here = (Get-Location).Path
  $parent = Split-Path -Parent $here
  $self = Split-Path -Leaf $here
  function Test-AndroidDir([string]$d) {
    (Test-Path (Join-Path $d "AndroidManifest.xml")) -or
    (Test-Path (Join-Path $d "app\AndroidManifest.xml")) -or
    (Test-Path (Join-Path $d "app\build.gradle")) -or
    (Test-Path (Join-Path $d "app\build.gradle.kts")) -or
    (Test-Path (Join-Path $d "settings.gradle")) -or
    (Test-Path (Join-Path $d "settings.gradle.kts"))
  }
  foreach ($c in @("android-app","android","Android","app")) {
    $d = Join-Path $parent $c
    if (($c -ne $self) -and (Test-Path $d) -and (Test-AndroidDir $d)) { return "../$c" }
  }
  Get-ChildItem -Directory $parent -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.Name -ne $self -and (Test-AndroidDir $_.FullName)) { return "../$($_.Name)" }
  } | Select-Object -First 1
  return ""
}

# ── Read + consume the install-time consent sidecar (if present) ────
# install.ps1 / install.sh collect the User Experience Improvement Plan decision
# in the user's real session (where a GUI popup CAN be raised — unlike inside
# Codex's sandbox) and drop it here as .migbot/pending-consent.json. Read it now,
# before the idempotency gate, so a stale sidecar is always consumed and a
# just-collected decision can seed (or repair) the config. Malformed → "unset".
$sidecar   = ".migbot/pending-consent.json"
$consent   = "unset"
$consentAt = "null"          # JSON literal null unless decided
$sid       = ""
$agrVer    = ""
if (Test-Path $sidecar) {
  try {
    $sc = Get-Content -Raw $sidecar -ErrorAction Stop | ConvertFrom-Json
    if ($sc.telemetry_consent -in @("granted","denied")) {
      $consent   = $sc.telemetry_consent
      if ($sc.telemetry_consent_at) { $consentAt = '"' + (Json-Escape $sc.telemetry_consent_at) + '"' }
      if ($sc.migbot_session_id)    { $sid    = "$($sc.migbot_session_id)" }
      if ($sc.agreement_version)    { $agrVer = "$($sc.agreement_version)" }
    }
  } catch { }
  Remove-Item $sidecar -ErrorAction SilentlyContinue
}

# ── Idempotency: config already exists → provisioning done, exit ────
if (Test-Path $Cfg) {
  # If the installer just handed us a decision but the existing config is still
  # undecided (a prior init aborted before consent), recreate it from the sidecar.
  # Otherwise the existing config is authoritative — leave it untouched.
  $existingTxt = Get-Content -Raw $Cfg -ErrorAction SilentlyContinue
  if (($consent -ne "unset") -and ($existingTxt -match '"telemetry_consent"\s*:\s*"unset"')) {
    Remove-Item $Cfg -ErrorAction SilentlyContinue
  } else {
    # Report the ACTUAL provisioned state, not the pre-provision defaults:
    # this early exit never runs the provision block below, and the repo
    # installer stages everything under final names (a2h.exe / a2h-tool(.ps1)
    # / policies) - so probe the files instead of echoing "missing".
    if (Test-Path (Join-Path ".migbot/bin" "a2h-tool")) { $provTool = "ok" }
    if (Test-Path (Join-Path ".migbot/bin" "a2h-tool.ps1")) { $provTool = "ok" }
    if (Test-Path (Join-Path ".migbot/bin" "a2h.exe")) { $provRuntime = "ok" }
    # Policy docs are read verbatim by $a2h-privacy and $a2h-init - both
    # languages must be present for the docs to be considered provisioned
    # (mirrors bin/a2h-bootstrap).
    if ((Test-Path ".migbot/policies/user-experience-improvement-plan.en.md") -and
        (Test-Path ".migbot/policies/user-experience-improvement-plan.zh.md")) {
      $provPolicies = "ok"
    }
    $prov = "{`"a2h_tool`":`"$provTool`",`"a2h_codex`":`"$provRuntime`",`"policies`":`"$provPolicies`"}"
    Write-Output "{`"status`":`"exists`",`"path`":`"$Cfg`",`"provisioned`":$prov}"
    exit 0
  }
}

# ── Provision runtime + policies + config skeleton ─────────────────
New-Item -ItemType Directory -Force -Path ".migbot/bin"   | Out-Null
New-Item -ItemType Directory -Force -Path ".migbot/policies" | Out-Null

# The raw-telemetry runtime, installed as `a2h.exe`; every call site
# selects a subcommand explicitly (hook / init-run / mark-stage / ...).
$srcBin = Join-Path $ScriptDir $MulticallAsset
if (Test-Path $srcBin) {
  Copy-Item -Force $srcBin (Join-Path ".migbot/bin" "a2h.exe")
  Get-Item (Join-Path ".migbot/bin" "a2h.exe") | Unblock-File -ErrorAction SilentlyContinue
  $provRuntime = "ok"
} elseif (Test-Path (Join-Path ".migbot/bin" "a2h.exe")) {
  # The repo installer stages the runtime under its final name only - the
  # arch-suffixed asset never lands in .migbot/bin. An already-present
  # binary IS the provisioned state, not "missing" (mirrors install_runtime
  # in bin/a2h-bootstrap).
  $provRuntime = "ok"
}
# Sweep what older bootstraps left behind (pre-a2h multicall runtime's per-name
# copies, plus the retired a2h-codex.exe alias of this very binary).
foreach ($stale in @("a2h-codex.exe","a2h-metrics.exe","a2h-stats.exe","a2h-keygen.exe",
                     "a2h-usage-hook.exe","a2h-usage-hook")) {
  Remove-Item (Join-Path ".migbot/bin" $stale) -ErrorAction SilentlyContinue
}
Remove-Item ".migbot/bin/a2h-windows-*.exe" -ErrorAction SilentlyContinue
# Wrappers — PowerShell (native Windows) AND bash (Git-Bash-present).
if (Copy-Wrapper "a2h-tool.ps1") { $provTool = "ok" }
foreach ($w in @("a2h-tool.ps1","a2h-agreement.ps1",
                 "a2h-tool","a2h-bootstrap","a2h-agreement")) {
  Copy-Wrapper $w | Out-Null
}
# Policy docs (both languages) — read verbatim by $a2h-privacy and $a2h-init.
$polSrc = Join-Path $PluginRoot "policies\user-experience-improvement-plan.*.md"
if (Test-Path $polSrc) {
  Copy-Item -Force $polSrc ".migbot/policies" -ErrorAction SilentlyContinue
  $provPolicies = "ok"
}

# ── Resolve paths + language ───────────────────────────────────────
$langChoice = Resolve-Lang
$androidRaw = Find-Android
if (-not $androidRaw) { $androidRaw = "../android-app" }
$devecoRaw = Find-DevEco

$android = Json-Escape $androidRaw
$deveco  = Json-Escape $devecoRaw
$sidEsc  = Json-Escape $sid
$agrEsc  = Json-Escape $agrVer

# ── Write config skeleton (telemetry unset unless the installer decided it) ──
New-Item -ItemType Directory -Force -Path ".migbot" | Out-Null
$json = @"
{
  "android": "$android",
  "harmonyos": ".",
  "hvigorw": "",
  "deveco": "$deveco",
  "adb": "",
  "hdc": "",
  "language": "$langChoice",
  "confirmed": false,
  "telemetry_consent": "$consent",
  "telemetry_consent_at": $consentAt,
  "migbot_session_id": "$sidEsc",
  "agreement_version": "$agrEsc"
}
"@
# Write WITHOUT a UTF-8 BOM: Set-Content -Encoding UTF8 (Windows PowerShell 5.1)
# adds a BOM that serde_json (the Rust binary's parser) rejects on a leading
# char. Mirror the bash version's BOM-less heredoc output.
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Join-Path (Get-Location).Path $Cfg), $json, $utf8NoBom)

# Register the pre-collected decision server-side (best-effort — the first
# $a2h-run upload reconciles it anyway; mirrors $a2h-privacy §B/§D).
$codexExe = ".migbot/bin/a2h.exe"
if (($consent -ne "unset") -and (Test-Path $codexExe)) {
  try {
    if ($sid) { & $codexExe init-run --consent $consent --migbot-session-id $sid *> $null }
    else      { & $codexExe init-run --consent $consent *> $null }
  } catch { }
}

$prov = "{`"a2h_tool`":`"$provTool`",`"a2h_codex`":`"$provRuntime`",`"policies`":`"$provPolicies`"}"
Write-Output ("{`"status`":`"created`",`"path`":`"$Cfg`",`"provisioned`":$prov," +
              "`"config`":{`"android`":`"$android`",`"harmonyos`":`".`",`"deveco`":`"$deveco`"," +
              "`"language`":`"$langChoice`",`"confirmed`":false,`"telemetry_consent`":`"$consent`"}}")
exit 0
