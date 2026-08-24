---
description: "Clarifica requisitos ambíguos antes do planejamento, refinamento ou implementação, gerando perguntas, premissas e decisões pendentes"
---

# /clarificar Workflow

## O que faz
Analisa um escopo ainda ambíguo e transforma incertezas em perguntas objetivas,
premissas explícitas e pontos que precisam de validação antes do time avançar.

## Quando usar
- Antes de `/plan`, `/story`, `/implement` ou `/decision`
- Quando houver campos marcados como `[PRECISA_VALIDAR]`
- Quando o épico, capability, feature ou story estiver grande demais ou vago
- Quando faltar regra de negócio, integração, persona ou critério de aceite

## O que NÃO faz
- Não escreve código
- Não substitui a decisão do negócio
- Não inventa requisitos sem sinalizar hipótese ou premissa

## Passos

// turbo
1. Ler o contexto e os artefatos já existentes (`PROJECT_CONTEXT.md`, `PRD.md`, backlog, story, ADRs)

// turbo
2. Detectar ambiguidades por categoria:
   - negócio e valor
   - regras e exceções
   - dados e integrações
   - UX e operação
   - riscos e dependências

3. Gerar perguntas priorizadas e objetivas

4. Se necessário, propor premissas temporárias marcadas como `[PRECISA_VALIDAR]`

5. Recomendar o próximo comando mais adequado:
   - `/story`
   - `/plan`
   - `/decision`
   - `/risk`

## Uso

```text
/clarificar [descrição do escopo]
/clarificar --epic EP-03
/clarificar --feature FEAT-07
/clarificar --story US-42
/clarificar --prd [arquivo ou contexto]
```

## Saídas Esperadas
- Perguntas de clarificação priorizadas
- Lista de premissas explícitas
- Gaps marcados como `[PRECISA_VALIDAR]`
- Recomendação de próximo passo
