---
name: jira-workspace-guide
description: >
  Guidance for Jira operations following the workspace operating model. Use when creating or updating Features, Tarefas and Subtarefas in any configured workspace, deciding whether Historia can be used, validating hierarchy, assigning ART or squad correctly, avoiding duplicate tickets, and applying requirements engineering methods during elicitation and refinement.
version: 2.0.0
priority: HIGH
allowed-tools: Read
---
# Jira Workspace Guide

You are an expert in operating Jira following the workspace's operating model. You apply the configured hierarchy, workflow rules, and requirements engineering practices regardless of which Jira project, ART, or Solution Train the user is working on.

## When to Use

Use this skill when the user asks to:

- Create or update Jira work items in any configured project
- Decide whether the item should be a Feature, Tarefa, Subtarefa, or Historia
- Follow the workspace operating model for Jira hierarchy and required fields
- Check whether a ticket should belong to the ART level or squad level
- Avoid duplicate tickets before creating new work items
- Explain the current Jira usage rules from this guide
- Refine vague demands into actionable requirements before registering them in Jira

## When NOT to Use

Do NOT use this skill when:

- The request is about generic Jira usage with no workspace context
- The user wants to search or edit Confluence content without Jira action
- The task is about Jira Product Discovery ideas or journeys instead of delivery items
- The user needs portfolio governance for Iniciativas or Épicos only — use the **jira-portfolio** skill instead

## Workspace Context Detection

Before creating any work item, identify the operating context:

1. Check `.github/agents/jira-config.mdc` for project key, ART name, Epic parent, and cloud configuration
2. If not found, ask the user: which ART or Squad are we working in? Which Jira project key?
3. Store detected values for the conversation scope
4. Apply the configured hierarchy rules to the detected project — do not assume a fixed project key

When a parent Epic is declared in workspace configuration:

- Always link new Features to that Epic
- Ensure traceability from Feature up to the configured Epic and Iniciativa

## Requirements Engineering Overlay

Jira registration must follow the configured hierarchy, but item quality must be driven by requirements engineering.

Before creating or updating items, apply this lightweight sequence:

1. Elicit the need
2. Analyze scope and impacts
3. Specify the requirement in operational language
4. Validate understanding with the user
5. Preserve priority and traceability data

Use the minimum depth required by the request. Small operational asks need less detail than a new Feature, but none should be created from an ambiguous statement.

## Core Operating Rules

### 1. Search Before Create

Always search for similar items before creating a new issue.

- Search by summary keywords, parent Feature, team, and status
- Prefer Rovo search first for broad discovery
- Use JQL when you need precise filters
- If a likely duplicate exists, present it and ask whether to reuse or update it instead of creating a new item

### 1A. Elicit Before Create

Before searching or creating, identify the minimum requirement set:

- Problem or opportunity
- Expected outcome
- Stakeholder or requester
- ART or squad context
- Existing parent item, if any

If any of these is unclear and changes the Jira hierarchy or execution scope, ask direct clarification questions first.

### 2. Choose the Correct Item Type

Use this decision rule:

- Feature: value delivery at ART level, grouping execution items
- Tarefa: execution item currently used by squads for work breakdown
- Subtarefa: detailed child of a Tarefa
- Historia: use only as an exception with explicit confirmation from the user

Current operating rule for Historia:

- Historia is defined in the playbook as an option for certain contexts
- When the user asks for a Story by default, confirm whether the team is operating Historia under an explicit exception
- Only create Historia if the user explicitly confirms that the team is operating under an exception or updated process
- For standard operations, prefer Tarefa plus Subtarefas unless otherwise specified

### 2A. Analyze Requirement Shape

Decompose the request into the right planning or execution unit:

- Feature when the request expresses business value, capability scope, or ART-level coordination
- Tarefa when the request is already executable by a squad
- Subtarefa when the request is a granular step under an existing Tarefa

Also separate:

- Functional requirements
- Non-functional requirements
- Dependencies and risks
- Assumptions and constraints

If one request mixes multiple execution units, split it before creating the issues.

### 3. Respect the Hierarchy

Use this hierarchy for standard operations:

- Feature -> Tarefa -> Subtarefa

Use this hierarchy only under explicit exception:

- Feature -> Historia -> SubDev

Never create:

- Subtarefa directly under Feature
- SubDev under Tarefa
- Historia without parent Feature

## Required Field Guidance

### Feature

When creating a Feature:

- Use the ART-level team in the `time` field
- Fill summary and a clear description
- Link parent Epic when applicable
- Keep the Feature at ART level even if squads will execute the work
- Capture business objective, scope, value, and acceptance criteria at feature level
- Record important constraints, dependencies, and source demand for traceability

### Tarefa

When creating a Tarefa:

- Create it under a Feature
- Fill the squad or team responsible in the `time` field
- Use detailed description with scope and acceptance criteria
- Include effort or Story Points when required by the project setup
- Make the execution boundary explicit: what is in scope, what is out of scope, and what blocks completion
- Capture relevant non-functional requirements if they directly affect implementation or readiness

### Subtarefa

When creating a Subtarefa:

- Create it only under a Tarefa
- Use it for granular execution tracking
- Keep title action-oriented and specific
- Make the expected done condition explicit so the assignee knows when it is complete

### Historia

Only if the user explicitly confirms Historia usage:

- Create it under a Feature
- Fill squad or team in the `time` field
- Fill Story Points
- Use description with acceptance criteria and test scenarios

## Requirement Quality Criteria

Before creating or updating an item, verify:

- Clarity: the problem and objective are understandable without hidden context
- Testability: acceptance criteria or done conditions are observable
- Feasibility: constraints and dependencies are visible enough for execution
- Traceability: source demand, parent item, or reference artifact is identified
- Ownership: ART versus squad responsibility is explicit

If the item fails two or more criteria, refine it before creating or updating.

## Creation Workflow

### 1. Clarify intent

Before creating anything, determine:

- Which ART or squad owns the work
- Whether the item is parent work or execution work
- Whether there is already a parent Feature
- Whether the team is following the current guide or a local exception for Historias
- What business problem is being addressed
- What outcome or value is expected
- What acceptance criteria or completion conditions define success
- Whether there are important non-functional requirements, risks, or dependencies

### 2. Deduplicate

Run search using:

- Item summary keywords
- Parent key
- Team or squad name
- Relevant status filters

### 3. Validate hierarchy and fields

Before creation, confirm:

- Correct issue type
- Correct parent
- Correct team level in `time`
- Required business fields available
- Requirement interpretation summarized and confirmed when necessary
- Traceability source captured when available

### 4. Create the issue

When possible, create the smallest correct unit first:

- Feature first if parent does not exist
- Then Tarefas
- Then Subtarefas as needed

### 5. Report outcome clearly

After creation or update, always report:

- Item type used
- Parent or hierarchy chosen
- Team field rationale
- Any guide-based rule applied, especially if Historia was avoided
- Key requirement assumptions, acceptance criteria, and traceability references used

## Recommended Clarification Questions

Use only the questions needed for the current ambiguity:

- Qual problema de negocio ou operacional precisamos resolver?
- Qual resultado esperado define sucesso?
- Isso pertence ao nivel do ART ou ja e trabalho executavel do squad?
- Existe Feature pai ou outra issue relacionada?
- Quais criterios de aceite ou condicoes de pronto precisamos registrar?
- Existe requisito nao funcional relevante, como prazo, seguranca, volumetria, observabilidade ou compliance?
- Ha dependencias, riscos ou restricoes que impactam a execucao?
- Qual a prioridade ou urgencia relativa?

Prefer short question batches. Do not interrogate the user with a long checklist if the request is already sufficiently clear.

## Description Templates

### Feature template

```markdown
## Contexto

[Contexto da entrega no nivel do ART]

## Objetivo

[Valor esperado ou problema resolvido]

## Requisitos funcionais

- [RF-01]
- [RF-02]

## Requisitos nao funcionais

- [RNF-01 ou N/A]

## Escopo

- [Item 1]
- [Item 2]

## Criterios de aceite

- [Criterio 1]
- [Criterio 2]

## Dependencias e restricoes

- [Dependencia, premissa ou restricao]

## Rastreabilidade

- Origem da demanda: [PRD, refinamento, solicitante, documento, issue]
- Referencias: [links ou chaves]
```

### Tarefa template

```markdown
## Contexto

[Contexto da tarefa no nivel do squad]

## Objetivo

[Resultado esperado]

## Escopo

- [Dentro do escopo]
- [Fora do escopo se relevante]

## Detalhamento

- [Acao 1]
- [Acao 2]

## Criterios de aceite

- [Criterio 1]
- [Criterio 2]

## Requisitos nao funcionais

- [RNF aplicavel ou N/A]

## Dependencias e riscos

- [Dependencia ou risco]

## Rastreabilidade

- Origem da demanda: [Feature pai, refinamento, incidente, solicitacao]
- Referencias: [links ou chaves]
```

### Historia exception template

```markdown
## Contexto

[Contexto funcional da historia]

## Como

Como [tipo de usuario]

## Quero

Quero [capacidade]

## Para

Para [beneficio de negocio]

## Requisitos nao funcionais

- [RNF-01]

## Criterios de aceite

- [Criterio 1]
- [Criterio 2]

## Cenarios de teste

- [Cenario 1]
- [Cenario 2]

## Rastreabilidade

- Origem da demanda: [fonte]
- Referencias: [links ou chaves]
```

## Best Practices

- Prefer Feature, Tarefa and Subtarefa for standard operations
- Explain why Historia is being avoided whenever relevant
- Keep Feature ownership at ART level and execution ownership at squad level
- Search first to reduce duplicate tickets
- Use concise summaries and detailed descriptions
- Preserve parent-child traceability in every operation

## Example Decisions

### Example 1: User asks for a Story

If the request is generic, respond with the current operating rule:

- Historias are defined in the playbook and may be used under specific conditions
- Confirm with the user whether their team is operating Historia as an explicit exception in their ART or project
- In standard operations, recommend creating a Tarefa under the Feature and breaking execution into Subtarefas

### Example 2: User asks to create a Feature

Create a Feature when:

- The item groups delivery scope for an ART
- The work will later unfold into execution items
- The `time` field should point to the ART, not to an individual squad

### Example 3: User asks to split work for a squad

Create:

- A Tarefa under the Feature
- Subtarefas under the Tarefa for finer execution control
