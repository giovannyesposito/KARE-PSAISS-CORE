#Requires -Version 5.1
<#
.SYNOPSIS
    KARE-SPEC — Setup & Onboarding Windows
.DESCRIPTION
    Script interativo de instalação para novos usuários do KARE-SPEC.
    Executa verificação de pré-requisitos, instalação de dependências Python,
    configuração de credenciais e validação do ambiente.

    Idempotente: pode ser executado múltiplas vezes sem efeitos colaterais.

.EXAMPLE
    .\setup.ps1                    # Setup completo interativo
    .\setup.ps1 -SkipCredentials   # Pula configuração de credenciais
    .\setup.ps1 -Quick             # Apenas instala deps, sem wizard

.NOTES
    Pré-requisitos:
      - Windows 10/11 ou Windows Server 2019+
      - PowerShell 5.1+ (já incluído no Windows)
      - Python 3.10+   → https://python.org/downloads
      - Git 2.40+      → https://git-scm.com
      - VS Code 1.90+  → https://code.visualstudio.com
      - GitHub Copilot Chat (extensão VS Code, requer assinatura)
#>

[CmdletBinding()]
param(
    [switch]$SkipCredentials,
    [switch]$Quick,
    [switch]$NoColor
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Força UTF-8 para exibir emojis e caracteres especiais no console Windows
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding           = [System.Text.Encoding]::UTF8

# ──────────────────────────────────────── CORES / UI ─────────────────────────
function Write-Header([string]$text) {
    Write-Host "`n$('─' * 62)" -ForegroundColor Cyan
    Write-Host "  $text" -ForegroundColor White
    Write-Host "$('─' * 62)" -ForegroundColor Cyan
}

function Write-Step([string]$icon, [string]$text) {
    Write-Host "`n$icon  $text" -ForegroundColor Yellow
}

function Write-OK([string]$text) {
    Write-Host "  [OK] $text" -ForegroundColor Green
}

function Write-WARN([string]$text) {
    Write-Host "  [!]  $text" -ForegroundColor Yellow
}

function Write-FAIL([string]$text) {
    Write-Host "  [X]  $text" -ForegroundColor Red
}

function Write-INFO([string]$text) {
    Write-Host "       $text" -ForegroundColor Gray
}

# ──────────────────────────────────────── VARIÁVEIS ──────────────────────────
$WORKSPACE   = $PSScriptRoot
$VSCODE_DIR  = Join-Path $WORKSPACE ".vscode"
$AGENT_DIR   = Join-Path $WORKSPACE ".agent"
$CONFIG_DIR  = Join-Path $WORKSPACE ".config" ".venv"
$HOOKS_DIR   = Join-Path $WORKSPACE ".git" "hooks"
$REQ_FILE    = Join-Path $WORKSPACE "requirements.txt"
$CREDS_SCRIPT= Join-Path $WORKSPACE ".agent" "scripts" "infra" "kare_credentials.py"
$MIN_PYTHON  = [version]"3.10"

$REQUIRED_VSCODE_EXTENSIONS = @(
    "GitHub.copilot-chat",
    "ms-python.python"
)

$OPTIONAL_VSCODE_EXTENSIONS = @(
    "mermaid.mermaid-markdown-syntax-highlighting",
    "davidanson.vscode-markdownlint"
)

# ──────────────────────────────────────── BANNER ─────────────────────────────
Clear-Host
Write-Host @"

  ██╗  ██╗ █████╗ ██████╗ ███████╗
  ██║ ██╔╝██╔══██╗██╔══██╗██╔════╝
  █████╔╝ ███████║██████╔╝█████╗
  ██╔═██╗ ██╔══██║██╔══██╗██╔══╝
  ██║  ██╗██║  ██║██║  ██║███████╗
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

  KARE-SPEC — Setup & Onboarding
  KARE-PSAISS-CORE

"@ -ForegroundColor Cyan

# ──────────────────────────────────────── PASSO 1: PRÉ-REQUISITOS ────────────
Write-Header "PASSO 1 — Verificando Pré-requisitos"
$prereqOK = $true

# Python
Write-Step "🐍" "Python"
try {
    $pyVer = python --version 2>&1
    if ($pyVer -match "Python (\d+\.\d+)") {
        $ver = [version]$Matches[1]
        if ($ver -ge $MIN_PYTHON) {
            Write-OK "Python $ver encontrado"
        } else {
            Write-FAIL "Python $ver menor que $MIN_PYTHON. Faca upgrade: https://python.org/downloads"
            $prereqOK = $false
        }
    }
} catch {
    Write-FAIL "Python não encontrado. Instale em: https://python.org/downloads"
    $prereqOK = $false
}

# Git
Write-Step "🔧" "Git"
try {
    $gitVer = git --version 2>&1
    Write-OK "$gitVer"
} catch {
    Write-FAIL "Git não encontrado. Instale em: https://git-scm.com"
    $prereqOK = $false
}

# VS Code
Write-Step "💻" "VS Code"
$codeCmd = Get-Command code -ErrorAction SilentlyContinue
if ($codeCmd) {
    $codeVer = code --version 2>&1 | Select-Object -First 1
    Write-OK "VS Code $codeVer"
} else {
    Write-WARN "VS Code não encontrado no PATH. Instale em: https://code.visualstudio.com"
    Write-INFO "O setup continua, mas abra o workspace manualmente depois."
}

# Extensões VS Code
Write-Step "🧩" "Extensões VS Code"
if ($codeCmd) {
    $installedExts = code --list-extensions 2>&1
    foreach ($ext in $REQUIRED_VSCODE_EXTENSIONS) {
        if ($installedExts -contains $ext) {
            Write-OK "$ext"
        } else {
            Write-WARN "$ext — NÃO instalada (obrigatória)"
            Write-INFO "Instale: code --install-extension $ext"
        }
    }
    foreach ($ext in $OPTIONAL_VSCODE_EXTENSIONS) {
        if ($installedExts -contains $ext) {
            Write-OK "$ext (opcional)"
        } else {
            Write-INFO "$ext — opcional, não instalada"
        }
    }
}

if (-not $prereqOK) {
    Write-Host "`n[X] Pré-requisitos críticos ausentes. Corrija e re-execute setup.ps1." -ForegroundColor Red
    exit 1
}

Write-Host "`n  Pré-requisitos OK." -ForegroundColor Green

# ──────────────────────────────────────── PASSO 2: DEPENDÊNCIAS PYTHON ───────
Write-Header "PASSO 2 — Instalando Dependências Python"

if (-not (Test-Path $REQ_FILE)) {
    Write-FAIL "requirements.txt não encontrado em $WORKSPACE"
    exit 1
}

Write-Step "📦" "pip install -r requirements.txt"
Write-INFO "Isso pode levar alguns minutos na primeira vez..."

try {
    python -m pip install --upgrade pip --quiet
    python -m pip install -r $REQ_FILE 2>&1 | ForEach-Object {
        if ($_ -match "Successfully installed") {
            Write-OK $_
        } elseif ($_ -match "error|Error") {
            Write-WARN $_
        }
    }
    Write-OK "Dependências instaladas."
} catch {
    Write-FAIL "Erro ao instalar dependências: $_"
    Write-INFO "Tente manualmente: pip install -r requirements.txt"
    exit 1
}

# ──────────────────────────────────────── PASSO 3: GIT HOOKS ─────────────────
Write-Header "PASSO 3 — Configurando Git Hooks (Segurança)"

$hookSrc  = Join-Path $AGENT_DIR "scripts" "hooks" "pre-commit"
$hookDest = Join-Path $HOOKS_DIR "pre-commit"

if (Test-Path $hookSrc) {
    if (-not (Test-Path $HOOKS_DIR)) {
        New-Item -ItemType Directory -Path $HOOKS_DIR -Force | Out-Null
    }
    Copy-Item $hookSrc $hookDest -Force
    Write-OK "Hook pre-commit instalado em .git/hooks/"
    Write-INFO "O hook bloqueia commit de credenciais em texto plano."
} else {
    Write-WARN "Hook pre-commit não encontrado em .agent/scripts/hooks/"
}

# ──────────────────────────────────────── PASSO 4: CREDENCIAIS ───────────────
if (-not $SkipCredentials -and -not $Quick) {
    Write-Header "PASSO 4 — Configurando Credenciais"
    Write-INFO "As credenciais são criptografadas com AES-256-GCM e salvas localmente."
    Write-INFO "Nunca são commitadas no repositório."
    Write-Host ""

    # Verifica se já existe configuração
    $credsFile = Join-Path $CONFIG_DIR "mcp-atlassian.enc"
    $doCreds = $true
    if (Test-Path $credsFile) {
        Write-WARN "Credenciais ja configuradas em $credsFile"
        $resp = Read-Host "  Reconfigurar? [s/N]"
        if ($resp -ne "s" -and $resp -ne "S") {
            Write-INFO "Mantendo credenciais existentes."
            $doCreds = $false
        }
    }

    if ($doCreds) {
    Write-Step "🔑" "Atlassian (Confluence + Jira)"
    Write-INFO "Obtenha o token em: https://id.atlassian.com/manage-profile/security/api-tokens"
    Write-Host ""
    $atlUrl   = Read-Host "  URL Confluence (ex: https://empresa.atlassian.net)"
    $atlUser  = Read-Host "  Email Atlassian"
    $atlToken = Read-Host "  API Token" -AsSecureString

    if ($atlUrl -and $atlUser) {
        # Constrói JSON de credenciais e chama o script de setup
        $tokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
            [Runtime.InteropServices.Marshal]::SecureStringToBSTR($atlToken)
        )

        if (Test-Path $CREDS_SCRIPT) {
            # Grava JSON em arquivo temporário — kare_credentials.py espera caminho, não stdin
            $tmpJson = [System.IO.Path]::GetTempFileName() + ".json"
            try {
                $jsonInput = @{
                    CONFLUENCE_URL      = $atlUrl
                    CONFLUENCE_USERNAME = $atlUser
                    CONFLUENCE_API_TOKEN= $tokenPlain
                    JIRA_URL            = $atlUrl
                    JIRA_USERNAME       = $atlUser
                    JIRA_API_TOKEN      = $tokenPlain
                } | ConvertTo-Json
                [System.IO.File]::WriteAllText($tmpJson, $jsonInput, [System.Text.Encoding]::UTF8)

                python $CREDS_SCRIPT setup --from-json $tmpJson 2>&1 | Out-Null
                Write-OK "Credenciais Atlassian salvas."
            } catch {
                Write-WARN "Não foi possível salvar credenciais automaticamente."
                Write-INFO "Execute manualmente: python .agent\scripts\infra\kare_credentials.py setup"
            } finally {
                # O script Python já apaga o arquivo; limpa se ainda existir
                if (Test-Path $tmpJson) { Remove-Item $tmpJson -Force -ErrorAction SilentlyContinue }
                $tokenPlain = $null
            }
        } else {
            Write-WARN "Script de credenciais não encontrado."
            Write-INFO "Execute: python .agent\scripts\infra\kare_credentials.py setup"
        }
    } else {
        Write-WARN "Credenciais Atlassian puladas. Configure depois com:"
        Write-INFO "  python .agent\scripts\infra\kare_credentials.py setup"
    }
    } # end if ($doCreds)
}

# ──────────────────────────────────────── CONCLUSÃO ──────────────────────────
Write-Header "SETUP CONCLUÍDO"

Write-Host @"

  Próximos passos:

  1. Abra o workspace no VS Code:
     code "$WORKSPACE"

  2. Confirme que a extensão GitHub Copilot Chat está ativa.

  3. Abra o Copilot Chat (Ctrl+Alt+I) e teste:
     /status

  4. Para iniciar o Context Engine (RAG semântico):
     Ctrl+Shift+P → Tasks: Run Task → KARE-SPEC: Start Context Engine

  5. Para configurar Atlassian depois:
     python .agent\scripts\infra\kare_credentials.py setup

"@ -ForegroundColor Cyan

Write-Host "  Documentação completa: README.md" -ForegroundColor White
Write-Host "  Suporte: use /status no Copilot Chat para verificar saúde do sistema.`n" -ForegroundColor Gray
