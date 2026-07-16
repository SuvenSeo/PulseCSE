from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterable, Protocol

from pulsecse.adapters import MockMarketAdapter
from pulsecse.adapters.cse_live import CSELiveAdapter
from pulsecse.config import settings
from pulsecse.core.analytics import market_breadth, risk_label, risk_score, sector_heatmap, suggested_alerts, top_movers
from pulsecse.core.engine import evaluate_rules
from pulsecse.core.models import AlertEvent, AlertRule, AlertType, DeliveryChannel, Disclosure, Holding, Stock, StockSnapshot, new_id, utc_now
from pulsecse.market_hours import MarketWindow, is_closed_from_live_status
from pulsecse.notifications.base import Notifier
from pulsecse.notifications.console import ConsoleNotifier
from pulsecse.observability import log_event, timer


class Repository(Protocol):
    database_type: str
    def upsert_stocks(self, stocks: Iterable[Stock]) -> None: ...
    def list_stocks(self) -> list[Stock]: ...
    def insert_snapshots(self, snapshots: Iterable[StockSnapshot]) -> None: ...
    def latest_snapshots(self) -> dict[str, StockSnapshot]: ...
    def price_history(self, symbol: str, limit: int = 40) -> list[float]: ...
    def insert_disclosures(self, disclosures: Iterable[Disclosure]) -> None: ...
    def recent_disclosures(self, limit: int = 20) -> list[Disclosure]: ...
    def add_watch(self, user_id: str, symbol: str) -> None: ...
    def watchlist(self, user_id: str) -> list[str]: ...
    def upsert_rules(self, rules: Iterable[AlertRule]) -> None: ...
    def list_rules(self, user_id: str | None = None, active_only: bool = False) -> list[AlertRule]: ...
    def insert_events(self, events: Iterable[AlertEvent]) -> None: ...
    def list_events(self, user_id: str | None = None, limit: int = 50) -> list[AlertEvent]: ...
    def log_delivery(self, event_id: str, channel: str, ok: bool, detail: str, latency_ms: float | None = None) -> None: ...
    def set_state(self, key: str, value: str) -> None: ...


class MarketService:
    def __init__(self, repository: Repository, notifier: Notifier):
        self.repository = repository
        self.notifier = notifier
        self.adapter = CSELiveAdapter() if settings.USE_LIVE_DATA else MockMarketAdapter()

    def update_stocks(self) -> None:
        stocks = self.adapter.list_stocks()
        self.repository.upsert_stocks(stocks)

    def update_snapshots(self) -> None:
        with timer("update_snapshots"):
            latest_snapshots = self.repository.latest_snapshots()
            new_snapshots = self.adapter.get_new_snapshots(latest_snapshots)
            self.repository.insert_snapshots(new_snapshots)

    def update_disclosures(self) -> None:
        disclosures = self.adapter.list_disclosures()
        self.repository.insert_disclosures(disclosures)

    def evaluate_rules(self) -> None:
        rules = self.repository.list_rules()
        events = evaluate_rules(rules)
        self.repository.insert_events(events)

    def send_notifications(self) -> None:
        events = self.repository.list_events()
        for event in events:
            self.notifier.send(event)

    def run(self) -> None:
        if is_closed_from_live_status(self.adapter.get_live_status()):
            log_event("Market is closed, skipping update")
            return

        self.update_stocks()
        self.update_snapshots()
        self.update_disclosures()
        self.evaluate_rules()
        self.send_notifications()

    def add_watch(self, user_id: str, symbol: str) -> None:
        self.repository.add_watch(user_id, symbol)

    def get_watchlist(self, user_id: str) -> list[str]:
        return self.repository.watchlist(user_id)

    def upsert_rules(self, rules: Iterable[AlertRule]) -> None:
        self.repository.upsert_rules(rules)

    def get_rules(self, user_id: str | None = None, active_only: bool = False) -> list[AlertRule]:
        return self.repository.list_rules(user_id, active_only)

    def get_events(self, user_id: str | None = None, limit: int = 50) -> list[AlertEvent]:
        return self.repository.list_events(user_id, limit)

    def log_delivery(self, event_id: str, channel: str, ok: bool, detail: str, latency_ms: float | None = None) -> None:
        self.repository.log_delivery(event_id, channel, ok, detail, latency_ms)

    def set_state(self, key: str, value: str) -> None:
        self.repository.set_state(key, value)


def main() -> None:
    repository = Repository()  # Initialize repository
    notifier = ConsoleNotifier()  # Initialize notifier
    service = MarketService(repository, notifier)
    service.run()


if __name__ == "__main__":
    main()