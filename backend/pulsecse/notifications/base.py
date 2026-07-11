from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pulsecse.core.models import AlertEvent


@dataclass(slots=True)
class DeliveryResult:
    channel: str
    ok: bool
    detail: str = ""


class Notifier(Protocol):
    channel: str

    def send(self, event: AlertEvent) -> DeliveryResult:
        ...
