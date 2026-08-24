---
description: "Verifica status de autorização de uma skill de alto risco antes de execução."
command: /guardrail-check
category: Security
disclaimer: "🔒 Consulta somente leitura — não altera nenhuma autorização. Exibe nível de risco, TTL restante e operador que autorizou. Tempo: < 5s."
---

# /guardrail-check — Verificar Status de Autorização

$ARGUMENTS

---

## O que faz

Consulta o `guardrail_gate.py` e exibe o status de autorização de uma skill específica
(ou de todas, se nenhuma for informada). Mostra nível de risco, validade da autorização
e o que fazer para ativar caso não esteja autorizada.

---

## Uso

```
/guardrail-check
/guardrail-check code-author-autogen
/guardrail-check agent-builder-autogen
/guardrail-check delivery-observer-sql
/guardrail-check rag-continual-learning
/guardrail-check security-red-team
/guardrail-check azure-iac-engineer
/guardrail-check gcp-analytics-agent
```

---

## Skills Monitoradas

| Skill | Nível | TTL |
|---|---|---|
| `code-author-autogen` | 🔴 CRITICAL | 60 min |
| `agent-builder-autogen` | 🔴 CRITICAL | 30 min |
| `rag-continual-learning` | 🔴 CRITICAL | 120 min |
| `delivery-observer-sql` | 🔴 CRITICAL | 30 min |
| `security-red-team` | 🟠 HIGH | 120 min |
| `azure-iac-engineer` | 🟠 HIGH | 60 min |
| `gcp-analytics-agent` | 🟠 HIGH | 60 min |
| `agent-simulation-testing` | 🟡 MEDIUM | 120 min |

---

## Passos de Execução

1. Identificar skill alvo a partir de `$ARGUMENTS`
   - Se vazio → executar para todas as skills do registro
   - Se informada → verificar apenas a skill especificada

2. Executar verificação:

```powershell
# Skill específica
python .agent/scripts/guards/guardrail_gate.py check <skill-name>

# Todas as skills
python .agent/scripts/guards/guardrail_gate.py status
```

3. Interpretar o resultado e exibir ao usuário:
   - ✅ **Autorizada** → informar validade e operador
   - ❌ **Não autorizada** → sugerir `/guardrail-approve <skill-name>`
   - ⌛ **Expirada** → informar quando expirou, sugerir renovação
   - ⛔ **Ambiente incorreto** → instruir como definir `$env:KARE_ENV`

4. Se alguma skill CRITICAL estiver não autorizada, alertar:
   > ⚠️ A skill `<nome>` está BLOQUEADA. Use `/guardrail-approve <nome>` antes de prosseguir.

---

## Saídas Esperadas

- Status de cada skill (✅ / ❌ / ⌛)
- Validade da autorização (se ativa)
- Instrução de como autorizar (se bloqueada)
