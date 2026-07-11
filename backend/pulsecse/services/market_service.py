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
from pulsecse.market_hours import MarketWindow
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
    def get_state(self, key: str, default: str = "") -> str: ...
    def upsert_holding(self, holding: Holding) -> None: ...
    def portfolio_summary(self, user_id: str): ...
    def delivery_stats(self) -> dict[str, object]: ...


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
        repository: Repository,
        adapter: object | None = None,
        notifiers: Iterable[Notifier] | None = None,
    ) -> None:
        self.repository = repository
        self.adapter = adapter or self._build_adapter()
        self.notifiers = list(notifiers or [ConsoleNotifier()])
        self.market_window = MarketWindow.from_settings()

    def _build_adapter(self) -> object:
        if settings.market_provider == "cse-live":
            return CSELiveAdapter(settings.cse_base_url)
        return MockMarketAdapter()

    def bootstrap(self) -> None:
        self.repository.upsert_stocks(self.adapter.list_stocks())  # type: ignore[attr-defined]
        if not self.repository.latest_snapshots():
            self.repository.insert_snapshots(self.adapter.latest_snapshots())  # type: ignore[attr-defined]
        for symbol in ["JKH.N0000", "COMB.N0000", "HNB.N0000", "DIAL.N0000"]:
            self.repository.add_watch(settings.default_user_id, symbol)
        self._seed_portfolio(settings.default_user_id)
        if not self.repository.list_rules(settings.default_user_id):
            self.repository.upsert_rules(self._default_rules())

    def _seed_portfolio(self, user_id: str) -> None:
        summary = self.repository.portfolio_summary(user_id)
        if summary.positions:
            return
        for holding in [
            Holding(user_id, "JKH.N0000", 120, 185.00),
            Holding(user_id, "COMB.N0000", 200, 116.50),
            Holding(user_id, "DIAL.N0000", 1600, 11.90),
        ]:
            self.repository.upsert_holding(holding)

    def _default_rules(self) -> list[AlertRule]:
        return [
            AlertRule(new_id("rule"), settings.default_user_id, "JKH.N0000", AlertType.PRICE_ABOVE, 198, channels=[DeliveryChannel.IN_APP], note="Momentum breakout"),
            AlertRule(new_id("rule"), settings.default_user_id, "HNB.N0000", AlertType.PRICE_BELOW, 230, channels=[DeliveryChannel.IN_APP], note="Support break"),
            AlertRule(new_id("rule"), settings.default_user_id, "COMB.N0000", AlertType.DISCLOSURE, 0, channels=[DeliveryChannel.IN_APP], note="Corporate updates"),
            AlertRule(new_id("rule"), settings.default_user_id, "DIAL.N0000", AlertType.VOLUME_SPIKE, 70, channels=[DeliveryChannel.IN_APP], note="Unusual activity"),
            AlertRule(new_id("rule"), settings.default_user_id, "JKH.N0000", AlertType.RISK_SCORE, 72, channels=[DeliveryChannel.IN_APP], note="Risk guardrail"),
        ]

    def tick(self, force: bool = True) -> TickResult:
        if not force and not self.market_window.is_open():
            self.repository.set_state("last_skip_reason", "market_closed")
            log_event("tick_skipped", reason="market_closed", market=self.market_window.status())
            return TickResult([], [], [])
        with timer("market_tick"):
            snapshots = self.adapter.latest_snapshots()  # type: ignore[attr-defined]
            disclosures = self.adapter.latest_disclosures()  # type: ignore[attr-defined]
            return self._ingest_and_evaluate(snapshots, disclosures)

    def simulate(self, scenario: str) -> TickResult:
        snapshots, disclosures = self.adapter.apply_scenario(scenario)  # type: ignore[attr-defined]
        return self._ingest_and_evaluate(snapshots, disclosures)

    def _ingest_and_evaluate(self, snapshots: list[StockSnapshot], disclosures: list[Disclosure]) -> TickResult:
        now = utc_now()
        self.repository.insert_snapshots(snapshots)
        self.repository.insert_disclosures(disclosures)
        latest = self.repository.latest_snapshots()
        risk_scores = {symbol: risk_score(self.repository.price_history(symbol), snapshot) for symbol, snapshot in latest.items()}
        portfolio = self.repository.portfolio_summary(settings.default_user_id)
        portfolio_drawdowns = {settings.default_user_id: portfolio.unrealized_pnl_percent}
        rules = self.repository.list_rules(active_only=True)
        updated_rules, events = evaluate_rules(rules, latest, disclosures, risk_scores, portfolio_drawdowns, now)
        self.repository.upsert_rules(updated_rules)
        self.repository.insert_events(events)
        for event in events:
            for notifier in self.notifiers:
                started = perf_counter()
                result = notifier.send(event)
                latency_ms = round((perf_counter() - started) * 1000, 2)
                self.repository.log_delivery(event.id, result.channel, result.ok, result.detail, latency_ms)
                log_event("alert_delivery", event_id=event.id, channel=result.channel, ok=result.ok, latency_ms=latency_ms)
        self.repository.set_state("last_tick_at", now)
        self.repository.set_state("last_event_count", str(len(events)))
        self.repository.set_state("last_snapshot_count", str(len(snapshots)))
        return TickResult(snapshots=snapshots, disclosures=disclosures, events=events)

    def health(self) -> dict[str, object]:
        last_tick = self.repository.get_state("last_tick_at", "")
        market = self.market_window.status()
        status = "ok" if last_tick or not market["is_open"] else "degraded"
        return {
            "ok": status == "ok",
            "status": status,
            "app": settings.app_name,
            "mode": settings.market_provider,
            "database": self.repository.database_type,
            "market": market,
            "last_tick_at": last_tick or "not yet run",
            "last_event_count": int(self.repository.get_state("last_event_count", "0") or 0),
            "delivery": self.repository.delivery_stats(),
        }

    def metrics(self) -> dict[str, object]:
        latest = self.repository.latest_snapshots()
        return {
            "stocks_tracked": len(self.repository.list_stocks()),
            "latest_snapshots": len(latest),
            "active_alerts": len(self.repository.list_rules(active_only=True)),
            "events_total": len(self.repository.list_events(limit=100000)),
            "delivery": self.repository.delivery_stats(),
        }

    def dashboard(self, user_id: str = "demo") -> dict[str, object]:
        stocks = self.repository.list_stocks()
        snapshots_map = self.repository.latest_snapshots()
        snapshots = list(snapshots_map.values())
        scores = {symbol: risk_score(self.repository.price_history(symbol), snapshot) for symbol, snapshot in snapshots_map.items()}
        movers = top_movers(snapshots)
        watchlist = self.repository.watchlist(user_id)
        portfolio = self.repository.portfolio_summary(user_id)
        return {
            "status": self.health(),
            "breadth": market_breadth(snapshots),
            "top_movers": {key: [item.to_dict() for item in value] for key, value in movers.items()},
            "sector_heatmap": sector_heatmap(stocks, snapshots),
            "watchlist": watchlist,
            "portfolio": portfolio.to_dict(),
            "stocks": [
                stock.to_dict()
                | snapshots_map.get(stock.symbol, StockSnapshot(stock.symbol, 0, 0, 0, 0, 0, 0)).to_dict()
                | {
                    "risk_score": scores.get(stock.symbol, 0),
                    "risk_label": risk_label(scores.get(stock.symbol, 0)),
                    "suggestions": suggested_alerts(snapshots_map[stock.symbol], scores.get(stock.symbol, 0)) if stock.symbol in snapshots_map else [],
                }
                for stock in stocks
            ],
            "alerts": [rule.to_dict() for rule in self.repository.list_rules(user_id)],
            "events": [event.to_dict() for event in self.repository.list_events(user_id, limit=20)],
            "disclosures": [item.to_dict() for item in self.repository.recent_disclosures(20)],
        }
