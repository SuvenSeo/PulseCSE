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
                alert_type = AlertType(parts[2])
                target = float(parts[3])
                keyword = " ".join(parts[4:]) if alert_type == AlertType.NEWS_KEYWORD and len(parts) > 4 else None
                rule = AlertRule(
                    id=new_id("rule"), user_id=user_id, symbol=symbol, type=alert_type, target=target,
                    channels=[DeliveryChannel.IN_APP, DeliveryChannel.TELEGRAM], keyword=keyword, note="Created from command router",
                )
                self.repository.upsert_rules([rule])
                return CommandResult(True, f"Created {alert_type.value} alert {rule.id} for {symbol}.")
            if command in {"/alerts", "/myalerts"}:
                rules = [rule for rule in self.repository.list_rules(user_id) if rule.status == AlertStatus.ACTIVE]
                if not rules:
                    return CommandResult(True, "No active alerts.")
                lines = [f"{rule.id}: {rule.symbol} {rule.type.value} {rule.target:g} ({'armed' if rule.armed else 'cooling'})" for rule in rules]
                return CommandResult(True, "Active alerts:\n" + "\n".join(lines))
            if command == "/cancel" and len(parts) >= 2:
                rule_id = parts[1]
                rules = self.repository.list_rules(user_id)
                target = next((rule for rule in rules if rule.id == rule_id), None)
                if not target:
                    return CommandResult(False, "Alert not found.")
                self.repository.upsert_rules([replace(target, status=AlertStatus.CANCELLED)])
                return CommandResult(True, f"Cancelled {rule_id}.")
            if command == "/holding" and len(parts) >= 4:
                symbol = parts[1].upper()
                quantity = float(parts[2])
                average_cost = float(parts[3])
                self.repository.upsert_holding(Holding(user_id, symbol, quantity, average_cost))
                return CommandResult(True, f"Saved holding: {quantity:g} {symbol} @ LKR {average_cost:g}.")
            if command == "/portfolio":
                portfolio = self.repository.portfolio_summary(user_id)
                lines = [f"Portfolio value LKR {portfolio.total_value:,.2f} | P&L {portfolio.unrealized_pnl_percent:.2f}%"]
                lines.extend(f"{p.symbol}: {p.quantity:g} shares, P&L {p.unrealized_pnl_percent:.2f}%" for p in portfolio.positions[:8])
                return CommandResult(True, "\n".join(lines))
            if command == "/events":
                events = self.repository.list_events(user_id, limit=5)
                if not events:
                    return CommandResult(True, "No alert events yet.")
                lines = [f"{event.created_at} {event.symbol}: {event.message}" for event in events]
                return CommandResult(True, "Latest events:\n" + "\n".join(lines))
        except ValueError as exc:
            return CommandResult(False, f"Invalid command value: {exc}")
        return CommandResult(False, "Unknown or incomplete command. Send /help.")
