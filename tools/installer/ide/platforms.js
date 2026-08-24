/**
 * Plataformas / IDEs suportadas pelo instalador KARE-SPEC (edição Light).
 *
 * `staticFile`: true quando o arquivo/pasta de configuração da IDE já vem
 * pronto no pacote (mirrorado por installer.js) — não precisa ser gerado.
 * `openCmd`: como abrir a IDE já apontando para o diretório de instalação.
 *   - 'arg'  → `<bin> <targetDir>`
 *   - 'cwd'  → `<bin>` executado com cwd = targetDir (CLI que não aceita path posicional)
 */

export const PLATFORMS = [
  {
    code: 'vscode',
    label: 'VS Code (GitHub Copilot Chat)',
    hint: 'Padrão — requer extensão GitHub.copilot-chat',
    default: true,
    staticFile: true,
    openCmd: { bin: 'code', mode: 'arg' },
  },
  {
    code: 'cursor',
    label: 'Cursor',
    hint: 'gera .cursorrules na raiz do projeto',
    default: false,
    staticFile: false,
    openCmd: { bin: 'cursor', mode: 'arg' },
  },
  {
    code: 'intellij',
    label: 'IntelliJ / JetBrains Junie',
    hint: 'gera .junie/guidelines.md',
    default: false,
    staticFile: false,
    openCmd: { bin: 'idea', mode: 'arg' },
  },
  {
    code: 'claude-code',
    label: 'Claude Code (CLI)',
    hint: 'usa o CLAUDE.md já incluído no pacote',
    default: false,
    staticFile: true,
    openCmd: { bin: 'claude', mode: 'cwd' },
  },
  {
    code: 'gemini',
    label: 'Gemini CLI',
    hint: 'usa o GEMINI.md já incluído no pacote',
    default: false,
    staticFile: true,
    openCmd: { bin: 'gemini', mode: 'cwd' },
  },
];

export function getPlatform(code) {
  return PLATFORMS.find((p) => p.code === code);
}
