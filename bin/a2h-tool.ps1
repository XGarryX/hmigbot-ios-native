<#
.SYNOPSIS
  a2h-tool.ps1 — deterministic helper for the migbot plugin (Windows).
.DESCRIPTION
  PowerShell mirror of bin/a2h-tool (spec §3.5 #1).
  Subcommands: validate (config + emulator readiness), build.
  Reads .migbot/config.json relative to CWD. Emits JSON like the bash version:
    validate -> {"ok":true} or {"ok":false,"failures":["..."]}
    build     -> runs hvigorw assembleHap in the harmonyos dir
.PARAMETER Command
  validate | build
#>
param([Parameter(Position=0)][string]$Command = "")
$ErrorActionPreference = "Stop"
$ios152Runtime = Join-Path (Get-Location).Path '.hmigbot-ios/plugin'
if ($Command -eq "validate" -and (Test-Path (Join-Path $ios152Runtime 'scripts/ios_setup.py'))) {
  & python (Join-Path $ios152Runtime 'scripts/ios_setup.py') validate
  exit $LASTEXITCODE
}

$Cfg = ".migbot/config.json"

function Read-Field([string]$name) {
  if (-not (Test-Path $Cfg)) { return "" }
  # Single-quoted pattern (PowerShell escapes quotes with backtick, NOT '\';
  # a literal '\"' inside a double-quoted string would terminate it). Build the
  # pattern with the field name spliced in so backslashes stay literal for regex.
  $pattern = '"' + $name + '"\s*:\s*"([^"]*)"'
  $m = [regex]::Match((Get-Content -Raw $Cfg), $pattern)
  if ($m.Success) { return $m.Groups[1].Value }
  return ""
}

# ── i18n (language from .migbot/config.json:language; default en) ───
$lang = "en"
$resolved = Read-Field "language"
if ($resolved -in @("zh","en")) { $lang = $resolved }
function Msg([string]$key) {
  $en = @{
    cfg_missing        = "config.json missing"
    android_unset      = "android path unset"
    android_missing    = "android path missing"
    harmonyos_unset    = "harmonyos path unset"
    harmonyos_missing  = "harmonyos path missing"
    hvigorw_not_exec   = "hvigorw not executable"
    hvigorw_not_exec_in= "hvigorw not executable in"
    emu_android_off    = "No Android device or emulator found online. Please connect a device or start an emulator."
    emu_harmonyos_off  = "No HarmonyOS device or emulator found online. Please connect a device or start an emulator."
    emu_adb_missing    = "adb command not found. Please check your Android SDK setup."
    emu_hdc_missing    = "hdc command not found. Please check your HarmonyOS SDK (commandline-tools) setup."
    usage              = "Usage: a2h-tool <validate|build>"
  }
  $zh = @{
    cfg_missing        = "config.json 缺失"
    android_unset      = "android 路径未设置"
    android_missing    = "android 路径不存在"
    harmonyos_unset    = "harmonyos 路径未设置"
    harmonyos_missing  = "harmonyos 路径不存在"
    hvigorw_not_exec   = "hvigorw 不可执行"
    hvigorw_not_exec_in= "hvigorw 在该目录中不可执行"
    emu_android_off    = "未检测到 Android 设备或模拟器在线，请连接设备或启动模拟器。"
    emu_harmonyos_off  = "未检测到 HarmonyOS 设备或模拟器在线，请连接设备或启动模拟器。"
    emu_adb_missing    = "未找到 adb 命令，请检查 Android SDK 配置。"
    emu_hdc_missing    = "未找到 hdc 命令，请检查 HarmonyOS SDK (commandline-tools) 配置。"
    usage              = "用法：a2h-tool <validate|build>"
  }
  $tbl = if ($lang -eq "zh") { $zh } else { $en }
  return $tbl[$key]
}

function Test-Hvigorw([string]$p) {
  if (-not $p) { return $false }
  if ($p -match '\.bat$') { return (Test-Path $p) }
  return (Test-Path $p)
}

function Invoke-Validate {
  if (-not (Test-Path $Cfg)) {
    Write-Output ("{`"ok`":false,`"failures`":[`"" + (Msg cfg_missing) + "`"]}")
    exit 1
  }
  $android          = Read-Field "android"
  $harmonyos        = Read-Field "harmonyos"
  $hvigorwOverride  = Read-Field "hvigorw"

  $failures = New-Object System.Collections.Generic.List[string]
  if (-not $android) {
    $failures.Add((Msg android_unset))
  } elseif (-not (Test-Path $android)) {
    $failures.Add("$(Msg android_missing): $android")
  }
  if (-not $harmonyos) {
    $failures.Add((Msg harmonyos_unset))
  } elseif (-not (Test-Path $harmonyos)) {
    $failures.Add("$(Msg harmonyos_missing): $harmonyos")
  } elseif ($hvigorwOverride -and -not (Test-Hvigorw $hvigorwOverride)) {
    $failures.Add("$(Msg hvigorw_not_exec): $hvigorwOverride")
  } elseif (-not $hvigorwOverride -and
            -not (Test-Hvigorw "$harmonyos/hvigorw") -and
            -not (Test-Hvigorw "$harmonyos/hvigorw.bat")) {
    $failures.Add("$(Msg hvigorw_not_exec_in) $harmonyos")
  }

  # ── Emulator / tool checks (skip via A2H_SKIP_EMU_CHECK=1 for CI) ──
  if ($env:A2H_SKIP_EMU_CHECK -ne "1") {
    # adb tool
    $adbPath = Read-Field "adb"
    $adbCmd = ""
    if ($adbPath -and (Test-Path $adbPath)) { $adbCmd = $adbPath }
    elseif (Get-Command adb -ErrorAction SilentlyContinue) { $adbCmd = "adb" }
    else { $failures.Add((Msg emu_adb_missing)) }

    # Android device online?
    $androidRunning = $false
    if ($adbCmd) {
      try {
        $out = & $adbCmd devices 2>$null
        if ($out -join "`n" -match '\r?\n[^\r\n]+\tdevice\s*$') { $androidRunning = $true }
      } catch {}
    }
    if (-not $androidRunning) {
      # Windows tasklist fallback for the qemu process
      $tl = & tasklist 2>$null
      if ($tl -and ($tl -join "`n" -match 'qemu-system')) { $androidRunning = $true }
    }
    if (-not $androidRunning) { $failures.Add((Msg emu_android_off)) }

    # hdc tool
    $hdcPath = Read-Field "hdc"
    $hdcCmd = ""
    if ($hdcPath -and (Test-Path $hdcPath)) { $hdcCmd = $hdcPath }
    elseif (Get-Command hdc -ErrorAction SilentlyContinue) { $hdcCmd = "hdc" }
    else { $failures.Add((Msg emu_hdc_missing)) }

    # HarmonyOS device online?
    $harmonyRunning = $false
    if ($hdcCmd) {
      try {
        $out = (& $hdcCmd list targets 2>$null) | Where-Object {
          $_ -and $_ -notmatch '^\s*(\[Empty\]|No any target)?\s*$'
        }
        if ($out) { $harmonyRunning = $true }
      } catch {}
    }
    if (-not $harmonyRunning) {
      $tl = & tasklist 2>$null
      if ($tl -and ($tl -join "`n" -match 'Emulator.exe')) { $harmonyRunning = $true }
    }
    if (-not $harmonyRunning) { $failures.Add((Msg emu_harmonyos_off)) }
  }

  if ($failures.Count -eq 0) { Write-Output "{`"ok`":true}"; exit 0 }
  $joined = ($failures | ForEach-Object { "`"$_`"" }) -join ","
  Write-Output "{`"ok`":false,`"failures`":[$joined]}"
  exit 1
}

function Invoke-Build {
  if (-not (Test-Path $Cfg)) { Write-Error (Msg cfg_missing); exit 1 }
  $harmonyos = Read-Field "harmonyos"
  $hvigorwOverride = Read-Field "hvigorw"
  if (-not $harmonyos -or -not (Test-Path $harmonyos)) {
    Write-Error "$(Msg harmonyos_missing): $harmonyos"; exit 1
  }
  if ($hvigorwOverride) {
    $hvigorwPath = if ([System.IO.Path]::IsPathRooted($hvigorwOverride)) { $hvigorwOverride }
                   else { Join-Path (Get-Location).Path $hvigorwOverride }
  } elseif (Test-Path "$harmonyos\hvigorw") {
    $hvigorwPath = ".\hvigorw"
  } elseif (Test-Path "$harmonyos\hvigorw.bat") {
    $hvigorwPath = ".\hvigorw.bat"
  } else {
    $hvigorwPath = ".\hvigorw"
  }
  Push-Location $harmonyos
  try { & cmd /c $hvigorwPath assembleHap }
  finally { Pop-Location }
}

switch ($Command) {
  "validate" { Invoke-Validate }
  "build"    { Invoke-Build }
  default    { Write-Error (Msg usage); exit 64 }
}
