param(
  [Parameter(Mandatory = $true)]
  [string]$TargetRoot,

  [string]$BuildCommand
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolvedTargetRoot = (Resolve-Path -LiteralPath $TargetRoot).Path

# --- Step 1: Find DevEco Studio installation ---

function Find-DevEcoHome {
  $candidates = @(
    "$env:ProgramFiles\Huawei\DevEco Studio",
    "${env:ProgramFiles(x86)}\Huawei\DevEco Studio",
    "D:\Huawei\DevEco Studio",
    "C:\Huawei\DevEco Studio"
  )
  foreach ($path in $candidates) {
    if (Test-Path -LiteralPath "$path\tools\hvigor\bin\hvigorw.bat") {
      return $path
    }
  }
  return $null
}

# --- Step 2: Ensure hvigorw.bat exists in project root ---

$hvigorWrapper = Join-Path $resolvedTargetRoot 'hvigorw.bat'
if (-not (Test-Path -LiteralPath $hvigorWrapper)) {
  Write-Host "hvigorw.bat not found in project root. Searching for DevEco Studio..."
  $devEcoHome = Find-DevEcoHome
  if (-not $devEcoHome) {
    throw "DevEco Studio not found. Install it or create hvigorw.bat manually."
  }
  Write-Host "Found DevEco Studio at: $devEcoHome"

  $wrapperContent = @"
@echo off
set NODE_HOME=$devEcoHome\tools\node
set JAVA_HOME=$devEcoHome\jbr
set PATH=%NODE_HOME%;%PATH%
set PATH=%JAVA_HOME%\bin;%PATH%
set HVIGOR_HOME=$devEcoHome\tools\hvigor\bin
set DEVECO_SDK_HOME=$devEcoHome\sdk
"%HVIGOR_HOME%\hvigorw.bat" %*
"@
  Set-Content -LiteralPath $hvigorWrapper -Value $wrapperContent -Encoding ASCII
  Write-Host "Created hvigorw.bat wrapper in project root."
}

# --- Step 3: Verify Node.js is available ---

$devEcoHome = Find-DevEcoHome
if ($devEcoHome) {
  $nodePath = Join-Path $devEcoHome 'tools\node\node.exe'
  if (-not (Test-Path -LiteralPath $nodePath)) {
    throw "Node.js not found at $nodePath. DevEco Studio installation may be incomplete."
  }
}

# --- Step 4: Smoke test hvigorw ---

Write-Host "Running hvigorw smoke test..."
Push-Location $resolvedTargetRoot
try {
  $versionOutput = & cmd /c ".\hvigorw.bat --version" 2>&1
  if ($LASTEXITCODE -ne 0) {
    $errorText = $versionOutput -join "`n"
    if ($errorText -match 'DEVECO_SDK_HOME') {
      Write-Host "SDK path issue detected. Checking SDK locations..."
      $sdkCandidates = @(
        "$env:LOCALAPPDATA\Huawei\Sdk",
        "$devEcoHome\sdk",
        "$devEcoHome\sdk\default"
      )
      $foundSdk = $null
      foreach ($sdkPath in $sdkCandidates) {
        if ((Test-Path "$sdkPath\hms") -or (Test-Path "$sdkPath\openharmony")) {
          $foundSdk = $sdkPath
          break
        }
      }
      if ($foundSdk) {
        Write-Host "Found SDK at $foundSdk. Updating hvigorw.bat wrapper..."
        $content = Get-Content -LiteralPath $hvigorWrapper -Raw
        if ($content -notmatch 'DEVECO_SDK_HOME') {
          $content = $content -replace '("%HVIGOR_HOME%)', "set DEVECO_SDK_HOME=$foundSdk`r`n`$1"
          Set-Content -LiteralPath $hvigorWrapper -Value $content -Encoding ASCII
        } else {
          $content = $content -replace 'set DEVECO_SDK_HOME=.*', "set DEVECO_SDK_HOME=$foundSdk"
          Set-Content -LiteralPath $hvigorWrapper -Value $content -Encoding ASCII
        }
        Write-Host "Updated DEVECO_SDK_HOME to $foundSdk"
      } else {
        throw "HarmonyOS SDK not found. Open DevEco Studio -> Settings -> SDK -> download the required version."
      }
    } elseif ($errorText -match 'SDK component missing') {
      throw "HarmonyOS SDK components are incomplete. Open DevEco Studio -> Settings -> SDK -> verify and repair the SDK installation."
    } else {
      throw "hvigorw smoke test failed: $errorText"
    }
  } else {
    Write-Host "hvigorw version: $versionOutput"
  }
} finally {
  Pop-Location
}

# --- Step 5: Check ohpm dependencies ---

$ohModules = Join-Path $resolvedTargetRoot 'oh_modules'
if (-not (Test-Path -LiteralPath $ohModules) -or @(Get-ChildItem -Path $ohModules -ErrorAction SilentlyContinue).Count -eq 0) {
  Write-Host "oh_modules missing or empty. Running ohpm install..."
  $ohpmCandidates = @(
    "$devEcoHome\tools\ohpm\bin\ohpm.bat",
    "$devEcoHome\tools\ohpm\bin\ohpm"
  )
  $ohpmPath = $null
  foreach ($candidate in $ohpmCandidates) {
    if (Test-Path -LiteralPath $candidate) {
      $ohpmPath = $candidate
      break
    }
  }
  if ($ohpmPath) {
    Push-Location $resolvedTargetRoot
    try {
      & $ohpmPath install
      if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: ohpm install failed. Build may fail due to missing dependencies."
      } else {
        Write-Host "ohpm install completed."
      }
    } finally {
      Pop-Location
    }
  } else {
    Write-Host "WARNING: ohpm not found. Skipping dependency install."
  }
}

# --- Step 6: Run the actual build ---

function Get-DefaultBuildCommand {
  param([string]$Root)
  $wrapper = Join-Path $Root 'hvigorw.bat'
  if (Test-Path -LiteralPath $wrapper) {
    Push-Location $Root
    try {
      $tasksOutput = & cmd /c ".\hvigorw.bat --mode project tasks" 2>&1
      if ($LASTEXITCODE -eq 0) {
        $taskText = $tasksOutput -join "`n"
        if ($taskText -match '(?m)^\s*assembleApp\b') {
          return '.\hvigorw.bat --mode project assembleApp'
        }
        if ($taskText -match '(?m)^\s*assembleHap\b') {
          return '.\hvigorw.bat --mode project assembleHap'
        }
      }
    } finally {
      Pop-Location
    }
    return '.\hvigorw.bat --mode project assembleApp'
  }
  return $null
}

if ([string]::IsNullOrWhiteSpace($BuildCommand)) {
  $BuildCommand = Get-DefaultBuildCommand -Root $resolvedTargetRoot
}

if ([string]::IsNullOrWhiteSpace($BuildCommand)) {
  throw "Could not infer a build command for $resolvedTargetRoot. Pass -BuildCommand explicitly."
}

Write-Host "Running build command in $resolvedTargetRoot"
Write-Host $BuildCommand
Push-Location $resolvedTargetRoot
try {
  Invoke-Expression $BuildCommand
} finally {
  Pop-Location
}
