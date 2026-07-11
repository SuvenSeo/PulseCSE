# PulseCSE Pro

PulseCSE Pro is a high-end full-stack alert cockpit for the Colombo Stock Exchange. It combines a polished investor-facing frontend with a Python backend, SQLite persistence, deterministic market simulation, a reusable alert engine, notification adapters, documentation, and CI.

The project is intentionally positioned differently from Telegram-first alert bots. PulseCSE is an **investor cockpit**: a dashboard, alert studio, simulator, company workspace, event history, and backend API in one repo.

## What makes it stronger

- Full frontend product: landing page, dashboard, alert studio, company directory, company detail page, simulator lab, history, and live API command center.
- Full backend product: Python package, API layer, SQLite database, repository pattern, market service, mock market adapter, alert engine, notification pipeline, and CLI commands.
- Serious alert engine: crossing semantics, cooldowns, re-arming, event fingerprints, percent-move alerts, disclosure alerts, volume spikes, keyword alerts, and risk-score alerts.
- Demo-safe market system: deterministic scenarios for breakouts, support breaks, disclosures, volume spikes, and broad market rallies.
- Extensible architecture: adapters isolate market data, storage, notification delivery, and frontend clients.
- CI-ready: frontend static checks, JavaScript tests, Python syntax checks, backend unit tests, Dockerfile, docker-compose, Makefile, and GitHub Actions.

## Run the static frontend only

Open `index.html` directly in your browser, or serve the folder with any static server.

## Run the backend API

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[api]
python -m pulsecse seed
python -m pulsecse api
```

Then open:

```text
http://127.0.0.1:8088/live.html
```

## CLI commands

```bash
python -m pulsecse seed
python -m pulsecse tick
python -m pulsecse simulate jkh_breakout
python -m pulsecse simulate hnb_support_break
python -m pulsecse simulate comb_disclosure
python -m pulsecse simulate dial_volume
python -m pulsecse worker --interval 60
python -m pulsecse api
```

## API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Backend liveness and last tick status |
| `GET /api/dashboard` | Full dashboard payload |
| `POST /api/tick` | Run one market tick and evaluate alerts |
| `POST /api/simulate/{scenario}` | Run deterministic scenario |
| `GET /api/stocks` | List stocks with latest snapshot and risk scores |
| `GET /api/alerts` | List alert rules |
| `POST /api/alerts` | Create alert rule |
| `GET /api/events` | List alert events |
| `POST /api/watchlist/{symbol}` | Add watchlist symbol |
| `DELETE /api/watchlist/{symbol}` | Remove watchlist symbol |

## Testing

```bash
npm run fullcheck
```

Equivalent manual commands:

```bash
npm run check
npm test
PYTHONPATH=backend python -m compileall -q backend
PYTHONPATH=backend python -m unittest discover -s backend/tests
```

## Docker

```bash
docker compose up --build
```

Then open `http://127.0.0.1:8088/live.html`.

## Project structure

```text
backend/pulsecse/
  bot/              Transport-neutral command router
  api/              FastAPI app and REST routes
  adapters/         Market-data adapter boundary and mock market source
  core/             Dataclasses, alert engine, analytics
  notifications/    Console, Telegram, and webhook delivery adapters
  services/         Market tick orchestration and dashboard aggregation
  storage/          SQLite repository and schema
backend/tests/      Backend unit tests
js/                 Static frontend modules and API client
css/                Responsive premium UI styles
docs/               Architecture, runbook, security, roadmap, comparison
.github/workflows/  CI checks
```

## Important disclaimer

PulseCSE Pro is an information and engineering project. It is not investment advice, a broker, a trading terminal, or a guarantee of real-time exchange accuracy. The default market provider is a mock adapter so the project is safe, deterministic, and easy to run locally.
