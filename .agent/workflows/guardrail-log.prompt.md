---
description: "Exibe audit log completo de autorizações, revogações e execuções de skills de alto risco."
command: /guardrail-log
category: Security
disclaimer: "🔒 Somente leitura — visualização do log de auditoria. Inclui autorizações, revogações, execuções permitidas e bloqueios. Tempo: < 5s."
---

# /guardrail-log — Audit Log de Autorizações e Operações

$ARGUMENTS

---

## O que faz

Exibe o histórico completo de eventos do Guardrail Gate: quem autorizou o quê,
quando operações foram executadas ou bloqueadas, e revogações manuais.
Essencial para auditoria de segurança e rastreabilidade operacional.

---

## Uso

```
/guardrail-log
/guardrail-log --last 10
/guardrail-log --last 50
/guardrail-log --skill code-author-autogen
/guardrail-log --sql
```

---

## Tipos de Eventos no Log

| Evento | Significado |
|---|---|
| `AUTHORIZED` | Operador autorizou a skill via `approve` |
| `ALLOWED` | Skill executada com autorização válida |
| `DENIED` | Execução bloqueada — sem autorização |
| `EXPIRED` | Autorização expirou no momento da verificação |
| `REVOKED` | Operador revogou a autorização manualmente |
| `BLOCKED_ENV` | Ambiente incorreto (ex: `security-red-team` fora de staging) |
| `CANCELLED` | Operador cancelou no prompt interativo |
| `ALLOWED_NO_CONFIRM` | Skill executada sem necessidade de confirmação (MEDIUM) |

---

## Passos de Execução

1. Extrair parâmetros de `$ARGUMENTS`:
   - `--last N` → número de entradas (padrão: 20)
   - `--skill <nome>` → filtrar por skill específica
   - `--sql` → exibir log de queries SQL (`sql_audit.jsonl`)

2. Executar o comando de log:

```powershell
# Audit log de autorizações (padrão)
python .agent/scripts/guards/guardrail_gate.py log --last 20

# Log de queries SQL
python .agent/scripts/guards/sql_guard.py log --last 20
```

3. Para filtro por skill (`--skill`), processar output e exibir apenas eventos da skill especificada

4. Formatar e apresentar ao usuário:

```
  2026-05-24T14:30:15Z  [AUTHORIZED         ] code-author-autogen
  2026-05-24T14:31:02Z  [ALLOWED            ] code-author-autogen
  2026-05-24T14:31:02Z  [ALLOWED            ] code-author-autogen
  2026-05-24T15:45:00Z  [DENIED             ] agent-builder-autogen
  2026-05-24T16:00:10Z  [AUTHORIZED         ] delivery-observer-sql
  2026-05-24T16:00:45Z  [ALLOWED            ] delivery-observer-sql
  2026-05-24T16:30:10Z  [EXPIRED            ] delivery-observer-sql
  2026-05-24T17:10:00Z  [REVOKED            ] code-author-autogen
  2026-05-24T17:22:00Z  [BLOCKED_ENV        ] security-red-team
```

5. Resumo ao final:
   - Total de autorizações: N
   - Total de bloqueios (DENIED + BLOCKED_ENV): N
   - Total de revogações: N
   - Skill com mais bloqueios: `<nome>`

---

## Arquivos de Log

| Arquivo | Conteúdo |
|---|---|
| `.agent/.guardrails/audit.jsonl` | Eventos Guardrail Gate (autorizações, bloqueios, revogações) |
| `.agent/.guardrails/authorizations.jsonl` | Estado atual das autorizações ativas |
| `.agent/.guardrails/sql_audit.jsonl` | Queries SQL executadas via `sql_guard.py` |

---

## Saídas Esperadas

- Lista de eventos cronológica
- Resumo executivo com contagem por tipo de evento
- Identificação de padrões suspeitos (ex: muitos DENIED para mesma skill)
