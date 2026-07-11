from __future__ import annotations

"""Postgres repository for production deployments.

This module intentionally imports psycopg lazily so the project can run in SQLite
mode without Postgres client libraries installed. The SQL schema lives in
``db/migrations`` and mirrors the SQLite repository API used by the service.
"""

import json
from typing import Iterable, Any

from pulsecse.core.models import (
    AlertEvent,
    AlertRule,
    AlertStatus,
    AlertType,
    DeliveryChannel,
    Disclosure,
    Holding,
    PortfolioPosition,
    PortfolioSummary,
    Stock,
    StockSnapshot,
    utc_now,
)


class PostgresRepository:
    database_type = "postgres"

    def __init__(self, database_url: str) -> None:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Postgres mode requires: pip install psycopg[binary,pool]") from exc
        self._psycopg = psycopg
        self.conn = psycopg.connect(database_url, row_factory=dict_row, autocommit=True)

    def close(self) -> None:
        self.conn.close()

    def _execute(self, sql: str, params: tuple[Any, ...] = ()):
        return self.conn.execute(sql, params)

    def applied_migrations(self) -> list[str]:
        self._execute("CREATE TABLE IF NOT EXISTS schema_migrations (filename TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT now())")
        return [row["filename"] for row in self._execute("SELECT filename FROM schema_migrations ORDER BY filename").fetchall()]

    def mark_migration(self, filename: str) -> None:
        self._execute("INSERT INTO schema_migrations(filename) VALUES(%s) ON CONFLICT(filename) DO NOTHING", (filename,))

    def create_user(self, user_id: str, telegram_id: str | None = None, display_name: str | None = None) -> None:
        self._execute(
            "INSERT INTO users(id,telegram_id,display_name,created_at) VALUES(%s,%s,%s,%s) ON CONFLICT(id) DO NOTHING",
            (user_id, telegram_id, display_name, utc_now()),
        )

    def upsert_stocks(self, stocks: Iterable[Stock]) -> None:
        with self.conn.cursor() as cur:
            for item in stocks:
                cur.execute(
                    """
                    INSERT INTO stocks(symbol,name,sector,board,isin) VALUES(%s,%s,%s,%s,%s)
                    ON CONFLICT(symbol) DO UPDATE SET name=EXCLUDED.name, sector=EXCLUDED.sector, board=EXCLUDED.board, isin=EXCLUDED.isin
                    """,
                    (item.symbol, item.name, item.sector, item.board, item.isin),
                )

    def list_stocks(self) -> list[Stock]:
        rows = self._execute("SELECT * FROM stocks ORDER BY symbol").fetchall()
        return [Stock(row["symbol"], row["name"], row["sector"], row["board"], row.get("isin")) for row in rows]

    def insert_snapshots(self, snapshots: Iterable[StockSnapshot]) -> None:
        with self.conn.cursor() as cur:
            for item in snapshots:
                cur.execute(
                    """
                    INSERT INTO snapshots(symbol,price,previous_close,volume,previous_volume,high,low,market_time,source)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT(symbol, market_time, source) DO NOTHING
                    """,
                    (item.symbol, item.price, item.previous_close, item.volume, item.previous_volume, item.high, item.low, item.market_time, item.source),
                )

    def latest_snapshots(self) -> dict[str, StockSnapshot]:
        rows = self._execute(
            """
            SELECT DISTINCT ON (symbol) * FROM snapshots
            ORDER BY symbol, id DESC
            """
        ).fetchall()
        return {row["symbol"]: self._row_to_snapshot(row) for row in rows}

    def _row_to_snapshot(self, row: dict[str, Any]) -> StockSnapshot:
        return StockSnapshot(row["symbol"], float(row["price"]), float(row["previous_close"]), int(row["volume"]), int(row["previous_volume"]), float(row["high"]), float(row["low"]), str(row["market_time"]), row["source"])

    def price_history(self, symbol: str, limit: int = 40) -> list[float]:
        rows = self._execute("SELECT price FROM snapshots WHERE symbol=%s ORDER BY id DESC LIMIT %s", (symbol, limit)).fetchall()
        return [float(row["price"]) for row in reversed(rows)]

    def insert_disclosures(self, disclosures: Iterable[Disclosure]) -> None:
        with self.conn.cursor() as cur:
            for item in disclosures:
                cur.execute(
                    "INSERT INTO disclosures(id,symbol,title,category,published_at,url,source) VALUES(%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(id) DO NOTHING",
                    (item.id, item.symbol, item.title, item.category, item.published_at, item.url, item.source),
                )

    def recent_disclosures(self, limit: int = 20) -> list[Disclosure]:
        rows = self._execute("SELECT * FROM disclosures ORDER BY published_at DESC LIMIT %s", (limit,)).fetchall()
        return [Disclosure(row["id"], row["symbol"], row["title"], row["category"], str(row["published_at"]), row.get("url"), row["source"]) for row in rows]

    def watchlist(self, user_id: str) -> list[str]:
        return [row["symbol"] for row in self._execute("SELECT symbol FROM watchlists WHERE user_id=%s ORDER BY symbol", (user_id,)).fetchall()]

    def add_watch(self, user_id: str, symbol: str) -> None:
        self.create_user(user_id)
        self._execute("INSERT INTO watchlists(user_id,symbol,created_at) VALUES(%s,%s,%s) ON CONFLICT(user_id,symbol) DO NOTHING", (user_id, symbol, utc_now()))

    def remove_watch(self, user_id: str, symbol: str) -> None:
        self._execute("DELETE FROM watchlists WHERE user_id=%s AND symbol=%s", (user_id, symbol))

    def upsert_holding(self, holding: Holding) -> None:
        self.create_user(holding.user_id)
        self._execute(
            """
            INSERT INTO holdings(user_id,symbol,quantity,average_cost,created_at) VALUES(%s,%s,%s,%s,%s)
            ON CONFLICT(user_id,symbol) DO UPDATE SET quantity=EXCLUDED.quantity, average_cost=EXCLUDED.average_cost
            """,
            (holding.user_id, holding.symbol, holding.quantity, holding.average_cost, holding.created_at),
        )

    def list_holdings(self, user_id: str) -> list[Holding]:
        rows = self._execute("SELECT * FROM holdings WHERE user_id=%s ORDER BY symbol", (user_id,)).fetchall()
        return [Holding(row["user_id"], row["symbol"], float(row["quantity"]), float(row["average_cost"]), str(row["created_at"])) for row in rows]

    def portfolio_summary(self, user_id: str) -> PortfolioSummary:
        snapshots = self.latest_snapshots()
        positions: list[PortfolioPosition] = []
        for holding in self.list_holdings(user_id):
            current = snapshots.get(holding.symbol)
            price = current.price if current else holding.average_cost
            cost = holding.quantity * holding.average_cost
            value = holding.quantity * price
            pnl = value - cost
            pnl_pct = (pnl / cost * 100) if cost else 0.0
            positions.append(PortfolioPosition(holding.symbol, holding.quantity, holding.average_cost, price, value, cost, pnl, pnl_pct))
        total_value = sum(item.market_value for item in positions)
        total_cost = sum(item.cost_basis for item in positions)
        pnl = total_value - total_cost
        pnl_pct = (pnl / total_cost * 100) if total_cost else 0.0
        return PortfolioSummary(user_id, total_value, total_cost, pnl, pnl_pct, positions)

    def upsert_rules(self, rules: Iterable[AlertRule]) -> None:
        with self.conn.cursor() as cur:
            for rule in rules:
                cur.execute(
                    """
                    INSERT INTO alert_rules(id,user_id,symbol,type,target,status,channels_json,note,armed,fire_count,cooldown_minutes,last_fired_at,keyword,created_at)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT(id) DO UPDATE SET user_id=EXCLUDED.user_id, symbol=EXCLUDED.symbol, type=EXCLUDED.type, target=EXCLUDED.target,
                    status=EXCLUDED.status, channels_json=EXCLUDED.channels_json, note=EXCLUDED.note, armed=EXCLUDED.armed,
                    fire_count=EXCLUDED.fire_count, cooldown_minutes=EXCLUDED.cooldown_minutes, last_fired_at=EXCLUDED.last_fired_at, keyword=EXCLUDED.keyword
                    """,
                    (rule.id, rule.user_id, rule.symbol, rule.type.value, rule.target, rule.status.value, json.dumps([channel.value for channel in rule.channels]), rule.note, rule.armed, rule.fire_count, rule.cooldown_minutes, rule.last_fired_at, rule.keyword, rule.created_at),
                )

    def list_rules(self, user_id: str | None = None, active_only: bool = False) -> list[AlertRule]:
        query = "SELECT * FROM alert_rules"
        clauses: list[str] = []
        args: list[Any] = []
        if user_id:
            clauses.append("user_id=%s")
            args.append(user_id)
        if active_only:
            clauses.append("status='active'")
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at DESC"
        return [self._row_to_rule(row) for row in self._execute(query, tuple(args)).fetchall()]

    def _row_to_rule(self, row: dict[str, Any]) -> AlertRule:
        return AlertRule(row["id"], row["user_id"], row["symbol"], AlertType(row["type"]), float(row["target"]), AlertStatus(row["status"]), [DeliveryChannel(item) for item in json.loads(row["channels_json"])], row["note"], bool(row["armed"]), int(row["fire_count"]), int(row["cooldown_minutes"]), str(row["last_fired_at"]) if row["last_fired_at"] else None, row.get("keyword"), str(row["created_at"]))

    def insert_events(self, events: Iterable[AlertEvent]) -> None:
        with self.conn.cursor() as cur:
            for item in events:
                cur.execute(
                    "INSERT INTO alert_events(id,rule_id,user_id,symbol,type,reason,message,severity,price,change_percent,metadata_json,created_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT(id) DO NOTHING",
                    (item.id, item.rule_id, item.user_id, item.symbol, item.type.value, item.reason, item.message, item.severity, item.price, item.change_percent, json.dumps(item.metadata), item.created_at),
                )

    def list_events(self, user_id: str | None = None, limit: int = 50) -> list[AlertEvent]:
        if user_id:
            rows = self._execute("SELECT * FROM alert_events WHERE user_id=%s ORDER BY created_at DESC LIMIT %s", (user_id, limit)).fetchall()
        else:
            rows = self._execute("SELECT * FROM alert_events ORDER BY created_at DESC LIMIT %s", (limit,)).fetchall()
        return [self._row_to_event(row) for row in rows]

    def _row_to_event(self, row: dict[str, Any]) -> AlertEvent:
        return AlertEvent(row["id"], row["rule_id"], row["user_id"], row["symbol"], AlertType(row["type"]), row["reason"], row["message"], row["severity"], float(row["price"]) if row["price"] is not None else None, float(row["change_percent"]) if row["change_percent"] is not None else None, json.loads(row["metadata_json"]), str(row["created_at"]))

    def log_delivery(self, event_id: str, channel: str, ok: bool, detail: str, latency_ms: float | None = None) -> None:
        self._execute("INSERT INTO delivery_log(event_id,channel,ok,detail,latency_ms,created_at) VALUES(%s,%s,%s,%s,%s,%s)", (event_id, channel, ok, detail[:500], latency_ms, utc_now()))

    def add_dead_letter(self, source: str, payload: dict[str, object], error: str) -> None:
        self._execute("INSERT INTO dead_letters(source,payload_json,error,created_at) VALUES(%s,%s,%s,%s)", (source, json.dumps(payload), error[:500], utc_now()))

    def delivery_stats(self) -> dict[str, object]:
        row = self._execute("SELECT COUNT(*) AS total, SUM(CASE WHEN ok THEN 1 ELSE 0 END) AS ok FROM delivery_log").fetchone()
        total = int(row["total"] or 0)
        ok = int(row["ok"] or 0)
        failed = total - ok
        lat = self._execute("SELECT AVG(latency_ms) AS avg_latency_ms FROM delivery_log WHERE latency_ms IS NOT NULL").fetchone()
        dead = self._execute("SELECT COUNT(*) AS total FROM dead_letters").fetchone()
        return {"total_deliveries": total, "successful_deliveries": ok, "failed_deliveries": failed, "success_rate": round(ok / total * 100, 2) if total else 100.0, "average_latency_ms": round(float(lat["avg_latency_ms"] or 0), 2), "dead_letters": int(dead["total"] or 0)}

    def set_state(self, key: str, value: str) -> None:
        self._execute("INSERT INTO system_state(key,value,updated_at) VALUES(%s,%s,%s) ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value, updated_at=EXCLUDED.updated_at", (key, value, utc_now()))

    def get_state(self, key: str, default: str = "") -> str:
        row = self._execute("SELECT value FROM system_state WHERE key=%s", (key,)).fetchone()
        return row["value"] if row else default
