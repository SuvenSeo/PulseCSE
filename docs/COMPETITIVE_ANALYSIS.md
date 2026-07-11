# Competitive Analysis

## Project positioning

PulseCSE is positioned as an investor-facing web cockpit for Sri Lankan CSE users. It focuses on the user experience around watchlists, alert creation, alert history, company exploration, and demo-safe market simulation.

## Reference project: Chime

Chime is a backend-first CSE alerting system. Its strength is technical depth: Python services, Telegram bot commands, Postgres persistence, rule evaluation, migration files, CI, and optional web dashboard.

PulseCSE does not copy Chime's implementation. Instead, it uses the same broad problem area—stock alerts—but solves it as a frontend coursework prototype.

### Where Chime is stronger

- Real backend architecture
- Database-backed state
- Telegram-first notification workflow
- More production-like polling design
- Automated backend tests and CI

### Where PulseCSE is stronger for coursework

- Easier to run on any browser
- Better visual demonstration
- Clearer HTML/CSS/JavaScript viva scope
- Company detail pages and dashboard experience
- Deterministic simulator for marker demonstrations
- No external account, token, or database setup required

## Official CSE and market tools

Official and commercial CSE tools usually focus on live market data, research, account services, or portfolio tracking. PulseCSE does not attempt to replace these. It demonstrates how a student-built interface could unify the alerting workflow in a clean prototype.

## Differentiation

PulseCSE differentiates itself through:

1. Browser-only execution.
2. Controlled deterministic demo scenarios.
3. Explainable rule engine separated from UI code.
4. Responsive investor cockpit interface.
5. Academic-safe mock data disclaimer.

## Ethical and academic boundary

PulseCSE is inspired by stock-alerting workflows, not copied from another repository. It uses original file structure, page design, mock data, state handling, and alert logic tailored for frontend coursework.
