from __future__ import annotations

import random
from dataclasses import replace
from typing import Iterable

from pulsecse.core.models import Disclosure, Stock, StockSnapshot, new_id, utc_now


SEED_STOCKS = [
    Stock("JKH.N0000", "John Keells Holdings PLC", "Capital Goods"),
    Stock("COMB.N0000", "Commercial Bank of Ceylon PLC", "Banks"),
    Stock("HNB.N0000", "Hatton National Bank PLC", "Banks"),
    Stock("DIAL.N0000", "Dialog Axiata PLC", "Telecommunication"),
    Stock("LOLC.N0000", "LOLC Holdings PLC", "Diversified Financials"),
    Stock("SAMP.N0000", "Sampath Bank PLC", "Banks"),
    Stock("CTC.N0000", "Ceylon Tobacco Company PLC", "Food Beverage and Tobacco"),
    Stock("NEST.N0000", "Nestle Lanka PLC", "Food Beverage and Tobacco"),
    Stock("EXPO.N0000", "Expolanka Holdings PLC", "Transportation"),
    Stock("ACL.N0000", "ACL Cables PLC", "Capital Goods"),
    Stock("HAYL.N0000", "Hayleys PLC", "Capital Goods"),
    Stock("MELS.N0000", "Melstacorp PLC", "Diversified Financials"),
]

_BASE = {
    "JKH.N0000": (194.50, 960000),
    "COMB.N0000": (122.75, 720000),
    "HNB.N0000": (238.25, 380000),
    "DIAL.N0000": (12.40, 1800000),
    "LOLC.N0000": (486.00, 230000),
    "SAMP.N0000": (91.20, 610000),
    "CTC.N0000": (1295.00, 46000),
    "NEST.N0000": (1015.00, 18000),
    "EXPO.N0000": (142.60, 880000),
    "ACL.N0000": (96.30, 320000),
    "HAYL.N0000": (107.80, 270000),
    "MELS.N0000": (78.50, 510000),
}

_DISCLOSURES = [
    "Interim financial statements released",
    "Board meeting outcome announced",
    "Dividend announcement published",
    "Annual General Meeting notice released",
    "Related party transaction disclosure",
    "Investor presentation update",
]


class MockMarketAdapter:
    """Deterministic-enough demo market source for local development and tests."""

    def __init__(self, seed: int = 7) -> None:
        self.random = random.Random(seed)
        self._snapshots: dict[str, StockSnapshot] = {
            symbol: StockSnapshot(
                symbol=symbol,
                price=price,
                previous_close=round(price * self.random.uniform(0.985, 1.012), 2),
                volume=volume,
                previous_volume=max(1, round(volume * self.random.uniform(0.8, 1.2))),
                high=round(price * 1.018, 2),
                low=round(price * 0.982, 2),
            )
            for symbol, (price, volume) in _BASE.items()
        }

    def list_stocks(self) -> list[Stock]:
        return list(SEED_STOCKS)

    def latest_snapshots(self) -> list[StockSnapshot]:
        next_snapshots = []
        for snapshot in self._snapshots.values():
            drift = self.random.uniform(-0.018, 0.022)
            volume_drift = self.random.uniform(0.88, 1.22)
            price = max(1, round(snapshot.price * (1 + drift), 2))
            volume = max(1, round(snapshot.volume * volume_drift))
            updated = StockSnapshot(
                symbol=snapshot.symbol,
                price=price,
                previous_close=snapshot.price,
                volume=volume,
                previous_volume=snapshot.volume,
                high=max(snapshot.high, price),
                low=min(snapshot.low, price),
                market_time=utc_now(),
                source="mock",
            )
            self._snapshots[snapshot.symbol] = updated
            next_snapshots.append(updated)
        return next_snapshots

    def latest_disclosures(self) -> list[Disclosure]:
        if self.random.random() > 0.35:
            return []
        stock = self.random.choice(SEED_STOCKS)
        title = self.random.choice(_DISCLOSURES)
        return [
            Disclosure(
                id=new_id("disc"),
                symbol=stock.symbol,
                title=title,
                category="Corporate Disclosure",
                published_at=utc_now(),
                source="mock",
            )
        ]

    def apply_scenario(self, scenario: str) -> tuple[list[StockSnapshot], list[Disclosure]]:
        recipes = {
            "jkh_breakout": ("JKH.N0000", 1.055, 1.40, None),
            "hnb_support_break": ("HNB.N0000", 0.955, 1.30, None),
            "comb_disclosure": ("COMB.N0000", 1.010, 1.08, "New interim financial statement and board update published"),
            "dial_volume": ("DIAL.N0000", 1.015, 2.10, None),
            "market_rally": ("ALL", 1.025, 1.25, None),
        }
        symbol, price_mult, volume_mult, disclosure_title = recipes.get(scenario, recipes["market_rally"])
        touched: list[StockSnapshot] = []
        disclosures: list[Disclosure] = []
        for current_symbol, snapshot in list(self._snapshots.items()):
            if symbol != "ALL" and current_symbol != symbol:
                continue
            updated = StockSnapshot(
                symbol=current_symbol,
                price=round(snapshot.price * price_mult, 2),
                previous_close=snapshot.price,
                volume=round(snapshot.volume * volume_mult),
                previous_volume=snapshot.volume,
                high=max(snapshot.high, round(snapshot.price * price_mult, 2)),
                low=min(snapshot.low, round(snapshot.price * price_mult, 2)),
                market_time=utc_now(),
                source=f"scenario:{scenario}",
            )
            self._snapshots[current_symbol] = updated
            touched.append(updated)
        if disclosure_title and symbol != "ALL":
            disclosures.append(
                Disclosure(
                    id=new_id("disc"),
                    symbol=symbol,
                    title=disclosure_title,
                    category="Financial Statements",
                    published_at=utc_now(),
                    source=f"scenario:{scenario}",
                )
            )
        return touched, disclosures
