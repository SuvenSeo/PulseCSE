from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "PulseCSE Pro"
    database_url: str = os.getenv("PULSECSE_DATABASE", "data/pulsecse.sqlite3")
    default_user_id: str = os.getenv("PULSECSE_DEFAULT_USER", "demo")
    market_provider: str = os.getenv("PULSECSE_MARKET_PROVIDER", "mock")
    telegram_token: str = os.getenv("PULSECSE_TELEGRAM_TOKEN", "")
    telegram_chat_id: str = os.getenv("PULSECSE_TELEGRAM_CHAT_ID", "")
    webhook_url: str = os.getenv("PULSECSE_WEBHOOK_URL", "")
    host: str = os.getenv("PULSECSE_HOST", "127.0.0.1")
    port: int = int(os.getenv("PULSECSE_PORT", "8088"))

    @property
    def database_path(self) -> Path:
        return Path(self.database_url)


settings = Settings()
