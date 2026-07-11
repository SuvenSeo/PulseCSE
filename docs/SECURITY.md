# Security Notes

## Secrets

Never commit `.env`. Telegram tokens, chat IDs, webhook URLs, or live market-data credentials must stay in environment variables.

## Notification safety

Notification delivery failures are logged but do not crash the alert engine. This prevents one failing channel from blocking all alerts.

## Financial safety

PulseCSE Pro is not investment advice. Default mode uses mock data to avoid misleading users with stale or unofficial market data.

## Future hardening

- Add authentication for multi-user deployments.
- Add CSRF protection for browser-authenticated mutation routes.
- Add rate limiting on alert creation and simulation endpoints.
- Add structured audit logs.
- Move from SQLite to Postgres for hosted multi-user usage.
