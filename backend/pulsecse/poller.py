from __future__ import annotations

import signal
import time
from dataclasses import dataclass

from pulsecse.config import settings
from pulsecse.market_hours import interval_with_jitter
from pulsecse.observability import log_event
from pulsecse.services.market_service import MarketService


@dataclass(slots=True)
class Poller:
    service: MarketService
    interval_seconds: int = settings.poll_interval_seconds
    respect_market_hours: bool = True
    running: bool = False

    def run_once(self, force: bool = False) -> dict[str, object]:
        result = self.service.tick(force=force or not self.respect_market_hours)
        payload = result.to_dict()
        log_event("poll_cycle", snapshots=len(result.snapshots), disclosures=len(result.disclosures), events=len(result.events))
        return payload

    def run_forever(self) -> None:
        self.running = True

        def stop(_signum: int, _frame: object) -> None:
            self.running = False
            log_event("poller_stop_requested")

        signal.signal(signal.SIGINT, stop)
        signal.signal(signal.SIGTERM, stop)
        log_event("poller_started", interval_seconds=self.interval_seconds, respect_market_hours=self.respect_market_hours)
        while self.running:
            self.run_once(force=False)
            time.sleep(interval_with_jitter(self.interval_seconds))
