/**
 * Installer — espelha a estrutura do pacote KARE-SPEC (edição Light) no
 * diretório alvo:
 *   .vscode/settings.json → aponta para .agent/workflows e .agent/rules
 *   .agent/rules/         → instruções always-on do Copilot
 *   .agent/workflows/     → slash commands (/create, /story, /sprint...)
 */

import { join, dirname } from 'path';
import { existsSync, mkdirSync, readdirSync, copyFileSync } from 'fs';
import { spawnSync } from 'child_process';
import { fileURLToPath } from 'url';
import { copyDirectory, ensureDir } from './file-ops.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Raiz do pacote instalado (onde estão os assets a copiar)
export const PACKAGE_ROOT = join(__dirname, '../../../');

// Diretórios do pacote a espelhar no projeto do usuário
const MIRROR_DIRS = ['.agent', '.vscode', '.specify/rag/seed'];

// Arquivos raiz a copiar
const MIRROR_FILES = [
  'CLAUDE.md',
  'GEMINI.md',
  'LICENSE',
  'NOTICE.md',
  'PRIVACY.md',
  'README.md',
  'requirements.txt',
  'setup.ps1',
  'setup.sh',
  '.gitignore',
];

// Arquivos soltos fora de MIRROR_DIRS (não são diretórios)
const MIRROR_SINGLE_FILES = ['.specify/rag/kare_perene_rag.db'];

// Diretórios de trabalho criados vazios (preenchidos em runtime)
const WORKSPACE_DIRS = ['_outputs', 'uploads', '.config/.venv'];

export class Installer {
  constructor({ targetDir, ide = [] }) {
    this.targetDir = targetDir;
    this.ide       = ide;
    this.report     = { added: [], configured: [] };
  }

  _mirrorDirs() {
    for (const rel of MIRROR_DIRS) {
      const src  = join(PACKAGE_ROOT, rel);
      const dest = join(this.targetDir, rel);
      if (!existsSync(src)) continue;
      ensureDir(dest);
      const copied = copyDirectory(src, dest, { overwrite: false });
      this.report.added.push(...copied);
    }
  }

  _mirrorFiles() {
    for (const file of MIRROR_FILES) {
      const src  = join(PACKAGE_ROOT, file);
      const dest = join(this.targetDir, file);
      if (!existsSync(src) || existsSync(dest)) continue;
      try {
        mkdirSync(dirname(dest), { recursive: true });
        copyFileSync(src, dest);
        this.report.added.push(file);
      } catch { /* ignora se não tiver permissão */ }
    }
  }

  _mirrorSingleFiles() {
    for (const rel of MIRROR_SINGLE_FILES) {
      const src  = join(PACKAGE_ROOT, rel);
      const dest = join(this.targetDir, rel);
      if (!existsSync(src) || existsSync(dest)) continue;
      mkdirSync(dirname(dest), { recursive: true });
      copyFileSync(src, dest);
      this.report.added.push(rel);
    }
  }

  _setupMcpTemplates() {
    const templatesDir = join(PACKAGE_ROOT, '.agent/templates/mcp');
    const venvDir = join(this.targetDir, '.config/.venv');
    if (!existsSync(templatesDir)) return;

    mkdirSync(venvDir, { recursive: true });
    for (const file of readdirSync(templatesDir)) {
      const dest = join(venvDir, file);
      if (!existsSync(dest)) {
        copyFileSync(join(templatesDir, file), dest);
        this.report.configured.push(`.config/.venv/${file}`);
      }
    }
  }

  _createWorkspaceDirs() {
    for (const rel of WORKSPACE_DIRS) {
      const full = join(this.targetDir, rel);
      if (!existsSync(full)) {
        mkdirSync(full, { recursive: true });
        this.report.configured.push(rel);
      }
    }
  }

  /**
   * Instala dependências Python + faz bootstrap do Context Engine,
   * reaproveitando setup.ps1 (Windows) / setup.sh (Mac/Linux) já mirrorados
   * — não reimplementa `pip install` em JS. As credenciais Atlassian ficam
   * de fora (--skip-credentials): é um passo separado do wizard.
   */
  runPythonSetup() {
    const isWindows = process.platform === 'win32';
    const script = isWindows
      ? join(this.targetDir, 'setup.ps1')
      : join(this.targetDir, 'setup.sh');

    if (!existsSync(script)) {
      return { ok: false, reason: 'setup script não encontrado no destino' };
    }

    const result = isWindows
      ? spawnSync('powershell', ['-ExecutionPolicy', 'Bypass', '-File', script, '-Quick', '-SkipCredentials', '-NoColor'], {
          cwd: this.targetDir, stdio: 'inherit',
        })
      : spawnSync('bash', [script, '--quick', '--skip-credentials'], {
          cwd: this.targetDir, stdio: 'inherit',
        });

    if (result.error) {
      return { ok: false, reason: result.error.message };
    }
    return { ok: result.status === 0, reason: result.status !== 0 ? `exit code ${result.status}` : null };
  }

  run() {
    this._mirrorDirs();
    this._mirrorFiles();
    this._mirrorSingleFiles();
    this._createWorkspaceDirs();
    this._setupMcpTemplates();
    return this.report;
  }
}
