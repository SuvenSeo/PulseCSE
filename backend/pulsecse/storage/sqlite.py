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
    Holding,
    PortfolioPosition,
    PortfolioSummary,
    Stock,
    StockSnapshot,
    utc_now,
)

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS schema_migrations (
  filename TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL
);
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
CREATE INDEX IF NOT EXISTS idx_snapshots_symbol_id ON snapshots(symbol, id DESC);
CREATE TABLE IF NOT EXISTS disclosures (
  id TEXT PRIMARY KEY,
  symbol TEXT NOT NULL,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  published_at TEXT NOT NULL,
  url TEXT,
  source TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_disclosures_symbol_time ON disclosures(symbol, published_at DESC);
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  telegram_id TEXT UNIQUE,
  display_name TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS watchlists (
  user_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY(user_id, symbol),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);
CREATE TABLE IF NOT EXISTS holdings (
  user_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  quantity REAL NOT NULL,
  average_cost REAL NOT NULL,
  created_at TEXT NOT NULL,
  PRIMARY KEY(user_id, symbol),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);
CREATE TABLE IF NOT EXISTS alert_rules (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  alert_type TEXT NOT NULL, -- e.g., PRICE_ABOVE, PRICE_BELOW, VOLUME_ABOVE
  trigger_value REAL NOT NULL,
  status TEXT NOT NULL, -- e.g., ACTIVE, TRIGGERED, INACTIVE
  created_at TEXT NOT NULL,
  updated_at TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);
CREATE TABLE IF NOT EXISTS alert_events (
  id TEXT PRIMARY KEY,
  rule_id TEXT NOT NULL,
  triggered_at TEXT NOT NULL,
  current_value REAL NOT NULL,
  status TEXT NOT NULL, -- e.g., PENDING_DELIVERY, DELIVERED, FAILED
  message TEXT,
  FOREIGN KEY (rule_id) REFERENCES alert_rules(id)
);
CREATE TABLE IF NOT EXISTS delivery_channels (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  channel_type TEXT NOT NULL, -- e.g., TELEGRAM, EMAIL
  identifier TEXT NOT NULL,
  is_active INTEGER NOT NULL DEFAULT 1, -- 0 for false, 1 for true
  created_at TEXT NOT NULL,
  updated_at TEXT,
  UNIQUE(user_id, channel_type, identifier),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS portfolio_positions (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  quantity REAL NOT NULL,
  average_cost REAL NOT NULL,
  current_price REAL NOT NULL, -- Price at the time of this position snapshot
  market_value REAL NOT NULL,
  snapshot_time TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (symbol) REFERENCES stocks(symbol)
);
CREATE TABLE IF NOT EXISTS portfolio_summaries (
  user_id TEXT PRIMARY KEY, -- Assuming one summary per user, user_id acts as PK
  total_value REAL NOT NULL,
  total_cost REAL NOT NULL,
  total_profit_loss REAL NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
"""