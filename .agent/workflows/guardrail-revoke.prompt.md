---
description: "Revoga imediatamente uma autorização ativa de skill de alto risco antes do TTL expirar."
command: /guardrail-revoke
category: Security
disclaimer: "⚡ Este comando REVOGA IMEDIATAMENTE uma autorização ativa! A skill ficará bloqueada até nova aprovação. Ação registrada no audit log. Use em caso de erro de autorização ou mudança de contexto."
---

# /guardrail-revoke — Revogar Autorização Ativa

$ARGUMENTS

---

## Disclaimer Obrigatório

```
🎬 DISCLAIMER: /guardrail-revoke
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Você está prestes a REVOGAR uma autorização ativa.
A skill ficará imediatamente BLOQUEADA após esta ação.
Qualquer execução em andamento NÃO será interrompida — apenas
novas execuções serão bloqueadas.

A revogação será registrada no audit log.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Confirma a revogação? [Sim/Não]
```

---

## O que faz

Cancela imediatamente uma autorização ativa no Guardrail Gate, bloqueando
a skill antes do TTL natural expirar. Útil quando:

- A operação foi autorizada por engano
- O contexto da operação mudou (ex: sprint encerrado)
- Uma sessão de sandbox deve ser encerrada imediatamente
- Suspeita de uso indevido de uma skill autorizada

---

## Uso

```
/guardrail-revoke code-author-autogen
/guardrail-revoke agent-builder-autogen
/guardrail-revoke delivery-observer-sql
/guardrail-revoke rag-continual-learning
/guardrail-revoke security-red-team
/guardrail-revoke azure-iac-engineer
/guardrail-revoke gcp-analytics-agent
```

---

## Passos de Execução

1. Extrair `<skill-name>` de `$ARGUMENTS`
   - Se não informado → listar skills atualmente autorizadas e perguntar qual revogar

2. Verificar se há autorização ativa:

```powershell
python .agent/scripts/guards/guardrail_gate.py check <skill-name>
```

3. Se não houver autorização ativa → informar e encerrar
4. Se houver → exibir disclaimer e aguardar confirmação do usuário

5. Após confirmação:

```powershell
python .agent/scripts/guards/guardrail_gate.py revoke <skill-name>
```

6. Confirmar revogação e informar:
   - Skill agora BLOQUEADA
   - Para reautorizar: `/guardrail-approve <skill-name> --reason "<motivo>"`
   - Registro no audit log: `.agent/.guardrails/audit.jsonl` (evento: `REVOKED`)

---

## Cenários de Uso

| Cenário | Ação |
|---|---|
| Autorizou `code-author-autogen` mas a task foi cancelada | `/guardrail-revoke code-author-autogen` |
| Sprint encerrou antes do TTL do `delivery-observer-sql` | `/guardrail-revoke delivery-observer-sql` |
| Sessão `security-red-team` concluída antes do tempo | `/guardrail-revoke security-red-team` |
| Agente gerado pelo `agent-builder` apresentou problema | `/guardrail-revoke agent-builder-autogen` |

---

## Saídas Esperadas

- Confirmação de revogação com timestamp
- Skill marcada como BLOQUEADA no status
- Entry `REVOKED` no audit log
