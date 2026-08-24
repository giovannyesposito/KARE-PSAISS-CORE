---
name: quality-guardian-agenteval
description: >
  Avaliação automatizada de artefatos KARE (US, PRD, ACs, código, ADRs) com
  score objetivo e critérios configuráveis por tipo. Base técnica para o
  @quality-guardian avaliar qualidade sem intervenção humana. Framework: AutoGen.
sprint: 1
agente_destino: "@quality-guardian"
framework: AutoGen
referencia: "https://github.com/microsoft/autogen/blob/0.2/notebook/agenteval_cq_math.ipynb"
tools:
  - Read
  - Grep
  - Write
triggers:
  - "avaliação de artefatos"
  - "score de qualidade"
  - "agenteval"
  - "DoR score"
  - "DoD score"
  - "qualidade de story"
  - "qualidade de PRD"
  - "autoavaliação"
  - "validar artefato"
---

# Quality Guardian AgentEval — Avaliação Automatizada de Artefatos KARE

> **Sprint 1 — Fundação** | Framework: AutoGen | Agente: `@quality-guardian`

## Propósito

Avaliar objetivamente qualquer artefato KARE (US, PRD, AC, código, ADR) com um **score
de 0 a 100** usando critérios customizáveis, sem necessidade de revisão manual.

---

## Critérios por Tipo de Artefato

### User Story

| Critério | Peso | Descrição |
|---|---|---|
| **INVEST** | 30% | Independente, Negociável, Valiosa, Estimável, Small, Testável |
| **Formato** | 15% | "Como... quero... para..." presente |
| **ACs em Gherkin** | 25% | Cenários Given/When/Then completos |
| **DoR** | 20% | Todos os itens do checklist de DoR preenchidos |
| **Rastreabilidade** | 10% | ID de Epic/Feature vinculado |

### PRD

| Critério | Peso | Descrição |
|---|---|---|
| **Visão e Objetivos** | 20% | Objetivo claro, KPIs definidos |
| **Personas/Stakeholders** | 15% | Personas identificadas e descritas |
| **Requisitos** | 25% | Funcionais e não-funcionais cobertos |
| **Riscos** | 20% | RAID com severidade e mitigação |
| **Critérios de Sucesso** | 20% | Mensuráveis e com baseline |

### Código

| Critério | Peso | Descrição |
|---|---|---|
| **Lint** | 20% | Zero erros de lint |
| **Cobertura de Testes** | 30% | >= 80% de cobertura |
| **SOLID** | 20% | Princípios aplicados |
| **Segurança** | 20% | OWASP Top 10 verificado |
| **Documentação** | 10% | JSDoc/docstrings nas interfaces públicas |

---

## Implementação — Sistema de Avaliação

```python
from autogen import AssistantAgent, UserProxyAgent

# Configuração do avaliador
avaliador = AssistantAgent(
    name="ArtifactEvaluator",
    system_message="""Você é um avaliador de artefatos ágeis do projeto.
    Avalie o artefato recebido segundo os critérios INVEST, DoR/DoD e padrões KARE.
    Retorne SEMPRE um JSON com:
    {
      "score": 0-100,
      "criterios": {"nome": {"score": 0-100, "justificativa": "..."}},
      "aprovado": true/false,
      "bloqueadores": ["lista de problemas críticos"],
      "sugestoes": ["melhorias recomendadas"]
    }
    """,
    llm_config={"config_list": [{"model": "gpt-4"}]}
)

# Threshold de aprovação
THRESHOLD_APROVACAO = 70

def avaliar_artefato(conteudo: str, tipo: str) -> dict:
    """Avalia um artefato e retorna score + feedback."""
    criterios = CRITERIOS_POR_TIPO[tipo]
    prompt = f"Tipo: {tipo}\n\nArtefato:\n{conteudo}\n\nCritérios: {criterios}"
    resultado = avaliador.generate_reply(messages=[{"role": "user", "content": prompt}])
    return json.loads(resultado)
```

---

## Resultado — Formato de Saída

```json
{
  "artefato": "US-042 — Login OAuth B2B",
  "tipo": "user_story",
  "score": 82,
  "aprovado": true,
  "threshold": 70,
  "criterios": {
    "INVEST": {"score": 85, "justificativa": "Story independente e testável, estimável em 3SP"},
    "formato": {"score": 100, "justificativa": "Formato Como/Quero/Para correto"},
    "acs_gherkin": {"score": 75, "justificativa": "3 cenários OK, faltando cenário de erro de timeout"},
    "dor": {"score": 80, "justificativa": "DoR 8/10 itens preenchidos — falta critério de performance"},
    "rastreabilidade": {"score": 70, "justificativa": "Epic EP-AUTH presente, Feature faltando"}
  },
  "bloqueadores": [],
  "sugestoes": [
    "Adicionar cenário Gherkin para timeout de autenticação OAuth",
    "Vincular à Feature FT-AUTH-001 antes do refinamento"
  ]
}
```

---

## Integração com ORCHESTRATION_REPORT

```markdown
## AgentEval — Quality Score

| Artefato | Tipo | Score | Status | Bloqueadores |
|----------|------|-------|--------|--------------|
| US-042 | user_story | 82/100 | ✅ APROVADO | 0 |
| PRD INI-001 | prd | 91/100 | ✅ APROVADO | 0 |
| auth.service.ts | código | 68/100 | ❌ BLOQUEADO | 1 (cobertura < 80%) |

**Score Médio da Sessão:** 80/100 | Aprovados: 2/3
```

---

## Configuração por Projeto

O threshold e os pesos são configuráveis via `PROJECT_CONTEXT.md`:

```yaml
quality_gates:
  user_story_threshold: 70
  prd_threshold: 75
  code_threshold: 80
  enforce_dor: true
  enforce_gherkin: true
```

---

## Critérios de Aceite

- [ ] Score gerado para PRD, US, AC e código em <= 30s
- [ ] Critérios de avaliação configuráveis por tipo de artefato
- [ ] Score integrado ao ORCHESTRATION_REPORT
- [ ] Threshold de qualidade configurável (padrão: 70/100)
- [ ] Artefatos abaixo do threshold bloqueiam a delegação para @code-author
