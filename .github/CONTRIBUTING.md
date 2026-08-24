# Contributing to KARE-SPEC

Obrigado por contribuir! Este guia explica como adicionar agentes, skills e workflows.

## Quick Start

```powershell
git clone https://github.com/giovannyesposito/KARE-PSAISS-CORE.git
cd KARE-PSAISS-CORE
.\setup.ps1
code .
```

Mac/Linux: `./setup.sh` no lugar de `.\setup.ps1`.

## Estrutura de Contribuição

| O que criar | Onde | Padrão |
|---|---|---|
| Novo agente | `.agent/agents/<nome>.md` | Copiar template de agente existente |
| Nova skill | `.agent/skills/<nome>/SKILL.md` | Padrão SKILL.md |
| Novo workflow | `.agent/workflows/<nome>.prompt.md` | Frontmatter com `description`, `command`, `category` |
| Novo script | `.agent/scripts/<nome>.py` | Verificar SCRIPTS-MANIFEST.md antes |

## Regras

- Todo script `.py` novo deve ser registrado em `.agent/scripts/SCRIPTS-MANIFEST.md`
- Workflows devem ter `description` entre aspas duplas no frontmatter YAML
- Artefatos gerados vão em `_outputs/` — nunca em `uploads/`
- Credenciais nunca em texto plano — use `kare_credentials.py`

## Como Testar

### Testes automatizados (obrigatório antes de abrir PR)

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v
```

Cobertura atual: `kare_credentials.py` (cofre AES-256-GCM), senha da base RAG
perene em `kare_rag.py`, `sql_guard.py`/`tool_guard.py`/`loop_guard.py`
(guardrails de governança), `secret_scan.py` (varredura de credenciais), e
integridade de configuração (todo `.json` faz parse, todo agente/workflow
tem frontmatter válido, `SKILL-REGISTRY.json` sem paths quebrados).

O CI (`.github/workflows/ci.yml`) roda essa mesma suíte em matrix
Ubuntu+Windows × Python 3.10/3.11/3.12, mais uma varredura de credenciais em
texto plano em todo o repositório (`secret-scan`) — defesa em profundidade
além do hook local de pre-commit.

### Validação manual do sistema de agentes

```
/status          # Verifica saúde do sistema
/quality --story <ID>  # Valida story
```

## Licença

Ao contribuir, você concorda que sua contribuição será licenciada sob os
mesmos termos do projeto: [MIT](../LICENSE). O nome "KARE-SPEC" e a marca
têm termos próprios, ver [NOTICE.md](../NOTICE.md).
