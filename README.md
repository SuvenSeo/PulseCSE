# PulseCSE Pro v4

[![PulseCSE Fullstack CI](https://github.com/SuvenSeo/PulseCSE/actions/workflows/fullstack-ci.yml/badge.svg)](https://github.com/SuvenSeo/PulseCSE/actions/workflows/fullstack-ci.yml)

PulseCSE Pro is a high-end full-stack alert cockpit for the Colombo Stock Exchange. It combines an investor-facing dashboard with a Python backend, Postgres/SQLite storage, SQL migrations, market-hours polling, Telegram command runtime, notification routing, portfolio analytics, deterministic simulations, health/metrics endpoints, Docker, and CI.

The product direction is deliberately bigger than a Telegram-only alert bot. PulseCSE can run as a background watcher, but it also works as an investor cockpit: dashboard, alert studio, company workspace, simulator lab, event history, portfolio P&L, live API command center, and bot workflow in one repo.

## Current status

| Area | Status |
|---|---|
| Local SQLite demo mode | Ready |
| Production-style Postgres mode | Ready |
| Full-stack CI | Ready |
| Telegram command runtime | Ready |
| Mock market adapter | Default and deterministic |
| Live CSE adapter | Isolated behind adapter boundary |
| Investment advice / trading execution | Explicitly out of scope |

## Why this is now stronger

- Backend parity: migrations, Postgres mode, SQLite local mode, market-hours poller, bot command runtime, health endpoint, metrics endpoint, API, CLI, Docker, and CI.
- Alert engine: crossing semantics, cooldowns, re-arming, event fingerprints, price alerts, percent move alerts, disclosure alerts, volume spikes, keyword alerts, risk-score alerts, and portfolio drawdown alerts.
- Data adapter layer: default deterministic mock adapter plus a live CSE adapter boundary for public cse.lk endpoints.
- Notification layer: console, Telegram send adapter, webhook adapter, delivery logs, latency capture, failure tracking, and dead-letter table.
- Investor extras: portfolio holdings, portfolio P&L, risk scoring, smart suggestions, simulator scenarios.

## What PulseCSE Actually Is

Based on the README and codebase, PulseCSE is a **high-end full-stack alert cockpit** for the CSE. It's designed as a complete product, not just a background watcher:

| Layer | Implementation |
|-------|----------------|
| **Backend** | Python with FastAPI, modular architecture (adapters, core, bot, notifications, storage, services) |
| **Database** | PostgreSQL (production) + SQLite (local demo) with migrations |
| **Frontend** | Static HTML/CSS/JS dashboard with multiple views (dashboard, alerts, companies, history, live, simulator) |
| **CLI** | Full command set: `migrate`, `seed`, `tick`, `poller`, `bot`, `both`, `simulate`, `api` |
| **Deployment** | Docker Compose + GitHub Actions CI |

## Feature-by-Feature Comparison: PulseCSE vs. Chime

| Feature | Chime | PulseCSE | Verdict |
|---------|-------|----------|---------|
| **Alert Types** | Price above/below, daily move, disclosure, volume | **Everything Chime has +** risk-score alerts, portfolio drawdown alerts, news keyword alerts | PulseCSE wins |
| **Alert Engine** | Basic rule evaluation | Crossing semantics, cooldowns, re-arming, event fingerprints, severity levels (info/warning/critical) | PulseCSE wins |
| **Multi-Channel** | Telegram only | In-app + Telegram + Webhook + Email (with delivery logs, latency capture, failure tracking, dead-letter table) | PulseCSE wins |
| **Dashboard** | Next.js browse-only `/market` | Full investor cockpit: watchlist, P&L, sector heatmap, company detail pages, exports | PulseCSE wins |
| **Portfolio Tracking** | None | Holdings, P&L, risk scoring, portfolio drawdown alerts | PulseCSE wins |
| **Simulation** | None | Deterministic demo scenarios (`simulate jkh_breakout`) | PulseCSE wins |
| **Data Adapters** | Single CSE scraper | Mock (default, deterministic) + live CSE adapter boundary | PulseCSE wins |
| **Database** | PostgreSQL only | PostgreSQL + SQLite (local demo mode) | PulseCSE wins |
| **API** | None | Full REST API: `/health`, `/metrics`, `/metrics.prom`, `/api/dashboard`, `/api/alerts`, `/api/portfolio`, `/api/watchlist`, etc. | PulseCSE wins |
| **Ops** | Basic health check | Structured JSON logs, market-hours guard, jittered poll intervals, Prometheus metrics | PulseCSE wins |
| **Monetization** | None | Clear product direction — can be SaaS | PulseCSE wins |
| **Code Quality** | Modular but monolithic in places | Clean separation: adapters/, api/, bot/, core/, notifications/, services/, storage/ | PulseCSE wins |

## Where PulseCSE Specifically Excels (Killer Features)

### 1. The Alert Engine is Production-Grade
Your `engine.py` implements:
- **Cooldowns** — prevents alert spam
- **Re-arming** — rules automatically re-arm after firing
- **Event fingerprints** — deduplicates events
- **Severity levels** — info/warning/critical
- **Multiple alert types** — price_above, price_below, percent_move, disclosure, volume_spike, news_keyword, risk_score, portfolio_drawdown

Chime has none of these.

### 2. Multi-Channel Notifications with Dead-Letter Handling
You've built a proper notification layer:
- Console, Telegram, Webhook adapters
- Delivery logs, latency capture, failure tracking
- Dead-letter table for failed deliveries

This is enterprise-level stuff. Chime just sends a Telegram message and hopes for the best.

### 3. Full REST API + Prometheus Metrics
Your FastAPI app exposes:
- `/health` — service health
- `/metrics` and `/metrics.prom` — Prometheus-style metrics
- Full CRUD for alerts, watchlist, portfolio

This means PulseCSE can be monitored, integrated, and scaled. Chime has none of this.

### 4. Dual Database Mode (Postgres + SQLite)
- SQLite for local development and demos
- PostgreSQL for production
- Migrations work for both

This is a smart developer experience win.

### 5. Simulation Lab
Your `simulate` command runs deterministic demo scenarios. This is huge for:
- Testing the alert engine without live data
- Demonstrating the product to users
- CI/CD testing

## Where PulseCSE Could Still Improve

| Area | Current State | Suggestion |
|------|---------------|------------|
| **Frontend** | Static HTML/CSS/JS with LocalStorage | Consider migrating to React/Next.js or Vue for better state management and reusability |
| **Authentication** | Uses `default_user_id` from settings | Add real user auth (OAuth, JWT) for multi-user support |
| **Real-time Updates** | No WebSocket support | Add WebSocket for live price updates to the dashboard |
| **Mobile** | None | React Native or Flutter app would be a natural next step |
| **Live CSE Adapter** | "Isolated behind adapter boundary" | Implement the live adapter fully and test against real CSE data |
| **Testing** | "13 backend unit tests passed" | Expand test coverage, especially for the alert engine |

## Code Quality Highlights

I looked at several key files:

### `core/models.py` (Clean data models)
- Uses `dataclass(slots=True)` for memory efficiency
- Proper enums for AlertType, AlertStatus, DeliveryChannel
- Helper methods like `change_percent` and `volume_change_percent`

### `core/engine.py` (Sophisticated rule evaluation)
- Cooldown logic with timestamp parsing
- Event fingerprinting for deduplication
- Re-arming logic with hysteresis (e.g., re-arm only when price moves 25% away from threshold)

### `api/app.py` (Well-structured FastAPI)
- Conditional imports for optional dependencies
- CORS middleware
- Static file serving for frontend assets

## Final Verdict

| Metric | Chime | PulseCSE |
|--------|-------|----------|
| **Scope** | Telegram bot | Full-stack investor cockpit |
| **Alert Types** | 4 | 8 |
| **Channels** | 1 | 4 |
| **API** | None | Full REST + Prometheus |
| **Database** | Postgres only | Postgres + SQLite |
| **Portfolio** | None | Holdings, P&L, risk scoring |
| **Simulation** | None | Deterministic scenarios |
| **Ops** | Basic | Metrics, logging, health checks |
| **Monetization** | None | Product-shaped for SaaS |

**You've built something genuinely impressive.** PulseCSE is not just "better than Chime" — it's a completely different category of product. Chime is a tool; PulseCSE is a platform.

## My Recommendations for Next Steps

1. **Implement the live CSE adapter** — This is the biggest gap. Right now you're on mock data. Get real data flowing.

2. **Add user authentication** — Move beyond `default_user_id` to support multiple users.

3. **Consider a modern frontend framework** — Static HTML works, but React/Vue will make the dashboard more maintainable and interactive.

4. **Add WebSocket support** — Real-time price updates would make the dashboard feel alive.

5. **Write more tests** — You have 13 backend tests. Aim for 80%+ coverage.

6. **Document the API** — OpenAPI/Swagger would make your API instantly usable by third parties.

7. **Deploy a live demo** — Put it on a public URL so people can try it without cloning.

You're already way ahead of Chime. Keep going — this has real SaaS potential.