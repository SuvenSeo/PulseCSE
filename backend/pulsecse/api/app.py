from __future__ import annotations

from pathlib import Path
from typing import Any
from dataclasses import replace

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover - allows pure-engine tests without optional deps
    FastAPI = None  # type: ignore
    HTTPException = Exception  # type: ignore
    CORSMiddleware = None  # type: ignore
    FileResponse = None  # type: ignore
    StaticFiles = None  # type: ignore
    BaseModel = object  # type: ignore
    Field = lambda default=None, **_: default  # type: ignore

from pulsecse.config import settings
from pulsecse.core.models import AlertRule, AlertStatus, AlertType, DeliveryChannel, new_id
from pulsecse.notifications.console import ConsoleNotifier
from pulsecse.notifications.telegram import TelegramNotifier
from pulsecse.notifications.webhook import WebhookNotifier
from pulsecse.services.market_service import MarketService
from pulsecse.storage.sqlite import SQLiteRepository


if BaseModel is object:
    class AlertIn:  # type: ignore
        pass
else:
    class AlertIn(BaseModel):
        symbol: str = Field(..., min_length=3)
        type: AlertType
        target: float = 0
        note: str = ""
        cooldown_minutes: int = 30
        channels: list[DeliveryChannel] = [DeliveryChannel.IN_APP]
        keyword: str | None = None


def build_service() -> MarketService:
    repo = SQLiteRepository(settings.database_path)
    notifiers = [ConsoleNotifier()]
    if settings.telegram_token and settings.telegram_chat_id:
        notifiers.append(TelegramNotifier(settings.telegram_token, settings.telegram_chat_id))
    if settings.webhook_url:
        notifiers.append(WebhookNotifier(settings.webhook_url))
    service = MarketService(repo, notifiers=notifiers)
    service.bootstrap()
    return service


service = None


def get_service() -> MarketService:
    global service
    if service is None:
        service = build_service()
    return service


def create_app() -> Any:
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Run: pip install -e .[api]")

    app = FastAPI(title="PulseCSE Pro API", version="3.0.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        svc = get_service()
        return {
            "ok": True,
            "app": settings.app_name,
            "mode": settings.market_provider,
            "last_tick_at": svc.repository.get_state("last_tick_at", "not yet run"),
        }

    @app.get("/api/dashboard")
    def dashboard(user_id: str = settings.default_user_id) -> dict[str, Any]:
        return get_service().dashboard(user_id)

    @app.post("/api/tick")
    def tick() -> dict[str, Any]:
        return get_service().tick().to_dict()

    @app.post("/api/simulate/{scenario}")
    def simulate(scenario: str) -> dict[str, Any]:
        return get_service().simulate(scenario).to_dict()

    @app.get("/api/stocks")
    def stocks() -> list[dict[str, Any]]:
        dashboard_data = get_service().dashboard(settings.default_user_id)
        return dashboard_data["stocks"]  # type: ignore[return-value]

    @app.get("/api/alerts")
    def alerts(user_id: str = settings.default_user_id) -> list[dict[str, Any]]:
        return [rule.to_dict() for rule in get_service().repository.list_rules(user_id)]

    @app.post("/api/alerts")
    def create_alert(payload: AlertIn, user_id: str = settings.default_user_id) -> dict[str, Any]:
        rule = AlertRule(
            id=new_id("rule"),
            user_id=user_id,
            symbol=payload.symbol.upper(),
            type=payload.type,
            target=payload.target,
            channels=payload.channels,
            note=payload.note,
            cooldown_minutes=payload.cooldown_minutes,
            keyword=payload.keyword,
        )
        get_service().repository.upsert_rules([rule])
        return rule.to_dict()

    @app.patch("/api/alerts/{rule_id}/{status}")
    def set_alert_status(rule_id: str, status: AlertStatus, user_id: str = settings.default_user_id) -> dict[str, Any]:
        repo = get_service().repository
        rules = repo.list_rules(user_id)
        target = next((rule for rule in rules if rule.id == rule_id), None)
        if not target:
            raise HTTPException(status_code=404, detail="alert not found")
        updated = replace(target, status=status)
        repo.upsert_rules([updated])
        return updated.to_dict()

    @app.get("/api/events")
    def events(user_id: str = settings.default_user_id, limit: int = 50) -> list[dict[str, Any]]:
        return [event.to_dict() for event in get_service().repository.list_events(user_id, limit)]

    @app.post("/api/watchlist/{symbol}")
    def add_watch(symbol: str, user_id: str = settings.default_user_id) -> dict[str, Any]:
        repo = get_service().repository
        repo.add_watch(user_id, symbol.upper())
        return {"ok": True, "watchlist": repo.watchlist(user_id)}

    @app.delete("/api/watchlist/{symbol}")
    def remove_watch(symbol: str, user_id: str = settings.default_user_id) -> dict[str, Any]:
        repo = get_service().repository
        repo.remove_watch(user_id, symbol.upper())
        return {"ok": True, "watchlist": repo.watchlist(user_id)}

    root = Path(__file__).resolve().parents[3]
    frontend = root
    if (frontend / "css").exists():
        app.mount("/css", StaticFiles(directory=frontend / "css"), name="css")
        app.mount("/js", StaticFiles(directory=frontend / "js"), name="js")
        app.mount("/assets", StaticFiles(directory=frontend / "assets"), name="assets")

        @app.get("/")
        def home() -> FileResponse:
            return FileResponse(frontend / "index.html")

        @app.get("/{page_name}.html")
        def page(page_name: str) -> FileResponse:
            path = frontend / f"{page_name}.html"
            if not path.exists():
                raise HTTPException(status_code=404, detail="page not found")
            return FileResponse(path)

    return app


app = create_app() if FastAPI is not None else None
