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

    def get_user(self, user_id: str) -> dict[str, Any] | None:
        result = self._execute("SELECT * FROM users WHERE id = %s", (user_id,)).fetchone()
        return result if result else None

    def create_alert_rule(
        self,
        user_id: str,
        alert_type: AlertType,
        stock_symbol: str,
        threshold: float,
        cooldown_seconds: int,
        delivery_channels: list[DeliveryChannel],
    ) -> None:
        self._execute(
            """
            INSERT INTO alert_rules(
                user_id,
                alert_type,
                stock_symbol,
                threshold,
                cooldown_seconds,
                delivery_channels,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id, stock_symbol, alert_type) DO UPDATE
            SET threshold = EXCLUDED.threshold,
                cooldown_seconds = EXCLUDED.cooldown_seconds,
                delivery_channels = EXCLUDED.delivery_channels
            """,
            (
                user_id,
                alert_type,
                stock_symbol,
                threshold,
                cooldown_seconds,
                json.dumps([channel.value for channel in delivery_channels]),
                utc_now(),
            ),
        )

    def get_alert_rules(self, user_id: str) -> list[dict[str, Any]]:
        return self._execute(
            """
            SELECT
                ar.id,
                ar.user_id,
                ar.alert_type,
                ar.stock_symbol,
                ar.threshold,
                ar.cooldown_seconds,
                ar.delivery_channels,
                ar.created_at
            FROM alert_rules ar
            WHERE ar.user_id = %s
            """,
            (user_id,),
        ).fetchall()

    def create_alert_event(
        self,
        user_id: str,
        alert_rule_id: int,
        stock_symbol: str,
        event_timestamp: int,
        event_data: dict[str, Any],
    ) -> None:
        self._execute(
            """
            INSERT INTO alert_events(
                user_id,
                alert_rule_id,
                stock_symbol,
                event_timestamp,
                event_data,
                created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                alert_rule_id,
                stock_symbol,
                event_timestamp,
                json.dumps(event_data),
                utc_now(),
            ),
        )

    def get_alert_events(self, user_id: str) -> list[dict[str, Any]]:
        return self._execute(
            """
            SELECT
                ae.id,
                ae.user_id,
                ae.alert_rule_id,
                ae.stock_symbol,
                ae.event_timestamp,
                ae.event_data,
                ae.created_at
            FROM alert_events ae
            WHERE ae.user_id = %s
            """,
            (user_id,),
        ).fetchall()

    def create_stock(self, symbol: str, name: str) -> None:
        self._execute(
            "INSERT INTO stocks(symbol, name, created_at) VALUES (%s, %s, %s) ON CONFLICT(symbol) DO NOTHING",
            (symbol, name, utc_now()),
        )

    def get_stock(self, symbol: str) -> dict[str, Any] | None:
        result = self._execute("SELECT * FROM stocks WHERE symbol = %s", (symbol,)).fetchone()
        return result if result else None

    def create_stock_snapshot(self, stock_symbol: str, timestamp: int, price: float) -> None:
        self._execute(
            """
            INSERT INTO stock_snapshots(
                stock_symbol,
                timestamp,
                price,
                created_at
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (stock_symbol, timestamp) DO UPDATE
            SET price = EXCLUDED.price
            """,
            (stock_symbol, timestamp, price, utc_now()),
        )

    def get_stock_snapshots(self, stock_symbol: str) -> list[dict[str, Any]]:
        return self._execute(
            """
            SELECT
                ss.id,
                ss.stock_symbol,
                ss.timestamp,
                ss.price,
                ss.created_at
            FROM stock_snapshots ss
            WHERE ss.stock_symbol = %s
            """,
            (stock_symbol,),
        ).fetchall()

    def create_holding(self, user_id: str, stock_symbol: str, quantity: int) -> None:
        self._execute(
            """
            INSERT INTO holdings(
                user_id,
                stock_symbol,
                quantity,
                created_at
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, stock_symbol) DO UPDATE
            SET quantity = EXCLUDED.quantity
            """,
            (user_id, stock_symbol, quantity, utc_now()),
        )

    def get_holdings(self, user_id: str) -> list[dict[str, Any]]:
        return self._execute(
            """
            SELECT
                h.id,
                h.user_id,
                h.stock_symbol,
                h.quantity,
                h.created_at
            FROM holdings h
            WHERE h.user_id = %s
            """,
            (user_id,),
        ).fetchall()

    def create_portfolio_position(self, user_id: str, stock_symbol: str, market_value: float) -> None:
        self._execute(
            """
            INSERT INTO portfolio_positions(
                user_id,
                stock_symbol,
                market_value,
                created_at
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, stock_symbol) DO UPDATE
            SET market_value = EXCLUDED.market_value
            """,
            (user_id, stock_symbol, market_value, utc_now()),
        )

    def get_portfolio_positions(self, user_id: str) -> list[dict[str, Any]]:
        return self._execute(
            """
            SELECT
                pp.id,
                pp.user_id,
                pp.stock_symbol,
                pp.market_value,
                pp.created_at
            FROM portfolio_positions pp
            WHERE pp.user_id = %s
            """,
            (user_id,),
        ).fetchall()

    def create_portfolio_summary(self, user_id: str, total_value: float) -> None:
        self._execute(
            """
            INSERT INTO portfolio_summaries(
                user_id,
                total_value,
                created_at
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE
            SET total_value = EXCLUDED.total_value
            """,
            (user_id, total_value, utc_now()),
        )

    def get_portfolio_summary(self, user_id: str) -> dict[str, Any] | None:
        result = self._execute("SELECT * FROM portfolio_summaries WHERE user_id = %s", (user_id,)).fetchone()
        return result if result else None