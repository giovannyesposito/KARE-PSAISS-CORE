# Antigravity Kit Architecture

> Comprehensive AI Agent Capability Expansion Toolkit

---

## 📋 Overview

Antigravity Kit is a modular system consisting of:

- **20 Specialist Agents** - Role-based AI personas
- **44 Skills** - Domain-specific knowledge modules
- **19 Workflows** - Slash command procedures

---

## 🏗️ Directory Structure

```plaintext
KARE-PSAISS-CORE/
├── .agent/
│   ├── agents/              # 26 agentes especializados
│   ├── skills/              # 78 skills em 6 domínios
│   │   ├── 01-upstream/     # Discovery, stories, backlog
│   │   ├── 02-downstream/   # Código, revisão, testes, deploy
│   │   ├── 03-architecture/ # Decisões técnicas, ADRs, padrões
│   │   ├── 04-governance/   # SPTI, CHG, JIRA, status report
│   │   ├── 05-tech-stack/  # Salesforce, BRM, MuleSoft... (on-demand)
│   │   └── 06-platform/     # Orquestração, RAG, guards, AI infra
│   ├── scripts/             # Scripts por propósito
│   │   ├── ai/              # RAG, ingestão, contexto
│   │   ├── guards/          # Guardrail, SQL guard, loop guard
│   │   ├── generators/      # PPT, PDF, HTML
│   │   ├── sync/            # Confluence, Obsidian, Figma
│   │   ├── telemetry/       # Métricas, sessões
│   │   ├── infra/           # Setup, MCP, credenciais
│   │   └── hooks/           # pre-commit, post-commit
│   ├── rules/               # Instructions globais
│   ├── config/              # mcp_config.json, workflows-index.json
│   ├── docs/                # ARCHITECTURE.md, MCP setup guides
│   ├── context/             # PROJECT_CONTEXT.md (gerado)
│   ├── workflows/           # Slash commands
│   └── _archived/           # Agentes e skills arquivados
├── .specify/rag/            # 3 bancos SQLite: perene, history, telemetry
├── .config/                 # Credenciais encriptadas (MCP)
├── .vscode/                 # settings.json, tasks.json, mcp.json
├── tools/
│   ├── installer/           # Instalador KARE-SPEC
│   └── KARE-SPEC-modules.yaml
└── uploads/                 # Entrada de documentos brutos
```

---

## 🤖 Agents (20)

Specialist AI personas for different domains.

| Agent                    | Focus                      | Skills Used                                              |
| ------------------------ | -------------------------- | -------------------------------------------------------- |
| `kare-orchestrator`      | Multi-agent coordination   | orchestration-patterns, parallel-agents, kare-operating-model |
| `project-planner`        | Discovery, task planning   | brainstorming, plan-writing, architecture                |
| `frontend-specialist`    | Web UI/UX                  | frontend-design, lint-and-validate                       |
| `backend-specialist`     | API, business logic        | api-patterns, nodejs-best-practices, database-design     |
| `database-architect`     | Schema, SQL                | database-design                                          |
| `mobile-developer`       | iOS, Android, RN           | -                                                        |
| `devops-engineer`        | CI/CD, infra               | deployment-procedures, observability-patterns            |
| `security-auditor`       | Security + pentest         | vulnerability-scanner, api-patterns                      |
| `test-engineer`          | Testing strategies         | test-artifact-generation, tdd-workflow, webapp-testing   |
| `debugger`               | Root cause analysis        | systematic-debugging                                     |
| `performance-optimizer`  | Speed, Web Vitals          | performance-profiling                                    |
| `documentation-writer`   | Manuals, docs              | documentation-templates                                  |
| `qa-automation-engineer` | E2E testing, CI pipelines  | webapp-testing, test-artifact-generation                 |
| `code-archaeologist`     | Legacy code, refactoring   | clean-code, review-patterns                              |

---

## 🧩 Skills (36)

Modular knowledge domains that agents can load on-demand. based on task context.

### Frontend & UI

| Skill                   | Description                                                           |
| ----------------------- | --------------------------------------------------------------------- |
| `react-best-practices`  | React & Next.js performance optimization (Vercel - 57 rules)          |
| `frontend-design`       | UI/UX patterns, design systems                                        |
| `ui-ux-pro-max`         | 50 styles, 21 palettes, 50 fonts                                      |

### Backend & API

| Skill                   | Description                    |
| ----------------------- | ------------------------------ |
| `api-patterns`          | REST, GraphQL, tRPC            |
| `nestjs-expert`         | NestJS modules, DI, decorators |
| `nodejs-best-practices` | Node.js async, modules         |
| `python-patterns`       | Python standards, FastAPI      |

### Database

| Skill             | Description                 |
| ----------------- | --------------------------- |
| `database-design` | Schema design, optimization |
| `prisma-expert`   | Prisma ORM, migrations      |

### TypeScript/JavaScript

| Skill               | Description                         |
| ------------------- | ----------------------------------- |
| `typescript-expert` | Type-level programming, performance |

### Cloud & Infrastructure

| Skill                   | Description               |
| ----------------------- | ------------------------- |
| `docker-expert`         | Containerization, Compose |
| `deployment-procedures` | CI/CD, deploy workflows   |
| `observability-patterns`| Monitoring, SLOs, runbooks |

### Testing & Quality

| Skill                   | Description              |
| ----------------------- | ------------------------ |
| `test-artifact-generation` | Test plans, BDD/Gherkin from ACs |
| `webapp-testing`           | E2E, Playwright                  |
| `tdd-workflow`             | Test-driven development          |
| `review-patterns`          | Code review + AI patterns        |
| `lint-and-validate`        | Linting, validation              |

### Security

| Skill                   | Description              |
| ----------------------- | ------------------------ |
| `vulnerability-scanner` | Security auditing, OWASP |

### Architecture & Planning

| Skill           | Description                |
| --------------- | -------------------------- |
| `app-builder`   | Full-stack app scaffolding |
| `architecture`  | System design patterns     |
| `plan-writing`  | Task planning, breakdown   |
| `brainstorming` | Socratic questioning       |

### Other

| Skill                     | Description               |
| ------------------------- | ------------------------- |
| `clean-code`              | Coding standards (Global)  |
| `behavioral-modes`        | Agent personas             |
| `parallel-agents`         | Multi-agent patterns       |
| `mcp-builder`             | Model Context Protocol     |
| `documentation-templates` | Doc formats (on-demand)    |
| `performance-profiling`   | Web Vitals, optimization   |
| `systematic-debugging`    | Troubleshooting            |

---

## 🔄 Workflows (11)

Slash command procedures. Invoke with `/command`.

| Command          | Description              |
| ---------------- | ------------------------ |
| `/brainstorm`    | Socratic discovery       |
| `/create`        | Create new features      |
| `/debug`         | Debug issues             |
| `/deploy`        | Deploy application       |
| `/enhance`       | Improve existing code    |
| `/orchestrate`   | Multi-agent coordination |
| `/plan`          | Task breakdown           |
| `/preview`       | Preview changes          |
| `/status`        | Check project status     |
| `/test`          | Run tests                |
| `/ui-ux-pro-max` | Design with 50 styles    |

---

## 🎯 Skill Loading Protocol

```plaintext
User Request → Skill Description Match → Load SKILL.md
                                            ↓
                                    Read references/
                                            ↓
                                    Read scripts/
```

### Skill Structure

```plaintext
skill-name/
├── SKILL.md           # (Required) Metadata & instructions
├── scripts/           # (Optional) Python/Bash scripts
├── references/        # (Optional) Templates, docs
└── assets/            # (Optional) Images, logos
```

### Enhanced Skills (with scripts/references)

| Skill               | Files | Coverage                            |
| ------------------- | ----- | ----------------------------------- |
| `ui-ux-pro-max`     | 27    | 50 styles, 21 palettes, 50 fonts    |
| `app-builder`       | 20    | Full-stack scaffolding              |

---

## � Scripts (2)

Master validation scripts that orchestrate skill-level scripts.

### Master Scripts

| Script          | Purpose                                 | When to Use              |
| --------------- | --------------------------------------- | ------------------------ |
| `checklist.py`  | Priority-based validation (Core checks) | Development, pre-commit  |
| `verify_all.py` | Comprehensive verification (All checks) | Pre-deployment, releases |

### Usage

```bash
# Quick validation during development
python .agent/scripts/checklist.py .

# Full verification before deployment
python .agent/scripts/verify_all.py . --url http://localhost:3000
```

### What They Check

**checklist.py** (Core checks):

- Security (vulnerabilities, secrets)
- Code Quality (lint, types)
- Schema Validation
- Test Suite
- UX Audit
- SEO Check

**verify_all.py** (Full suite):

- Everything in checklist.py PLUS:
- Lighthouse (Core Web Vitals)
- Playwright E2E
- Bundle Analysis
- Mobile Audit
- i18n Check

For details, see [scripts/README.md](scripts/README.md)

---

## 📊 Statistics

| Metric              | Value                         |
| ------------------- | ----------------------------- |
| **Total Agents**    | 20                            |
| **Total Skills**    | 36                            |
| **Total Workflows** | 11                            |
| **Total Scripts**   | 2 (master) + 18 (skill-level) |
| **Coverage**        | ~90% web/mobile development   |

---

## 🔗 Quick Reference

| Need     | Agent                 | Skills                                |
| -------- | --------------------- | ------------------------------------- |
| Web App  | `frontend-specialist` | react-best-practices, frontend-design |
| API      | `backend-specialist`  | api-patterns, nodejs-best-practices   |
| Mobile   | `mobile-developer`    | mobile-design                         |
| Database | `database-architect`  | database-design, prisma-expert        |
| Security | `security-auditor`    | vulnerability-scanner                 |
| Testing  | `test-engineer`       | test-artifact-generation, webapp-testing |
| Debug    | `debugger`            | systematic-debugging                  |
| Plan     | `project-planner`     | brainstorming, plan-writing           |
