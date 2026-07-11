from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pulsecse.core.models import AlertRule, AlertType, StockSnapshot
from pulsecse.services.market_service import MarketService
from pulsecse.storage.sqlite import SQLiteRepository


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


if __name__ == "__main__":
    unittest.main()
