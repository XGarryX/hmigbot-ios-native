<#
.SYNOPSIS
  a2h-agreement.ps1 — present the User Experience Improvement Plan out-of-band (Windows).
.DESCRIPTION
  PowerShell mirror of bin/a2h-agreement. The agreement's full text never enters
  the agent's context window:
    Plan A (preferred): Start-Process raises the default .md handler in its own
                         window without blocking this shell.
    Plan B (fallback):  print the absolute, openable path; the agent asks the
                         user to open and read it manually.
  The absolute path is ALWAYS printed. The final stdout line is compact JSON:
    {"shown":"popup"|"path"|"error","method":"...","path":"<abs>","lang":"..","version":"vX.Y","reason":".."}
.PARAMETER Lang
  zh | en (selects the policy file). Defaults to en.
.PARAMETER File
  Override the policy file path.
.PARAMETER Check
  Quiet probe: emit the current agreement version + path WITHOUT raising a window.
#>
param(
  [string]$Lang = "",
  [string]$File = "",
  [switch]$Check
)
$ErrorActionPreference = "Stop"

if (-not $Lang) { $Lang = "en" }
if (-not $File) { $File = ".migbot/policies/user-experience-improvement-plan.$Lang.md" }

function Json-Escape([string]$s) { return ($s -replace '\\','\\' -replace '"','\"') }

if (-not (Test-Path $File)) {
  Write-Output ("{`"shown`":`"error`",`"method`":`"none`",`"path`":`"" + (Json-Escape $File) +
                "`",`"lang`":`"" + (Json-Escape $Lang) + "`",`"reason`":`"policy file not found`"}")
  exit 0
}

$abs = (Resolve-Path $File).Path

# Pull the agreement version (bottom "Version: vX.Y" / "版本号：vX.Y") so the
# agent can record agreement_version without reading the policy body.
$version = ""
foreach ($line in (Get-Content $File -ErrorAction SilentlyContinue)) {
  if ($line -match '(?i)^\s*(version|版本号)') {
    if ($line -match 'v[0-9]+(\.[0-9]+){1,2}') { $version = $matches[0] }
  }
}

if ($Check) {
  Write-Output ("{`"shown`":`"check`",`"method`":`"none`",`"path`":`"" + (Json-Escape $abs) +
                "`",`"lang`":`"" + (Json-Escape $Lang) + "`",`"version`":`"" + (Json-Escape $version) +
                "`",`"reason`":`"version probe`"}")
  exit 0
}

$method = "none"
$shown  = "path"
$reason = ""

# Plan A: raise the default .md handler in its own window.
try {
  Start-Process -FilePath $abs -ErrorAction Stop
  $method = "Start-Process"; $shown = "popup"
} catch {
  $reason = "Start-Process failed: $($_.Exception.Message)"
}

if (-not $reason) { $reason = "opened in a GUI window via $method" }

Write-Output ("{`"shown`":`"$shown`",`"method`":`"$method`",`"path`":`"" + (Json-Escape $abs) +
              "`",`"lang`":`"" + (Json-Escape $Lang) + "`",`"version`":`"" + (Json-Escape $version) +
              "`",`"reason`":`"" + (Json-Escape $reason) + "`"}")
exit 0
