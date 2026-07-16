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
- Investor extras: portfolio holdings, portfolio P&L, risk scoring, smart suggestions, simulator scenarios, and more.

## Recent Changes

As part of our ongoing efforts to improve PulseCSE Pro, we have applied changes to 38 files in the SuvenSeo/PulseCSE repository. These changes aim to enhance the overall performance, stability, and functionality of the system, ensuring a better experience for our users.

## Getting Started

To get started with PulseCSE Pro, please refer to our documentation and guidelines for setting up and configuring the system. Our community is always available to provide support and answer any questions you may have.

## Contributing

We welcome contributions from the community to help improve PulseCSE Pro. If you're interested in contributing, please review our contribution guidelines and submit a pull request with your proposed changes.

## License

PulseCSE Pro is licensed under [insert license]. By using or contributing to PulseCSE Pro, you agree to abide by the terms of the license.

## Acknowledgments

We would like to thank our community and contributors for their support and contributions to PulseCSE Pro. Your efforts have helped make PulseCSE Pro a robust and reliable platform for the Colombo Stock Exchange.