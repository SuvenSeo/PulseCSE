# PulseCSE Operations Runbook

This runbook covers the minimum checks needed to operate PulseCSE as a private alert cockpit.

## Routine checks

Daily during market days:

- Check `/health`.
- Check `/metrics` or `/metrics.prom`.
- Confirm `last_tick` is moving during the configured market window.
- Confirm notification failures and dead letters are not increasing.
- Confirm the configured market provider is the expected provider.

## Health endpoint

```text
GET /health
```

Use this for liveness and basic readiness. A healthy deployment should report the expected database mode, market window state, last tick metadata, and delivery health.

## Metrics endpoint

```text
GET /metrics
GET /metrics.prom
```

Use the Prometheus-style endpoint when integrating with external monitoring.

Recommended alert conditions:

- API is unavailable.
- No tick has completed during market hours for more than two poll intervals.
- Dead-letter count increases.
- Notification failure rate increases sharply.
- Database migration status is not current.

## Market polling

Run one manual tick:

```bash
python -m pulsecse tick --force
```

Run the market-hours poller:

```bash
python -m pulsecse poller
```

If live data fails, switch to mock mode to keep the app usable while investigating:

```env
PULSECSE_MARKET_PROVIDER=mock
```

## Telegram checks

Run a local command without Telegram transport:

```bash
python -m pulsecse command /portfolio
```

Useful smoke commands:

```text
/help
/watchlist
/alerts
/portfolio
/events
```

## Database operations

Apply migrations:

```bash
python -m pulsecse migrate
```

Seed demo/default data:

```bash
python -m pulsecse seed
```

For persistent deployments, schedule Postgres backups outside the app process.

## Incident response

### API down

1. Check process logs.
2. Check database connectivity.
3. Run migrations if schema mismatch is reported.
4. Restart the API process.
5. Confirm `/health` and `/metrics.prom`.

### No alerts delivered

1. Check delivery logs and dead-letter count.
2. Confirm Telegram token/chat ID or webhook URL.
3. Run `python -m pulsecse command /help`.
4. Run `python -m pulsecse tick --force`.
5. Confirm alert rules are armed and not in cooldown.

### Live market data changed

1. Switch to mock provider if production usability is affected.
2. Probe the live endpoint shape.
3. Update only the adapter layer.
4. Add/adjust tests.
5. Re-run `npm run fullcheck`.

## Release checklist

- [ ] `npm run fullcheck`
- [ ] Docker Compose boot tested, if deployment files changed
- [ ] `/health` checked
- [ ] `/metrics.prom` checked
- [ ] Telegram command path checked, if bot code changed
- [ ] Mock provider checked
- [ ] Live provider reviewed only if intentionally changed
