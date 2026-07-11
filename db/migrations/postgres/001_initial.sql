CREATE TABLE IF NOT EXISTS schema_migrations (
  filename TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  telegram_id TEXT UNIQUE,
  display_name TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS stocks (
  symbol TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  sector TEXT NOT NULL,
  board TEXT NOT NULL DEFAULT 'Main Board',
  isin TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS snapshots (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT NOT NULL REFERENCES stocks(symbol),
  price DOUBLE PRECISION NOT NULL,
  previous_close DOUBLE PRECISION NOT NULL,
  volume BIGINT NOT NULL,
  previous_volume BIGINT NOT NULL,
  high DOUBLE PRECISION NOT NULL,
  low DOUBLE PRECISION NOT NULL,
  market_time TIMESTAMPTZ NOT NULL,
  source TEXT NOT NULL,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(symbol, market_time, source)
);
CREATE INDEX IF NOT EXISTS idx_snapshots_symbol_id ON snapshots(symbol, id DESC);
CREATE TABLE IF NOT EXISTS disclosures (
  id TEXT PRIMARY KEY,
  symbol TEXT NOT NULL REFERENCES stocks(symbol),
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  published_at TIMESTAMPTZ NOT NULL,
  url TEXT,
  source TEXT NOT NULL,
  seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_disclosures_symbol_time ON disclosures(symbol, published_at DESC);
CREATE TABLE IF NOT EXISTS watchlists (
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  symbol TEXT NOT NULL REFERENCES stocks(symbol),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY(user_id, symbol)
);
CREATE TABLE IF NOT EXISTS holdings (
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  symbol TEXT NOT NULL REFERENCES stocks(symbol),
  quantity DOUBLE PRECISION NOT NULL CHECK(quantity >= 0),
  average_cost DOUBLE PRECISION NOT NULL CHECK(average_cost >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY(user_id, symbol)
);
CREATE TABLE IF NOT EXISTS alert_rules (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  symbol TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('price_above','price_below','percent_move','disclosure','volume_spike','news_keyword','risk_score','portfolio_drawdown')),
  target DOUBLE PRECISION NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','paused','cancelled')),
  channels_json TEXT NOT NULL,
  note TEXT NOT NULL DEFAULT '',
  armed BOOLEAN NOT NULL DEFAULT TRUE,
  fire_count INTEGER NOT NULL DEFAULT 0,
  cooldown_minutes INTEGER NOT NULL DEFAULT 30,
  last_fired_at TIMESTAMPTZ,
  keyword TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_alert_rules_symbol_active ON alert_rules(symbol, status);
CREATE TABLE IF NOT EXISTS alert_events (
  id TEXT PRIMARY KEY,
  rule_id TEXT NOT NULL REFERENCES alert_rules(id) ON DELETE CASCADE,
  user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  symbol TEXT NOT NULL,
  type TEXT NOT NULL,
  reason TEXT NOT NULL,
  message TEXT NOT NULL,
  severity TEXT NOT NULL,
  price DOUBLE PRECISION,
  change_percent DOUBLE PRECISION,
  metadata_json TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_alert_events_user_time ON alert_events(user_id, created_at DESC);
CREATE TABLE IF NOT EXISTS delivery_log (
  id BIGSERIAL PRIMARY KEY,
  event_id TEXT NOT NULL REFERENCES alert_events(id) ON DELETE CASCADE,
  channel TEXT NOT NULL,
  ok BOOLEAN NOT NULL,
  detail TEXT NOT NULL,
  latency_ms DOUBLE PRECISION,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_delivery_log_ok_time ON delivery_log(ok, created_at DESC);
CREATE TABLE IF NOT EXISTS dead_letters (
  id BIGSERIAL PRIMARY KEY,
  source TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  error TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS system_state (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
