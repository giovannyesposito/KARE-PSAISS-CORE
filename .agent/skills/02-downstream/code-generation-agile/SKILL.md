---
name: code-generation-agile
description: >
  Geração de código orientado por stories e ACs. Segue TDD (Red-Green-Refactor),
  respeita ADRs e patterns do projeto, e sempre verifica PROJECT_CONTEXT.md
  antes de gerar. Produz código limpo, sem over-engineering.
triggers:
  - "gerar código"
  - "implementar story"
  - "TDD"
  - "red green refactor"
  - "implementação"
---

# Code Generation Agile Skill

## Protocolo de Geração (Proativo)

Antes de escrever qualquer código:
1. Lê a story e seus ACs (Gherkin)
2. Lê `PROJECT_CONTEXT.md` — stack, patterns, BF/GF
3. Lê ADRs relevantes — respeitando decisões técnicas tomadas
4. Verifica stories similares já implementadas — evita duplicação de código
5. Gera na ordem TDD: **Teste primeiro → Implementação → Refactor**

---

## TDD Workflow

### Fase RED — Teste Falhando

```
1. Lê o AC (Gherkin)
2. Gera o teste correspondente (AAA pattern)
3. O teste falha porque a implementação não existe ainda
4. Apresenta o teste ao usuário para validação
```

### Fase GREEN — Implementação Mínima

```
1. Escreve o código mínimo para passar no teste
2. Sem over-engineering — YAGNI (You Ain't Gonna Need It)
3. Sem abstrações prematuras
4. Prioriza legibilidade sobre "elegância"
```

### Fase REFACTOR — Limpeza

```
1. Elimina duplicação (DRY)
2. Melhora nomes (classes, funções, variáveis)
3. Extrai quando há coesão clara
4. Todos os testes continuam passando
5. Sem alteração de comportamento
```

---

## Regras de Código (Clean Code KARE)

```
✅ Funções fazem UMA coisa
✅ Nomes revelam intenção (sem abreviações crípticas)
✅ Sem comentários óbvios (código auto-documentado)
✅ Máximo 20 linhas por função (ideal ≤10)
✅ Sem magic numbers — use constantes nomeadas
✅ Dependency Injection sobre hard-coded dependencies
✅ Tratamento de erro explícito (sem swallow silencioso)

❌ God Objects / God Functions
❌ Comentários que explicam "o que" (deve ser óbvio)
❌ Variáveis de loop genéricas (i, j, k) — use nomes de domínio
❌ Logs de debug deixados no código
❌ TODO sem ticket de rastreamento
```

---

## Checklist por Bloco de Código

```
[ ] Código implementa exatamente o AC? (nem mais, nem menos)
[ ] Existe teste cobrindo o happy path?
[ ] Existe teste cobrindo unhappy paths?
[ ] Inputs são validados?
[ ] Erros são propagados/logados adequadamente?
[ ] Nenhuma lógica duplicada com código existente?
[ ] Respeitou ADRs do projeto?
[ ] Sem dependências desnecessárias adicionadas?
```

---

## Proactive Code Review (Auto-Review antes de entregar)

O agente executa auto-review antes de apresentar o código:

```
🔍 Auto-review:
- Complexidade ciclomática: [baixa/média/alta]
- Cobertura de AC: [n/N cenários cobertos]
- Violações detectadas: [lista ou "nenhuma"]
- Sugestões de melhoria: [se houver]
```

---

## Contexto de Stack por Projeto

O agente adapta o código ao stack definido no `PROJECT_CONTEXT.md`:

| Stack | Patterns aplicados |
|-------|-------------------|
| Node.js/TypeScript | async/await, Result types, Zod validation |
| Python | type hints, dataclasses/Pydantic, pytest |
| Java/Spring | DI por construtor, @Service layers, JUnit 5 |
| React | hooks, composição, prop drilling mínimo |
| Genérico | SOLID, Clean Architecture layers |

---

## Integração com ADRs

Ao gerar código, o agente verifica conflitos com ADRs:

```
⚠️ Detectado: Você está usando [biblioteca X], mas ADR-003 define [biblioteca Y]
   como padrão do projeto. Deseja:
   a) Usar Y conforme ADR-003
   b) Criar RFC para propor X como alternativa
   c) Ignorar (não recomendado — gera inconsistência)
```
