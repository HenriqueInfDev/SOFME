<#
Create a ZIP of dist\SOFME for distribution.
Usage: run from repository root (where SOFME folder is).
#>
$here = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $here

$dist = Join-Path $here 'dist\SOFME'
if (-not (Test-Path $dist)) { Write-Error "Pasta de build não encontrada: $dist"; exit 1 }

# Create a temporary staging directory
$staging = Join-Path $here 'staging_release'
if (Test-Path $staging) { Remove-Item $staging -Recurse -Force }
New-Item -ItemType Directory -Path $staging | Out-Null

Write-Host "Preparando arquivos para o pacote..."

# Copy dist\SOFME contents (executable and _internal)
Copy-Item (Join-Path $dist '*') -Destination $staging -Recurse -Force

# Copy app folder with latest code
Write-Host "Copiando pasta app com código atualizado..."
Copy-Item (Join-Path $here 'app') -Destination (Join-Path $staging 'app') -Recurse -Force

# Copy main.py and other important files
Copy-Item (Join-Path $here 'main.py') -Destination $staging -Force
Copy-Item (Join-Path $here 'requirements.txt') -Destination $staging -Force
Copy-Item (Join-Path $here 'local_params.txt') -Destination $staging -Force

# Copy database folder structure
$dbfolder = Join-Path $here 'Gestão de Produção'
if (Test-Path $dbfolder) {
    Write-Host "Copiando estrutura do banco de dados..."
    Copy-Item $dbfolder -Destination (Join-Path $staging 'Gestão de Produção') -Recurse -Force
}

$zip = Join-Path $here 'SOFME_release.zip'
if (Test-Path $zip) { Remove-Item $zip -Force }

Write-Host "Compactando em $zip ..."
Compress-Archive -Path (Join-Path $staging '*') -DestinationPath $zip -Force

# Clean up staging directory
Remove-Item $staging -Recurse -Force

Write-Host "ZIP criado com sucesso: $zip"
