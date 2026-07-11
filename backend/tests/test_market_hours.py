from __future__ import annotations

import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from pulsecse.market_hours import MarketWindow, interval_with_jitter


class MarketHoursTests(unittest.TestCase):
    def test_market_open_window_weekday(self) -> None:
        window = MarketWindow("Asia/Colombo", __import__("datetime").time(9, 30), __import__("datetime").time(14, 30))
        at = datetime(2026, 7, 13, 10, 0, tzinfo=ZoneInfo("Asia/Colombo"))
        self.assertTrue(window.is_open(at))

    def test_market_closed_weekend(self) -> None:
        window = MarketWindow("Asia/Colombo", __import__("datetime").time(9, 30), __import__("datetime").time(14, 30))
        at = datetime(2026, 7, 12, 10, 0, tzinfo=ZoneInfo("Asia/Colombo"))
        self.assertFalse(window.is_open(at))

    def test_jitter_is_positive(self) -> None:
        self.assertGreater(interval_with_jitter(60, 8), 0)


if __name__ == "__main__":
    unittest.main()
