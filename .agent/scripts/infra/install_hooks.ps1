# install_hooks.ps1 — Instala os git hooks do KARE no repositório local
# Execute UMA VEZ após cada clone: .agent/scripts/infra/install_hooks.ps1
#
# O que instala:
#   • pre-commit   → bloqueia commits com credenciais em plain-text (SECURITY)

$ROOT      = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
$HOOKS_SRC = Join-Path (Split-Path -Parent $PSScriptRoot) "hooks"
$HOOKS_DST = Join-Path $ROOT ".git\hooks"

if (-not (Test-Path $HOOKS_DST)) {
    Write-Host "❌ Pasta .git/hooks não encontrada. Certifique-se de estar na raiz do repositório." -ForegroundColor Red
    exit 1
}

$hooks = @("pre-commit", "post-commit")

foreach ($hook in $hooks) {
    $src = Join-Path $HOOKS_SRC $hook
    $dst = Join-Path $HOOKS_DST $hook

    if (-not (Test-Path $src)) {
        Write-Host "⚠️  Hook source não encontrado: $src" -ForegroundColor Yellow
        continue
    }

    Copy-Item -Path $src -Destination $dst -Force
    Write-Host "✅ Hook instalado: $hook" -ForegroundColor Green
}

Write-Host ""
Write-Host "Bootstrapping Context Engine (SQLite/FTS5)..." -ForegroundColor Cyan
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & python "$ROOT/.agent/scripts/ai/kare_rag.py" migrate
} else {
    Write-Host "  python nao encontrado — execute manualmente:" -ForegroundColor Yellow
    Write-Host "  python .agent/scripts/ai/kare_rag.py migrate" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Git hooks KARE instalados com sucesso." -ForegroundColor Green
Write-Host "  * pre-commit  : bloqueia credenciais em plain-text"
Write-Host "  * Context Engine: .specify/rag/ (3 bancos SQLite standalone)"
