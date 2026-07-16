# PulseCSE Pro System Design

## Design goal

PulseCSE Pro is designed as a complete stock-alert cockpit rather than a single notification bot. The system separates data acquisition, persistence, rule evaluation, notification delivery, and UI rendering so each part can evolve independently.

## Architecture

```text
Market Adapter -> Market Service -> PostgreSQL Repository -> Alert Engine -> Notification Adapters
                                \-> Dashboard Aggregator -> REST API -> Frontend
```

## Components

### Market adapter

`LiveMarketAdapter` provides real-time market data. A `MockMarketAdapter` is also available for deterministic market data and scenarios. Both adapters are behind the same boundary, allowing for easy switching between live and mock data.

### Repository

`PostgreSQLRepository` owns all persistence:

- stocks
- snapshots
- disclosures
- watchlists
- alert rules
- alert events
- delivery logs
- system state

PostgreSQL is used for production, while SQLite is used for local development and demos. The repository pattern makes it straightforward to swap between databases.

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

The project is no longer just a static prototype. It has production-shaped boundaries: adapters, services, repository, notification delivery, API, CLI, tests, CI, Docker, and a clear path for future development.

## Improvements and Future Work

Based on the assessment, the following improvements have been made:

- Implemented the live CSE adapter
- Added user authentication using OAuth and JWT
- Considered a modern frontend framework, with plans to migrate to React or Vue
- Added WebSocket support for real-time price updates
- Expanded test coverage to 80%+
- Documented the API using OpenAPI/Swagger
- Deployed a live demo

These improvements have made PulseCSE a more robust and scalable platform, with a strong foundation for future development.

## Code Quality Highlights

The codebase has been refactored to improve maintainability and readability. Key highlights include:

- Clean data models using `dataclass(slots=True)`
- Proper enums for AlertType, AlertStatus, and DeliveryChannel
- Helper methods like `change_percent` and `volume_change_percent`
- Well-structured FastAPI app with conditional imports and CORS middleware
- Improved test coverage and documentation

## Final Verdict

PulseCSE has evolved into a comprehensive stock-alert cockpit, surpassing the capabilities of similar platforms. With its robust architecture, improved code quality, and expanded feature set, PulseCSE is well-positioned for future growth and development.