from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from pulsecse.adapters import MockMarketAdapter
from pulsecse.core.analytics import market_breadth, risk_label, risk_score, sector_heatmap, suggested_alerts, top_movers
from pulsecse.core.engine import evaluate_rules
from pulsecse.core.models import AlertEvent, AlertRule, Disclosure, StockSnapshot, utc_now
from pulsecse.notifications.base import Notifier
from pulsecse.notifications.console import ConsoleNotifier
from pulsecse.storage.sqlite import SQLiteRepository


@dataclass(slots=True)
class TickResult:
    snapshots: list[StockSnapshot]
    disclosures: list[Disclosure]
    events: list[AlertEvent]

    def to_dict(self) -> dict[str, object]:
        return {
            "snapshots": [item.to_dict() for item in self.snapshots],
            "disclosures": [item.to_dict() for item in self.disclosures],
            "events": [item.to_dict() for item in self.events],
        }


class MarketService:
    def __init__(
        self,
        repository: SQLiteRepository,
        adapter: MockMarketAdapter | None = None,
        notifiers: Iterable[Notifier] | None = None,
    ) -> None:
        self.repository = repository
        self.adapter = adapter or MockMarketAdapter()
        self.notifiers = list(notifiers or [ConsoleNotifier()])

    def bootstrap(self) -> None:
        self.repository.upsert_stocks(self.adapter.list_stocks())
        if not self.repository.latest_snapshots():
            snapshots = self.adapter.latest_snapshots()
            self.repository.insert_snapshots(snapshots)
        for symbol in ["JKH.N0000", "COMB.N0000", "HNB.N0000", "DIAL.N0000"]:
            self.repository.add_watch("demo", symbol)
        if not self.repository.list_rules("demo"):
            seed_rules = self._default_rules()
            self.repository.upsert_rules(seed_rules)

    def _default_rules(self) -> list[AlertRule]:
        from pulsecse.core.models import AlertType, DeliveryChannel, new_id

        return [
            AlertRule(new_id("rule"), "demo", "JKH.N0000", AlertType.PRICE_ABOVE, 198, channels=[DeliveryChannel.IN_APP], note="Momentum breakout"),
            AlertRule(new_id("rule"), "demo", "HNB.N0000", AlertType.PRICE_BELOW, 230, channels=[DeliveryChannel.IN_APP], note="Support break"),
            AlertRule(new_id("rule"), "demo", "COMB.N0000", AlertType.DISCLOSURE, 0, channels=[DeliveryChannel.IN_APP], note="Corporate updates"),
            AlertRule(new_id("rule"), "demo", "DIAL.N0000", AlertType.VOLUME_SPIKE, 70, channels=[DeliveryChannel.IN_APP], note="Unusual activity"),
        ]

    def tick(self) -> TickResult:
        snapshots = self.adapter.latest_snapshots()
        disclosures = self.adapter.latest_disclosures()
        return self._ingest_and_evaluate(snapshots, disclosures)

    def simulate(self, scenario: str) -> TickResult:
        snapshots, disclosures = self.adapter.apply_scenario(scenario)
        return self._ingest_and_evaluate(snapshots, disclosures)

    def _ingest_and_evaluate(self, snapshots: list[StockSnapshot], disclosures: list[Disclosure]) -> TickResult:
        now = utc_now()
        self.repository.insert_snapshots(snapshots)
        self.repository.insert_disclosures(disclosures)
        latest = self.repository.latest_snapshots()
        risk_scores = {symbol: risk_score(self.repository.price_history(symbol), snapshot) for symbol, snapshot in latest.items()}
        rules = self.repository.list_rules(active_only=True)
        updated_rules, events = evaluate_rules(rules, latest, disclosures, risk_scores, now)
        self.repository.upsert_rules(updated_rules)
        self.repository.insert_events(events)
        for event in events:
            for notifier in self.notifiers:
                result = notifier.send(event)
                self.repository.log_delivery(event.id, result.channel, result.ok, result.detail)
        self.repository.set_state("last_tick_at", now)
        self.repository.set_state("last_event_count", str(len(events)))
        return TickResult(snapshots=snapshots, disclosures=disclosures, events=events)

    def dashboard(self, user_id: str = "demo") -> dict[str, object]:
        stocks = self.repository.list_stocks()
        snapshots_map = self.repository.latest_snapshots()
        snapshots = list(snapshots_map.values())
        scores = {symbol: risk_score(self.repository.price_history(symbol), snapshot) for symbol, snapshot in snapshots_map.items()}
        movers = top_movers(snapshots)
        watchlist = self.repository.watchlist(user_id)
        return {
            "status": {
                "mode": "mock-live",
                "last_tick_at": self.repository.get_state("last_tick_at", "not yet run"),
                "last_event_count": int(self.repository.get_state("last_event_count", "0") or 0),
            },
            "breadth": market_breadth(snapshots),
            "top_movers": {key: [item.to_dict() for item in value] for key, value in movers.items()},
            "sector_heatmap": sector_heatmap(stocks, snapshots),
            "watchlist": watchlist,
            "stocks": [stock.to_dict() | snapshots_map.get(stock.symbol, StockSnapshot(stock.symbol, 0, 0, 0, 0, 0, 0)).to_dict() | {"risk_score": scores.get(stock.symbol, 0), "risk_label": risk_label(scores.get(stock.symbol, 0)), "suggestions": suggested_alerts(snapshots_map[stock.symbol], scores.get(stock.symbol, 0)) if stock.symbol in snapshots_map else []} for stock in stocks],
            "alerts": [rule.to_dict() for rule in self.repository.list_rules(user_id)],
            "events": [event.to_dict() for event in self.repository.list_events(user_id, limit=20)],
            "disclosures": [item.to_dict() for item in self.repository.recent_disclosures(20)],
        }
