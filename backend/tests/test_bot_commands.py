from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pulsecse.bot.commands import CommandRouter
from pulsecse.storage.sqlite import SQLiteRepository


class CommandRouterTests(unittest.TestCase):
    def test_watch_and_alert_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = SQLiteRepository(Path(tmp) / "bot.sqlite3")
            router = CommandRouter(repo)
            result = router.handle("/watch JKH.N0000")
            self.assertTrue(result.ok)
            self.assertIn("JKH.N0000", repo.watchlist("demo"))
            result = router.handle("/alert JKH.N0000 price_above 200")
            self.assertTrue(result.ok)
            self.assertEqual(len(repo.list_rules("demo")), 1)
            alerts = router.handle("/alerts")
            self.assertIn("price_above", alerts.text)
            repo.close()


if __name__ == "__main__":
    unittest.main()
