from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256
from typing import Iterable

from .models import AlertEvent, AlertRule, AlertStatus, AlertType, Disclosure, StockSnapshot, new_id, utc_now


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


def event_fingerprint(rule: AlertRule, reason: str, market_time: str) -> str:
    raw = f"{rule.id}:{rule.symbol}:{rule.type.value}:{reason}:{market_time}"
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
    if rule.type in {AlertType.DISCLOSURE, AlertType.NEWS_KEYWORD}:
        return replace(rule, armed=True)
    if rule.type == AlertType.RISK_SCORE:
        return replace(rule, armed=True)
    return rule


def _severity(rule_type: AlertType, change_percent: float | None = None) -> str:
    if rule_type in {AlertType.PRICE_BELOW, AlertType.RISK_SCORE}:
        return "critical"
    if change_percent is not None and abs(change_percent) >= 5:
        return "critical"
    if rule_type in {AlertType.PERCENT_MOVE, AlertType.VOLUME_SPIKE, AlertType.DISCLOSURE}:
        return "warning"
    return "info"


def evaluate_rule(
    rule: AlertRule,
    snapshot: StockSnapshot,
    disclosures: Iterable[Disclosure] = (),
    risk_score: int | None = None,
    now: str | None = None,
) -> tuple[AlertRule, AlertEvent | None]:
    now = now or utc_now()
    rule = rearm_rule(rule, snapshot)
    if rule.status != AlertStatus.ACTIVE or not rule.armed or not cooldown_expired(rule, now):
        return rule, None

    reason = ""
    message = ""
    metadata: dict[str, object] = {}

    if rule.type == AlertType.PRICE_ABOVE:
        if snapshot.previous_close < rule.target <= snapshot.price:
            reason = "crossed_above_threshold"
            message = f"{snapshot.symbol} crossed above LKR {rule.target:.2f}: LKR {snapshot.previous_close:.2f} -> LKR {snapshot.price:.2f}."

    elif rule.type == AlertType.PRICE_BELOW:
        if snapshot.previous_close > rule.target >= snapshot.price:
            reason = "crossed_below_threshold"
            message = f"{snapshot.symbol} crossed below LKR {rule.target:.2f}: LKR {snapshot.previous_close:.2f} -> LKR {snapshot.price:.2f}."

    elif rule.type == AlertType.PERCENT_MOVE:
        if abs(snapshot.change_percent) >= rule.target:
            reason = "daily_percent_move"
            message = f"{snapshot.symbol} moved {snapshot.change_percent:.2f}% today, crossing the {rule.target:.2f}% alert limit."

    elif rule.type == AlertType.VOLUME_SPIKE:
        if snapshot.volume_change_percent >= rule.target:
            reason = "volume_spike"
            message = f"{snapshot.symbol} volume is up {snapshot.volume_change_percent:.2f}%, above the {rule.target:.2f}% spike threshold."

    elif rule.type == AlertType.DISCLOSURE:
        disclosure = next((item for item in disclosures if item.symbol == rule.symbol), None)
        if disclosure:
            reason = "new_disclosure"
            message = f"{snapshot.symbol} disclosure: {disclosure.title}"
            metadata["disclosure_id"] = disclosure.id
            metadata["category"] = disclosure.category

    elif rule.type == AlertType.NEWS_KEYWORD:
        keyword = (rule.keyword or "").lower().strip()
        disclosure = next(
            (item for item in disclosures if item.symbol == rule.symbol and keyword and keyword in item.title.lower()),
            None,
        )
        if disclosure:
            reason = "keyword_matched"
            message = f"{snapshot.symbol} disclosure matched '{rule.keyword}': {disclosure.title}"
            metadata["disclosure_id"] = disclosure.id
            metadata["keyword"] = rule.keyword

    elif rule.type == AlertType.RISK_SCORE:
        if risk_score is not None and risk_score >= rule.target:
            reason = "risk_score_limit"
            message = f"{snapshot.symbol} risk score reached {risk_score}, above the {rule.target:.0f} limit."
            metadata["risk_score"] = risk_score

    if not reason:
        return rule, None

    event = AlertEvent(
        id=f"evt_{event_fingerprint(rule, reason, snapshot.market_time)}",
        rule_id=rule.id,
        user_id=rule.user_id,
        symbol=rule.symbol,
        type=rule.type,
        reason=reason,
        message=message,
        severity=_severity(rule.type, snapshot.change_percent),
        price=snapshot.price,
        change_percent=round(snapshot.change_percent, 2),
        metadata=metadata,
        created_at=now,
    )
    updated = replace(rule, armed=False, fire_count=rule.fire_count + 1, last_fired_at=now)
    return updated, event


def evaluate_rules(
    rules: Iterable[AlertRule],
    snapshots: dict[str, StockSnapshot],
    disclosures: Iterable[Disclosure] = (),
    risk_scores: dict[str, int] | None = None,
    now: str | None = None,
) -> tuple[list[AlertRule], list[AlertEvent]]:
    risk_scores = risk_scores or {}
    updated: list[AlertRule] = []
    events: list[AlertEvent] = []
    for rule in rules:
        snapshot = snapshots.get(rule.symbol)
        if not snapshot:
            updated.append(rule)
            continue
        next_rule, event = evaluate_rule(rule, snapshot, disclosures, risk_scores.get(rule.symbol), now)
        updated.append(next_rule)
        if event:
            events.append(event)
    return updated, events
