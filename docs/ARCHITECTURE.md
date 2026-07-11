# PulseCSE Architecture

PulseCSE is a static frontend prototype designed to run directly in a browser or through GitHub Pages. It avoids a live financial API so the coursework demo is reliable, explainable, and safe.

## Layered structure

```text
HTML pages       Page structure and semantic content
CSS              Responsive visual system and reusable cards/tables/layouts
js/data.js       Mock CSE company and alert seed data
js/engine.js     Pure alert engine, risk scoring, sector summary, scenarios
js/store.js      LocalStorage persistence and application state operations
js/ui.js         Formatting, navigation, toast notifications, chart drawing
Page scripts     DOM rendering and page-specific event handlers
```

## Core design decision

The most important technical decision is separating `js/engine.js` from the DOM. The engine can be tested with Node because it does not depend on browser elements. This gives the project stronger engineering credibility than a single-script prototype.

## Alert object model

```js
{
  id: "alert-jkh-above",
  symbol: "JKH.N0000",
  type: "price_above",
  target: 190,
  note: "Breakout watch",
  enabled: true,
  armed: true,
  cooldownMinutes: 30,
  fireCount: 0,
  lastFiredAt: "2026-07-11T20:00:00.000Z"
}
```

## Alert lifecycle

1. User creates or loads an alert.
2. Alert starts as `enabled: true` and `armed: true`.
3. A market tick or scenario updates mock company prices/volume/disclosures.
4. `PulseEngine.evaluateAlerts()` compares previous state to current state.
5. If the rule fires, an event is saved to history.
6. The alert becomes `armed: false` until the condition resets.
7. Cooldown fields prevent repeated duplicate notifications.

## Supported rule types

- `price_above`: fires when price crosses upward through the target.
- `price_below`: fires when price crosses downward through the target.
- `percent_move`: fires when absolute percentage move exceeds the target.
- `disclosure`: fires only when a scenario explicitly includes a disclosure event.
- `volume_spike`: fires when volume change percentage exceeds the target.

## Storage

LocalStorage keys use versioned names:

```text
pulsecse_companies_v2
pulsecse_watchlist_v2
pulsecse_alerts_v2
pulsecse_history_v2
```

Versioned keys prevent old demo data from breaking after new object fields are introduced.

## Limitations

- Market data is mock data.
- It does not send real Telegram, email, or SMS notifications.
- It does not provide investment advice.
- It is a frontend prototype, not a production trading system.

## Future backend plan

A real version could add:

- Backend scheduler/poller
- Database tables for users, alerts, snapshots, and disclosures
- CSE API adapter
- Authenticated user accounts
- Telegram/email notification service
- Server-side duplicate prevention
