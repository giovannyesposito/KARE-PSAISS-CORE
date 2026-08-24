---
description: "Comprime sessão longa gerando checkpoint estruturado com decisões, ações e próximos passos"
category: "Operations"
command: "/compress-session"
disclaimer: "📋 Gera checkpoint em memories/session/. Não apaga histórico. Rebase de contexto ativo após execução."
orchestrator: kare-orchestrator
orchestrator-mode: sequential
agents-required:
  - primary: kare-orchestrator
context-required:
  - PROJECT_CONTEXT.md
  - ORCHESTRATION_REPORT.md
skill: session-compressor
---

# /compress-session — Compressão de Sessão Longa

> **Ativa o skill `session-compressor`** para gerar um checkpoint estruturado
> da sessão corrente e rebaser o contexto do agente.

---

## Gatilhos de Ativação

- Usuário executa `/compress-session` manualmente
- `loop_guard.py` emite `SessionTimeoutError` (sessão > 120 min)
- Agente detecta degradação de qualidade de respostas por excesso de contexto

---

## O Que Este Comando Faz

```
1. Coleta estado bruto da sessão (PROJECT_CONTEXT.md, ORCHESTRATION_REPORT.md, arquivos modificados)
2. Extrai: decisões tomadas, ações executadas, estado atual, próximos passos, riscos
3. Gera: memories/session/checkpoint-<YYYYMMDD-HHmm>.md
4. Emite instrução de rebase de contexto
5. Reseta loop_guard (se ativo) para evitar falso timeout pós-checkpoint
```

---

## Saídas

| Artefato | Localização |
|---|---|
| Checkpoint de sessão | `memories/session/checkpoint-<YYYYMMDD-HHmm>.md` |
| Notificação de rebase | Exibida no chat |

---

## Protocolo de Execução

O orchestrator invoca o skill `session-compressor`:

```
@kare-orchestrator → session-compressor
  └─ Passo 1: Coletar estado bruto
  └─ Passo 2: Extrair estrutura do checkpoint
  └─ Passo 3: Gerar arquivo em memories/session/
  └─ Passo 4: Emitir instrução de rebase
  └─ Passo 5: Resetar loop_guard
```

---

## Instrução de Rebase (emitida após geração)

```
✅ Checkpoint salvo: memories/session/checkpoint-<YYYYMMDD-HHmm>.md

🔄 REBASE DE CONTEXTO ATIVO:
   Use SOMENTE o checkpoint como baseline de contexto daqui em diante.
   Em caso de dúvida sobre decisões passadas, consulte o checkpoint.
```

---

## Referência

Skill completo: `.agent/skills/session-compressor/SKILL.md`
