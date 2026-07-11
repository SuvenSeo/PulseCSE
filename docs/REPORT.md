# PulseCSE Pro Report

## Overview

PulseCSE Pro is a full-stack Colombo Stock Exchange alert cockpit. It combines a premium frontend with a Python backend, SQLite persistence, deterministic market simulation, alert evaluation, notification adapters, and CI.

## Problem

Retail investors often need to monitor price thresholds, unusual daily movement, volume spikes, and corporate disclosures without constantly refreshing market pages. PulseCSE Pro solves this as an integrated cockpit: dashboard, alert studio, company workspace, simulator, event history, and backend API.

## Solution

PulseCSE Pro provides:

- Watchlist dashboard
- Alert rule management
- Price, percent, disclosure, keyword, volume, and risk-score alerts
- Company cards and detail pages
- Deterministic simulator scenarios
- Backend API command center
- Persistent SQLite event log
- Notification adapters for console, Telegram, and webhooks

## Engineering decisions

- Static frontend remains usable without backend.
- Backend-connected mode upgrades the app into a full-stack system.
- SQLite gives frictionless local persistence.
- Repository pattern keeps database logic isolated.
- Market adapter boundary allows approved live data integration later.
- Alert engine is pure and unit-testable.
- Scenarios make QA and demos deterministic.

## Limitations

- Default data provider is mock-live, not official real-time CSE data.
- Multi-user authentication is not implemented yet.
- Telegram bot command handling is not implemented yet; notification delivery adapter is included.
- SQLite is ideal for local use, while hosted multi-user deployment should move to Postgres.

## Next steps

- Add official/approved live data adapter.
- Add auth and user settings.
- Add portfolio holdings and P/L.
- Add server-sent events for live UI updates.
- Add Postgres repository.
- Add Telegram bot commands.
