#Requires -Version 5.1
<#
.SYNOPSIS
    Registra a Task Agendada "KARE Telemetry Export" no Windows Task Scheduler.

.DESCRIPTION
    Cria uma tarefa que executa kare_rag.py telemetry stats --quiet a cada 15 minutos,
    consolidando métricas de uso no banco SQLite local (kare_telemetry.db).

    Comportamento:
      - Detecta automaticamente o executável Python correto (python → py → fallback)
      - Cria a tarefa para rodar como o usuário logado, sem janela visível
      - Se a tarefa já existir, atualiza sem perguntar

.EXAMPLE
    .\register_metrics_task.ps1
    .\register_metrics_task.ps1 -Unregister     # Remove a tarefa
    .\register_metrics_task.ps1 -Status         # Exibe status da tarefa
    .\register_metrics_task.ps1 -RunNow         # Força execução imediata (teste)

.NOTES
    A tarefa é registrada em: \KARE\KARE Telemetry Export
    Intervalo: 15 minutos
    Fonte de dados: .specify/rag/kare_telemetry.db (SQLite standalone)
#>

[CmdletBinding()]
param(
    [switch]$Unregister,
    [switch]$Status,
    [switch]$RunNow
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Constantes ───────────────────────────────────────────────────────────────
$TASK_FOLDER  = "\KARE"
$TASK_NAME    = "KARE Telemetry Export"
$TASK_FULL    = "$TASK_FOLDER\$TASK_NAME"
$INTERVAL_MIN = 15

# Caminho do workspace (2 níveis acima deste script: .agent\scripts\infra\ → raiz)
$SCRIPT_DIR   = Split-Path -Parent $PSScriptRoot   # .agent\scripts\
$WORKSPACE    = Split-Path -Parent $SCRIPT_DIR      # .agent\
$WORKSPACE    = Split-Path -Parent $WORKSPACE       # raiz do projeto

$METRICS_SCRIPT = Join-Path $WORKSPACE ".agent\scripts\ai\kare_rag.py"

# ── Helpers de UI ─────────────────────────────────────────────────────────────
function Write-Step([string]$icon, [string]$text) {
    Write-Host "`n$icon  $text" -ForegroundColor Yellow
}
function Write-OK([string]$text)   { Write-Host "   [OK] $text" -ForegroundColor Green }
function Write-Warn([string]$text) { Write-Host "   [!!] $text" -ForegroundColor Yellow }
function Write-Err([string]$text)  { Write-Host "   [XX] $text" -ForegroundColor Red }

# ── Detectar Python ───────────────────────────────────────────────────────────
function Get-PythonExe {
    <#
    Testa 'python' e 'py' na ordem.
    Retorna o caminho completo do executável que funciona.
    Falha se nenhum for encontrado.
    #>
    $candidates = @("python", "py")
    foreach ($cmd in $candidates) {
        try {
            $result = & $cmd --version 2>&1
            if ($LASTEXITCODE -eq 0 -or $result -match "Python") {
                $resolved = (Get-Command $cmd -ErrorAction SilentlyContinue).Source
                if ($resolved) {
                    Write-OK "Python encontrado: $resolved ($result)"
                    return $resolved
                }
                # Fallback: usar o nome do comando diretamente se Get-Command não resolver
                Write-OK "Python encontrado via '$cmd' ($result)"
                return $cmd
            }
        } catch {
            # Ignora e tenta próximo
        }
    }
    throw "Python não encontrado. Instale Python 3.10+ e adicione ao PATH."
}

# ── Ação: Status ──────────────────────────────────────────────────────────────
if ($Status) {
    Write-Host "`n🔷 KARE Telemetry Task — Status" -ForegroundColor Cyan
    try {
        $task = Get-ScheduledTask -TaskPath $TASK_FOLDER -TaskName $TASK_NAME -ErrorAction Stop
        $info = Get-ScheduledTaskInfo -TaskPath $TASK_FOLDER -TaskName $TASK_NAME
        Write-Host "   Nome:            $TASK_FULL"
        Write-Host "   Estado:          $($task.State)"
        Write-Host "   Última execução: $($info.LastRunTime)"
        Write-Host "   Último resultado: $($info.LastTaskResult) $(if ($info.LastTaskResult -eq 0) {'(Sucesso)'} else {'(Falha)'})"
        Write-Host "   Próxima execução: $($info.NextRunTime)"
    } catch {
        Write-Warn "Tarefa não encontrada: $TASK_FULL"
        Write-Host "   Execute o script sem parâmetros para registrar a tarefa."
    }
    exit 0
}

# ── Ação: Remover ─────────────────────────────────────────────────────────────
if ($Unregister) {
    Write-Host "`n🔷 KARE Telemetry Task — Removendo..." -ForegroundColor Cyan
    try {
        Unregister-ScheduledTask -TaskPath $TASK_FOLDER -TaskName $TASK_NAME -Confirm:$false -ErrorAction Stop
        Write-OK "Tarefa removida: $TASK_FULL"
    } catch {
        Write-Warn "Tarefa não encontrada ou já removida."
    }
    exit 0
}

# ── Ação: Executar agora ──────────────────────────────────────────────────────
if ($RunNow) {
    Write-Host "`n🔷 KARE Telemetry Task — Executando agora..." -ForegroundColor Cyan
    try {
        Start-ScheduledTask -TaskPath $TASK_FOLDER -TaskName $TASK_NAME -ErrorAction Stop
        Write-OK "Tarefa disparada. Aguarde ~30s e verifique a pasta OneDrive."
        Write-Host "   Para ver resultado: .\register_metrics_task.ps1 -Status"
    } catch {
        Write-Err "Falha ao disparar tarefa. Ela está registrada?"
        Write-Host "   Execute o script sem parâmetros para registrar primeiro."
    }
    exit 0
}

# ── Ação Principal: Registrar ─────────────────────────────────────────────────
Write-Host ""
Write-Host "🔷 KARE Telemetry Export — Registro de Task Agendada" -ForegroundColor Cyan
Write-Host "   Intervalo: a cada $INTERVAL_MIN minutos" -ForegroundColor DarkGray
Write-Host "   Script:    $METRICS_SCRIPT telemetry stats --quiet" -ForegroundColor DarkGray

# [1] Validar que o script existe
Write-Step "1" "Validando script RAG..."
if (-not (Test-Path $METRICS_SCRIPT)) {
    Write-Err "Script não encontrado: $METRICS_SCRIPT"
    Write-Host "   Verifique a instalação do KARE." -ForegroundColor Red
    exit 1
}
Write-OK "Script encontrado."

# [2] Detectar Python (python → py)
Write-Step "2" "Detectando executável Python..."
try {
    $PY = Get-PythonExe
} catch {
    Write-Err $_.Exception.Message
    Write-Host "   Download: https://python.org/downloads" -ForegroundColor Red
    exit 1
}

# [3] Montar comando da tarefa
$PY_ESCAPED     = $PY -replace '"', '\"'
$SCRIPT_ESCAPED = $METRICS_SCRIPT -replace '"', '\"'

$psCommand = @"
`$result = & "$PY_ESCAPED" "$SCRIPT_ESCAPED" telemetry stats --quiet 2>&1; if (`$LASTEXITCODE -ne 0) { & py "$SCRIPT_ESCAPED" telemetry stats --quiet }
"@

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -Command `"$psCommand`"" `
    -WorkingDirectory $WORKSPACE

# [4] Trigger: repetir a cada 15 min, indefinidamente, a partir de agora
# Nota: omitir -RepetitionDuration faz o Task Scheduler repetir indefinidamente
# (usar [TimeSpan]::MaxValue gera XML inválido — P99999999D — rejeitado pelo scheduler)
$startTime = (Get-Date).AddMinutes(2)   # inicia 2 min à frente para dar tempo de registro
$trigger = New-ScheduledTaskTrigger `
    -RepetitionInterval (New-TimeSpan -Minutes $INTERVAL_MIN) `
    -Once `
    -At $startTime

# [6] Configurações da tarefa
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -WakeToRun:$false

# Principal: rodar como usuário logado (sem senha necessária, sem janela)
$principal = New-ScheduledTaskPrincipal `
    -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Limited

# [7] Registrar (cria ou sobrescreve)
Write-Step "4" "Registrando tarefa agendada..."
try {
    # Garantir que a pasta \KARE existe no Task Scheduler
    $schedService = New-Object -ComObject Schedule.Service
    $schedService.Connect()
    $rootFolder = $schedService.GetFolder("\")
    try {
        $rootFolder.GetFolder("KARE") | Out-Null
    } catch {
        $rootFolder.CreateFolder("KARE") | Out-Null
        Write-OK "Pasta '\KARE' criada no Task Scheduler."
    }
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($schedService) | Out-Null

    Register-ScheduledTask `
        -TaskPath $TASK_FOLDER `
        -TaskName $TASK_NAME `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Force `
        -ErrorAction Stop | Out-Null

    Write-OK "Tarefa registrada com sucesso!"
} catch {
    Write-Err "Falha ao registrar tarefa: $($_.Exception.Message)"
    exit 1
}

# [8] Confirmação
Write-Step "5" "Verificando registro..."
try {
    $task = Get-ScheduledTask -TaskPath $TASK_FOLDER -TaskName $TASK_NAME -ErrorAction Stop
    $info = Get-ScheduledTaskInfo -TaskPath $TASK_FOLDER -TaskName $TASK_NAME

    Write-Host ""
    Write-Host "✅ Task Scheduler configurado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Tarefa  : $TASK_FULL"                          -ForegroundColor White
    Write-Host "   Estado  : $($task.State)"                      -ForegroundColor White
    Write-Host "   Próxima : $($info.NextRunTime)"                -ForegroundColor White
    Write-Host "   Python  : $PY"                                 -ForegroundColor White
    Write-Host "   Script  : $METRICS_SCRIPT telemetry stats --quiet" -ForegroundColor White
    Write-Host ""
    Write-Host "   Comandos úteis:" -ForegroundColor DarkGray
    Write-Host "   .\register_metrics_task.ps1 -Status   → Ver status"   -ForegroundColor DarkGray
    Write-Host "   .\register_metrics_task.ps1 -RunNow   → Forçar execução agora" -ForegroundColor DarkGray
    Write-Host "   .\register_metrics_task.ps1 -Unregister → Remover tarefa"       -ForegroundColor DarkGray
} catch {
    Write-Warn "Tarefa registrada mas não foi possível consultar status."
}
