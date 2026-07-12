# PulseCSE Deployment Guide

PulseCSE supports three operating modes: local SQLite demo, production-style Postgres, and containerized service deployment.

## 1. Local SQLite demo

Use this for development, classroom/demo walkthroughs, and deterministic testing.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[api]
python -m pulsecse migrate
python -m pulsecse seed
python -m pulsecse api
```

Default URL:

```text
http://127.0.0.1:8088/live.html
```

Recommended `.env` values:

```env
PULSECSE_DATABASE=sqlite:///data/pulsecse.sqlite3
PULSECSE_MARKET_PROVIDER=mock
PULSECSE_HOST=127.0.0.1
PULSECSE_PORT=8088
PULSECSE_LOG_JSON=1
```

## 2. Production-style Postgres

Use this when testing migrations, persistence, and API smoke checks against a real database.

```bash
cp .env.example .env
pip install -e .[prod]
python -m pulsecse migrate
python -m pulsecse seed
python -m pulsecse api
```

Example database value:

```env
PULSECSE_DATABASE=postgresql://pulsecse:pulsecse@localhost:5432/pulsecse
```

## 3. Docker Compose

Use Docker Compose when you want the backend and database lifecycle to be reproducible.

```bash
docker compose up --build
```

Before exposing outside localhost, set real secrets and review:

- `PULSECSE_TELEGRAM_TOKEN`
- `PULSECSE_TELEGRAM_CHAT_ID`
- `PULSECSE_WEBHOOK_URL`
- `PULSECSE_MARKET_PROVIDER`
- `PULSECSE_CSE_BASE_URL`

## Market provider strategy

Default to mock mode unless you have confirmed that your use of live CSE data is allowed.

```env
PULSECSE_MARKET_PROVIDER=mock
```

Live mode should remain a deliberate opt-in:

```env
PULSECSE_MARKET_PROVIDER=cse-live
PULSECSE_CSE_BASE_URL=https://www.cse.lk
```

If the live endpoint changes, the app should fail gracefully through the adapter boundary instead of breaking the alert engine or dashboard.

## Telegram runtime

For a bot-only deployment:

```bash
python -m pulsecse bot
```

For combined bot and poller mode:

```bash
python -m pulsecse both
```

The combined mode is convenient for a small private deployment, but for larger deployments split the API, poller, and bot into separate processes so failures are isolated.

## Operational health checks

Use these endpoints for uptime monitoring:

```text
GET /health
GET /metrics
GET /metrics.prom
```

Minimum production checks:

- API returns `200` from `/health`
- Database mode is the expected mode
- Last successful tick is recent during market hours
- Delivery failure rate is not rising
- Dead-letter count is not growing unexpectedly

## Deployment checklist

- [ ] Use Postgres for persistent deployments.
- [ ] Run `python -m pulsecse migrate` before serving traffic.
- [ ] Use mock provider unless live CSE data access is approved.
- [ ] Keep Telegram/webhook secrets out of Git.
- [ ] Confirm `/health` and `/metrics.prom` after deploy.
- [ ] Run `npm run fullcheck` before release.
- [ ] Enable GitHub branch protection and require full-stack CI.
- [ ] Add a backup strategy for Postgres.
- [ ] Monitor notification delivery failures and dead letters.
