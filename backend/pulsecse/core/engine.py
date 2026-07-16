from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from hashlib import sha256
from typing import Iterable

from .models import AlertEvent, AlertRule, AlertStatus, AlertType, Disclosure, StockSnapshot, utc_now


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def cooldown_expired(rule: AlertRule, now: str) -> bool:
    if not rule.last_fired_at:
        return True
    last = parse_time(rule.last_fired_at)
    current = parse_time(now)
    if not last or not current:
        return True
    return (current - last).total_seconds() >= rule.cooldown_minutes * 60


def event_fingerprint(rule: AlertRule, reason: str, market_time: str, extra: str = "") -> str:
    raw = f"{rule.id}:{rule.symbol}:{rule.type.value}:{reason}:{market_time}:{extra}"
    return sha256(raw.encode("utf-8")).hexdigest()[:20]


def rearm_rule(rule: AlertRule, snapshot: StockSnapshot) -> AlertRule:
    if rule.armed or rule.status != AlertStatus.ACTIVE:
        return rule
    if rule.type == AlertType.PRICE_ABOVE and snapshot.price < rule.target:
        return replace(rule, armed=True)
    if rule.type == AlertType.PRICE_BELOW and snapshot.price > rule.target:
        return replace(rule, armed=True)
    if rule.type == AlertType.PERCENT_MOVE and abs(snapshot.change_percent) < rule.target * 0.75:
        return replace(rule, armed=True)
    if rule.type == AlertType.VOLUME_SPIKE and snapshot.volume_change_percent < rule.target * 0.75:
        return replace(rule, armed=True)
    if rule.type in {AlertType.DISCLOSURE, AlertType.NEWS_KEYWORD, AlertType.RISK_SCORE, AlertType.PORTFOLIO_DRAWDOWN}:
        return replace(rule, armed=True)
    return rule


def _severity(rule_type: AlertType, change_percent: float | None = None) -> str:
    if rule_type in {AlertType.PRICE_ABOVE, AlertType.PRICE_BELOW, AlertType.PERCENT_MOVE}:
        if change_percent is not None:
            abs_change = abs(change_percent)
            if abs_change >= 10.0:  # e.g., 10% or more change
                return "HIGH"
            elif abs_change >= 5.0:  # e.g., 5% or more change
                return "MEDIUM"
            else:
                # If an alert fires for these types, it implies a significant enough event
                # based on the rule's target. So, at least MEDIUM.
                return "MEDIUM"
        return "MEDIUM"  # Default if change_percent is not provided

    if rule_type == AlertType.VOLUME_SPIKE:
        # Volume spikes can vary in significance. Default to MEDIUM.
        # A more sophisticated system might use the magnitude of the spike.
        return "MEDIUM"

    if rule_type in {AlertType.DISCLOSURE, AlertType.NEWS_KEYWORD}:
        # These typically represent important information.
        return "MEDIUM"

    if rule_type == AlertType.RISK_SCORE:
        # A risk score alert usually indicates a significant change in risk profile.
        return "HIGH"

    if rule_type == AlertType.PORTFOLIO_DRAWDOWN:
        # Portfolio drawdown alerts are critical for portfolio management.
        return "CRITICAL"

    # Default for any other unhandled or less critical alert types
    return "LOW"