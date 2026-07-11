# PulseCSE Testing Notes

## Browser Testing

Target browsers:

- Chrome
- Edge
- Firefox

## Automated Checks

Run:

```bash
npm test
npm run check
```

`npm test` runs the alert-engine unit tests. `npm run check` verifies required HTML structure and shared script references.

## Manual Test Cases

| ID | Test | Expected Result |
| --- | --- | --- |
| T01 | Open `index.html` | Landing page loads with navigation and hero section. |
| T02 | Click Dashboard link | Dashboard page opens. |
| T03 | Click Companies link | Company directory opens. |
| T04 | Search for `bank` | Banking sector companies are shown. |
| T05 | Filter by Banks | Only bank companies are shown. |
| T06 | Click Watch on a company | Company is added to watchlist and button changes. |
| T07 | Click Details on a company | Company detail page opens with chart and metrics. |
| T08 | Create quick alert from company page | Alert is created and company enters watchlist. |
| T09 | Open Alerts page | Alert form and active alerts table load. |
| T10 | Create price alert | Alert appears in active alerts table. |
| T11 | Pause an alert | Alert enabled state changes. |
| T12 | Click Load Sample Alerts | Demo alert set appears. |
| T13 | Click Test Alerts | Market tick runs and may create history entries. |
| T14 | Open Simulator page | Scenario cards and smart suggestions load. |
| T15 | Run JKH Breakout after loading demo alerts | Price-above alert fires if armed. |
| T16 | Run COMB Disclosure after loading demo alerts | Disclosure alert fires. |
| T17 | Run DIAL Volume Spike after loading demo alerts | Volume alert fires. |
| T18 | Open History page | Triggered alert events are displayed. |
| T19 | Click Export JSON | History downloads as a JSON file. |
| T20 | Click Export CSV | History downloads as a CSV file. |
| T21 | Click Clear History | History list becomes empty. |
| T22 | Resize browser to mobile width | Navigation collapses and cards stack correctly. |
| T23 | Reload page after adding watchlist item | Watchlist item persists through LocalStorage. |
| T24 | Reset demo from dashboard | App returns to default mock data. |

## Known Limitations

The application uses mock data. Real CSE market data and real notifications would require backend integration, authentication, API monitoring, and notification services.
