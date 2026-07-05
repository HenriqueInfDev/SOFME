<#
Create a ZIP of dist\SOFME for distribution.
Usage: run from repository root (where SOFME folder is).
#>
$here = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $here

$dist = Join-Path $here 'dist\SOFME'
if (-not (Test-Path $dist)) { Write-Error "Pasta de build não encontrada: $dist"; exit 1 }

$zip = Join-Path $here 'SOFME_release.zip'
if (Test-Path $zip) { Remove-Item $zip -Force }

Write-Host "Compactando $dist em $zip ..."
Compress-Archive -Path (Join-Path $dist '*') -DestinationPath $zip -Force
Write-Host "ZIP criado: $zip"
