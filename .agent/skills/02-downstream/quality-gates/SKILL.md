---
name: quality-gates
description: >
  Quality gates automáticos: DoD check, AC validation, cobertura de testes,
  lint, segurança, performance e compliance. Define critérios mínimos por
  nível (story, sprint, release) e emite QA Report.
triggers:
  - "quality gate"
  - "DoD"
  - "definition of done"
  - "checklist de qualidade"
  - "release checklist"
  - "AC validation"
---

# Quality Gates Skill

## Níveis de Gate

```
Story Gate   → antes de mover para "Done"
Sprint Gate  → antes do sprint review
Release Gate → antes do deploy em produção
Hotfix Gate  → gate acelerado para fixes emergenciais
```

---

## Story Gate — Checklist

```markdown
# Story Gate — STORY-XXX

## Código
- [ ] PR criado e aprovado (≥1 reviewer)
- [ ] Sem conflitos pendentes na branch
- [ ] Build CI passando
- [ ] Sem linting errors (0 warnings críticos)

## Testes
- [ ] Testes unitários escritos para nova lógica
- [ ] Cobertura ≥ 80% no módulo modificado
- [ ] Testes de integração para pontos de integração
- [ ] Todos os critérios de aceite validados (incluindo unhappy paths)
- [ ] Testes de regressão relevantes passando

## Segurança
- [ ] Sem secrets no código (git-secrets, trufflehog)
- [ ] Inputs validados e sanitizados
- [ ] Dependências sem vulnerabilidades críticas (npm audit, pip-audit)

## Documentação
- [ ] Comentários de código onde necessário
- [ ] README atualizado se houver mudança de setup
- [ ] ADR gerado para decisões técnicas relevantes

## Deploy
- [ ] Testado em ambiente de staging
- [ ] Feature flag configurada (se aplicável)
- [ ] Rollback plan definido

**Resultado**: APROVADO | REPROVADO: [itens bloqueantes]
```

---

## Sprint Gate — Checklist

```markdown
# Sprint Gate — Sprint [N]

## Velocidade e Entrega
- [ ] Todas as stories comprometidas estão DONE ou justificadas
- [ ] Velocity dentro de ±20% da média histórica
- [ ] Sprint goal atingido

## Qualidade Técnica
- [ ] Cobertura de testes ≥ threshold definido no projeto
- [ ] Dívida técnica não aumentou sem tracking (TECH items adicionados)
- [ ] SLOs do ambiente de staging atendidos

## Segurança
- [ ] Vulnerability scan executado (SAST)
- [ ] Nenhuma vulnerabilidade crítica aberta

## Documentação
- [ ] Stories finalizadas têm AC documentado como "validado"
- [ ] ADRs propostos no sprint foram fechados ou têm data

## Risk Register
- [ ] Riscos revisados e atualizados
- [ ] Riscos materializados têm post-mortem ou lição aprendida

**Resultado**: APROVADO | REPROVADO: [bloqueantes]
```

---

## Release Gate — Checklist

```markdown
# Release Gate — Release [X.Y.Z]

## Requisitos Funcionais
- [ ] 100% dos ACs das stories da release validados
- [ ] UAT (User Acceptance Testing) concluído com sign-off
- [ ] Nenhum bug crítico/alto aberto

## Performance
- [ ] Load test executado com carga esperada
- [ ] Core Web Vitals dentro do target
- [ ] Latência de API dentro do SLA definido

## Segurança
- [ ] SAST e DAST executados sem críticos
- [ ] Pen test realizado (se release major)
- [ ] OWASP Top 10 validado

## Observabilidade
- [ ] Dashboards de monitoramento configurados
- [ ] Alertas definidos para métricas críticas
- [ ] Runbook de incidente documentado
- [ ] SLO/SLA definido e monitorado

## Deploy
- [ ] Canary/Blue-Green configurado
- [ ] Rollback plan testado
- [ ] Feature flags prontas para toggle
- [ ] Comunicação de release preparada

## Compliance
- [ ] LGPD/GDPR checklist validado (se aplica)
- [ ] Auditoria de acesso a dados revisada

**Resultado**: GO | NO-GO: [bloqueantes críticos]
```

---

## AC Validation Protocol

Para cada critério de aceite de uma story, o agente executa:

```
1. Lê o AC no formato Gherkin
2. Verifica se existe teste mapeado para aquele cenário
3. Verifica se o teste passou na última execução CI
4. Marca: ✅ VALIDADO | ⚠️ TESTE AUSENTE | ❌ TESTE FALHANDO
```

Saída por story:

```markdown
## AC Validation Report — STORY-XXX

| Cenário | Teste | Status |
|---------|-------|--------|
| Happy Path — usuário logado acessa dashboard | test_dashboard_authenticated | ✅ |
| Unhappy Path — usuário sem permissão é redirecionado | test_dashboard_unauthorized | ✅ |
| Edge Case — token expirado exibe mensagem de reautenticação | [AUSENTE] | ⚠️ |
```
