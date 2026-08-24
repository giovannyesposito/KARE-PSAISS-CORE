---
name: test-artifact-generation
supersedes: testing-patterns
description: >
  Geração automática de Test Plans, Test Cases e relatórios de cobertura.
  Suporta BDD (Gherkin), test pyramid e estratégias por tipo de projeto.
  Detecta gaps de cobertura analisando stories e AC.
triggers:
  - "test plan"
  - "plano de testes"
  - "test cases"
  - "casos de teste"
  - "BDD"
  - "test pyramid"
  - "/gen-testplan"
---

# Test Artifact Generation Skill

## Test Pyramid Strategy

```
           /\
          /E2E\          (5-10%) — Cenários críticos de negócio
         /──────\
        /Integr. \       (20-30%) — Contratos entre componentes
       /──────────\
      / Unit Tests \     (60-70%) — Lógica de negócio isolada
     /──────────────\
```

Ajuste por tipo de projeto:
- **Greenfield**: siga a pirâmide (TDD puro)
- **Brownfield**: priorize integração e E2E primeiro (para estabilizar legado)

---

## Template — TEST_PLAN.md

```markdown
# Test Plan — [Feature/Release]
<!-- DRAFT v1 | Gerado por KARE -->

## Escopo
- **Incluído**: [o que será testado]
- **Excluído explicitamente**: [o que NÃO será testado neste plano]
- **Stories cobertas**: STORY-XXX, STORY-XXX

## Estratégia

### Tipos de Teste
| Tipo | Ferramenta | Responsável | Gate |
|------|-----------|-------------|------|
| Unitário | [Jest/pytest/JUnit] | Dev | Sprint Gate |
| Integração | [Testcontainers/Supertest] | Dev | Sprint Gate |
| E2E | [Playwright/Cypress] | QA/Dev | Release Gate |
| Performance | [k6/Locust] | Dev/Infra | Release Gate |
| Segurança | [SAST: SonarQube] | Dev | Sprint Gate |

### Ambientes
| Ambiente | Propósito | Dados |
|----------|-----------|-------|
| Local | Desenvolvimento | Mock/seed |
| Staging | Pre-release | Dados sanitizados |
| Produção | Smoke test | Real (somente leitura) |

## Critérios de Qualidade
- Cobertura de código: ≥ [80]%
- Todos ACs validados: [✅]
- Nenhum teste crítico pulado (skipped): [✅]
- Tempo máximo de test suite: [X minutos]

## Risco de Teste
[Áreas sem cobertura adequada e por quê]

---
⚠️ Itens para Validação
[PRECISA_VALIDAR: ...]
```

---

## Geração de Test Cases por AC

Para cada critério de aceite Gherkin, o agente gera:

```markdown
## Test Case — TC-001
**Story**: STORY-XXX
**Cenário**: [Happy Path / Unhappy Path / Edge Case]
**Prioridade**: P1 (Bloqueante) | P2 (Regressão) | P3 (Complementar)

**Pré-condições**:
- [Estado necessário antes de executar]

**Passos**:
1. [Ação exata]
2. [Verificação]

**Resultado Esperado**:
[Comportamento observável verificável]

**Dados de Teste**:
- Input válido: [exemplo]
- Input inválido: [exemplo]
- Boundary: [valor limite]

**Mapeamento**:
- AC: [Dado/Quando/Então]
- Tipo: Unitário | Integração | E2E
```

---

## Gap Analysis de Cobertura

O agente detecta e reporta:

```markdown
## Coverage Gap Report — STORY-XXX

| Critério de Aceite | Teste Mapeado | Status |
|-------------------|--------------|--------|
| Cenário happy path | test_login_success | ✅ Coberto |
| Senha incorreta → erro | test_login_wrong_pass | ✅ Coberto |
| Token expirado → reauth | [AUSENTE] | ⚠️ Gap detectado |
| Rate limit após 5 falhas | [AUSENTE] | ⚠️ Gap detectado |

**Gaps críticos**: 2
**Cobertura de AC**: 50% (2/4)
**Recomendação**: Adicionar TC-003 e TC-004 antes de Sprint Gate
```

---

## BDD Test Skeleton Generator

Dado um cenário Gherkin, gera o skeleton de teste na linguagem do projeto:

**JavaScript/TypeScript (Jest)**:
```typescript
describe('[Feature Name]', () => {
  describe('[Cenário]', () => {
    it('should [comportamento esperado]', async () => {
      // Arrange
      // [setup pré-condições]

      // Act
      // [executa a ação]

      // Assert
      // [verifica resultado esperado]
    });
  });
});
```

**Python (pytest)**:
```python
class TestFeature:
    def test_should_[comportamento](self, setup_fixtures):
        # Arrange
        # Act
        # Assert
```
