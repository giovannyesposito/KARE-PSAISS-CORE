/**
 * Adaptadores de IDE — gera apenas o que NÃO vem como arquivo estático do
 * pacote (CLAUDE.md, GEMINI.md e .vscode/settings.json já são mirrorados
 * por installer.js, não precisam de geração aqui).
 */

import { join, dirname } from 'path';
import { existsSync, mkdirSync, writeFileSync } from 'fs';

function write(filePath, content) {
  if (existsSync(filePath)) return null;
  mkdirSync(dirname(filePath), { recursive: true });
  writeFileSync(filePath, content, 'utf8');
  return filePath;
}

const CURSOR_RULES = `\
# KARE-SPEC — Cursor

Este projeto usa o KARE-SPEC para desenvolvimento assistido por IA.

Ponto de entrada obrigatório: agente \`kare-orchestrator\` em \`.agent/agents/\`.

## Regras (carregadas automaticamente)

Leia \`.agent/rules/\` para o protocolo completo (orquestração, padrões de
entrega). Os workflows/slash commands estão em \`.agent/workflows/\`:

\`\`\`
/create       → Discovery completo (PRD + Backlog + ADRs)
/story        → User Story com ACs
/sprint       → Sprint Planning
/implement    → Código com TDD
/review       → Code Review
/test         → Testes automatizados
/risk         → Análise RAID
/status       → Status Report
\`\`\`

## Context Engine (RAG)

\`\`\`bash
python .agent/scripts/ai/kare_rag.py search "sua busca"
python .agent/scripts/ai/kare_rag.py status
\`\`\`

Documentação: https://github.com/giovannyesposito/KARE-PSAISS-CORE
`;

const JUNIE_GUIDELINES = `\
# KARE-SPEC — JetBrains Junie

Este projeto usa o KARE-SPEC para desenvolvimento assistido por IA.

Ponto de entrada obrigatório: agente \`kare-orchestrator\` em \`.agent/agents/\`.

## Regras (carregadas automaticamente)

Leia \`.agent/rules/\` para o protocolo completo. Os workflows/slash commands
estão em \`.agent/workflows/\`:

\`\`\`
/create       → Discovery completo (PRD + Backlog + ADRs)
/story        → User Story com ACs
/sprint       → Sprint Planning
/implement    → Código com TDD
/review       → Code Review
/test         → Testes automatizados
/risk         → Análise RAID
/status       → Status Report
\`\`\`

## Context Engine (RAG)

\`\`\`bash
python .agent/scripts/ai/kare_rag.py search "sua busca"
python .agent/scripts/ai/kare_rag.py status
\`\`\`

Documentação: https://github.com/giovannyesposito/KARE-PSAISS-CORE
`;

/**
 * Gera os arquivos de adaptação para as IDEs selecionadas que não têm um
 * arquivo estático equivalente já mirrorado do pacote.
 *
 * @param {string[]} codes - códigos das IDEs selecionadas
 * @param {string} targetDir
 * @returns {string[]} caminhos absolutos dos arquivos gerados
 */
export function generateAdapters(codes, targetDir) {
  const generated = [];

  for (const code of codes) {
    let result = null;
    switch (code) {
      case 'cursor':
        result = write(join(targetDir, '.cursorrules'), CURSOR_RULES);
        break;
      case 'intellij':
        result = write(join(targetDir, '.junie', 'guidelines.md'), JUNIE_GUIDELINES);
        break;
      default:
        break; // vscode / claude-code / gemini: arquivo estático já mirrorado
    }
    if (result) generated.push(result);
  }

  return generated;
}
