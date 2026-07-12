# PulseCSE Roadmap

PulseCSE is intended to grow from a strong private CSE alert cockpit into a reliable market-intelligence workspace while keeping compliance, correctness, and operational safety explicit.

## Phase 1: Full-stack private cockpit

Status: implemented.

- Investor dashboard and frontend workspace
- Python backend with API routes
- SQLite local mode and Postgres production-style mode
- SQL migrations and seed flow
- Alert engine with cooldown, re-arming, and event fingerprints
- Telegram command runtime
- Portfolio analytics and deterministic simulations
- Health, metrics, Docker, and CI

## Phase 2: Demo and product polish

Status: next.

- Add screenshots and short GIFs to the README
- Add a guided first-run setup checklist
- Add clearer sample alert scenarios for CSE symbols
- Add dashboard empty states and API-unavailable states
- Add export examples for portfolio and alert history
- Add release tags and changelog entries

## Phase 3: Data reliability and observability

Status: planned.

- Add endpoint probe script for live CSE adapter checks
- Add adapter contract tests using recorded sample payloads
- Add richer delivery metrics and dead-letter inspection
- Add market-calendar overrides for holidays and shortened sessions
- Add admin page for provider mode, last tick, delivery health, and database status

## Phase 4: Investor intelligence features

Status: planned.

- Add watchlist-level risk summaries
- Add portfolio concentration analysis
- Add disclosure/company matching improvements
- Add event timeline filters by sector, alert type, and severity
- Add scenario templates for price gaps, volume spikes, and portfolio drawdowns
- Add notification digest mode for lower-noise alerts

## Non-goals

- Brokerage, order execution, or automated trading
- Investment advice or personalized financial recommendations
- Claiming official CSE affiliation
- Depending on live public endpoints for tests or demos
