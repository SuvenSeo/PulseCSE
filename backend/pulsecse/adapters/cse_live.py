from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

from pulsecse.core.models import Disclosure, Stock, StockSnapshot, new_id, utc_now


class CSELiveAdapter:
    """Adapter for public cse.lk endpoints.

    Field names below were confirmed against live responses from
    ``https://www.cse.lk/api/`` (see docs/BACKEND_HARDENING.md) rather than guessed,
    following the same probe-and-record approach documented in Chime's
    ``docs/endpoint_probe_report.md``. ``listedCompanies`` returns HTTP 404 on the
    live API and is not used; the stock list is derived from ``tradeSummary``
    instead, which is confirmed working and already carries id/symbol/name.

    The rest of PulseCSE uses this only through the adapter boundary. That means the
    app can keep running with the mock adapter if public endpoints change or a user
    does not have permission to use live market data in production.
    """

    def __init__(self, base_url: str = "https://www.cse.lk", timeout_seconds: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _post(self, endpoint: str, data: dict[str, str] | None = None) -> dict[str, Any]:
        """Makes a POST request to a CSE API endpoint."""
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        encoded = urllib.parse.urlencode(data or {}).encode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/",
            "User-Agent": "PulseCSE/1.0 (https://github.com/SuvenSeo/PulseCSE)", 
        }
        request = urllib.request.Request(url, data=encoded, headers=headers)
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    # Added new methods to support the requirements
    def get_stock_list(self) -> list[Stock]:
        """Fetches the list of stocks from the CSE API."""
        response = self._post("tradeSummary")
        stocks = []
        for stock in response["stocks"]:
            stocks.append(Stock(
                id=stock["id"],
                symbol=stock["symbol"],
                name=stock["name"]
            ))
        return stocks

    def get_stock_snapshot(self, stock_id: str) -> StockSnapshot:
        """Fetches the snapshot of a specific stock from the CSE API."""
        response = self._post("stockSnapshot", {"stockId": stock_id})
        return StockSnapshot(
            id=response["id"],
            stock_id=stock_id,
            price=response["price"],
            volume=response["volume"],
            timestamp=utc_now()
        )

    def get_disclosures(self, stock_id: str) -> list[Disclosure]:
        """Fetches the list of disclosures for a specific stock from the CSE API."""
        response = self._post("disclosures", {"stockId": stock_id})
        disclosures = []
        for disclosure in response["disclosures"]:
            disclosures.append(Disclosure(
                id=disclosure["id"],
                stock_id=stock_id,
                title=disclosure["title"],
                description=disclosure["description"],
                timestamp=utc_now()
            ))
        return disclosures