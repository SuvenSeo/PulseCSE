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
class Disclosure:
    id: str
    symbol: str
    title: str
    category: str
    published_at: str
    url: str | None = None
    source: str = "mock"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AlertRule:
    id: str
    user_id: str
    symbol: str
    type: AlertType
    target: float = 0.0
    status: AlertStatus = AlertStatus.ACTIVE
    channels: list[DeliveryChannel] = field(default_factory=lambda: [DeliveryChannel.IN_APP])
    note: str = ""
    armed: bool = True
    fire_count: int = 0
    cooldown_minutes: int = 30
    last_fired_at: str | None = None
    keyword: str | None = None
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        item = asdict(self)
        item["type"] = self.type.value
        item["status"] = self.status.value
        item["channels"] = [channel.value for channel in self.channels]
        return item


@dataclass(slots=True)
class AlertEvent:
    id: str
    rule_id: str
    user_id: str
    symbol: str
    type: AlertType
    reason: str
    message: str
    severity: Literal["info", "warning", "critical"] = "info"
    price: float | None = None
    change_percent: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        item = asdict(self)
        item["type"] = self.type.value
        return item
