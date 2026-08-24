---
name: project-context
description: >
  Diagnóstico e roteamento Brownfield × Greenfield. Gate de entrada obrigatório
  que analisa o projeto, emite PROJECT_CONTEXT.md e define a trilha de execução
  correta para todos os outros agentes.
triggers:
  - "diagnosticar projeto"
  - "brownfield ou greenfield"
  - "iniciar projeto"
  - "PROJECT_CONTEXT"
  - "/init-project"
---

# Project Context Skill

## Objetivo

Classificar o projeto como **Greenfield**, **Brownfield** ou **Híbrido** e
emitir `PROJECT_CONTEXT.md` — o artefato raiz que todos os outros agentes consultam.

---

## Protocolo de Diagnóstico

### Scan Automático (Proactive — executa antes de qualquer pergunta)

```
1. Verifica existência de codebase no repositório atual
2. Procura por: package.json, pom.xml, requirements.txt, go.mod, Gemfile
3. Verifica idade dos commits (git log --oneline -20)
4. Procura por arquivos de dívida técnica: TODO, FIXME, HACK, DEPRECATED
5. Verifica CI/CD existente: .github/workflows, Jenkinsfile, .gitlab-ci.yml
6. Verifica documentação existente: README, ARCHITECTURE, ADR_*
```

Resultado do scan → infere classificação com confidence score.

### Classificação

| Critério | Greenfield | Brownfield | Híbrido |
|----------|-----------|-----------|---------|
| Codebase | Inexistente | Existente e ativa | Parcial / módulo novo |
| Dívida técnica | Zero | Presente | Localizada |
| Time | Novo ou sem legado | Conhece o sistema | Misto |
| Arquitetura | A definir | Existente e restringente | Parcialmente nova |
| Prazo | Flexível (normalmente) | Rígido (deploy contínuo) | Variável |

### Score de Dívida Técnica (BF)

```
+10 → sem testes automatizados
+10 → sem CI/CD
+5  → dependências com >2 major versions de defasagem
+5  → sem documentação de arquitetura
+5  → código com warnings persistentes no build
+3  → ausência de linting/formatting enforcement
```

Score 0-10: dívida baixa | 11-20: média | 21+: crítica

---

## Saída — PROJECT_CONTEXT.md

```markdown
# PROJECT_CONTEXT

## Classificação
- **Tipo**: Greenfield | Brownfield | Híbrido
- **Confidence**: Alta | Média | Baixa
- **Score Dívida Técnica**: X/38

## Stack Detectada
- Linguagem principal: [inferida]
- Framework: [inferido]
- Banco de dados: [inferido]
- CI/CD: [inferido]

## Trilha Recomendada
- **Greenfield**: Brief → PRD → Full Design → TDD-first
- **Brownfield**: Audit → Impact Map → Migration Plan → Regression-first
- **Híbrido**: BF + GF parcial com priorização de impacto

## Restrições Detectadas
- [lista de restricoes inferidas ou marcadas como PRECISA_VALIDAR]

## Variáveis de Roteamento
- FLOW_TYPE: greenfield | brownfield | hybrid
- DEBT_SCORE: [número]
- HAS_TESTS: true | false
- HAS_CI: true | false
- HAS_DOCS: true | false

## Gerado em
- [timestamp]
- [DRAFT v1 — valide e faça commit]
```

---

## Trilhas de Execução

### Greenfield
```
Brief → PRD → Architecture ADR → Epic breakdown
→ Stories com TDD → Code review → Deploy
```

### Brownfield
```
Audit (dívida + legado) → Impact Map → Migration/Strangler Fig plan
→ Regression suite primeiro → Incremental stories → Gate de regressão
```

### Híbrido
```
Audit do módulo afetado → Isolamento de escopo
→ Trilha GF para módulo novo + BF para integrações
```

---

## Bloqueio de Outros Agentes

Todos os agentes KARE devem verificar `PROJECT_CONTEXT.md` antes de agir.
Se o arquivo não existir: alertar e sugerir `/init-project`.

```
⚠️ PROJECT_CONTEXT.md não encontrado.
   Execute /init-project para classificar o projeto antes de continuar.
   Alternativa: informar manualmente se é BF ou GF.
```
