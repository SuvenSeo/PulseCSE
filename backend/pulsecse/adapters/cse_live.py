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
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        encoded = urllib.parse.urlencode(data or {}).encode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/",
        }
        request = urllib.request.Request(url, data=encoded, headers=headers)
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def list_stocks(self) -> list[Stock]:
        # listedCompanies is not a real cse.lk endpoint (confirmed 404); tradeSummary
        # already carries id/symbol/name for every listed stock, so it doubles as
        # the stock directory. It does not carry sector, so that stays "Unknown"
        # until it's sourced from a verified endpoint.
        payload = self._post("tradeSummary")
        rows = payload.get("reqTradeSummery") or []
        stocks: list[Stock] = []
        for row in rows:
            symbol = str(row.get("symbol") or "").strip().upper()
            if not symbol:
                continue
            stocks.append(
                Stock(
                    symbol=symbol,
                    name=str(row.get("name") or symbol),
                    sector="Unknown",
                    board="Main Board",
                    isin=None,
                )
            )
        return stocks

    def latest_snapshots(self) -> list[StockSnapshot]:
        payload = self._post("tradeSummary")
        rows = payload.get("reqTradeSummery") or []
        snapshots: list[StockSnapshot] = []
        for row in rows:
            symbol = str(row.get("symbol") or "").strip().upper()
            if not symbol:
                continue
            price = _float(row.get("price") or 0)
            previous = _float(row.get("previousClose") or price)
            volume = int(_float(row.get("sharevolume") or 0))
            snapshots.append(
                StockSnapshot(
                    symbol=symbol,
                    price=price,
                    previous_close=previous,
                    volume=volume,
                    previous_volume=max(1, volume),
                    high=_float(row.get("high") or price),
                    low=_float(row.get("low") or price),
                    market_time=_epoch_ms_to_iso(row.get("lastTradedTime")),
                    source="cse-live",
                )
            )
        return snapshots

    def latest_disclosures(self) -> list[Disclosure]:
        payload = self._post("approvedAnnouncement")
        rows = payload.get("approvedAnnouncements") or []
        disclosures: list[Disclosure] = []
        for row in rows:
            # cse.lk returns "symbol": null on almost every announcement row; there is
            # no reliable per-row symbol here. Callers that need a symbol match must
            # resolve `company` (the issuer's display name) against the stock list
            # themselves - this adapter does not fabricate a symbol.
            company = str(row.get("company") or "").strip()
            title = str(row.get("remarks") or row.get("announcementCategory") or "Corporate disclosure")
            external_id = str(row.get("announcementId") or row.get("id") or f"{company}:{title}")
            disclosures.append(
                Disclosure(
                    id=f"disc_{abs(hash(external_id))}",
                    symbol=str(row.get("symbol") or "").strip().upper(),
                    title=f"{company}: {title}" if company else title,
                    category=str(row.get("announcementCategory") or "Announcement"),
                    published_at=str(row.get("dateOfAnnouncement") or _epoch_ms_to_iso(row.get("createdDate"))),
                    url=None,
                    source="cse-live",
                )
            )
        return disclosures


def _epoch_ms_to_iso(value: Any) -> str:
    try:
        millis = float(value)
        if millis <= 0:
            raise ValueError
        return datetime.fromtimestamp(millis / 1000, tz=timezone.utc).isoformat(timespec="seconds")
    except (TypeError, ValueError):
        return utc_now()


def _float(value: Any) -> float:
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return 0.0
