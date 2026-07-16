from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from pulsecse.core.models import AlertEvent


@dataclass(slots=True)
class DeliveryResult:
    """Result of a delivery attempt."""
    channel: str
    """The channel used for delivery."""
    ok: bool
    """Whether the delivery was successful."""
    detail: str = field(default="")
    """Additional details about the delivery result."""


class Notifier(Protocol):
    """Protocol for notifiers."""
    channel: str
    """The channel used by this notifier."""

    def send(self, event: AlertEvent) -> DeliveryResult:
        """Send a notification for the given event."""
        ...