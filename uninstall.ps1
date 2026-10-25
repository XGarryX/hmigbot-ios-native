param([string]$Target=(Get-Location).Path)
& python "$PSScriptRoot/scripts/manage_install.py" uninstall --workspace $Target
exit $LASTEXITCODE
