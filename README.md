# PulseCSE Pro v4

PulseCSE Pro is a high-end full-stack alert cockpit for the Colombo Stock Exchange. It combines an investor-facing dashboard with a Python backend, Postgres/SQLite storage, SQL migrations, market-hours polling, Telegram command runtime, notification routing, portfolio analytics, deterministic simulations, health/metrics endpoints, Docker, and CI.

The product direction is deliberately bigger than a Telegram-only alert bot. PulseCSE can run as a background watcher, but it also works as an investor cockpit: dashboard, alert studio, company workspace, simulator lab, event history, portfolio P&L, live API command center, and bot workflow in one repo.

## Why this is now stronger

- Backend parity: migrations, Postgres mode, SQLite local mode, market-hours poller, bot command runtime, health endpoint, metrics endpoint, API, CLI, Docker, and CI.
- Alert engine: crossing semantics, cooldowns, re-arming, event fingerprints, price alerts, percent move alerts, disclosure alerts, volume spikes, keyword alerts, risk-score alerts, and portfolio drawdown alerts.
- Data adapter layer: default deterministic mock adapter plus a live CSE adapter boundary for public cse.lk endpoints.
- Notification layer: console, Telegram send adapter, webhook adapter, delivery logs, latency capture, failure tracking, and dead-letter table.
- Investor extras: portfolio holdings, portfolio P&L, risk scoring, smart suggestions, simulator scenarios, sector heatmap, company detail pages, and exports.
- Ops layer: `/health`, `/metrics`, `/metrics.prom`, structured JSON logs, market-hours guard, jittered poll intervals, Docker Compose with Postgres, and GitHub Actions with Postgres integration.

## Quick start: SQLite local mode

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[api]
python -m pulsecse migrate
python -m pulsecse seed
python -m pulsecse api
```

Open:

```text
http://127.0.0.1:8088/live.html
```

## Production-style Postgres mode

```bash
cp .env.example .env
# set PULSECSE_DATABASE=postgresql://pulsecse:pulsecse@localhost:5432/pulsecse
pip install -e .[prod]
python -m pulsecse migrate
python -m pulsecse seed
python -m pulsecse api
```

Docker:

```bash
docker compose up --build
```

## CLI commands

| Command | Purpose |
|---|---|
| `python -m pulsecse migrate` | Apply Postgres migrations or initialize SQLite schema tracking |
| `python -m pulsecse seed` | Seed stocks, snapshots, watchlist, portfolio, and default rules |
| `python -m pulsecse tick --force` | Run one poll/evaluation cycle |
| `python -m pulsecse poller` | Run market-hours polling loop with jitter |
| `python -m pulsecse bot` | Run Telegram long-polling command bot |
| `python -m pulsecse both` | Run bot and poller in one process when Telegram token is configured |
| `python -m pulsecse command /portfolio` | Run one transport-neutral bot command locally |
| `python -m pulsecse simulate jkh_breakout` | Run deterministic demo scenario |
| `python -m pulsecse api` | Start FastAPI backend and serve frontend |

## Telegram commands

```text
/watch SYMBOL
/unwatch SYMBOL
/watchlist or /mywatchlist
/alert SYMBOL TYPE TARGET [keyword]
/alerts or /myalerts
/cancel ALERT_ID
/portfolio
/holding SYMBOL QTY AVG_COST
/events
/help
```

Supported alert types:

```text
price_above, price_below, percent_move, disclosure, volume_spike, news_keyword, risk_score, portfolio_drawdown
```

## API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness, market window, last tick, database mode, delivery health |
| `GET /metrics` | JSON operational metrics |
| `GET /metrics.prom` | Prometheus-style metrics text |
| `GET /api/dashboard` | Full dashboard payload |
| `POST /api/tick?force=true` | Run one market tick and evaluate alerts |
| `POST /api/simulate/{scenario}` | Run deterministic scenario |
| `GET /api/stocks` | Stocks with latest snapshot and risk scores |
| `GET /api/alerts` | List alert rules |
| `POST /api/alerts` | Create alert rule |
| `GET /api/events` | List alert events |
| `GET /api/portfolio` | Portfolio summary and holdings P&L |
| `POST /api/portfolio/holding` | Upsert a holding |
| `POST /api/watchlist/{symbol}` | Add watchlist symbol |
| `DELETE /api/watchlist/{symbol}` | Remove watchlist symbol |

## Quality checks

```bash
npm run fullcheck
```

Current local check result:

```text
Checked 9 HTML files and 13 JavaScript files.
6 frontend alert-engine tests passed.
13 backend unit tests passed.
Python backend compile check passed.
```

## Project structure

```text
backend/pulsecse/
  adapters/          Mock and live CSE market-data adapter boundary
  api/               FastAPI routes, health, metrics, frontend serving
  bot/               Command router and optional Telegram long-polling runtime
  core/              Models, alert engine, analytics, portfolio models
  notifications/     Console, Telegram, webhook delivery adapters
  services/          Market service orchestration
  storage/           SQLite, Postgres, repository factory
  migrate.py         Migration runner
  market_hours.py    Market window and jitter helpers
  poller.py          Market-hours worker loop
  observability.py   Structured JSON logging and timers
db/migrations/       Production Postgres SQL migrations
backend/tests/       Backend unit tests
js/                  Frontend modules and API client
css/                 Responsive premium UI
.github/workflows/   Static, backend, and Postgres CI gates
```

## Disclaimer

PulseCSE Pro is an information and engineering project. It is not investment advice, a broker, a trading terminal, or a guarantee of exchange accuracy. The default provider is mock mode so the project is safe, deterministic, and easy to run locally. Live CSE access is isolated behind an adapter boundary and should be used only with approved/appropriate market-data access.
