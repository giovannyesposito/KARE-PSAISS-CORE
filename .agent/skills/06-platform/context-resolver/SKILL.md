---
name: context-resolver
description: >
  Resolução de contexto em 3 cenários: Grafo como índice → SQLite como cache →
  Confluence como fonte da verdade. Use quando precisar acessar contexto de
  iniciativa (INI-XXX), decisão arquitetural, histórico de demanda ou qualquer
  conhecimento do projeto armazenado no Confluence. Aciona busca no
  grafo local, valida cache SQLite com TTL e busca via MCP Atlassian quando
  necessário.
triggers:
  - "contexto de INI-"
  - "o que foi decidido"
  - "histórico da iniciativa"
  - "sobre a demanda"
  - "o que é a INI-"
  - "qual o status de"
  - "buscar contexto"
  - "context-resolver"
ttl_hours: 72
---

# Context Resolver Skill

## Objetivo

Garantir que qualquer resposta do KARE sobre contexto de iniciativa, decisão
ou conhecimento do projeto seja sempre baseada em dados rastreáveis,
com fonte auditável e atualização automática via cadeia de 3 cenários.

**Hierarquia de fontes (ordem de prioridade):**
```
Grafo (índice de existência)
  ↓ miss ou TTL expirado
SQLite RAG (cache de conteúdo)
  ↓ miss ou TTL expirado
Confluence via MCP Atlassian (fonte da verdade)
```

---

## Schema de Metadados de Nó

Cada nó do grafo/SQLite que representa um contexto do Confluence DEVE ter no
campo `data` (JSON) os seguintes campos:

```json
{
  "confluence_page_id": "<ID numérico da página>",
  "confluence_url": "<URL completa da página>",
  "confluence_space": "<sigla do space>",
  "confluence_parent_id": "<ID da página pai, se houver>",
  "content_fetched_at": "<ISO 8601 timestamp do último fetch>",
  "ini_code": "<ex: INI-001 — ou null se não aplicável>",
  "page_type": "<initiative|prd|architecture|decision|backlog|general>"
}
```

---

## Algoritmo dos 3 Cenários

### Pré-condição: identificar o contexto alvo

Antes de entrar nos cenários, determinar:
- Qual INI-XXX ou tema está sendo consultado?
- Há um `confluence_page_id` conhecido? (vindo do grafo, da conversa ou do usuário)
- Qual o `context_slug` associado? (ex: `ini-518`, `KARE-b2b`)

---

### CENÁRIO 1 — Cache hit completo ✅

**Condição de entrada:** Nó existe no grafo E `content_fetched_at` está dentro do TTL (< 72h)

**Passos:**
1. `GET /search?q=<termos>&context=<slug>&limit=5` — busca BM25 no RAG
2. Verificar se retornou resultados com `content_fetched_at` presente e válido
   - Calcular: `(agora - content_fetched_at) < 72h`
3. ✅ **Utilizar conteúdo do SQLite diretamente**
4. Gerar resposta citando: título da página + `confluence_url` como fonte

**Output esperado:**
```
> Fonte: [Título da página](confluence_url) — cache de <data do fetch>
```

---

### CENÁRIO 2 — Grafo desatualizado / SQLite tem conteúdo 🔄

**Condição de entrada:** Nó NÃO encontrado no grafo, MAS conteúdo existe no SQLite
(ou nó existe com `content_fetched_at` ausente/expirado MAS o SQLite tem conteúdo útil)

**Passos:**
1. `GET /nodes?context=<slug>&limit=50` — listar nós do contexto
2. Nó não encontrado no grafo OU `confluence_page_id` ausente no `data`
3. `GET /search?q=<termos>&limit=5` — busca geral no SQLite
4. Conteúdo encontrado no SQLite:
   a. `POST /nodes` — criar nó no grafo com metadados mínimos:
      ```json
      {
        "title": "<título>",
        "type": "context",
        "content": "<descrição rica com keywords>",
        "context_slug": "<slug>",
        "metadata": {
          "confluence_page_id": "<id se conhecido>",
          "confluence_url": "<url se conhecida>",
          "content_fetched_at": "<timestamp original>"
        }
      }
      ```
   b. `POST /edges` — criar arestas relacionais:
      - `BELONGS_TO` para nó pai (KARE-b2b ou ini-XXX)
      - `REFERENCES` para nós relacionados identificados no conteúdo
5. ✅ **Utilizar conteúdo do SQLite**
6. Avisar: `⚠️ Grafo atualizado com nova referência — conteúdo do cache local`

---

### CENÁRIO 3 — Cache miss completo 🌐

**Condição de entrada:** Nó NÃO no grafo E NÃO no SQLite (ou conteúdo expirado > TTL)

**Passos:**
1. `GET /search?q=<termos>&limit=5` — confirmar ausência no SQLite
2. Se `confluence_page_id` conhecido (veio do grafo mesmo sem conteúdo):
   - MCP: `confluence_get_page(page_id=<id>)` — buscar conteúdo completo
3. Se `confluence_page_id` desconhecido:
   - MCP: `confluence_search(query=<termos>, space_key="<sigla do space>", limit=5)`
   - Identificar a página mais relevante pelo título
   - MCP: `confluence_get_page(page_id=<id encontrado>)`
4. Com conteúdo obtido do Confluence:
   a. `POST /ingest` — atualizar SQLite:
      ```json
      {
        "title": "<título da página>",
        "content": "<conteúdo completo>",
        "type": "<classificado por page_type>",
        "context_slug": "<slug>",
        "metadata": {
          "confluence_page_id": "<id>",
          "confluence_url": "<url>",
          "confluence_space": "<sigla do space>",
          "content_fetched_at": "<agora ISO 8601>",
          "ini_code": "<INI-XXX ou null>",
          "page_type": "<tipo classificado>"
        }
      }
      ```
   b. `POST /nodes` — criar/atualizar nó no grafo
   c. `POST /edges` — criar arestas relacionais
5. ✅ **Utilizar conteúdo recém-obtido**
6. Informar: `✅ Contexto atualizado via Confluence — página: <título>`

---

## Classificação Automática de Tipo de Página

Usar o título e conteúdo para inferir `page_type` e `node_type`:

| Sinal no título/conteúdo | page_type | node_type |
|---|---|---|
| "INI-XXX — Nome" (página raiz de demanda) | `initiative` | `context` |
| "PRD", "Product Requirements" | `prd` | `artifact` |
| "ADR-", "Architecture Decision" | `decision` | `decision` |
| "BACKLOG", "User Stories", "Épicos" | `backlog` | `artifact` |
| "Arquitetura", "Architecture", "Diagrama" | `architecture` | `artifact` |
| "RAID", "Riscos", "Dependências" | `risk` | `artifact` |
| Demais | `general` | `concept` |

---

## Descrição Mínima Rica (garantir BM25 funcional)

Ao criar um nó no grafo sem conteúdo completo ainda, o campo `content` DEVE
conter uma descrição mínima rica em keywords para que o BM25 retorne o nó
em buscas relevantes. Formato obrigatório:

```
<Título da Página>

Programa: <Nome do Programa> | INI-XXX | Space: <sigla do space> | page_id: <id>
Tipo: <page_type>
Ancestrais: <caminho de ancestrais separado por " > ">

<Resumo de 2-3 linhas descrevendo o que a página trata,
sistemas envolvidos, decisões principais e período>
```

---

## Criação de Arestas — Tipos e Semântica

| Situação | relation_type | De → Para |
|---|---|---|
| Página pertence a uma iniciativa | `belongs_to` | nó-página → nó-iniciativa |
| Iniciativa pertence ao programa | `belongs_to` | nó-iniciativa → nó-KARE-b2b |
| ADR referencia uma iniciativa | `references` | nó-adr → nó-iniciativa |
| Iniciativa depende de outra | `depends_on` | nó-ini-a → nó-ini-b |
| Página conflita com outra decisão | `conflicts_with` | nó-a → nó-b |
| Nova versão substitui anterior | `supersedes` | nó-novo → nó-antigo |

---

## Regras de Fallback

### MCP Confluence inacessível
- Cenário 3 não pode completar o fetch
- **Ação:** Usar o conteúdo disponível no SQLite (mesmo que expirado) + adicionar aviso:
  ```
  ⚠️ Confluence inacessível — respondendo com cache local de <data>.
  Reconecte ao MCP Atlassian e repita para obter dados atualizados.
  ```
- **Não falhar silenciosamente.** Nunca inventar contexto de demanda.

### RAG API inacessível (localhost:8000 offline)
- Cenário 1 e 2 não funcionam
- **Ação:** Ir direto ao Cenário 3 (MCP Confluence)
- Avisar: `⚠️ RAG API offline — contexto obtido diretamente do Confluence sem cache`

### Página não encontrada no Confluence
- Nenhum cenário retorna dados
- **Ação:** Informar explicitamente:
  ```
  ❌ Contexto não encontrado para <INI-XXX / termos>.
  Verifique se a página existe no Confluence (space configurado) ou forneça o page_id diretamente.
  ```

---

## Saídas Esperadas

- Contexto utilizado na resposta com rastreabilidade de fonte
- Nós e arestas atualizados no grafo (Cenários 2 e 3)
- SQLite atualizado com `content_fetched_at` (Cenário 3)
- Aviso de status de cache para o usuário (staleness, miss, hit)
