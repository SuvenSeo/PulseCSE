from __future__ import annotations

from pathlib import Path
from typing import Any
from dataclasses import replace

try:
    from fastapi import FastAPI, HTTPException, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover
    FastAPI = None  # type: ignore
    HTTPException = Exception  # type: ignore
    Response = object  # type: ignore
    JSONResponse = None  # type: ignore
    CORSMiddleware = None  # type: ignore
    FileResponse = None  # type: ignore
    StaticFiles = None  # type: ignore
    BaseModel = object  # type: ignore
    Field = lambda default=None, **_: default  # type: ignore

from pulsecse.config import settings
from pulsecse.core.models import AlertRule, AlertStatus, AlertType, DeliveryChannel, Holding, new_id
from pulsecse.notifications.console import ConsoleNotifier
from pulsecse.notifications.telegram import TelegramNotifier
from pulsecse.notifications.webhook import WebhookNotifier
from pulsecse.services.market_service import MarketService
from pulsecse.storage.factory import build_repository


if BaseModel is object:
    class AlertIn:  # type: ignore
        pass
    class HoldingIn:  # type: ignore
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

    class HoldingIn(BaseModel):
        symbol: str = Field(..., min_length=3)
        quantity: float = Field(..., ge=0)
        average_cost: float = Field(..., ge=0)


def build_service() -> MarketService:
    repo = build_repository()
    notifiers = [ConsoleNotifier()]
    if settings.telegram_token and settings.telegram_chat_id:
        notifiers.append(TelegramNotifier())
    if settings.webhook_url:
        notifiers.append(WebhookNotifier())
    return MarketService(repo, notifiers)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/alerts/")
def read_alerts() -> list[AlertRule]:
    service = build_service()
    return service.get_alerts()


@app.post("/alerts/")
def create_alert(alert: AlertIn) -> AlertRule:
    service = build_service()
    alert_rule = AlertRule(
        id=new_id(),
        symbol=alert.symbol,
        type=alert.type,
        target=alert.target,
        note=alert.note,
        cooldown_minutes=alert.cooldown_minutes,
        channels=alert.channels,
        keyword=alert.keyword,
    )
    service.create_alert(alert_rule)
    return alert_rule


@app.get("/holdings/")
def read_holdings() -> list[Holding]:
    service = build_service()
    return service.get_holdings()


@app.post("/holdings/")
def create_holding(holding: HoldingIn) -> Holding:
    service = build_service()
    holding_obj = Holding(
        id=new_id(),
        symbol=holding.symbol,
        quantity=holding.quantity,
        average_cost=holding.average_cost,
    )
    service.create_holding(holding_obj)
    return holding_obj


@app.get("/metrics")
def read_metrics() -> dict[str, Any]:
    service = build_service()
    return service.get_metrics()


@app.get("/metrics.prom")
def read_metrics_prom() -> Response:
    service = build_service()
    metrics = service.get_metrics()
    prom_metrics = ""
    for key, value in metrics.items():
        prom_metrics += f"{key} {value}\n"
    return Response(content=prom_metrics, media_type="text/plain")


@app.get("/api/dashboard")
def read_dashboard() -> dict[str, Any]:
    service = build_service()
    return service.get_dashboard()


@app.get("/api/alerts")
def read_api_alerts() -> list[AlertRule]:
    service = build_service()
    return service.get_alerts()


@app.post("/api/alerts")
def create_api_alert(alert: AlertIn) -> AlertRule:
    service = build_service()
    alert_rule = AlertRule(
        id=new_id(),
        symbol=alert.symbol,
        type=alert.type,
        target=alert.target,
        note=alert.note,
        cooldown_minutes=alert.cooldown_minutes,
        channels=alert.channels,
        keyword=alert.keyword,
    )
    service.create_alert(alert_rule)
    return alert_rule


@app.get("/api/portfolio")
def read_api_portfolio() -> list[Holding]:
    service = build_service()
    return service.get_holdings()


@app.post("/api/portfolio")
def create_api_portfolio(holding: HoldingIn) -> Holding:
    service = build_service()
    holding_obj = Holding(
        id=new_id(),
        symbol=holding.symbol,
        quantity=holding.quantity,
        average_cost=holding.average_cost,
    )
    service.create_holding(holding_obj)
    return holding_obj


@app.get("/api/watchlist")
def read_api_watchlist() -> list[str]:
    service = build_service()
    return service.get_watchlist()


@app.get("/api/history")
def read_api_history() -> list[dict[str, Any]]:
    service = build_service()
    return service.get_history()


@app.get("/api/live")
def read_api_live() -> dict[str, Any]:
    service = build_service()
    return service.get_live()


@app.get("/api/simulator")
def read_api_simulator() -> dict[str, Any]:
    service = build_service()
    return service.get_simulator()


@app.get("/api/{path:path}")
def read_api(path: str) -> JSONResponse:
    return JSONResponse(content={"error": "Not Found"}, status_code=404)