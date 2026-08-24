#!/usr/bin/env python3
"""
kare_rag.py — KARE Context Engine (standalone, SQLite/FTS5)

Três bancos de dados:
  kare_perene_rag.db   — conhecimento perene do projeto
                         Escrita protegida por palavra-passe (padrão de fábrica na
                         primeira inserção; troque com "perene-password change")
  kare_history_rag.db  — artefatos gerados/analisados: PRDs, ADRs, análises, specs
                         Populado automaticamente pelos agentes ao gerar/analisar artefatos
  kare_telemetry.db    — telemetria multi-usuário: tokens, modelos, agentes, sessões
                         100% local, nunca transmitida automaticamente. Desativar:
                         export KARE_TELEMETRY_DISABLED=1 (ver PRIVACY.md)

Usuário ativo: variável de ambiente KARE_USER (ex: export KARE_USER=joao.silva)

Uso:
  python kare_rag.py search "<query>" [--db perene|history|all] [--limit N] [--max-tokens N]
  python kare_rag.py ask    "<query>" [--limit N] [--max-tokens N]

  python kare_rag.py ingest --title X --type Y (--file|--content) [--password P]
  python kare_rag.py bootstrap [--seed path.json] [--force] [--password P]
  python kare_rag.py migrate
  python kare_rag.py status [--db perene|history|telemetry|all]
  python kare_rag.py export [--output path]
  python kare_rag.py import --input path [--password P]
  python kare_rag.py perene-password status
  python kare_rag.py perene-password change

  python kare_rag.py history ingest --title X --type prd|adr --domains "vender,implantar" (--file|--content)
  python kare_rag.py history search "<query>" [--domain D] [--type T]
  python kare_rag.py history list [--type T] [--domain D]

  python kare_rag.py telemetry log --agent X --action-type query [--context-slug ini-001]
  python kare_rag.py telemetry stats [--days N] [--user U] [--agent A]
  # Auto-detectado sem config manual: modelo (settings.json), iniciativa (branch git), usuário (SO)
  python kare_rag.py telemetry session-start
  python kare_rag.py telemetry session-end --session-id N

Tipos perene  : artifact | concept | context | decision | domain | journey | product | symbol | system
Tipos history : adr | analysis | epic | initiative | prd | spec | story_map
Ações telemetria: analysis | artifact_created | artifact_reviewed | other | planning | query
"""

import hashlib
import json
import argparse
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta

try:
    # Evita UnicodeEncodeError em print() com emoji/acentos quando o console
    # Windows usa codepage legado (cp1252/cp850) em vez de UTF-8.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass
from pathlib import Path
from typing import Optional

# ─── Localização ───────────────────────────────────────────────────────────────
_ROOT        = Path(__file__).parents[3]
RAG_DIR      = _ROOT / ".specify" / "rag"
DB_PERENE    = RAG_DIR / "kare_perene_rag.db"
DB_HISTORY   = RAG_DIR / "kare_history_rag.db"
DB_TELEMETRY = RAG_DIR / "kare_telemetry.db"
SEED_DIR     = RAG_DIR / "seed"
DEFAULT_SEED = SEED_DIR / "KARE-universal.json"

# Hash SHA-256 da senha padrão de fábrica da base perene — o valor em texto
# plano NUNCA fica no código-fonte (só o hash, que não é reversível e não é,
# por si só, uma credencial válida). O valor de fábrica está documentado em
# README.md ("Configuração do Ambiente"). Assim que o usuário rodar
# `kare_credentials.py setup-perene`, a senha customizada passa a viver
# criptografada (AES-256-GCM) fora do código — ver _perene_current_hash().
_PERENE_FACTORY_HASH = "f80b4a63952c01e5ea951f3c0128da815d9e46b48a12f59e813dc0cd3cfd26c2"


def _kare_credentials():
    """Importa kare_credentials.py (pasta irmã .agent/scripts/infra/).
    Retorna None se o módulo ou a dependência 'cryptography' não estiverem
    disponíveis — chamadores tratam isso como 'senha customizada não
    configurada' e caem para a senha padrão de fábrica."""
    try:
        infra_dir = _ROOT / ".agent" / "scripts" / "infra"
        if str(infra_dir) not in sys.path:
            sys.path.insert(0, str(infra_dir))
        import kare_credentials
        return kare_credentials
    except ImportError:
        return None

# Usuário ativo: KARE_USER > usuário logado no SO (Windows/Mac/Linux)
def _active_user() -> str:
    override = os.environ.get("KARE_USER")
    if override:
        return override
    try:
        import getpass as _gp
        return _gp.getuser()
    except Exception:
        return "unknown"

NODE_TYPES_PERENE  = {"artifact", "concept", "context", "decision", "domain", "journey", "product", "symbol", "system"}
NODE_TYPES_HISTORY = {"adr", "analysis", "epic", "initiative", "prd", "spec", "story_map"}
ACTION_TYPES       = {"analysis", "artifact_created", "artifact_reviewed", "other", "planning", "query"}
# Modos do GitHub Copilot no VS Code
INTERACTION_MODES  = {"agent", "ask", "edit", "unknown"}
DOMAINS_KARE      = {"atender", "ciclo_receita", "evolucao_negocio", "global", "implantar", "vender"}

# Cache de sessão — evita subprocess repetido por processo
_model_cache: Optional[str] = None
_slug_cache:  Optional[str] = None

def _detect_copilot_model() -> str:
    """Lê o modelo ativo do GitHub Copilot nas configurações do VS Code. Sem input manual."""
    global _model_cache
    if _model_cache is not None:
        return _model_cache
    import platform
    candidates = [_ROOT / ".vscode" / "settings.json"]
    if platform.system() == "Windows":
        candidates.append(Path(os.environ.get("APPDATA", "")) / "Code" / "User" / "settings.json")
    elif platform.system() == "Darwin":
        candidates.append(Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json")
    else:
        candidates.append(Path.home() / ".config" / "Code" / "User" / "settings.json")
    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for key in ("github.copilot.chat.defaultModel", "github.copilot.advanced.model"):
                if key in data and data[key]:
                    _model_cache = str(data[key]).strip()
                    return _model_cache
        except Exception:
            pass
    _model_cache = "unknown"
    return _model_cache

def _detect_context_slug() -> str:
    """Infere a iniciativa ativa pelo nome do branch git atual. Sem input manual."""
    global _slug_cache
    if _slug_cache is not None:
        return _slug_cache
    import subprocess, re
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=str(_ROOT), timeout=3,
        )
        if r.returncode == 0:
            branch = r.stdout.strip()
            m = re.search(r'(?i)(ini-\d+)', branch)
            if m:
                _slug_cache = m.group(1).lower()
                return _slug_cache
            if branch and branch not in ("HEAD", "main", "master") and len(branch) <= 50:
                _slug_cache = branch
                return _slug_cache
    except Exception:
        pass
    _slug_cache = "global"
    return _slug_cache

def _active_mode() -> str:
    mode = (os.environ.get("KARE_MODE") or "unknown").strip().lower()
    return mode if mode in INTERACTION_MODES else "unknown"


# ─── Schemas ───────────────────────────────────────────────────────────────────

_SCHEMA_PERENE = [
    """CREATE TABLE IF NOT EXISTS nodes (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        type         TEXT    NOT NULL,
        title        TEXT    NOT NULL,
        content      TEXT    NOT NULL DEFAULT '',
        symbols      TEXT    NOT NULL DEFAULT '',
        context_slug TEXT    NOT NULL DEFAULT 'global',
        layer        TEXT    NOT NULL DEFAULT 'project'
                         CHECK(layer IN ('universal', 'project')),
        pinned       INTEGER NOT NULL DEFAULT 0,
        metadata     TEXT    NOT NULL DEFAULT '{}',
        created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
        updated_at   TEXT    NOT NULL DEFAULT (datetime('now'))
    )""",
    """CREATE TABLE IF NOT EXISTS edges (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id  INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
        target_id  INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
        relation   TEXT    NOT NULL,
        weight     REAL    NOT NULL DEFAULT 1.0,
        created_at TEXT    NOT NULL DEFAULT (datetime('now'))
    )""",
    """CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts USING fts5(
        title, content, symbols,
        node_id UNINDEXED,
        tokenize = 'unicode61 remove_diacritics 1'
    )""",
    "CREATE INDEX IF NOT EXISTS idx_nodes_type    ON nodes(type)",
    "CREATE INDEX IF NOT EXISTS idx_nodes_context ON nodes(context_slug)",
    "CREATE INDEX IF NOT EXISTS idx_nodes_layer   ON nodes(layer)",
    """CREATE TRIGGER IF NOT EXISTS trg_nodes_ai AFTER INSERT ON nodes BEGIN
        INSERT INTO nodes_fts(rowid, title, content, symbols, node_id)
        VALUES (new.id, new.title, new.content, new.symbols, new.id);
    END""",
    """CREATE TRIGGER IF NOT EXISTS trg_nodes_au AFTER UPDATE OF title, content, symbols ON nodes BEGIN
        DELETE FROM nodes_fts WHERE rowid = old.id;
        INSERT INTO nodes_fts(rowid, title, content, symbols, node_id)
        VALUES (new.id, new.title, new.content, new.symbols, new.id);
    END""",
    """CREATE TRIGGER IF NOT EXISTS trg_nodes_ad AFTER DELETE ON nodes BEGIN
        DELETE FROM nodes_fts WHERE rowid = old.id;
    END""",
]

_SCHEMA_HISTORY = [
    """CREATE TABLE IF NOT EXISTS artifacts (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        type         TEXT    NOT NULL
                         CHECK(type IN ('adr','analysis','epic','initiative','prd','spec','story_map')),
        title        TEXT    NOT NULL,
        content      TEXT    NOT NULL DEFAULT '',
        symbols      TEXT    NOT NULL DEFAULT '',
        domain_refs  TEXT    NOT NULL DEFAULT '[]',
        status       TEXT    NOT NULL DEFAULT 'draft'
                         CHECK(status IN ('approved','draft','review','superseded')),
        version      TEXT    NOT NULL DEFAULT '1.0',
        author       TEXT    NOT NULL,
        metadata     TEXT    NOT NULL DEFAULT '{}',
        created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
        updated_at   TEXT    NOT NULL DEFAULT (datetime('now'))
    )""",
    """CREATE TABLE IF NOT EXISTS artifact_domains (
        artifact_id  INTEGER NOT NULL REFERENCES artifacts(id) ON DELETE CASCADE,
        domain       TEXT    NOT NULL,
        PRIMARY KEY  (artifact_id, domain)
    )""",
    """CREATE TABLE IF NOT EXISTS artifact_edges (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER NOT NULL REFERENCES artifacts(id) ON DELETE CASCADE,
        target_id INTEGER NOT NULL REFERENCES artifacts(id) ON DELETE CASCADE,
        relation  TEXT    NOT NULL
                      CHECK(relation IN ('conflicts_with','depends_on','implements','references','supersedes')),
        created_at TEXT   NOT NULL DEFAULT (datetime('now'))
    )""",
    """CREATE VIRTUAL TABLE IF NOT EXISTS artifacts_fts USING fts5(
        title, content, symbols, domain_refs,
        artifact_id UNINDEXED,
        tokenize = 'unicode61 remove_diacritics 1'
    )""",
    "CREATE INDEX IF NOT EXISTS idx_artifacts_type   ON artifacts(type)",
    "CREATE INDEX IF NOT EXISTS idx_artifacts_status ON artifacts(status)",
    "CREATE INDEX IF NOT EXISTS idx_artifacts_author ON artifacts(author)",
    """CREATE TRIGGER IF NOT EXISTS trg_artifacts_ai AFTER INSERT ON artifacts BEGIN
        INSERT INTO artifacts_fts(rowid, title, content, symbols, domain_refs, artifact_id)
        VALUES (new.id, new.title, new.content, new.symbols, new.domain_refs, new.id);
    END""",
    """CREATE TRIGGER IF NOT EXISTS trg_artifacts_au AFTER UPDATE OF title, content, symbols, domain_refs ON artifacts BEGIN
        DELETE FROM artifacts_fts WHERE rowid = old.id;
        INSERT INTO artifacts_fts(rowid, title, content, symbols, domain_refs, artifact_id)
        VALUES (new.id, new.title, new.content, new.symbols, new.domain_refs, new.id);
    END""",
    """CREATE TRIGGER IF NOT EXISTS trg_artifacts_ad AFTER DELETE ON artifacts BEGIN
        DELETE FROM artifacts_fts WHERE rowid = old.id;
    END""",
]

_SCHEMA_TELEMETRY = [
    """CREATE TABLE IF NOT EXISTS sessions (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      TEXT    NOT NULL,
        started_at   TEXT    NOT NULL DEFAULT (datetime('now')),
        ended_at     TEXT,
        duration_sec INTEGER
    )""",
    """CREATE TABLE IF NOT EXISTS events (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id       INTEGER REFERENCES sessions(id),
        user_id          TEXT    NOT NULL,
        agent            TEXT    NOT NULL DEFAULT 'unknown',
        model_id         TEXT    NOT NULL DEFAULT 'unknown',
        tokens_in        INTEGER NOT NULL DEFAULT 0,
        tokens_out       INTEGER NOT NULL DEFAULT 0,
        action_type      TEXT    NOT NULL DEFAULT 'query'
                             CHECK(action_type IN ('analysis','artifact_created','artifact_reviewed','other','planning','query')),
        interaction_mode TEXT    NOT NULL DEFAULT 'unknown',
        context_slug     TEXT    NOT NULL DEFAULT 'global',
        artifact_ref     TEXT,
        duration_ms      INTEGER,
        timestamp        TEXT    NOT NULL DEFAULT (datetime('now'))
    )""",
    # Migração incremental — silencioso se coluna já existir
    "ALTER TABLE events ADD COLUMN interaction_mode TEXT NOT NULL DEFAULT 'unknown'",
    "ALTER TABLE events ADD COLUMN cost_usd REAL NOT NULL DEFAULT 0.0",
    "ALTER TABLE events ADD COLUMN context_slug TEXT NOT NULL DEFAULT 'global'",
    "CREATE INDEX IF NOT EXISTS idx_events_user      ON events(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_events_session   ON events(session_id)",
    "CREATE INDEX IF NOT EXISTS idx_events_agent     ON events(agent)",
    "CREATE INDEX IF NOT EXISTS idx_events_model     ON events(model_id)",
    "CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)",
    "CREATE INDEX IF NOT EXISTS idx_events_slug      ON events(context_slug)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_user    ON sessions(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at)",
]


# ─── Conexões ──────────────────────────────────────────────────────────────────

def _open(db_path: Path) -> sqlite3.Connection:
    RAG_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def _init(conn: sqlite3.Connection, schema: list) -> None:
    for stmt in schema:
        try:
            conn.execute(stmt)
        except sqlite3.OperationalError as e:
            if "duplicate column name" not in str(e).lower():
                raise
    conn.commit()

def _perene()    -> sqlite3.Connection: return _open(DB_PERENE)
def _history()   -> sqlite3.Connection: return _open(DB_HISTORY)
def _telemetry() -> sqlite3.Connection: return _open(DB_TELEMETRY)


# ─── Proteção da base perene ───────────────────────────────────────────────────

def _perene_current_hash() -> str:
    """Hash da palavra-passe vigente: customizada (cofre AES-256-GCM do
    kare_credentials.py) se já configurada, senão a padrão de fábrica."""
    kc = _kare_credentials()
    if kc is not None:
        try:
            custom = kc.get_perene_rag_password()
            if custom:
                return hashlib.sha256(custom.encode()).hexdigest()
        except Exception:
            pass
    return _PERENE_FACTORY_HASH


def _perene_password_is_default() -> bool:
    kc = _kare_credentials()
    if kc is None:
        return True
    try:
        return not kc.get_perene_rag_password()
    except Exception:
        return True


def _perene_is_first_insertion() -> bool:
    """True se a base perene ainda não tem nenhum nó — ainda não houve nenhuma inserção."""
    if not DB_PERENE.exists():
        return True
    try:
        conn = _perene()
        total = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        conn.close()
        return total == 0
    except sqlite3.OperationalError:
        # tabela 'nodes' ainda não existe (schema não inicializado) = ainda não houve inserção
        return True


def _require_perene_password(provided: Optional[str]) -> bool:
    """Valida a palavra-passe antes de qualquer escrita na base perene.

    Retorna True se esta é a PRIMEIRA inserção já feita na base perene — o
    chamador (cmd_ingest/cmd_bootstrap/cmd_import) deve usar esse retorno
    para exibir a orientação de pós-primeira-inserção (troca de senha)."""
    first_insertion = _perene_is_first_insertion()

    if provided is None:
        try:
            import getpass
            prompt = (
                "Primeira inserção na base perene — informe a palavra-passe padrão "
                "de fábrica (documentada em README.md, seção 'Configuração do Ambiente'): "
                if first_insertion else
                "Palavra-passe para modificar a base perene: "
            )
            provided = getpass.getpass(prompt)
        except (EOFError, KeyboardInterrupt):
            _err("Operação cancelada.")

    if hashlib.sha256(provided.encode()).hexdigest() != _perene_current_hash():
        _err("Palavra-passe incorreta. Acesso negado à base perene.")

    return first_insertion


def _print_first_insertion_guidance() -> None:
    """Mensagem exibida uma única vez, ao final da primeira inserção na base perene.
    O agente que invocou o comando (tipicamente @kare-orchestrator) deve ler esta
    saída e perguntar ao usuário se deseja trocar a senha agora, informando os riscos."""
    print(
        "\n"
        "⚠️  PRIMEIRA INSERÇÃO NA BASE PERENE CONCLUÍDA\n"
        "A base está protegida pela senha padrão de fábrica.\n"
        "\n"
        "Riscos de manter a senha padrão:\n"
        "  - É uma senha pública, documentada no README deste repositório\n"
        "  - Não protege contra ninguém com acesso ao repositório\n"
        "  - Qualquer pessoa que já usou este template conhece o valor padrão\n"
        "\n"
        "Para trocar agora (fica salva criptografada — AES-256-GCM,\n"
        "chave fora do repositório, mesmo mecanismo do Jira/Confluence):\n"
        "  python .agent/scripts/infra/kare_credentials.py setup-perene\n"
    )


def cmd_perene_password(args) -> None:
    """Consulta ou troca a senha da base perene. O armazenamento real (cofre
    AES-256-GCM) é responsabilidade de kare_credentials.py — este comando é
    um atalho de leitura de status e um redirecionamento para lá, evitando
    duas implementações paralelas do mesmo mecanismo de senha."""
    action = args.action
    if action == "status":
        state = "PADRÃO DE FÁBRICA (não alterada)" if _perene_password_is_default() else "PERSONALIZADA"
        print(f"Senha da base perene: {state}")
        if _perene_password_is_default():
            print("⚠️  Ainda usando a senha padrão. Troque com:")
            print("   python .agent/scripts/infra/kare_credentials.py setup-perene")
        return

    if action == "change":
        print("Para trocar a senha da base perene, execute:")
        print("  python .agent/scripts/infra/kare_credentials.py setup-perene")
        print("(fica salva criptografada — AES-256-GCM, chave fora do repositório —")
        print(" no mesmo cofre já usado para as credenciais Jira/Confluence.)")
        return


# ─── Telemetry helper — fire-and-forget, never raises ─────────────────────────

def _telemetry_enabled() -> bool:
    """Opt-out global de telemetria: export KARE_TELEMETRY_DISABLED=1 (ou true/yes)."""
    return os.environ.get("KARE_TELEMETRY_DISABLED", "").strip().lower() not in ("1", "true", "yes")


def _telem(action_type: str, agent: str = 'system', tokens_in: int = 0, tokens_out: int = 0, artifact_ref: str = None) -> None:
    if not _telemetry_enabled():
        return
    try:
        conn  = _telemetry(); _init(conn, _SCHEMA_TELEMETRY)
        conn.execute(
            "INSERT INTO events (user_id, agent, model_id, tokens_in, tokens_out, action_type, interaction_mode, context_slug, artifact_ref) VALUES (?,?,?,?,?,?,?,?,?)",
            (_active_user(), agent, _detect_copilot_model(), tokens_in, tokens_out,
             action_type, _active_mode(), _detect_context_slug(), artifact_ref),
        )
        conn.commit(); conn.close()
    except Exception:
        pass


# ─── FTS helper ────────────────────────────────────────────────────────────────

def _fts(query: str) -> str:
    cleaned = re.sub(r'[^\w\s\-]', ' ', query, flags=re.UNICODE)
    terms = cleaned.split()
    return ' '.join(terms) if terms else '*'


# ─── Rerank + orçamento de tokens (sem modelo externo, determinístico) ─────────

def _estimate_tokens(text: str) -> int:
    """Mesma heurística já usada em _telem() para tokens_in: 1 token ~= 4 chars."""
    return len(text or "") // 4


def _rerank(results: list, query: str) -> list:
    """Combina o score BM25 (já retornado pelo SQL, negativo/menor=melhor) com um
    boost por match exato de termo no título/símbolos. Sem modelo externo — roda
    em memória, determinístico. Reordena `results` in-place por relevância desc."""
    terms = [t.lower() for t in _fts(query).split() if t != '*']
    for r in results:
        boost = 0.0
        title_l   = (r.get('title') or '').lower()
        symbols_l = (r.get('symbols') or '').lower()
        for t in terms:
            if t in title_l:
                boost += 2.0
            if t in symbols_l:
                boost += 1.0
        r['_relevance'] = abs(r.get('score', 0.0)) + boost
    results.sort(key=lambda r: r['_relevance'], reverse=True)
    return results


def _apply_token_budget(results: list, max_tokens: Optional[int]) -> list:
    """Trunca a lista (já ordenada por relevância) pelo orçamento de tokens,
    cortando os itens menos relevantes primeiro — nunca corta o texto de um
    item pela metade. Sem orçamento definido, devolve a lista inteira."""
    if not max_tokens:
        return results
    kept, used = [], 0
    for r in results:
        text = f"{r.get('title', '')} {r.get('content', '')} {r.get('symbols', '')}"
        cost = _estimate_tokens(text)
        if kept and used + cost > max_tokens:
            break
        kept.append(r)
        used += cost
        if used >= max_tokens:
            break
    return kept


# ─── PERENE — comandos ─────────────────────────────────────────────────────────

def cmd_search(args):
    db_flag = getattr(args, 'db', 'all')
    limit   = getattr(args, 'limit', 5)
    results = []

    if db_flag in ('perene', 'all'):
        c = _perene(); _init(c, _SCHEMA_PERENE)
        results += _search_nodes(c, args, source='perene')
        c.close()

    if db_flag in ('history', 'all'):
        c = _history(); _init(c, _SCHEMA_HISTORY)
        results += _search_artifacts(c, args, source='history')
        c.close()

    _rerank(results, args.query)
    results = results[:limit]
    results = _apply_token_budget(results, getattr(args, 'max_tokens', None))

    _telem('query', tokens_in=len(args.query) // 4)

    if not results:
        print("Nenhum resultado encontrado.")
        return

    if getattr(args, 'json', False):
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    header = f"\n-- Resultados: '{args.query}' " + "-" * 40
    sys.stdout.buffer.write((header + "\n").encode("utf-8"))
    for i, row in enumerate(results, 1):
        pinned  = "  [PINNED]" if row.get("pinned") else ""
        src     = f"[{row.get('_source','?')}]"
        snippet = row.get("content", "").replace("\n", " ")[:240]
        line = (
            f"\n[{i}] {abs(row['score']):.2f} | {src} [{row['type']}] {row['title']}{pinned}\n"
            f"    {snippet}...\n"
        )
        sys.stdout.buffer.write(line.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


def _search_nodes(conn, args, source: str) -> list:
    fts_q = _fts(args.query)
    params = [fts_q]
    extra  = ""
    layer  = getattr(args, 'layer', 'all')
    if layer != 'all':
        extra += " AND n.layer = ?"
        params.append(layer)
    params.append(getattr(args, 'limit', 5))
    sql = f"""
        SELECT n.id, n.type, n.title, n.content, n.symbols, n.layer, n.pinned,
               bm25(nodes_fts, 3.0, 1.0, 1.5) AS score
        FROM nodes_fts JOIN nodes n ON n.id = nodes_fts.rowid
        WHERE nodes_fts MATCH ? {extra}
        ORDER BY score LIMIT ?
    """
    try:
        rows = conn.execute(sql, params).fetchall()
        return [{**dict(r), "_source": source} for r in rows]
    except sqlite3.OperationalError:
        return []


def _search_artifacts(conn, args, source: str) -> list:
    fts_q = _fts(args.query)
    params = [fts_q, getattr(args, 'limit', 5)]
    sql = """
        SELECT a.id, a.type, a.title, a.content, a.symbols, a.domain_refs, a.status,
               bm25(artifacts_fts, 3.0, 1.0, 1.5, 0.5) AS score
        FROM artifacts_fts JOIN artifacts a ON a.id = artifacts_fts.rowid
        WHERE artifacts_fts MATCH ?
        ORDER BY score LIMIT ?
    """
    try:
        rows = conn.execute(sql, params).fetchall()
        return [{**dict(r), "_source": source, "pinned": 0, "layer": "project"} for r in rows]
    except sqlite3.OperationalError:
        return []


def cmd_ask(args):
    args.layer = 'all'
    args.db    = 'all'
    cmd_search(args)


def cmd_ingest(args):
    first_insertion = _require_perene_password(getattr(args, 'password', None))

    if getattr(args, 'file', None):
        try:
            content = Path(args.file).read_text(encoding="utf-8")
        except OSError as e:
            _err(f"Não foi possível ler o arquivo: {e}")
    elif getattr(args, 'content', None):
        content = args.content
    else:
        _err("Forneça --file <caminho> ou --content '<texto>'")

    if args.type not in NODE_TYPES_PERENE:
        _err(f"Tipo inválido '{args.type}'. Válidos: {', '.join(sorted(NODE_TYPES_PERENE))}")

    conn = _perene(); _init(conn, _SCHEMA_PERENE)
    conn.execute(
        "INSERT INTO nodes (type, title, content, symbols, context_slug, layer, pinned) VALUES (?,?,?,?,?,'project',0)",
        (args.type, args.title, content,
         getattr(args, 'symbols', '') or '',
         getattr(args, 'context', 'global') or 'global'),
    )
    conn.commit(); conn.close()
    _telem('artifact_created', tokens_in=len(content) // 4, artifact_ref=args.title)
    print(f"OK [perene] [{args.type}] '{args.title}'")
    if first_insertion:
        _print_first_insertion_guidance()


def cmd_bootstrap(args):
    first_insertion = _require_perene_password(getattr(args, 'password', None))

    seed_path = Path(args.seed) if getattr(args, 'seed', None) else DEFAULT_SEED
    if not seed_path.exists():
        _err(f"Seed não encontrado: {seed_path}")

    with open(seed_path, encoding="utf-8") as f:
        seed = json.load(f)

    conn = _perene(); _init(conn, _SCHEMA_PERENE)

    existing = conn.execute("SELECT COUNT(*) FROM nodes WHERE layer='universal'").fetchone()[0]
    force    = getattr(args, 'force', False)

    if existing and not force:
        print(f"Base perene já populada ({existing} nós). Use --force para repopular.")
        conn.close(); return

    if force and existing:
        conn.execute("DELETE FROM nodes WHERE layer='universal'")
        conn.commit()
        print(f"  Removidos {existing} nós anteriores.")

    nodes_data = seed.get("nodes", [])
    edges_data = seed.get("edges", [])
    ok = err = 0
    title_to_id: dict = {}

    for node in nodes_data:
        try:
            cur = conn.execute(
                "INSERT INTO nodes (type, title, content, symbols, context_slug, layer, pinned) VALUES (?,?,?,?,?,'universal',1)",
                (node["type"], node["title"],
                 node.get("content", ""), node.get("symbols", ""),
                 node.get("context_slug", "global")),
            )
            title_to_id[node["title"]] = cur.lastrowid
            ok += 1
        except Exception as e:
            print(f"  ERRO '{node.get('title', '?')}': {e}", file=sys.stderr)
            err += 1

    for edge in edges_data:
        src = title_to_id.get(edge.get("source"))
        tgt = title_to_id.get(edge.get("target"))
        if src and tgt:
            try:
                conn.execute(
                    "INSERT INTO edges (source_id, target_id, relation, weight) VALUES (?,?,?,?)",
                    (src, tgt, edge.get("relation", "related_to"), edge.get("weight", 1.0)),
                )
            except Exception as e:
                print(f"  EDGE ERRO: {e}", file=sys.stderr)

    conn.commit(); conn.close()
    suffix = f", {err} erros" if err else ""
    print(f"Bootstrap perene concluído: {ok} nós universais{suffix}")
    print(f"DB: {DB_PERENE}")
    if first_insertion:
        _print_first_insertion_guidance()


def cmd_migrate(args):
    """Inicializa schemas dos 3 bancos sem exigir senha (não toca em dados)."""
    conn = _perene(); _init(conn, _SCHEMA_PERENE)
    n = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    conn.close()
    print(f"[perene]    schema OK  |  {n} nós  |  {DB_PERENE.name}")

    conn = _history(); _init(conn, _SCHEMA_HISTORY)
    n = conn.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0]
    conn.close()
    print(f"[history]   schema OK  |  {n} artefatos  |  {DB_HISTORY.name}")

    conn = _telemetry(); _init(conn, _SCHEMA_TELEMETRY)
    n = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    conn.close()
    print(f"[telemetry] schema OK  |  {n} eventos  |  {DB_TELEMETRY.name}")

    perene_n = _perene().execute("SELECT COUNT(*) FROM nodes WHERE layer='universal'").fetchone()[0]
    if perene_n == 0:
        print("\nAVISO: base perene vazia. Execute: python kare_rag.py bootstrap")


def cmd_status(args):
    db_flag = getattr(args, 'db', 'all')
    lines   = ["\nKARE Context Engine — SQLite/FTS5 (standalone)\n"]

    if db_flag in ('perene', 'all') and DB_PERENE.exists():
        conn = _perene()
        total     = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        universal = conn.execute("SELECT COUNT(*) FROM nodes WHERE layer='universal'").fetchone()[0]
        project   = conn.execute("SELECT COUNT(*) FROM nodes WHERE layer='project'").fetchone()[0]
        by_type   = conn.execute("SELECT type, COUNT(*) n FROM nodes GROUP BY type ORDER BY n DESC").fetchall()
        conn.close()
        lines += [
            f"[PERENE] {DB_PERENE.name}",
            f"  Total: {total}  |  Universal: {universal}  |  Project: {project}",
            "  Tipos: " + ", ".join(f"{r['type']}:{r['n']}" for r in by_type),
            "",
        ]

    if db_flag in ('history', 'all') and DB_HISTORY.exists():
        conn = _history()
        total   = conn.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0]
        by_type = conn.execute("SELECT type, COUNT(*) n FROM artifacts GROUP BY type ORDER BY n DESC").fetchall()
        by_dom  = conn.execute("SELECT domain, COUNT(*) n FROM artifact_domains GROUP BY domain ORDER BY n DESC").fetchall()
        conn.close()
        lines += [
            f"[HISTORY] {DB_HISTORY.name}",
            f"  Total: {total}",
            "  Tipos: "    + (", ".join(f"{r['type']}:{r['n']}" for r in by_type) or "vazio"),
            "  Domínios: " + (", ".join(f"{r['domain']}:{r['n']}" for r in by_dom) or "nenhum"),
            "",
        ]

    if db_flag in ('telemetry', 'all') and DB_TELEMETRY.exists():
        conn  = _telemetry()
        total = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        if total:
            toks  = conn.execute("SELECT SUM(tokens_in), SUM(tokens_out) FROM events").fetchone()
            tok_in, tok_out = (toks[0] or 0), (toks[1] or 0)
            today = datetime.utcnow().strftime('%Y-%m-%d')
            since = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
            dau   = conn.execute("SELECT COUNT(DISTINCT user_id) FROM events WHERE timestamp LIKE ?", (today + '%',)).fetchone()[0]
            mau   = conn.execute("SELECT COUNT(DISTINCT user_id) FROM events WHERE timestamp >= ?", (since,)).fetchone()[0]
            agents = conn.execute("SELECT agent, COUNT(*) n FROM events GROUP BY agent ORDER BY n DESC LIMIT 5").fetchall()
            models = conn.execute("SELECT model_id, COUNT(*) n FROM events GROUP BY model_id ORDER BY n DESC LIMIT 5").fetchall()
            lines += [
                f"[TELEMETRIA] {DB_TELEMETRY.name}",
                f"  Eventos: {total:,}  |  DAU: {dau}  |  MAU (30d): {mau}",
                f"  Tokens: entrada={tok_in:,}  saída={tok_out:,}  total={tok_in+tok_out:,}",
                "  Agentes: " + (", ".join(f"{r['agent']}:{r['n']}" for r in agents) or "nenhum"),
                "  Modelos: " + (", ".join(f"{r['model_id']}:{r['n']}" for r in models) or "nenhum"),
                "",
            ]
        else:
            lines.append(f"[TELEMETRIA] {DB_TELEMETRY.name}  |  sem eventos ainda\n")
        conn.close()

    sys.stdout.buffer.write("\n".join(lines).encode("utf-8"))


def cmd_export(args):
    if not DB_PERENE.exists():
        _err(f"Banco não encontrado: {DB_PERENE}")
    default_out = _ROOT / "_outputs" / "rag-export.json"
    output = Path(getattr(args, 'output', None) or default_out)
    output.parent.mkdir(parents=True, exist_ok=True)
    conn = _perene()
    rows = conn.execute(
        "SELECT type, title, content, symbols, context_slug, metadata FROM nodes WHERE layer='project'"
    ).fetchall()
    conn.close()
    data = {"exported_at": datetime.utcnow().isoformat(), "nodes": [dict(r) for r in rows]}
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exportados {len(rows)} nós (project layer) -> {output}")


def cmd_import(args):
    first_insertion = _require_perene_password(getattr(args, 'password', None))
    input_path = Path(args.input)
    if not input_path.exists():
        _err(f"Arquivo não encontrado: {input_path}")
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)
    conn = _perene(); _init(conn, _SCHEMA_PERENE)
    ok = 0
    for node in data.get("nodes", []):
        try:
            conn.execute(
                "INSERT OR IGNORE INTO nodes (type, title, content, symbols, context_slug, layer, pinned, metadata) VALUES (?,?,?,?,?,'project',0,?)",
                (node.get("type", "artifact"), node["title"],
                 node.get("content", ""), node.get("symbols", ""),
                 node.get("context_slug", "global"), node.get("metadata", "{}")),
            )
            ok += 1
        except Exception as e:
            print(f"  ERRO '{node.get('title', '?')}': {e}", file=sys.stderr)
    conn.commit(); conn.close()
    print(f"Importados {ok} nós (project layer) de {input_path}")
    if first_insertion:
        _print_first_insertion_guidance()


# ─── HISTORY — comandos ────────────────────────────────────────────────────────

def cmd_history_ingest(args):
    if getattr(args, 'file', None):
        try:
            content = Path(args.file).read_text(encoding="utf-8")
        except OSError as e:
            _err(f"Não foi possível ler o arquivo: {e}")
    elif getattr(args, 'content', None):
        content = args.content
    else:
        _err("Forneça --file <caminho> ou --content '<texto>'")

    if args.type not in NODE_TYPES_HISTORY:
        _err(f"Tipo inválido '{args.type}'. Válidos: {', '.join(sorted(NODE_TYPES_HISTORY))}")

    raw_domains  = getattr(args, 'domains', '') or ''
    domains      = [d.strip().lower() for d in raw_domains.split(',') if d.strip()]
    domain_refs  = json.dumps(domains)
    author       = getattr(args, 'author', None) or _active_user()

    conn = _history(); _init(conn, _SCHEMA_HISTORY)

    existing = conn.execute(
        "SELECT id FROM artifacts WHERE title = ? AND type = ?", (args.title, args.type)
    ).fetchone()

    if existing and not getattr(args, 'update', False):
        print(f"Artefato já existe: [{args.type}] '{args.title}' (id={existing['id']}). Use --update para sobrescrever.")
        conn.close(); return

    if existing:
        conn.execute(
            "UPDATE artifacts SET content=?, symbols=?, domain_refs=?, status=?, version=?, updated_at=datetime('now') WHERE id=?",
            (content, getattr(args, 'symbols', '') or '', domain_refs,
             getattr(args, 'status', 'draft') or 'draft',
             getattr(args, 'version', '1.0') or '1.0',
             existing['id']),
        )
        conn.execute("DELETE FROM artifact_domains WHERE artifact_id=?", (existing['id'],))
        for d in domains:
            conn.execute("INSERT OR IGNORE INTO artifact_domains VALUES (?,?)", (existing['id'], d))
        conn.commit()
        _telem('artifact_reviewed', tokens_in=len(content) // 4, artifact_ref=args.title)
        print(f"Atualizado [history] [{args.type}] '{args.title}'  domínios={domains}")
    else:
        cur = conn.execute(
            "INSERT INTO artifacts (type, title, content, symbols, domain_refs, status, version, author) VALUES (?,?,?,?,?,?,?,?)",
            (args.type, args.title, content,
             getattr(args, 'symbols', '') or '',
             domain_refs,
             getattr(args, 'status', 'draft') or 'draft',
             getattr(args, 'version', '1.0') or '1.0',
             author),
        )
        artifact_id = cur.lastrowid
        for d in domains:
            conn.execute("INSERT OR IGNORE INTO artifact_domains VALUES (?,?)", (artifact_id, d))
        conn.commit()
        _telem('artifact_created', tokens_in=len(content) // 4, artifact_ref=args.title)
        print(f"OK [history] [{args.type}] '{args.title}'  id={artifact_id}  domínios={domains}")
    conn.close()


def cmd_history_search(args):
    conn = _history(); _init(conn, _SCHEMA_HISTORY)
    fts_q  = _fts(args.query)
    params = [fts_q]
    extra  = ""
    if getattr(args, 'domain', None):
        extra += " AND a.id IN (SELECT artifact_id FROM artifact_domains WHERE domain=?)"
        params.append(args.domain.lower())
    if getattr(args, 'type', None):
        extra += " AND a.type = ?"
        params.append(args.type)
    params.append(getattr(args, 'limit', 10))
    sql = f"""
        SELECT a.id, a.type, a.title, a.content, a.domain_refs, a.status, a.version, a.author,
               bm25(artifacts_fts, 3.0, 1.0, 1.5, 0.5) AS score
        FROM artifacts_fts JOIN artifacts a ON a.id = artifacts_fts.rowid
        WHERE artifacts_fts MATCH ? {extra}
        ORDER BY score LIMIT ?
    """
    try:
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError as e:
        _err(f"Erro na busca: {e}")
    conn.close()

    _telem('query', tokens_in=len(args.query) // 4)

    if not rows:
        print("Nenhum resultado encontrado.")
        return

    if getattr(args, 'json', False):
        print(json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2))
        return

    header = f"\n-- [HISTORY] Resultados: '{args.query}' " + "-" * 30
    sys.stdout.buffer.write((header + "\n").encode("utf-8"))
    for i, row in enumerate(rows, 1):
        domains = json.loads(row["domain_refs"] or "[]")
        snippet = row["content"].replace("\n", " ")[:240]
        line = (
            f"\n[{i}] {abs(row['score']):.2f} | [{row['type']}] {row['title']}  v{row['version']} [{row['status']}]  @{row['author']}\n"
            f"    domínios: {', '.join(domains) or 'nenhum'}\n"
            f"    {snippet}...\n"
        )
        sys.stdout.buffer.write(line.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


def cmd_history_list(args):
    conn = _history(); _init(conn, _SCHEMA_HISTORY)
    where  = ""
    params = []
    if getattr(args, 'type', None):
        where = " WHERE type = ?"
        params.append(args.type)
    elif getattr(args, 'domain', None):
        where = " WHERE id IN (SELECT artifact_id FROM artifact_domains WHERE domain=?)"
        params.append(args.domain.lower())
    rows = conn.execute(
        f"SELECT id, type, title, status, version, domain_refs, author, created_at FROM artifacts{where} ORDER BY created_at DESC",
        params,
    ).fetchall()
    conn.close()

    if not rows:
        print("Nenhum artefato encontrado.")
        return

    header = "\n-- [HISTORY] Artefatos " + "-" * 40 + "\n"
    sys.stdout.buffer.write(header.encode("utf-8"))
    for r in rows:
        domains = json.loads(r["domain_refs"] or "[]")
        line = (
            f"  [{r['id']:3d}] [{r['type']:<12}] {r['title'][:55]:<55}  "
            f"v{r['version']}  [{r['status']}]  @{r['author']}  [{', '.join(domains) or '-'}]\n"
        )
        sys.stdout.buffer.write(line.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


# ─── TELEMETRY — comandos ──────────────────────────────────────────────────────

def cmd_telemetry_log(args):
    if not _telemetry_enabled():
        print("Telemetria desativada (KARE_TELEMETRY_DISABLED) — nada foi registrado.")
        return
    if args.action_type not in ACTION_TYPES:
        _err(f"action-type inválido. Válidos: {', '.join(sorted(ACTION_TYPES))}")
    user  = getattr(args, 'user',  None) or _active_user()
    model = getattr(args, 'model', None) or _detect_copilot_model()
    mode  = getattr(args, 'interaction_mode', None) or _active_mode()
    if mode not in INTERACTION_MODES:
        mode = "unknown"
    slug  = getattr(args, 'context_slug', None) or _detect_context_slug()
    conn  = _telemetry(); _init(conn, _SCHEMA_TELEMETRY)
    conn.execute(
        "INSERT INTO events (session_id, user_id, agent, model_id, tokens_in, tokens_out, action_type, interaction_mode, context_slug, artifact_ref, duration_ms) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (
            getattr(args, 'session_id', None),
            user,
            getattr(args, 'agent', 'unknown'),
            model,
            getattr(args, 'tokens_in',  0) or 0,
            getattr(args, 'tokens_out', 0) or 0,
            args.action_type,
            mode,
            slug,
            getattr(args, 'artifact_ref', None),
            getattr(args, 'duration_ms', None),
        ),
    )
    conn.commit(); conn.close()
    print(f"OK [telemetria] user={user}  agente={args.agent}  modelo={model}  modo={mode}  iniciativa={slug}  ação={args.action_type}")


def cmd_telemetry_session_start(args):
    if not _telemetry_enabled():
        print("Telemetria desativada (KARE_TELEMETRY_DISABLED) — sessão não registrada.")
        return
    user = getattr(args, 'user', None) or _active_user()
    conn = _telemetry(); _init(conn, _SCHEMA_TELEMETRY)
    cur = conn.execute("INSERT INTO sessions (user_id) VALUES (?)", (user,))
    session_id = cur.lastrowid
    conn.commit(); conn.close()
    print(f"Sessão iniciada: id={session_id}  user={user}")


def cmd_telemetry_session_end(args):
    if not _telemetry_enabled():
        print("Telemetria desativada (KARE_TELEMETRY_DISABLED) — sessão não registrada.")
        return
    conn = _telemetry(); _init(conn, _SCHEMA_TELEMETRY)
    session = conn.execute("SELECT id, started_at FROM sessions WHERE id=?", (args.session_id,)).fetchone()
    if not session:
        _err(f"Sessão não encontrada: {args.session_id}")
    started  = datetime.fromisoformat(session["started_at"])
    ended    = datetime.utcnow()
    duration = int((ended - started).total_seconds())
    conn.execute(
        "UPDATE sessions SET ended_at=?, duration_sec=? WHERE id=?",
        (ended.isoformat(), duration, args.session_id),
    )
    conn.commit(); conn.close()
    print(f"Sessão {args.session_id} encerrada: {duration}s ({duration // 60}min {duration % 60}s)")


def cmd_telemetry_stats(args):
    if not DB_TELEMETRY.exists():
        print("Base de telemetria ainda não criada. Execute: python kare_rag.py migrate")
        return
    conn  = _telemetry(); _init(conn, _SCHEMA_TELEMETRY)
    days  = getattr(args, 'days', 30) or 30
    since = (datetime.utcnow() - timedelta(days=days)).strftime('%Y-%m-%d')
    today = datetime.utcnow().strftime('%Y-%m-%d')

    user_filter  = getattr(args, 'user',  None)
    agent_filter = getattr(args, 'agent', None)
    quiet        = getattr(args, 'quiet', False)

    filters, fparams = [], []
    if user_filter:  filters.append("user_id = ?");  fparams.append(user_filter)
    if agent_filter: filters.append("agent = ?");    fparams.append(agent_filter)
    extra = (" AND " + " AND ".join(filters)) if filters else ""

    def q(sql, *p): return conn.execute(sql, list(p) + fparams).fetchone()
    def qa(sql, *p): return conn.execute(sql, list(p) + fparams).fetchall()

    total    = q(f"SELECT COUNT(*) FROM events WHERE timestamp >= ?{extra}", since)[0]
    toks     = q(f"SELECT SUM(tokens_in), SUM(tokens_out) FROM events WHERE timestamp >= ?{extra}", since)
    tok_in, tok_out = (toks[0] or 0), (toks[1] or 0)
    dau      = q(f"SELECT COUNT(DISTINCT user_id) FROM events WHERE timestamp LIKE ?{extra}", today + '%')[0]
    mau      = q(f"SELECT COUNT(DISTINCT user_id) FROM events WHERE timestamp >= ?{extra}", since)[0]
    sessions = q(f"SELECT COUNT(*) FROM sessions WHERE started_at >= ?", since)[0]
    avg_sess = q(f"SELECT AVG(duration_sec) FROM sessions WHERE duration_sec IS NOT NULL AND started_at >= ?", since)[0]
    avg_ev   = q(f"SELECT AVG(duration_ms) FROM events WHERE duration_ms IS NOT NULL AND timestamp >= ?{extra}", since)[0]
    agents   = qa(f"SELECT agent, COUNT(*) n FROM events WHERE timestamp >= ?{extra} GROUP BY agent ORDER BY n DESC LIMIT 10", since)
    models   = qa(f"SELECT model_id, COUNT(*) n FROM events WHERE timestamp >= ?{extra} GROUP BY model_id ORDER BY n DESC", since)
    acts     = qa(f"SELECT action_type, COUNT(*) n FROM events WHERE timestamp >= ?{extra} GROUP BY action_type ORDER BY n DESC", since)
    modes    = qa(f"SELECT interaction_mode, COUNT(*) n FROM events WHERE timestamp >= ?{extra} AND interaction_mode != 'unknown' GROUP BY interaction_mode ORDER BY n DESC", since)
    users    = qa(f"SELECT user_id, COUNT(*) n FROM events WHERE timestamp >= ?{extra} GROUP BY user_id ORDER BY n DESC LIMIT 10", since)
    slugs    = qa(f"SELECT context_slug, COUNT(*) n FROM events WHERE timestamp >= ?{extra} AND context_slug != 'global' GROUP BY context_slug ORDER BY n DESC LIMIT 10", since)
    conn.close()

    if quiet:
        sys.stdout.buffer.write(f"[telemetria] {total} eventos  {tok_in+tok_out:,} tokens (est.)  {sessions} sessões\n".encode("utf-8"))
        return

    avg_s   = int(avg_sess or 0)
    filtros = "  ".join(filter(None, [
        f"user=@{user_filter}"   if user_filter  else "",
        f"agente={agent_filter}" if agent_filter else "",
    ]))
    lines = [
        f"\n[TELEMETRIA KARE — GitHub Copilot] últimos {days} dias (desde {since})" + (f"  [{filtros}]" if filtros else ""),
        "",
        f"  Interações     : {total:,}",
        f"  Sessões        : {sessions:,}",
        f"  DAU            : {dau}",
        f"  MAU ({days}d)  : {mau}",
        f"  Duração sessão : {avg_s // 60}min {avg_s % 60}s (média)",
        f"  Dur. evento    : {int(avg_ev or 0):,}ms (média)",
        f"  Vol. consultas : {tok_in:,} chars est. (entrada)  {tok_out:,} (saída)",
        "",
        "  Usuários ativos:",
    ]
    for r in users:
        lines.append(f"    @{r['user_id']:<40} {r['n']:>6} eventos")
    if slugs:
        lines += ["", "  Iniciativas mais ativas:"]
        for r in slugs:
            lines.append(f"    {r['context_slug']:<40} {r['n']:>6} eventos")
    lines += ["", "  Modelos Copilot detectados:"]
    for r in models:
        label = r['model_id'] if r['model_id'] != 'unknown' else '(não configurado em settings.json)'
        lines.append(f"    {label:<40} {r['n']:>6} usos")
    lines += ["", "  Agentes mais utilizados:"]
    for r in agents:
        lines.append(f"    {r['agent']:<40} {r['n']:>6}")
    lines += ["", "  Tipos de ação:"]
    for r in acts:
        lines.append(f"    {r['action_type']:<24} {r['n']:>6}")
    if modes:
        lines += ["", "  Modos Copilot (agent/ask/edit):"]
        for r in modes:
            lines.append(f"    {r['interaction_mode']:<24} {r['n']:>6}")
    lines.append("")
    sys.stdout.buffer.write("\n".join(lines).encode("utf-8"))


# ─── Helpers ───────────────────────────────────────────────────────────────────

def _err(msg: str) -> None:
    print(f"ERRO: {msg}", file=sys.stderr)
    sys.exit(1)


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        prog="kare_rag",
        description="KARE Context Engine — 3 bancos: perene | history | telemetry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # search
    s = sub.add_parser("search", help="Busca BM25 (perene + history por padrão)")
    s.add_argument("query")
    s.add_argument("--limit",  type=int, default=5)
    s.add_argument("--db",     choices=["perene", "history", "all"], default="all")
    s.add_argument("--layer",  choices=["all", "universal", "project"], default="all")
    s.add_argument("--json",   action="store_true")
    s.add_argument("--max-tokens", type=int, default=None, dest="max_tokens",
                   help="Orçamento de tokens (estima 1 token ~= 4 chars); corta os resultados menos relevantes primeiro")

    # ask
    s = sub.add_parser("ask", help="Alias de search")
    s.add_argument("query")
    s.add_argument("--limit",  type=int, default=10)
    s.add_argument("--json",   action="store_true")
    s.add_argument("--max-tokens", type=int, default=None, dest="max_tokens",
                   help="Orçamento de tokens (estima 1 token ~= 4 chars); corta os resultados menos relevantes primeiro")

    # ingest (perene — requer senha)
    s = sub.add_parser("ingest", help="Adiciona nó à base perene (requer palavra-passe)")
    s.add_argument("--title",    required=True)
    s.add_argument("--type",     required=True, choices=sorted(NODE_TYPES_PERENE))
    s.add_argument("--context",  default="global")
    s.add_argument("--file",     default=None)
    s.add_argument("--content",  default=None)
    s.add_argument("--symbols",  default="")
    s.add_argument("--password", default=None)

    # bootstrap
    s = sub.add_parser("bootstrap", help="Popula base perene com seed JSON (requer palavra-passe)")
    s.add_argument("--seed",     default=None)
    s.add_argument("--force",    action="store_true")
    s.add_argument("--password", default=None)

    # migrate
    sub.add_parser("migrate", help="Inicializa schemas dos 3 bancos sem tocar em dados")

    # status
    s = sub.add_parser("status", help="Mostra estatísticas de todos os bancos")
    s.add_argument("--db", choices=["perene", "history", "telemetry", "all"], default="all")

    # export / import
    s = sub.add_parser("export", help="Exporta project layer do perene para JSON")
    s.add_argument("--output", default=None)

    s = sub.add_parser("import", help="Importa nós ao perene (requer palavra-passe)")
    s.add_argument("--input",    required=True)
    s.add_argument("--password", default=None)

    # perene-password
    s = sub.add_parser("perene-password", help="Consulta ou troca a palavra-passe da base perene")
    s.add_argument("action", choices=["status", "change"])

    # history
    ph = sub.add_parser("history", help="Artefatos: PRDs, ADRs, análises, specs")
    hs = ph.add_subparsers(dest="history_cmd", required=True)

    s = hs.add_parser("ingest", help="Adiciona/atualiza artefato")
    s.add_argument("--title",   required=True)
    s.add_argument("--type",    required=True, choices=sorted(NODE_TYPES_HISTORY))
    s.add_argument("--domains", default="", help="Domínios do projeto separados por vírgula: vender,implantar,...")
    s.add_argument("--file",    default=None)
    s.add_argument("--content", default=None)
    s.add_argument("--symbols", default="")
    s.add_argument("--status",  choices=["draft", "review", "approved", "superseded"], default="draft")
    s.add_argument("--version", default="1.0")
    s.add_argument("--author",  default=None, help="Padrão: KARE_USER env var")
    s.add_argument("--update",  action="store_true")

    s = hs.add_parser("search", help="Busca em artefatos")
    s.add_argument("query")
    s.add_argument("--limit",  type=int, default=10)
    s.add_argument("--domain", default=None)
    s.add_argument("--type",   choices=sorted(NODE_TYPES_HISTORY), default=None)
    s.add_argument("--json",   action="store_true")

    s = hs.add_parser("list", help="Lista artefatos")
    s.add_argument("--type",   choices=sorted(NODE_TYPES_HISTORY), default=None)
    s.add_argument("--domain", default=None)

    # telemetry
    pt = sub.add_parser("telemetry", help="Telemetria de uso do KARE")
    ts = pt.add_subparsers(dest="telemetry_cmd", required=True)

    s = ts.add_parser("log", help="Registra evento de uso")
    s.add_argument("--agent",            required=True)
    s.add_argument("--model",            default=None,
                   help="Padrão: lido de .vscode/settings.json (github.copilot.chat.defaultModel)")
    s.add_argument("--interaction-mode", choices=sorted(INTERACTION_MODES), default=None, dest="interaction_mode",
                   help="Modo Copilot: agent|ask|edit. Padrão: KARE_MODE env var")
    s.add_argument("--context-slug",     default=None, dest="context_slug",
                   help="Padrão: inferido do branch git atual")
    s.add_argument("--tokens-in",        type=int, default=0,   dest="tokens_in")
    s.add_argument("--tokens-out",       type=int, default=0,   dest="tokens_out")
    s.add_argument("--action-type",      choices=sorted(ACTION_TYPES), default="query", dest="action_type")
    s.add_argument("--duration-ms",      type=int, default=None, dest="duration_ms")
    s.add_argument("--session-id",       type=int, default=None, dest="session_id")
    s.add_argument("--artifact-ref",     default=None,           dest="artifact_ref")
    s.add_argument("--user",             default=None, help="Padrão: KARE_USER env var")

    s = ts.add_parser("stats", help="Estatísticas de uso")
    s.add_argument("--days",  type=int, default=30)
    s.add_argument("--user",  default=None, help="Filtra por usuário específico")
    s.add_argument("--agent", default=None, help="Filtra por agente específico")
    s.add_argument("--quiet", action="store_true", help="Saída mínima (para Task Scheduler)")

    s = ts.add_parser("session-start", help="Inicia sessão")
    s.add_argument("--user", default=None, help="Padrão: KARE_USER env var")

    s = ts.add_parser("session-end", help="Encerra sessão")
    s.add_argument("--session-id", type=int, required=True, dest="session_id")

    args = p.parse_args()

    dispatch = {
        "search":    cmd_search,
        "ask":       cmd_ask,
        "ingest":    cmd_ingest,
        "bootstrap": cmd_bootstrap,
        "migrate":   cmd_migrate,
        "status":    cmd_status,
        "export":    cmd_export,
        "import":    cmd_import,
        "perene-password": cmd_perene_password,
    }

    if args.cmd == "history":
        {"ingest": cmd_history_ingest, "search": cmd_history_search, "list": cmd_history_list}[args.history_cmd](args)
    elif args.cmd == "telemetry":
        {
            "log":           cmd_telemetry_log,
            "stats":         cmd_telemetry_stats,
            "session-start": cmd_telemetry_session_start,
            "session-end":   cmd_telemetry_session_end,
        }[args.telemetry_cmd](args)
    else:
        dispatch[args.cmd](args)


if __name__ == "__main__":
    main()
