from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AlertType(str, Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENT_MOVE = "percent_move"
    DISCLOSURE = "disclosure"
    VOLUME_SPIKE = "volume_spike"
    NEWS_KEYWORD = "news_keyword"
    RISK_SCORE = "risk_score"
    PORTFOLIO_DRAWDOWN = "portfolio_drawdown"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class DeliveryChannel(str, Enum):
    IN_APP = "in_app"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"
    EMAIL = "email"


@dataclass(slots=True)
class Stock:
    symbol: str
    name: str
    sector: str
    board: str = "Main Board"
    isin: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class StockSnapshot:
    symbol: str
    price: float
    previous_close: float
    volume: int
    previous_volume: int
    high: float
    low: float
    market_time: str = field(default_factory=utc_now)
    source: str = "mock"

    @property
    def change_percent(self) -> float:
        if self.previous_close == 0:
            return 0.0
        return ((self.price - self.previous_close) / self.previous_close) * 100

    @property
    def volume_change_percent(self) -> float:
        if self.previous_volume == 0:
            return 0.0
        return ((self.volume - self.previous_volume) / self.previous_volume) * 100

    def to_dict(self) -> dict[str, Any]:
        item = asdict(self)
        item["change_percent"] = round(self.change_percent, 2)
        item["volume_change_percent"] = round(self.volume_change_percent, 2)
        return item


@dataclass(slots=True)
class Alert:
    id: str = field(default_factory=lambda: new_id("alert"))
    type: AlertType
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PriceAlert(Alert):
    stock: Stock
    target_price: float

    def to_dict(self) -> dict[str, Any]:
        item = super().to_dict()
        item["stock"] = self.stock.to_dict()
        item["target_price"] = self.target_price
        return item


@dataclass(slots=True)
class PercentMoveAlert(Alert):
    stock: Stock
    percent_move: float

    def to_dict(self) -> dict[str, Any]:
        item = super().to_dict()
        item["stock"] = self.stock.to_dict()
        item["percent_move"] = self.percent_move
        return item


@dataclass(slots=True)
class DisclosureAlert(Alert):
    stock: Stock
    keyword: str

    def to_dict(self) -> dict[str, Any]:
        item = super().to_dict()
        item["stock"] = self.stock.to_dict()
        item["keyword"] = self.keyword
        return item


@dataclass(slots=True)
class VolumeSpikeAlert(Alert):
    stock: Stock
    volume_threshold: int

    def to_dict(self) -> dict[str, Any]:
        item = super().to_dict()
        item["stock"] = self.stock.to_dict()
        item["volume_threshold"] = self.volume_threshold
        return item


@dataclass(slots=True)
class NewsKeywordAlert(Alert):
    stock: Stock
    keyword: str

    def to_dict(self) -> dict[str, Any]:
        item = super().to_dict()
        item["stock"] = self.stock.to_dict()
        item["keyword"] = self.keyword
        return item


@dataclass(slots=True)
class RiskScoreAlert(Alert):
    stock: Stock
    risk_score_threshold: float

    def to_dict(self) -> dict[str, Any]:
        item = super().to_dict()
        item["stock"] = self.stock.to_dict()
        item["risk_score_threshold"] = self.risk_score_threshold
        return item


@dataclass(slots=True)
class PortfolioDrawdownAlert(Alert):
    portfolio: list[Stock]
    drawdown_threshold: float

    def to_dict(self) -> dict[str, Any]:
        item = super().to_dict()
        item["portfolio"] = [stock.to_dict() for stock in self.portfolio]
        item["drawdown_threshold"] = self.drawdown_threshold
        return item


@dataclass(slots=True)
class Notification:
    id: str = field(default_factory=lambda: new_id("notification"))
    alert: Alert
    delivery_channel: DeliveryChannel
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        item = asdict(self)
        item["alert"] = self.alert.to_dict()
        return item