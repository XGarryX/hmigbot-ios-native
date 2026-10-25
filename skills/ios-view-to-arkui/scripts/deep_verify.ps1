param(
  [Parameter(Mandatory = $true)]
  [string]$SourceRoot,

  [Parameter(Mandatory = $true)]
  [string]$ManifestPath,

  [string]$OutputPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolvedSourceRoot = (Resolve-Path -LiteralPath $SourceRoot).Path
$resolvedManifestPath = (Resolve-Path -LiteralPath $ManifestPath).Path

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
  $OutputPath = Join-Path (Split-Path -Parent $resolvedManifestPath) 'manifest-verify-report.json'
}

$manifest = Get-Content -LiteralPath $resolvedManifestPath -Raw | ConvertFrom-Json

# Collect all page names and dependency class names already in manifest
$manifestPageNames = New-Object 'System.Collections.Generic.HashSet[string]'
$manifestDepClassNames = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($page in $manifest.pages) {
  [void]$manifestPageNames.Add($page.name)
  if ($page.dependencies.classes) {
    foreach ($cls in $page.dependencies.classes) {
      [void]$manifestDepClassNames.Add($cls.name)
    }
  }
}

# --- Deep scan functions ---

function Find-ByPattern {
  param([string]$Root, [string]$Pattern, [string]$Extension)
  $results = New-Object System.Collections.Generic.List[object]
  $files = Get-ChildItem -Path $Root -Recurse -File -Filter "*$Extension"
  foreach ($file in $files) {
    $content = Get-Content -LiteralPath $file.FullName -Raw
    if ($content -match $Pattern) {
      $className = $file.BaseName
      $results.Add([ordered]@{
        name = $className
        file = $file.FullName
      })
    }
  }
  return $results
}

# --- Deep scan: Activities ---
$activityPatterns = @(
  'extends\s+\w*Activity\b',
  ':\s*\w*Activity\s*\('
)
$foundActivities = New-Object System.Collections.Generic.List[object]
foreach ($pattern in $activityPatterns) {
  $javaHits = Find-ByPattern -Root $resolvedSourceRoot -Pattern $pattern -Extension '.java'
  $ktHits = Find-ByPattern -Root $resolvedSourceRoot -Pattern $pattern -Extension '.kt'
  foreach ($hit in @($javaHits) + @($ktHits)) {
    if (-not ($foundActivities | Where-Object { $_.name -eq $hit.name })) {
      $foundActivities.Add($hit)
    }
  }
}

# --- Deep scan: Fragments ---
$fragmentPatterns = @(
  'extends\s+(Fragment|DialogFragment|BottomSheetDialogFragment|PreferenceFragmentCompat|ListFragment)\b',
  ':\s*(Fragment|DialogFragment|BottomSheetDialogFragment|PreferenceFragmentCompat)\s*\(',
  'extends\s+\w*Fragment\b',
  ':\s*\w*Fragment\s*\('
)
$foundFragments = New-Object System.Collections.Generic.List[object]
foreach ($pattern in $fragmentPatterns) {
  $javaHits = Find-ByPattern -Root $resolvedSourceRoot -Pattern $pattern -Extension '.java'
  $ktHits = Find-ByPattern -Root $resolvedSourceRoot -Pattern $pattern -Extension '.kt'
  foreach ($hit in @($javaHits) + @($ktHits)) {
    if (-not ($foundFragments | Where-Object { $_.name -eq $hit.name })) {
      $foundFragments.Add($hit)
    }
  }
}

# --- Deep scan: Dialogs ---
$dialogPatterns = @(
  'extends\s+(Dialog|AlertDialog|DialogFragment|BottomSheetDialogFragment)\b',
  'AlertDialog\.Builder',
  'MaterialAlertDialogBuilder'
)
$foundDialogs = New-Object System.Collections.Generic.List[object]
foreach ($pattern in $dialogPatterns) {
  $javaHits = Find-ByPattern -Root $resolvedSourceRoot -Pattern $pattern -Extension '.java'
  $ktHits = Find-ByPattern -Root $resolvedSourceRoot -Pattern $pattern -Extension '.kt'
  foreach ($hit in @($javaHits) + @($ktHits)) {
    if (-not ($foundDialogs | Where-Object { $_.name -eq $hit.name })) {
      # Exclude items already counted as fragments (DialogFragment is both)
      if (-not ($foundFragments | Where-Object { $_.name -eq $hit.name })) {
        $foundDialogs.Add($hit)
      }
    }
  }
}

# --- Deep scan: Adapters ---
$adapterPatterns = @(
  'extends\s+RecyclerView\.Adapter\b',
  'extends\s+(BaseAdapter|ArrayAdapter|ListAdapter|PagerAdapter|FragmentPagerAdapter|FragmentStateAdapter)\b',
  ':\s*RecyclerView\.Adapter\b',
  ':\s*(BaseAdapter|ArrayAdapter|ListAdapter|PagerAdapter|FragmentStateAdapter)\b'
)
$foundAdapters = New-Object System.Collections.Generic.List[object]
foreach ($pattern in $adapterPatterns) {
  $javaHits = Find-ByPattern -Root $resolvedSourceRoot -Pattern $pattern -Extension '.java'
  $ktHits = Find-ByPattern -Root $resolvedSourceRoot -Pattern $pattern -Extension '.kt'
  foreach ($hit in @($javaHits) + @($ktHits)) {
    if (-not ($foundAdapters | Where-Object { $_.name -eq $hit.name })) {
      $foundAdapters.Add($hit)
    }
  }
}

# --- Deep scan: Custom Views ---
$viewPatterns = @(
  'extends\s+(View|ViewGroup|FrameLayout|LinearLayout|RelativeLayout|ImageView|TextView|WebView|SurfaceView|RecyclerView(?!\s*\.))\b',
  ':\s*(View|ViewGroup|FrameLayout|LinearLayout|RelativeLayout|ImageView|TextView|WebView|SurfaceView|RecyclerView(?!\s*\.))\s*\('
)
$foundCustomViews = New-Object System.Collections.Generic.List[object]
foreach ($pattern in $viewPatterns) {
  $javaHits = Find-ByPattern -Root $resolvedSourceRoot -Pattern $pattern -Extension '.java'
  $ktHits = Find-ByPattern -Root $resolvedSourceRoot -Pattern $pattern -Extension '.kt'
  foreach ($hit in @($javaHits) + @($ktHits)) {
    if (-not ($foundCustomViews | Where-Object { $_.name -eq $hit.name })) {
      $foundCustomViews.Add($hit)
    }
  }
}

# --- Cross-check against manifest ---

$allKnownNames = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($name in $manifestPageNames) { [void]$allKnownNames.Add($name) }
foreach ($name in $manifestDepClassNames) { [void]$allKnownNames.Add($name) }

function Get-Missing {
  param([System.Collections.Generic.List[object]]$Found, [System.Collections.Generic.HashSet[string]]$Known)
  $missing = New-Object System.Collections.Generic.List[object]
  foreach ($item in $Found) {
    if (-not $Known.Contains($item.name)) {
      $missing.Add($item)
    }
  }
  return $missing
}

$missingActivities = Get-Missing -Found $foundActivities -Known $allKnownNames
$missingFragments = Get-Missing -Found $foundFragments -Known $allKnownNames
$missingDialogs = Get-Missing -Found $foundDialogs -Known $allKnownNames
$missingAdapters = Get-Missing -Found $foundAdapters -Known $allKnownNames
$missingCustomViews = Get-Missing -Found $foundCustomViews -Known $allKnownNames

# --- Collect all missing items ---

$allMissing = New-Object System.Collections.Generic.List[object]
foreach ($item in $missingActivities) {
  $allMissing.Add([ordered]@{ name = $item.name; file = $item.file; kind = 'activity' })
}
foreach ($item in $missingFragments) {
  $allMissing.Add([ordered]@{ name = $item.name; file = $item.file; kind = 'fragment' })
}
foreach ($item in $missingDialogs) {
  $allMissing.Add([ordered]@{ name = $item.name; file = $item.file; kind = 'dialog' })
}
foreach ($item in $missingAdapters) {
  $allMissing.Add([ordered]@{ name = $item.name; file = $item.file; kind = 'adapter' })
}
foreach ($item in $missingCustomViews) {
  $allMissing.Add([ordered]@{ name = $item.name; file = $item.file; kind = 'custom-view' })
}

# --- Module coverage ---

$allSourceModules = New-Object 'System.Collections.Generic.HashSet[string]'
$allFound = New-Object System.Collections.Generic.List[object]
foreach ($collection in @($foundActivities, $foundFragments, $foundDialogs, $foundAdapters, $foundCustomViews)) {
  foreach ($item in $collection) {
    $allFound.Add($item)
  }
}
foreach ($item in $allFound) {
  $relPath = $item.file.Replace($resolvedSourceRoot, '').TrimStart([char[]]@('\', '/'))
  $modulePart = $relPath -replace '[\\/]src[\\/].*$', ''
  if ($modulePart -ne $relPath) {
    [void]$allSourceModules.Add($modulePart)
  }
}

$manifestModules = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($page in $manifest.pages) {
  $relPath = $page.file.Replace($resolvedSourceRoot, '').TrimStart([char[]]@('\', '/'))
  $modulePart = $relPath -replace '[\\/]src[\\/].*$', ''
  if ($modulePart -ne $relPath) {
    [void]$manifestModules.Add($modulePart)
  }
}

$modulesCovered = @($allSourceModules | Where-Object { $manifestModules.Contains($_) } | Sort-Object)
$modulesNotCovered = @($allSourceModules | Where-Object { -not $manifestModules.Contains($_) } | Sort-Object)

# --- Determine verdict ---

$totalMissing = $allMissing.Count
$verdict = if ($totalMissing -eq 0) { 'COMPLETE' } else { 'INCOMPLETE' }

# --- Build and write report ---

$activitiesInManifest = ($manifest.pages | Where-Object { $_.kind -eq 'activity' } | Measure-Object).Count
$fragmentsInManifest = ($manifest.pages | Where-Object { $_.kind -eq 'fragment' } | Measure-Object).Count
$activitiesInProjectCount = ($foundActivities | Measure-Object).Count
$fragmentsInProjectCount = ($foundFragments | Measure-Object).Count
$dialogsInProjectCount = ($foundDialogs | Measure-Object).Count
$adaptersInProjectCount = ($foundAdapters | Measure-Object).Count
$customViewsInProjectCount = ($foundCustomViews | Measure-Object).Count
$activitiesMissingCount = ($missingActivities | Measure-Object).Count
$fragmentsMissingCount = ($missingFragments | Measure-Object).Count
$dialogsMissingCount = ($missingDialogs | Measure-Object).Count
$adaptersMissingCount = ($missingAdapters | Measure-Object).Count
$customViewsMissingCount = ($missingCustomViews | Measure-Object).Count

$missingItems = foreach ($item in $allMissing) {
  [pscustomobject]@{
    name = $item.name
    file = $item.file
    kind = $item.kind
  }
}

$coveredModules = foreach ($module in $modulesCovered) {
  $module
}

$uncoveredModules = foreach ($module in $modulesNotCovered) {
  $module
}

$summary = [pscustomobject]@{
  activitiesInProject  = $activitiesInProjectCount
  activitiesInManifest = $activitiesInManifest
  activitiesMissing    = $activitiesMissingCount
  fragmentsInProject   = $fragmentsInProjectCount
  fragmentsInManifest  = $fragmentsInManifest
  fragmentsMissing     = $fragmentsMissingCount
  dialogsInProject     = $dialogsInProjectCount
  dialogsMissing       = $dialogsMissingCount
  adaptersInProject    = $adaptersInProjectCount
  adaptersMissing      = $adaptersMissingCount
  customViewsInProject = $customViewsInProjectCount
  customViewsMissing   = $customViewsMissingCount
}

$report = [pscustomobject]@{
  generatedAt       = (Get-Date).ToString('s')
  manifestPath      = $resolvedManifestPath
  summary           = $summary
  missingItems      = @($missingItems)
  modulesCovered    = @($coveredModules)
  modulesNotCovered = @($uncoveredModules)
  verdict           = $verdict
}

$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8

Write-Host "Verification report written to $OutputPath"
Write-Host "Verdict: $verdict"
if ($totalMissing -gt 0) {
  Write-Host "$totalMissing items missing from manifest:"
  foreach ($item in $allMissing) {
    Write-Host "  [$($item.kind)] $($item.name) - $($item.file)"
  }
  exit 1
}
