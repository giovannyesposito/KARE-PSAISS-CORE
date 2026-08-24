"""
sqlite_to_neo4j.py — Exporta kare_perene_rag.db para Neo4j (visualização via Bevel)

Uso:
    python .agent/scripts/infra/sqlite_to_neo4j.py
    python .agent/scripts/infra/sqlite_to_neo4j.py --uri bolt://localhost:7687 --password sua_senha

Pré-requisito: Neo4j rodando (Docker):
    docker run -d --name kare-neo4j -p 7474:7474 -p 7687:7687 \
        -e NEO4J_AUTH=neo4j/KARE2026 neo4j:5

Depois abra o Bevel no VS Code e conecte em:
    URI:      bolt://localhost:7687
    Usuário:  neo4j
    Senha:    KARE2026
"""

import argparse
import sqlite3
from pathlib import Path

ROOT     = Path(__file__).parents[3]
DB_PATH  = ROOT / ".specify" / "rag" / "kare_perene_rag.db"

DEFAULT_URI  = "bolt://localhost:7687"
DEFAULT_USER = "neo4j"
DEFAULT_PASS = "KARE2026"


def get_args():
    p = argparse.ArgumentParser(description="Exporta SQLite RAG → Neo4j")
    p.add_argument("--uri",      default=DEFAULT_URI,  help="Bolt URI do Neo4j")
    p.add_argument("--user",     default=DEFAULT_USER, help="Usuário Neo4j")
    p.add_argument("--password", default=DEFAULT_PASS, help="Senha Neo4j")
    p.add_argument("--clear",    action="store_true",  help="Limpa o grafo antes de importar")
    return p.parse_args()


def load_sqlite():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    nodes = conn.execute(
        "SELECT id, type, title, content, symbols, context_slug, layer, pinned FROM nodes"
    ).fetchall()
    edges = conn.execute(
        """SELECT e.id, e.source_id, e.target_id, e.relation, e.weight,
                  n1.title AS source_title, n2.title AS target_title
           FROM edges e
           JOIN nodes n1 ON n1.id = e.source_id
           JOIN nodes n2 ON n2.id = e.target_id"""
    ).fetchall()
    conn.close()
    return [dict(n) for n in nodes], [dict(e) for e in edges]


def run(args):
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("Instale o driver: pip install neo4j")
        raise SystemExit(1)

    nodes, edges = load_sqlite()
    print(f"Carregado: {len(nodes)} nós, {len(edges)} arestas do SQLite")

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))

    with driver.session() as s:
        if args.clear:
            s.run("MATCH (n) DETACH DELETE n")
            print("Grafo limpo.")

        # Criar nós — label = tipo capitalizado (ex: concept → Concept)
        for n in nodes:
            label = n["type"].capitalize()
            s.run(
                f"""MERGE (x:KareNode:{label} {{sqlite_id: $id}})
                    SET x.title       = $title,
                        x.content     = $content,
                        x.symbols     = $symbols,
                        x.context     = $context_slug,
                        x.layer       = $layer,
                        x.pinned      = $pinned""",
                id=n["id"], title=n["title"], content=n["content"],
                symbols=n["symbols"], context_slug=n["context_slug"],
                layer=n["layer"], pinned=bool(n["pinned"]),
            )
        print(f"  OK {len(nodes)} nos criados")

        # Criar arestas — relation vira tipo de relação em UPPER_CASE
        for e in edges:
            rel_type = e["relation"].upper()
            s.run(
                f"""MATCH (a:KareNode {{sqlite_id: $src}}), (b:KareNode {{sqlite_id: $tgt}})
                    MERGE (a)-[r:{rel_type} {{weight: $weight}}]->(b)""",
                src=e["source_id"], tgt=e["target_id"], weight=e["weight"],
            )
        print(f"  OK {len(edges)} arestas criadas")

    driver.close()
    print("\nPronto! Abra o Bevel no VS Code:")
    print(f"  URI:     {args.uri}")
    print(f"  Usuário: {args.user}")
    print(f"  Senha:   {args.password}")
    print("\nQuery sugerida para visualizar tudo:")
    print("  MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100")


if __name__ == "__main__":
    run(get_args())
