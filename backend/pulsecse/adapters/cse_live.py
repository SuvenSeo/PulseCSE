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
            "User-Agent": "PulseCSE/1.0 (https://github.com/SuvenSeo/PulseCSE)", # Good practice for public APIs
        }
        request = urllib.request.Request(url, data=encoded, headers=headers)
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def _get_trade_summary_data(self) -> list[dict[str, Any]]:
        """Fetches the raw trade summary data from CSE API.
        Assumes the endpoint /api/tradeSummary/daily provides the full daily summary.
        """
        try:
            response = self._post("tradeSummary/daily") # Common CSE endpoint for daily summary
            # CSE API often wraps lists in a 'data' key, or returns directly a list
            if isinstance(response, dict) and "data" in response and isinstance(response["data"], list):
                return response["data"]
            elif isinstance(response, list):
                return response
            else:
                # In a real application, use a proper logger here
                print(f"Warning: Unexpected tradeSummary response format: {response}")
                return []
        except Exception as e:
            # In a real application, use a proper logger here
            print(f"Error fetching trade summary from CSE live adapter: {e}")
            return []

    def list_stocks(self) -> list[Stock]:
        """Lists all tradable stocks from the CSE by parsing the trade summary."""
        trade_summary = self._get_trade_summary_data()
        stocks = []
        for item in trade_summary:
            try:
                # Use 'id' from API if available and looks like a valid ID, else generate
                stock_api_id = item.get("id")
                stock_id = stock_api_id if isinstance(stock_api_id, str) and stock_api_id else new_id("stock")
                
                symbol = item.get("symbol")
                name = item.get("name")
                
                if symbol and name:
                    stocks.append(Stock(id=stock_id, symbol=symbol, name=name))
            except Exception as e:
                print(f"Error parsing stock item from trade summary: {item}. Error: {e}")
        return stocks

    def get_stock_snapshot(self, symbol: str) -> StockSnapshot | None:
        """Retrieves the latest snapshot for a specific stock symbol from the trade summary."""
        trade_summary = self._get_trade_summary_data()
        for item in trade_summary:
            if item.get("symbol") == symbol:
                try:
                    # Map CSE API fields to StockSnapshot model
                    price = float(item.get("lastTradedPrice", 0.0))
                    open_price = float(item.get("openPrice", 0.0))
                    high_price = float(item.get("highPrice", 0.0))
                    low_price = float(item.get("lowPrice", 0.0))
                    volume = int(item.get("volume", 0))
                    change = float(item.get("change", 0.0))
                    change_percent = float(item.get("changePercentage", 0.0))
                    trade_count = int(item.get("tradeCount", 0))
                    turnover = float(item.get("turnover", 0.0))

                    # Parse timestamp from API response, assuming ISO format
                    timestamp_str = item.get("dateTime")
                    if timestamp_str:
                        # Attempt to parse as ISO 8601 with optional timezone (Z or offset)
                        # If no timezone info, assume UTC for consistency with PulseCSE models
                        try:
                            # Replace 'Z' with '+00:00' for standard library parsing
                            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")).astimezone(timezone.utc)
                        except ValueError:
                            # Fallback for naive datetime strings, assume UTC
                            timestamp = datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc)
                    else:
                        timestamp = utc_now() # Fallback to current UTC time if no timestamp provided

                    return StockSnapshot(
                        id=new_id("snapshot"), # Snapshots always get new IDs
                        stock_symbol=symbol,
                        timestamp=timestamp,
                        price=price,
                        open=open_price,
                        high=high_price,
                        low=low_price,
                        volume=volume,
                        change=change,
                        change_percent=change_percent,
                        trade_count=trade_count,
                        turnover=turnover,
                    )
                except (ValueError, TypeError) as e:
                    print(f"Error parsing snapshot data for {symbol} from item {item}: {e}")
                    return None
        return None

    def list_disclosures(self) -> list[Disclosure]:
        """Lists recent company disclosures from the CSE."""
        disclosures = []
        try:
            # Assuming an endpoint like /api/announcements/latest exists for recent disclosures
            response = self._post("announcements/latest") # Common CSE endpoint for latest announcements
            
            # CSE API often wraps lists in a 'data' key or returns directly a list
            items = response.get("data", response) if isinstance(response, dict) else response

            for item in items:
                try:
                    # Use 'id' from API if available and looks like a valid ID, else generate
                    disclosure_api_id = item.get("id")
                    disclosure_id = disclosure_api_id if isinstance(disclosure_api_id, str) and disclosure_api_id else new_id("disclosure")
                    
                    title = item.get("title")
                    url = item.get("url")
                    # CSE API might use 'companySymbol' or just 'symbol' for the associated stock
                    company_symbol = item.get("companySymbol") or item.get("symbol")
                    date_str = item.get("date")

                    if not all([title, url, date_str]): # Basic validation
                        continue

                    # Parse date string, similar logic to StockSnapshot timestamp
                    try:
                        disclosure_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")).astimezone(timezone.utc)
                    except ValueError:
                        disclosure_date = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)

                    disclosures.append(Disclosure(
                        id=disclosure_id,
                        title=title,
                        url=url,
                        date=disclosure_date,
                        symbol=company_symbol,
                    ))
                except Exception as e:
                    print(f"Error parsing disclosure item {item}: {e}")
        except Exception as e:
            print(f"Error fetching disclosures from CSE live adapter: {e}")
        return disclosures
