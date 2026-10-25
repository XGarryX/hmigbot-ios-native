param(
  [Parameter(Mandatory = $true)]
  [string]$ManifestPath,

  [Parameter(Mandatory = $true)]
  [string[]]$PageNames,

  [string]$OutputDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Convert-ToSlug {
  param([string]$Value)

  $slug = [regex]::Replace($Value, '([a-z0-9])([A-Z])', '$1-$2')
  $slug = [regex]::Replace($slug, '[^A-Za-z0-9\-]+', '-')
  $slug = [regex]::Replace($slug, '-{2,}', '-')
  return $slug.Trim('-').ToLowerInvariant()
}

function Resolve-FullPath {
  param([string]$Path)

  if ([System.IO.Path]::IsPathRooted($Path)) {
    return [System.IO.Path]::GetFullPath($Path)
  }

  return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
}

$resolvedManifestPath = (Resolve-Path -LiteralPath $ManifestPath).Path
$manifest = Get-Content -LiteralPath $resolvedManifestPath -Raw | ConvertFrom-Json
$manifestDirectory = Split-Path -Parent $resolvedManifestPath

if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
  $resolvedOutputDirectory = Join-Path $manifestDirectory 'batches'
} else {
  $resolvedOutputDirectory = Resolve-FullPath -Path $OutputDirectory
}
if (-not (Test-Path -LiteralPath $resolvedOutputDirectory)) {
  New-Item -ItemType Directory -Force -Path $resolvedOutputDirectory | Out-Null
}

$selectedPages = New-Object System.Collections.Generic.List[object]
foreach ($pageName in $PageNames) {
  $page = $manifest.pages | Where-Object {
    $_.name -eq $pageName -or $_.file -like "*$pageName*"
  } | Select-Object -First 1

  if (-not $page) {
    throw "Page '$pageName' was not found in manifest $resolvedManifestPath"
  }

  if (-not ($selectedPages | Where-Object { $_.name -eq $page.name })) {
    $selectedPages.Add($page) | Out-Null
  }
}

$sourceFiles = New-Object 'System.Collections.Generic.HashSet[string]'
$layoutFiles = New-Object 'System.Collections.Generic.HashSet[string]'
$menuFiles = New-Object 'System.Collections.Generic.HashSet[string]'
$classFiles = New-Object 'System.Collections.Generic.HashSet[string]'

foreach ($page in $selectedPages) {
  [void]$sourceFiles.Add($page.file)
  foreach ($layout in $page.dependencies.layouts) {
    [void]$layoutFiles.Add($layout.file)
    [void]$sourceFiles.Add($layout.file)
  }
  foreach ($menu in $page.dependencies.menus) {
    [void]$menuFiles.Add($menu.file)
    [void]$sourceFiles.Add($menu.file)
  }
  foreach ($classDependency in $page.dependencies.classes) {
    [void]$classFiles.Add($classDependency.file)
    [void]$sourceFiles.Add($classDependency.file)
  }
}

$batchName = ($selectedPages | ForEach-Object { Convert-ToSlug -Value $_.name }) -join '__'
$batchTitle = ($selectedPages | ForEach-Object { $_.name }) -join ', '
$markdownPath = Join-Path $resolvedOutputDirectory "$batchName.md"
$jsonPath = Join-Path $resolvedOutputDirectory "$batchName.json"
$migrationIndexPath = Join-Path $manifestDirectory 'migration-index.json'

if (-not (Test-Path -LiteralPath $migrationIndexPath)) {
  @{
    coveredPages = @()
    coveredSourceFiles = @()
    translatedTargets = @()
  } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $migrationIndexPath -Encoding UTF8
}

$batch = [ordered]@{
  name = $batchName
  title = $batchTitle
  manifestPath = $resolvedManifestPath
  migrationIndexPath = $migrationIndexPath
  pages = @($selectedPages | ForEach-Object {
      [ordered]@{
        name = $_.name
        kind = $_.kind
        file = $_.file
      }
    })
  sourceFiles = @($sourceFiles | Sort-Object)
  groups = [ordered]@{
    layouts = @($layoutFiles | Sort-Object)
    menus = @($menuFiles | Sort-Object)
    classes = @($classFiles | Sort-Object)
  }
  status = 'todo'
}

$batch | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $jsonPath -Encoding UTF8

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# Feature Batch: $batchTitle") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("## Purpose") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("Migrate only this Android source batch into ArkUI. Do not include unrelated pages.") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("## Batch Metadata") | Out-Null
$lines.Add("") | Out-Null
$lines.Add(("- Batch JSON: ``{0}``" -f $jsonPath)) | Out-Null
$lines.Add(("- Manifest: ``{0}``" -f $resolvedManifestPath)) | Out-Null
$lines.Add(("- Migration index: ``{0}``" -f $migrationIndexPath)) | Out-Null
$lines.Add("") | Out-Null
$lines.Add("## Entry Pages") | Out-Null
$lines.Add("") | Out-Null
foreach ($page in $selectedPages) {
  $lines.Add(("- {0} (``{1}``)" -f $page.name, $page.kind)) | Out-Null
  $lines.Add(("  Source: ``{0}``" -f $page.file)) | Out-Null
}
$lines.Add("") | Out-Null
$lines.Add("## Direct Dependencies") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("### Layouts") | Out-Null
foreach ($layoutPath in (@($layoutFiles) | Sort-Object)) {
  $lines.Add(("- ``{0}``" -f $layoutPath)) | Out-Null
}
$lines.Add("") | Out-Null
$lines.Add("### Menus") | Out-Null
foreach ($menuPath in (@($menuFiles) | Sort-Object)) {
  $lines.Add(("- ``{0}``" -f $menuPath)) | Out-Null
}
$lines.Add("") | Out-Null
$lines.Add("### Classes") | Out-Null
foreach ($classPath in (@($classFiles) | Sort-Object)) {
  $lines.Add(("- ``{0}``" -f $classPath)) | Out-Null
}
$lines.Add("") | Out-Null
$lines.Add("## Guardrails") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("- List dependencies before editing target files.") | Out-Null
$lines.Add("- Translate static UI structure before wiring deep behavior.") | Out-Null
$lines.Add("- Create missing child components, item components, and dialogs in the same batch.") | Out-Null
$lines.Add("- Keep unsupported behavior as explicit TODOs.") | Out-Null
$lines.Add("- Update `migration-index.json` after the batch is migrated.") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("## Done Criteria") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("- All entry pages and direct dependencies in this pack are represented in target code.") | Out-Null
$lines.Add("- The migration index is updated.") | Out-Null
$lines.Add("- Coverage check passes.") | Out-Null
$lines.Add("- Target build check passes or remaining blockers are explicitly documented.") | Out-Null

$lines | Set-Content -LiteralPath $markdownPath -Encoding UTF8

Write-Host "Wrote batch markdown to $markdownPath"
Write-Host "Wrote batch metadata to $jsonPath"
