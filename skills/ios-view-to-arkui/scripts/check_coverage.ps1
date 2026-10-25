param(
  [Parameter(Mandatory = $true)]
  [string]$BatchJsonPath,

  [string]$MigrationIndexPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolvedBatchPath = (Resolve-Path -LiteralPath $BatchJsonPath).Path
$batch = Get-Content -LiteralPath $resolvedBatchPath -Raw | ConvertFrom-Json

if ([string]::IsNullOrWhiteSpace($MigrationIndexPath)) {
  $resolvedMigrationIndexPath = $batch.migrationIndexPath
} else {
  $resolvedMigrationIndexPath = (Resolve-Path -LiteralPath $MigrationIndexPath).Path
}

if (-not (Test-Path -LiteralPath $resolvedMigrationIndexPath)) {
  @{
    coveredPages = @()
    coveredSourceFiles = @()
    translatedTargets = @()
  } | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $resolvedMigrationIndexPath -Encoding UTF8
  throw "Created a starter migration index at $resolvedMigrationIndexPath. Update it and rerun coverage."
}

$migrationIndex = Get-Content -LiteralPath $resolvedMigrationIndexPath -Raw | ConvertFrom-Json
$coveredPages = @($migrationIndex.coveredPages)
$coveredSourceFiles = @($migrationIndex.coveredSourceFiles)

$expectedPages = @($batch.pages | ForEach-Object { $_.name })
$expectedFiles = @($batch.sourceFiles)

$missingPages = @($expectedPages | Where-Object { $_ -notin $coveredPages })
$missingFiles = @($expectedFiles | Where-Object { $_ -notin $coveredSourceFiles })
$extraFiles = @($coveredSourceFiles | Where-Object { $_ -notin $expectedFiles })

$result = [ordered]@{
  batch = $batch.name
  migrationIndexPath = $resolvedMigrationIndexPath
  expectedPageCount = $expectedPages.Count
  expectedFileCount = $expectedFiles.Count
  missingPages = $missingPages
  missingFiles = $missingFiles
  extraCoveredFiles = $extraFiles
}

$result | ConvertTo-Json -Depth 6 | Write-Output

if ($missingPages.Count -gt 0 -or $missingFiles.Count -gt 0) {
  exit 1
}
