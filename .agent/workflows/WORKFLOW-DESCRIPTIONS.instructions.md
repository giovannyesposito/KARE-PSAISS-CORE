---
applyTo: "**"
priority: "high"
loadAlways: true
---

# WORKFLOW DESCRIPTIONS — Exibição de Descrições em Seleção de Comandos

## Objetivo

Quando o usuário digita `/` e seleciona um comando, o **VS Code deve exibir a descrição completa** do que o comando faz, em vez de linhas em branco ou erros.

---

## Configuração VS Code

Para que as descrições apareçam corretamente, adicione/valide em `.vscode/settings.json`:

```json
{
  "chat.promptFilesLocations": {
    ".agent/workflows": true
  },
  "chat.commandCompletionItems": true
}
```

---

## Estrutura YAML Obrigatória

Cada arquivo `.prompt.md` em `.agent/workflows/` DEVE ter este formato no frontmatter:

```yaml
---
description: "Uma frase clara que responde: O que este comando faz?"
category: "Discovery|Planning|Backlog|Development|Quality|Risk|Operations|Release"
command: "/nome-do-comando"
---
```

### Campos:

| Campo | Obrigatório? | Descrição |
|-------|-------------|-----------|
| `description` | ✅ SIM | Frase clara (50-100 chars) explicando o que o comando faz |
| `category` | ✅ SIM | Categoria do comando para agrupamento |
| `command` | ✅ SIM | Nome do comando (ex: `/create`, `/story`, `/KARE-flow`) |
| `disclaimer` | ⚠️ OPCIONAL | Aviso crítico (se comando escreve código, faz deploy, etc) |

---

## Template para Novos Workflows

```yaml
---
description: "[Ação] [Objeto] [Resultado] — Ex: Cria stories com ACs em Gherkin e DoR checklist"
category: "Backlog"
command: "/story"
disclaimer: "📝 Cria stories formatadas. Valida DoR automaticamente. Gera casos de teste."
---
```

---

## Exemplo Prático

### ✅ CORRETO

```yaml
---
description: "Executa fluxo KARE end-to-end: Canvas → PRD → Story Map → Backlog → ADRs → RAID"
category: "Discovery"
command: "/KARE-flow"
disclaimer: "🎯 Fluxo completo. Publicação no Confluence é opcional (use /publish-confluence depois)"
---
```

### ❌ ERRADO

```yaml
---
description:
---
```

---

## Renderização Esperada

Quando o usuário digita `/fen` e vê sugestão:

```
/KARE-flow
├─ Executa fluxo KARE end-to-end: Canvas → PRD → Story Map → Backlog → ADRs → RAID
├─ Categoria: Discovery
└─ 🎯 Fluxo completo. Publicação no Confluence é opcional...
```

Em vez de:

```
/KARE-flow
├─ (linhas em branco/vazias)
├─ (erro de carregamento)
└─ ❌ Sem descrição
```

---

## Checklist: Validar Todos os Workflows

Para cada arquivo `.prompt.md` em `.agent/workflows/`:

- [ ] Tem campo `description`?
- [ ] Descrição tem 50-100 caracteres?
- [ ] Tem campo `category`?
- [ ] Tem campo `command`?
- [ ] Disclaimer está presente (se for operação crítica)?

---

## Como Validar (Método Oficial)

Use as tasks dedicadas no VS Code (`Ctrl+Shift+P` → `Tasks: Run Task`):

| Task | Ação |
|---|---|
| `KARE: Validate Slash Commands` | Detecta problemas sem alterar arquivos |
| `KARE: Fix Slash Commands (auto-fix + reload hint)` | Corrige automaticamente + instrui reload |

O script está em `.agent/scripts/infra/validate_workflows.py` (cross-platform).

---

## REGRA CRÍTICA — description SEMPRE entre aspas duplas

> **INEGOCIÁVEL:** Todo `description` nos `.prompt.md` DEVE estar entre aspas duplas.

```yaml
# ❌ ERRADO — quebra o parser YAML do VS Code (vírgulas, hífens, dois pontos)
description: Cria stories com ACs, testes e DoR — fluxo completo

# ✅ CORRETO — sempre aspas duplas
description: "Cria stories com ACs, testes e DoR — fluxo completo"
```

**Por que quebrra sem aspas?** Caracteres como `,` `:` `—` `→` `(` `)` `/` são especiais em YAML.
Sem aspas, o parser falha silenciosamente e o VS Code não exibe a descrição no picker.

---

## Recovery Procedure — Se as Descriptions Pararem de Aparecer

> Este problema é recorrente após atualizações do VS Code ou da extensão Copilot Chat.  
> O estado dos arquivos é correto — o problema é o cache do VS Code.

### Passo 1: Validar o estado dos arquivos
```
Ctrl+Shift+P → Tasks: Run Task → KARE: Validate Slash Commands
```

### Passo 2: Se encontrar problemas, corrigir
```
Ctrl+Shift+P → Tasks: Run Task → KARE: Fix Slash Commands (auto-fix + reload hint)
```

### Passo 3: Recarregar a janela do VS Code (OBRIGATÓRIO)
```
Ctrl+Shift+P → Developer: Reload Window
```

> **IMPORTANTE:** O reload é sempre necessário para que o VS Code recarregue os  
> metadados dos prompt files (descriptions) após qualquer alteração.

---

## Integração com Chat

Quando carregado automaticamente via `.vscode/settings.json`, o sistema:

1. Lê todos os `.prompt.md` em `.agent/workflows/`
2. Extrai `description` (deve estar entre aspas duplas)
3. Mostra ao usuário quando digita `/`
4. Usuário seleciona e vê a descrição ANTES de executar

---

**Versão:** 2.0.0 | **Data:** 2026-05-14 | **Prioridade:** HIGH  
**Changelog v2.0:** Adicionada regra de aspas duplas obrigatórias + Recovery Procedure + Tasks de validação
