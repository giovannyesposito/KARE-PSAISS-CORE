"""
kare_metrics_local.py — Exportador de Métricas KARE para arquivo local

Lê o log JSONL de invocações (.specify/telemetry/agent-invocations.jsonl),
gera um arquivo .txt com conteúdo CSV (separado por ;) na pasta local do usuário
e sobrescreve o arquivo anterior a cada execução.

Destino:
    C:\\Users\\{USERNAME}\\kare_metrics\\metrics_{username}_{YYYY-MM-DD_HH-MM}.txt

Comportamento:
    - Detecta USERNAME automaticamente via variável de ambiente do Windows
    - Cria a pasta C:\\Users\\{USERNAME}\\kare_metrics\\ se não existir
    - Deleta qualquer arquivo metrics_{username}_*.txt anterior (um por vez — sem acúmulo)
    - Escreve o novo arquivo com timestamp atualizado no nome
    - Encoding UTF-8-BOM para compatibilidade direta com Excel

Campos CSV:
    timestamp;user;session_id;agent;command;status;tokens_est;
    latency_ms;artifact_type;time_saved_min;session_concluded

Uso (chamado pelo Task Scheduler a cada 30 min):
    python .agent/scripts/telemetry/kare_metrics_local.py

Uso manual para diagnóstico:
    python .agent/scripts/telemetry/kare_metrics_local.py --dry-run
    python .agent/scripts/telemetry/kare_metrics_local.py --status
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
_SCRIPT_DIR   = Path(__file__).parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent   # raiz do projeto instalado
_JSONL_FILE   = _PROJECT_ROOT / ".specify" / "telemetry" / "agent-invocations.jsonl"

_CSV_COLUMNS = [
    "timestamp",
    "user",
    "session_id",
    "agent",
    "command",
    "status",
    "tokens_est",
    "latency_ms",
    "artifact_type",
    "time_saved_min",
    "session_concluded",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_username() -> str:
    """Detecta o username Windows atual."""
    return (
        os.environ.get("USERNAME")
        or os.environ.get("USER")
        or "unknown"
    ).lower()


def _get_dest_folder(username: str) -> Path:
    """Retorna C:\\Users\\{USERNAME}\\kare_metrics\\"""
    user_profile = os.environ.get("USERPROFILE") or str(Path.home())
    return Path(user_profile) / "kare_metrics"


def _build_filename(username: str) -> str:
    """Gera nome do arquivo com timestamp atual: metrics_{user}_{YYYY-MM-DD_HH-MM}.txt"""
    now = datetime.now()
    ts  = now.strftime("%Y-%m-%d_%H-%M")
    return f"metrics_{username}_{ts}.txt"


def _read_jsonl() -> list[dict]:
    """Lê todas as entradas do JSONL de telemetria."""
    if not _JSONL_FILE.exists():
        return []
    entries = []
    with open(_JSONL_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _delete_old_files(folder: Path, username: str) -> list[str]:
    """Remove arquivos metrics_{username}_*.txt anteriores. Retorna lista de nomes deletados."""
    deleted = []
    pattern = f"metrics_{username}_*.txt"
    for f in folder.glob(pattern):
        try:
            f.unlink()
            deleted.append(f.name)
        except OSError:
            pass
    return deleted


def _write_csv(dest_file: Path, entries: list[dict]) -> int:
    """
    Escreve o arquivo .txt com conteúdo CSV separado por ';'.
    Encoding UTF-8-BOM para compatibilidade com Excel.
    Retorna o número de linhas escritas (sem contar o header).
    """
    dest_file.parent.mkdir(parents=True, exist_ok=True)

    with open(dest_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(_CSV_COLUMNS)
        for entry in entries:
            writer.writerow([
                entry.get("timestamp", ""),
                entry.get("user", ""),
                entry.get("session_id", ""),
                entry.get("agent", ""),
                entry.get("command", ""),
                entry.get("status", ""),
                entry.get("tokens_est", 0),
                entry.get("latency_ms", 0),
                entry.get("artifact_type", ""),
                entry.get("time_saved_min", 0.0),
                entry.get("session_concluded", 0),
            ])
    return len(entries)


# ---------------------------------------------------------------------------
# Ações CLI
# ---------------------------------------------------------------------------
def cmd_export(dry_run: bool = False) -> None:
    username   = _get_username()
    dest_folder = _get_dest_folder(username)
    dest_file   = dest_folder / _build_filename(username)
    entries     = _read_jsonl()

    print(f"KARE Metrics — Exportação local")
    print(f"   Usuário   : {username}")
    print(f"   Destino   : {dest_folder}")
    print(f"   Arquivo   : {dest_file.name}")
    print(f"   Entradas  : {len(entries)} invocações no JSONL")

    if dry_run:
        print("\n[dry-run] Nenhum arquivo foi criado ou deletado.")
        return

    # Criar pasta se necessário
    dest_folder.mkdir(parents=True, exist_ok=True)

    # Deletar arquivo anterior do mesmo usuário
    deleted = _delete_old_files(dest_folder, username)
    if deleted:
        for name in deleted:
            print(f"   Deletado  : {name}")

    # Escrever novo arquivo
    rows = _write_csv(dest_file, entries)
    size_kb = dest_file.stat().st_size / 1024
    print(f"\n✅ Exportado: {dest_file}")
    print(f"   Linhas    : {rows} | Tamanho: {size_kb:.1f} KB")


def cmd_status() -> None:
    username    = _get_username()
    dest_folder = _get_dest_folder(username)
    pattern     = f"metrics_{username}_*.txt"

    print(f"KARE Metrics — Status local")
    print(f"   Usuário : {username}")
    print(f"   Pasta   : {dest_folder}")
    print(f"   JSONL   : {_JSONL_FILE}")

    if not _JSONL_FILE.exists():
        print("\n⚠️  JSONL não encontrado — nenhuma invocação registrada ainda.")
    else:
        count = sum(1 for line in open(_JSONL_FILE, encoding="utf-8") if line.strip())
        print(f"   Entradas no JSONL: {count}")

    if not dest_folder.exists():
        print(f"\n⚠️  Pasta de métricas não existe ainda: {dest_folder}")
        print("   Execute 'kare-agent setup-telemetry' para configurar.")
    else:
        files = list(dest_folder.glob(pattern))
        if files:
            latest = max(files, key=lambda f: f.stat().st_mtime)
            size_kb = latest.stat().st_size / 1024
            from datetime import datetime
            mtime = datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            print(f"\n✅ Arquivo atual : {latest.name}")
            print(f"   Modificado    : {mtime} | Tamanho: {size_kb:.1f} KB")
        else:
            print(f"\n⚠️  Nenhum arquivo metrics_{username}_*.txt encontrado em {dest_folder}")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------
def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="KARE Metrics Local — Exporta métricas de uso para arquivo local",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simula a exportação sem criar ou deletar arquivos",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Exibe status atual (pasta, arquivo mais recente, contagem de entradas)",
    )
    args = parser.parse_args()

    if args.status:
        cmd_status()
    else:
        cmd_export(dry_run=args.dry_run)


if __name__ == "__main__":
    _cli()
