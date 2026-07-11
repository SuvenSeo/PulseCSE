# PulseCSE Pro v4 vs Chime Backend Parity

## Chime capability checklist

| Chime backend capability | PulseCSE Pro v4 status |
|---|---|
| Python package | Implemented |
| PostgreSQL storage | Implemented through `PostgresRepository` and `db/migrations/postgres` |
| Local lightweight DB | SQLite local mode included |
| SQL migrations | Implemented through `python -m pulsecse migrate` |
| Market polling loop | Implemented through `Poller` and `python -m pulsecse poller` |
| Market-hours guard | Implemented with `MarketWindow` and jittered intervals |
| One-shot tick command | Implemented with `python -m pulsecse tick --force` |
| Telegram commands | Implemented with transport-neutral router plus Telegram runtime |
| `/watch`, `/unwatch`, `/alert`, `/cancel`, `/myalerts`, `/mywatchlist`, `/help` | Implemented; aliases included |
| Rule engine crossing semantics | Implemented |
| Re-arming and cooldowns | Implemented |
| Delivery tracking | Implemented with delivery log and latency |
| Health endpoint | Implemented with `/health` plus `/metrics` and `/metrics.prom` |
| Docker Compose Postgres | Implemented |
| CI with frontend/backend checks | Implemented |
| Postgres integration job | Implemented |

## PulseCSE-only additions

- Full investor dashboard, not only a thin management screen.
- Portfolio holdings and P&L analytics.
- Portfolio drawdown alert type.
- Risk score alert type.
- Keyword disclosure alerts.
- Volume spike alerts.
- Deterministic simulation lab.
- Sector heatmap and smart alert suggestions.
- Prometheus-style metrics endpoint.
- Dead-letter table for failed processing paths.
- Static frontend fallback and backend-powered live command center.

## Remaining production notes

- Real CSE endpoint parsing is isolated behind `CSELiveAdapter`; production users should validate endpoint terms, response shapes, and data licensing.
- Telegram runtime requires `python-telegram-bot` and a real bot token.
- Email delivery is represented in the channel model but not implemented as a notifier yet.
