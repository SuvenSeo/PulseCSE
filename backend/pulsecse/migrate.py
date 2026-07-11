from __future__ import annotations

from pathlib import Path

from pulsecse.config import settings
from pulsecse.storage.factory import build_repository


def migrations_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "db" / "migrations"


def run_migrations() -> list[str]:
    repo = build_repository()
    applied = set(repo.applied_migrations()) if hasattr(repo, "applied_migrations") else set()
    ran: list[str] = []
    if settings.uses_postgres:
        files = sorted((migrations_dir() / "postgres").glob("*.sql"))
        for file in files:
            if file.name in applied:
                continue
            with repo.conn.cursor() as cur:  # type: ignore[attr-defined]
                cur.execute(file.read_text())
            repo.mark_migration(file.name)
            ran.append(file.name)
    else:
        # SQLite repository creates/updates its schema on connect. Mark logical migrations for audit parity.
        for name in ["001_sqlite_schema", "002_sqlite_indexes"]:
            if name not in applied:
                repo.mark_migration(name)
                ran.append(name)
    repo.close()
    return ran


if __name__ == "__main__":
    for name in run_migrations():
        print(f"applied {name}")
