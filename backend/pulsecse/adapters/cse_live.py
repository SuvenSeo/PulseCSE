from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any

from pulsecse.core.models import Disclosure, Stock, StockSnapshot, new_id, utc_now


class CSELiveAdapter:
    """Best-effort adapter for public cse.lk endpoints.

    The rest of PulseCSE uses this only through the adapter boundary. That means the
    app can keep running with the mock adapter if public endpoints change or a user
    does not have permission to use live market data in production.
    """

    def __init__(self, base_url: str = "https://www.cse.lk", timeout_seconds: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _post(self, endpoint: str, data: dict[str, str] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        encoded = urllib.parse.urlencode(data or {}).encode("utf-8")
        request = urllib.request.Request(url, data=encoded, headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def list_stocks(self) -> list[Stock]:
        payload = self._post("listedCompanies")
        rows = payload.get("reqSymbolInfo") or payload.get("data") or payload.get("list") or []
        stocks: list[Stock] = []
        for row in rows:
            symbol = str(row.get("symbol") or row.get("Symbol") or "").strip().upper()
            if not symbol:
                continue
            stocks.append(
                Stock(
                    symbol=symbol,
                    name=str(row.get("name") or row.get("companyName") or row.get("Name") or symbol),
                    sector=str(row.get("sector") or row.get("sectorName") or "Unknown"),
                    board=str(row.get("board") or "Main Board"),
                    isin=row.get("isin"),
                )
            )
        return stocks

    def latest_snapshots(self) -> list[StockSnapshot]:
        payload = self._post("tradeSummary")
        rows = payload.get("reqTradeSummery") or payload.get("data") or payload.get("list") or []
        snapshots: list[StockSnapshot] = []
        for row in rows:
            symbol = str(row.get("symbol") or row.get("Symbol") or "").strip().upper()
            if not symbol:
                continue
            price = _float(row.get("lastTradedPrice") or row.get("price") or row.get("last") or 0)
            previous = _float(row.get("previousClose") or row.get("previous_close") or price)
            volume = int(_float(row.get("volume") or row.get("shareVolume") or 0))
            snapshots.append(
                StockSnapshot(
                    symbol=symbol,
                    price=price,
                    previous_close=previous,
                    volume=volume,
                    previous_volume=max(1, int(_float(row.get("previousVolume") or volume))),
                    high=_float(row.get("high") or row.get("High") or price),
                    low=_float(row.get("low") or row.get("Low") or price),
                    market_time=str(row.get("tradeTime") or row.get("date") or utc_now()),
                    source="cse-live",
                )
            )
        return snapshots

    def latest_disclosures(self) -> list[Disclosure]:
        payload = self._post("approvedAnnouncement")
        rows = payload.get("reqAnnouncements") or payload.get("data") or payload.get("list") or []
        disclosures: list[Disclosure] = []
        for row in rows:
            symbol = str(row.get("symbol") or row.get("companySymbol") or "").strip().upper()
            title = str(row.get("title") or row.get("announcementTitle") or row.get("heading") or "Corporate disclosure")
            external_id = str(row.get("id") or row.get("announcementId") or f"{symbol}:{title}")
            disclosures.append(
                Disclosure(
                    id=f"disc_{abs(hash(external_id))}",
                    symbol=symbol,
                    title=title,
                    category=str(row.get("category") or row.get("type") or "Announcement"),
                    published_at=str(row.get("publishedDate") or row.get("date") or utc_now()),
                    url=row.get("url") or row.get("filePath"),
                    source="cse-live",
                )
            )
        return disclosures


def _float(value: Any) -> float:
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return 0.0
