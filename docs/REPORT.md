# PulseCSE Project Report

## 1. Project Overview

PulseCSE is a web-based prototype for Sri Lankan stock market users who want to track selected Colombo Stock Exchange counters and receive alerts when important events happen. The upgraded version is an **Investor Alert Cockpit** with a dashboard, company directory, company detail pages, alert builder, deterministic simulation lab, and alert history.

The project is designed as a frontend-only application so it can run on GitHub Pages without server configuration. It uses mock CSE-style data instead of live financial data, which keeps the project explainable, stable, and suitable for coursework demonstration.

## 2. Problem Statement

Retail investors often need to check prices, announcements, and market movement manually. This can cause them to miss important events such as price breakouts, sharp daily changes, unusual volume spikes, or company disclosures. PulseCSE addresses this by providing a single interface where users can create watchlists, alert rules, and review triggered signals.

## 3. Main Users

- Students demonstrating frontend web application design
- Retail investors who want a conceptual alerting workflow
- Evaluators who need clear HTML, CSS, and JavaScript functionality

## 4. Functional Requirements

1. Users can view a landing page explaining the application.
2. Users can view a dashboard of watched companies.
3. Users can browse companies and filter by sector.
4. Users can open a company detail page.
5. Users can add and remove companies from a watchlist.
6. Users can create stock alert rules.
7. Users can pause, enable, and delete alert rules.
8. Users can load sample alerts for the demo.
9. Users can simulate random market movement.
10. Users can run deterministic simulator scenarios.
11. Users can view sector heatmap summaries.
12. Users can view smart alert suggestions.
13. Users can view fired alert history.
14. Users can export alert history as JSON and CSV.

## 5. Non-Functional Requirements

- The website must be responsive.
- The UI should look modern and professional.
- The project should run without backend setup.
- The code should be readable and explainable.
- Core alert logic should be separated from DOM code.
- Data should persist between page reloads using LocalStorage.
- The demo should be reliable during a viva.

## 6. Technical Implementation

### HTML

The project uses semantic HTML pages for each major section. Each page includes accessible labels, headings, navigation, structured content sections, and responsive layouts.

### CSS

The stylesheet uses CSS variables for theme colors, responsive grid layouts, media queries, glass-style cards, status pills, heatmap cards, and consistent UI spacing.

### JavaScript

The JavaScript is split by responsibility:

- `data.js` stores mock company and alert seed data.
- `engine.js` contains pure alert logic, risk scoring, sector summaries, and deterministic scenario logic.
- `store.js` handles LocalStorage and application state operations.
- `ui.js` contains shared formatting, navigation, toast messages, and chart drawing.
- `dashboard.js` renders watchlist, stats, heatmap, suggestions, disclosures, and chart.
- `alerts.js` handles alert creation, testing, pausing, and deletion.
- `companies.js` handles searching, filtering, and watchlist changes.
- `company.js` renders company detail pages and quick alerts.
- `simulator.js` runs deterministic market events.
- `history.js` renders and exports alert history.

## 7. Alert Logic

The alert engine evaluates saved rules against current mock company data. It is designed to avoid repeated alert spam by using `armed`, `lastFiredAt`, `cooldownMinutes`, and `fireCount` fields.

### Price Above

This fires when the latest price becomes greater than or equal to the target and the previous price was below the target.

### Price Below

This fires when the latest price becomes less than or equal to the target and the previous price was above the target.

### Percent Move

This fires when the absolute percentage change between the previous price and latest price is greater than or equal to the target.

### Disclosure

This fires when the simulator explicitly marks the selected company as having a new disclosure event.

### Volume Spike

This fires when the percentage increase in volume exceeds the alert target.

## 8. Simulator Lab

The simulator is included so the demo is not dependent on random chance. It has controlled scenarios:

- JKH breakout
- HNB support break
- COMB disclosure
- DIAL volume spike
- Random market tick

Each scenario updates mock company data, calls the same alert engine used by the rest of the app, and stores fired events in history.

## 9. LocalStorage

LocalStorage is used to save:

- Current company prices after simulation
- User watchlist
- Saved alerts
- Alert history

Versioned keys are used so old browser data does not break the upgraded app.

## 10. Testing

The project includes Node-based alert-engine tests in `tests/alert-engine.test.js`. These verify price crossing, disclosure triggers, volume spikes, and risk-score boundaries. The project also includes `scripts/static-check.js` to check page structure and required script references.

## 11. Limitations

- The project does not use live CSE API data.
- It does not send Telegram, SMS, or email notifications.
- It does not include login or user accounts.
- It should not be treated as financial advice.

## 12. Future Improvements

- Connect to a real financial data API.
- Add user authentication.
- Add real notification channels such as email or Telegram.
- Add a backend database.
- Add portfolio tracking and risk analytics.
- Add candlestick charts and historical data filtering.

## 13. Viva Explanation Points

You can explain:

- How company data is stored in an array of objects.
- How watchlist symbols are stored in LocalStorage.
- How event listeners react to button clicks and form submissions.
- How search and filtering use JavaScript `filter()`.
- How alert rules are evaluated by a pure engine.
- How threshold crossing prevents duplicate alerts.
- How the simulator applies deterministic scenarios.
- How the dashboard table and company cards are rendered dynamically.
- How responsive CSS grids adapt for mobile screens.
- How tests validate the alert engine.
