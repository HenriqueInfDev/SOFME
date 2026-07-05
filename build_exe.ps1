param(
    [switch]$onefile
)

# PowerShell build script for packaging SOFME with PyInstaller
# Usage: .\build_exe.ps1        -> onedir build
#        .\build_exe.ps1 -onefile -> onefile build

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# Try to activate project virtualenv (assumes .venv is in parent folder)
$venvActivate = Join-Path $scriptDir "..\.venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Host "Ativando venv: $venvActivate"
    . $venvActivate
} else {
    Write-Warning "Virtualenv não encontrado em ..\\.venv. Certifique-se de ativar manualmente se necessário."
}

Write-Host "Instalando/atualizando PyInstaller..."
pip install -U pyinstaller

# Files/folders to include (ajuste conforme necessário)
$adddata = @(
    "local_params.txt;.",
    "app\styles;app/styles",
    "app\images;app/images"
)

$addArgs = $adddata | ForEach-Object { "--add-data `"$_`"" } | Out-String
$addArgs = $addArgs -replace "\r?\n"," "

$mode = if ($onefile) { "--onefile" } else { "--onedir" }

Write-Host "Executando PyInstaller (modo: $mode) ..."
pyinstaller --name SOFME $mode --windowed $addArgs main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build concluído com sucesso. Verifique a pasta dist\SOFME"
} else {
    Write-Error "Build falhou com código de saída $LASTEXITCODE"
}
