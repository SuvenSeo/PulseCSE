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

    def get_user(self, user_id: str) -> dict[str, Any]:
        result = self._execute("SELECT * FROM users WHERE id = %s", (user_id,)).fetchone()
        return result if result else {}

    def create_alert_rule(self, alert_rule: AlertRule) -> None:
        self._execute(
            "INSERT INTO alert_rules(id,user_id,alert_type,stock_symbol,condition,threshold,created_at) VALUES(%s,%s,%s,%s,%s,%s,%s)",
            (
                alert_rule.id,
                alert_rule.user_id,
                alert_rule.alert_type,
                alert_rule.stock_symbol,
                alert_rule.condition,
                alert_rule.threshold,
                utc_now(),
            ),
        )

    def get_alert_rules(self, user_id: str) -> list[dict[str, Any]]:
        return self._execute("SELECT * FROM alert_rules WHERE user_id = %s", (user_id,)).fetchall()

    def create_alert_event(self, alert_event: AlertEvent) -> None:
        self._execute(
            "INSERT INTO alert_events(id,alert_rule_id,alert_status,created_at) VALUES(%s,%s,%s,%s)",
            (alert_event.id, alert_event.alert_rule_id, alert_event.alert_status, utc_now()),
        )

    def get_alert_events(self, alert_rule_id: str) -> list[dict[str, Any]]:
        return self._execute("SELECT * FROM alert_events WHERE alert_rule_id = %s", (alert_rule_id,)).fetchall()

    def create_stock_snapshot(self, stock_snapshot: StockSnapshot) -> None:
        self._execute(
            "INSERT INTO stock_snapshots(id,stock_symbol,price,created_at) VALUES(%s,%s,%s,%s)",
            (stock_snapshot.id, stock_snapshot.stock_symbol, stock_snapshot.price, utc_now()),
        )

    def get_stock_snapshots(self, stock_symbol: str) -> list[dict[str, Any]]:
        return self._execute("SELECT * FROM stock_snapshots WHERE stock_symbol = %s", (stock_symbol,)).fetchall()

    def create_portfolio_position(self, portfolio_position: PortfolioPosition) -> None:
        self._execute(
            "INSERT INTO portfolio_positions(id,user_id,stock_symbol,quantity,created_at) VALUES(%s,%s,%s,%s,%s)",
            (portfolio_position.id, portfolio_position.user_id, portfolio_position.stock_symbol, portfolio_position.quantity, utc_now()),
        )

    def get_portfolio_positions(self, user_id: str) -> list[dict[str, Any]]:
        return self._execute("SELECT * FROM portfolio_positions WHERE user_id = %s", (user_id,)).fetchall()

    def create_portfolio_summary(self, portfolio_summary: PortfolioSummary) -> None:
        self._execute(
            "INSERT INTO portfolio_summaries(id,user_id,cash_balance,stock_value,created_at) VALUES(%s,%s,%s,%s,%s)",
            (portfolio_summary.id, portfolio_summary.user_id, portfolio_summary.cash_balance, portfolio_summary.stock_value, utc_now()),
        )

    def get_portfolio_summary(self, user_id: str) -> dict[str, Any]:
        result = self._execute("SELECT * FROM portfolio_summaries WHERE user_id = %s", (user_id,)).fetchone()
        return result if result else {}

    def create_disclosure(self, disclosure: Disclosure) -> None:
        self._execute(
            "INSERT INTO disclosures(id,stock_symbol,company_name,reporting_owner,relationship,transaction_date,transaction_type,ownership_type,shares_owned,price_per_share,shares_change,change_percentage,created_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                disclosure.id,
                disclosure.stock_symbol,
                disclosure.company_name,
                disclosure.reporting_owner,
                disclosure.relationship,
                disclosure.transaction_date,
                disclosure.transaction_type,
                disclosure.ownership_type,
                disclosure.shares_owned,
                disclosure.price_per_share,
                disclosure.shares_change,
                disclosure.change_percentage,
                utc_now(),
            ),
        )

    def get_disclosures(self, stock_symbol: str) -> list[dict[str, Any]]:
        return self._execute("SELECT * FROM disclosures WHERE stock_symbol = %s", (stock_symbol,)).fetchall()

    def create_holding(self, holding: Holding) -> None:
        self._execute(
            "INSERT INTO holdings(id,stock_symbol,company_name,market_value,shares_owned,created_at) VALUES(%s,%s,%s,%s,%s,%s)",
            (holding.id, holding.stock_symbol, holding.company_name, holding.market_value, holding.shares_owned, utc_now()),
        )

    def get_holdings(self, user_id: str) -> list[dict[str, Any]]:
        return self._execute("SELECT * FROM holdings WHERE user_id = %s", (user_id,)).fetchall()