from __future__ import annotations

import json
import urllib.request

from pulsecse.core.models import AlertEvent
from .base import DeliveryResult


class WebhookNotifier:
    channel = "webhook"

    def __init__(self, url: str, timeout_seconds: int = 8) -> None:
        self.url = url
        self.timeout_seconds = timeout_seconds

    def send(self, event: AlertEvent) -> DeliveryResult:
        if not self.url:
            return DeliveryResult(self.channel, False, "missing webhook url")
        request = urllib.request.Request(
            self.url,
            data=json.dumps(event.to_dict()).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return DeliveryResult(self.channel, 200 <= response.status < 300, f"status={response.status}")
        except Exception as exc:
            return DeliveryResult(self.channel, False, str(exc))
