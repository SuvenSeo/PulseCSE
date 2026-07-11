from __future__ import annotations

from collections import defaultdict
from statistics import mean

from .models import Stock, StockSnapshot


def risk_score(history: list[float], snapshot: StockSnapshot) -> int:
    returns = []
    for previous, current in zip(history, history[1:]):
        if previous:
            returns.append(abs((current - previous) / previous) * 100)
    volatility = mean(returns) if returns else 0
    daily_move = abs(snapshot.change_percent)
    volume_pressure = max(0, snapshot.volume_change_percent) / 10
    score = round(volatility * 12 + daily_move * 9 + volume_pressure)
    return max(0, min(100, score))


def risk_label(score: int) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def market_breadth(snapshots: list[StockSnapshot]) -> dict[str, int]:
    gainers = sum(1 for item in snapshots if item.change_percent > 0)
    losers = sum(1 for item in snapshots if item.change_percent < 0)
    flat = len(snapshots) - gainers - losers
    return {"gainers": gainers, "losers": losers, "flat": flat}


def top_movers(snapshots: list[StockSnapshot], limit: int = 5) -> dict[str, list[StockSnapshot]]:
    return {
        "gainers": sorted(snapshots, key=lambda item: item.change_percent, reverse=True)[:limit],
        "losers": sorted(snapshots, key=lambda item: item.change_percent)[:limit],
        "volume": sorted(snapshots, key=lambda item: item.volume_change_percent, reverse=True)[:limit],
    }


def sector_heatmap(stocks: list[Stock], snapshots: list[StockSnapshot]) -> list[dict[str, object]]:
    by_symbol = {item.symbol: item for item in stocks}
    groups: dict[str, list[StockSnapshot]] = defaultdict(list)
    for snapshot in snapshots:
        stock = by_symbol.get(snapshot.symbol)
        if stock:
            groups[stock.sector].append(snapshot)
    heatmap = []
    for sector, items in groups.items():
        average_change = mean([item.change_percent for item in items]) if items else 0
        heatmap.append(
            {
                "sector": sector,
                "count": len(items),
                "average_change": round(average_change, 2),
                "total_volume": sum(item.volume for item in items),
                "leader": max(items, key=lambda item: item.change_percent).symbol,
            }
        )
    return sorted(heatmap, key=lambda item: item["average_change"], reverse=True)


def suggested_alerts(snapshot: StockSnapshot, score: int) -> list[dict[str, object]]:
    suggestions: list[dict[str, object]] = []
    if snapshot.change_percent >= 2:
        suggestions.append({"type": "price_above", "target": round(snapshot.price * 1.01, 2), "reason": "momentum continuation"})
    if snapshot.change_percent <= -1.5 or score >= 55:
        suggestions.append({"type": "price_below", "target": round(snapshot.price * 0.98, 2), "reason": "downside protection"})
    if snapshot.volume_change_percent >= 35:
        suggestions.append({"type": "volume_spike", "target": 50, "reason": "unusual activity"})
    suggestions.append({"type": "disclosure", "target": 0, "reason": "corporate announcement monitoring"})
    return suggestions[:3]
