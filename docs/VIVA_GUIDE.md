# PulseCSE Viva Guide

## One-minute explanation

PulseCSE is a frontend prototype for a Colombo Stock Exchange stock-alert dashboard. It lets users browse mock companies, add stocks to a watchlist, create alert rules, simulate market events, and review triggered alert history. It uses HTML, CSS, JavaScript, LocalStorage, and Canvas.

## What to demonstrate first

1. Open `index.html` and explain the project idea.
2. Go to `dashboard.html` and show watchlist, stats, chart, heatmap, and suggestions.
3. Go to `alerts.html` and load sample alerts.
4. Go to `simulator.html` and run JKH Breakout or COMB Disclosure.
5. Go to `history.html` and show the saved alert event.
6. Open `company.html?symbol=JKH.N0000` and show quick-alert creation.

## Important code explanations

### Why use LocalStorage?

LocalStorage keeps demo state in the browser without needing a backend database. It stores companies, watchlist, alerts, and alert history.

### Why separate `engine.js`?

The alert engine is pure logic. It does not touch the DOM, so it can be tested independently using Node. This makes the project cleaner than putting all logic inside click handlers.

### How price alerts work

A price-above alert fires only when the previous price was below the target and the new price is equal to or above the target. This avoids repeatedly firing the same alert when the price stays above the threshold.

### How the simulator works

The simulator applies a known scenario to mock companies, such as raising JKH price or publishing a COMB disclosure. Then it calls the same alert engine used by the dashboard and alerts page.

### Why data is mock data

Real stock APIs can be unreliable, restricted, or out of scope for a frontend assignment. Mock data makes the demo stable and keeps the project safe from giving real financial advice.

## Possible viva questions and answers

**Q: Is this real financial data?**

No. It is mock CSE-style data used for a frontend prototype.

**Q: What JavaScript features did you use?**

Arrays, objects, functions, event listeners, DOM manipulation, LocalStorage, template literals, Canvas API, and modules implemented through global objects.

**Q: What is the most advanced part?**

The rule engine because it handles crossing logic, re-arming, cooldown state, disclosure triggers, volume spikes, risk scoring, and testable output.

**Q: How is this different from Chime?**

Chime is backend/Telegram-first. PulseCSE is dashboard/user-experience-first and built as a browser-based coursework prototype.

**Q: What would you add in a real version?**

Backend API, user authentication, live CSE adapter, database storage, notification service, and server-side scheduled polling.
