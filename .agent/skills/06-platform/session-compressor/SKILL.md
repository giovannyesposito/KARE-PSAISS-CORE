---
name: session-compressor
description: >
  Comprime sessões longas (+2h) gerando um checkpoint estruturado em
  memories/session/. Salva: decisões tomadas, ações executadas, estado atual
  e próximos passos. Use quando o contexto parecer "pesado" ou ao receber
  aviso de timeout de sessão do loop_guard. Invoke com /compress-session.
triggers:
  - "/compress-session"
  - "comprimir sessão"
  - "checkpoint de sessão"
  - "contexto muito longo"
  - "session timeout"
  - "KARE_SESSION_TIMEOUT"
  - "sessão travada"
  - "resumir o que foi feito"
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
---

# Session Compressor Skill

## Objetivo

Evitar context drift em sessões longas comprimindo o estado corrente em um
checkpoint estruturado. O agente usa o checkpoint como novo baseline de contexto,
descartando o histórico bruto anterior sem perder rastreabilidade.

---

## Quando Ativar

- Usuário executa `/compress-session`
- `loop_guard.py` emite `SessionTimeoutError` (sessão > 120 min)
- Agente percebe respostas degradando por excesso de contexto
- Antes de trocar de tarefa num fluxo muito longo

---

## Protocolo de Compressão (5 Passos)

### Passo 1 — Coletar Estado Bruto

Antes de gerar o checkpoint, leia:

```
□ PROJECT_CONTEXT.md (se existir)
□ BACKLOG.md (se existir)
□ Último ORCHESTRATION_REPORT.md gerado
□ Arquivos modificados/criados na sessão (listar por Glob)
□ ADRs e decisões referenciadas na sessão
```

### Passo 2 — Extrair Estrutura do Checkpoint

Organize o que foi coletado em 6 blocos obrigatórios:

```
1. IDENTIDADE DA SESSÃO     — ID, agente principal, data/hora, duração estimada
2. CONTEXTO DO PROJETO      — Nome, iniciativa(s), trilha BF/GF
3. DECISÕES TOMADAS         — Lista numerada de cada decisão + razão + data
4. AÇÕES EXECUTADAS         — O que foi criado/editado/deletado (com caminho)
5. ESTADO ATUAL             — Onde estamos agora (o que está completo, em andamento)
6. PRÓXIMOS PASSOS          — Sequência priorizada do que falta fazer
```

### Passo 3 — Gerar Arquivo de Checkpoint

**Destino:** `memories/session/checkpoint-<YYYYMMDD-HHmm>.md`

**Template obrigatório:**

```markdown
# Checkpoint de Sessão — <YYYYMMDD-HHmm>

> **Agente:** @kare-orchestrator | **Duração:** ~Xh | **Data:** DD/MM/YYYY HH:mm

---

## 1. Identidade da Sessão

| Campo | Valor |
|---|---|
| ID da sessão | checkpoint-<YYYYMMDD-HHmm> |
| Agente principal | @[nome] |
| Data/hora | <timestamp> |
| Duração estimada | ~Xh Ymin |
| Trilha | BF / GF |

---

## 2. Contexto do Projeto

- **Projeto/Iniciativa:** [Nome ou INI-XXX]
- **Objetivo da sessão:** [Em 1-2 frases]
- **Arquivos de contexto base:** [lista]

---

## 3. Decisões Tomadas

| # | Decisão | Razão | Artefato |
|---|---|---|---|
| 1 | [decisão] | [razão] | [arquivo ou N/A] |
| 2 | ... | ... | ... |

---

## 4. Ações Executadas

| Tipo | Arquivo/Recurso | Detalhe |
|---|---|---|
| CRIADO | [caminho] | [descrição] |
| EDITADO | [caminho] | [o que mudou] |
| DELETADO | [caminho] | [por quê] |
| PUBLICADO | [URL Confluence] | [página] |

---

## 5. Estado Atual

### ✅ Completo
- [Item 1]
- [Item 2]

### ⏳ Em Andamento
- [Item 1 — parcialmente concluído, falta: X]

### 🔴 Bloqueado
- [Item 1 — bloqueador: Y]

---

## 6. Próximos Passos

> Sequência priorizada para retomar o trabalho após este checkpoint.

1. [Próximo passo imediato]
2. [Segundo passo]
3. [Terceiro passo]
4. ...

---

## 7. Riscos e Alertas

> Riscos identificados na sessão que o próximo agente/operador deve conhecer.

- ⚠️ [Risco 1]
- ⚠️ [Risco 2]

---

*Gerado automaticamente pelo session-compressor KARE | v1.0.0*
```

### Passo 4 — Instrução de Rebase de Contexto

Após salvar o checkpoint, emita explicitamente ao agente/usuário:

```
✅ Checkpoint salvo: memories/session/checkpoint-<YYYYMMDD-HHmm>.md

🔄 REBASE DE CONTEXTO ATIVO:
   A partir de agora, use SOMENTE o checkpoint acima como contexto de sessão.
   Descarte o histórico anterior de conversação como baseline.
   Em caso de dúvida sobre decisões passadas, consulte o checkpoint.

📋 Próximo passo sugerido: [Passo 1 da seção "Próximos Passos"]
```

### Passo 5 — Registrar Compressão no Loop Guard

Se `loop_guard.py` estiver ativo, resetar a sessão para evitar falso positivo
de timeout após o checkpoint:

```python
from loop_guard import get_session_tracker
tracker = get_session_tracker()
tracker.reset_all()  # Nova contagem após checkpoint
```

---

## Regras Inegociáveis

| Regra | Descrição |
|---|---|
| ✅ Nunca apagar contexto real | O checkpoint ADICIONA um arquivo. Nada é deletado. |
| ✅ Sempre listar ações executadas | Rastreabilidade total do que foi feito |
| ✅ Decisões com razão | Cada decisão documenta o "por quê" |
| ❌ Não omitir itens em andamento | Estado parcial é mais importante que completo |
| ❌ Não inventar próximos passos | Extrair do estado real — não especular |

---

## Integração com Outros Componentes

### Com `loop_guard.py`
```
SessionTimeoutError disparada
  → session-compressor ativado automaticamente
  → Checkpoint gerado
  → loop_guard.reset_all() chamado
  → Sessão retomada com contexto limpo
```

### Com `tool_guard.py`
```
ToolPermissionError no audit log
  → session-compressor inclui na seção "Riscos e Alertas"
  → Próximos passos incluem: revisar permissões do agente [X]
```

### Com `ORCHESTRATION_REPORT.md`
```
Último ORCHESTRATION_REPORT.md
  → Usado como fonte primária para "Ações Executadas"
  → Seção 3 (Decisões) extraída do report
```

---

## Exemplo de Saída

```
✅ Checkpoint gerado: memories/session/checkpoint-20260422-1530.md

📊 Resumo da compressão:
   • Duração da sessão: ~2h 35min
   • Decisões registradas: 7
   • Arquivos criados/editados: 12
   • Itens completos: 5/8
   • Próximo passo: Implementar gap #3 (session-compressor skill)

🔄 Contexto rebased. Use o checkpoint como baseline daqui em diante.
```

---

## Referência Rápida — Gatilhos de Ativação

```
/compress-session                     → Compressão manual pelo usuário
loop_guard.SessionTimeoutError        → Compressão automática por timeout (120 min)
Agente detecta degradação de contexto → Compressão proativa (opcional)
Troca de tarefa em sessão longa       → Checkpoint antes de mudar foco
```

---

*Skill version: 1.0.0 | Criado: 2026-04-22 | Prioridade: HIGH*
