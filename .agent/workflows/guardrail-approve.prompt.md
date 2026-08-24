---
description: "Autoriza execução de operação de alto risco em uma skill KARE. Requer motivo explícito."
command: /guardrail-approve
category: Security
disclaimer: "⚡ Este comando CONCEDE AUTORIZAÇÃO para operações de alto risco! Registra operador + motivo + timestamp. Autorização expira automaticamente (TTL por skill). IRREVERSÍVEL até o TTL ou revogação manual."
---

# /guardrail-approve — Autorizar Operação de Alto Risco

$ARGUMENTS

---

## Disclaimer Obrigatório

```
🎬 DISCLAIMER: /guardrail-approve
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Você está prestes a AUTORIZAR uma operação de alto risco no KARE.
Esta autorização será registrada no audit log com:
  → Sua identidade ($USERNAME)
  → Motivo informado
  → Timestamp e TTL de expiração

A skill só poderá ser executada após esta autorização.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Deseja prosseguir com a autorização? [Sim/Não]
```

---

## O que faz

Registra autorização explícita de operador humano para uma skill de alto risco.
Sem esta autorização, a skill é bloqueada automaticamente ao tentar executar.

---

## Uso

```
/guardrail-approve code-author-autogen "TDD para US-42 — sprint 6"
/guardrail-approve agent-builder-autogen "Criar agente log-analyzer — aprovado em reunião 24/05"
/guardrail-approve rag-continual-learning "Sync programado Confluence B2B do cliente — semanal"
/guardrail-approve delivery-observer-sql "Consulta métricas sprint 8 — relatório executivo"
/guardrail-approve security-red-team "Pentest OWASP LLM10 — staging — aprovado por tech-lead"
/guardrail-approve azure-iac-engineer "Deploy INI-004 infra AKS — revisado por arquiteto"
/guardrail-approve gcp-analytics-agent "Treino modelo churn — dataset sintético — aprovado"
```

---

## Pré-Requisitos por Skill

| Skill | Pré-requisito adicional |
|---|---|
| `security-red-team` | `$env:KARE_ENV = "staging"` obrigatório antes de aprovar |
| `azure-iac-engineer` | Ter revisado o `terraform plan` antes de autorizar o `apply` |
| `gcp-analytics-agent` | Confirmar que `GCP_PROJECT_ID` aponta para ambiente de staging |
| `code-author-autogen` | Confirmar que o sandbox está isolado (sem rede externa) |

---

## Passos de Execução

1. Extrair `<skill-name>` e `<motivo>` de `$ARGUMENTS`
   - Se faltarem → perguntar ao usuário antes de prosseguir

2. Verificar pré-requisitos da skill (tabela acima)
   - Se `security-red-team` → verificar `$env:KARE_ENV`
   - Se `azure-iac-engineer` → confirmar que plan foi revisado

3. Exibir disclaimer completo com detalhes da operação e aguardar confirmação

4. Após confirmação **explícita** do usuário:

```powershell
python .agent/scripts/guards/guardrail_gate.py approve <skill-name> --reason "<motivo>" --yes
```

5. Confirmar registro e informar:
   - Validade da autorização (timestamp de expiração)
   - Como verificar: `/guardrail-check <skill-name>`
   - Como revogar: `/guardrail-revoke <skill-name>`

---

## TTL por Skill (Expiração Automática)

| Skill | TTL | Motivo |
|---|---|---|
| `agent-builder-autogen` | 30 min | Revisão deve ser imediata após geração |
| `delivery-observer-sql` | 30 min | Janela de consulta pontual |
| `code-author-autogen` | 60 min | Sessão de TDD típica |
| `azure-iac-engineer` | 60 min | Apply deve ocorrer logo após plan |
| `gcp-analytics-agent` | 60 min | Job de compute tem duração definida |
| `security-red-team` | 120 min | Ciclo de pentest completo |
| `rag-continual-learning` | 120 min | Sync periódico |
| `agent-simulation-testing` | 120 min | Suíte de simulação completa |

---

## Saídas Esperadas

- ✅ Confirmação de autorização registrada
- Timestamp de expiração
- Entry no audit log: `.agent/.guardrails/audit.jsonl`
