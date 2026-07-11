from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pulsecse.core.models import Holding, StockSnapshot
from pulsecse.storage.sqlite import SQLiteRepository


class PortfolioTests(unittest.TestCase):
    def test_portfolio_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = SQLiteRepository(Path(tmp) / "portfolio.sqlite3")
            repo.insert_snapshots([StockSnapshot("JKH.N0000", 200, 190, 1000, 900, 202, 188)])
            repo.upsert_holding(Holding("demo", "JKH.N0000", 10, 180))
            summary = repo.portfolio_summary("demo")
            self.assertEqual(summary.total_value, 2000)
            self.assertGreater(summary.unrealized_pnl_percent, 0)
            repo.close()


if __name__ == "__main__":
    unittest.main()
