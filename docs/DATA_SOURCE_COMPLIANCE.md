# Market Data and Compliance Notes

PulseCSE is an information and engineering project. It is not a broker, exchange member, investment adviser, trading terminal, or official market-data vendor.

## Default data mode

The default market provider is mock mode:

```env
PULSECSE_MARKET_PROVIDER=mock
```

Mock mode is deterministic and safe for demos, CI, development, and UI testing.

## Live CSE adapter boundary

Live CSE access is isolated behind the `cse-live` adapter. The rest of the app should not depend directly on public endpoint field names or transport details.

```env
PULSECSE_MARKET_PROVIDER=cse-live
PULSECSE_CSE_BASE_URL=https://www.cse.lk
```

Use live mode only when your usage is permitted by the source, applicable terms, and any market-data rules that apply to your deployment.

## Engineering requirements for live data

When live mode is enabled:

- Keep all CSE-specific parsing inside the adapter layer.
- Do not fabricate symbols, sectors, prices, volumes, or disclosure links when the source does not provide them reliably.
- Fail closed or degrade gracefully when an endpoint changes.
- Preserve the source identifier on stored snapshots and disclosures.
- Avoid aggressive polling. Respect configured intervals and jitter.
- Keep mock mode available so tests and demos do not depend on public endpoint availability.

## Product disclaimers

Any UI, Telegram message, API response, or export that contains market information should preserve these boundaries:

- No investment advice.
- No buy/sell/hold recommendations presented as financial advice.
- No guarantee of exchange accuracy or completeness.
- No claim of official affiliation with the Colombo Stock Exchange.
- No automated trading or order placement.

## Suggested release gate

Before releasing changes that touch the live adapter:

- [ ] Run backend tests.
- [ ] Run the API smoke test.
- [ ] Confirm mock mode still works.
- [ ] Probe live endpoints manually or with a documented script.
- [ ] Update adapter comments or docs when source fields change.
- [ ] Review rate limits, source terms, and deployment context.
