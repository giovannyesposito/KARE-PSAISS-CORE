#!/usr/bin/env bash
# setup.sh — KARE-SPEC Setup & Onboarding (Mac/Linux)
#
# Script interativo de instalação para novos usuários do KARE-SPEC.
# Executa verificação de pré-requisitos, instalação de dependências Python,
# configuração de credenciais e validação do ambiente.
#
# Idempotente: pode ser executado múltiplas vezes sem efeitos colaterais.
# Equivalente Windows: setup.ps1
#
# Uso:
#   ./setup.sh                    # Setup completo interativo
#   ./setup.sh --skip-credentials # Pula configuração de credenciais
#   ./setup.sh --quick            # Apenas instala deps, sem wizard
#
# Pré-requisitos:
#   - macOS ou Linux
#   - bash 4+
#   - Python 3.10+  -> https://python.org/downloads
#   - Git            -> https://git-scm.com
#   - VS Code 1.90+  -> https://code.visualstudio.com
#   - GitHub Copilot Chat (extensão VS Code, requer assinatura)

set -uo pipefail

QUICK=false
SKIP_CREDENTIALS=false
NO_COLOR=false

for arg in "$@"; do
  case "$arg" in
    --quick) QUICK=true ;;
    --skip-credentials) SKIP_CREDENTIALS=true ;;
    --no-color) NO_COLOR=true ;;
    *) echo "Argumento desconhecido: $arg" ;;
  esac
done

# ──────────────────────────────────────── CORES / UI ─────────────────────────
if [ "$NO_COLOR" = true ] || [ ! -t 1 ]; then
  CYAN=""; YELLOW=""; GREEN=""; RED=""; GRAY=""; WHITE=""; NC=""
else
  CYAN=$'\033[0;36m'; YELLOW=$'\033[1;33m'; GREEN=$'\033[0;32m'
  RED=$'\033[0;31m'; GRAY=$'\033[0;90m'; WHITE=$'\033[1;37m'; NC=$'\033[0m'
fi

write_header() { printf "\n%s%s%s\n" "$CYAN" "──────────────────────────────────────────────────────────" "$NC"; printf "  %s%s%s\n" "$WHITE" "$1" "$NC"; printf "%s%s%s\n" "$CYAN" "──────────────────────────────────────────────────────────" "$NC"; }
write_step()   { printf "\n%s  %s\n" "$1" "$2"; }
write_ok()     { printf "  ${GREEN}[OK]${NC} %s\n" "$1"; }
write_warn()   { printf "  ${YELLOW}[!] ${NC} %s\n" "$1"; }
write_fail()   { printf "  ${RED}[X] ${NC} %s\n" "$1"; }
write_info()   { printf "       ${GRAY}%s${NC}\n" "$1"; }

# ──────────────────────────────────────── VARIÁVEIS ──────────────────────────
WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$WORKSPACE/.config/.venv"
HOOKS_DIR="$WORKSPACE/.git/hooks"
REQ_FILE="$WORKSPACE/requirements.txt"
CREDS_SCRIPT="$WORKSPACE/.agent/scripts/infra/kare_credentials.py"
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=10

REQUIRED_VSCODE_EXTENSIONS=(GitHub.copilot-chat ms-python.python)
OPTIONAL_VSCODE_EXTENSIONS=(mermaid.mermaid-markdown-syntax-highlighting davidanson.vscode-markdownlint)

# ──────────────────────────────────────── BANNER ─────────────────────────────
clear 2>/dev/null || true
printf "%s\n" "$CYAN"
cat <<'EOF'

  ██╗  ██╗ █████╗ ██████╗ ███████╗
  ██║ ██╔╝██╔══██╗██╔══██╗██╔════╝
  █████╔╝ ███████║██████╔╝█████╗
  ██╔═██╗ ██╔══██║██╔══██╗██╔══╝
  ██║  ██╗██║  ██║██║  ██║███████╗
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝

  KARE-SPEC — Setup & Onboarding
  KARE-PSAISS-CORE

EOF
printf "%s\n" "$NC"

# ──────────────────────────────────────── PASSO 1: PRÉ-REQUISITOS ────────────
write_header "PASSO 1 — Verificando Pré-requisitos"
PREREQ_OK=true

# Python (aceita "python3" ou "python")
write_step "🐍" "Python"
PYTHON_BIN=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1; then PYTHON_BIN="$cand"; break; fi
done
if [ -z "$PYTHON_BIN" ]; then
  write_fail "Python não encontrado. Instale em: https://python.org/downloads"
  PREREQ_OK=false
else
  PY_VER=$("$PYTHON_BIN" --version 2>&1 | awk '{print $2}')
  PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
  PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
  if [ "$PY_MAJOR" -gt "$MIN_PYTHON_MAJOR" ] || { [ "$PY_MAJOR" -eq "$MIN_PYTHON_MAJOR" ] && [ "$PY_MINOR" -ge "$MIN_PYTHON_MINOR" ]; }; then
    write_ok "Python $PY_VER encontrado ($PYTHON_BIN)"
  else
    write_fail "Python $PY_VER menor que $MIN_PYTHON_MAJOR.$MIN_PYTHON_MINOR. Faça upgrade: https://python.org/downloads"
    PREREQ_OK=false
  fi
fi

# Git
write_step "🔧" "Git"
if command -v git >/dev/null 2>&1; then
  write_ok "$(git --version)"
else
  write_fail "Git não encontrado. Instale em: https://git-scm.com"
  PREREQ_OK=false
fi

# VS Code
write_step "💻" "VS Code"
if command -v code >/dev/null 2>&1; then
  CODE_VER=$(code --version 2>&1 | head -n1)
  write_ok "VS Code $CODE_VER"
else
  write_warn "VS Code não encontrado no PATH. Instale em: https://code.visualstudio.com"
  write_info "O setup continua, mas abra o workspace manualmente depois."
fi

# Extensões VS Code
write_step "🧩" "Extensões VS Code"
if command -v code >/dev/null 2>&1; then
  INSTALLED_EXTS=$(code --list-extensions 2>&1 || true)
  for ext in "${REQUIRED_VSCODE_EXTENSIONS[@]}"; do
    if echo "$INSTALLED_EXTS" | grep -qi "^${ext}$"; then
      write_ok "$ext"
    else
      write_warn "$ext — NÃO instalada (obrigatória)"
      write_info "Instale: code --install-extension $ext"
    fi
  done
  for ext in "${OPTIONAL_VSCODE_EXTENSIONS[@]}"; do
    if echo "$INSTALLED_EXTS" | grep -qi "^${ext}$"; then
      write_ok "$ext (opcional)"
    else
      write_info "$ext — opcional, não instalada"
    fi
  done
fi

if [ "$PREREQ_OK" != true ]; then
  printf "\n${RED}[X] Pré-requisitos críticos ausentes. Corrija e re-execute ./setup.sh.${NC}\n"
  exit 1
fi

printf "\n  ${GREEN}Pré-requisitos OK.${NC}\n"

# ──────────────────────────────────────── PASSO 2: DEPENDÊNCIAS PYTHON ───────
write_header "PASSO 2 — Instalando Dependências Python"

if [ ! -f "$REQ_FILE" ]; then
  write_fail "requirements.txt não encontrado em $WORKSPACE"
  exit 1
fi

write_step "📦" "pip install -r requirements.txt"
write_info "Isso pode levar alguns minutos na primeira vez..."

if "$PYTHON_BIN" -m pip install --upgrade pip --quiet && \
   "$PYTHON_BIN" -m pip install -r "$REQ_FILE" --quiet; then
  write_ok "Dependências instaladas."
else
  write_fail "Erro ao instalar dependências."
  write_info "Tente manualmente: $PYTHON_BIN -m pip install -r requirements.txt"
  exit 1
fi

# ──────────────────────────────────────── PASSO 3: GIT HOOKS ─────────────────
write_header "PASSO 3 — Configurando Git Hooks (Segurança)"

HOOK_SRC="$WORKSPACE/.agent/scripts/hooks/pre-commit"
HOOK_DEST="$HOOKS_DIR/pre-commit"

if [ -f "$HOOK_SRC" ]; then
  mkdir -p "$HOOKS_DIR"
  cp "$HOOK_SRC" "$HOOK_DEST"
  chmod +x "$HOOK_DEST"
  write_ok "Hook pre-commit instalado em .git/hooks/"
  write_info "O hook bloqueia commit de credenciais em texto plano."
else
  write_warn "Hook pre-commit não encontrado em .agent/scripts/hooks/"
fi

# ──────────────────────────────────────── PASSO 4: CREDENCIAIS ───────────────
if [ "$SKIP_CREDENTIALS" != true ] && [ "$QUICK" != true ]; then
  write_header "PASSO 4 — Configurando Credenciais"
  write_info "As credenciais são criptografadas com AES-256-GCM e salvas localmente."
  write_info "Nunca são commitadas no repositório."
  echo ""

  CREDS_FILE="$CONFIG_DIR/mcp-atlassian.enc"
  DO_CREDS=true
  if [ -f "$CREDS_FILE" ]; then
    write_warn "Credenciais já configuradas em $CREDS_FILE"
    read -r -p "  Reconfigurar? [s/N] " RESP
    if [ "$RESP" != "s" ] && [ "$RESP" != "S" ]; then
      write_info "Mantendo credenciais existentes."
      DO_CREDS=false
    fi
  fi

  if [ "$DO_CREDS" = true ]; then
    write_step "🔑" "Atlassian (Confluence + Jira)"
    write_info "Obtenha o token em: https://id.atlassian.com/manage-profile/security/api-tokens"
    echo ""
    read -r -p "  URL Confluence (ex: https://empresa.atlassian.net): " ATL_URL
    read -r -p "  Email Atlassian: " ATL_USER
    read -r -s -p "  API Token: " ATL_TOKEN
    echo ""

    if [ -n "$ATL_URL" ] && [ -n "$ATL_USER" ]; then
      if [ -f "$CREDS_SCRIPT" ]; then
        TMP_JSON="$(mktemp).json"
        # Constrói o JSON via Python (evita problemas de escaping em bash)
        CONFLUENCE_URL="$ATL_URL" CONFLUENCE_USERNAME="$ATL_USER" CONFLUENCE_API_TOKEN="$ATL_TOKEN" \
        JIRA_URL="$ATL_URL" JIRA_USERNAME="$ATL_USER" JIRA_API_TOKEN="$ATL_TOKEN" \
        "$PYTHON_BIN" -c "
import json, os
fields = {k: os.environ[k] for k in (
    'CONFLUENCE_URL','CONFLUENCE_USERNAME','CONFLUENCE_API_TOKEN',
    'JIRA_URL','JIRA_USERNAME','JIRA_API_TOKEN')}
with open('$TMP_JSON', 'w', encoding='utf-8') as f:
    json.dump(fields, f)
"
        if "$PYTHON_BIN" "$CREDS_SCRIPT" setup --from-json "$TMP_JSON" >/dev/null 2>&1; then
          write_ok "Credenciais Atlassian salvas."
        else
          write_warn "Não foi possível salvar credenciais automaticamente."
          write_info "Execute manualmente: $PYTHON_BIN .agent/scripts/infra/kare_credentials.py setup"
        fi
        # O script Python já apaga o arquivo temporário; limpa se ainda existir
        [ -f "$TMP_JSON" ] && rm -f "$TMP_JSON"
        unset ATL_TOKEN
      else
        write_warn "Script de credenciais não encontrado."
        write_info "Execute: $PYTHON_BIN .agent/scripts/infra/kare_credentials.py setup"
      fi
    else
      write_warn "Credenciais Atlassian puladas. Configure depois com:"
      write_info "  $PYTHON_BIN .agent/scripts/infra/kare_credentials.py setup"
    fi
  fi
fi

# ──────────────────────────────────────── CONCLUSÃO ──────────────────────────
write_header "SETUP CONCLUÍDO"

printf "%s\n" "$CYAN"
cat <<EOF

  Próximos passos:

  1. Abra o workspace no VS Code:
     code "$WORKSPACE"

  2. Confirme que a extensão GitHub Copilot Chat está ativa.

  3. Abra o Copilot Chat e teste:
     /status

  4. Para iniciar o Context Engine (RAG semântico):
     python .agent/scripts/ai/kare_rag.py migrate

  5. Para configurar Atlassian depois:
     $PYTHON_BIN .agent/scripts/infra/kare_credentials.py setup

EOF
printf "%s\n" "$NC"

echo "  Documentação completa: README.md"
echo "  Suporte: use /status no Copilot Chat para verificar saúde do sistema."
echo ""
