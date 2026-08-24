# ✅ Descrições de Comandos — Guia de Uso

## O Que Mudou

Todos os comandos slash agora têm **descrição visual** quando você os seleciona no VS Code Copilot Chat.

Quando digita `/` e seleciona um comando, em vez de linhas vermelhas vazias, você verá:

```
/kare-flow
├─ Executa o KARE Flow ponta a ponta a partir de um Canvas...
├─ Categoria: Discovery
└─ 🎯 Fluxo completo. Publicação no Confluence é opcional...
```

---

## 🎯 Comandos com Descrição

| Comando | Descrição |
|---------|-----------|
| `/kare-flow` | Executa o KARE Flow ponta a ponta: Canvas → PRD → Story Map → Backlog → ADRs → RAID |
| `/create` | Inicia fluxo completo de discovery — classifica projeto, gera Brief + PRD e backlog |
| `/story` | Cria ou refina items de backlog SAFe com ACs Gherkin e DoR checklist |
| `/sprint` | Gera plano de sprint, sprint goal e organiza backlog |
| `/plan` | Create project plan (apenas planning, sem código) |
| `/implement` | Implementa User Story com código, testes e ADRs |
| `/test` | Gera plano de testes, casos BDD/Gherkin e Test Coverage Matrix |
| `/review` | Executa code review contextualizado com relatório |
| `/auditoria-de-codigo` | Auditoria completa de codebase: arqueologia, padrões, testes, métricas e quality gate |
| `/risk` | Identifica e registra riscos com RAID Log |
| `/deploy` | Deployment para staging/produção com pre-flight checks |
| `/release` | Release management: versionamento, notas, tags Git |

---

## 🔄 Como Fazer Funcionar

### 1️⃣ Recarregue o VS Code

Após as mudanças, recarregue a janela do VS Code:

**Windows/Linux:**
- `Ctrl + Shift + P` → "Developer: Reload Window"

**Mac:**
- `Cmd + Shift + P` → "Developer: Reload Window"

### 2️⃣ Teste Digitando `/`

No chat Copilot:
```
Digite: /
Veja: Lista de comandos com descrições
Selecione: /kare-flow
Resultado: Descrição completa aparece
```

### 3️⃣ Validação

Se **não aparecer descrição**, verifique:

✅ VS Code foi recarregado?  
✅ Copilot Chat está aberto?  
✅ Arquivo `.agent/workflows/kare-flow.prompt.md` tem `description`?  
✅ `.vscode/settings.json` tem `"chat.promptFilesLocations": { ".agent/workflows": true }`?  

---

## 📋 Estrutura do YAML (Referência)

Cada comando tem este formato:

```yaml
---
description: "Descrição do que o comando faz (50-100 chars)"
command: "/nome-do-comando"
category: "Categoria do comando"
disclaimer: "Aviso importante (se houver)"
---
```

---

## 🎨 Campos Visuais

Quando selecionado, um comando mostra:

```
/COMANDO
├─ description (linha principal — o que faz)
├─ Categoria: [categoria]
└─ 🎬 disclaimer (aviso crítico, se houver)
```

---

## ✨ Exemplo Real

### Antes (linhas vermelhas):
```
/kare-flow
❌ ━━━━━━━━━━━ (linhas vazias)
❌ ━━━━━━━━━━━
```

### Depois (com descrição):
```
/kare-flow
✅ Executa o KARE Flow ponta a ponta a partir de um Canvas, gerando PRD, Story Map, Backlog SAFe, ADRs e RAID.
✅ Categoria: Discovery
✅ 🎯 Fluxo completo. Publicação no Confluence é opcional (use /publish-confluence depois)
```

---

## 🔧 Troubleshooting

### Descrição ainda não aparece após reload?

1. Verifique `.vscode/settings.json`:
```json
{
  "chat.promptFilesLocations": {
    ".agent/workflows": true
  }
}
```

2. Limpe cache do VS Code:
   - Feche VS Code completamente
   - Delete pasta `.vscode/CopilotChat`
   - Reabra VS Code

3. Verifique se arquivo tem `command` field:
```bash
# Windows PowerShell
cd .agent/workflows
Select-String -Path "*.prompt.md" "^command:" | Select-Object -Unique
```

### Descrição aparece mas está vazia?

Verifique se o frontmatter YAML está correto:

```yaml
---
description: "Texto aqui — não deixar em branco"
command: "/comando"
category: "Categoria"
---
```

---

## 📚 Referências

- **Instruções Completas:** `.agent/workflows/WORKFLOW-DESCRIPTIONS.instructions.md`
- **Índice de Disclaimers:** `.agent/workflows/DISCLAIMERS.md`
- **Índice de Workflows:** `.agent/config/workflows-index.json`

---

## 🎯 Próximo Passo

1. Recarregue o VS Code
2. Digite `/` no Copilot Chat
3. Selecione um comando
4. Veja a descrição aparecer! 🎉

---

**Data:** 2026-04-19 | **Status:** ✅ Implementado
