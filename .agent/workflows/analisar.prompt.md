---
description: "Analisa consistência, cobertura e rastreabilidade entre contexto, PRD, backlog, features, stories, testes, riscos e ADRs"
---

# /analisar Workflow

## O que faz
Executa uma análise transversal dos artefatos do KARE para detectar desalinhamentos,
gaps de cobertura, inconsistências e itens sem rastreabilidade.

## Quando usar
- Antes de iniciar implementação de uma feature importante
- Depois de gerar PRD, backlog, stories ou testes
- Antes de uma revisão, sprint planning ou release
- Quando houver suspeita de drift entre especificação e execução

## O que NÃO faz
- Não substitui o quality gate formal do `/quality`
- Não aprova release sozinho
- Não altera artefatos sem deixar claro o impacto

## Passos

// turbo
1. Ler o escopo alvo e os artefatos relacionados

// turbo
2. Validar consistência entre:
   - contexto ? PRD
   - PRD ? épicos/capabilities/features
   - features ? stories ? ACs
   - stories ? testes ? DoD
   - implementação ? ADRs ? riscos

3. Detectar gaps, conflitos, duplicações e dependências ocultas

4. Classificar achados em:
   - ? OK
   - ?? Atenção
   - ? Bloqueador

5. Indicar ações corretivas e o próximo comando recomendado

## Uso

```text
/analisar [escopo]
/analisar --epic EP-05
/analisar --feature FEAT-12
/analisar --story US-15
/analisar --release v1.2.0
```

## Saídas Esperadas
- Relatório de consistência cross-artifact
- Lista de gaps e bloqueadores
- Matriz resumida de rastreabilidade
- Próximas ações recomendadas
