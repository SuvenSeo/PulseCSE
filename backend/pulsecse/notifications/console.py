from __future__ import annotations

from pulsecse.core.models import AlertEvent
from .base import DeliveryResult


class ConsoleNotifier:
    channel = "console"

    def send(self, event: AlertEvent) -> DeliveryResult:
        print(f"[PulseCSE] {event.severity.upper()} {event.symbol}: {event.message}")
        return DeliveryResult(channel=self.channel, ok=True, detail="printed")