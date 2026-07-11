# PulseCSE Project Report

## 1. Project Overview

PulseCSE is a web-based prototype for Sri Lankan stock market users who want to track selected Colombo Stock Exchange counters and receive alerts when important events happen. The prototype demonstrates a modern dashboard experience for watchlists, stock alerts, company disclosures, and alert history.

The project is designed as a frontend-only application so it can run on GitHub Pages without server configuration. It uses mock data instead of live CSE data, which keeps the project explainable, stable, and suitable for coursework demonstration.

## 2. Problem Statement

Retail investors often need to check prices, announcements, and market movement manually. This can cause them to miss important events such as price breakouts, sharp daily changes, or company disclosures. PulseCSE addresses this by providing a single interface where users can create watchlists and alert rules.

## 3. Main Users

- Students learning market dashboard UI design
- Retail investors who want a conceptual alerting tool
- Evaluators who need to see clear frontend functionality

## 4. Functional Requirements

1. Users can view a landing page explaining the application.
2. Users can view a dashboard of watched companies.
3. Users can browse companies and filter by sector.
4. Users can add and remove companies from a watchlist.
5. Users can create stock alert rules.
6. Users can simulate market movement.
7. Users can view fired alert history.
8. Users can export alert history as JSON.

## 5. Non-Functional Requirements

- The website must be responsive.
- The UI should look modern and professional.
- The project should run without backend setup.
- The code should be readable and explainable.
- Data should persist between page reloads using LocalStorage.

## 6. Technical Implementation

### HTML

The project uses semantic HTML pages for each major section. Each page includes accessible labels, headings, and structured content sections.

### CSS

The stylesheet uses CSS variables for theme colors, responsive grid layouts, media queries, glass-style cards, and consistent UI spacing.

### JavaScript

The JavaScript is split into modules by responsibility:

- `data.js` stores mock company and alert seed data.
- `store.js` handles LocalStorage and alert evaluation logic.
- `ui.js` contains shared formatting, navigation, toast messages, and chart drawing.
- `dashboard.js` renders the dashboard page.
- `alerts.js` handles alert creation and testing.
- `companies.js` handles searching, filtering, and watchlist changes.
- `history.js` renders and exports alert history.

## 7. Alert Logic

The alert engine evaluates saved rules against the current mock company data.

### Price Above

This fires when the latest price becomes greater than or equal to the target and the previous price was below the target.

### Price Below

This fires when the latest price becomes less than or equal to the target and the previous price was above the target.

### Percent Move

This fires when the absolute percentage change between the previous price and latest price is greater than or equal to the target.

### Disclosure

This simulates a company announcement event and stores it in alert history.

## 8. LocalStorage

LocalStorage is used to save:

- Current company prices after simulation
- User watchlist
- Saved alerts
- Alert history

This allows the app to feel more realistic because user changes remain after page reloads.

## 9. Limitations

- The project does not use live CSE API data.
- It does not send Telegram, SMS, or email notifications.
- It does not include login or user accounts.
- It should not be treated as financial advice.

## 10. Future Improvements

- Connect to a real financial data API.
- Add user authentication.
- Add real notification channels such as email or Telegram.
- Add a backend database.
- Add portfolio tracking and risk analytics.
- Add candlestick charts and historical data filtering.

## 11. Viva Explanation Points

You can explain:

- How company data is stored in an array of objects.
- How watchlist symbols are stored in LocalStorage.
- How event listeners react to button clicks and form submissions.
- How filter and search work using JavaScript `filter()`.
- How alert rules are evaluated.
- How the market tick simulates price changes.
- How the dashboard table is rendered dynamically.
- How responsive CSS grids adapt for mobile screens.
