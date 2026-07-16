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
                id=new_id(),
                timestamp=utc_now(),
                stock=stock,
                price=self.random.uniform(_BASE[stock.symbol][0] * 0.9, _BASE[stock.symbol][0] * 1.1),
                volume=self.random.randint(_BASE[stock.symbol][1] * 0.9, _BASE[stock.symbol][1] * 1.1),
                disclosures=[
                    Disclosure(
                        id=new_id(),
                        timestamp=utc_now(),
                        content=self.random.choice(_DISCLOSURES),
                    )
                ],
            )
            for symbol, stock in [(stock.symbol, stock) for stock in SEED_STOCKS]
        }

    def get_stock_snapshot(self, symbol: str) -> StockSnapshot:
        """Get the current stock snapshot for the given symbol."""
        return self._snapshots[symbol]

    def get_stock_snapshots(self) -> Iterable[StockSnapshot]:
        """Get all current stock snapshots."""
        return self._snapshots.values()

    def update_stock_snapshot(self, symbol: str, price: float, volume: int) -> None:
        """Update the stock snapshot for the given symbol."""
        self._snapshots[symbol] = replace(self._snapshots[symbol], price=price, volume=volume)

    def add_disclosure(self, symbol: str, content: str) -> None:
        """Add a new disclosure to the stock snapshot for the given symbol."""
        self._snapshots[symbol].disclosures.append(
            Disclosure(id=new_id(), timestamp=utc_now(), content=content)
        )