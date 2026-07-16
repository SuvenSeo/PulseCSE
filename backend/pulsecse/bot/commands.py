from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from pulsecse.core.models import AlertRule, AlertStatus, AlertType, DeliveryChannel, Holding, new_id


@dataclass(slots=True)
class CommandResult:
    ok: bool
    text: str


HELP_TEXT = """PulseCSE commands:
/watch SYMBOL - add to watchlist
/unwatch SYMBOL - remove from watchlist
/watchlist or /mywatchlist - show watchlist
/alert SYMBOL TYPE TARGET [keyword] - create alert
/alerts or /myalerts - list active alerts
/cancel ALERT_ID - cancel alert
/portfolio - show portfolio P&L
/holding SYMBOL QTY AVG_COST - set holding
/events - show latest events
/help - show help

Types: price_above, price_below, percent_move, disclosure, volume_spike, news_keyword, risk_score, portfolio_drawdown"""


class CommandRouter:
    """Transport-neutral command router for Telegram, CLI, Slack, or web chat."""

    def __init__(self, repository: Any) -> None:
        self.repository = repository

    def handle(self, text: str, user_id: str = "demo") -> CommandResult:
        parts = text.strip().split()
        if not parts:
            return CommandResult(False, "Send /help to see commands.")
        command = parts[0].lower()
        try:
            if command == "/help":
                return CommandResult(True, HELP_TEXT)
            if command == "/watch" and len(parts) >= 2:
                symbol = parts[1].upper()
                self.repository.add_watch(user_id, symbol)
                return CommandResult(True, f"Watching {symbol}.")
            if command == "/unwatch" and len(parts) >= 2:
                symbol = parts[1].upper()
                self.repository.remove_watch(user_id, symbol)
                return CommandResult(True, f"Removed {symbol} from watchlist.")
            if command in {"/watchlist", "/mywatchlist"}:
                items = self.repository.watchlist(user_id)
                return CommandResult(True, "Watchlist: " + (", ".join(items) if items else "empty"))
            if command == "/alert" and len(parts) >= 4:
                symbol = parts[1].upper()
                alert_type = parts[2]
                target = parts[3]
                keyword = " ".join(parts[4:]) if len(parts) > 4 else None
                alert_id = new_id()
                self.repository.create_alert(user_id, alert_id, symbol, alert_type, target, keyword)
                return CommandResult(True, f"Alert created for {symbol} with type {alert_type} and target {target}")
            if command in {"/alerts", "/myalerts"}:
                alerts = self.repository.alerts(user_id)
                alert_texts = [f"Alert {alert.id} for {alert.symbol} with type {alert.type} and target {alert.target}" for alert in alerts]
                return CommandResult(True, "\n".join(alert_texts) if alert_texts else "No active alerts")
            if command == "/cancel" and len(parts) >= 2:
                alert_id = parts[1]
                self.repository.cancel_alert(user_id, alert_id)
                return CommandResult(True, f"Alert {alert_id} cancelled")
            if command == "/portfolio":
                portfolio = self.repository.portfolio(user_id)
                return CommandResult(True, "Portfolio P&L: " + str(portfolio))
            if command == "/holding" and len(parts) >= 4:
                symbol = parts[1].upper()
                qty = int(parts[2])
                avg_cost = float(parts[3])
                self.repository.set_holding(user_id, symbol, qty, avg_cost)
                return CommandResult(True, f"Holding {symbol} set to {qty} with average cost {avg_cost}")
            if command == "/events":
                events = self.repository.events(user_id)
                event_texts = [f"Event {event.id} for {event.symbol} with type {event.type}" for event in events]
                return CommandResult(True, "\n".join(event_texts) if event_texts else "No events")
            return CommandResult(False, "Unknown command")
        except Exception as e:
            return CommandResult(False, str(e))