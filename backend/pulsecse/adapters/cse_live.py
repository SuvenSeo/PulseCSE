from __future__ import annotations

from pulsecse.core.models import Disclosure, Stock, StockSnapshot


class CSELiveAdapter:
    """Optional live adapter boundary.

    The production project should keep live exchange integration behind this class so
    the rest of the system is stable even if public CSE endpoints change. The mock
    adapter is the default because it is deterministic, demo-safe, and does not make
    financial claims.
    """

    def __init__(self, base_url: str = "https://www.cse.lk") -> None:
        self.base_url = base_url.rstrip("/")

    def list_stocks(self) -> list[Stock]:
        raise NotImplementedError("Live CSE adapter is intentionally separated from the core app.")

    def latest_snapshots(self) -> list[StockSnapshot]:
        raise NotImplementedError("Implement with official/approved market-data access before production use.")

    def latest_disclosures(self) -> list[Disclosure]:
        raise NotImplementedError("Implement with official/approved disclosure access before production use.")
