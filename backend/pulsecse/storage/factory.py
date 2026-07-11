from __future__ import annotations

from pulsecse.config import settings
from pulsecse.storage.sqlite import SQLiteRepository


def build_repository():
    if settings.uses_postgres:
        from pulsecse.storage.postgres import PostgresRepository
        return PostgresRepository(settings.database_url)
    return SQLiteRepository(settings.database_path)
