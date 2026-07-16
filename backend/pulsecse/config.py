from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "PulseCSE Pro"
    version: str = "0.5.0"  # Added a version for better tracking and production readiness
    database_url: str = os.getenv("PULSECSE_DATABASE", "sqlite:///data/pulsecse.sqlite3")
    default_user_id: str = os.getenv("PULSECSE_DEFAULT_USER", "demo")
    market_provider: str = os.getenv("PULSECSE_MARKET_PROVIDER", "mock")
    cse_base_url: str = os.getenv("PULSECSE_CSE_BASE_URL", "https://www.cse.lk")
    telegram_token: str = os.getenv("PULSECSE_TELEGRAM_TOKEN", "")
    telegram_chat_id: str = os.getenv("PULSECSE_TELEGRAM_CHAT_ID", "")
    webhook_url: str = os.getenv("PULSECSE_WEBHOOK_URL", "")
    host: str = os.getenv("PULSECSE_HOST", "127.0.0.1")
    port: int = int(os.getenv("PULSECSE_PORT", "8088"))
    health_port: int = int(os.getenv("PULSECSE_HEALTH_PORT", "8089"))
    poll_interval_seconds: int = int(os.getenv("PULSECSE_POLL_INTERVAL_SECONDS", "60"))
    poll_jitter_seconds: int = int(os.getenv("PULSECSE_POLL_JITTER_SECONDS", "8"))
    market_timezone: str = os.getenv("PULSECSE_MARKET_TIMEZONE", "Asia/Colombo")
    market_open: str = os.getenv("PULSECSE_MARKET_OPEN", "09:30")
    market_close: str = os.getenv("PULSECSE_MARKET_CLOSE", "14:30")
    log_json: bool = os.getenv("PULSECSE_LOG_JSON", "1") != "0"

    @property
    def database_path(self) -> Path:
        if self.database_url.startswith("sqlite:///"):
            return Path(self.database_url.replace("sqlite:///", "", 1))
        return Path(self.database_url)

    @property
    def uses_postgres(self) -> bool:
        return self.database_url.startswith(("postgresql://", "postgres://"))


settings = Settings()