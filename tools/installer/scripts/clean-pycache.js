#!/usr/bin/env node
/**
 * Remove __pycache__/ e *.pyc gerados localmente antes de empacotar
 * (`npm pack`/`npm publish`). Necessário porque `files` no package.json é
 * uma allowlist "as-is" — .gitignore/.npmignore não filtram o que já está
 * fisicamente em disco dentro de diretórios incluídos.
 */

import { rmSync, readdirSync, statSync } from 'fs';
import { join } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = join(__dirname, '../../../');

function clean(dir) {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }

  for (const entry of entries) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === '__pycache__' || entry.name === 'node_modules' || entry.name === '.git') {
        if (entry.name === '__pycache__') {
          rmSync(full, { recursive: true, force: true });
          console.log(`[clean-pycache] removido: ${full}`);
        }
        continue; // não desce em node_modules/.git
      }
      clean(full);
    } else if (entry.name.endsWith('.pyc') || entry.name.endsWith('.pyo')) {
      rmSync(full, { force: true });
    }
  }
}

clean(join(REPO_ROOT, '.agent'));
console.log('[clean-pycache] concluído.');
