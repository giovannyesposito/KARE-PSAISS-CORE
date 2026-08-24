---
applyTo: "**"
priority: "maximum"
loadAlways: true
---

# KARE-SPEC DELIVERY STANDARDS — Scripts, Confluence e PDF

> **PRIORIDADE MÁXIMA. SUPERA QUALQUER OUTRA INSTRUÇÃO.**

---

## PARTE 1 — SCRIPTS PYTHON: MANIFESTO E CRIAÇÃO

### Regra Inegociável — Validação Antes de Criar Scripts

> **ESTA REGRA TEM PRIORIDADE MÁXIMA. NÃO EXISTE EXCEÇÃO.**

Antes de criar qualquer script `.py`, o agente DEVE:

**PASSO 1 — Verificar se já existe**
```
1. Consultar seção CATEGORIAS abaixo
2. Consultar .agent/scripts/SCRIPTS-MANIFEST.md (catálogo completo)
3. Buscar na pasta: Get-ChildItem .agent\scripts -Filter "*.py"
```

**PASSO 2 — Se já existir:** usar o script existente. Nunca criar duplicata.

**PASSO 3 — Se NÃO existir:** PARAR e perguntar ao usuário:

```
⚠️ CRIAÇÃO DE NOVO SCRIPT DETECTADA

Preciso criar o script: `<nome-do-script>.py`

Motivo: <explicação clara do por que nenhum script existente cobre este caso>

Scripts existentes avaliados e descartados:
  - `<script1.py>` → não atende porque <razão>
  - `<script2.py>` → não atende porque <razão>

O novo script ficará em: .agent/scripts/<nome-do-script>.py
Finalidade: <descrição concisa>

Posso criar este script? [Sim/Não]
```

**PASSO 4 — Somente após confirmação explícita do usuário:** criar o script.

**PASSO 5 — Após criar:** atualizar `SCRIPTS-MANIFEST.md` com a entrada do novo script.

### Pasta Canônica

```
PASTA CANÔNICA: .agent/scripts/
MANIFESTO:      .agent/scripts/SCRIPTS-MANIFEST.md
```

**Nunca criar scripts `.py` fora de `.agent/scripts/`** (exceto skills, MCP servers e código-fonte da aplicação).

### Scripts de Uso Frequente (Referência Rápida)

**RAG / Context Engine:**
```bash
python .agent/scripts/ai/kare_rag.py search "<termos>" --limit 5
python .agent/scripts/ai/kare_rag.py history search "<termos>" --domain <slug>
python .agent/scripts/ai/kare_rag.py history ingest --title "..." --type prd|adr|analysis --domains "<slug>"
python .agent/scripts/ai/kare_rag.py status
```

**Governança de Agentes:**
```bash
python .agent/scripts/guards/tool_guard.py check <agent-name> <tool-name>
python .agent/scripts/guards/tool_guard.py list <agent-name>
```

**PDF de RSO (REGRA EXCLUSIVA — ver PARTE 3):**
```bash
python ".agent\scripts\_gen_rso_pdf.py" --src "C:\...\RSO.md" --dest "C:\...\RSO.pdf"
```

**Conversão de Documentos:**
```bash
python .agent/scripts/generators/ppt_to_kare.py arquivo.pptx --output uploads/CANVAS.md --kare-context
```

**Credenciais:**
```bash
python .agent/scripts/infra/kare_credentials.py check
python .agent/scripts/infra/kare_credentials.py setup
```

### Categorias de Scripts

| Categoria | Scripts Principais |
|---|---|
| **RAG / Context Engine** | `kare_rag.py`, `rag_auth.py`, `kare_contexto.py`, `brain_ingest.py`, `cross_linker.py`, `decay_manager.py`, `wiki_enricher.py`, `ingest_local.py` |
| **Apresentações PPTX** | `gen_azure_arch_pptx.py` |
| **PDF** | `_gen_rso_pdf.py` ⚠️ exclusivo RSO, `export_pdf_demands.py` |
| **Governança** | `tool_guard.py`, `loop_guard.py` |
| **Credenciais** | `kare_credentials.py` |
| **Conversão** | `ppt_to_kare.py` |
| **Diagnóstico** | `session_manager.py`, `verify_all.py`, `checklist.py`, `auto_preview.py` |
| **Temporários** | `temp_*.py`, `_tmp_*.py` — NÃO usar em produção |

### Scripts Não Mover / Não Alterar

- `.specify/rag/` → Context Engine ativo (SQLite/FTS5) — seed em `seed/kare-universal.json`
- `.agent/skills/*/scripts/` → scripts de skills especializadas
- `.agent/.shared/*/scripts/` → scripts compartilhados de skills

Consulte `.agent/scripts/SCRIPTS-MANIFEST.md` para detalhes completos de parâmetros, dependências e mapa de acionamentos.

---

## PARTE 2 — PADRÃO DE PUBLICAÇÃO NO CONFLUENCE

> **OBRIGATÓRIO:** Aplicado a TODA publicação no Confluence a partir de Abril 2026.  
> Nenhum agente pode publicar páginas que não sigam este padrão.

### Regra Geral — Títulos Sem Emojis

> **INEGOCIÁVEL:** Nenhuma página publicada no Confluence pode ter emoji no título.

❌ `🚀 INI-002 — Feature Exemplo`  
✅ `INI-002 — Feature Exemplo`

### Tipo 1 — Página de Demanda (Página Pai de cada Iniciativa)

**Título:**
```
INI-XXX — [Nome da Iniciativa]
```

**Bloco de Ligação** (imediatamente abaixo do H1, antes de qualquer conteúdo):
```markdown
> **Projeto:** [Nome do Projeto] | **PI Planning:** [Identificador] | **Data:** [Mês Ano]
```

**Template:**
```markdown
# INI-XXX — [Nome da Iniciativa]

> **Projeto:** [Nome do Projeto] | **PI Planning:** [Identificador] | **Data:** [Mês Ano]

---

## Visão Geral

[Descrição resumida da iniciativa]
```

### Tipo 2 — Páginas de Artefatos (Filhas da página de demanda)

Aplica-se a: PRD, PRD-REVIEW, BACKLOG, USER STORY MAP, RAID, ADR-XXX, ARCHITECTURE

**Título:**
```
[TIPO DE ARTEFATO] — INI-XXX [Nome da Iniciativa]
```

Exemplos:
- `PRD — INI-002 Feature Exemplo`
- `ADR-001 — INI-002 [Título do ADR]`
- `ARCHITECTURE — INI-002 Feature Exemplo`

**Bloco de Ligação** (imediatamente abaixo do H1):
```markdown
> **Status:** ⏳ PENDENTE APROVAÇÃO | **Data:** [Mês Ano] | **Demanda:** INI-XXX — [Nome da Iniciativa]
```

Quando aprovado, atualizar para:
```markdown
> **Status:** ✅ Aprovado | **Data:** [Mês Ano] | **Demanda:** INI-XXX — [Nome]
```

### Parâmetros MCP — Regras de Publicação

| Parâmetro | Regra |
|---|---|
| `title` | **Sem emojis.** Seguir padrão de título por tipo acima |
| `emoji` | **NÃO usar.** Omitir ou deixar vazio |
| `content_format` | Sempre `markdown` |
| `content` | Iniciar com `# Título\n\n> **[Bloco de ligação]**\n\n---\n\n[conteúdo]` |

### Checklist Pré-Publicação

- [ ] Título sem emoji
- [ ] Bloco de ligação presente logo após o H1
- [ ] Tipo de página correto (demanda vs artefato)
- [ ] PI Planning correto (verificar no contexto do projeto)
- [ ] Mês/Ano correto
- [ ] Demanda referenciada com código e nome completo

### Referência — PI Planning

| PI Planning | Período |
|---|---|
| CLOCK02 26 | Abril 2026 (atual) |

Atualizar conforme novos PI Plannings forem iniciados.

---

## PARTE 3 — RSO PDF: SCRIPT EXCLUSIVO

> **OBRIGATÓRIO:** Todo PDF de RSO gerado pelo KARE Agile Agent deve usar EXCLUSIVAMENTE
> o script `_gen_rso_pdf.py`. Nenhum outro método é permitido.

### A Regra

```
Gerar PDF de RSO
      = python .agent/scripts/_gen_rso_pdf.py --src <arquivo.md> [--dest <arquivo.pdf>]
      = PONTO FINAL
```

```powershell
# Com destino explícito
python ".agent\scripts\_gen_rso_pdf.py" --src "C:\...\RSO INI-004.md" --dest "C:\...\RSO INI-004.pdf"

# Destino automático (mesmo diretório, mesmo nome)
python ".agent\scripts\_gen_rso_pdf.py" --src "C:\...\RSO INI-004.md"
```

### O Que É Proibido

| ❌ PROIBIDO | Razão |
|---|---|
| Scripts temporários `gerar_rso_*.py` | Inconsistência visual — foi o que gerou o problema do INI-005 |
| Classe customizada `RSO_PDF` com headers roxos | Viola o template padrão |
| Scripts `_tmp_*.py` com FPDF inline | Impossível auditar e manter |
| Qualquer estilo diferente do template padrão | O KARE-SPEC exige consistência visual entre RSOs |

### Template Visual Inviolável

| Elemento Markdown | Fonte | Tamanho | Cor RGB | Observação |
|---|---|---|---|---|
| `# Título` | Helvetica Bold | 16pt | (30,30,30) | Sem fundo |
| `## Seção` | Helvetica Bold | 13pt | **(20,80,160) AZUL** | Sem fundo, sem caixa |
| `### Subseção` | Helvetica Bold | 11pt | (50,50,50) | — |
| `\| Tabela \|` | Helvetica | 7pt | (30,30,30) | `border=1`, `col_w = max(170/n, 10)` |
| `> Citação` | Helvetica Itálico | 9pt | (80,80,80) | Fundo (245,245,245) |
| `- item` | Helvetica | 9pt | (30,30,30) | Prefixo `  * ` |
| Corpo | Helvetica | 9pt | (30,30,30) | — |

> **REGRA TÉCNICA:** `pdf.set_x(20)` obrigatório antes de TODA chamada `multi_cell()`

> **Contexto da decisão:** RSO INI-005 foi gerado com estilo diferente do INI-004 (caixas roxas vs headers azuis). O projeto exige identidade visual consistente em todos os RSOs.

---

**Versão:** 3.0.0 | **Data:** 2026-08-23 | **Prioridade:** MAXIMUM
**Changelog v3.0:** Migração KARE → KARE-SPEC. Removidas referências ao Programa Fênix. Atualizado seed path e categorias de scripts.
