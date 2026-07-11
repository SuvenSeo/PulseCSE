# Backend Hardening Notes

PulseCSE Pro v4 is designed as a production-style personal project rather than a coursework prototype.

## Reliability

- Polling is controlled by market-hours configuration and jitter to avoid fixed thundering-herd intervals.
- Alert events use deterministic fingerprints to avoid duplicate event spam.
- Rules disarm after firing and re-arm only when conditions reset.
- Delivery attempts are logged with success/failure and latency.
- Dead-letter storage exists for future adapter/parser failure capture.

## Observability

- JSON logs are emitted for ticks and deliveries.
- `/health` returns status, market window, database mode, last tick, and delivery health.
- `/metrics` returns JSON metrics.
- `/metrics.prom` returns scrape-friendly text metrics.

## Storage

- SQLite mode is for fast local demos.
- Postgres mode uses SQL migrations under `db/migrations/postgres`.
- CI includes a Postgres service job that applies migrations, seeds data, runs a tick, and API-smokes health/metrics.

## Security and product safety

- Secrets are environment variables only.
- `.env` is not committed.
- Live market access is behind an adapter boundary.
- The README states that the system is informational and not financial advice.
