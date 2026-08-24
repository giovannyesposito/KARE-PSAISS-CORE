---
name: review-patterns
supersedes: code-review-checklist
description: >
  Code review principles e padrões de feedback construtivo.
  Detecta issues de segurança, performance, design e testabilidade.
  Gera relatório estruturado por severidade.
triggers:
  - "code review"
  - "revisão de código"
  - "PR review"
  - "pull request"
  - "/review"
---

# Review Patterns Skill

## Filosofia de Code Review KARE

```
✅ Revisar o CÓDIGO, não a PESSOA
✅ Questionar com curiosidade: "Por que esta abordagem?"
✅ Separar: bloqueantes × sugestões × nitpicks
✅ Oferecer solução ao apontar problema
✅ Reconhecer e elogiar boas decisões
✅ Ser específico — evitar "isso está errado" sem contexto
```

---

## Níveis de Feedback

| Nível | Prefixo | Significado |
|-------|---------|-------------|
| **BLOCKER** | `🔴 BLOCKER:` | Não pode mergear — funcional, segurança, data loss |
| **MAJOR** | `🟠 MAJOR:` | Deve ser adressado neste PR — design, performance |
| **MINOR** | `🟡 MINOR:` | Preferivelmente corrigir — code style, legibilidade |
| **NIT** | `🟢 NIT:` | Opcional — preferência pessoal, nitpick |
| **PRAISE** | `⭐ PRAISE:` | Reconhecer boa decisão ou pattern |
| **QUESTION** | `❓ QUESTION:` | Pedido de esclarecimento, não crítica |

---

## Checklist de Review por Dimensão

### Funcionalidade
```
[ ] O código faz o que a story/AC descreve?
[ ] Edge cases estão tratados?
[ ] Unhappy paths têm comportamento correto?
[ ] Não há breaking changes não anunciadas?
```

### Segurança
```
[ ] Inputs são validados antes de usar?
[ ] Não há SQL injection, XSS, path traversal?
[ ] Dados sensíveis não são logados?
[ ] Autenticação/autorização correta?
[ ] Secrets não estão no código?
```

### Performance
```
[ ] Sem N+1 queries (em loops)?
[ ] Queries têm índices adequados?
[ ] Sem cálculos desnecessários dentro de loops?
[ ] Cache necessário foi implementado?
```

### Design
```
[ ] Responsabilidade única por função/classe?
[ ] Sem acoplamento desnecessário?
[ ] Abstrações estão no nível certo (nem muito, nem pouco)?
[ ] Decisões técnicas refletem ADRs do projeto?
```

### Testabilidade
```
[ ] Código pode ser testado sem mocks excessivos?
[ ] Lógica de negócio está separada de side-effects?
[ ] Testes cobrem comportamento, não implementação?
```

---

## Template de Review Report

```markdown
# Code Review — PR #[número]
**Story**: STORY-XXX
**Autor**: [dev]
**Reviewer**: KARE AI
**Data**: [data]

## Sumário
- 🔴 BLOCKERs: [n]
- 🟠 MAJORs: [n]
- 🟡 MINORs: [n]
- 🟢 NITs: [n]
- ⭐ PRAISEs: [n]

**Decisão**: APROVADO | APROVADO COM RESSALVAS | REPROVADO

---

## Findings

### 🔴 BLOCKER — [arquivo:linha] — [título]
**Problema**: [descrição do problema]
**Impacto**: [o que pode acontecer se não corrigir]
**Sugestão**:
\`\`\`[linguagem]
// código sugerido
\`\`\`

### 🟠 MAJOR — [arquivo:linha] — [título]
[mesmo formato]

### ⭐ PRAISE — [arquivo:linha]
[O que foi bem feito e por quê merece destaque]

---

## Observações Gerais
[Tendências observadas, sugestões de longo prazo, padrões detectados]
```

---

## Regras de Aprovação

```
APROVADO: 0 BLOCKERs E 0 MAJORs
APROVADO COM RESSALVAS: 0 BLOCKERs, ≥1 MAJOR (resolve antes do merge)
REPROVADO: ≥1 BLOCKER (obrigatório corrigir e solicitar novo review)
```

---

## Proactive Suggestions During Review

O agente sinaliza proativamente:
- Padrões inconsistentes com o restante do codebase
- Oportunidade de reusar código existente (DRY)
- Decisões que deveriam virar ADR
- Cobertura de testes insuficiente para o risco do código

---

## AI & LLM Review Patterns (2025)

### Lógica e Alucinações
```
[ ] Chain of Thought: a lógica segue um caminho verificável?
[ ] Edge Cases: o código cobre estados vazios, timeouts e falhas parciais?
[ ] External State: há suposições inseguras sobre filesystem ou network?
```

### Prompt Engineering Review
```typescript
// ❌ Prompt vago no código
const response = await ai.generate(userInput);

// ✅ Prompt estruturado e seguro
const response = await ai.generate({
  system: "You are a specialized parser...",
  input: sanitize(userInput),
  schema: ResponseSchema
});
```

### AI-Specific Security
```
[ ] Proteção contra Prompt Injection implementada?
[ ] Outputs sanitizados antes de usar em sinks críticos?
[ ] Dados sensíveis não vazam via contexto do LLM?
```

---

## Anti-Patterns a Sinalizar

```typescript
// ❌ Magic numbers
if (status === 3) { ... }
// ✅ Named constants
if (status === Status.ACTIVE) { ... }

// ❌ Deep nesting
if (a) { if (b) { if (c) { ... } } }
// ✅ Early returns
if (!a) return;
if (!b) return;
// do work

// ❌ Funções longas (100+ linhas)
// ✅ Funções pequenas e focadas

// ❌ any type
const data: any = ...
// ✅ Tipos explícitos
const data: UserData = ...
```
