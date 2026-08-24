/**
 * Comando: kare-spec install
 *
 * Wizard de instalação em 6 passos:
 *   1. Consentimento de instalação + licença
 *   2. Consentimento sobre o comportamento no VS Code
 *   3. Seleção do diretório de destino
 *   4. Seleção de IDE(s) + instalação dos arquivos
 *   5. Configuração opcional de credenciais Atlassian
 *   6. Abertura opcional da IDE no diretório instalado
 *
 * Uso:
 *   npx @dit-h/kare-spec install
 *   npx @dit-h/kare-spec install --directory /meu/projeto
 *   npx @dit-h/kare-spec install --yes
 */

import { spawnSync } from 'child_process';
import { existsSync } from 'fs';
import { join } from 'path';
import {
  confirmLicenseStep,
  confirmVSCodeStep,
  promptTargetDir,
  promptIdeSelection,
} from '../prompts.js';
import { Installer } from '../core/installer.js';
import { generateAdapters } from '../ide/adapters.js';
import { getPlatform, PLATFORMS } from '../ide/platforms.js';
import * as ui from '../ui.js';

function findPython() {
  for (const bin of ['python', 'python3']) {
    const result = spawnSync(bin, ['--version'], { stdio: 'ignore' });
    if (!result.error && result.status === 0) return bin;
  }
  return null;
}

function commandExists(bin) {
  const probe = process.platform === 'win32' ? 'where' : 'which';
  const result = spawnSync(probe, [bin], { stdio: 'ignore' });
  return !result.error && result.status === 0;
}

export function register(program) {
  program
    .command('install')
    .description('Instala o KARE-SPEC no diretório do projeto')
    .option('-d, --directory <path>', 'Diretório de destino (padrão: pergunta interativamente)')
    .option('-y, --yes', 'Responde sim aos consentimentos e usa o diretório atual (modo CI/CD)')
    .action(async (opts) => {
      ui.printBanner();
      ui.intro('Instalador — KARE-SPEC (edição Light)');

      // ── Passo 1: consentimento de instalação + licença ────────────────
      if (!opts.yes) {
        const agreed = await confirmLicenseStep();
        if (!agreed) {
          ui.cancel('Instalação cancelada — termos não aceitos.');
          return;
        }
      }

      // ── Passo 2: consentimento sobre o comportamento no VS Code ───────
      const vscodeAllowed = opts.yes ? true : await confirmVSCodeStep();

      // ── Passo 3: diretório de destino ──────────────────────────────────
      if (opts.yes && !opts.directory) opts.directory = process.cwd();
      const targetDir = await promptTargetDir(opts);

      // ── Passo 4: seleção de IDE(s) ──────────────────────────────────────
      let ideArray;
      if (opts.yes && !opts.ide) {
        ideArray = PLATFORMS.filter((p) => p.default && (vscodeAllowed || p.code !== 'vscode')).map((p) => p.code);
      } else {
        ideArray = await promptIdeSelection(opts, vscodeAllowed);
      }
      if (!ideArray || ideArray.length === 0) {
        ideArray = PLATFORMS.filter((p) => p.default).map((p) => p.code);
      }
      const ideLabels = ideArray.map((c) => getPlatform(c)?.label || c).join(', ');

      if (!opts.yes) {
        ui.note(
          [
            `Destino:    ${targetDir}`,
            `IDE(s):     ${ideLabels}`,
            ``,
            `Será instalado:`,
            `  .agent/                    → agentes, skills, workflows, regras, scripts`,
            `  .vscode/                   → settings.json (Copilot), tasks.json, mcp.json`,
            `  .specify/rag/               → Context Engine (SQLite/FTS5) — dados universais`,
            `  CLAUDE.md, GEMINI.md, README.md, LICENSE, NOTICE.md, PRIVACY.md`,
            `  setup.ps1 / setup.sh`,
            ideArray.some((c) => c !== 'vscode') ? `  + adaptadores de IDE: ${ideLabels}` : '',
            ``,
            `Também criado/configurado:`,
            `  _outputs/, uploads/, .config/.venv/  (templates MCP)`,
            `  Dependências Python + Context Engine  (via setup.ps1/setup.sh --quick)`,
          ].filter((l) => l !== '').join('\n'),
          'Resumo da instalação'
        );

        const confirmed = await ui.confirm({ message: 'Confirma a instalação?', initialValue: true });
        if (!confirmed) {
          ui.cancel('Instalação cancelada.');
          return;
        }
      }

      // ── Instalação de arquivos ──────────────────────────────────────────
      const spin = ui.spinner();
      spin.start('Copiando arquivos do KARE-SPEC...');

      let report;
      const installer = new Installer({ targetDir, ide: ideArray });
      try {
        report = installer.run();
        spin.stop('Arquivos copiados.');
      } catch (err) {
        spin.stop('Falha na instalação.');
        ui.error(`Erro: ${err.message}`);
        process.exit(1);
      }

      if (report.added.length > 0) {
        ui.success(`${report.added.length} arquivo(s) instalado(s).`);
      }
      if (report.configured.length > 0) {
        ui.log(`Configurado: ${report.configured.join(', ')}`);
      }

      // Adaptadores de IDE (só o que não é arquivo estático do pacote)
      try {
        const adapters = generateAdapters(ideArray, targetDir);
        adapters.forEach((f) => {
          const rel = f.replace(targetDir, '').replace(/\\/g, '/').replace(/^\//, '');
          ui.success(`Adaptador de IDE gerado: ${rel}`);
        });
      } catch (err) {
        ui.warn(`Adaptador de IDE não gerado: ${err.message}`);
      }

      // Dependências Python + bootstrap do Context Engine
      const python = findPython();
      if (python) {
        const spin2 = ui.spinner();
        spin2.start('Instalando dependências Python e inicializando o Context Engine...');
        const result = installer.runPythonSetup();
        if (result.ok) {
          spin2.stop('Dependências e Context Engine prontos.');
        } else {
          spin2.stop('Etapa Python não concluída.');
          ui.warn(`${result.reason || 'motivo desconhecido'} — rode setup.ps1/setup.sh manualmente depois.`);
        }
      } else {
        ui.warn('Python não encontrado — pule esta etapa e rode setup.ps1/setup.sh manualmente depois.');
      }

      ui.note(
        [
          `1. Abra o projeto na IDE escolhida (${ideLabels})`,
          ``,
          `2. Use @kare-orchestrator como ponto de entrada`,
          ``,
          `3. Primeiro fluxo:`,
          `     /create [descreva sua ideia]`,
          ``,
          `Documentação: https://github.com/giovannyesposito/KARE-PSAISS-CORE`,
        ].join('\n'),
        'Próximos passos'
      );

      // ── Passo 5: credenciais Atlassian (opcional) ───────────────────────
      if (!opts.yes && python) {
        const setupCreds = await ui.confirm({
          message: 'Deseja configurar agora as credenciais Atlassian (Jira/Confluence)?',
          initialValue: false,
        });

        if (setupCreds) {
          const credsScript = join(targetDir, '.agent', 'scripts', 'infra', 'kare_credentials.py');
          if (existsSync(credsScript)) {
            spawnSync(python, [credsScript, 'setup'], { cwd: targetDir, stdio: 'inherit' });
          } else {
            ui.warn('Script de credenciais não encontrado no destino.');
          }
        } else {
          ui.log('Credenciais não configuradas. Rode depois: python .agent/scripts/infra/kare_credentials.py setup');
        }
      }

      // ── Passo 6: abrir a IDE (opcional) ─────────────────────────────────
      if (!opts.yes) {
        const openNow = await ui.confirm({
          message: 'Deseja abrir a IDE agora, já apontando para o diretório instalado?',
          initialValue: true,
        });

        if (openNow) {
          let chosen = ideArray[0];
          if (ideArray.length > 1) {
            chosen = await ui.select({
              message: 'Qual IDE deseja abrir?',
              options: ideArray.map((c) => ({ value: c, label: getPlatform(c)?.label || c })),
            });
          }

          const platform = getPlatform(chosen);
          const bin = platform?.openCmd?.bin;
          if (bin && commandExists(bin)) {
            const args = platform.openCmd.mode === 'arg' ? [targetDir] : [];
            const spawnOpts = platform.openCmd.mode === 'cwd'
              ? { cwd: targetDir, stdio: 'inherit' }
              : { stdio: 'inherit' };
            spawnSync(bin, args, spawnOpts);
          } else {
            ui.warn(`Comando "${bin}" não encontrado no PATH. Abra "${platform?.label}" manualmente em: ${targetDir}`);
          }
        }
      }

      ui.outro(`KARE-SPEC instalado em ${targetDir}`);
    });
}
