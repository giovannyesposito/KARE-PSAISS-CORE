---
name: agent-builder-autogen
description: >
  Meta-agente que cria novos agentes KARE a partir de descrições em linguagem
  natural: gera o arquivo .agent.md, configura frontmatter, define tools
  permitidas (Tool Guard) e registra no SKILL-REGISTRY.json. Framework: AutoGen.
sprint: 5
agente_destino: "@kare-orchestrator"
framework: AutoGen
referencia: "https://github.com/microsoft/autogen/blob/0.2/notebook/agentchat_agentbuilder.ipynb"
tools:
  - Read
  - Grep
  - Write
  - Edit
triggers:
  - "criar novo agente"
  - "AgentBuilder"
  - "meta-agente"
  - "novo skill"
  - "configurar agente"
  - "registrar agente"
  - "gerar .agent.md"
---

# Agent Builder AutoGen — Meta-Agente que Cria Novos Agentes

> **Sprint 5 — Orchestrator Core** | Framework: AutoGen | Agente: `@kare-orchestrator`

## Propósito

Permitir que o `@kare-orchestrator` crie e configure novos agentes KARE
dinamicamente a partir de uma descrição em linguagem natural — com toda a
estrutura de segurança (Tool Guard) e registro (SKILL-REGISTRY) automáticos.

---

## O Que o AgentBuilder Gera

Para cada novo agente solicitado, o builder produz:

1. **`.agent/<nome-do-agente>.agent.md`** — Definição completa do agente
2. **`.agent/skills/<nome>/SKILL.md`** — Skill associada (se aplicável)
3. **Entry no `SKILL-REGISTRY.json`** — Registro centralizado
4. **Atualização no `Tool Guard`** — Permissões de ferramentas

---

## Fluxo de Criação

```
Usuário: "Crie um agente para análise de logs do Elastic"
       │
       ▼
[INTERVIEW] — Perguntas de clarificação (máx 5)
  ├── Domínio do agente (DevOps, QA, Product, etc.)
  ├── Ferramentas necessárias
  ├── Inputs e outputs esperados
  ├── Agente que delega para este
  └── Constraints de segurança
       │
       ▼
[DESIGN] — Desenhar perfil do agente
  ├── Role + Goal + Backstory
  ├── Tools matrix (Tool Guard)
  └── Trigger keywords
       │
       ▼
[GENERATE] — Criar artefatos
  ├── .agent.md
  ├── SKILL.md
  └── Atualizar SKILL-REGISTRY.json
       │
       ▼
[VALIDATE] — Verificar conformidade KARE
  ├── YAML válido?
  ├── Tools declaradas no Tool Guard?
  └── Triggers únicos?
       │
       ▼
[CONFIRM] → Apresentar ao usuário para aprovação
```

---

## Template Gerado — .agent.md

```yaml
---
name: elastic-observability
description: "Agente especialista em observabilidade via Elastic Stack"
role: "Elastic Observability Engineer"
goal: "Analisar logs, métricas e traces do stack do projeto no Elastic Search"
backstory: "SRE sênior com 5 anos em Elastic Stack em ambiente de telecom"
sprint: 7
tools:
  - Read
  - Grep
triggers:
  - "logs do elastic"
  - "observabilidade"
  - "kibana dashboard"
  - "alertas ELK"
constraints:
  - "Read-only em produção"
  - "Nunca expor IPs ou endpoints internos"
parent_agent: "@delivery-observer"
---

# Elastic Observability Agent

[Corpo do agente gerado automaticamente pelo AgentBuilder]
```

---

## Entrevista de Criação

```python
PERGUNTAS_ENTREVISTA = [
    "Qual é o domínio principal deste agente? (ex: DevOps, QA, Product)",
    "Quais ferramentas ele precisa? (Read, Write, Bash, MCP, etc.)",
    "Quem delega tarefas para ele? (qual agente pai)",
    "Quais são os 3 principais triggers (palavras-chave que o ativam)?",
    "Há restrições de segurança? (ex: nunca em produção, read-only)",
]

def entrevistar_usuario(requisito: str) -> dict:
    """Coleta informações para construir o agente."""
    respostas = {}
    for pergunta in PERGUNTAS_ENTREVISTA:
        resposta = hitl_perguntar(pergunta)  # Escala ao humano
        respostas[pergunta] = resposta
    return respostas
```

---

## Guardrail — Autorização + HITL Gate Obrigatório

> ⛔ **NÍVEL: CRÍTICO** — Esta skill cria agentes autônomos com permissões de ferramenta.
> Um agente criado com `tools: [Bash, Write, Edit]` pode ter acesso irrestrito ao sistema.
> **Dupla barreira: autorização prévia + revisão humana do artefato gerado.**

### Ativar antes de usar

```powershell
# 1. Verificar status
python .agent/scripts/guards/guardrail_gate.py check agent-builder-autogen

# 2. Autorizar (expira em 30 min — revisão deve ser imediata)
python .agent/scripts/guards/guardrail_gate.py approve agent-builder-autogen \
  --reason "Criar agente <nome> para <domínio> — aprovado em reunião <data>"
```

### HITL Gate — Revisão Obrigatória do Artefato

Após gerar o `.agent.md`, o agente **DEVE pausar e exibir**:

```
⚠️  HITL GATE — Revisão Obrigatória Antes de Registrar Agente
══════════════════════════════════════════════════════════════
Agente gerado: <nome>
Tools solicitadas: <lista>

⚠️  WHITELIST de tools permitidas para agentes gerados automaticamente:
   ✅ Permitidas: Read, Grep, Write
   ❌ Bloqueadas: Bash, Edit, Agent, Browser

Artefato gerado em: .agent/<nome>.agent.md
→ Revisar antes de confirmar ativação.

Deseja ATIVAR este agente? [sim/não]:
```

### Integração no código

```python
from guardrail_gate import require_authorization, GuardrailDenied

require_authorization("agent-builder-autogen")

# Após gerar o .agent.md — pausa obrigatória
print("⚠️  HITL GATE — Revise o artefato gerado antes de continuar.")
confirm = input("Ativar agente? [sim/não]: ").strip().lower()
if confirm not in ("sim", "s"):
    print("❌ Ativação cancelada. Artefato salvo mas não registrado.")
    sys.exit(0)

# Só então registrar no SKILL-REGISTRY e Tool Guard
```

### Whitelist de Tools para Agentes Gerados

```python
ALLOWED_TOOLS_FOR_GENERATED = ["Read", "Grep", "Write"]
# Qualquer outro tool exige aprovação manual adicional no .agent.md
```

---

## Critérios de Aceite

- [ ] Agente criado com YAML válido e sem campos obrigatórios faltando
- [ ] Tool Guard atualizado com permissões do novo agente
- [ ] SKILL-REGISTRY.json atualizado automaticamente
- [ ] Entrevista de clarificação antes de gerar (máx 5 perguntas)
- [ ] Aprovação humana obrigatória antes de salvar os artefatos
- [ ] **Guardrail verificado: autorização ativa antes de qualquer geração**
- [ ] **HITL Gate exibido com conteúdo completo do .agent.md para revisão**
- [ ] **Tools do agente gerado restritas à whitelist [Read, Grep, Write]**
- [ ] **Audit log registra: aprovação + identidade do operador + timestamp**
