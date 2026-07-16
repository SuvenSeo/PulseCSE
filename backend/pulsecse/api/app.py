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


app = FastAPI(
    title="PulseCSE API",
    description="API for PulseCSE",
    version="1.0.0",
    contact={
        "name": "SuvenSeo",
        "url": "https://suvenseo.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/alerts/")
async def read_alerts():
    service = build_service()
    return service.get_alerts()

@app.post("/alerts/")
async def create_alert(alert: AlertIn):
    service = build_service()
    return service.create_alert(alert)

@app.get("/holdings/")
async def read_holdings():
    service = build_service()
    return service.get_holdings()

@app.post("/holdings/")
async def create_holding(holding: HoldingIn):
    service = build_service()
    return service.create_holding(holding)

@app.get("/healthcheck/")
async def healthcheck():
    return JSONResponse(content={"status": "ok"}, media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)