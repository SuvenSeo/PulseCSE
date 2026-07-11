from __future__ import annotations

import json
import urllib.parse
import urllib.request

from pulsecse.core.models import AlertEvent
from .base import DeliveryResult


class TelegramNotifier:
    channel = "telegram"

    def __init__(self, token: str, chat_id: str, timeout_seconds: int = 8) -> None:
        self.token = token
        self.chat_id = chat_id
        self.timeout_seconds = timeout_seconds

    def send(self, event: AlertEvent) -> DeliveryResult:
        if not self.token or not self.chat_id:
            return DeliveryResult(self.channel, False, "missing token or chat id")
        text = f"PulseCSE {event.severity.upper()}\n{event.symbol}\n{event.message}"
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": self.chat_id, "text": text}).encode("utf-8")
        try:
            with urllib.request.urlopen(url, data=data, timeout=self.timeout_seconds) as response:
                payload = response.read().decode("utf-8")
            ok = json.loads(payload).get("ok", False)
            return DeliveryResult(self.channel, bool(ok), payload[:200])
        except Exception as exc:  # network errors should not crash rule evaluation
            return DeliveryResult(self.channel, False, str(exc))
