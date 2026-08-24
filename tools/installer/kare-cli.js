#!/usr/bin/env node
/**
 * KARE-SPEC CLI
 * Entry point: npx @dit-h/kare-spec install
 */

import { readFileSync } from 'fs';
import { fileURLToPath, pathToFileURL } from 'url';
import { dirname, join } from 'path';
import { Command } from 'commander';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Windows: fix stdin interaction in non-TTY environments
if (process.platform === 'win32') {
  process.stdin.setRawMode = process.stdin.setRawMode || (() => process.stdin);
}

const packageJson = JSON.parse(
  readFileSync(join(__dirname, '../../package.json'), 'utf8')
);

async function loadCommands(program) {
  const commandFiles = [join(__dirname, 'commands/install.js')];

  for (const file of commandFiles) {
    try {
      const mod = await import(pathToFileURL(file).href);
      if (mod.register) mod.register(program);
    } catch (err) {
      console.error(`[kare-spec] Erro ao carregar comando: ${file}\n${err.message}`);
    }
  }
}

async function main() {
  const program = new Command();

  program
    .name('kare-spec')
    .description('KARE-SPEC — Instalador de agentes de IA para times de desenvolvimento')
    .version(packageJson.version, '-v, --version', 'Exibe a versão atual')
    .helpOption('-h, --help', 'Exibe esta ajuda');

  await loadCommands(program);

  program.addHelpText('after', `
Exemplos:
  $ npx @dit-h/kare-spec install
  $ npx @dit-h/kare-spec install --directory /meu/projeto
  $ npx @dit-h/kare-spec install --yes

Documentação:
  https://github.com/giovannyesposito/KARE-PSAISS-CORE
`);

  await program.parseAsync(process.argv);

  if (process.argv.length <= 2) {
    program.help();
  }
}

main().catch((err) => {
  console.error('\n\x1b[31m[kare-spec] Erro fatal:\x1b[0m', err.message);
  process.exit(1);
});
