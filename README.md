# PulseCSE

PulseCSE is a polished frontend prototype for a Colombo Stock Exchange watchlist and stock-alert web app. It was built as an original academic-safe project inspired by the general idea of stock alerting, but it does not copy third-party source code and does not claim to provide real financial data.

## Version 2 upgrade

This version turns PulseCSE into an **Investor Alert Cockpit** with a stronger alert engine, deterministic simulator, company detail pages, risk scoring, smart suggestions, tests, documentation, and a GitHub Actions workflow.

## Features

- Responsive landing page and dashboard
- Mock CSE company directory
- Search and sector filtering
- Watchlist add/remove flow
- Company detail page with chart, risk score, peers, and disclosure notes
- Rule-based alert builder
- Alert enable/disable controls
- Alert arming and cooldown state
- Deterministic simulator lab for viva demonstrations
- Alert types:
  - Price rises above a target
  - Price falls below a target
  - Daily percent move exceeds a target
  - New disclosure update
  - Volume spike exceeds a target
- Simulated market tick button
- Sector heatmap
- Smart alert suggestions
- Alert history log
- JSON and CSV export for triggered alerts
- LocalStorage persistence
- Canvas-based watchlist and company charts
- Node-based alert-engine tests
- Static project validation script
- GitHub Actions workflow

## Pages

- `index.html` - product landing page
- `dashboard.html` - watchlist, market summary, heatmap, suggestions, disclosures, recent fired alerts
- `alerts.html` - create, pause, delete, seed, and test alerts
- `companies.html` - browse companies and manage watchlist
- `company.html` - inspect one company and create quick alerts
- `simulator.html` - run deterministic market scenarios
- `history.html` - audit triggered alerts and export history
- `about.html` - project explanation and architecture

## Tech Stack

- HTML5
- CSS3
- JavaScript ES6
- Browser LocalStorage
- Canvas API
- Node.js for tests only
- No external frontend dependencies

## How to Run

Open `index.html` directly in a browser, or run a simple local server:

```bash
python -m http.server 8000
```

Then visit:

```text
http://localhost:8000
```

## How to Test

Node is only required for the optional test/check workflow.

```bash
npm test
npm run check
```

## Best Demo Flow

1. Open `dashboard.html` and show watchlist, chart, heatmap, and suggestions.
2. Open `alerts.html` and click **Load Sample Alerts**.
3. Open `simulator.html` and run **JKH Breakout**, **COMB Disclosure**, or **DIAL Volume Spike**.
4. Open `history.html` and show the fired alert audit log.
5. Open a company detail page from `companies.html` and create a quick alert.

## GitHub Pages Deployment

1. Push these files to your GitHub repository.
2. Go to repository **Settings**.
3. Open **Pages**.
4. Set source to **Deploy from a branch**.
5. Choose `main` branch and `/root` folder.
6. Save.

## Documentation

- `docs/ARCHITECTURE.md` - technical architecture and alert lifecycle
- `docs/COMPETITIVE_ANALYSIS.md` - Chime comparison and product positioning
- `docs/VIVA_GUIDE.md` - what to explain during the viva
- `docs/REPORT.md` - report-style project explanation
- `docs/TESTING.md` - manual testing notes

## Important Disclaimer

This is a coursework/prototype project. All market data is mock data stored in JavaScript. It is not financial advice and should not be used for real investment decisions.
