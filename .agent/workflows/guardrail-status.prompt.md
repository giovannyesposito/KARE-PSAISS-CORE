---
description: "Exibe painel completo de todas as autorizações ativas, expiradas e bloqueadas no KARE."
command: /guardrail-status
category: Security
disclaimer: "🔒 Somente leitura — não altera autorizações. Exibe snapshot completo do estado de segurança. Tempo: < 5s."
---

# /guardrail-status — Painel de Autorizações Ativas

$ARGUMENTS

---

## O que faz

Exibe o estado atual de **todas as skills monitoradas pelo Guardrail Gate**: quais estão
autorizadas, quais estão bloqueadas, quando expiram e quem autorizou cada uma.
Equivalente a um dashboard de segurança operacional do KARE.

---

## Uso

```
/guardrail-status
/guardrail-status --detail
```

---

## Passos de Execução

1. Executar o comando de status:

```powershell
python .agent/scripts/guards/guardrail_gate.py status
```

2. Formatar e apresentar o resultado em tabela:

```
────────────────────────────────────────────────────────────────
  KARE GUARDRAIL STATUS — <timestamp>
────────────────────────────────────────────────────────────────
  [CRITICAL] code-author-autogen          ❌ não autorizado
  [CRITICAL] agent-builder-autogen        ✅ válida  (expira 2026-05-24T18:30Z)
  [CRITICAL] rag-continual-learning       ⌛ EXPIRADA
  [CRITICAL] delivery-observer-sql        ✅ válida  (expira 2026-05-24T17:00Z)
  [HIGH    ] security-red-team            ❌ não autorizado
  [HIGH    ] azure-iac-engineer           ❌ não autorizado
  [HIGH    ] gcp-analytics-agent          ❌ não autorizado
  [MEDIUM  ] agent-simulation-testing     ✅ válida  (expira 2026-05-24T20:00Z)
────────────────────────────────────────────────────────────────
```

3. Se `--detail` informado → para cada skill autorizada, exibir também:
   - Operador que autorizou
   - Motivo registrado
   - Timestamp da autorização original

4. Resumo executivo ao final:
   - Total autorizado: N skills
   - Total bloqueado: N skills
   - Total expirado: N skills (sugerir renovação)

5. Se houver skills CRITICAL **não autorizadas**, emitir alerta:
   > ⚠️ N skill(s) CRITICAL bloqueada(s). Use `/guardrail-approve <nome>` para autorizar antes de usar.

---

## Saídas Esperadas

- Tabela de status de todas as 8 skills monitoradas
- Resumo executivo de autorização
- Alertas para skills expiradas ou bloqueadas
