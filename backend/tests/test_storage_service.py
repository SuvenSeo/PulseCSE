from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pulsecse.adapters.mock_market import MockMarketAdapter
from pulsecse.core.models import AlertRule, AlertType, StockSnapshot
from pulsecse.services.market_service import MarketService
from pulsecse.storage.sqlite import SQLiteRepository


class _FakeLiveStatusAdapter(MockMarketAdapter):
    """MockMarketAdapter plus a live market_status(), for testing the
    live-status-preferred-over-local-guess behavior without hitting cse.lk."""

    def __init__(self, status: str) -> None:
        super().__init__()
        self._status = status

    def market_status(self) -> str:
        return self._status


class StorageServiceTests(unittest.TestCase):
    def test_repository_roundtrip_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = SQLiteRepository(Path(tmp) / "test.sqlite3")
            rule = AlertRule("rule_test", "demo", "JKH.N0000", AlertType.PRICE_ABOVE, 200)
            repo.upsert_rules([rule])
            rules = repo.list_rules("demo")
            self.assertEqual(len(rules), 1)
            self.assertEqual(rules[0].symbol, "JKH.N0000")
            repo.close()

    def test_service_bootstrap_and_dashboard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = SQLiteRepository(Path(tmp) / "test.sqlite3")
            service = MarketService(repo)
            service.bootstrap()
            data = service.dashboard("demo")
            self.assertGreaterEqual(len(data["stocks"]), 10)
            self.assertIn("breadth", data)
            repo.close()

    def test_tick_skips_when_live_status_reports_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = SQLiteRepository(Path(tmp) / "test.sqlite3")
            service = MarketService(repo, adapter=_FakeLiveStatusAdapter("Market Closed"))
            result = service.tick(force=False)
            self.assertEqual(result.snapshots, [])
            self.assertEqual(repo.get_state("last_skip_reason"), "market_closed")
            repo.close()

    def test_tick_proceeds_when_live_status_reports_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = SQLiteRepository(Path(tmp) / "test.sqlite3")
            service = MarketService(repo, adapter=_FakeLiveStatusAdapter("Market Open"))
            result = service.tick(force=False)
            self.assertGreater(len(result.snapshots), 0)
            repo.close()

    def test_market_open_falls_back_to_local_window_without_live_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = SQLiteRepository(Path(tmp) / "test.sqlite3")
            service = MarketService(repo, adapter=MockMarketAdapter())
            is_open, live_status = service._market_open()
            self.assertIsNone(live_status)
            self.assertEqual(is_open, service.market_window.is_open())
            repo.close()


if __name__ == "__main__":
    unittest.main()
