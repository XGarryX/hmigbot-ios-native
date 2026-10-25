param(
  [Parameter(Mandatory = $true)]
  [string]$SourceRoot,

  [string]$OutputPath = ".codex/ui-migration/manifest.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Convert-CamelToSnake {
  param([string]$Value)

  if ([string]::IsNullOrWhiteSpace($Value)) {
    return $Value
  }

  $value = [regex]::Replace($Value, '([a-z0-9])([A-Z])', '$1_$2')
  $value = [regex]::Replace($value, '([A-Z]+)([A-Z][a-z])', '$1_$2')
  return $value.ToLowerInvariant()
}

function Get-ClassKind {
  param(
    [string]$Content,
    [string]$FileName
  )

  if ($Content -match 'extends\s+[A-Za-z0-9_]*Activity\b' -or $Content -match ':\s*[A-Za-z0-9_]*Activity\b' -or $FileName -match 'Activity\.(java|kt)$') {
    return 'activity'
  }
  if ($Content -match 'extends\s+[A-Za-z0-9_]*Fragment\b' -or $Content -match ':\s*[A-Za-z0-9_]*Fragment\b' -or $FileName -match 'Fragment\.(java|kt)$') {
    return 'fragment'
  }
  if ($Content -match 'DialogFragment\b' -or $FileName -match 'Dialog\.(java|kt)$') {
    return 'dialog'
  }
  if ($FileName -match 'Adapter\.(java|kt)$') {
    return 'adapter'
  }
  if ($FileName -match 'ViewHolder\.(java|kt)$') {
    return 'viewholder'
  }
  if ($FileName -match 'Section\.(java|kt)$') {
    return 'section'
  }
  if ($Content -match 'extends\s+[A-Za-z0-9_]*View\b' -or $Content -match ':\s*[A-Za-z0-9_]*View\b' -or $FileName -match 'View\.(java|kt)$') {
    return 'custom-view'
  }
  return 'other'
}

function Get-UniqueMatches {
  param(
    [string]$Content,
    [string]$Pattern,
    [int]$Group = 1
  )

  $values = New-Object 'System.Collections.Generic.HashSet[string]'
  foreach ($match in [regex]::Matches($Content, $Pattern)) {
    $value = $match.Groups[$Group].Value
    if (-not [string]::IsNullOrWhiteSpace($value)) {
      [void]$values.Add($value)
    }
  }
  return @($values | Sort-Object)
}

function Resolve-FullPath {
  param([string]$Path)

  if ([System.IO.Path]::IsPathRooted($Path)) {
    return [System.IO.Path]::GetFullPath($Path)
  }

  return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
}

$resolvedSourceRoot = (Resolve-Path -LiteralPath $SourceRoot).Path
$resolvedOutputPath = Resolve-FullPath -Path $OutputPath
$outputDirectory = Split-Path -Parent $resolvedOutputPath
if (-not (Test-Path -LiteralPath $outputDirectory)) {
  New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
}

$sourceFiles = Get-ChildItem -Path $resolvedSourceRoot -Recurse -File | Where-Object {
  $_.Extension -in @('.java', '.kt')
}
$layoutFiles = Get-ChildItem -Path $resolvedSourceRoot -Recurse -File | Where-Object {
  $_.Extension -eq '.xml' -and $_.FullName -match '[\\/](layout[^\\/]*?)[\\/]'
}
$menuFiles = Get-ChildItem -Path $resolvedSourceRoot -Recurse -File | Where-Object {
  $_.Extension -eq '.xml' -and $_.FullName -match '[\\/]menu[\\/]'
}

$layoutIndex = @{}
foreach ($layoutFile in $layoutFiles) {
  $layoutIndex[$layoutFile.BaseName] = $layoutFile.FullName
}

$menuIndex = @{}
foreach ($menuFile in $menuFiles) {
  $menuIndex[$menuFile.BaseName] = $menuFile.FullName
}

$classIndex = @{}
$contentIndex = @{}
foreach ($sourceFile in $sourceFiles) {
  $content = Get-Content -LiteralPath $sourceFile.FullName -Raw
  $contentIndex[$sourceFile.BaseName] = $content
  $packageMatch = [regex]::Match($content, 'package\s+([\w\.]+)')
  $classIndex[$sourceFile.BaseName] = [ordered]@{
    name = $sourceFile.BaseName
    file = $sourceFile.FullName
    package = if ($packageMatch.Success) { $packageMatch.Groups[1].Value } else { '' }
    kind = Get-ClassKind -Content $content -FileName $sourceFile.Name
  }
}

$pageEntries = New-Object System.Collections.Generic.List[object]
foreach ($className in ($classIndex.Keys | Sort-Object)) {
  $classMeta = $classIndex[$className]
  if ($classMeta.kind -notin @('activity', 'fragment')) {
    continue
  }

  $content = $contentIndex[$className]
  $layoutRefs = New-Object 'System.Collections.Generic.HashSet[string]'
  foreach ($layoutName in (Get-UniqueMatches -Content $content -Pattern 'R\.layout\.(\w+)')) {
    [void]$layoutRefs.Add($layoutName)
  }
  foreach ($bindingName in (Get-UniqueMatches -Content $content -Pattern '([A-Z][A-Za-z0-9_]*)Binding' -Group 1)) {
    [void]$layoutRefs.Add((Convert-CamelToSnake -Value $bindingName))
  }

  $menuRefs = Get-UniqueMatches -Content $content -Pattern 'R\.menu\.(\w+)'
  $classRefs = New-Object 'System.Collections.Generic.HashSet[string]'
  foreach ($candidateName in $classIndex.Keys) {
    if ($candidateName -eq $className) {
      continue
    }
    if ($content -match "\b$([regex]::Escape($candidateName))\b") {
      $candidateKind = $classIndex[$candidateName].kind
      if ($candidateKind -ne 'other') {
        [void]$classRefs.Add($candidateName)
      }
    }
  }

  $resolvedLayouts = New-Object System.Collections.Generic.List[object]
  $missingLayouts = New-Object System.Collections.Generic.List[string]
  foreach ($layoutRef in (@($layoutRefs) | Sort-Object)) {
    if ($layoutIndex.ContainsKey($layoutRef)) {
      $resolvedLayouts.Add([ordered]@{
          name = $layoutRef
          file = $layoutIndex[$layoutRef]
        }) | Out-Null
    } else {
      $missingLayouts.Add($layoutRef) | Out-Null
    }
  }

  $resolvedMenus = New-Object System.Collections.Generic.List[object]
  $missingMenus = New-Object System.Collections.Generic.List[string]
  foreach ($menuRef in $menuRefs) {
    if ($menuIndex.ContainsKey($menuRef)) {
      $resolvedMenus.Add([ordered]@{
          name = $menuRef
          file = $menuIndex[$menuRef]
        }) | Out-Null
    } else {
      $missingMenus.Add($menuRef) | Out-Null
    }
  }

  $resolvedClasses = New-Object System.Collections.Generic.List[object]
  foreach ($classRef in (@($classRefs) | Sort-Object)) {
    $refMeta = $classIndex[$classRef]
    $resolvedClasses.Add([ordered]@{
        name = $refMeta.name
        kind = $refMeta.kind
        file = $refMeta.file
      }) | Out-Null
  }

  $pageEntries.Add([ordered]@{
      name = $classMeta.name
      kind = $classMeta.kind
      file = $classMeta.file
      package = $classMeta.package
      dependencies = [ordered]@{
        layouts = $resolvedLayouts
        menus = $resolvedMenus
        classes = $resolvedClasses
      }
      unresolved = [ordered]@{
        layouts = $missingLayouts
        menus = $missingMenus
      }
      status = 'todo'
    }) | Out-Null
}

$summary = [ordered]@{
  sourceRoot = $resolvedSourceRoot
  generatedAt = (Get-Date).ToString('s')
  stats = [ordered]@{
    sourceFileCount = $sourceFiles.Count
    layoutCount = $layoutFiles.Count
    menuCount = $menuFiles.Count
    pageCount = $pageEntries.Count
    activityCount = @($pageEntries | Where-Object { $_.kind -eq 'activity' }).Count
    fragmentCount = @($pageEntries | Where-Object { $_.kind -eq 'fragment' }).Count
    dialogCount = @($classIndex.Values | Where-Object { $_.kind -eq 'dialog' }).Count
    adapterCount = @($classIndex.Values | Where-Object { $_.kind -eq 'adapter' }).Count
  }
  pages = $pageEntries
}

$summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resolvedOutputPath -Encoding UTF8
Write-Host "Wrote manifest to $resolvedOutputPath"
