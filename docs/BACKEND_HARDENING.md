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

## Live CSE adapter: verified endpoints

`cse.lk` has no official public API. `CSELiveAdapter` (`backend/pulsecse/adapters/cse_live.py`)
only calls endpoints that were confirmed live via direct `curl` probes (2026-07-12), not guessed:

| Endpoint | Status | Used for |
|---|---|---|
| `POST /api/tradeSummary` | 200, confirmed | stock list + price/volume snapshots (fields: `symbol`, `name`, `price`, `previousClose`, `high`, `low`, `sharevolume`, `lastTradedTime`) |
| `POST /api/approvedAnnouncement` | 200, confirmed | disclosures (fields: `company`, `remarks`, `announcementCategory`, `dateOfAnnouncement`, `announcementId`; `symbol` is almost always `null` on this feed) |
| `POST /api/listedCompanies` | **404, confirmed dead** | not used — `tradeSummary` already carries id/symbol/name for every listed stock |

Because `approvedAnnouncement` rarely returns a `symbol`, disclosure alerts cannot be
symbol-matched from this endpoint alone today; `Disclosure.symbol` will usually be empty
until announcements are resolved against the stock list by issuer name, or the
per-company endpoint (`getAnnouncementByCompany`, `symbol=`) is adopted instead.

This endpoint map should be re-verified periodically — `cse.lk` publishes no versioning
or deprecation notice for these routes, so they can change without warning.
