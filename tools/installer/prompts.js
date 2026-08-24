/**
 * Prompts interativos do instalador KARE-SPEC — os 6 passos do wizard:
 *   1. Consentimento de instalação + licença
 *   2. Consentimento sobre o comportamento no VS Code
 *   3. Seleção do diretório de destino
 *   4. Seleção de IDE(s)
 * (5 e 6 — credenciais Atlassian e abrir IDE — ficam em commands/install.js,
 *  pois dependem do resultado da instalação de arquivos.)
 */

import { readFileSync } from 'fs';
import { join, resolve } from 'path';
import * as ui from './ui.js';
import { PACKAGE_ROOT } from './core/installer.js';
import { PLATFORMS } from './ide/platforms.js';

function readPackageText(relPath) {
  try {
    return readFileSync(join(PACKAGE_ROOT, relPath), 'utf8');
  } catch {
    return null;
  }
}

// ── Passo 1: Consentimento de instalação + licença ────────────────────────

export async function confirmLicenseStep() {
  const license = readPackageText('LICENSE');

  ui.note(
    [
      'O KARE-SPEC vai instalar agentes de IA, workflows (slash commands),',
      'skills e um Context Engine local (RAG em SQLite) no diretório que',
      'você escolher a seguir.',
      '',
      '── Licença (MIT) ──',
      license
        ? license.trim()
        : 'MIT License — uso, cópia, modificação e redistribuição livres.',
      '',
      '── Marca / nome do projeto ──',
      'A licença MIT acima cobre o código. Ela NÃO inclui uma licença para',
      'o nome e a identidade do projeto: "KARE-SPEC", "KARE-Orquestrator" e',
      'o logo associado são mantidos pelo autor original. Você pode usar,',
      'modificar e redistribuir o código livremente sob outro nome, mas não',
      'pode publicar um fork usando esses nomes/logo de forma que sugira',
      'ser a versão oficial, sem autorização. Detalhes em NOTICE.md.',
    ].join('\n'),
    'Instalação do KARE-SPEC'
  );

  return ui.confirm({
    message: 'Você concorda com os termos acima e deseja instalar o KARE-SPEC?',
    initialValue: true,
  });
}

// ── Passo 2: Consentimento sobre o comportamento no VS Code ───────────────

/**
 * Retorna true se VS Code deve continuar disponível como opção no passo 4.
 */
export async function confirmVSCodeStep() {
  ui.note(
    [
      'Se o VS Code estiver entre as IDEs escolhidas no próximo passo, o',
      'KARE-SPEC configura `.vscode/settings.json` (chat.instructionsFilesLocations',
      'e chat.promptFilesLocations) para que o GitHub Copilot Chat carregue',
      'automaticamente a persona e as regras do KARE-SPEC desde a primeira',
      'mensagem, em qualquer conversa dentro deste projeto.',
    ].join('\n'),
    'Comportamento no VS Code'
  );

  const agreed = await ui.confirm({
    message: 'Você concorda que o VS Code seja pré-configurado dessa forma?',
    initialValue: true,
  });

  if (agreed) return true;

  // Segunda confirmação — explica exatamente a consequência de recusar
  const reallyDecline = await ui.confirm({
    message: [
      'Você optou por não configurar o VS Code para carregar a persona',
      'KARE-SPEC automaticamente. Isso significa que o VS Code NÃO vai',
      'aparecer como opção na seleção de IDEs a seguir — a instalação vai',
      'seguir sem nenhuma configuração pra ele.',
      '',
      'Se depois você mudar de ideia e quiser usar o KARE-SPEC no VS Code,',
      'vai precisar reiniciar o instalador do zero (rodar `npx @dit-h/kare-spec',
      'install` de novo) pra essa opção voltar a aparecer.',
      '',
      'Confirma que quer continuar sem VS Code?',
    ].join('\n'),
    initialValue: false,
  });

  // Se reconsiderou (respondeu não à segunda pergunta), trata como consentimento
  return !reallyDecline;
}

// ── Passo 3: Diretório de destino ──────────────────────────────────────────

export async function promptTargetDir(opts = {}) {
  if (opts.directory) return resolve(opts.directory);

  const targetDir = await ui.text({
    message: 'Diretório do projeto onde o KARE-SPEC será instalado:',
    placeholder: process.cwd(),
    defaultValue: process.cwd(),
    validate: (v) => (v?.trim() ? undefined : 'O diretório não pode ser vazio.'),
  });

  return resolve(targetDir);
}

// ── Passo 4: Seleção de IDE(s) ──────────────────────────────────────────────

export async function promptIdeSelection(opts = {}, vscodeAllowed = true) {
  if (opts.ide) {
    return Array.isArray(opts.ide) ? opts.ide : [opts.ide];
  }

  const available = PLATFORMS.filter((p) => vscodeAllowed || p.code !== 'vscode');
  const options = available.map((p) => ({ value: p.code, label: p.label, hint: p.hint }));
  const initialValues = available.filter((p) => p.default).map((p) => p.code);

  ui.log('  Use Espaço para marcar/desmarcar • Enter para confirmar • Setas para navegar');
  const ides = await ui.multiselect({
    message: 'Selecione as IDEs / ferramentas de IA que você vai usar com o KARE-SPEC:',
    options,
    initialValues,
    required: true,
  });

  return ides;
}
