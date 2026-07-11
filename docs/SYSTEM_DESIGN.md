# PulseCSE Pro System Design

## Design goal

PulseCSE Pro is designed as a complete stock-alert cockpit rather than a single notification bot. The system separates data acquisition, persistence, rule evaluation, notification delivery, and UI rendering so each part can evolve independently.

## Architecture

```text
Market Adapter -> Market Service -> SQLite Repository -> Alert Engine -> Notification Adapters
                                \-> Dashboard Aggregator -> REST API -> Frontend
```

## Components

### Market adapter

`MockMarketAdapter` provides deterministic market data and scenarios. A future live adapter can be added behind the same boundary without changing the alert engine or UI.

### Repository

`SQLiteRepository` owns all persistence:

- stocks
- snapshots
- disclosures
- watchlists
- alert rules
- alert events
- delivery logs
- system state

SQLite is used because the project can run locally without extra infrastructure. The repository pattern makes it straightforward to swap to Postgres later.

### Alert engine

The engine is pure Python and testable. It supports:

- price-above crossing
- price-below crossing
- percent move
- disclosure
- keyword disclosure
- volume spike
- risk-score threshold
- cooldown enforcement
- re-arming logic
- event fingerprinting

### Market service

`MarketService` orchestrates one tick:

1. Pull snapshots and disclosures from adapter.
2. Persist new data.
3. Calculate risk scores.
4. Evaluate active alert rules.
5. Save updated rule state.
6. Save events.
7. Deliver notifications.
8. Update system health state.

### API

FastAPI exposes dashboard, tick, simulation, alerts, events, and watchlist endpoints. The static frontend can run without the API, but `live.html` connects to the backend for full-stack mode.

## Why this architecture is stronger

The project is no longer just a static prototype. It has production-shaped boundaries: adapters, services, repository, notification delivery, API, CLI, tests, CI, Docker, and docs.
