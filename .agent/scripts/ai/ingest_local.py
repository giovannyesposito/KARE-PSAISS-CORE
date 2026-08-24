#!/usr/bin/env python3
"""
KARE ingest-local — Ingere arquivos PROJECT_CONTEXT.md e CONTEXTO-*.md do uploads/
no RAG como nodes do grafo, sem depender do Confluence.

Estrutura reconhecida:
  uploads/INI-XXX - Titulo/Recursos/PROJECT_CONTEXT.md  -> type=initiative
  uploads/INI-XXX - Titulo/arquitetura/*.md              -> type=architecture
  uploads/INI-XXX - Titulo/canvas/*.md                   -> type=prd
  uploads/KARE-stop3e4/Recursos/PROJECT_CONTEXT.md      -> type=program
"""

import json, re, sys
from pathlib import Path
import urllib.request

sys.path.insert(0, str(Path(__file__).parent))
from rag_auth import get_auth_headers as _rag_auth  # noqa: E402

RAG = 'http://localhost:8000'
UPLOADS = Path('uploads')
MEMORY = Path('.specify') / 'memory'

# ─── Helpers ──────────────────────────────────────────────────────────────────
def post_rag(endpoint, payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(RAG + endpoint, data=body,
                                  headers={'Content-Type': 'application/json',
                                           **_rag_auth()}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  [RAG ERRO] {e}")
        return None

def load_existing_slugs():
    """Retorna slugs ja existentes no RAG."""
    slugs = set(); offset = 0
    while True:
        try:
            req = urllib.request.Request(f"{RAG}/nodes?offset={offset}&limit=100")
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read())
            nodes = data if isinstance(data, list) else data.get('nodes', [])
            if not nodes: break
            for n in nodes:
                s = n.get('context_slug') or n.get('slug')
                if s: slugs.add(s)
            offset += 100
            if len(nodes) < 100: break
        except Exception as e:
            print(f"  [RAG] Erro: {e}"); break
    return slugs

def extract_ini_info(folder_name: str):
    """Extrai codigo INI e titulo de nome de pasta."""
    m = re.match(r'(INI-\d+(?:-\d+)?)\s*[-–]\s*(.+)', folder_name, re.IGNORECASE)
    if m:
        return m.group(1).upper(), m.group(2).strip()
    return None, folder_name

def classify_file_type(file_path: Path) -> str:
    name = file_path.name.lower()
    parent = file_path.parent.name.lower()
    if 'project_context' in name: return 'initiative'
    if parent in ('arquitetura', 'architecture') or 'arq' in parent: return 'architecture'
    if parent in ('canvas',): return 'prd'
    if parent in ('testes', 'tests'): return 'test'
    if parent in ('design',): return 'design'
    if 'contexto' in name: return 'program'
    return 'general'

def build_slug(ini_code, page_type, title=''):
    if ini_code:
        base = ini_code.lower().replace(' ', '-')
        if page_type == 'initiative': return base
        return f"{base}-{page_type}"
    # Sem INI (paginas do programa)
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:50]
    return slug or 'KARE-b2b'

def find_markdown_files():
    """Retorna lista de (path, ini_code, page_type, title)."""
    items = []

    # 1. INI-XXX folders
    for ini_dir in sorted(UPLOADS.iterdir()):
        if not ini_dir.is_dir(): continue
        ini_code, ini_title = extract_ini_info(ini_dir.name)
        if not ini_code: continue

        # PROJECT_CONTEXT.md em Recursos/
        pc = ini_dir / 'Recursos' / 'PROJECT_CONTEXT.md'
        if pc.exists():
            items.append((pc, ini_code, 'initiative', ini_title))

        # Arquivos em subdiretorios
        for sub in ['arquitetura', 'canvas', 'testes', 'design', 'observabilidade']:
            sub_dir = ini_dir / sub
            if not sub_dir.is_dir(): continue
            for md in sorted(sub_dir.glob('*.md')):
                page_type = classify_file_type(md)
                items.append((md, ini_code, page_type, md.stem))

    # 2. KARE-programa
    fp = MEMORY / 'KARE-programa'
    if fp.is_dir():
        for md in sorted(fp.rglob('*.md')):
            items.append((md, None, 'program', md.stem))

    # 3. KARE-stop3e4
    fs = UPLOADS / 'KARE-stop3e4'
    if fs.is_dir():
        for md in sorted(fs.rglob('*.md')):
            items.append((md, None, 'program', md.stem))

    return items

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("KARE ingest-local — uploads/ → RAG")
    print("=" * 60)

    # Verificar RAG
    try:
        req = urllib.request.Request(f"{RAG}/health")
        with urllib.request.urlopen(req, timeout=5) as r:
            h = json.loads(r.read())
        node_count = h.get('total_nodes', h.get('node_count', '?'))
        print(f"RAG: {h.get('status','ok')} | {node_count} nodes\n")
    except Exception as e:
        print(f"[ERRO] RAG offline: {e}"); sys.exit(1)

    existing_slugs = load_existing_slugs()
    print(f"Slugs existentes no RAG: {len(existing_slugs)}\n")

    files = find_markdown_files()
    print(f"Arquivos encontrados em uploads/: {len(files)}\n")

    total_new = 0; total_skip = 0; total_fail = 0
    node_map = {}  # ini_code → node_id (do tipo initiative)

    for fpath, ini_code, page_type, title in files:
        slug = build_slug(ini_code, page_type, title)

        if slug in existing_slugs:
            print(f"  [SKIP] {slug}")
            total_skip += 1
            continue

        try:
            content = fpath.read_text(encoding='utf-8')
        except Exception as e:
            print(f"  [ERRO leitura] {fpath}: {e}")
            total_fail += 1
            continue

        # Truncar conteudo grande
        if len(content) > 6000:
            content = content[:6000] + '\n\n[... truncado ...]'

        # Header com titulo se nao tiver
        if not content.startswith('#'):
            header = f"# {title or ini_code or slug}\n\n"
            content = header + content

        # Mapear page_type para NodeType enum
        type_map = {
            'initiative': 'context',
            'program': 'context',
            'architecture': 'artifact',
            'prd': 'artifact',
            'design': 'artifact',
            'test': 'artifact',
            'general': 'concept',
        }
        node_type = type_map.get(page_type, 'concept')

        payload = {
            'type': node_type,
            'title': title or slug,
            'content': content,
            'context_slug': slug,
            'metadata': {
                'source_file': str(fpath.relative_to(UPLOADS.parent)),
                'ini_code': ini_code,
                'page_type': page_type,
                'KARE_program': True,
                'source_type': 'local',
            }
        }

        result = post_rag('/ingest', payload)
        if result and result.get('id'):
            node_id = str(result['id'])
            existing_slugs.add(slug)
            total_new += 1

            # Guardar mapeamento para edges
            if page_type == 'initiative' and ini_code:
                node_map[ini_code] = node_id

            print(f"  [OK] {slug} → node {node_id} ({page_type})")
        else:
            print(f"  [FALHA RAG] {slug}")
            total_fail += 1

    # Criar edges: subpages → initiative node
    print(f"\n[EDGES] Criando hierarquia...")
    # Buscar nodes para criar edges
    for fpath, ini_code, page_type, title in files:
        if page_type == 'initiative' or not ini_code: continue
        slug = build_slug(ini_code, page_type, title)
        parent_slug = build_slug(ini_code, 'initiative')
        if ini_code in node_map:
            # Buscar node_id do filho
            try:
                req = urllib.request.Request(f"{RAG}/search",
                    data=json.dumps({'query': slug, 'limit': 1}).encode(),
                    headers={'Content-Type': 'application/json'}, method='POST')
                with urllib.request.urlopen(req, timeout=5) as r:
                    hits = json.loads(r.read())
                if hits:
                    child_id = str(hits[0].get('id', ''))
                    if child_id:
                        post_rag('/edges', {
                            'from_node': node_map[ini_code],
                            'to_node': child_id,
                            'relation': 'belongs_to',
                            'weight': 1.0
                        })
                        print(f"  [EDGE] {ini_code} → {slug} ({child_id})")
            except:
                pass

    print(f"\n{'='*60}")
    print(f"CONCLUIDO: {total_new} novos | {total_skip} skip | {total_fail} falhas")

if __name__ == '__main__':
    main()
