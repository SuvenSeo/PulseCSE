# PulseCSE Testing Notes

## Browser Testing

Tested intended browsers:

- Chrome
- Edge
- Firefox

## Manual Test Cases

| ID | Test | Expected Result |
| --- | --- | --- |
| T01 | Open `index.html` | Landing page loads with navigation and hero section. |
| T02 | Click Dashboard link | Dashboard page opens. |
| T03 | Click Companies link | Company directory opens. |
| T04 | Search for `bank` | Banking sector companies are shown. |
| T05 | Filter by Banks | Only bank companies are shown. |
| T06 | Click Watch on a company | Company is added to watchlist and button changes. |
| T07 | Open Alerts page | Alert form and active alerts table load. |
| T08 | Create price alert | Alert appears in active alerts table. |
| T09 | Click Test Alerts | Market tick runs and may create history entries. |
| T10 | Open History page | Triggered alert events are displayed. |
| T11 | Click Export JSON | History downloads as a JSON file. |
| T12 | Click Clear History | History list becomes empty. |
| T13 | Resize browser to mobile width | Navigation collapses and cards stack correctly. |
| T14 | Reload page after adding watchlist item | Watchlist item persists through LocalStorage. |
| T15 | Reset demo from dashboard | App returns to default mock data. |

## Known Limitations

The disclosure alert is simulated randomly to demonstrate notification behavior. Real disclosure monitoring would require a backend service or official API integration.
