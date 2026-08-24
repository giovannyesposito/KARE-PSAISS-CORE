/**
 * FileOps — operações de arquivo para o instalador KARE-SPEC
 * Cópia recursiva e sincronização inteligente com SHA-256.
 * Preserva modificações locais do usuário; atualiza apenas o que mudou upstream.
 */

import {
  readdirSync,
  statSync,
  existsSync,
  mkdirSync,
  copyFileSync,
  readFileSync,
  writeFileSync,
  unlinkSync,
} from 'fs';
import { join, relative, dirname } from 'path';
import { createHash } from 'crypto';

const IGNORE_PATTERNS = ['.git', 'node_modules', '__pycache__', '*.pyc', '*.db', '*.log', '*.pid'];

function shouldIgnore(name) {
  return IGNORE_PATTERNS.some((pat) => {
    if (pat.includes('*')) {
      const ext = pat.replace('*', '');
      return name.endsWith(ext);
    }
    return name === pat;
  });
}

/**
 * Calcula o hash SHA-256 de um arquivo.
 */
export function sha256(filePath) {
  const content = readFileSync(filePath);
  return createHash('sha256').update(content).digest('hex');
}

/**
 * Copia um diretório recursivamente para o destino.
 * Cria diretórios ausentes automaticamente.
 * Retorna lista de arquivos copiados.
 */
export function copyDirectory(src, dest, opts = {}) {
  const { overwrite = true, filter } = opts;
  const copied = [];

  if (!existsSync(src)) return copied;
  mkdirSync(dest, { recursive: true });

  const entries = readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    if (shouldIgnore(entry.name)) continue;
    if (filter && !filter(entry.name)) continue;

    const srcPath  = join(src, entry.name);
    const destPath = join(dest, entry.name);

    if (entry.isDirectory()) {
      copied.push(...copyDirectory(srcPath, destPath, opts));
    } else {
      if (!overwrite && existsSync(destPath)) continue;
      mkdirSync(dirname(destPath), { recursive: true });
      copyFileSync(srcPath, destPath);
      copied.push(relative(dest, destPath));
    }
  }

  return copied;
}

/**
 * Sincroniza src → dest com SHA-256.
 * - Copia arquivos novos ou modificados upstream (hash diferente)
 * - Preserva modificações locais mais recentes (mtime)
 * - Remove no dest arquivos que não existem mais em src
 * Retorna { added, updated, skipped, removed }
 */
export function syncDirectory(src, dest, opts = {}) {
  const { dryRun = false } = opts;
  const result = { added: [], updated: [], skipped: [], removed: [] };

  if (!existsSync(src)) return result;
  mkdirSync(dest, { recursive: true });

  const srcEntries = new Set();

  function walk(srcDir, destDir) {
    const entries = readdirSync(srcDir, { withFileTypes: true });

    for (const entry of entries) {
      if (shouldIgnore(entry.name)) continue;

      const srcPath  = join(srcDir, entry.name);
      const destPath = join(destDir, entry.name);
      const relPath  = relative(src, srcPath);

      srcEntries.add(relPath);

      if (entry.isDirectory()) {
        mkdirSync(destPath, { recursive: true });
        walk(srcPath, destPath);
      } else {
        if (!existsSync(destPath)) {
          if (!dryRun) {
            mkdirSync(dirname(destPath), { recursive: true });
            copyFileSync(srcPath, destPath);
          }
          result.added.push(relPath);
        } else {
          const srcHash  = sha256(srcPath);
          const destHash = sha256(destPath);

          if (srcHash === destHash) {
            result.skipped.push(relPath);
            continue;
          }

          // Verifica se o usuário modificou o arquivo local
          const srcMtime  = statSync(srcPath).mtimeMs;
          const destMtime = statSync(destPath).mtimeMs;

          if (destMtime > srcMtime) {
            // Arquivo local é mais recente → preservar
            result.skipped.push(relPath);
          } else {
            if (!dryRun) copyFileSync(srcPath, destPath);
            result.updated.push(relPath);
          }
        }
      }
    }
  }

  walk(src, dest);

  // Remove arquivos no destino que não existem mais na origem
  function walkDest(destDir) {
    if (!existsSync(destDir)) return;
    const entries = readdirSync(destDir, { withFileTypes: true });
    for (const entry of entries) {
      if (shouldIgnore(entry.name)) continue;
      const destPath = join(destDir, entry.name);
      const relPath  = relative(dest, destPath);
      if (entry.isDirectory()) {
        walkDest(destPath);
      } else if (!srcEntries.has(relPath)) {
        if (!dryRun) unlinkSync(destPath);
        result.removed.push(relPath);
      }
    }
  }

  walkDest(dest);

  return result;
}

/**
 * Garante que um diretório existe (equivalente a mkdir -p).
 */
export function ensureDir(dir) {
  mkdirSync(dir, { recursive: true });
}

/**
 * Lê um arquivo de texto; retorna null se não existir.
 */
export function readText(filePath) {
  try { return readFileSync(filePath, 'utf8'); } catch { return null; }
}

/**
 * Escreve texto em arquivo, criando diretórios pai se necessário.
 */
export function writeText(filePath, content) {
  mkdirSync(dirname(filePath), { recursive: true });
  writeFileSync(filePath, content, 'utf8');
}
