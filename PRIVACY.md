# Privacidade e Telemetria

## O que é coletado

O KARE-SPEC registra localmente, em `.specify/rag/kare_telemetry.db` (SQLite):

- Usuário ativo (variável `KARE_USER`, ou o usuário logado no sistema operacional
  se `KARE_USER` não estiver definida)
- Agente/comando usado, tipo de ação, modo de interação (agent/ask/edit)
- Modelo de IA detectado (lido de `.vscode/settings.json`, nunca perguntado)
- Contagem de tokens de entrada/saída (estimativa local, não o conteúdo)
- Iniciativa/contexto ativo (inferido do branch git atual)
- Timestamps de início/fim de sessão

Nenhum conteúdo de conversa, código ou artefato é armazenado na telemetria —
apenas metadados de uso (o quê, quando, por quem, com qual agente).

## Onde fica

100% local. `kare_telemetry.db` nunca é transmitido automaticamente para
nenhum servidor — não há chamada de rede no código de telemetria. A única
forma de os dados saírem da máquina é uma ação manual explícita (ex:
copiar o arquivo, ou rodar `kare_rag.py export`, que exporta artefatos de
`kare_perene_rag.db`, não a telemetria).

As bases `kare_history_rag.db` (artefatos de projeto) e `kare_telemetry.db`
não são versionadas no repositório — cada instalação acumula as suas
próprias localmente, sem afetar nem ser afetada por outras.

## Como desativar

```bash
export KARE_TELEMETRY_DISABLED=1
```

Com essa variável definida, `kare_rag.py telemetry log`, `session-start`,
`session-end` e o helper interno `_telem()` (usado por `search`/`ingest`)
viram no-op — nada é escrito no banco.

## Como apagar dados existentes

```bash
rm .specify/rag/kare_telemetry.db
```

Ou, para manter o schema mas zerar os dados:

```bash
python .agent/scripts/ai/kare_rag.py migrate
```

(recria o arquivo do zero se ele não existir).

## Credenciais (Jira, Confluence, senha da base RAG perene)

Não é telemetria, mas relacionado: credenciais são criptografadas com
AES-256-GCM via `kare_credentials.py`, com a chave fora do repositório
(`%USERPROFILE%\kare.key` ou `~/kare.key`). Ver [README.md](README.md#configuração-do-ambiente)
e [NOTICE.md](NOTICE.md) para detalhes.
