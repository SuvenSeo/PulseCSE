from __future__ import annotations

import unittest

from pulsecse.core.engine import evaluate_rule, evaluate_rules
from pulsecse.core.models import AlertRule, AlertType, Disclosure, StockSnapshot


class EngineTests(unittest.TestCase):
    def test_price_above_crossing_fires_once(self) -> None:
        rule = AlertRule("rule_1", "demo", "JKH.N0000", AlertType.PRICE_ABOVE, target=200)
        snapshot = StockSnapshot("JKH.N0000", price=202, previous_close=198, volume=1000, previous_volume=900, high=203, low=197)
        updated, event = evaluate_rule(rule, snapshot, now="2026-07-11T20:00:00+00:00")
        self.assertIsNotNone(event)
        self.assertFalse(updated.armed)
        self.assertEqual(updated.fire_count, 1)

    def test_price_above_does_not_fire_when_already_above(self) -> None:
        rule = AlertRule("rule_1", "demo", "JKH.N0000", AlertType.PRICE_ABOVE, target=200)
        snapshot = StockSnapshot("JKH.N0000", price=205, previous_close=203, volume=1000, previous_volume=900, high=206, low=202)
        updated, event = evaluate_rule(rule, snapshot)
        self.assertIsNone(event)
        self.assertTrue(updated.armed)

    def test_disclosure_fires(self) -> None:
        rule = AlertRule("rule_2", "demo", "COMB.N0000", AlertType.DISCLOSURE, target=0)
        snapshot = StockSnapshot("COMB.N0000", price=120, previous_close=119, volume=1000, previous_volume=900, high=121, low=118)
        disclosure = Disclosure("disc_1", "COMB.N0000", "Dividend announcement published", "Dividend", "2026-07-11T20:00:00+00:00")
        _, event = evaluate_rule(rule, snapshot, disclosures=[disclosure])
        self.assertIsNotNone(event)
        self.assertEqual(event.reason, "new_disclosure")

    def test_keyword_disclosure_requires_keyword_match(self) -> None:
        rule = AlertRule("rule_3", "demo", "COMB.N0000", AlertType.NEWS_KEYWORD, keyword="dividend")
        snapshot = StockSnapshot("COMB.N0000", price=120, previous_close=119, volume=1000, previous_volume=900, high=121, low=118)
        disclosure = Disclosure("disc_1", "COMB.N0000", "Dividend announcement published", "Dividend", "2026-07-11T20:00:00+00:00")
        _, event = evaluate_rule(rule, snapshot, disclosures=[disclosure])
        self.assertIsNotNone(event)

    def test_evaluate_rules_handles_missing_snapshot(self) -> None:
        rule = AlertRule("rule_4", "demo", "MISSING", AlertType.PRICE_ABOVE, target=10)
        updated, events = evaluate_rules([rule], {})
        self.assertEqual(len(updated), 1)
        self.assertEqual(events, [])


if __name__ == "__main__":
    unittest.main()
