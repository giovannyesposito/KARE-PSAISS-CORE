$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Delega toda a lógica de configuração para kare_credentials.py (AES-256-GCM)
# A chave fica em %USERPROFILE%\kare.key (fora do projeto, nunca no git).
# As credenciais ficam em .config\.venv\mcp-atlassian.enc (criptografado).
# ---------------------------------------------------------------------------

$pythonExe = $null

# Tentar Python do .venv do workspace primeiro, depois Python global
$repoRoot   = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    $pythonExe = $venvPython
} else {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) { $pythonExe = $cmd.Source }
}

if (-not $pythonExe) {
    Write-Error "Python nao encontrado. Instale Python 3.11+ e tente novamente."
    exit 1
}

$credScript = Join-Path $PSScriptRoot "kare_credentials.py"

# Garantir que cryptography está instalado
# Temporariamente desativa Stop para evitar NativeCommandError do pip
$_eap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& $pythonExe -m pip install cryptography --quiet 2>$null | Out-Null
$ErrorActionPreference = $_eap

# Validar que cryptography foi instalado com sucesso
$_check = & $pythonExe -c "import cryptography" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: Nao foi possivel instalar o pacote 'cryptography'." -ForegroundColor Red
    Write-Host "Tente manualmente:" -ForegroundColor Yellow
    Write-Host "  pip install cryptography" -ForegroundColor Cyan
    exit 1
}

# Executar setup interativo via Python
& $pythonExe $credScript setup
