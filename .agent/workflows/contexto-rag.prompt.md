---
description: "Ingere arquivo externo (PDF, PPTX, DOCX, XLSX, CSV, MD, TXT) no KARE Context Engine (RAG) para consulta pelos agentes. Classificação automática do tipo de nó pelo conteúdo."
---

# /contexto-rag Workflow

## O que faz

Permite inserir qualquer arquivo externo diretamente no grafo de conhecimento RAG do KARE,
sem precisar rodar uma demanda completa. O agente detecta o tipo de nó automaticamente
pelo conteúdo e nome do arquivo — não é necessário indicar o que é o arquivo.

## Comportamento no Chat (Fluxo Automático)

Quando o usuário:
- Anexar um arquivo **ou** informar um caminho de arquivo **E**
- Mencionar um projeto, contexto ou slug de destino

O agente deve:

1. **Identificar o arquivo** — caminho informado, arquivo anexado, ou última menção de arquivo
2. **Identificar o contexto** — slug explícito ou derivar do nome do projeto mencionado
   - Se não for possível derivar, perguntar: *"Para qual projeto esse arquivo se destina? (ex: `KARE-programa`, `ini-001-checkout-mobile`)"*
3. **Executar a ingestão** sem fazer mais perguntas:
   ```powershell
   python .agent/scripts/ai/kare_contexto.py --file "<caminho_absoluto>" --context "<slug>"
   ```
4. **Reportar resultado** com número de nós criados e tipo detectado automaticamente

> **REGRA:** Não perguntar sobre o tipo de nó. Não pedir confirmação se o arquivo e o contexto forem identificados. Agir imediatamente.

## Política de Classificação Automática

O script `.agent/scripts/ai/kare_contexto.py` analisa nome do arquivo + primeiros ~4.000 caracteres do conteúdo e classifica:

| Tipo detectado | Sinais no arquivo |
|---|---|
| `decision` | ADR, decisão, optamos por, tradeoff, status: accepted, alternativas rejeitadas |
| `symbol` | glossário, sigla, terminologia, entidade, definição, léxico |
| `concept` | conceito, overview, introdução, fundamentos, como funciona |
| `context` | brief, kickoff, charter, iniciativa, programa, squad |
| `artifact` | **padrão** — qualquer outro arquivo (atas, planilhas, PDFs, apresentações, requisitos) |

## Inferência de Slug

O agente deve tentar derivar o slug automaticamente de frases como:
- "para o projeto KARE" ? `KARE-programa`
- "para a iniciativa 001" ? `ini-001-checkout-mobile` (verificar em `_outputs/` ou `_outputs/projetos_KARE/`)
- "para o contexto X" ? `x`
- slug literal já informado ? usar diretamente

Se não conseguir derivar com segurança ? perguntar uma única vez.

## Formatos Suportados

| Formato | Extensão |
|---|---|
| Markdown / Texto | `.md` `.txt` `.rst` |
| Dados | `.csv` `.json` |
| PDF | `.pdf` |
| Word | `.docx` |
| PowerPoint | `.pptx` |
| Excel | `.xlsx` `.xls` |

## Exemplos de Invocação no Chat

```
/contexto-rag --file C:\docs\arquitetura_hub.pdf --context KARE-programa
```
```
/contexto-rag --file C:\docs\requisitos.xlsx --context ini-001-checkout-mobile
```
```
/contexto-rag --dir C:\docs\projeto-x --context projeto-x --recursive
```

### Invocação Implícita (Fluxo Anexo)
O usuário pode simplesmente escrever:
> "esse arquivo é para o projeto KARE-programa"
> "insere esse documento no contexto da iniciativa 420"
> "guarda isso no RAG para o projeto X"

Nesses casos o agente **não precisa do comando explícito** — executa `.agent/scripts/ai/kare_contexto.py` automaticamente.

## Parâmetros Disponíveis

| Parâmetro | Obrigatório | Padrão | Descrição |
|---|---|---|---|
| `--file` ou `--dir` | sim (um dos dois) | — | Arquivo ou pasta a ingerir |
| `--context` | sim | — | Slug do projeto destino |
| `--type` | não | `auto` | Forçar tipo (artifact/symbol/decision/concept/context) |
| `--title` | não | nome do arquivo | Título personalizado (single file) |
| `--recursive` | não | false | Varrer subpastas (com `--dir`) |
| `--no-rebuild` | não | false | Não reconstruir índice BM25 (útil para batch) |

## Saídas Esperadas

```
================================================================
  KARE Context Engine — /contexto-rag
  contexto : KARE-programa
  tipo     : auto (detectado por arquivo)
================================================================

  [ARQUIVO] arquitetura_hub.pdf  (PDF)
  4 chunk(s) | ~18,432 chars
  [AUTO] Tipo detectado: artifact

  [OK]    #86  arquitetura_hub — Págs 1–8
  [OK]    #87  arquitetura_hub — Págs 9–16
  ...

================================================================
  [OK]  4 nó(s) ingerido(s)  |  0 falha(s)
================================================================
```

## Checklist Pós-Ingestão

- [ ] Confirmar número de nós criados
- [ ] Informar tipo detectado automaticamente
- [ ] Sugerir `python .agent/scripts/ai/kare_rag.py search "<termos>" --context <slug>` para validar recuperação
- [ ] Se a API estiver offline, avisar e instruir como iniciar
