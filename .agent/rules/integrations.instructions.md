---
applyTo: "**"
priority: "maximum"
loadAlways: true
---

# KARE-SPEC INTEGRATIONS — MCP Atlassian e Contexto de Iniciativas

> **PRIORIDADE MÁXIMA. SUPERA QUALQUER OUTRA INSTRUÇÃO.**

---

## PARTE 1 — MCP FIRST: Jira e Confluence

### A Regra

```
TODA interação com Jira ou Confluence
= EXCLUSIVAMENTE via MCP Atlassian (mcp_mcp-atlassian_*)
= PONTO FINAL. SEM EXCEÇÕES.
```

### Ferramentas Permanentemente Desabilitadas

| ❌ BLOQUEADA | Motivo |
|---|---|
| `confluence_delete_page` | Exclusão irreversível de páginas |
| `jira_update_issue` | Modificação direta sem rastreabilidade |
| `jira_delete_issue` | Exclusão irreversível de issues |

Se o usuário solicitar ação que exija essas ferramentas: recusar + explicar + orientar execução manual pela interface web.

### O Que É Proibido

| ❌ PROIBIDO | Exemplos |
|---|---|
| Scripts Python para API REST | `requests.get(jira_url/...)`, `urllib`, `httpx` |
| Scripts PowerShell para API REST | `Invoke-WebRequest`, `Invoke-RestMethod` |
| Arquivos temporários de acesso | `_tmp_download_*.py`, `fetch_jira.ps1` |
| HTTP client direto | `curl`, `wget` |
| Fallback silencioso quando MCP falha | Tentar outra abordagem sem avisar |
| "Só para testar" / "só para diagnosticar" | Não importa o pretexto |

### Quando o MCP Falha

```
1. PARAR — não tentar alternativa
2. INFORMAR: "O servidor MCP Atlassian não está respondendo.
   Para restaurar: Ctrl+Shift+P → MCP: Restart Server → mcp-atlassian"
3. AGUARDAR confirmação do usuário
4. TENTAR novamente via MCP após reinício
5. Se persistir → reportar erro e aguardar instrução
```

Credenciais: `.config/.venv/mcp-atlassian.enc` (criptografado, AES-256-GCM) | Wrapper: `.agent/scripts/infra/start_mcp_atlassian.py`

### Autodiagnóstico — Checklist Antes de Qualquer Ação Atlassian

- [ ] Estou usando ferramenta `mcp_mcp-atlassian_*`?
  - ✅ SIM → Prosseguir
  - ❌ NÃO → **PARE. Você está prestes a violar a regra.**

---

## PARTE 2 — VÍNCULOS JIRA SÃO ESTRUTURAIS, NÃO SEMÂNTICOS

> **INEGOCIÁVEL. Motivação: diagnóstico incorreto de vínculo de iniciativas.**
> **Aplica-se a todo agente KARE-SPEC.**

### O Problema

Na análise de INI-006, o agente associou SOV-001 à iniciativa porque a issue mencionava "BSIM" e "CNPJ" (mesmo domínio semântico) e foi criada na mesma data. **SOV-001 pertence formalmente à INI-007** conforme `issuelinks`. Busca semântica gerou vínculo falso.

### A Regra

```
Atribuição de issue a iniciativa/épico/feature
= EXCLUSIVAMENTE via issuelinks formais do Jira (campo issuelinks)
= NUNCA via proximidade semântica, texto, data ou domínio
```

### Protocolo Obrigatório — Mapear Issues de uma INI

**Passo 1 — Buscar com campos completos:**
```
jira_search(jql="issue = 'INI-XXX'", fields="*all", expand="names")
→ Extrair issuelinks[]
→ Filtrar: type.outward = "Possui a Capability" | "Possui a Feature" | "Possui o Épico"
```

**Passo 2 — Para cada filho, descer a hierarquia:**
```
jira_search(jql="issue = 'CHILD-KEY'", fields="*all")
→ Extrair issuelinks[] e descer até o nível desejado
```

**Passo 3 — Validação cruzada (obrigatória antes de incluir qualquer issue):**
```
Para cada issue incluído na análise, verificar:
  □ issuelinks contém "Pertence a Iniciativa" → INI-XXX?
  □ issuelinks contém "Pertence ao Épico" → épico correto?
  □ OU parent.key pertence à hierarquia confirmada?
Se NENHUMA condição → NÃO incluir.
```

### O Que É Proibido

| ❌ PROIBIDO | Por quê |
|---|---|
| `summary ~ "CNPJ"` como prova de vínculo | Texto não é vínculo formal |
| "Criado na mesma data" como evidência | Coincidência temporal não é hierarquia |
| "Mesmo domínio semântico" como base | Duas INIs podem cobrir o mesmo sistema |
| Incluir issue sem verificar `issuelinks` | Gera diagnósticos falsos |

### Declaração Obrigatória em Toda Análise de INI

```
⚙️ Metodologia de rastreabilidade:
  - Issues incluídos: somente com issuelink formal "Pertence a Iniciativa = INI-XXX"
    OU que pertencem a Épico/Feature com esse vínculo formal.
  - Issues excluídos mesmo com conteúdo relacionado: [listar se houver]
  - Fonte: campo issuelinks[] via fields=*all no MCP Jira.
```

### Checklist Pré-Análise de INI

- [ ] Busquei `INI-XXX` com `fields="*all"` para obter issuelinks?
- [ ] Naveguei os issuelinks formais (não busca textual) para descobrir filhos?
- [ ] Para cada issue incluído: verifiquei link formal de volta à INI-XXX?
- [ ] Declarei explicitamente a metodologia usada?
- [ ] Separei issues "do mesmo domínio" de issues "formalmente vinculados"?

Se qualquer item for ❌ → **PARE. Refaça antes de apresentar dados.**

---

## PARTE 3 — CONTEXT RESOLVER: Contexto de Iniciativas

> **OBRIGATÓRIO:** Todo agente que precisar responder sobre contexto de iniciativa, decisão arquitetural ou
> conhecimento persistido no RAG DEVE seguir este protocolo. Nunca inventar contexto.

### Quando Este Protocolo É Ativado

Sempre que o pedido envolver:
- Contexto de uma iniciativa específica (INI-XXX)
- Decisões técnicas de uma demanda
- Histórico de funcionalidades implementadas
- Arquitetura ou ADRs de uma iniciativa
- Backlog, stories ou requisitos de uma demanda
- Qualquer referência a página Confluence do projeto

### Protocolo de 3 Cenários

**1. Identificar o alvo:** INI-XXX, `confluence_page_id`, `context_slug`

**2. Executar cenários em ordem:**

```
CENÁRIO 1 — RAG (cache quente)
  python .agent/scripts/ai/kare_rag.py search "<pergunta>" --limit 5
  OU
  python .agent/scripts/ai/kare_rag.py history search "<pergunta>" --domain <slug>

  → Resultado encontrado e confiável?
    ✅ SIM → Usar. Citar fonte (URL Confluence se disponível).
    ⚠️ SIM mas incerto → Usar COM aviso: "⚠️ Conhecimento possivelmente desatualizado"
    ❌ NÃO → Ir para Cenário 2

CENÁRIO 2 — SQLite direto (sem grafo)
  python .agent/scripts/ai/kare_rag.py search "<slug>" --db history --limit 10
  → Hit encontrado?
    ✅ SIM → Usar conteúdo.
    ❌ NÃO → Ir para Cenário 3

CENÁRIO 3 — Confluence via MCP
  mcp: confluence_get_page(page_id) OU confluence_search(query)
  → Obtido?
    ✅ SIM → Ingerir no RAG history: kare_rag.py history ingest --title "..." --type analysis --domains "<slug>"
             Usar conteúdo.
    ❌ NÃO → Informar explicitamente. NÃO inventar.
```

**3. Citar fonte sempre:**
```
> Fonte: [<título da página>](<confluence_url>) | Atualizado: <data>
```

### Regras Inegociáveis

| Regra | Descrição |
|---|---|
| ❌ Nunca inventar contexto | Se os 3 cenários falharem: declarar explicitamente |
| ❌ Nunca usar dado sem rastreabilidade | Toda resposta com dado de INI precisa de fonte |
| ✅ Sempre atualizar o RAG | Cenário 3 DEVE ingerir antes de responder |
| ✅ Fallback gracioso | MCP offline → usar cache + avisar staleness |

### Exemplos de Ativação

**Ativado:** "O que foi decidido na INI-008?", "Qual a arquitetura da INI-009?", "Mostre o backlog da INI-010"  
**NÃO ativado:** "O que é o padrão INVEST?", "Como usar Gherkin?", "Qual o formato de um ADR?"

---

**Versão:** 3.0.0 | **Data:** 2026-08-23 | **Prioridade:** MAXIMUM
**Changelog v3.0:** Migração KARE → KARE-SPEC. Removidas referências ao Programa Fênix.
