from __future__ import annotations

from dataclasses import dataclass

from pulsecse.core.models import AlertRule, AlertStatus, AlertType, DeliveryChannel, new_id
from pulsecse.storage.sqlite import SQLiteRepository


@dataclass(slots=True)
class CommandResult:
    ok: bool
    text: str


HELP_TEXT = """PulseCSE commands:\n/watch SYMBOL - add to watchlist\n/unwatch SYMBOL - remove from watchlist\n/watchlist - show watchlist\n/alert SYMBOL TYPE TARGET - create alert\n/alerts - list active alerts\n/cancel ALERT_ID - cancel alert\n/events - show latest events\n/help - show help\n\nTypes: price_above, price_below, percent_move, disclosure, volume_spike, news_keyword, risk_score"""


class CommandRouter:
    """Transport-neutral command router.

    Telegram, Discord, Slack, or CLI handlers can all pass text into this router.
    This gives PulseCSE a bot workflow without tying the core project to one SDK.
    """

    def __init__(self, repository: SQLiteRepository) -> None:
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
            if command == "/watchlist":
                items = self.repository.watchlist(user_id)
                return CommandResult(True, "Watchlist: " + (", ".join(items) if items else "empty"))
            if command == "/alert" and len(parts) >= 4:
                symbol = parts[1].upper()
                alert_type = AlertType(parts[2])
                target = float(parts[3])
                keyword = " ".join(parts[4:]) if alert_type == AlertType.NEWS_KEYWORD and len(parts) > 4 else None
                rule = AlertRule(
                    id=new_id("rule"),
                    user_id=user_id,
                    symbol=symbol,
                    type=alert_type,
                    target=target,
                    channels=[DeliveryChannel.IN_APP],
                    keyword=keyword,
                    note="Created from command router",
                )
                self.repository.upsert_rules([rule])
                return CommandResult(True, f"Created {alert_type.value} alert {rule.id} for {symbol}.")
            if command == "/alerts":
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
                target.status = AlertStatus.CANCELLED
                self.repository.upsert_rules([target])
                return CommandResult(True, f"Cancelled {rule_id}.")
            if command == "/events":
                events = self.repository.list_events(user_id, limit=5)
                if not events:
                    return CommandResult(True, "No alert events yet.")
                lines = [f"{event.created_at} {event.symbol}: {event.message}" for event in events]
                return CommandResult(True, "Latest events:\n" + "\n".join(lines))
        except ValueError as exc:
            return CommandResult(False, f"Invalid command value: {exc}")
        return CommandResult(False, "Unknown or incomplete command. Send /help.")
