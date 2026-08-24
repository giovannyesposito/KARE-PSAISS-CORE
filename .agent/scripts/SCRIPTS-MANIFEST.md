# SCRIPTS MANIFEST — KARE Agile Agent

> **PROPÓSITO:** Catálogo completo de todos os scripts Python em `.agent/scripts/`.
> Todo agente KARE DEVE consultar este manifesto antes de executar ou referenciar um script.
> **Última atualização:** Maio 2026 | **Versão:** 1.0.0

---

## REGRA DE ORGANIZAÇÃO

**Pasta canônica:** `.agent/scripts/`

Todos os scripts `.py` de suporte ao KARE Agile Agent residem EXCLUSIVAMENTE nesta pasta.
Scripts de outros contextos (exceto os listados na seção "Scripts Fora do Escopo") NÃO devem ser criados fora desta pasta.

---

## GRUPOS DE SCRIPTS

| Grupo | Prefixo/Padrão | Finalidade |
|---|---|---|
| **RAG / Context Engine** | `kare_rag`, `kare_contexto`, `rag_auth`, `cross_linker`, `decay_manager`, `wiki_enricher`, `brain_ingest`, `ingest_*` | Ingestão, busca e manutenção do grafo de conhecimento |
| **PPTX / Apresentações** | `gen_azure_arch_pptx` | Geração de slides e apresentações PowerPoint |
| **PDF** | `_gen_rso_pdf`, `export_pdf_demands`, `gen_pdf_padrão` | Exportação de artefatos para PDF |
| **Governança de Agentes** | `tool_guard`, `loop_guard`, `guardrail_gate`, `sql_guard` | Controle de permissões, detecção de loops e autorização de operações de alto risco |
| **Credenciais / Segurança** | `kare_credentials` | Gestão segura de tokens e credenciais |
| **Documentos / Conversão** | `ppt_to_kare` | Conversão de documentos para Markdown KARE |
| **Observabilidade / Diagnóstico** | `session_manager`, `verify_all`, `checklist`, `auto_preview` | Diagnóstico, validação e monitoramento |
| **Runtime Portability** | `kare_runner` | Execução de agentes KARE fora do VS Code via OpenAI/Anthropic/Ollama |
| **Skills & Contexto** | `skill_registry`, `context_optimizer` | Skill discovery dinâmico, TTL decay, relevance scoring e session check |
| **Temporários / Diagnóstico One-off** | `temp_*`, `_tmp_*` | Scripts utilitários criados pontualmente (não invocar em produção) |

---

## CATÁLOGO DETALHADO

### 🔵 RAG / CONTEXT ENGINE

---

#### `kare_rag.py`
- **Propósito:** CLI principal do Context Engine RAG — busca, ingestão, migração e status
- **Quando usar:** Toda vez que um agente precisar buscar contexto, ingerir artefato ou verificar o estado do RAG
- **Comandos:**
  ```
  python .agent/scripts/ai/kare_rag.py search "<termos>" [--limit N] [--context <slug>] [--max-tokens N]
  python .agent/scripts/ai/kare_rag.py ask "<pergunta>" [--limit N] [--max-tokens N]
  python .agent/scripts/ai/kare_rag.py ingest --title "..." --type artifact --context <slug> --file path/to/file.md
  python .agent/scripts/ai/kare_rag.py migrate
  python .agent/scripts/ai/kare_rag.py status
  python .agent/scripts/ai/kare_rag.py export
  python .agent/scripts/ai/kare_rag.py import
  ```
- **Tipos válidos para ingest:** `symbol | decision | artifact | concept | context`
- **Diferença search vs ask:** `search` → BM25; `ask` → Hybrid (BM25 + semântico + grafo)
- **Rerank + orçamento de tokens:** após o BM25, os resultados passam por um rerank local (boost por match exato de título/símbolo, sem modelo externo) e, se `--max-tokens` for informado, são truncados por ordem de relevância (corta os menos relevantes primeiro, nunca corta um item pela metade)
- **Agentes que usam:** todos (via context-resolver protocol), `delivery-observer`, `code-author`, `@kare-orchestrator`
- **Workflows que acionam:** `/create`, tasks.json (`KARE: Export/Import/Rebuild RAG`)
- **Dependências:** `rag_auth.py` (auth JWT), Context Engine rodando em `http://localhost:8000`
- **⚠️ Requer:** RAG API ativa (`KARE: Start Context Engine`)

---

#### `rag_auth.py`
- **Propósito:** Módulo central de autenticação JWT para todos os scripts cliente do RAG
- **Quando usar:** Importar em qualquer script que faça chamadas à RAG API
- **Interface:**
  ```python
  from rag_auth import get_auth_headers   # para scripts urllib
  from rag_auth import rag_session        # para scripts requests
  ```
- **Agentes que usam:** Não acionado diretamente — importado por outros scripts
- **Dependências internas:** Chamado por `cross_linker.py`, `decay_manager.py`, `wiki_enricher.py`, `ingest_local.py`, `[REMOVIDO] ingest_kare_project.py`, `kare_rag.py`
- **Variáveis de ambiente requeridas:** `JWT_SECRET_KEY`, `RAG_API_USER`, `RAG_API_PASSWORD`

---

#### `kare_contexto.py`
- **Propósito:** Gerencia e exibe o contexto de iniciativas KARE — recupera nós, arestas e metadados do grafo
- **Quando usar:** Quando um agente precisa listar ou inspecionar o contexto persistido de uma iniciativa
- **Agentes que usam:** `@kare-orchestrator`, `delivery-observer`
- **Dependências:** `rag_auth.py`, RAG API

---

#### `brain_ingest.py`
- **Propósito:** Ingesta arquivos de conhecimento para o cofre Obsidian por domínio (arquitetura, sistemas, integrações, APIs, etc.)
- **Quando usar:** Para persistir documentos estruturados no Obsidian com links para anexos
- **Comando:**
  ```
  python .agent/scripts/ai/brain_ingest.py . --input <path> --domain <domain_key> --context <slug>
  ```
- **Domínios suportados:** `arquitetura`, `sistemas`, `integracoes`, `apis`, `observabilidade`, `stakeholders`, `projetos`
- **Agentes que usam:** agentes de discovery e documentação
- **Referenciado em:** `.agent/rules/kare.instructions.md`

---

#### `cross_linker.py`
- **Propósito:** Detecta relações semânticas entre nós WIKI_PAGE e cria arestas `SIMILAR_TO` e `REUSES_PATTERN` no grafo
- **Quando usar:** Após ingestão em massa, para enriquecer o grafo com relacionamentos automáticos
- **Comandos:**
  ```
  python .agent/scripts/ai/cross_linker.py --all [--threshold 0.82] [--dry-run]
  python .agent/scripts/ai/cross_linker.py --node-id <id>
  ```
- **Agentes que usam:** Acionado pelo scheduler/kare_start.ps1
- **Dependências:** `rag_auth.py`, RAG API, modelo de embeddings ativo

---

#### `decay_manager.py`
- **Propósito:** Gerencia ciclo de vida e confiança de WIKI_PAGEs — aplica decay de conhecimento, detecta nós stale
- **Quando usar:** Periodicamente (via kare_start.ps1) ou manualmente para verificar qualidade do grafo
- **Comandos:**
  ```
  python .agent/scripts/sync/decay_manager.py --check
  python .agent/scripts/sync/decay_manager.py --list-stale
  python .agent/scripts/sync/decay_manager.py --refresh-stale
  ```
- **Regras:** confidence < 0.60 → stale; confidence < 0.40 → critical
- **Agentes que usam:** Acionado pelo scheduler (`kare_start.ps1`)
- **Dependências:** `rag_auth.py`, RAG API

---

#### `wiki_enricher.py`
- **Propósito:** Enriquece WIKI_PAGEs stale com novo conteúdo do Confluence, atualizando confidence_score
- **Quando usar:** Após `decay_manager.py --list-stale` identificar nós a serem re-enriquecidos
- **Agentes que usam:** Acionado pelo scheduler (`kare_start.ps1`)
- **Dependências:** `rag_auth.py`, RAG API, MCP Atlassian ativo

---

### 🟣 CONFLUENCE

---

> ✅ **REMOVIDO:** `confluence_sync_runner.py` e o workflow `/sync-confluence` — eram específicos do espaço Confluence de um programa/cliente (page_id fixo), fora do escopo da plataforma genérica KARE-SPEC.

---

#### `[REMOVIDO] ingest_kare_project.py`
- **Propósito:** Ingere documentos-base de um contexto de negócio (arquitetura macro, modelo operacional) como ARTIFACT perene
- **Quando usar:** Bootstrap inicial ou quando os documentos-base do contexto forem atualizados
- **Comando:**
  ```
  python .agent/scripts/ai/[REMOVIDO] ingest_kare_project.py
  ```
- **Dependências:** `rag_auth.py`, RAG API, arquivos em `uploads/KARE-programa/`

---

#### `ingest_local.py`
- **Propósito:** Ingere arquivos locais (PROJECT_CONTEXT.md, CONTEXTO-*.md, arquitetura) no RAG sem depender do Confluence
- **Quando usar:** Quando há artefatos locais que precisam estar no grafo mas não vieram do Confluence
- **Estruturas reconhecidas:** `uploads/INI-XXX/`, `uploads/KARE-*/`, etc.
- **Dependências:** `rag_auth.py`, RAG API

---

### 🟡 PPTX / APRESENTAÇÕES

---

> ✅ **REMOVIDO:** `gen_roadmap_pptx.py`, `generate_pptx.py`, `generate_kare_deck.py`, `gen_rag_evolution_deck.py`, `gen_kare_analise_cruzada.py`, `gen_quebra_issues_pptx.py`, `gen_kare_timeline_slide.py` — geradores de deck/slide construídos para entregáveis de um programa/cliente específico (paths hardcoded, marcos e paletas exclusivas do engajamento). Fora do escopo da plataforma genérica KARE-SPEC.

---

#### `gen_azure_arch_pptx.py`
- **Propósito:** Gera apresentação PowerPoint minimalista de Arquitetura Azure do KARE Agile Agent (5 slides)
- **Quando usar:** Criar deck de arquitetura Azure para captação de recursos junto à diretoria ou apresentações técnicas
- **Slides gerados:** Capa | Arquitetura Alto Nível | Stack Tecnológica | Fluxo Teams | Roadmap
- **Paleta:** Azure (#0078D4) + Accent (#660099) — identidade visual corporativa
- **Comandos:**
  ```
  python .agent/scripts/generators/gen_azure_arch_pptx.py
  python .agent/scripts/generators/gen_azure_arch_pptx.py --dest "C:\...\saida.pptx"
  ```
- **Saída padrão:** `_outputs/kare-azure/upstream/KARE_Azure_Architecture.pptx`
- **Agentes que usam:** `@kare-orchestrator`, `delivery-observer`

---

### 🔴 PDF

---

#### `_gen_rso_pdf.py`
- **Propósito:** **Script oficial e exclusivo** para geração de PDFs de RSO (Relatório de Status Operacional)
- **⚠️ REGRA INEGOCIÁVEL:** Todo PDF de RSO DEVE ser gerado com este script. Nenhum outro método é permitido.
- **Comandos:**
  ```
  python ".agent\scripts\_gen_rso_pdf.py" --src "C:\...\RSO INI-004.md" --dest "C:\...\RSO INI-004.pdf"
  python ".agent\scripts\_gen_rso_pdf.py" --src "C:\...\RSO INI-004.md"
  ```
- **Template visual:** H1=16pt cinza, H2=13pt azul (20,80,160), tabelas border=1, body=9pt
- **Referenciado em:** `.agent/rules/delivery-standards.instructions.md` (PARTE 3 — RSO PDF, regra CRITICAL)

---

#### `export_pdf_demands.py`
- **Propósito:** Converte artefatos Markdown das demandas processadas em PDF, replicando estrutura no OneDrive
- **Quando usar:** Exportar lote de artefatos de demandas para PDF e sincronizar com OneDrive
- **Dependências:** `pypandoc` ou `weasyprint` (fallback entre si)

---

#### `gen_pdf_padrão.py`
- **Propósito:** Exporta qualquer arquivo Markdown para PDF com visual fiel ao preview VS Code / GitHub (tema claro)
- **Quando usar:** Gerar PDF de README, RELEASE-NOTES, PRD, ADR ou qualquer artefato Markdown com aparência profissional
- **Stack:** `fpdf2` + `Markdown` + Calibri/Consolas TTF (Unicode completo, sem dependências externas adicionais)
- **Visual:** Headers hierárquicos H1–H6, code blocks com fundo cinza, tabelas sombreadas, blockquotes com barra lateral, HR estilo GitHub
- **Comandos:**
  ```
  python ".agent\scripts\gen_pdf_padrão.py" --src README.md
  python ".agent\scripts\gen_pdf_padrão.py" --src README.md --dest "C:\path\README.pdf"
  python ".agent\scripts\gen_pdf_padrão.py" --src README.md --dest "C:\pasta\"  # pasta
  ```
- **Diferença de `_gen_rso_pdf.py`:** Script RSO usa template fixo com identidade visual padronizada do projeto. Este script replica o preview Markdown genérico.
- **Criado em:** Maio 2026

---

### 🟢 GOVERNANÇA DE AGENTES

---

#### `guardrail_gate.py`
- **Propósito:** Controle de autorização para operações de alto risco — bloqueia execução sem aprovação explícita de operador humano
- **Quando usar:** Antes de qualquer operação CRÍTICA ou ALTA (sandbox de código, criação de agentes, ingestão RAG, IaC, red team, GCP jobs)
- **Comandos CLI:**
  ```
  python .agent/scripts/guards/guardrail_gate.py check <skill-name>
  python .agent/scripts/guards/guardrail_gate.py approve <skill-name> --reason "<motivo>"
  python .agent/scripts/guards/guardrail_gate.py status
  python .agent/scripts/guards/guardrail_gate.py log [--last N]
  python .agent/scripts/guards/guardrail_gate.py revoke <skill-name>
  ```
- **Uso programático:**
  ```python
  from guardrail_gate import require_authorization, GuardrailDenied
  require_authorization("code-author-autogen")   # lança GuardrailDenied se não autorizado
  ```
- **Skills monitoradas:** `code-author-autogen` (CRITICAL), `agent-builder-autogen` (CRITICAL), `rag-continual-learning` (CRITICAL), `delivery-observer-sql` (CRITICAL), `security-red-team` (HIGH), `azure-iac-engineer` (HIGH), `gcp-analytics-agent` (HIGH), `agent-simulation-testing` (MEDIUM)
- **Funções auxiliares:** `sanitize_rag_content(text, source)` → anti-poisoning; `check_sql_safety(query)` → pré-validação SELECT
- **Audit log:** `.agent/.guardrails/authorizations.jsonl` + `.agent/.guardrails/audit.jsonl`
- **TTL por skill:** CRITICAL=30-120 min | HIGH=60 min | MEDIUM=120 min
- **Referenciado em:** `code-author-autogen/SKILL.md`, `agent-builder-autogen/SKILL.md`, `delivery-observer-sql/SKILL.md`, `rag-continual-learning/SKILL.md`, `security-red-team/SKILL.md`, `azure-iac-engineer/SKILL.md`, `gcp-analytics-agent/SKILL.md`

---

#### `sql_guard.py`
- **Propósito:** Enforcer de segurança SQL para queries geradas por LLM — garante somente SELECT, bloqueia DDL/DML destrutivo
- **Quando usar:** Toda query gerada por `delivery-observer-sql` antes de execução
- **Comandos CLI:**
  ```
  python .agent/scripts/guards/sql_guard.py validate "<query SQL>"
  python .agent/scripts/guards/sql_guard.py log [--last N]
  ```
- **Uso programático:**
  ```python
  from sql_guard import safe_execute, open_readonly_connection, SQLGuardError
  conn = open_readonly_connection(".specify/session_store.db")  # read-only URI
  rows = safe_execute(conn, generated_sql)   # valida + executa + audita
  ```
- **Bloqueados:** `DELETE DROP UPDATE INSERT ALTER TRUNCATE ATTACH PRAGMA CREATE -- /*`
- **Limite de rows:** 5.000 por query (com aviso de truncamento)
- **Modo conexão:** `sqlite3.connect(uri, uri=True)` com `?mode=ro` — impossível escrever
- **Audit log:** `.agent/.guardrails/sql_audit.jsonl`
- **Referenciado em:** `delivery-observer-sql/SKILL.md`

---

#### `secret_scan.py`
- **Propósito:** Varredura de credenciais em texto plano em todo o conteúdo versionado do repositório (reaproveita os padrões do hook `pre-commit`, mas cobre `git ls-files` inteiro, não só um diff)
- **Quando usar:** Rodado automaticamente pelo job `secret-scan` do CI (`.github/workflows/ci.yml`); pode rodar manualmente para auditoria pontual
- **Comandos CLI:**
  ```
  python .agent/scripts/guards/secret_scan.py
  python .agent/scripts/guards/secret_scan.py --path <arquivo-ou-pasta>
  ```
- **Uso programático:**
  ```python
  from secret_scan import scan_file
  hits = scan_file(Path("algum_arquivo.py"))  # lista de linhas suspeitas, vazia se limpo
  ```
- **Referenciado em:** `.github/workflows/ci.yml` (job `secret-scan`), `tests/test_secret_scan.py`

---

#### `tool_guard.py`
- **Propósito:** Aplicação programática de permissões de ferramentas por agente — impede uso de tools não autorizadas
- **Quando usar:** Verificar se um agente tem permissão para usar uma ferramenta; auditar chamadas
- **Comandos CLI:**
  ```
  python .agent/scripts/guards/tool_guard.py check <agent-name> <tool-name>
  python .agent/scripts/guards/tool_guard.py list <agent-name>
  python .agent/scripts/guards/tool_guard.py audit [--last N]
  python .agent/scripts/guards/tool_guard.py agents
  ```
- **Uso programático:**
  ```python
  from tool_guard import ToolGuard
  guard = ToolGuard("code-author")
  guard.check("Bash")        # ToolPermissionError se não autorizado
  @guard.require("Bash")     # decorator
  ```
- **Audit log:** `.agent/config/.tool_guard_audit.jsonl`
- **Agentes mapeados:** 20 agentes KARE-SPEC
- **Referenciado em:** `.agent/rules/orchestration.instructions.md` (seção Tool Guard)

---

#### `loop_guard.py`
- **Propósito:** Detecção de loops de agentes (HITL Guard) e timeout de sessão (>120min)
- **Quando usar:** Incluir em pipelines de orquestração para prevenir loops infinitos
- **Regra dos 3 strikes:** 4ª repetição da mesma ação → `LoopDetectedError`
- **Uso programático:**
  ```python
  from loop_guard import get_session_tracker, LoopDetectedError
  tracker = get_session_tracker("minha-sessao", max_retries=3)
  tracker.record("Bash", {"cmd": "pytest tests/"})
  ```
- **Audit log:** `.agent/config/.loop_guard_audit.jsonl`
- **Referenciado em:** `.agent/rules/orchestration.instructions.md` (seção Loop Detection), `.agent/workflows/compress-session.prompt.md`

---

#### `verify_loop.py`
- **Propósito:** Loop de verificação-até-critério — chama uma função de tentativa e uma de validação repetidamente até atingir `PASS` (score ≥80, mesma escala do `@quality-guardian`) ou até `loop_guard.ActionTracker` detectar que a mesma falha está se repetendo sem progresso (escala para HITL nesse caso)
- **Quando usar:** Ciclos de tentativa-e-validação com critério de qualidade objetivo — ex.: `@code-author` (tentativa) + `@quality-guardian` (validação) no `/implement`
- **Uso programático:**
  ```python
  from verify_loop import run_until_criteria
  outcome = run_until_criteria(attempt_fn, verify_fn, max_retries=3)
  # outcome.passed / outcome.escalated / outcome.attempts / outcome.last_verification
  ```
- **Referenciado em:** `.agent/workflows/implement.prompt.md`

---

### 🔐 CREDENCIAIS / SEGURANÇA

---

#### `kare_sanitizer.py`
- **Propósito:** Defesa contra Prompt Injection — sanitiza conteúdo de `uploads/` antes de injetar no RAG
- **Quando usar:** Antes de ingerir qualquer documento externo no RAG via `kare_rag.py ingest` ou `kare_contexto.py`
- **Comandos:**
  ```
  python .agent/scripts/guards/kare_sanitizer.py --file uploads/canvas.md
  python .agent/scripts/guards/kare_sanitizer.py --dir uploads/ini-518/
  python .agent/scripts/guards/kare_sanitizer.py --text "texto a verificar"
  python .agent/scripts/guards/kare_sanitizer.py --file canvas.md --json
  ```
- **Padrões detectados:** INJ-001 a INJ-008 (override de persona, bypass de segurança, exfiltração, etc.)
- **Dados sensíveis:** SEN-001 a SEN-005 (tokens Atlassian, Bearer, senhas, API keys)
- **Exit code:** 0 = seguro; 1 = ameaças detectadas
- **Uso como módulo:**
  ```python
  from kare_sanitizer import sanitize_content
  result = sanitize_content(raw_text)
  if result.is_safe:
      ingest(result.clean_text)
  ```
- **Agentes que usam:** `@kare-orchestrator` (pré-ingestão), `kare_contexto.py` (importação futura)
- **Referenciado em:** Plano de evolução arquitetural (Fase 1 — Prompt Injection Defense)

---

#### `kare_telemetry.py`
- **Propósito:** Shim de compatibilidade — redireciona todos os comandos para `kare_rag.py telemetry` (SQLite)
- **Fonte canônica:** `kare_rag.py telemetry` → `kare_telemetry.db`
- **Coleta automática:** search/ingest auto-instrumentados em `kare_rag.py`; session-start via VS Code task; post-commit via git hook; consolidação a cada 15 min via Windows Task Scheduler
- **Comandos canônicos:**
  ```
  python .agent/scripts/ai/kare_rag.py telemetry log --agent X --action-type query
  python .agent/scripts/ai/kare_rag.py telemetry stats [--days N] [--agent X] [--user U]
  python .agent/scripts/ai/kare_rag.py telemetry session-start
  python .agent/scripts/ai/kare_rag.py telemetry session-end --session-id N
  ```
- **Banco:** `.specify/rag/kare_telemetry.db` (SQLite standalone)

---

---

#### `kare_runner.py`
- **Propósito:** Runtime Portability Layer — executa agentes KARE fora do VS Code via qualquer LLM
- **Quando usar:** CI/CD pipelines, automação, testar agentes contra OpenAI/Anthropic/Ollama
- **Comandos:**
  ```
  python .agent/scripts/infra/kare_runner.py list
  python .agent/scripts/infra/kare_runner.py run --agent story-crafter --prompt "..." --adapter openai --api-key $KEY --model gpt-4o
  python .agent/scripts/infra/kare_runner.py run --agent project-classifier --prompt "..." --adapter anthropic --api-key $KEY
  python .agent/scripts/infra/kare_runner.py run --agent backlog-architect --prompt "..." --adapter ollama --model llama3.1
  python .agent/scripts/infra/kare_runner.py health
  ```
- **Adapters disponíveis:** `openai` (default), `anthropic`, `ollama`, `copilot` (stub VS Code)
- **Dependências:** stdlib apenas (urllib, json, abc) — sem pip install necessário
- **Variáveis de ambiente:** `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `KARE_API_BASE`
- **Referenciado em:** Plano de evolução arquitetural (Fase 3 — Runtime Portability)

---

#### `skill_registry.py`
- **Propósito:** Skill Registry Dinâmico — escaneia `.agent/skills/`, constrói `SKILL-REGISTRY.json` e oferece lookup semântico por tarefa
- **Quando usar:** Descobrir skills relevantes para uma tarefa, auditar skills sem agente referenciando, validar consistência agente→skill
- **Comandos:**
  ```
  python .agent/scripts/ai/skill_registry.py scan
  python .agent/scripts/ai/skill_registry.py query "criar user story com ACs"
  python .agent/scripts/ai/skill_registry.py list
  python .agent/scripts/ai/skill_registry.py audit --unused
  python .agent/scripts/ai/skill_registry.py validate
  ```
- **Output:** `.agent/skills/SKILL-REGISTRY.json` com 65 skills, triggers e agentes
- **Dependências internas:** Lê frontmatter de `SKILL.md` em cada skill directory
- **Referenciado em:** Plano de evolução arquitetural (Fase 3 — Skill Registry Dinâmico)

---

#### `context_optimizer.py`
- **Propósito:** Context Window Optimization — TTL decay, relevance scoring e session compression check
- **Quando usar:** Antes de grandes execuções, para identificar nós stale, priorizar contexto relevante e verificar se sessão precisa de `/compress-session`
- **Comandos:**
  ```
  python .agent/scripts/ai/context_optimizer.py optimize --context ini-518
  python .agent/scripts/ai/context_optimizer.py decay --context ini-518 [--dry-run]
  python .agent/scripts/ai/context_optimizer.py stale --context ini-518
  python .agent/scripts/ai/context_optimizer.py score --context ini-518 --query "payment gateway" --top 10
  python .agent/scripts/ai/context_optimizer.py session-check --session-start "2026-05-14T09:00:00"
  python .agent/scripts/ai/context_optimizer.py report --context ini-518
  ```
- **Exit codes:** 0 = OK, 1 = erro, 2 = sessão precisa de compressão
- **Dependências internas:** `decay_manager.py` (TTL decay), RAG API (`/nodes`)
- **Variáveis de ambiente:** `KARE_API_BASE` (default: `http://localhost:8000`)
- **Referenciado em:** Plano de evolução arquitetural (Fase 3 — Context Window Optimization)

---

#### `kare_credentials.py`
- **Propósito:** Gerenciador seguro de credenciais KARE com AES-256-GCM
- **Quando usar:** Setup inicial de credenciais, verificação de status, recuperação de valores criptografados
- **Comandos:**
  ```
  python .agent/scripts/infra/kare_credentials.py setup
  python .agent/scripts/infra/kare_credentials.py check
  python .agent/scripts/infra/kare_credentials.py setup-rag
  python .agent/scripts/infra/kare_credentials.py check figma
  ```
- **Arquivos:** Chave em `%USERPROFILE%\kare.key` (fora do projeto); credenciais em `.config\.venv\mcp-atlassian.enc`
- **Referenciado em:** `setup.ps1`, `kare_start.ps1`

---

### 📄 DOCUMENTOS / CONVERSÃO

---

#### `ppt_to_kare.py`
- **Propósito:** Converte documentos (PPTX, DOCX, PDF, XLSX) para Markdown estruturado com frontmatter KARE
- **Quando usar:** Antes de ingerir documentos no RAG — converter canvas, briefs e apresentações
- **Formatos suportados:** `.pptx`, `.ppt`, `.docx`, `.doc`, `.pdf`, `.xlsx`
- **Comandos:**
  ```
  python .agent/scripts/generators/ppt_to_kare.py input.pptx
  python .agent/scripts/generators/ppt_to_kare.py canvas.pptx --output uploads/CANVAS.md --kare-context
  python .agent/scripts/generators/ppt_to_kare.py brief.docx --output uploads/BRIEF.md --kare-context
  ```
- **Referenciado em:** `.agent/workflows/create.prompt.md` (step 3)

---

### 🔎 OBSERVABILIDADE / DIAGNÓSTICO

---

#### `session_manager.py`
- **Propósito:** Analisa estado do projeto — detecta tech stack, rastreia estatísticas de arquivos, fornece resumo de sessão
- **Quando usar:** Início de sessão para identificar contexto técnico do projeto
- **Comandos:**
  ```
  python .agent/scripts/telemetry/session_manager.py status [path]
  python .agent/scripts/telemetry/session_manager.py info [path]
  ```

---

#### `verify_all.py`
- **Propósito:** Suite completa de validação — segurança, lint, testes, UX, SEO, Lighthouse, E2E. Para uso pré-deploy.
- **Quando usar:** Antes de deployments ou releases maiores
- **Comando:**
  ```
  python .agent/scripts/guards/verify_all.py . --url <URL>
  ```
- **Referenciado em:** `.agent/docs/ARCHITECTURE.md`

---

#### `checklist.py`
- **Propósito:** Orquestra validações incrementais em ordem de prioridade (P0 Segurança → P6 Performance)
- **Quando usar:** Durante desenvolvimento para validação incremental
- **Comandos:**
  ```
  python .agent/scripts/generators/checklist.py .
  python .agent/scripts/generators/checklist.py . --url <URL>
  ```
- **Referenciado em:** `.agent/docs/ARCHITECTURE.md`

---

#### `auto_preview.py`
- **Propósito:** Gerencia servidor de desenvolvimento local (start/stop/status) para preview da aplicação
- **Quando usar:** Para iniciar ou verificar servidor de preview local
- **Comandos:**
  ```
  python .agent/scripts/generators/auto_preview.py start [port]
  python .agent/scripts/generators/auto_preview.py stop
  python .agent/scripts/generators/auto_preview.py status
  ```

---

### 🗃️ TEMPORÁRIOS / DIAGNÓSTICO ONE-OFF

> **⚠️ ATENÇÃO:** Estes scripts foram criados para diagnóstico pontual. NÃO devem ser invocados em produção ou por agentes automaticamente.

---

#### `_tmp_download_ini004.py`
- **Propósito:** Download de anexo da issue INI-004 do Jira (uso pontual)
- **Status:** Temporário — criado para diagnóstico em sessão específica
- **⚠️ Viola a regra MCP-FIRST:** usa `requests` direto com verify=False. Não usar.

---

#### `temp_excel.py`
- **Propósito:** Lê arquivo Excel de Metas 2026 do OneDrive e imprime conteúdo (diagnóstico)
- **Status:** One-off — caminho hardcoded para OneDrive do usuário

---

#### `temp_read_excel.py`
- **Propósito:** Versão melhorada de `temp_excel.py` — lê Excel de Metas 2026 com melhor formatação
- **Status:** One-off — caminho hardcoded para OneDrive do usuário

---

#### `temp_read_sqlite.py`
- **Propósito:** Lê e exibe conteúdo do banco SQLite do Context Engine (`kare_context.db`)
- **Status:** One-off — útil para diagnóstico do estado do banco de dados

---

#### `temp_sqlite.py`
- **Propósito:** Lê e exibe conteúdo de banco SQLite com listagem de tabelas
- **Status:** One-off — diagnóstico de banco de dados local

---

## SCRIPTS FORA DO ESCOPO `.agent/scripts/`

Os seguintes conjuntos de scripts existem no projeto mas NÃO são scripts de suporte ao agente — ficam nas suas pastas originais:

### `.agent/skills/*/scripts/` — Scripts de Skills Especializadas
Cada skill contém seus próprios scripts auxiliares. NÃO mover.

| Script | Skill | Propósito |
|---|---|---|
| `playwright_runner.py` | `webapp-testing` | Runner E2E com Playwright |
| `ux_audit.py` | `frontend-design` | Auditoria UX |
| `accessibility_checker.py` | `frontend-design` | Verificação de acessibilidade |
| `lint_runner.py` | `lint-and-validate` | Runner de linting |
| `type_coverage.py` | `lint-and-validate` | Cobertura de tipos |
| `schema_validator.py` | `database-design` | Validação de schema |
| `api_validator.py` | `api-patterns` | Validação de padrões de API |
| `lighthouse_audit.py` | `performance-profiling` | Auditoria Lighthouse |
| `security_scan.py` | `vulnerability-scanner` | Scanner de segurança |
| `geo_checker.py` | `geo-fundamentals` | Verificações geográficas |
| `i18n_checker.py` | `i18n-localization` | Verificação de internacionalização |
| `react_performance_checker.py` | `nextjs-react-expert` | Performance React |
| `convert_rules.py` | `nextjs-react-expert` | Conversão de regras ESLint |
| `mobile_audit.py` | `mobile-design` | Auditoria de design mobile |
| `test_runner.py` | `testing-patterns` | Runner de testes |
| `seo_checker.py` | `seo-fundamentals` | Verificação SEO |

### `.agent/.shared/ui-ux-pro-max/scripts/` — Scripts UI/UX Compartilhados
| Script | Propósito |
|---|---|
| `core.py` | Utilitários core UI/UX |
| `design_system.py` | Integração com design system |
| `search.py` | Busca em design tokens e componentes |

✅ **DELETADO:** `.agent/mcp-servicenow/` (MCP ServiceNow — removido na versao-pura)
✅ **DELETADO:** `.agent/mcp_email/` (MCP e-mail — removido na versao-pura)
✅ **DELETADO:** `uploads/ini-361/gerar_rso_ini361_pdf.py` (violação de regra RSO PDF Export)

---

## MAPA DE ACIONAMENTOS

### Via VS Code Tasks (`.vscode/tasks.json`)
| Task | Script | Trigger |
|---|---|---|
| `KARE: Start Context Engine` | `kare_start.ps1` (orquestra scripts Python) | Abertura da pasta |
| `KARE: Export RAG Snapshot` | `kare_rag.py export` | Manual |
| `KARE: Import RAG Snapshot` | `kare_rag.py import` | Manual |
| `KARE: Rebuild RAG Index` | `kare_rag.py migrate` | Manual |
| `KARE: Status` | `kare_rag.py status` | Manual |

### Via Workflows (`.agent/workflows/`)
| Workflow/Comando | Script Acionado |
|---|---|
| `/create` | `ppt_to_kare.py` (se houver PPT) |
| `/compress-session` | referencia `loop_guard.py` (reset) |

### Via Agentes (`.agent/agents/`)
| Agente | Script Acionado | Contexto |
|---|---|---|
| `delivery-observer` | `kare_rag.py search/ask/ingest` | Busca e registro de status |
| `code-author` | `kare_rag.py search/ask/ingest` | Busca de decisões e padrões |
| Todos via context-resolver | `kare_rag.py ask` | Protocolo de 3 cenários |

### Via Rules (`.agent/rules/`)
| Rule | Script Referenciado | Tipo |
|---|---|---|
| `delivery-standards.instructions.md` | `_gen_rso_pdf.py` | OBRIGATÓRIO (regra CRITICAL) |
| `orchestration.instructions.md` | `tool_guard.py`, `loop_guard.py` | Governança |
| `kare.instructions.md` | `brain_ingest.py` | Ingestão |

---

## CHECKLIST ANTES DE CRIAR NOVO SCRIPT

- [ ] O script realmente precisa existir como arquivo `.py` separado?
- [ ] Já existe um script que faz algo similar? (verificar este manifesto)
- [ ] O script vai residir em `.agent/scripts/`?
- [ ] O script viola a regra **MCP-FIRST**? (não usar requests/urllib para Jira/Confluence)
- [ ] O script tem docstring explicando propósito, uso e comandos?
- [ ] Após criar, atualizar este `SCRIPTS-MANIFEST.md`

---

---

## SCRIPTS POWERSHELL — `.agent/scripts/infra/`

> Scripts `.ps1` organizados na subpasta `ps1/`. Acionados via VS Code tasks, mcp.json ou manualmente.
> `publish_confluence.ps1` foi **REMOVIDO** em Maio 2026 — violava a regra MCP-FIRST (usava REST API direta).

### Índice de Scripts PS1

| Script | Finalidade | Acionamento |
|---|---|---|
| `kare_start.ps1` | Inicia o KARE Context Engine (API RAG) | `.vscode/tasks.json` (runOn: folderOpen) |
| `configure_mcp_atlassian.ps1` | Setup interativo das credenciais Atlassian (AES-256-GCM) | Manual / primeira vez |
| `install_hooks.ps1` | Instala git hooks de segurança | Manual após cada clone |
| `build_copilot_studio_package.ps1` | Empacota agentes para Copilot Studio | Manual / release |

> `start_mcp_atlassian.ps1` e `validate-workflows.ps1` foram **substituídos** por
> `start_mcp_atlassian.py` e `validate_workflows.py` (mesma pasta `infra/`) para
> funcionar igual em Windows/Mac/Linux — ver seção "RAG / CONTEXT ENGINE" /
> "GOVERNANÇA" abaixo para o Python equivalente. Não há mais versão `.ps1` dos dois.

### Detalhamento por Script

#### `register_metrics_task.ps1`
```powershell
# Setup inicial (uma vez por máquina)
powershell -ExecutionPolicy Bypass -File .agent\scripts\infra\register_metrics_task.ps1

# Ver status da tarefa agendada
.\register_metrics_task.ps1 -Status

# Forçar execução imediata (teste)
.\register_metrics_task.ps1 -RunNow

# Remover a tarefa
.\register_metrics_task.ps1 -Unregister
```
- Registra "KARE Telemetry" no Windows Task Scheduler (pasta `\KARE\`)
- Executa `kare_rag.py telemetry stats --quiet` a cada 15 minutos, como usuário logado, sem janela
- **Detecção automática de Python:** tenta `python` primeiro; se falhar, tenta `py`
- Trigger com `StartWhenAvailable` — garante execução mesmo se a máquina estava suspensa
- **Referenciado em:** setup.ps1, onboarding KARE distribuído

#### `kare_start.ps1`
```powershell
# Uso: automático via tasks.json ao abrir o workspace
powershell -ExecutionPolicy Bypass -File .agent\scripts\infra\kare_start.ps1
```
- Verifica se os bancos RAG em `.specify/rag/` estão acessíveis
- Executa `kare_rag.py migrate` se bancos não existirem (primeiro uso)

#### `start_mcp_atlassian.py` (`.agent/scripts/infra/`)
```bash
# Uso: automático via .vscode/mcp.json
# NÃO executar diretamente
```
- Resolve o binário `mcp-atlassian` (.venv ou global) — cross-platform
- Descriptografa credenciais via `kare_credentials.py` (AES-256-GCM, import direto)
- Injeta credenciais como variáveis de ambiente **apenas nesta sessão**
- Inicia o servidor MCP via stdio (`subprocess.run`)

#### `configure_mcp_atlassian.ps1`
```powershell
powershell -ExecutionPolicy Bypass -File .agent\scripts\infra\configure_mcp_atlassian.ps1
```
- Setup interativo: solicita URL, username e API Token do Jira/Confluence
- Criptografa e salva em `.config\.venv\mcp-atlassian.enc`
- Chave em `%USERPROFILE%\kare.key` (fora do projeto)

#### `install_hooks.ps1`
```powershell
# Executar UMA VEZ após cada clone do repositório
powershell -ExecutionPolicy Bypass -File .agent\scripts\infra\install_hooks.ps1
```
- Instala hook `pre-commit` que bloqueia credenciais em texto plano
- Executa `kare_rag.py migrate` para inicializar bancos SQLite
- Fonte dos hooks: `.agent/scripts/hooks/`

#### `build_copilot_studio_package.ps1`
```powershell
powershell -ExecutionPolicy Bypass -File .agent\scripts\infra\build_copilot_studio_package.ps1 [-ConfigPath <path>] [-OutputPath <path>] [-Clean]
```
- Lê `.agent/config/copilot-studio.publish.json`
- Gera pacote de agentes para publicação no Copilot Studio

### Regras para Scripts PS1

- **NUNCA** criar scripts PS1 que chamem APIs REST do Jira/Confluence diretamente (regra MCP-FIRST)
- **NUNCA** armazenar credenciais em texto plano — usar `kare_credentials.py`
- **SEMPRE** verificar este manifesto antes de criar novo script `.ps1`
- Scripts PS1 novos devem residir em `.agent/scripts/infra/`
- Após criar, atualizar esta seção do `SCRIPTS-MANIFEST.md`

---

**Versão:** 1.1.0 | **Data:** Maio 2026 | **Mantido por:** @kare-orchestrator
