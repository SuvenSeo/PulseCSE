from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from pulsecse.core.models import (
    AlertEvent,
    AlertRule,
    AlertStatus,
    AlertType,
    DeliveryChannel,
    Disclosure,
    Stock,
    StockSnapshot,
    utc_now,
)

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS stocks (
  symbol TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  sector TEXT NOT NULL,
  board TEXT NOT NULL,
  isin TEXT
);
CREATE TABLE IF NOT EXISTS snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  symbol TEXT NOT NULL,
  price REAL NOT NULL,
  previous_close REAL NOT NULL,
  volume INTEGER NOT NULL,
  previous_volume INTEGER NOT NULL,
  high REAL NOT NULL,
  low REAL NOT NULL,
  market_time TEXT NOT NULL,
  source TEXT NOT NULL,
  UNIQUE(symbol, market_time, source)
);
CREATE TABLE IF NOT EXISTS disclosures (
  id TEXT PRIMARY KEY,
  symbol TEXT NOT NULL,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  published_at TEXT NOT NULL,
  url TEXT,
  source TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS watchlists (
  user_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY(user_id, symbol)
);
CREATE TABLE IF NOT EXISTS alert_rules (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  type TEXT NOT NULL,
  target REAL NOT NULL,
  status TEXT NOT NULL,
  channels_json TEXT NOT NULL,
  note TEXT NOT NULL,
  armed INTEGER NOT NULL,
  fire_count INTEGER NOT NULL,
  cooldown_minutes INTEGER NOT NULL,
  last_fired_at TEXT,
  keyword TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS alert_events (
  id TEXT PRIMARY KEY,
  rule_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  type TEXT NOT NULL,
  reason TEXT NOT NULL,
  message TEXT NOT NULL,
  severity TEXT NOT NULL,
  price REAL,
  change_percent REAL,
  metadata_json TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS delivery_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL,
  channel TEXT NOT NULL,
  ok INTEGER NOT NULL,
  detail TEXT NOT NULL,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS system_state (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
"""


class SQLiteRepository:
    def __init__(self, path: str | Path = "pulsecse.sqlite3") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def upsert_stocks(self, stocks: Iterable[Stock]) -> None:
        self.conn.executemany(
            "INSERT INTO stocks(symbol,name,sector,board,isin) VALUES(?,?,?,?,?) "
            "ON CONFLICT(symbol) DO UPDATE SET name=excluded.name, sector=excluded.sector, board=excluded.board, isin=excluded.isin",
            [(item.symbol, item.name, item.sector, item.board, item.isin) for item in stocks],
        )
        self.conn.commit()

    def list_stocks(self) -> list[Stock]:
        rows = self.conn.execute("SELECT * FROM stocks ORDER BY symbol").fetchall()
        return [Stock(row["symbol"], row["name"], row["sector"], row["board"], row["isin"]) for row in rows]

    def insert_snapshots(self, snapshots: Iterable[StockSnapshot]) -> None:
        self.conn.executemany(
            "INSERT OR IGNORE INTO snapshots(symbol,price,previous_close,volume,previous_volume,high,low,market_time,source) VALUES(?,?,?,?,?,?,?,?,?)",
            [
                (
                    item.symbol,
                    item.price,
                    item.previous_close,
                    item.volume,
                    item.previous_volume,
                    item.high,
                    item.low,
                    item.market_time,
                    item.source,
                )
                for item in snapshots
            ],
        )
        self.conn.commit()

    def latest_snapshots(self) -> dict[str, StockSnapshot]:
        rows = self.conn.execute(
            """
            SELECT s.* FROM snapshots s
            JOIN (SELECT symbol, MAX(id) AS max_id FROM snapshots GROUP BY symbol) latest
              ON s.symbol = latest.symbol AND s.id = latest.max_id
            ORDER BY s.symbol
            """
        ).fetchall()
        return {
            row["symbol"]: StockSnapshot(
                symbol=row["symbol"],
                price=row["price"],
                previous_close=row["previous_close"],
                volume=row["volume"],
                previous_volume=row["previous_volume"],
                high=row["high"],
                low=row["low"],
                market_time=row["market_time"],
                source=row["source"],
            )
            for row in rows
        }

    def price_history(self, symbol: str, limit: int = 40) -> list[float]:
        rows = self.conn.execute(
            "SELECT price FROM snapshots WHERE symbol=? ORDER BY id DESC LIMIT ?",
            (symbol, limit),
        ).fetchall()
        return [row["price"] for row in reversed(rows)]

    def insert_disclosures(self, disclosures: Iterable[Disclosure]) -> None:
        self.conn.executemany(
            "INSERT OR IGNORE INTO disclosures(id,symbol,title,category,published_at,url,source) VALUES(?,?,?,?,?,?,?)",
            [(item.id, item.symbol, item.title, item.category, item.published_at, item.url, item.source) for item in disclosures],
        )
        self.conn.commit()

    def recent_disclosures(self, limit: int = 20) -> list[Disclosure]:
        rows = self.conn.execute("SELECT * FROM disclosures ORDER BY published_at DESC LIMIT ?", (limit,)).fetchall()
        return [Disclosure(row["id"], row["symbol"], row["title"], row["category"], row["published_at"], row["url"], row["source"]) for row in rows]

    def watchlist(self, user_id: str) -> list[str]:
        rows = self.conn.execute("SELECT symbol FROM watchlists WHERE user_id=? ORDER BY symbol", (user_id,)).fetchall()
        return [row["symbol"] for row in rows]

    def add_watch(self, user_id: str, symbol: str) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO watchlists(user_id,symbol,created_at) VALUES(?,?,?)",
            (user_id, symbol, utc_now()),
        )
        self.conn.commit()

    def remove_watch(self, user_id: str, symbol: str) -> None:
        self.conn.execute("DELETE FROM watchlists WHERE user_id=? AND symbol=?", (user_id, symbol))
        self.conn.commit()

    def upsert_rules(self, rules: Iterable[AlertRule]) -> None:
        self.conn.executemany(
            """
            INSERT INTO alert_rules(id,user_id,symbol,type,target,status,channels_json,note,armed,fire_count,cooldown_minutes,last_fired_at,keyword,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
              user_id=excluded.user_id, symbol=excluded.symbol, type=excluded.type, target=excluded.target,
              status=excluded.status, channels_json=excluded.channels_json, note=excluded.note, armed=excluded.armed,
              fire_count=excluded.fire_count, cooldown_minutes=excluded.cooldown_minutes, last_fired_at=excluded.last_fired_at,
              keyword=excluded.keyword
            """,
            [self._rule_tuple(rule) for rule in rules],
        )
        self.conn.commit()

    def _rule_tuple(self, rule: AlertRule) -> tuple:
        return (
            rule.id,
            rule.user_id,
            rule.symbol,
            rule.type.value,
            rule.target,
            rule.status.value,
            json.dumps([channel.value for channel in rule.channels]),
            rule.note,
            1 if rule.armed else 0,
            rule.fire_count,
            rule.cooldown_minutes,
            rule.last_fired_at,
            rule.keyword,
            rule.created_at,
        )

    def list_rules(self, user_id: str | None = None, active_only: bool = False) -> list[AlertRule]:
        query = "SELECT * FROM alert_rules"
        clauses: list[str] = []
        args: list[object] = []
        if user_id:
            clauses.append("user_id=?")
            args.append(user_id)
        if active_only:
            clauses.append("status='active'")
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY created_at DESC"
        rows = self.conn.execute(query, args).fetchall()
        return [self._row_to_rule(row) for row in rows]

    def _row_to_rule(self, row: sqlite3.Row) -> AlertRule:
        channels = [DeliveryChannel(item) for item in json.loads(row["channels_json"])]
        return AlertRule(
            id=row["id"],
            user_id=row["user_id"],
            symbol=row["symbol"],
            type=AlertType(row["type"]),
            target=row["target"],
            status=AlertStatus(row["status"]),
            channels=channels,
            note=row["note"],
            armed=bool(row["armed"]),
            fire_count=row["fire_count"],
            cooldown_minutes=row["cooldown_minutes"],
            last_fired_at=row["last_fired_at"],
            keyword=row["keyword"],
            created_at=row["created_at"],
        )

    def insert_events(self, events: Iterable[AlertEvent]) -> None:
        self.conn.executemany(
            "INSERT OR IGNORE INTO alert_events(id,rule_id,user_id,symbol,type,reason,message,severity,price,change_percent,metadata_json,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    item.id,
                    item.rule_id,
                    item.user_id,
                    item.symbol,
                    item.type.value,
                    item.reason,
                    item.message,
                    item.severity,
                    item.price,
                    item.change_percent,
                    json.dumps(item.metadata),
                    item.created_at,
                )
                for item in events
            ],
        )
        self.conn.commit()

    def list_events(self, user_id: str | None = None, limit: int = 50) -> list[AlertEvent]:
        if user_id:
            rows = self.conn.execute("SELECT * FROM alert_events WHERE user_id=? ORDER BY created_at DESC LIMIT ?", (user_id, limit)).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM alert_events ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [self._row_to_event(row) for row in rows]

    def _row_to_event(self, row: sqlite3.Row) -> AlertEvent:
        return AlertEvent(
            id=row["id"],
            rule_id=row["rule_id"],
            user_id=row["user_id"],
            symbol=row["symbol"],
            type=AlertType(row["type"]),
            reason=row["reason"],
            message=row["message"],
            severity=row["severity"],
            price=row["price"],
            change_percent=row["change_percent"],
            metadata=json.loads(row["metadata_json"]),
            created_at=row["created_at"],
        )

    def log_delivery(self, event_id: str, channel: str, ok: bool, detail: str) -> None:
        self.conn.execute(
            "INSERT INTO delivery_log(event_id,channel,ok,detail,created_at) VALUES(?,?,?,?,?)",
            (event_id, channel, 1 if ok else 0, detail[:500], utc_now()),
        )
        self.conn.commit()

    def set_state(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO system_state(key,value,updated_at) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
            (key, value, utc_now()),
        )
        self.conn.commit()

    def get_state(self, key: str, default: str = "") -> str:
        row = self.conn.execute("SELECT value FROM system_state WHERE key=?", (key,)).fetchone()
        return row["value"] if row else default
