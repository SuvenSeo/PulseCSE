# Differentiators

PulseCSE Pro is positioned as an investor cockpit, not a clone of a Telegram-first bot.

## Product differences

- Dashboard-first experience instead of notification-only experience.
- Company workspace with chart, risk score, peers, disclosures, and alert shortcuts.
- Simulator lab for deterministic demos and QA.
- Live API command center for backend-connected usage.
- Event history export and persistent state.
- Clear path to portfolio analytics, technical indicators, and multi-channel alerts.

## Engineering differences

- Clean backend package with separated domains.
- Reusable alert engine in both frontend and backend contexts.
- SQLite persistence by default for frictionless local setup.
- Notification adapters for console, Telegram, and webhook.
- Scenario-based testability.
- CI that checks frontend and backend.
- Dockerized deployment path.

## Scope decision

The default data provider is mock-live because public market-data endpoints can change, have access rules, or be unsuitable for production. PulseCSE isolates live-data work behind an adapter boundary so the app remains stable.
