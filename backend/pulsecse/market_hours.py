from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from random import randint
from zoneinfo import ZoneInfo

from pulsecse.config import settings


@dataclass(slots=True)
class MarketWindow:
    timezone: str
    open_time: time
    close_time: time

    @classmethod
    def from_settings(cls) -> "MarketWindow":
        return cls(settings.market_timezone, _parse_hhmm(settings.market_open), _parse_hhmm(settings.market_close))

    def is_open(self, at: datetime | None = None) -> bool:
        zone = ZoneInfo(self.timezone)
        current = at.astimezone(zone) if at else datetime.now(zone)
        if current.weekday() >= 5:
            return False
        return self.open_time <= current.time() <= self.close_time

    def status(self, at: datetime | None = None) -> dict[str, object]:
        zone = ZoneInfo(self.timezone)
        current = at.astimezone(zone) if at else datetime.now(zone)
        return {
            "timezone": self.timezone,
            "local_time": current.isoformat(timespec="seconds"),
            "open": self.open_time.isoformat(timespec="minutes"),
            "close": self.close_time.isoformat(timespec="minutes"),
            "is_open": self.is_open(current),
        }


def is_closed_from_live_status(status_text: str) -> bool:
    """Parse cse.lk's marketStatus text (e.g. "Market Closed", "Market Open").

    Matches on "closed" rather than an exact string, since cse.lk documents no
    fixed enum of status values - a permissive parse is safer than assuming the
    exact open-state wording without ever having observed it live.
    """
    return "closed" in status_text.lower()


def _parse_hhmm(value: str) -> time:
    hour, minute = value.split(":", 1)
    return time(int(hour), int(minute))


def interval_with_jitter(base_seconds: int | None = None, jitter_seconds: int | None = None) -> int:
    base = base_seconds if base_seconds is not None else settings.poll_interval_seconds
    jitter = jitter_seconds if jitter_seconds is not None else settings.poll_jitter_seconds
    if jitter <= 0:
        return base
    return max(1, base + randint(-jitter, jitter))
