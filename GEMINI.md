# KARE-SPEC — Gemini CLI

Este projeto usa o **KARE-SPEC** (KARE-PSAISS-CORE) para desenvolvimento assistido por IA com Gemini CLI.

## Agentes disponíveis

Os agentes estão em `.agent/agents/`. Ponto de entrada obrigatório: `kare-orchestrator`.

## Comandos principais

```
/create       → Discovery completo (PRD + Backlog + ADRs)
/story        → User Story com ACs
/sprint       → Sprint Planning
/plan         → Project Planning
/implement    → Código com TDD
/review       → Code Review
/test         → Testes automatizados
/risk         → Análise RAID
/status       → Status Report
/kare-flow    → Fluxo E2E Produto/Software (idea → PR)
```

## Context Engine (RAG)

```bash
python .agent/scripts/ai/kare_rag.py search "sua busca"
python .agent/scripts/ai/kare_rag.py status
```

## Regras e instruções

Leia os arquivos em `.agent/rules/` para entender o protocolo KARE-SPEC.
Documentação: https://github.com/giovannyesposito/KARE-PSAISS-CORE
