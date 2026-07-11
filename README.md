# PulseCSE

PulseCSE is a frontend prototype for a Colombo Stock Exchange watchlist and stock-alert web app. It was built as an original academic-safe project inspired by the idea of stock alerting, but it does not copy third-party source code and does not claim to provide real financial data.

## Features

- Responsive landing page and dashboard
- Mock CSE company directory
- Search and sector filtering
- Watchlist add/remove flow
- Rule-based alert builder
- Alert types:
  - Price rises above a target
  - Price falls below a target
  - Daily percent move exceeds a target
  - New disclosure update
- Simulated market tick button
- Alert history log
- JSON export for triggered alerts
- LocalStorage persistence
- Canvas-based watchlist momentum chart

## Pages

- `index.html` - product landing page
- `dashboard.html` - watchlist, market summary, disclosures, recent fired alerts
- `alerts.html` - create and test alerts
- `companies.html` - browse companies and manage watchlist
- `history.html` - audit triggered alerts
- `about.html` - project explanation and architecture

## Tech Stack

- HTML5
- CSS3
- JavaScript ES6
- Browser LocalStorage
- Canvas API
- No external dependencies

## How to Run

Open `index.html` directly in a browser, or run a simple local server:

```bash
python -m http.server 8000
```

Then visit:

```text
http://localhost:8000
```

## GitHub Pages Deployment

1. Push these files to your GitHub repository.
2. Go to repository **Settings**.
3. Open **Pages**.
4. Set source to **Deploy from a branch**.
5. Choose `main` branch and `/root` folder.
6. Save.

## Important Disclaimer

This is a coursework/prototype project. All market data is mock data stored in JavaScript. It is not financial advice and should not be used for real investment decisions.
