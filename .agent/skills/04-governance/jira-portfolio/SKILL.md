---
name: jira-portfolio
description: >
  Portfolio governance for the workspace operating model. Covers the lifecycle of Iniciativas and Épicos in Jira Cloud, including the TO BE workflow with all statuses and transitions, automation rules for upstream propagation (Feature → Épico → Iniciativa), and cascade rules for Concluído and Cancelado. Use when managing or reviewing portfolio items above the Feature layer, setting up Jira workflows, or checking whether automations are correctly configured.
version: 1.0.0
priority: NORMAL
allowed-tools: Read
---
# Jira Portfolio Governance

You are an expert in Jira portfolio governance. You manage and advise on the lifecycle of **Iniciativas** and **Épicos** in Jira Cloud following the TO BE model defined in the workspace's Playbook, including workflow status, transitions, cascade rules, and automation patterns.

## When to Use

Use this skill when the user asks to:

- Review or transition an Épico or Iniciativa in Jira
- Understand the allowed statuses and transitions for Épicos or Iniciativas
- Set up or validate Jira workflow automations for the portfolio layer
- Check whether cascade rules between Iniciativa → Épico → Feature are respected
- Govern portfolio-level items without touching execution items (Feature and below)
- Explain or apply the Concluído / Cancelado rules for Épicos or Iniciativas

## When NOT to Use

Do NOT use this skill when:

- The request is about Features, Tarefas, or Subtarefas — use **jira-workspace-guide**
- The user needs generic Jira operations — use **jira-assistant**
- The user is working outside configured projects

## Hierarchy Context

```
Iniciativa  (portfolio / strategic)
  └── Épico  (portfolio / capability)
        └── Feature  (ART / delivery)  ← boundary of this skill
```

This skill covers only **Iniciativa** and **Épico**. Features and below are governed by `jira-workspace-guide`.

---

## Épico — Workflow TO BE

### Status sequence (Happy Path)

| # | Status | Category |
|---|--------|----------|
| 1 | **Criado** | To Do |
| 2 | **Em Triagem** | In Progress |
| 3 | **Pronto para Refinamento** | To Do |
| 4 | **Em Refinamento** | In Progress |
| 5 | **Pronto para Design** | To Do |
| 6 | **Em Design** | In Progress |
| 7 | **Pronto para Construção** | To Do |
| 8 | **Em Construção** | In Progress |
| 9 | **Em Avaliação de Resultados** | In Progress |
| 10 | **Pronto para Apresentação dos Resultados** | To Do |
| 11 | **Concluído** | Done |
| — | **Cancelado** | Done |

### Objective of each status

| Status | Purpose |
|--------|---------|
| Criado | Initial registration in the portfolio |
| Em Triagem | Validate the demand and domain fit |
| Pronto para Refinamento | Épico prioritized for detailed scoping |
| Em Refinamento | Define scope, hypotheses, ROI |
| Pronto para Design | Enough information to start solution design |
| Em Design | Design solution and create child Features |
| Pronto para Construção | Approved and planned, ready for execution |
| Em Construção | Features actively being developed |
| Em Avaliação de Resultados | All Features done; validate business outcomes |
| Pronto para Apresentação | Prepare results communication |
| Concluído | Objectives met, results measured |
| Cancelado | Closed without full execution |

### Key transition rules

- **Em Design → Pronto para Construção**: child Features must be created
- **Em Construção → Em Avaliação de Resultados**: all child Features must be Done
- **Concluído**: all child Features in Done AND at least one with status "Concluída"
- **Cancelado**: all child Features in Done AND at least one "Cancelada", none "Concluída"

### Allowed return flows

- Triagem ↔ Criado
- Em Refinamento ↔ Em Triagem
- Em Design ↔ Pronto para Design
- Em Construção ↔ Pronto para Construção
- Em Avaliação de Resultados ↔ Em Construção

### Cancelamento

Transition to **Cancelado** is allowed from any status except Concluído:
- Criado, Em Triagem, Pronto para Refinamento, Em Refinamento, Pronto para Design, Em Design, Pronto para Construção, Em Construção, Em Avaliação de Resultados

---

## Automation Rules — Épico reacts to Features

### A1 — Move Épico to "Em Construção" when first Feature enters In Progress

| | |
|---|---|
| **Trigger** | Feature transitioned to statusCategory = In Progress |
| **Condition 1** | Feature has a parent Épico |
| **Condition 2** | Épico is in a status before "Em Construção" (e.g., Pronto para Construção or Em Design) |
| **Action** | Transition Épico → Em Construção |

### A2 — Suggest "Em Avaliação de Resultados" when all Features are Done

| | |
|---|---|
| **Trigger** | Feature transitioned to statusCategory = Done |
| **Condition 1** | Find parent Épico |
| **Condition 2** | ALL child Features of the Épico are in statusCategory = Done |
| **Condition 3** | At least one Feature has status "Concluída" |
| **Action** | Transition Épico → Em Avaliação de Resultados, OR add a comment suggesting the move |

### A3 — Cascade rules for Épico Concluído / Cancelado

**For Concluído:**
- Trigger: Em Avaliação de Resultados → Concluído transition
- Guard: ALL child Features Done AND at least one "Concluída"
- Block the transition if conditions are not met

**For Cancelado:**
- Trigger: Feature → Done (any)
- Conditions: ALL Features Done; at least one "Cancelada"; NONE "Concluída"
- Action: Suggest or transition Épico → Cancelado

---

## Automation Rules — Iniciativa reacts to Épico

### B1 — Move Iniciativa to "Em Execução" when first Épico enters In Progress

| | |
|---|---|
| **Trigger** | Épico transitioned to statusCategory = In Progress |
| **Condition** | Épico has a parent Iniciativa in status "Aprovada para Execução" (or equivalent) |
| **Action** | Transition Iniciativa → Em Execução |

### B2 — Cascade rules for Iniciativa Concluída / Cancelada

**Concluída:**
- All child Épicos Done AND at least one "Concluído"

**Cancelada:**
- All child Épicos Done AND at least one "Cancelado", NONE "Concluído"

---

## Workflow Validation Checklist

Before marking an Épico as Concluído, verify:

- [ ] All child Features are in statusCategory = Done
- [ ] At least one Feature has status "Concluída" (not just "Cancelada")
- [ ] Business results have been recorded in Em Avaliação de Resultados
- [ ] Parent Iniciativa status reflects the current execution state

Before marking as Cancelado:

- [ ] All child Features are Done
- [ ] No Feature is "Concluída"
- [ ] Cancellation rationale is documented in the Épico description or comment

---

## Iniciativa — Lifecycle

The Iniciativa is the highest strategic layer. It groups Épicos that contribute to a common business objective.

Key rules:

- An Iniciativa should not be Concluída if any child Épico is still active
- Iniciativa status should reflect the aggregate progress of its Épicos
- When all Épicos are Concluídos → suggest Iniciativa → Concluída
- When all Épicos are Done (mix of Concluído/Cancelado) → follow cascade rule B2

---

## Operating Rules

### Search portfolio items

```
search("Épicos em Em Construção no projeto XYZ")
searchJiraIssuesUsingJql(
  cloudId,
  "project = {PROJECT_KEY} AND issuetype = Epic AND status = 'Em Construção'"
)
```

### Transition an Épico

```
1. getTransitionsForJiraIssue(cloudId, epicKey)
2. Confirm the transition against the allowed flow above
3. transitionJiraIssue(cloudId, epicKey, transitionId)
```

### Validate before Concluído

```
1. searchJiraIssuesUsingJql(
     cloudId,
     "parent = {EPIC_KEY} AND issuetype = Feature"
   )
2. Check: all Done? At least one "Concluída"?
3. If yes, proceed. If no, report the blockers to the user.
```

---

## Skill Composition

| Need | Skill |
|------|-------|
| Épico and Iniciativa lifecycle, automations | **jira-portfolio** *(this skill)* |
| Feature, Tarefa, Subtarefa, requirements | **jira-workspace-guide** |
| Raw Jira operations (search, create, transition) | **jira-assistant** |

This skill focuses on **governance and lifecycle decisions**. It relies on `jira-assistant` for the actual MCP tool calls.
