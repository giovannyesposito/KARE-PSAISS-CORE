# Setup MCP Miro para KARE

## Objetivo
Habilitar o servidor `miro-mcp` para o KARE acessar e operar em boards do Miro via MCP remoto.

## Status
Entrada adicionada na configuracao MCP ativa do workspace:
- `.vscode/mcp.json`

Entrada adicionada na configuracao de referencia do KARE:
- `.agent/config/mcp_config.json`

## Endpoint MCP
- URL: `https://mcp.miro.com/`
- Transporte: HTTP
- Autenticacao: OAuth 2.1 (fluxo de autorizacao do Miro)

## Pre-requisitos
- Cliente MCP compativel (VS Code com GitHub Copilot em modo agente).
- Conta com acesso ao workspace/time do Miro que contem os boards.
- Se Miro Enterprise: habilitar o Miro MCP Server no tenant com admin antes do uso.

## Passo a passo (VS Code + Copilot)
1. Recarregue a janela do VS Code para recarregar servidores MCP.
2. Abra o Copilot Chat e confirme que o servidor `miro-mcp` aparece na lista de MCPs.
3. Clique em conectar/autenticar quando solicitado.
4. No OAuth da Miro, selecione o time correto que contem o board alvo.
5. Volte ao VS Code e confirme ferramentas/prompts do Miro habilitados.

## Regra critica de escopo
O Miro MCP e autenticado por time. Se ocorrer erro de acesso em board, refaca o OAuth e selecione o time correto.

## Smoke tests recomendados
1. Resumo de board:
   - Prompt: `Summarize the content on this board: <URL-da-board>`
2. Geracao de diagrama:
   - Prompt: `Create a sequence diagram for this codebase and add it to this board: <URL-da-board>`

## Troubleshooting
- Servidor nao aparece:
  - Verifique se `.vscode/mcp.json` contem `miro-mcp`.
  - Recarregue janela: `Developer: Reload Window`.
- Erro de autorizacao/acesso:
  - Reautentique e selecione o time correto no OAuth da Miro.
- Rate limit:
  - Reduza operacoes paralelas e tente novamente.

## Observacoes de governanca
- Evite usar boards com conteudo sensivel sem controle de permissao.
- Priorize leitura/sumarizacao antes de automacoes de escrita em board.
- Mantenha rastreabilidade dos prompts usados em fluxos criticos.